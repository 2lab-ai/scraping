# Site-Specific Scraping Playbooks

Patterns verified as of 2026-03. Sites change — when a pattern breaks, inspect the HTML and update this file.

## Coupang (coupang.com)

**Anti-bot**: Akamai Bot Manager. `Fetcher` → 403. Must use `StealthyFetcher`.

**Search URL**: `https://www.coupang.com/np/search?q={query}&sorter={sort}&listSize=60`
- Sorters: `scoreDesc` (리뷰순), `salePriceAsc` (낮은가격순), `saleCountDesc` (판매량순)

**HTML structure** (React SPA, CSS Modules):
- Product block: `<li>` with class matching `ProductUnit_productUnit__*`
- Extract via regex: `re.findall(r'<li[^>]*ProductUnit_productUnit[^>]*>(.*?)</li>', html, re.DOTALL)`
- Product name: `<img alt="...">` inside the block, or class `ProductUnit_productNameV2__*`
- Sale price: element with class `fw-text-[20px]` (the large-font price)
- Original price: element with class `fw-line-through`
- Discount: `>N%<` pattern
- Reviews: `(N,NNN)` parenthesized number pattern
- Rating: count occurrences of `fullRating` (= full stars) and `halfRating` (= half stars)
- Link: `href="/vp/products/..."` → prepend `https://www.coupang.com`
- Ad marker: presence of `AdMark` class
- Unit price: `(Nml당 N원)` or `(Ng당 N원)` pattern

**Example parser**:
```python
import re
for block in re.findall(r'<li[^>]*ProductUnit_productUnit[^>]*>(.*?)</li>', html, re.DOTALL):
    name = re.search(r'<img[^>]*alt="([^"]+)"', block)
    price = re.search(r'fw-text-\[20px\][^>]*>([^<]+)<', block)
    reviews = re.search(r'\(([\d,]+)\)', block)
    stars = len(re.findall(r'fullRating', block))
    link = re.search(r'href="(/vp/products/[^"]+)"', block)
```

## Amazon.de

**Anti-bot**: Moderate. `Fetcher` works for search results (200), but product prices are JS-rendered.

**Search URL**: `https://www.amazon.de/s?k={query}`

**HTML structure**:
- Product block: `data-asin="B0XXXXXXXX"` attribute on divs
- Title: `<span class="a-text-normal">` or `alt=""` on product image
- Price: `<span class="a-price-whole">` + `<span class="a-price-fraction">` (often missing in search results — JS rendered)
- Link: `/dp/{ASIN}` pattern → `https://www.amazon.de/dp/{ASIN}`

**Tip**: For Amazon prices, it's often easier to go directly to the product page `/dp/{ASIN}` and extract from there, or use `StealthyFetcher` for JS rendering.

## DocMorris.de (German pharmacy)

**Anti-bot**: None. `Fetcher` works fine (200).

**Search URL**: `https://www.docmorris.de/search?query={query}`

**HTML structure**:
- Product names: `alt="Product Name"` on images
- Product links: `href="/product-slug/PZN-number"`
- Prices: `>NN,NN €<` pattern
- UVP (list price) appears before sale price; sale price is lower

## Naver Shopping (search.shopping.naver.com)

**Anti-bot**: Aggressive. API returns 418, main page returns 405 for non-browser requests. `StealthyFetcher` required. Even then, may serve different HTML structure.

## General Korean E-commerce

Korean sites (쿠팡, 네이버, 11번가, G마켓) tend to have aggressive bot protection. Default approach:
1. Try `Fetcher` first
2. If blocked → `StealthyFetcher` with `headless=True, network_idle=True`
3. Parse with regex (CSS Modules make CSS selectors unreliable)
