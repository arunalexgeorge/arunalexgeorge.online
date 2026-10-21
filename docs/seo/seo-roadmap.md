# SEO roadmap — next 30, 60 and 90 days

21 October 2026. Ordered by impact relative to effort. SEO results take months
and cannot be guaranteed; the goals below are actions, not ranking promises.

## Needs your accounts (do first)

| # | Task | Where | Why |
|---|---|---|---|
| 1 | SSL/TLS mode **Full**; **Always Use HTTPS** on | Cloudflare → SSL/TLS | Stops plain-HTTP duplicates (audit P0-2). Then delete the HTTPS script at the top of `BaseLayout.astro`. |
| 2 | Redirect `www` → `https://arunalexgeorge.online` | Cloudflare → Rules → Redirect Rules | `www` currently redirects to HTTP. |
| 3 | Verify the domain property | [Google Search Console](https://search.google.com/search-console) → Add property → Domain → DNS TXT record in Cloudflare | Indexing, queries, CTR and positions. Nothing in these reports used Search Console data. |
| 4 | Submit `https://arunalexgeorge.online/sitemap-index.xml` | Search Console → Sitemaps | After the branch is deployed. |
| 5 | Same for Bing | [Bing Webmaster Tools](https://www.bing.com/webmasters) → import from Search Console | Bing also feeds DuckDuckGo and several AI assistants. |
| 6 | Decide on analytics consent | Code change, your decision | gtag loads before consent and "Decline" does not stop it (audit P3-4). Google Consent Mode v2, or load gtag only after "Accept". |

What to send back for the next round of analysis: a Search Console export
(Performance → last 3 months → queries and pages) and the Page indexing report.

## Days 0–30: ship and measure

1. **Merge and deploy** `seo/audit-and-implementation`. After the deploy:
   - `curl -sI https://arunalexgeorge.online/about/` → `200`
   - share a page on LinkedIn or WhatsApp: the preview shows the new image
   - Search Console URL Inspection on `/`, `/services/odoo-development/`,
     `/products/parishcore/`
2. **Request indexing** for the home page, the four Odoo service pages and
   the five industry product pages (Search Console, manually).
3. **Fill in the cost gap.** Add a "What affects the cost" section to
   `/services/odoo-implementation/` and `/services/odoo-customization/`:
   modules, data volume, integrations, custom reports, training. Only give
   figures you are willing to quote.
4. **Expand `/services/odoo-migration/`** with a "What I check before a
   migration" list: custom modules, deprecated APIs, data volume, third-party
   apps, OpenUpgrade coverage, rollback plan.
5. **Unify the contact email.** App Store descriptions say
   `admin@arunalexgeorge.online`, the site says `hello@`.
6. **Profiles.** Make LinkedIn, GitHub and the Odoo App Store author profile
   link to `https://arunalexgeorge.online/` and use the same title,
   "Senior Odoo Developer & ERP Consultant".

## Days 31–60: landing pages and first articles

1. **Two solution landing pages**, built only from verified product features:
   - `/solutions/church-management/`: primary keyword *church management
     software India*; secondary *parish management software*, *Odoo church
     management*. Families and Family Units, sacramental registers and
     certificates, dues and offerings in Odoo accounting, hall bookings. CTA:
     demo request via `/contact/`, link to `/products/parishcore/`.
   - `/solutions/temple-management/`: primary *temple management software
     Kerala*. Vazhipadu counter, nakshatra, hundi counting with witnesses,
     fund accounting, hall bookings. Link to `/products/temple-management/`.
   Each needs screenshots, an FAQ from real customer questions and a clear
   "runs on your own Odoo / server" explanation. Do not publish without them.
2. **Publish the first two articles** (briefs below) and remove `noIndex` from
   `/blog/`.
3. **Case studies.** Draft two from real projects, with client permission:
   problem, modules, what was built, outcome you can evidence. No invented
   metrics.

## Days 61–90: authority

1. Articles 3–5 below.
2. Outreach (below), one or two targets a week, personally.
3. **Optimise store images at build time.** Product page LCP is ~5.5 s
   because covers come from `apps.odoocdn.com`. Astro can download and
   convert them during the build (`image.domains`). Trade-off: longer builds
   and a dependency on the store CDN during deploys.
4. Review Search Console: pages at positions 8–20 with impressions are the
   best candidates for content updates; high-impression, low-CTR pages need
   better titles and descriptions.

## Content plan

Each article needs your own experience or screenshots; these are briefs for
you to write or review, not text to publish as is.

### 1. Odoo Community vs Enterprise: what you actually lose (and how to fill the gaps)
- **Audience:** SMEs choosing an edition; IT managers on Community.
- **Primary keyword:** odoo community vs enterprise.
  **Supporting:** difference, comparison, pricing, odoo community features.
- **Intent:** informational, with commercial follow-through.
- **Outline:** licence and hosting differences · apps missing in Community
  (Helpdesk, Subscriptions, Documents, Sign, Appointments, Field Service,
  Quality, Appraisal, Studio, Assets, Budgets, follow-up levels, financial
  reports) · options for each gap (Enterprise, OCA, App Store apps) · when
  Enterprise is the right call · total cost questions to ask.
- **Internal links:** the Community-gap product pages, `/services/erp-consulting/`.
- **CTA:** "Not sure which edition fits? Book a discovery call."
- **Evidence needed:** current Odoo pricing page (cite, date it), your own
  experience of when clients chose which.

### 2. Odoo migration checklist: upgrading custom modules safely
- **Audience:** companies on old versions with custom code.
- **Primary:** odoo migration checklist. **Supporting:** odoo upgrade custom
  modules, odoo migration guide.
- **Outline:** inventory of modules · Odoo upgrade service vs OpenUpgrade ·
  common breaking changes between recent versions · testing on a copy ·
  cutover and rollback · after go-live.
- **Internal links:** `/services/odoo-migration/`, `/services/odoo-development/`.
- **Evidence needed:** your real migration steps; version-specific examples.

### 3. How much does an Odoo implementation cost in India?
- **Primary:** odoo implementation cost in india.
- **Outline:** licence vs implementation cost · what drives effort · ranges
  only if you are willing to stand behind them · how to reduce cost.
- **Internal links:** `/services/odoo-implementation/`, `/contact/`.
- **Evidence needed:** your own pricing approach.

### 4. Running a parish on Odoo: registers, dues and certificates
- **Primary:** parish management software. **Supporting:** church management
  software with accounting, church management software India.
- **Outline:** paper registers to locked digital registers · family units ·
  dues and receipts with accounting · certificates with verification codes.
- **Internal links:** `/products/parishcore/`, church landing page.
- **Evidence needed:** screenshots with demo data; parish feedback if any.

### 5. Adding AI to Odoo without vendor lock-in
- **Primary:** odoo ai integration. **Supporting:** odoo ai module, odoo ai
  assistant.
- **Outline:** use cases that work (OCR bills, email drafting, ERP Q&A) ·
  bring-your-own-key model · data privacy choices · limits.
- **Internal links:** `/services/ai-solutions/`, AI product pages.

## Off-page and outreach plan

No paid links, link networks, fake reviews or automated outreach. Nothing has
been submitted anywhere.

| Priority | Target | Relevance | Angle |
|---|---|---|---|
| 1 | Odoo App Store author profile and every app's "Website" field | Already yours; 153 listings | Point to the matching `/products/<slug>/` page rather than only the home page |
| 1 | LinkedIn profile + featured section | Profile, high trust | Link to services and the two industry landing pages |
| 1 | GitHub profile README | Developer audience | Link site; pin open-source modules (e.g. Web Responsive Enterprise, LGPL) |
| 2 | Odoo Community Association (OCA) | Strongest Odoo community signal | Contribute fixes or modules; profile links back |
| 2 | Odoo forum (odoo.com/forum) | Where buyers ask questions | Answer real questions; link only when it genuinely helps |
| 2 | Capterra / GetApp / SoftwareSuggest listings for ParishCore and Temple Management | Church and temple searches show these directories | Free vendor listings with accurate features; reviews only from real customers |
| 2 | Kerala tech and startup ecosystem (Kerala Startup Mission listings, local developer meetups) | Local relevance | Talks or listings that naturally link to the site |
| 3 | Medium (existing account) | Already linked | Republish articles with a canonical link to the site |
| 3 | Dev.to / Hashnode | Developer reach | Technical Odoo tutorials with canonical to site |
| 3 | Diocese and parish networks, temple trusts | ParishCore / Temple buyers | Case study or demo; only with the organisation's agreement |
