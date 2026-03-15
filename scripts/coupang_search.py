#!/usr/bin/env python3
"""Coupang product search.

Usage:
  LD_LIBRARY_PATH="$HOME/.local/lib/chromium-deps/usr/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH" \
    ~/.scrapling-venv/bin/python3 coupang_search.py "검색어" [sorter] [limit]

Sorters: scoreDesc (리뷰순), salePriceAsc (낮은가격순), saleCountDesc (판매량순)
"""
import sys
import json
import re
from urllib.parse import quote
from scrapling.fetchers import StealthyFetcher


def search(query: str, sorter: str = "scoreDesc", limit: int = 15) -> list[dict]:
    url = f"https://www.coupang.com/np/search?q={quote(query)}&sorter={sorter}&listSize=60"
    page = StealthyFetcher.fetch(url, headless=True, network_idle=True)

    if page.status != 200:
        print(f"[!] Status {page.status}", file=sys.stderr)
        return []

    html = page.html_content
    blocks = re.findall(r'<li[^>]*ProductUnit_productUnit[^>]*>(.*?)</li>', html, re.DOTALL)
    products = []

    for block in blocks:
        try:
            alt = re.search(r'<img[^>]*alt="([^"]+)"', block)
            name = alt.group(1) if alt else ''
            pm = re.search(r'fw-text-\[20px\][^>]*>([^<]+)<', block)
            price = int(re.sub(r'[^\d]', '', pm.group(1))) if pm else 0
            dm = re.search(r'>(\d+%)<', block)
            discount = dm.group(1) if dm else ''
            rm = re.search(r'\(([\d,]+)\)', block)
            reviews = int(rm.group(1).replace(',', '')) if rm else 0
            rating = len(re.findall(r'fullRating', block)) + 0.5 * len(re.findall(r'halfRating', block))
            lm = re.search(r'href="(/vp/products/[^"]+)"', block)
            link = 'https://www.coupang.com' + lm.group(1).replace('&amp;', '&') if lm else ''
            um = re.search(r'\(([^)]*당\s*[\d,]+원)\)', block)
            unit_price = um.group(1) if um else ''
            is_ad = 'AdMark' in block

            if name and price > 0:
                products.append(dict(
                    name=name[:100], price=price, discount=discount,
                    rating=rating, reviews=reviews, unit_price=unit_price,
                    link=link, is_ad=is_ad, score=reviews * rating,
                ))
        except Exception:
            continue

    products.sort(key=lambda x: x['score'], reverse=True)
    return products[:limit]


if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "단백질 음료"
    s = sys.argv[2] if len(sys.argv) > 2 else "scoreDesc"
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 15

    results = search(q, s, n)
    print(json.dumps(results, ensure_ascii=False, indent=2))
