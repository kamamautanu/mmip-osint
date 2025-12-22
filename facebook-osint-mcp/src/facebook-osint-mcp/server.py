from __future__ import annotations

import os
import re
import time
import hashlib
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse, parse_qs

import httpx
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP


###############################################################################
# MCP Server Setup
###############################################################################

mcp = FastMCP("facebook_public_intel")

DEFAULT_UA = "mmip-facebook-public-intel/0.1 (compliance-first)"
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "").strip()


###############################################################################
# Utilities
###############################################################################

def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def _now() -> int:
    return int(time.time())


def _is_facebook_url(url: str) -> bool:
    host = urlparse(url).netloc.lower()
    return any(
        host.endswith(h)
        for h in ("facebook.com", "fb.com", "fb.watch")
    )


###############################################################################
# URL Normalization / Classification
###############################################################################

FB_URL_RE = re.compile(r"^https?://(www\.)?facebook\.com/(?P<path>.+)$", re.I)


def normalize_facebook_url(url: str) -> Dict[str, Any]:
    """
    Normalize and classify a Facebook URL for routing + evidence.
    """
    parsed = urlparse(url)
    result: Dict[str, Any] = {
        "input_url": url,
        "normalized_url": url,
        "host": parsed.netloc.lower(),
        "entity_type": "unknown",
        "vanity": None,
        "numeric_id": None,
        "possible_post_id": None,
    }

    if parsed.netloc.endswith("fb.watch"):
        result["entity_type"] = "video"
        return result

    match = FB_URL_RE.match(url)
    if not match:
        return result

    path = match.group("path").strip("/")
    result["normalized_url"] = f"https://www.facebook.com/{path}"

    if path.startswith("profile.php"):
        result["entity_type"] = "profile"
        qs = parse_qs(parsed.query)
        result["numeric_id"] = qs.get("id", [None])[0]
        return result

    if "/posts/" in path:
        result["entity_type"] = "post"
        segments = path.split("/")
        result["vanity"] = segments[0]
        for seg in reversed(segments):
            if seg.isdigit():
                result["possible_post_id"] = seg
                break
        return result

    segments = path.split("/")
    if segments:
        result["entity_type"] = "page_or_profile"
        result["vanity"] = segments[0]

    return result


###############################################################################
# Public Fetch (No Auth, No Bypass)
###############################################################################

async def fetch_public_html(
    url: str,
    max_bytes: int = 2_000_000,
) -> Dict[str, Any]:
    """
    Fetch HTML only if publicly reachable without authentication.
    """
    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=20.0,
        headers={
            "User-Agent": DEFAULT_UA,
            "Accept": "text/html,application/xhtml+xml",
        },
    ) as client:
        r = await client.get(url)
        body = r.text

    if len(body.encode("utf-8", errors="ignore")) > max_bytes:
        body = body.encode("utf-8", errors="ignore")[:max_bytes].decode("utf-8", errors="ignore")

    return {
        "final_url": str(r.url),
        "status_code": r.status_code,
        "fetched_at_unix": _now(),
        "sha256": _sha256(body),
        "headers": {
            "content-type": r.headers.get("content-type"),
            "cache-control": r.headers.get("cache-control"),
        },
        "html": body,
    }


###############################################################################
# HTML Extraction (Capture-First Compatible)
###############################################################################

PROFILE_ID_RE = re.compile(r"fb://profile/(?P<id>\d+)")
PAGE_ID_RE = re.compile(r"fb://page/(?P<id>\d+)")


def extract_opengraph(html: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "lxml")
    meta: Dict[str, str] = {}
    numeric_ids: List[Dict[str, str]] = []

    for tag in soup.find_all("meta"):
        key = tag.get("property") or tag.get("name")
        val = tag.get("content")
        if not key or not val:
            continue

        key = key.lower()
        meta[key] = val.strip()

        if key.startswith("al:"):
            if m := PROFILE_ID_RE.search(val):
                numeric_ids.append({"type": "profile", "id": m.group("id"), "source": f"meta[{key}]"})
            if m := PAGE_ID_RE.search(val):
                numeric_ids.append({"type": "page", "id": m.group("id"), "source": f"meta[{key}]"})

    return {
        "meta": meta,
        "numeric_ids": numeric_ids,
    }


def extract_outbound_links(html: str, limit: int = 50) -> List[Dict[str, str]]:
    soup = BeautifulSoup(html, "lxml")
    links = []
    seen = set()

    for a in soup.find_all("a"):
        href = a.get("href")
        if not href or href in seen:
            continue
        seen.add(href)
        links.append({
            "href": href,
            "text": (a.get_text() or "").strip()[:200],
        })
        if len(links) >= limit:
            break

    return links


###############################################################################
# MCP Tools
###############################################################################

@mcp.tool()
async def fb_normalize_url(url: str) -> Dict[str, Any]:
    """
    Normalize and classify a Facebook URL.
    """
    return normalize_facebook_url(url)


@mcp.tool()
async def fb_fetch_public_html(url: str) -> Dict[str, Any]:
    """
    Fetch publicly accessible HTML (no auth, no bypass).
    """
    if not _is_facebook_url(url):
        return {"error": "Not a Facebook URL", "input_url": url}

    return await fetch_public_html(url)


@mcp.tool()
async def fb_extract_from_html(
    html: str,
    base_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Extract OSINT signals from investigator-provided HTML capture.
    """
    og = extract_opengraph(html)
    links = extract_outbound_links(html)

    result: Dict[str, Any] = {
        "opengraph": og,
        "outbound_links": links,
    }

    meta = og.get("meta", {})

    if "og:title" in meta:
        result["display_name"] = {
            "value": meta["og:title"],
            "source": "opengraph:og:title",
        }

    if "og:description" in meta:
        result["description"] = {
            "value": meta["og:description"],
            "source": "opengraph:og:description",
        }

    if "og:image" in meta:
        result["profile_image_url"] = {
            "value": meta["og:image"],
            "source": "opengraph:og:image",
        }

    if base_url:
        result["base_url"] = base_url

    return result


@mcp.tool()
async def fb_build_lead_packet(
    target_url: str,
    extracted_signals: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Build a law-enforcement-oriented lead packet from extracted signals.
    """
    norm = normalize_facebook_url(target_url)

    packet: Dict[str, Any] = {
        "target_url": target_url,
        "normalized": norm,
        "identifiers": [],
        "public_profile_signals": {},
        "recommended_followups": [],
        "disclaimer": (
            "OSINT derived from public Facebook content or investigator-provided capture. "
            "No access controls bypassed."
        ),
    }

    if norm.get("vanity"):
        packet["identifiers"].append({
            "type": "facebook_vanity",
            "value": norm["vanity"],
            "source": "url",
        })

    if norm.get("numeric_id"):
        packet["identifiers"].append({
            "type": "facebook_numeric_id",
            "value": norm["numeric_id"],
            "source": "url_query",
        })

    og = extracted_signals.get("opengraph", {})
    meta = og.get("meta", {})
    numeric_ids = og.get("numeric_ids", [])

    for item in numeric_ids:
        packet["identifiers"].append({
            "type": f"facebook_{item['type']}_id",
            "value": item["id"],
            "source": item["source"],
        })

    if "display_name" in extracted_signals:
        packet["public_profile_signals"]["display_name"] = extracted_signals["display_name"]

    if "description" in extracted_signals:
        packet["public_profile_signals"]["description"] = extracted_signals["description"]

    if "profile_image_url" in extracted_signals:
        packet["public_profile_signals"]["profile_image_url"] = extracted_signals["profile_image_url"]

    if extracted_signals.get("outbound_links"):
        packet["public_profile_signals"]["outbound_links"] = extracted_signals["outbound_links"]

    packet["recommended_followups"] = [
        "Preserve the URL, HTML capture, and hash if time-sensitive.",
        "Submit a Meta preservation request referencing numeric IDs or vanity URL.",
        "Cross-pivot outbound links and display name across other social platforms.",
        "Request account records via legal process if authorized.",
    ]

    return packet


###############################################################################
# Entrypoint
###############################################################################

def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
