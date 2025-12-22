# instagram-osint-mcp

An MCP (Model Context Protocol) server for **ethical, evidence-grade Instagram OSINT collection**, designed for missing and murdered Indigenous persons (MMIP) investigations and similar public-interest cases.

This server mirrors **manual investigative practice**: viewing Instagram content through a standard browser session and preserving what is visible, without bypassing access controls.

---

## ⚖️ Ethical & Legal Design

This tool is intentionally constrained:

- **No private account access**
- **No login bypassing**
- **No scraping behind authentication walls**
- **No interaction with targets** (no follows, likes, messages)
- **Evidence-first**: preserves HTML + screenshots + hashes

The goal is to replicate what a human investigator could lawfully observe and document.

---

## 🔐 Authenticated Viewing (Sock Puppet / Investigator Account)

Instagram often restricts visibility unless the viewer is logged in.

This server assumes:
- An **investigator-controlled Instagram account**
- Used only for passive viewing
- No impersonation, engagement, or deception

Login/session handling is intentionally minimal and can be extended later using
Playwright storage state or a persistent browser profile.

---

## 🧰 MCP Tools

### `capture_instagram_profile`

Captures an Instagram profile page.

**Inputs**
- `profile_url` (string)
- `require_login` (bool, default `true`)
- `out_dir` (string)

**Outputs**
- HTML snapshot
- Full-page PNG screenshot
- SHA256 hashes
- Timestamped metadata

---

### `list_visible_profile_posts`

Captures the profile page and extracts a small number of **visible** post or reel URLs.

**Important**
- No scrolling is performed
- Extraction is best-effort
- Intended for pivoting to post-level captures

---

## 📁 Evidence Output

Artifacts are written to:

raw/instagram/evidence/

yaml
Copy code

Each capture produces:
- `<timestamp>__<safe_url>.html`
- `<timestamp>__<safe_url>.png`

Hashes are returned in the MCP response for chain-of-custody verification.

---

## 🚀 Running the Server

### Install dependencies
```bash
playwright install chromium
Run via uvx
bash
Copy code
uvx instagram-osint-mcp
Or directly
bash
Copy code
python server.py
🧠 Integration Notes
Designed to be called by an OSINT connector agent

Outputs are suitable for downstream reduce/analysis agents

Structure is compatible with later migration to a shared osint_core library

⚠️ Disclaimer
This tool is provided for lawful OSINT and humanitarian investigations only.
Operators are responsible for ensuring compliance with platform terms of service
and applicable laws in their jurisdiction.