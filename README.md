# scraping

A Claude Code skill for web scraping and data extraction using [Scrapling](https://github.com/D4Vinci/Scrapling).

## What is this?

This is a **skill** (in [Anthropic skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator) format) that gives Claude Code the ability to scrape websites, extract structured data, search e-commerce sites, and compare prices across multiple stores.

## Installation

### As a Claude Code Skill

```bash
# From this repo
claude install-skill /path/to/scraping

# Or from GitHub
claude install-skill https://github.com/2lab-ai/scraping
```

### Prerequisites

The skill expects a Python venv with Scrapling installed:

```bash
# Create venv
python3 -m venv ~/.scrapling-venv

# Install Scrapling with all extras
~/.scrapling-venv/bin/pip install "scrapling[all]"

# Install Chromium for headless browsing
~/.scrapling-venv/bin/python3 -c "from scrapling.fetchers import StealthyFetcher; StealthyFetcher.setup()"
```

**Note**: On servers without root access, Chromium shared libraries (libnspr4, libnss3, etc.) may need manual installation. See [SKILL.md](SKILL.md) for the `LD_LIBRARY_PATH` workaround.

## Capabilities

| Feature | Fetcher | Bot Protection |
|---------|---------|---------------|
| Static HTML scraping | `Fetcher` | None |
| Anti-bot bypass (Akamai, Cloudflare) | `StealthyFetcher` | Yes |
| JS-rendered SPA content | `DynamicFetcher` | Yes |
| Multi-page crawling | `Spider` | None |
| Stateful sessions (login, cookies) | `StealthySession` | Yes |

## Supported Sites

Site-specific parsing patterns are documented in [`references/sites.md`](references/sites.md):

- **Coupang** (coupang.com) — Akamai-protected, React SPA, requires StealthyFetcher
- **Amazon.de** — ASIN-based product extraction
- **DocMorris.de** — German pharmacy, static HTML

## Scripts

Ready-to-use scripts in [`scripts/`](scripts/):

- **`coupang_search.py`** — Search Coupang products by keyword, sort by reviews/price/sales
- **`price_compare.py`** — Compare prices across Amazon.de and DocMorris.de

## Structure

```
scraping/
├── SKILL.md              # Skill definition (Anthropic skill-creator format)
├── README.md             # This file
├── references/
│   └── sites.md          # Site-specific scraping playbooks
├── scripts/
│   ├── coupang_search.py # Coupang product search
│   └── price_compare.py  # Multi-site price comparison
├── evals/
│   └── evals.json        # Test cases for skill evaluation
└── .gitignore
```

## License

MIT
