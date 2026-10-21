# SEO audit — arunalexgeorge.online

Baseline audit, 21 October 2026. Every finding below was observed on the live
site or in the production build of `master` at `fb362c5`. Nothing here is
hypothetical; where something could not be checked, that is stated.

## How the audit was done

| Area | Method |
|---|---|
| Stack | Read the repo: Astro 7.0.6 static site, `@astrojs/sitemap` 3.7.3, React islands, deployed to GitHub Pages by `.github/workflows/deploy.yml` on every push to `master`, served through Cloudflare (`server: cloudflare`, `x-github-request-id`). Product catalogue generated from the Odoo App Store by `scripts/sync_odoo_apps.py`. Not WordPress, so no SEO plugin is involved. |
| Live HTTP behaviour | `curl` against every scheme/host/slash variant, robots.txt, sitemaps, missing assets. |
| On-page | A crawler (`audit.py`, kept outside the repo) parsed all 174 built pages: titles, descriptions, canonicals, robots, headings, image alt/dimensions, internal links, JSON-LD. |
| Performance | Lighthouse 12.8.2, mobile, simulated throttling, against a local `astro preview` of the `master` build, 6 pages × 2 runs. PageSpeed Insights could not be used: the anonymous API quota was exhausted (HTTP 429). |
| Search data | No Google Search Console or Analytics access was available. Nothing in this audit is based on Google ranking or traffic data. |

## Stack and existing SEO

- One layout (`src/layouts/BaseLayout.astro`) owns `<head>`: title, description,
  canonical, Open Graph, Twitter card, favicons, Google Fonts, gtag
  (`G-LKG8YLNEEK`) and a site-wide `Person` JSON-LD block.
- Product pages already emitted `SoftwareApplication` JSON-LD.
- `robots.txt` allows everything except `/404` and points to `sitemap-index.xml`.
- `privacy` and `terms` are `noindex, nofollow`; `404` is `noindex`.
- Lighthouse SEO category scored 100 on every tested page. The issues below are
  ones that category does not test.

## Findings

### P0 — Critical

#### P0-1 Internal links redirect visitors from HTTPS to plain HTTP
- **Evidence:** `curl -I https://arunalexgeorge.online/about` →
  `301 location: http://arunalexgeorge.online/about/`, which then answers
  `200` over HTTP. The same happens for every page linked without a trailing
  slash. The crawl counted **7,013 internal links without a trailing slash**
  across 174 pages: every nav, footer, card and product link.
- **Cause:** GitHub Pages adds the slash with a redirect; behind Cloudflare it
  sees the request as HTTP and builds an `http://` location.
- **Affected URLs:** every page except `/`.
- **Impact:** visitors who click any internal link end up on an unencrypted
  page (browser "Not secure" warning, contact form on HTTP). Google sees a
  redirect chain on every internal link. Canonicals already pointed to the
  HTTPS slash URLs, which limited the indexing damage.
- **Fix:** link every page with a trailing slash; `trailingSlash: 'always'`.
- **Status:** fixed on branch `seo/audit-and-implementation`.
- **Verification:** crawl of the new build finds 0 slashless internal links.

#### P0-2 Plain HTTP is served without redirecting to HTTPS
- **Evidence:** `curl -I http://arunalexgeorge.online/` → `200`.
  `https://www.…/` → `301 http://arunalexgeorge.online/` (redirects to HTTP).
- **Impact:** two copies of every page (HTTP and HTTPS); www links land on HTTP.
- **Fix:** Cloudflare → SSL/TLS → set mode to **Full**, and Edge Certificates →
  **Always Use HTTPS** on. Optionally a redirect rule `www` → `https://apex`.
- **Status:** fixed on 21 October 2026 in Cloudflare (mode Full, Always Use
  HTTPS, `www` redirect). The interim inline HTTPS script was then removed.
- **Verification:** `curl -I http://arunalexgeorge.online/` → `301
  https://arunalexgeorge.online/`; `https://www.…/` → `301` to the HTTPS
  apex; `https://…/about` → `301 https://…/about/`.

### P1 — High

| ID | Finding | Evidence | Fix | Status |
|---|---|---|---|---|
| P1-1 | Default social image missing | `/og-image.png` → 404; used as `og:image` on 21 pages, so shares had no preview image | Generated a 1200×630 image (`npm run generate:social`) | Fixed |
| P1-2 | Linked favicons missing | `/favicon-32x32.png`, `/apple-touch-icon.png` → 404 | Generated from `favicon.svg` | Fixed |
| P1-3 | Generic titles that do not say what the page offers | e.g. "Odoo Development — Arun Alex George", "Products — Arun Alex George", home "ERP Consultant & Solution Architect" without "Odoo" | Keyword-mapped titles for every page (see keyword-research.md) | Fixed |
| P1-4 | Home LCP 7.5 s (mobile) | Lighthouse: LCP element is the hero paragraph with 7,075 ms render delay; hero content had `opacity: 0` until the bundled reveal script ran | Hero animates with transform only; reveal observer runs inline | Fixed; LCP 1.7 s |
| P1-5 | Render-blocking Google Fonts CSS on every page | Lighthouse: ~1.2 s blocking from `fonts.googleapis.com` | Self-hosted via the Astro Fonts API with preloads and metric fallbacks | Fixed |
| P1-6 | Portfolio page loads 10.2 MB | 7 PNG screenshots, 0.5–4.3 MB each, up to 3360 px wide | Responsive WebP via `astro:assets` | Fixed; 461 KiB |
| P1-7 | 680 KB hero avatar PNG | Served unresized on every home visit | Responsive AVIF/WebP `<Picture>` (4.5–19 KB) | Fixed |
| P1-8 | Core Odoo services barely linked from the home page | Home service cards linked ERP Consulting, Custom Software, Website, Cloud; Odoo development/implementation/customization/migration had no home links | Odoo Development card plus a links row for the other Odoo services | Fixed |

### P2 — Medium

| ID | Finding | Evidence | Fix | Status |
|---|---|---|---|---|
| P2-1 | Sitemap lists noindex pages | `/privacy/`, `/terms/` in `sitemap-0.xml` while `noindex` | Sitemap filter | Fixed |
| P2-2 | Thin "Coming soon" blog page indexed | `/blog/` has no articles | `noindex` until the first article; out of sitemap | Fixed |
| P2-3 | Broken resume download | `/resume.pdf` → 404 (only file is an old copy in the git-ignored `_old/`) | "Save as PDF" print button + print stylesheet | Fixed |
| P2-4 | Structured data limited to one `Person` blob | No `WebSite`, `WebPage`, `BreadcrumbList`, `Service`; product schema not linked to the person | One `@graph` per page with stable `@id`s | Fixed |
| P2-5 | No internal links between related services or from services to apps | Service pages linked only to `/services/` and `/contact/` | "Related services" and "Related Odoo apps" sections | Fixed |
| P2-6 | Product pages: LCP 5.5–5.9 s | LCP is the cover image hosted on `apps.odoocdn.com` (5.3 s load) | Added `preconnect`; image itself not optimised (remote) | Partly fixed |
| P2-7 | Home page scrolls sideways on phones | At 390 px, `scrollWidth` 411: industry tiles could not shrink | `minmax(0, 1fr)` columns | Fixed |
| P2-8 | `404` page had a canonical to `/404/` | Built `404.html` | Canonical omitted on noindex pages | Fixed |
| P2-9 | Stale "Odoo ERP (v10–v19)" | Services and resume; catalogue now covers 20.0 | Derived from catalogue | Fixed |
| P2-10 | Hero avatar alt text described it as a portrait | It is an illustrated 3D avatar | Alt text corrected | Fixed |
| P2-11 | No human-readable sitemap | Only the XML sitemap existed; 153 product pages were reachable only through `/products/` | HTML sitemap at `/sitemap/`, linked from every footer; `<link rel="sitemap">` in every page head | Fixed |

### P3 — Long-term

| ID | Finding | Evidence | Recommendation |
|---|---|---|---|
| P3-1 | Weak brand visibility | No Google autocomplete suggestion for "arun alex george"; a web search for `"Arun Alex George" Odoo` did not return the site | Consistent profiles linking back (LinkedIn, GitHub, Odoo App Store author page, Medium); see roadmap |
| P3-2 | No articles | Blog empty; Medium link only | Content plan in seo-roadmap.md |
| P3-3 | No case studies | Claims such as "20+ implementations" have no supporting pages | Write case studies when client permission allows |
| P3-4 | Analytics loads before cookie consent | gtag loads unconditionally; "Decline" only hides the banner | Google Consent Mode v2 or load gtag after "Accept" — your decision, not changed |
| P3-5 | Two contact emails | Site uses `hello@`, App Store descriptions use `admin@arunalexgeorge.online` | Pick one public address |
| P3-6 | Footer column titles are `<h4>` after `<h2>` sections | Heading level skip on every page | Cosmetic; change to styled `<p>` or `<h2>` when convenient |
| P3-7 | Person image is an illustration | Knowledge panels and profiles favour a real photo | Add a real headshot if you want one |

## Not checked

- Google Search Console coverage, queries, CTR, positions, sitemap status: no access.
- Google Analytics traffic and conversions: no access.
- Field Core Web Vitals (CrUX): PageSpeed Insights API quota exhausted.
- Google Rich Results Test: no API; Schema.org Validator used instead.
- Backlink profile: no backlink tool available.
