# Keyword research and URL mapping

21 October 2026.

## What the data is, and is not

- **No search volumes or difficulty scores are given here.** No keyword tool
  with volume data (Google Keyword Planner, Ahrefs, Semrush) was available, and
  none is invented. Search Console data would be the best source once
  connected.
- **Demand signals used:** Google Autocomplete (`suggestqueries.google.com`,
  `gl=in`, `hl=en`) for 37 seed terms. A query appearing as a suggestion means
  people search it; order is a rough popularity hint, nothing more.
- **Competition signals used:** who ranks in web search results (the search
  tool is US-based, not Google India) and what those pages do. See
  competitor-analysis.md.

## Key observations

1. **Personal brand has no measurable search demand yet.** "arun alex george"
   returns no autocomplete suggestions, and a web search for
   `"Arun Alex George" Odoo` did not surface the site. Brand work is about
   being findable when someone already has the name (from the Odoo App Store,
   LinkedIn, a referral), not about volume.
2. **"Odoo developer" queries are mostly job seekers.** Suggestions:
   *odoo developer jobs, salary, remote jobs, jobs kochi, jobs in kerala,
   interview questions, internship*. The commercial versions are narrower:
   *odoo developer in india, odoo freelancer india, odoo implementation
   freelancer, odoo consultant freelancer*.
3. **Service queries with buyer intent exist and match the services pages:**
   *odoo implementation partners in india, odoo implementation cost in india,
   odoo customization services, odoo customization services kerala,
   odoo migration services, odoo upgrade service, odoo integration services,
   odoo integration api*.
4. **The industry products sit on real, specific demand:**
   - *odoo church management, odoo church management system*
   - *temple management software kerala* (the **first** suggestion for
     "temple management software"), *temple management software in india*
   - *dental lab management software india, dental lab management system*
   - *church management software india, church management software with
     accounting*
5. **"For Odoo Community" is a strong long-tail pattern:** *odoo helpdesk
   community, odoo community helpdesk module, odoo community subscription
   module, odoo whatsapp integration community, odoo community backend theme,
   odoo 19 backend theme*. About 20 of the catalogue's apps exist precisely to
   fill a gap in Community, and their store descriptions say so.
6. **AI + Odoo is an emerging cluster:** *odoo ai integration, odoo ai module,
   odoo ai app, odoo ai assistant, odoo integration with claude*.
7. **Comparison/informational queries** suit future articles, not service
   pages: *odoo community vs enterprise (difference, comparison, pricing,
   reddit)*, *odoo migration checklist, odoo migration guide, odoo upgrade
   script*, *odoo implementation methodology*.

## URL mapping

One primary keyword per page, so pages do not compete for the same intent.
Priority: H = act now, M = this quarter, L = later.

| Target URL | Primary keyword | Related keywords | Intent | Priority | Competitive landscape | Content gap | Action taken / recommended | Internal links |
|---|---|---|---|---|---|---|---|---|
| `/` | Arun Alex George (brand) + "Odoo developer India" | senior Odoo developer, ERP consultant Kerala | Navigational / commercial | H | Agencies (CodersFort, Cybrosys) own "Odoo company Kerala"; freelancer marketplaces own "Odoo freelancer" | No location or "Odoo" in old title | Title and description rewritten; hero roles lead with "Senior Odoo Developer" | → services, Odoo Development, products |
| `/about/` | Arun Alex George | Odoo developer Kochi, Odoo team lead | Navigational | H | None for the name | Generic "About" title | Title; `ProfilePage` schema | → resume, services, contact |
| `/services/` | Odoo development services | Odoo consulting services, ERP services India | Commercial | H | Agency service hubs | Generic title | Title, description, `CollectionPage` | → every service |
| `/services/odoo-development/` | Odoo custom module development | Odoo integration services, Odoo API integration | Commercial | H | Fiverr gigs, agencies, Cybrosys | No proof linked | Title; related apps (Helpdesk, WhatsApp, Subscriptions); related services | → customization, migration, AI, products |
| `/services/odoo-implementation/` | Odoo implementation services | Odoo implementation partners in India, implementation cost in India | Commercial | H | Official partners dominate "partners" | No cost guidance, no case studies | Title; related industry apps. **Recommend:** add an honest "what drives cost" section | → consulting, customization, migration |
| `/services/odoo-customization/` | Odoo customization services | customization services Kerala, customization company | Commercial | H | CodersFort, Cybrosys, Confianz | No local signal beyond footer | Title + description. **Recommend:** state Kochi/Kerala availability in body copy | → development, implementation |
| `/services/odoo-migration/` | Odoo migration services | Odoo upgrade service, upgrade version | Commercial | H | Softhealer, Innowise: long pages with process + FAQ + `Service` schema | Thin compared with competitors (process list only) | Title + description. **Recommend:** expand with what is checked before a migration | → development, customization, cloud |
| `/services/erp-consulting/` | Odoo ERP consulting | ERP consultant India | Commercial | M | Agencies | — | Title + description | → implementation, customization |
| `/services/ai-solutions/` | Odoo AI integration | Odoo AI module, AI assistant, integration with Claude | Commercial | M | Few established players | — | Title; related AI apps | → development, AI apps |
| `/services/website-development/` | website development (WordPress) | — | Commercial | L | Saturated | Not an Odoo strength | Title + description | → custom software, cloud |
| `/services/custom-software/` | custom software development Python | — | Commercial | L | Saturated | — | Title | → Odoo development |
| `/services/cloud-devops/` | Odoo hosting / server setup | Docker, CI/CD | Commercial | L | Odoo.sh, hosting firms | Page does not mention Odoo hosting explicitly | Title. **Recommend:** only target "Odoo hosting" if you offer it | → implementation, migration |
| `/products/` | Odoo apps | Odoo modules, Odoo Community apps | Commercial / navigational | H | Odoo App Store itself | — | Title with count and version range | → every product |
| `/products/parishcore/` | Odoo church management | church management software India, parish management software, church management software with accounting | Commercial | H | Parishinfo, Kristapp (Kerala), ParishSOFT, ChurchTrac (US); one Odoo membership-form app | No dedicated landing content beyond store description | Curated title + description. **Recommend:** a "Church & parish management" landing page (see roadmap) | → Odoo implementation |
| `/products/temple-management/` | temple management software Kerala | temple management software India, pooja/vazhipadu booking software | Commercial | H | Vyapar (generic billing), BookSeva (seva booking), ITMS (state devaswom) | None target Odoo | Curated title + description | → Odoo implementation |
| `/products/dental-lab-management/` | dental lab management software India | dental lab management system | Commercial | H | DentLabSoft, OralStop, Dental APT | None target Odoo | Curated title + description | → Odoo implementation |
| `/products/auto-sales-management/`, `/products/auto-service-management/` | Odoo automotive dealer / workshop software | vehicle dealership software, job card software | Commercial | M | — | — | Curated titles | → Odoo implementation |
| Community-gap apps (Helpdesk, Subscriptions, Documents, Knowledge, eSign, Appointments, Field Service, Studio Lite, Quality, Appraisal, WhatsApp, Payroll India, Barcode, Assets, Follow-ups, Budgets, Auralis, Web Responsive Enterprise) | "<feature> for Odoo Community" | odoo community <feature> module | Commercial | H | Other App Store vendors' pages (e.g. `helpdesk_community`) | Store titles don't say "Community" | Curated titles in `src/data/product-seo.ts` | → Odoo customization |
| `/portfolio/` | web design portfolio | — | Navigational | L | — | — | Title + description | → website development |
| `/resume/` | Arun Alex George resume | — | Navigational | L | — | Broken PDF link | Title; print-to-PDF | → about, contact |
| `/contact/` | hire Odoo developer | Odoo consultant contact | Transactional | H | — | — | Title + description, `ContactPage` | — |
| `/blog/` | — | — | — | — | — | Empty | `noindex` until articles exist | — |

## Keywords deliberately not targeted

- **"odoo developer jobs / salary / interview questions"**: job seekers, not
  clients. A careers or interview article could attract them, but it would not
  bring in projects.
- **GPU cloud, cloud gaming, GPU virtual desktops, LLM hosting**: the only
  related work on the site is a website built for InstaGPU (portfolio). There
  is no service or product here to rank for these, so no pages were created.
- **City-by-city pages** ("Odoo developer in Dubai / Bangalore / …"): these
  would be doorway pages. Only Kochi / Kerala / India appear, matching the
  address already published on the site.
- **"Odoo partner"**: you are not an official Odoo partner on the site, so this
  is not claimed.
