#!/usr/bin/env python3
"""Sync the product catalogue with the Odoo App Store.

Crawls the author listings for apps and themes, which only ever contain
published products, then fetches each product's store page for its details
and description. Writes:

  src/data/odoo-apps.json           generated catalogue, never edit by hand
  src/data/product-categories.json  curated site category per technical name;
                                    newly published products are added with a
                                    guessed category, review them after a sync

Run with `npm run sync:apps`. Standard library only.
"""

from __future__ import annotations

import datetime as dt
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path

STORE = "https://apps.odoo.com"
AUTHOR = "Arun A George"
KINDS = {"modules": "app", "themes": "theme"}
ROOT = Path(__file__).resolve().parent.parent
CATALOGUE_PATH = ROOT / "src/data/odoo-apps.json"
CATEGORIES_PATH = ROOT / "src/data/product-categories.json"
USER_AGENT = "Mozilla/5.0 (compatible; arunalexgeorge.online catalogue sync)"
WORKERS = 6

# Fallback when a newly published product has no curated site category yet.
STORE_TO_SITE_CATEGORY = {
    "Accounting": "Accounting", "Invoicing": "Accounting",
    "Sales": "Sales", "CRM": "Sales", "Point of Sale": "Sales",
    "Inventory": "Warehouse", "Warehouse": "Warehouse",
    "Purchase": "Purchase", "Purchases": "Purchase",
    "Human Resources": "HR", "Employees": "HR", "Attendances": "HR",
    "Human Resources Payroll": "HR", "Payroll": "HR", "Recruitment": "HR",
    "Manufacturing": "Manufacturing",
    "Marketing": "Marketing", "Email Marketing": "Marketing", "Surveys": "Marketing",
    "Website": "Website", "eCommerce": "Website",
    "Field Service": "Operations", "Services": "Operations", "Contracts": "Operations",
    "Industries": "Industry",
}

CARD_RE = re.compile(
    r'<div class="loempia_app_entry[^"]*"[^>]*data-publish="(?P<publish>\w+)"[^>]*>\s*'
    r'<a href="/apps/(?P<kind>modules|themes)/(?P<series>[\d.]+)/(?P<tech>[\w.-]+)">'
    r"(?P<body>.*?)</a>",
    re.S,
)


def fetch(url: str, tries: int = 4) -> str:
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=60) as res:
                return res.read().decode("utf-8", "replace")
        except Exception:
            if attempt == tries - 1:
                raise
            time.sleep(2 * (attempt + 1))
    raise AssertionError("unreachable")


def clean_text(value: str) -> str:
    text = html.unescape(re.sub(r"<[^>]+>", "", value))
    # A few summaries are double-escaped upstream ("Profit &amp; Loss").
    if re.search(r"&(#\d+|[a-zA-Z]+);", text):
        text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def absolute(url: str) -> str:
    return "https:" + url if url.startswith("//") else urllib.parse.urljoin(STORE, url)


def parse_price(raw: str) -> float:
    if raw.upper() == "FREE":
        return 0.0
    match = re.fullmatch(r"\$\s*([\d,]+(?:\.\d+)?)", raw)
    if not match:
        raise ValueError(f"expected a USD price, got {raw!r}")
    return float(match.group(1).replace(",", ""))


# --- Listings --------------------------------------------------------------

def listing_url(kind: str, page: int, series: str | None) -> str:
    path = f"/apps/{kind}/browse" + (f"/page/{page}" if page > 1 else "")
    query = {"author": AUTHOR, **({"series": series} if series else {})}
    return f"{STORE}{path}?{urllib.parse.urlencode(query)}"


def crawl_listing(kind: str, series: str | None = None) -> tuple[list[dict], str]:
    """Every card on every page of one author listing, plus the first page's HTML."""
    first = fetch(listing_url(kind, 1, series))
    last = max([1, *map(int, re.findall(rf"/apps/{kind}/browse/page/(\d+)", first))])
    pages = [first] + [fetch(listing_url(kind, p, series)) for p in range(2, last + 1)]
    cards = []
    for page in pages:
        for m in CARD_RE.finditer(page):
            body = m.group("body")
            name = re.search(r'<h5 title="([^"]*)"', body)
            summary = re.search(r'loempia_panel_summary">(.*?)</p>', body, re.S)
            price = re.search(r'loempia_panel_price[^"]*">\s*<b>(.*?)</b>', body, re.S)
            cards.append({
                "publish": m.group("publish"),
                "kind": m.group("kind"),
                "series": m.group("series"),
                "tech": m.group("tech"),
                "name": clean_text(name.group(1)) if name else m.group("tech"),
                "summary": clean_text(summary.group(1)) if summary else "",
                "price": clean_text(price.group(1)) if price else "",
            })
    return cards, first


def listed_series(first_page: str) -> list[str]:
    return sorted(set(re.findall(r'\?series=([\d.]+)&amp;author=', first_page)), key=float)


# --- Description sanitiser -------------------------------------------------

VOID = {"br", "hr", "img", "input", "meta", "link", "source", "wbr", "col", "area", "base", "embed", "param", "track"}
DROP = {"script", "style", "iframe", "object", "embed", "form", "input", "button", "select", "textarea", "noscript", "svg", "video", "audio", "head", "title"}
KEEP = {
    "section", "div", "p", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li", "b", "strong", "i", "em", "u",
    "a", "img", "br", "hr", "code", "pre", "small", "blockquote", "sup", "sub", "table", "thead", "tbody",
    "tfoot", "tr", "td", "th", "figure", "figcaption", "span",
}
RENAME = {"tt": "code", "h1": "h2"}  # the page itself owns the only <h1>
COLUMN_RE = re.compile(r"\b(oe_span\d+|col(-(xs|sm|md|lg|xl))?(-\d+)?)\b")


class Node:
    def __init__(self, tag: str | None, attrs: dict | None = None, text: str = ""):
        self.tag, self.attrs, self.text, self.children = tag, attrs or {}, text, []


class TreeBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("root")
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = Node(tag, {k: v or "" for k, v in attrs})
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.stack[-1].children.append(Node(tag, {k: v or "" for k, v in attrs}))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        self.stack[-1].children.append(Node(None, text=data))


def is_banner_section(node: Node) -> bool:
    """An opening section that only shows the banner, which the page already uses as its cover."""
    imgs, text = [], []

    def walk(n):
        if n.tag == "img":
            imgs.append(n)
        elif n.tag is None:
            text.append(n.text.strip())
        for c in n.children:
            walk(c)

    walk(node)
    return len(imgs) == 1 and not "".join(text) and "banner" in imgs[0].attrs.get("src", "")


def is_column_row(node: Node) -> bool:
    """A row of side-by-side columns, laid out with Odoo/Bootstrap column classes or inline flex/grid."""
    kids = [c for c in node.children if c.tag]
    if sum(1 for c in kids if COLUMN_RE.search(c.attrs.get("class", ""))) >= 2:
        return True
    style = node.attrs.get("style", "")
    return (sum(1 for c in kids if c.tag == "div") >= 2
            and bool(re.search(r"display\s*:\s*(flex|grid)", style))
            and not re.search(r"flex-direction\s*:\s*column", style))


def is_pill(node: Node) -> bool:
    style = node.attrs.get("style", "")
    return "badge" in node.attrs.get("class", "").split() or ("inline-block" in style and "border-radius" in style)


def render(node: Node, in_pre: bool = False) -> str:
    if node.tag is None:
        return html.escape(node.text if in_pre else re.sub(r"\s+", " ", node.text), quote=False)
    if node.tag in DROP:
        return ""
    inner = "".join(render(c, in_pre or node.tag == "pre") for c in node.children)
    tag = RENAME.get(node.tag, node.tag)
    if tag not in KEEP:
        return inner
    a = node.attrs
    out = {}
    if tag == "a":
        href = a.get("href", "").strip()
        if not re.match(r"(https?:|mailto:|//)", href):
            return inner
        out["href"] = absolute(href) if href.startswith("//") else href
        if not href.startswith("mailto:"):
            out.update(target="_blank", rel="noopener noreferrer")
    elif tag == "img":
        src = a.get("src", "").strip()
        if not src or src.startswith("data:"):
            return ""
        out = {"src": absolute(src), "alt": a.get("alt", ""), "loading": "lazy", "decoding": "async"}
    elif tag in ("td", "th"):
        out = {k: a[k] for k in ("colspan", "rowspan") if a.get(k, "").isdigit()}

    classes = []
    if tag == "div" and is_column_row(node):
        classes.append("d-cols")
    if tag == "span" and is_pill(node):
        classes.append("d-pill")
    if re.search(r"text-align\s*:\s*center", a.get("style", "")) or {"text-center", "oe_slogan"} & set(a.get("class", "").split()):
        classes.append("d-center")
    if classes:
        out["class"] = " ".join(classes)

    if tag in ("span", "div") and not out:
        if tag == "span" or not inner.strip():
            return inner
    attrs = "".join(f' {k}="{html.escape(v)}"' for k, v in out.items())
    if tag in VOID:
        return f"<{tag}{attrs}>"
    if not inner.strip() and tag not in ("td", "th"):
        return ""
    return f"<{tag}{attrs}>{inner}</{tag}>"


def sanitise_description(fragment: str) -> str:
    builder = TreeBuilder()
    builder.feed(fragment)
    builder.close()
    top = [c for c in builder.root.children if c.tag or c.text.strip()]
    # Descend through single wrappers to the list of sections.
    while len(top) == 1 and top[0].tag == "div":
        top = [c for c in top[0].children if c.tag or c.text.strip()]
    if top and top[0].tag == "section" and is_banner_section(top[0]):
        top = top[1:]
    return "".join(render(c) for c in top).strip()


# --- Product pages ---------------------------------------------------------

def parse_product_page(page: str) -> dict:
    def find(pattern, default=None, flags=re.S):
        m = re.search(pattern, page, flags)
        return m.group(1) if m else default

    desc = find(r'<div class="tab-pane active" id="desc">(.*?)<div class="tab-pane" id="manifest">')
    if desc is None:
        raise ValueError("description tab not found")
    availability = find(r'class="loempia_platform_availability[^"]*">(.*?)</td>', "")
    platforms = {
        label.strip(): icon == "check"
        for icon, label in re.findall(r'fa-(check|times)"[^>]*></i>\s*(?:<span>)?\s*([\w. -]+?)\s*<', availability)
    }
    deps_block = find(r'id="resetCollapse">(.*?)</div>', "")
    loc = find(r"Lines of code</b>.*?<td><span>(\d+)</span>")
    icon = find(r'loempia_app_icon big" src="([^"]+)"')
    cover = find(r"loempia_app_cover[^>]*background-image:\s*url\(([^)]+)\)")
    return {
        "storeCategory": clean_text(find(r'itemprop="applicationCategory" href="[^"]*">([^<]*)<', "")),
        "license": clean_text(find(r"<td><b>License</b></td><td>(.*?)</td>", "")),
        "linesOfCode": int(loc) if loc else None,
        "availability": {
            "odooOnline": platforms.get("Odoo Online", False),
            "odooSh": platforms.get("Odoo.sh", False),
            "onPremise": platforms.get("On Premise", False),
        },
        "dependencies": [
            {"technicalName": href.rsplit("/", 1)[-1], "name": clean_text(name), "storeUrl": absolute(href)}
            for href, name in re.findall(r'<a href="([^"]+)">([^<]+)</a>', deps_block)
        ],
        "icon": absolute(re.sub(r"/icon_image/\d+x\d+", "/icon_image/128x128", html.unescape(icon))) if icon else None,
        "cover": absolute(html.unescape(cover)) if cover else None,
        "description": sanitise_description(desc),
    }


# --- Main ------------------------------------------------------------------

def guess_category(product: dict) -> str:
    if product["kind"] == "theme":
        return "Theme"
    if re.search(r"(^|\W)AI(\W|$)", product["name"]):
        return "AI"
    return STORE_TO_SITE_CATEGORY.get(product["storeCategory"], "Productivity")


def main() -> int:
    pool = ThreadPoolExecutor(WORKERS)

    # 1. Published products: the author listings only show published ones.
    listings = dict(zip(KINDS, pool.map(crawl_listing, KINDS)))
    published = {}
    for kind, (cards, _) in listings.items():
        for card in cards:
            if card["publish"] == "on":
                published[card["tech"]] = card
    if not published:
        print("No published products found; the store markup may have changed. Nothing written.", file=sys.stderr)
        return 1

    # 2. Published series per product, from the per-series listings.
    series_jobs = [(kind, s) for kind, (_, first) in listings.items() for s in listed_series(first)]
    versions: dict[str, set[str]] = {}
    for (kind, series), (cards, _) in zip(series_jobs, pool.map(lambda job: crawl_listing(*job), series_jobs)):
        for card in cards:
            if card["publish"] == "on":
                versions.setdefault(card["tech"], set()).add(series)

    # 3. Each product's store page, at its newest published series.
    def product(card):
        series = sorted(versions.get(card["tech"]) or {card["series"]}, key=float)
        store_url = f"{STORE}/apps/{card['kind']}/{series[-1]}/{card['tech']}"
        return {
            "technicalName": card["tech"],
            "kind": KINDS[card["kind"]],
            "name": card["name"],
            "summary": card["summary"],
            "price": parse_price(card["price"]),
            "versions": series,
            "storeUrl": store_url,
            **parse_product_page(fetch(store_url)),
        }

    products = sorted(pool.map(product, published.values()), key=lambda p: p["technicalName"])

    # 4. Curated categories: keep existing, guess for new products.
    categories = json.loads(CATEGORIES_PATH.read_text()) if CATEGORIES_PATH.exists() else {}
    guessed = []
    for p in products:
        if p["technicalName"] not in categories:
            categories[p["technicalName"]] = guess_category(p)
            guessed.append(p)

    previous = {}
    if CATALOGUE_PATH.exists():
        previous = {p["technicalName"]: p for p in json.loads(CATALOGUE_PATH.read_text())["products"]}

    CATALOGUE_PATH.write_text(json.dumps({
        "syncedAt": dt.date.today().isoformat(),
        "currency": "USD",
        "products": products,
    }, indent=2, ensure_ascii=False) + "\n")
    CATEGORIES_PATH.write_text(json.dumps(dict(sorted(categories.items())), indent=2, ensure_ascii=False) + "\n")

    # 5. Report what changed.
    current = {p["technicalName"]: p for p in products}
    apps = sum(p["kind"] == "app" for p in products)
    print(f"Synced {len(products)} published products ({apps} apps, {len(products) - apps} themes).")
    for title, techs in (("Added", current.keys() - previous.keys()), ("Removed", previous.keys() - current.keys())):
        for tech in sorted(techs):
            print(f"  {title}: {(current.get(tech) or previous[tech])['name']} ({tech})")
    for tech in sorted(current.keys() & previous.keys()):
        old, new = previous[tech], current[tech]
        for field in ("price", "versions", "name"):
            if old[field] != new[field]:
                print(f"  Changed {field}: {new['name']}: {old[field]} -> {new[field]}")
    for p in guessed:
        print(f"  Review category: {p['name']} ({p['technicalName']}) -> {categories[p['technicalName']]}"
              f" [store: {p['storeCategory']}] in {CATEGORIES_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
