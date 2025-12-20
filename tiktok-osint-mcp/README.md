# TikTok MCP Server (yt-dlp)

A minimal **Model Context Protocol (MCP) server** that extracts **public TikTok metadata** using `yt-dlp`, designed to support **missing person / MMIP investigations** by producing structured, source-linked signals suitable for inclusion in a **law-enforcement dossier**.

This server **does not perform account discovery**. It only enumerates **explicitly provided TikTok profiles or video URLs**.

---

## Purpose

This MCP server exists to:

- Enumerate **public TikTok posts** from known accounts or URLs
- Extract **timestamps, captions, hashtags, and basic media metadata**
- Support construction of a **clean investigative timeline**
- Reduce manual OSINT effort while avoiding speculative expansion

The output is intended to be **reviewable, source-attributed, and conservative**, aligning with real-world investigative workflows.

---

## MVP Scope & Constraints

### Included (v0.1)
- Enumerate recent posts from a provided TikTok profile (`@handle` or profile URL)
- Extract metadata for a single TikTok video URL
- Metadata-only (no video downloads)
- Public content only
- Bounded enumeration via:
  - `max_items`
  - `lookback_days`

### Explicitly Excluded
- Automated account discovery
- Friends/followers or social graph expansion
- Login-based scraping
- Private or restricted content
- Comment mining
- Persistent storage (e.g., SQLite)

These exclusions are intentional to keep the MVP small, defensible, and finishable.

---

## Intended Use

This server is designed to be called by an **orchestrator or agent system** that:

- Already knows which TikTok accounts or URLs are relevant  
  (e.g., provided on a flyer, official post, family advocacy page, or found manually)
- Needs **structured, reviewable outputs** for an investigative dossier
- Separates clearly between:
  - official sources
  - family / advocacy posts
  - public amplification
  - unverified witness content (flagged downstream)

The server **does not infer relationships, discover new accounts, or make investigative claims**.

---

## Tools Exposed

### `tiktok.profile_recent`

Enumerates recent public posts from a provided TikTok profile.

#### Input
```json
{
  "handle_or_url": "@bringJaneHome",
  "limits": {
    "max_items": 50,
    "lookback_days": 180
  }
}
````

#### Behavior

* Accepts `@handle` or full profile URL
* Returns up to `max_items` posts
* Skips posts older than `lookback_days`
* Metadata only (no media downloads)

---

### `tiktok.video_meta`

Extracts metadata for a single TikTok video URL.

#### Input

```json
{
  "video_url": "https://www.tiktok.com/@user/video/1234567890"
}
```

#### Behavior

* Extracts uploader, caption text, publish date, thumbnail, and URL
* Returns a single standardized item

---

## Output Format

All tools return a **standardized connector object** with the following top-level fields:

* `connector_name`
* `run_metadata`
* `seeds_used`
* `items[]`
* `summary`

Each `item` includes:

* source name and URL
* post URL
* published timestamp (when available)
* caption text
* basic extracted signals (hashtags, lightweight location/time hints)
* credibility flags (left unset for reducer logic)

This format is designed to make downstream **reduction, prioritization, and review trivial**.

---

## Installation

### Requirements

* Python 3.11+
* `yt-dlp` available on PATH
* `uv` / `uvx` (recommended)

### Install dependencies

```bash
uv sync
```

---

## Running the Server

### Local development (stdio transport)

```bash
uv run tiktok-mcp
```

The server runs over **stdio**, suitable for use by MCP-compatible hosts.

### Run via `uvx`

After building:

```bash
uv build
uvx --from dist/tiktok_mcp-0.1.0-py3-none-any.whl tiktok-mcp
```

---

## Design Notes

* `yt-dlp --dump-json` is used in metadata-only mode
* Enumeration is intentionally capped to prevent scope explosion
* Signal extraction is deliberately lightweight; deeper NLP belongs downstream
* Errors or partial failures are tolerated when some metadata is returned

This design mirrors how a human investigator would manually review public TikTok content—just faster and more consistent.

---

## Ethics & Safety

* Public content only
* No private data access
* No automated relationship inference
* No speculative labeling
* Clear provenance for every returned item

This server is meant to **support**, not replace, human investigative judgment.

---

## Future Work (Out of Scope for MVP)

* SQLite or other persistent caching
* Comment enumeration
* Automated account discovery
* Cross-platform correlation
* Evidence preservation workflows (media download/export)

---

## License

MIT (or your preferred license)

---

## Disclaimer

This tool is intended for **lawful, ethical use** in support of missing person investigations.
Users are responsible for complying with applicable laws, platform terms of service, and investigative standards.
