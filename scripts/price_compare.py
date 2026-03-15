#!/usr/bin/env python3
"""Multi-site price comparison.

Usage:
  ~/.scrapling-venv/bin/python3 price_compare.py "product name" [site1,site2,...]

Supported sites: amazon.de, docmorris.de
For sites requiring Chromium, set LD_LIBRARY_PATH.
"""
import sys
import json
import re
from scrapling.fetchers import Fetcher
from urllib.parse import quote


def search_amazon_de(query: str) -> list[dict]:
    url = f"https://www.amazon.de/s?k={quote(query)}"
    page = Fetcher.get(url, impersonate="chrome131", stealthy_headers=True,
                       headers={"Accept-Language": "de-DE,de;q=0.9"})
    results = []
    if page.status != 200:
        return results

    html = page.html_content
    for m in re.finditer(r'data-asin="([A-Z0-9]{10})"', html):
        asin = m.group(1)
        # find title near this asin
        chunk = html[m.start():m.start()+5000]
        title_m = re.search(r'alt="([^"]*' + re.escape(query.split()[0]) + r'[^"]*)"', chunk, re.I)
        if not title_m:
            title_m = re.search(r'a-text-normal[^>]*>([^<]+)<', chunk)
        if title_m:
            results.append(dict(
                source="Amazon.de",
                name=title_m.group(1).strip()[:120],
                link=f"https://www.amazon.de/dp/{asin}",
            ))
    return results[:10]


def search_docmorris(query: str) -> list[dict]:
    url = f"https://www.docmorris.de/search?query={quote(query)}"
    page = Fetcher.get(url, impersonate="chrome131", stealthy_headers=True,
                       headers={"Accept-Language": "de-DE,de;q=0.9"})
    results = []
    if page.status != 200:
        return results

    html = page.html_content
    names = re.findall(r'alt="([^"]+)"', html)
    prices = re.findall(r'>(\d+[,\.]\d{2})\s*€<', html)
    links = re.findall(r'href="(/[^"]+)"', html)
    product_links = [l for l in links if l.startswith('/orthomol') or l.startswith('/product')]

    for i, name in enumerate(names[:10]):
        if any(w in name.lower() for w in query.lower().split()):
            price = prices[i] if i < len(prices) else ''
            link = f"https://www.docmorris.de{product_links[i]}" if i < len(product_links) else ''
            results.append(dict(
                source="DocMorris.de",
                name=name[:120],
                price=f"{price} €" if price else '',
                link=link,
            ))
    return results[:10]


SITE_HANDLERS = {
    "amazon.de": search_amazon_de,
    "docmorris.de": search_docmorris,
}


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "Orthomol Immun 30"
    sites = sys.argv[2].split(",") if len(sys.argv) > 2 else list(SITE_HANDLERS.keys())

    all_results = []
    for site in sites:
        handler = SITE_HANDLERS.get(site.strip())
        if handler:
            print(f"[*] Searching {site}...", file=sys.stderr)
            all_results.extend(handler(query))

    print(json.dumps(all_results, ensure_ascii=False, indent=2))
