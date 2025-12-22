# Facebook Public Intel MCP Server

This MCP server extracts **publicly available** OSINT signals from Facebook URLs and/or investigator-provided HTML captures, producing structured outputs that can support investigations.

## Compliance & Safety Principles

- **No login bypass / no circumvention**: The server does not automate authentication and does not attempt to defeat access controls.
- **API-first**: Where programmatic access is required, use official Meta APIs/permissions (e.g., oEmbed / Graph API features).
- **Capture-mode supported**: If Facebook blocks automated retrieval, provide an investigator-collected HTML capture (page source / archive) and run extraction locally.
- **Evidence-first**: Outputs are structured and can include hashable captures to support chain-of-custody style workflows.

Meta maintains policies and terms governing automated data collection and API usage; ensure your use aligns with the applicable requirements and your organization's legal guidance.

## Tools

- `fb_normalize_url(url)`  
  Classifies URL (page/profile/post/video) and extracts vanity/id hints.

- `fb_fetch_public_html(url)`  
  Attempts a **public** fetch without authentication (may return login-wall HTML).

- `fb_extract_signals_from_html(html, base_url)`  
  Extracts OpenGraph metadata + outbound links from a provided HTML capture.

- `fb_oembed_lookup(url, access_token)`  
  Optional oEmbed call (token required). Set `META_ACCESS_TOKEN` env var.

- `fb_build_lead_packet(url, signals)`  
  Generates a structured “lead packet” with identifiers + suggested follow-ups.

## Running

### With uvx (recommended)
```bash
uvx --from facebook-public-intel-mcp facebook-public-intel-mcp
Env vars
META_ACCESS_TOKEN (optional): token for oEmbed/Graph calls

Output Notes
This server intentionally avoids private data and focuses on identifiers and public metadata (display name, canonical URL, profile image URL, description, outbound links).

yaml
Copy code

---

## Why this is “structured similarly” and future-proof for your MMIP tool

- Your ingestion phase can run:
  - `fb_normalize_url` → route
  - `fb_fetch_public_html` (best effort)
  - fallback: investigator provides HTML capture → `fb_extract_signals_from_html`
  - reduce step: `fb_build_lead_packet`

- It’s compatible with map-reduce: each tool returns small, composable JSON chunks.

---

## Notes on Meta endpoints (so your design matches reality)

- **Page Public Content Access (PPCA)** exists to read public Page data via Graph API for Pages you don’t manage, but it’s permission-gated and use-case restricted. :contentReference[oaicite:1]{index=1}  
- **oEmbed requires token-based access** and has had migration/deprecation timelines (so treat oEmbed as optional/feature-flagged). :contentReference[oaicite:2]{index=2}  
- Meta also has a **Content Library / Content Library API** (primarily for transparency/research use cases). If you’re eligible, that can become a separate MCP server later. :contentReference[oaicite:3]{index=3}
