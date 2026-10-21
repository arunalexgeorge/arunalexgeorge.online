# SEO testing report

21 October 2026, branch `seo/audit-and-implementation` against `master`
(`fb362c5`). "Confirmed" means the check was run and passed; anything that
could not be run is listed at the end.

## Build

| Check | Result |
|---|---|
| `npm run build` | Passes. 175 pages (174 + the new `/sitemap/`), no errors or warnings. Fonts: 2 files copied. |
| Product pages | 153, one per published product (unchanged). |
| Build output size | `dist/` 10 MB (portfolio PNG originals are no longer copied; responsive WebP/AVIF variants are). |

## Performance (Lighthouse 12.8.2)

Mobile form factor, simulated throttling (slow 4G, 4× CPU), Chrome headless,
against `astro preview` of each build on the same machine. Two baseline runs
are shown to give an idea of run-to-run variance. Lab data only; this is not
field (CrUX) data.

| Page | Perf before (run 1 / 2) | Perf after | LCP before (1 / 2) | LCP after | FCP before → after | Transfer before → after |
|---|---|---|---|---|---|---|
| `/` | 69 / 64 | **99** | 7.5 s / 7.5 s | **1.7 s** | 3.1–3.9 s → 0.9 s | 929 → 279 KiB |
| `/portfolio/` | 78 / 71 | **98** | 4.2 s / 4.9 s | **2.3 s** | 3.6–3.9 s → 0.8 s | 10,197 → 461 KiB |
| `/products/` | 68 / 68 | **100** | 5.4 s / 5.3 s | **1.5 s** | 4.2–4.3 s → 0.9 s | 274 → 274 KiB |
| `/products/parishcore/` | 72 / 67 | **80** | 5.9 s / 5.8 s | 5.5 s | 3.1–3.8 s → 0.9 s | 1,022 → 1,022 KiB |
| `/services/odoo-development/` | 82 / 73 | **100** | 3.9 s / 5.0 s | **1.5 s** | 3.0–3.8 s → 0.9 s | 260 → 261 KiB |
| `/about/` | 78 / 74 | **100** | 4.0 s / 5.3 s | **1.5 s** | 3.0–3.9 s → 0.9 s | 261 → 261 KiB |

CLS stayed at 0–0.004 on every page. TBT stayed between 0 and 110 ms.
Lighthouse SEO was 100 before and after; accessibility 94–96 and best
practices 96–100 did not change.

**Product pages remain the slowest:** their LCP is the cover image served from
`apps.odoocdn.com` (about 5.3 s to load under throttling). Only a `preconnect`
was added; see the roadmap for build-time optimisation of store images.

## Metadata and indexing (crawl of all built pages: 174 before, 175 after)

| Check | Before | After |
|---|---|---|
| Internal links without trailing slash | 7,013 | **0** |
| Broken internal links | 1 (`/resume.pdf`) | **0** |
| Duplicate titles | 0 | 0 |
| Pages with one H1 | 174 / 174 | 175 / 175 |
| Images without `alt` | 0 | 0 |
| Indexable pages whose canonical ≠ own URL | 0 | 0 |
| Noindex pages with a canonical | 3 (404, privacy, terms) | **0** |
| Noindex pages in sitemap | 2 (`/privacy/`, `/terms/`) | **0** |
| XML sitemap URLs | 173 | 171 (all indexable, all present in the build) |
| HTML sitemap | none | `/sitemap/`: 8 pages, 9 services, 153 products by category; linked from every footer |
| `og:image` that 404s | 21 pages (`/og-image.png`) | **0** |
| Titles over 65 characters | 6 | 1 ("Approval Chain Hub - Multi-Level Approvals for Any Model — Odoo App", 67: the store name itself is 56 characters) |
| Duplicate meta descriptions | 4 | 3 (only on noindex pages: 404, privacy, terms) |

## Structured data

| Check | Result |
|---|---|
| Schema.org Validator (`validator.schema.org`) on home, about, Odoo development, ParishCore, products, contact | **0 errors, 0 warnings** on each |
| JSON-LD parses on every page | 171 indexable pages, all valid JSON |
| Every `@id` reference resolves within the page graph | Yes, 0 dangling references |
| Every breadcrumb URL exists in the build | Yes |
| One JSON-LD block per page | Yes (product pages no longer have a second block) |
| Node counts | WebSite 171, Person 171, BreadcrumbList 170, WebPage 166, SoftwareApplication 153, Service 9, CollectionPage 3, ContactPage 1, ProfilePage 1 |

## Functional checks (headless Chrome, Puppeteer)

| Page | Status | JS errors | Notes |
|---|---|---|---|
| `/` | 200 | 0 | Theme toggle switches to light; mobile menu opens (`aria-expanded=true`) |
| `/about/`, `/services/`, `/services/ai-solutions/`, `/portfolio/`, `/resume/`, `/play/`, `/blog/` | 200 | 0 | |
| `/products/` | 200 | 0 | "AI" filter shows the 8 AI apps |
| `/products/parishcore/` | 200 | 0 | |
| `/contact/` | 200 | 0 | Form still posts to `api.web3forms.com`, 4 required fields |
| `/does-not-exist/` | 404 | 1 | The expected 404 for the page itself |
| `/sitemap/` | 200 | 0 | No horizontal overflow at 390 px; footer links fit on one line |

No broken images on any tested page; self-hosted Inter and Space Grotesk load.

## Mobile layout (390 × 844, device emulation)

| Page | Horizontal overflow before | After |
|---|---|---|
| `/` | **21 px** (industry tiles) | 0 |
| `/services/odoo-development/`, `/portfolio/`, `/products/parishcore/`, `/resume/` | 0 | 0 |

Screenshots of the new home links row and the service-page "Related Odoo Apps"
section were reviewed at 390 px. A missing space after "Also:" was found and
fixed.

## Live-site checks (before deploy)

| Check | Result |
|---|---|
| `http://arunalexgeorge.online/` | 200 — **no HTTPS redirect** (Cloudflare setting, not fixed) |
| `https://www.…/` | 301 → `http://` apex (Cloudflare/GitHub Pages) |
| `https://…/about` | 301 → `http://…/about/` (no longer linked internally on the branch) |
| `https://…/robots.txt`, `/sitemap-index.xml` | 200 |
| Unknown URL | 404 with the custom page |
| Product resync deploy (`fb362c5`) | GitHub Actions run 39579887662 succeeded; ParishCore shows Odoo 20.0 live |

## Could not be checked

- **Google Rich Results Test**: no API. The Schema.org Validator was used instead.
- **PageSpeed Insights / CrUX field data**: anonymous API quota exhausted (HTTP 429).
- **Search Console**: indexing, coverage, queries, sitemap status. No access.
- **Post-deploy behaviour**: the branch is not deployed, so HTTPS upgrade and
  redirects were only tested locally. After merging, re-run:
  `curl -sI https://arunalexgeorge.online/about/` (expect 200) and open
  `http://arunalexgeorge.online/` in a browser (expect a switch to https).
- **Real devices**: mobile checks used Chrome device emulation, not phones.
