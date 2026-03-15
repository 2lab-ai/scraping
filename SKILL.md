---
name: scrape
description: Web scraping and data extraction using Scrapling. Use this skill whenever the user wants to scrape a website, crawl pages, extract data from URLs, search for products/prices online, compare prices across sites, or pull structured data from web pages. Also use when the user mentions Coupang, Amazon, shopping search, price comparison, or any task involving fetching and parsing web content — even if they don't explicitly say "scrape".
---

# Scrape — Web Scraping with Scrapling

Extract data from any website using [Scrapling](https://github.com/D4Vinci/Scrapling), a Python scraping framework with TLS fingerprint spoofing and anti-bot bypass.

## Environment

- **Python**: `~/.scrapling-venv/bin/python3`
- **Chromium libs**: `~/.local/lib/chromium-deps/usr/lib/x86_64-linux-gnu/`
- **Temp scripts**: write to `/tmp/scrapling_task.py`, execute from there

When using StealthyFetcher or DynamicFetcher (headless Chromium), prefix the command with:
```bash
LD_LIBRARY_PATH="$HOME/.local/lib/chromium-deps/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH"
```

## Choosing a Fetcher

Pick the lightest fetcher that works. Escalate only on failure.

| Situation | Fetcher | Speed | Chromium? |
|-----------|---------|-------|-----------|
| Static HTML, no bot protection | `Fetcher` | ⚡ fast | No |
| Akamai, Cloudflare, bot walls | `StealthyFetcher` | 🐢 slow | Yes (LD_LIBRARY_PATH) |
| JS-rendered SPA (React, Vue) | `DynamicFetcher` | 🐢 slow | Yes (LD_LIBRARY_PATH) |
| Multi-page crawl | `Spider` | ⚡ parallel | No |
| Stateful (cookies/login) | `StealthySession` | 🐢 slow | Yes (LD_LIBRARY_PATH) |

**Escalation order**: Try `Fetcher` first. If 403/418/captcha → switch to `StealthyFetcher`. If content still missing (JS render) → `DynamicFetcher`.

## Writing a Scraping Script

Every scraping task follows this pattern:

1. **Write** a Python script to `/tmp/scrapling_task.py`
2. **Execute** with the venv Python
3. **Parse** results and present to user

### Fetcher (fast, no browser)

```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://example.com', stealthy_headers=True, impersonate="chrome131")
print(f"Status: {page.status}")

# CSS selectors (Scrapy-style)
titles = page.css('h2::text').getall()
links = page.css('a::attr(href)').getall()

# XPath
items = page.xpath('//div[@class="item"]/text()').getall()
```

Key parameters: `impersonate` (browser TLS fingerprint), `stealthy_headers` (real browser headers), `follow_redirects`, `timeout`, `headers`, `cookies`.

Available impersonate values: `chrome131`, `chrome136`, `firefox135`, `safari184`, `chrome_android`, etc.

### StealthyFetcher (beats Akamai/Cloudflare)

```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch('https://protected-site.com',
    headless=True,
    network_idle=True,        # wait for all network requests to finish
    solve_cloudflare=True,    # auto-solve Turnstile
)
```

### Session (cookie persistence)

```python
from scrapling.fetchers import StealthySession

with StealthySession(headless=True) as session:
    page1 = session.fetch('https://site.com/login')
    page2 = session.fetch('https://site.com/data')  # cookies carry over
```

### Spider (multi-page)

```python
from scrapling.spiders import Spider, Response

class MySpider(Spider):
    name = "crawler"
    start_urls = ["https://example.com/page/1"]
    concurrent_requests = 5

    async def parse(self, response: Response):
        for item in response.css('.product'):
            yield {
                "name": item.css('.name::text').get(),
                "price": item.css('.price::text').get(),
            }
        next_page = response.css('.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page)

result = MySpider().start()
result.items.to_json("/tmp/output.json")
```

## Execution

```bash
# Fetcher (no Chromium needed)
~/.scrapling-venv/bin/python3 /tmp/scrapling_task.py

# StealthyFetcher / DynamicFetcher (Chromium needed)
LD_LIBRARY_PATH="$HOME/.local/lib/chromium-deps/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH" \
  ~/.scrapling-venv/bin/python3 /tmp/scrapling_task.py
```

## Site-Specific Playbooks

Read `references/sites.md` for site-specific parsing patterns (Coupang, Amazon, etc.). These change over time — when a known pattern fails, investigate the HTML and update the reference.

## Error Recovery

| Error | Fix |
|-------|-----|
| 403 / Access Denied | Escalate to StealthyFetcher |
| 418 / bot detection | StealthyFetcher + `solve_cloudflare=True` |
| Empty content (JS) | DynamicFetcher + `network_idle=True` |
| `libnspr4.so not found` | Add `LD_LIBRARY_PATH` prefix |
| Import error | `~/.scrapling-venv/bin/pip install "scrapling[all]"` |
| Timeout | Increase `timeout` parameter |

## Output

- Present extracted data in a clean table or summary
- For large datasets, save to `/tmp/` as JSON and tell the user the path
- Always include source URLs/links in results
