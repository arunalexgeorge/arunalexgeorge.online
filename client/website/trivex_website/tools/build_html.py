#!/usr/bin/env python3
"""Multi-page static-site generator for Trivex Industrial Solutions.
Dependency-free. Emits clean directory-index URLs (e.g. /products/<slug>/).
Run: python3 tools/build_html.py   (writes into the project root)
Data-driven: products/services/industries/projects live in the tables below."""
import os, html, json, shutil, hashlib, textwrap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__))

def asset_ver(rel):
    """Short content hash for cache-busting a static asset (?v=...).
    Ensures browsers/CDNs fetch a fresh copy whenever the file changes."""
    try:
        with open(os.path.join(ROOT, rel), "rb") as f:
            return hashlib.md5(f.read()).hexdigest()[:8]
    except OSError:
        return "0"

CSS_VER = asset_ver("assets/css/styles.css")
JS_VER  = asset_ver("assets/js/main.js")

# ---------- Config ----------
# BASE_PATH: URL sub-path prefix for hosting under a folder (e.g. GitHub Pages project site "/repo").
# SITE_URL:  absolute site origin (used for canonical / OG / sitemap). Both overridable via env.
BASE   = os.environ.get("BASE_PATH", "").rstrip("/")
SITE   = os.environ.get("SITE_URL", "https://trivexindustrialsolutions.com").rstrip("/")
YEAR   = 2025
PHONE_DISPLAY = "+971 6 534 6311"
PHONE_TEL     = "+97165346311"
PHONE2_DISPLAY = "+971 50 584 0555"        # second number (no WhatsApp)
PHONE2_TEL     = "+971505840555"
EMAIL  = "sales@trivexindustrialsolutions.com"
WHATSAPP_NUMBER = "97165346311"            # international format, no +/spaces
ADDRESS = "Warehouse Q3-65, SAIF Zone, Sharjah, United Arab Emirates"

# EmailJS — client-side delivery for the quote form (no backend needed).
# All three IDs are public by design: they ship inside the page source, and abuse is
# contained in the EmailJS dashboard via the allow-listed domain + monthly quota, not by
# keeping them secret. Leave any of them blank and the form falls back to the mailto: handoff.
EMAILJS_PUBLIC_KEY  = os.environ.get("EMAILJS_PUBLIC_KEY",  "")
EMAILJS_SERVICE_ID  = os.environ.get("EMAILJS_SERVICE_ID",  "")
EMAILJS_TEMPLATE_ID = os.environ.get("EMAILJS_TEMPLATE_ID", "")

# Vectorised wordmark logo (traced from client_data/logo_green.jpeg)
_logo_vb, _logo_inner = open(os.path.join(HERE, "data/logo_symbol.txt")).read().split("\n", 1)
_logo_inner = _logo_inner.strip()

def logo(cls=""):
    return f'<svg class="tlogo {cls}" viewBox="{_logo_vb}" role="img" aria-label="Trivex Industrial Solutions"><use href="#trivexLogo"/></svg>'

def esc(s): return html.escape(str(s), quote=True)
def wa_link(msg):
    from urllib.parse import quote
    return f"https://wa.me/{WHATSAPP_NUMBER}?text={quote(msg)}"

def prod_img(slug):
    """Product image URL — prefer a transparent .png when one exists, else .jpg."""
    ext = ".png" if os.path.exists(os.path.join(ROOT, "assets", "img", "products", f"{slug}.png")) else ".jpg"
    return f"/assets/img/products/{slug}{ext}"

# ---------- SVG icons ----------
def _svg(body, sw="1.8"):
    return (f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>')
IC = {
 "arrow": _svg('<path d="M5 12h14M13 6l6 6-6 6"/>'),
 "arrow-ur": _svg('<path d="M7 17 17 7M8 7h9v9"/>'),
 "plus": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M12 6v12M6 12h12"/></svg>',
 "chevron": _svg('<path d="m6 9 6 6 6-6"/>'),
 "chevron-r": _svg('<path d="m9 6 6 6-6 6"/>'),
 "check": _svg('<path d="M20 6 9 17l-5-5"/>'),
 "phone": _svg('<path d="M4 4h4l2 5-2.5 1.5a11 11 0 0 0 6 6L15 14l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 2 6a2 2 0 0 1 2-2z"/>'),
 "mail": _svg('<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>'),
 "globe": _svg('<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a15 15 0 0 1 0 18 15 15 0 0 1 0-18z"/>'),
 "pin": _svg('<path d="M12 21s7-6.3 7-11a7 7 0 1 0-14 0c0 4.7 7 11 7 11z"/><circle cx="12" cy="10" r="2.6"/>'),
 "whatsapp": '<svg viewBox="0 0 32 32" fill="currentColor" aria-hidden="true"><path d="M16 3C9 3 3.5 8.5 3.5 15.5c0 2.3.6 4.5 1.8 6.5L3 29l7.2-2.2c1.9 1 4 1.6 6.1 1.6 6.9 0 12.5-5.6 12.5-12.5S22.9 3 16 3zm0 22.7c-1.9 0-3.7-.5-5.3-1.5l-.4-.2-4.3 1.3 1.3-4.1-.3-.4a10 10 0 0 1-1.6-5.6C5.1 9.9 9.9 5.2 16 5.2S26.9 9.9 26.9 15.6 22.1 25.7 16 25.7zm5.9-7.6c-.3-.2-1.9-.9-2.2-1-.3-.1-.5-.2-.7.2s-.8 1-1 1.2c-.2.2-.4.2-.7.1-1.9-.9-3.1-1.7-4.4-3.8-.3-.6.3-.5.9-1.7.1-.2 0-.4 0-.6s-.7-1.7-1-2.3c-.3-.6-.5-.5-.7-.5h-.6c-.2 0-.6.1-.9.4-1.3 1.3-1.3 3.1-.1 5 .3.5 2.5 4 6.1 5.5 2.3 1 3.2 1.1 4.3.9.7-.1 1.9-.8 2.2-1.6.3-.8.3-1.4.2-1.6-.1-.1-.3-.2-.6-.3z"/></svg>',
 "download": _svg('<path d="M12 3v12m0 0 4-4m-4 4-4-4M4 21h16"/>'),
 "clock": _svg('<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>'),
 "layers": _svg('<path d="m12 3 9 5-9 5-9-5 9-5zM3 13l9 5 9-5"/>'),
 "shield": _svg('<path d="M12 3 5 6v5c0 4.4 3 8 7 10 4-2 7-5.6 7-10V6l-7-3z"/>'),
 "wrench": _svg('<path d="M14 6a4 4 0 0 0 5 5l-8 8a3 3 0 0 1-4-4l7-9z"/>'),
 "factory": _svg('<path d="M3 21V9l6 4V9l6 4V6l6 3v12H3z"/><path d="M7 21v-4M12 21v-4M17 21v-4"/>'),
 "drop": _svg('<path d="M12 3c3 4 6 7 6 11a6 6 0 0 1-12 0c0-4 3-7 6-11z"/>'),
 "gear": _svg('<circle cx="12" cy="12" r="3.2"/><path d="M12 2v3M12 19v3M4.2 4.2l2.1 2.1M17.7 17.7l2.1 2.1M2 12h3M19 12h3M4.2 19.8l2.1-2.1M17.7 6.3l2.1-2.1"/>'),
 "cube": _svg('<path d="m12 3 8 4.5v9L12 21l-8-4.5v-9L12 3zM4 7.5 12 12l8-4.5M12 12v9"/>'),
 "bolt": _svg('<path d="M13 2 4 14h7l-1 8 9-12h-7l1-8z"/>'),
 "building": _svg('<rect x="4" y="3" width="16" height="18" rx="1"/><path d="M9 7h.01M15 7h.01M9 11h.01M15 11h.01M9 15h.01M15 15h.01"/>'),
 "anchor": _svg('<circle cx="12" cy="5" r="2"/><path d="M12 7v13M5 13a7 7 0 0 0 14 0M3 13h4M17 13h4"/>'),
 "quote": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M7 7H4a2 2 0 0 0-2 2v3a2 2 0 0 0 2 2h2v2a2 2 0 0 1-2 2H4v2h1a4 4 0 0 0 4-4V9a2 2 0 0 0-2-2zm11 0h-3a2 2 0 0 0-2 2v3a2 2 0 0 0 2 2h2v2a2 2 0 0 1-2 2h0v2h1a4 4 0 0 0 4-4V9a2 2 0 0 0-2-2z"/></svg>',
 "linkedin": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M4.98 3.5A2.5 2.5 0 1 1 0 3.5a2.5 2.5 0 0 1 4.98 0zM0 8h5v16H0zM8 8h4.8v2.2h.07c.67-1.2 2.3-2.5 4.73-2.5 5.06 0 6 3.3 6 7.6V24h-5v-7.2c0-1.7 0-3.9-2.4-3.9s-2.7 1.9-2.7 3.8V24H8z"/></svg>',
}

# ---------- Quote form (shared by the home CTA and /contact/) ----------
def contact_form(pad=""):
    """Markup for the "Request a quote" form.

    Delivery is client-side: assets/js/main.js posts it through EmailJS when the three
    EMAILJS_* IDs are set, and otherwise falls back to composing a mailto:. The `website`
    field is a honeypot -- hidden from people, read by that handler to drop bot submissions.
    `pad` is the indent of the surrounding markup (cosmetic only)."""
    prod_opts = "".join(f'<option value="{c[1]}">{c[1]}</option>' for c in PRODUCT_CATEGORIES)
    ejs = ""
    if EMAILJS_PUBLIC_KEY and EMAILJS_SERVICE_ID and EMAILJS_TEMPLATE_ID:
        ejs = (f' data-ejs-key="{esc(EMAILJS_PUBLIC_KEY)}"'
               f' data-ejs-service="{esc(EMAILJS_SERVICE_ID)}"'
               f' data-ejs-template="{esc(EMAILJS_TEMPLATE_ID)}"')
    form = f'''<form class="contact-form reveal" data-delay="1" id="contactForm" novalidate{ejs}>
  <h2>Request a quote</h2>
  <p class="form-note">Fields marked <span style="color:var(--green-strong)">*</span> are required.</p>
  <div class="form-row">
    <div class="field"><label for="cf-name">Name <span class="req">*</span></label><input id="cf-name" name="name" type="text" autocomplete="name" required></div>
    <div class="field"><label for="cf-company">Company</label><input id="cf-company" name="company" type="text" autocomplete="organization"></div>
  </div>
  <div class="form-row">
    <div class="field"><label for="cf-email">Email <span class="req">*</span></label><input id="cf-email" name="email" type="email" autocomplete="email" required></div>
    <div class="field"><label for="cf-phone">Phone</label><input id="cf-phone" name="phone" type="tel" autocomplete="tel"></div>
  </div>
  <div class="field"><label for="cf-interest">Area of interest</label>
    <select id="cf-interest" name="interest"><option value="">Select…</option>{prod_opts}<option>Services / Installation</option><option>Maintenance &amp; support</option></select>
  </div>
  <div class="field"><label for="cf-msg">Message <span class="req">*</span></label><textarea id="cf-msg" name="message" required placeholder="Tell us about your requirement…"></textarea></div>
  <div class="hp" aria-hidden="true"><label for="cf-website">Leave this field empty</label><input id="cf-website" name="website" type="text" tabindex="-1" autocomplete="off"></div>
  <button class="btn btn--solid btn--lg" type="submit" style="width:100%">Send enquiry {IC['arrow']}</button>
  <p class="form-status" id="formStatus" role="status" aria-live="polite"></p>
</form>'''
    return textwrap.indent(form, pad)[len(pad):]

# =====================================================================
#  DATA
# =====================================================================
PRODUCT_CATEGORIES = [
 ("water","Water & Wastewater","drop","Treatment, screening, clarification and reuse systems."),
 ("filtration","Filtration & Screening","layers","Filters, screens, strainers and separation."),
 ("valves","Valves & Flow","gear","Valves, actuators, pumps, couplings and hydraulics."),
 ("lifting","Lifting & Cranes","cube","Hoists, davits, gantry and workshop cranes."),
 ("fabrication","Fabrication & Skids","factory","Custom fabrication, spools and process skids."),
 ("electrical","Instrumentation & Control","bolt","Control panels, drives and measurement."),
]
CAT_LABEL = {c[0]: c[1] for c in PRODUCT_CATEGORIES}

# Category-level content templates (accurate at the equipment-class level)
CAT_APPLICATIONS = {
 "water": ["Municipal sewage treatment plants","Industrial effluent treatment","Water reuse & recycling","Desalination & potable water"],
 "filtration": ["Wastewater inlet works","Process & cooling water","Solids & debris separation","Industrial pre-treatment"],
 "valves": ["Water & wastewater networks","Oil & gas facilities","Process & utility piping","Building & HVAC services"],
 "lifting": ["Treatment plants & pump stations","Workshops & maintenance","Fabrication yards","Industrial facilities"],
 "fabrication": ["Oil, gas & petrochemical","Water & wastewater plants","Process industries","EPC & contractor packages"],
 "electrical": ["Treatment-plant automation","Pumping stations","Process plants","Utility & building systems"],
}
CAT_FEATURES = {
 "water": ["Robust construction for continuous duty","Energy-efficient operation","Modular, skid-mounted options","Instrumentation & control ready","Designed for reliable effluent quality","Low operator intervention"],
 "filtration": ["Corrosion-resistant stainless construction","Configurable aperture / filtration rating","Manual or automatic cleaning","Low pressure drop, high capture","Compact footprint","Engineered to site flow & load"],
 "valves": ["Materials selected for the process media","Reliable, tight shut-off","Manual, pneumatic or electric operation","Full testing & traceability","Wide size & pressure-class range","Spares & after-sales support"],
 "lifting": ["Certified, load-tested design","Portable or fixed configurations","Corrosion-protected finish","Safe working load to requirement","Smooth, controlled operation","Compliant with lifting standards"],
 "fabrication": ["Built to drawing & specification","In-house welding & NDT testing","Material certification & traceability","Coating & finishing to spec","Modular, transport-ready assemblies","Fast, reliable delivery"],
 "electrical": ["Built to IEC standards","Quality components from leading brands","Factory tested & documented","Custom I/O and control logic","Clear labelling & as-built drawings","Commissioning & support"],
}
CAT_SPECS = {
 "water": [("Construction","Carbon / stainless steel to duty"),("Configuration","Packaged or skid-mounted"),("Capacity","Engineered to flow & load"),("Controls","PLC / manual, as required"),("Finish","Coated / galvanised to spec"),("Standards","On request")],
 "filtration": [("Construction","Stainless steel (SS304 / SS316)"),("Cleaning","Manual / automatic"),("Aperture / rating","Application-specific"),("Capacity","Engineered to flow rate"),("Drive","As required"),("Standards","On request")],
 "valves": [("Body material","CS / SS / suit media"),("Size range","To requirement"),("Pressure class","Project-specific"),("Operation","Manual / pneumatic / electric"),("Connections","Flanged / threaded / welded"),("Testing","As per applicable code")],
 "lifting": [("Construction","Steel / aluminium"),("Safe working load","To requirement"),("Configuration","Portable / fixed"),("Finish","Painted / galvanised"),("Certification","Load-tested"),("Standards","On request")],
 "fabrication": [("Materials","CS / SS / alloy to spec"),("Fabrication","Welded & tested in-house"),("Testing","NDT / hydro as specified"),("Finish","Coating to spec"),("Documentation","Full traceability"),("Standards","ASME / client code")],
 "electrical": [("Enclosure","IP-rated to environment"),("Components","Leading OEM brands"),("Control","PLC / relay logic"),("Certification","Tested & documented"),("Ratings","Project-specific"),("Standards","IEC compliant")],
}
def cat_faqs(name, cat):
    common = [
     (f"Can the {name} be customised to our requirements?",
      "Yes — every unit is engineered to your process duty, materials and installation constraints. Share your parameters and our team will propose the right configuration."),
     ("Do you provide installation and after-sales support?",
      "Yes. Trivex offers supply, installation, commissioning, spares and ongoing maintenance from our SAIF Zone facility in Sharjah."),
     ("What is the typical lead time?",
      "Lead time depends on configuration and materials. Contact us with your specification for a project-specific schedule and quotation."),
    ]
    mat = {
     "filtration": ("What materials are available?","Typically SS304 or SS316; alternative materials are available on request to suit the media."),
     "water": ("Can it be delivered as a packaged plant?","Yes — many solutions are supplied skid-mounted or packaged for fast, low-risk installation."),
     "valves": ("Can valves be supplied automated?","Yes — valves can be supplied with pneumatic or electric actuation and position feedback."),
     "lifting": ("Is the equipment certified?","Yes — lifting equipment is load-tested and supplied with the appropriate certification."),
     "fabrication": ("Do you fabricate to our drawings and codes?","Yes — we fabricate to your drawings and applicable codes with full material traceability and testing."),
     "electrical": ("Can you integrate with our control system?","Yes — panels and instruments are designed to integrate with your control philosophy and SCADA."),
    }.get(cat)
    return ([mat] if mat else []) + common

# Products: slug, name, cat, short, long, benefits, [featured]
# Optional per-product overrides (else the category templates are used):
#   brand    – key into BRANDS for partner-manufactured lines
#   specs    – [(label, value)] spec table;  features / apps – lists
def P(slug, name, cat, short, long, benefits, featured=False, brand=None, specs=None, features=None, apps=None):
    return dict(slug=slug, name=name, cat=cat, short=short, long=long, benefits=benefits, featured=featured,
                brand=brand, specs=specs, features=features, apps=apps)

# Channel-partner brands whose product lines Trivex supplies
BRANDS = {
 "unicorn": dict(name="Unicorn Valves", url="https://www.unicorn-valves.com/",
                 logo="/assets/img/clients/unicorn-valves.png",
                 brochure="/assets/docs/unicorn-valves-brochure.pdf",
                 about="Unicorn Valves (Coimbatore, India) is an ISO 9001:2015 certified manufacturer of control valves and actuators."),
}

# Unicorn Valves control valves & actuators (data from the Unicorn product brochure)
_UV_PRESSURE = "ASME 150 – ASME 2500 / DIN PN 6 – PN 250"
_UV_BONNET   = "Standard, extended, bellows-sealed or cryogenic"
_UV_BODY     = "Carbon, alloy, stainless, duplex & super duplex steel; exotic materials"
_UV_ACT      = "Pneumatic spring-diaphragm (single acting), pneumatic piston (single / double acting) or electric"
_UV_ENDS_NPT = 'Flanged; butt-weld (BW) & socket-weld (SW); threaded NPT 0.5" – 2"'
_UV_ENDS_W   = "Flanged; butt-weld (BW) & socket-weld (SW)"
def _uv_specs(sizes, ends, chars, leak):
    return [("Sizes",sizes),("Pressure rating",_UV_PRESSURE),("End connections",ends),("Bonnet options",_UV_BONNET),
            ("Characteristics",chars),("Leakage class",leak),("Body material",_UV_BODY),("Actuation",_UV_ACT)]
_UV_TOP_FEATURES = ["Contoured unbalanced plug","Deci-Nill® noise and Cav-Kill® cavitation-control trims","Single- or double-stage trim",
                    "Steam-jacket and vacuum-service options","Soft seat and low-emission packing","Expander with cartridge for very high noise reduction"]
_UV_CAGE_FEATURES = ["Pressure-energised seal ring","Auxiliary pilot plug design","Deci-Nill® and Cav-Kill® severe-service trims",
                     "Diffuser seat-ring design","Single-, double- or three-stage design","Steam-jacket and vacuum-service options",
                     "Expander with cartridge for very high noise reduction","Low-emission packing"]
_UV_APPS = ["Oil, gas & petrochemical plants","Power generation & steam systems","Chemical & process industries","Water & utility networks"]
_UV_SEVERE_APPS = ["High pressure-drop letdown","Cavitating liquid service","Noise-critical gas & steam service","Oil, gas & power plants"]

PRODUCTS = [
 P("rotary-drum-screens","Rotary Drum Screens","filtration","Fine solids separation for inlet works",
   "Rotary drum screens separate suspended solids from wastewater using a continuously rotating, perforated or wedge-wire drum. Captured screenings are lifted clear and discharged while screened liquid passes through — ideal for high-throughput inlet works.",
   ["High-capacity screening in a compact footprint","Continuous self-cleaning operation","Reliable solids capture and dewatering"], True),
 P("basket-strainers","Basket Strainers","filtration","In-line protection for pumps & lines",
   "Basket strainers protect pumps, valves and instruments by capturing debris from process lines in a removable perforated basket that is quickly cleaned or replaced.",
   ["Protects downstream equipment","Quick basket removal for cleaning","Low pressure drop across the element"]),
 P("automatic-self-cleaning-filters","Automatic Self-Cleaning Filters","filtration","Continuous back-flush filtration",
   "Automatic self-cleaning filters remove solids continuously and back-flush the element on a timer or differential-pressure trigger, so filtration continues without interrupting the process.",
   ["Uninterrupted, automated filtration","Minimal operator intervention","Consistent filtrate quality"]),
 P("automatic-basket-screens","Automatic Basket Screens","filtration","Mechanised screening for channels",
   "Mechanised basket screens rake and lift screenings from open channels automatically, keeping flow clear at pumping stations and treatment inlets.",
   ["Automated channel screening","Reliable solids removal","Reduced manual cleaning"]),
 P("odor-control-systems","Odour Control Systems","water","Scrubbing & dosing for foul air",
   "Odour control systems capture and treat foul air from wastewater and process facilities, using scrubbing and chemical dosing to neutralise odorous compounds before discharge.",
   ["Effective H₂S and odour removal","Protects staff and neighbours","Packaged, easy-to-integrate skids"], True),
 P("daf-systems","DAF Systems","water","Dissolved-air flotation clarifiers",
   "Dissolved air flotation (DAF) systems clarify water by attaching fine air bubbles to suspended solids, fats and oils, floating them to the surface for skimming.",
   ["Efficient removal of solids, fats & oils","Compact, high-rate clarification","Stable, reliable performance"], True),
 P("air-diffusers","Air Diffusers","water","Fine-bubble aeration for basins",
   "Fine-bubble air diffusers deliver oxygen efficiently to aeration basins, supporting biological treatment while minimising energy use.",
   ["High oxygen-transfer efficiency","Lower aeration energy cost","Even, fine-bubble distribution"]),
 P("filter-press","Filter Press","filtration","Sludge dewatering & cake recovery",
   "Filter presses dewater sludge into stackable, transportable cake by pressing slurry between filter plates — reducing volume and disposal cost.",
   ["High dry-solids cake","Reduced sludge volume & disposal cost","Batch operation to suit load"], True),
 P("pipe-spools","Pipe Spools","fabrication","Prefabricated flanged pipework",
   "Prefabricated pipe spools are cut, welded and tested off-site to your isometrics, then delivered ready for rapid on-site installation.",
   ["Faster site installation","Shop-controlled weld quality","Full material traceability"]),
 P("reverse-osmosis-plants","Reverse Osmosis Plants","water","Membrane desalination & polishing",
   "Reverse osmosis plants produce high-purity water by forcing feed water through semi-permeable membranes, removing dissolved salts and contaminants for process or potable use.",
   ["High-purity permeate","Skid-mounted, factory-tested packages","Low-fouling, efficient design"], True),
 P("control-panels","Control Panels","electrical","PLC & motor-control assemblies",
   "Control panels house the switchgear, PLC and motor-control equipment that run your process — designed, built and tested to your control philosophy.",
   ["Built and tested to specification","Standards-compliant, reliable build","Clear documentation & support"], True),
 P("ss-manifolds","SS Manifolds","fabrication","Stainless distribution manifolds",
   "Stainless steel manifolds distribute and collect fluids across multiple lines from a single, hygienic, corrosion-resistant assembly.",
   ["Hygienic stainless construction","Custom port configuration","Leak-tested assemblies"]),
 P("pump-hoists","Pump Hoists","lifting","Davit cranes for pump retrieval",
   "Pump hoists (davit cranes) allow safe retrieval and installation of submersible pumps and equipment from wet wells and tanks.",
   ["Safe pump retrieval","Portable, single-operator use","Corrosion-protected build"]),
 P("grit-classifier","Grit Classifier","water","Grit washing & dewatering",
   "Grit classifiers separate and wash grit from wastewater, dewatering it for easy disposal and protecting downstream pumps and digesters from abrasion.",
   ["Protects pumps from abrasion","Clean, dewatered grit","Reliable continuous operation"]),
 P("gantry-cranes","Gantry Cranes","lifting","Portable & fixed lifting frames",
   "Gantry cranes provide flexible overhead lifting for workshops, treatment plants and yards — available in portable and fixed configurations.",
   ["Flexible overhead lifting","Portable or fixed options","Certified, load-tested"], True),
 P("workshop-cranes","Workshop Cranes","lifting","Mobile folding engine cranes",
   "Mobile workshop (engine) cranes provide compact, folding lifting for maintenance and assembly tasks.",
   ["Compact, folding design","Easy manoeuvring","Load-rated for workshop use"]),
 P("combination-screens","Combination Screens","filtration","Screening & grit removal in one",
   "Combination screens integrate screening and grit removal into a single unit, saving space and civil works at inlet works.",
   ["Screening + grit in one unit","Space-saving inlet works","Reduced civil works"]),
 P("screw-compactors","Screw Compactors","filtration","Wash-press screenings compaction",
   "Screw compactors wash, convey and compact screenings, reducing volume and organic content for lower disposal cost.",
   ["Compacts and dewaters screenings","Reduces disposal volume","Hygienic, enclosed transport"]),
 P("micro-grit-classifiers","Micro Grit Classifiers","water","Fine-grit recovery units",
   "Micro grit classifiers recover fine grit that conventional systems miss, protecting downstream processes from wear.",
   ["Captures fine grit","Protects downstream assets","Compact, efficient design"]),
 P("screw-screens","Screw Screens","filtration","Inclined screw screening & transport",
   "Screw screens combine screening, conveying and compaction on an inclined shaftless screw — ideal for compact pumping stations.",
   ["3-in-1 screen, convey & compact","Compact inclined design","Low maintenance"]),
 P("sludge-decanters","Sludge Decanters","water","Centrifugal sludge thickening",
   "Decanter centrifuges thicken and dewater sludge continuously using high centrifugal force, producing consistent, transportable cake.",
   ["Continuous dewatering","Consistent cake dryness","High throughput"]),
 P("vertical-self-cleaning-filters","Vertical Self-Cleaning Filters","filtration","Automatic vertical strainers",
   "Vertical self-cleaning filters provide automatic, in-line filtration with a minimal footprint and low maintenance.",
   ["Automatic in-line filtration","Small footprint","Low maintenance"]),
 P("dust-hoppers","Dust Hoppers","filtration","Collection hoppers for dry solids",
   "Dust hoppers collect and channel dry solids from dust-extraction and process systems for controlled discharge.",
   ["Reliable dry-solids collection","Custom capacity & geometry","Durable construction"]),
 P("bag-filters","Bag Filters","filtration","Liquid & dust bag filtration",
   "Bag filters remove particulates from liquids or gases using replaceable filter bags in a robust housing.",
   ["Simple, low-cost filtration","Quick bag change-out","Wide micron range"]),
 P("fabricated-filtration-units","Fabricated Filtration Units","fabrication","Custom pressure filtration vessels",
   "Custom-fabricated pressure filtration vessels are engineered and built to your process duty and code requirements.",
   ["Engineered to your duty","Code-compliant fabrication","Full testing & documentation"]),
 P("valves","Valves","valves","Gate, globe, ball & butterfly valves",
   "Trivex supplies gate, globe, ball and butterfly valves in materials and pressure classes to suit your process, with installation and maintenance support.",
   ["Wide range & material options","Reliable shut-off","Supply, install & maintain"], True),
 P("actuators","Actuators","valves","Pneumatic & electric actuation",
   "Pneumatic and electric actuators automate valve operation for safe, remote and repeatable process control.",
   ["Reliable valve automation","Pneumatic or electric","Position-feedback options"]),
 P("top-guided-globe-control-valves","Top Guided Globe Control Valves — 91000 Series","valves","Unicorn 91000 series, 0.5\" – 8\"",
   "The Unicorn Valves 91000 series is a top-guided globe control valve for precise throttling of liquids, gases and steam, available from 0.5\" to 8\" in ASME 150 – 2500 and DIN PN 6 – PN 250 ratings with a wide choice of trims, bonnets and body materials.",
   ["Linear, equal-percentage or quick-opening characteristics","Class IV / V shut-off as standard, Class VI optional","Noise and cavitation-control trims available"],
   brand="unicorn", specs=_uv_specs('0.5" – 8"', _UV_ENDS_NPT, "Linear, equal percentage, quick opening",
                                    "ANSI/FCI 70-2 Class IV / V (standard); Class VI (option)"),
   features=_UV_TOP_FEATURES, apps=_UV_APPS),
 P("top-guided-angle-control-valves","Top Guided Angle Control Valves — 92000 Series","valves","Unicorn 92000 series, 0.5\" – 8\"",
   "The Unicorn Valves 92000 series is a top-guided angle-body control valve, suited to erosive, flashing and high pressure-drop duties and to piping layouts that need a 90° turn. Sizes 0.5\" – 8\", ASME 150 – 2500 and DIN PN 6 – PN 250.",
   ["Angle body for erosive and flashing service","Class IV / V shut-off as standard, Class VI optional","Noise and cavitation-control trims available"],
   brand="unicorn", specs=_uv_specs('0.5" – 8"', _UV_ENDS_NPT, "Linear, equal percentage, quick opening",
                                    "ANSI/FCI 70-2 Class IV / V (standard); Class VI (option)"),
   features=_UV_TOP_FEATURES, apps=_UV_APPS),
 P("micro-flow-globe-control-valves","Micro Flow Globe Control Valves — 93000 Series","valves","Unicorn 93000 series, 0.5\" – 1\"",
   "The Unicorn Valves 93000 series is a micro-flow globe control valve for accurate control of very low flow rates, with a contoured micro-flow plug and a solid Stellite single-piece plug and stem. Sizes 0.5\", 0.75\" and 1\".",
   ["Precise control of very low flows","Solid Stellite single-piece plug & stem","Class V shut-off as standard, Class VI optional"],
   brand="unicorn", specs=_uv_specs('0.5", 0.75" – 1"', 'Flanged; butt-weld (BW) & socket-weld (SW); threaded NPT 0.5" – 1"',
                                    "Linear, equal percentage", "ANSI/FCI 70-2 Class V (standard); Class VI (option)"),
   features=["Contoured micro-flow control","Solid Stellite single-piece plug & stem","Deci-Nill® noise and Cav-Kill® cavitation-control trims",
             "Single- or double-stage trim","Steam-jacket and vacuum-service options","Soft seat and low-emission packing",
             "Expander with cartridge for very high noise reduction"], apps=_UV_APPS),
 P("cage-guided-globe-control-valves","Cage Guided Globe Control Valves — 94000 Series","valves","Unicorn 94000 series, 2\" – 36\"",
   "The Unicorn Valves 94000 series is a cage-guided globe control valve for large-bore, high-capacity and severe-service duties, from 2\" to 36\". Cage guiding gives stable plug guidance, and the pressure-energised seal ring and pilot-plug design keep actuator forces low.",
   ["Large sizes up to 36\"","Stable cage-guided trim for severe service","Single-, double- or three-stage designs"],
   brand="unicorn", specs=_uv_specs('2" – 36"', _UV_ENDS_NPT, "Linear, equal percentage, quick opening, modified equal percentage",
                                    "ANSI/FCI 70-2 Class IV (standard); Class V (option)"),
   features=_UV_CAGE_FEATURES, apps=_UV_APPS),
 P("cage-guided-angle-control-valves","Cage Guided Angle Control Valves — 95000 Series","valves","Unicorn 95000 series, 2\" – 24\"",
   "The Unicorn Valves 95000 series is a cage-guided angle control valve for high pressure-drop, flashing and erosive service, from 2\" to 24\", with severe-service trims and multi-stage designs.",
   ["Angle body for flashing and erosive service","Stable cage-guided trim","Single-, double- or three-stage designs"],
   brand="unicorn", specs=_uv_specs('2" – 24"', _UV_ENDS_NPT, "Linear, equal percentage, quick opening, modified equal percentage",
                                    "ANSI/FCI 70-2 Class IV (standard); Class V (option)"),
   features=_UV_CAGE_FEATURES, apps=_UV_APPS),
 P("three-way-mixing-diverting-control-valves","3-Way Mixing / Diverting Control Valves — 96000 Series","valves","Unicorn 96000 series, 0.75\" – 24\"",
   "The Unicorn Valves 96000 series is a three-way control valve that mixes two streams into one or diverts one stream into two — ideal for temperature control, HVAC and flow-diverting applications. Sizes 0.75\" – 24\".",
   ["Mixing or diverting in a single valve","Ideal for temperature control loops","Class IV shut-off as standard, Class VI optional"],
   brand="unicorn", specs=_uv_specs('0.75" – 24"', _UV_ENDS_NPT, "Linear, equal percentage, quick opening, modified equal percentage",
                                    "ANSI/FCI 70-2 Class IV (standard); Class VI (option)"),
   features=["HVAC applications","Temperature-control services","Flow-diverting applications","Steam-jacket option","Low-emission packing"],
   apps=["Temperature-control loops","HVAC & district cooling","Heat-exchanger bypass","Process & utility systems"]),
 P("multi-step-multi-stage-axial-flow-control-valves","Multi-Step Multi-Stage Axial Flow Control Valves — 97000 Series","valves","Unicorn 97000 series critical-service valve",
   "The Unicorn Valves 97000 series is a critical-service control valve with a multi-step, multi-stage axial-flow trim that breaks a high pressure drop into controlled steps, limiting velocity to prevent cavitation, erosion and noise. Sizes 1\" – 8\".",
   ["Built for high pressure-drop applications","Velocity-control trim prevents cavitation & erosion","Class IV / V shut-off as standard, Class VI optional"],
   brand="unicorn", specs=_uv_specs('1" – 8"', _UV_ENDS_W, "Modified equal percentage",
                                    "Class IV / V (standard); ANSI/FCI 70-2 Class VI (option)"),
   features=["High pressure-drop applications","Velocity-control trim","Low-emission packing","Cav-Kill® cavitation-control trim",
             "Deci-Nill® noise-reduction trim","Multi-step (axial) flow trim"], apps=_UV_SEVERE_APPS),
 P("multi-stage-radial-flow-control-valves","Multi-Stage Radial Flow Control Valves — 98000 Series","valves","Unicorn 98000 series critical-service valve",
   "The Unicorn Valves 98000 series is a critical-service control valve with a multi-stage, multi-cage radial-flow trim that stages the pressure drop across concentric cages to control velocity and cavitation. Sizes 2\" – 24\".",
   ["Multi-stage, multi-cage radial-flow trim","Velocity and cavitation control","Sizes 2\" – 24\" up to ASME 2500"],
   brand="unicorn", specs=_uv_specs('2" – 24"', _UV_ENDS_W, "Linear, equal percentage, modified linear & equal percentage",
                                    "Class IV (standard); ANSI/FCI 70-2 Class V (option)"),
   features=["Low-emission packing","Cav-Kill® cavitation-control trim","Multi-stage multi-cage (radial) flow trim","Velocity-control trim"],
   apps=_UV_SEVERE_APPS),
 P("multi-stage-axial-flow-control-valves","Multi-Stage Axial Flow Control Valves — 99000 Series","valves","Unicorn 99000 series critical-service valve",
   "The Unicorn Valves 99000 series is a critical-service control valve with a multi-stage, multi-cage axial-flow trim that drops pressure progressively along the flow path to control velocity and cavitation. Sizes 2\" – 24\".",
   ["Multi-stage, multi-cage axial-flow trim","Velocity and cavitation control","Sizes 2\" – 24\" up to ASME 2500"],
   brand="unicorn", specs=_uv_specs('2" – 24"', _UV_ENDS_W, "Linear, equal percentage, modified linear & equal percentage",
                                    "Class IV (standard); ANSI/FCI 70-2 Class V (option)"),
   features=["Low-emission packing","Cav-Kill® cavitation-control trim","Multi-stage multi-cage (axial) flow trim","Velocity-control trim"],
   apps=_UV_SEVERE_APPS),
 P("pneumatic-spring-diaphragm-actuators","Pneumatic Spring Diaphragm Actuators — UA-11/12 Series","valves","Unicorn single-acting diaphragm actuators",
   "Unicorn Valves UA-11 (direct acting) and UA-12 (reverse acting) pneumatic spring-diaphragm actuators provide reliable, fail-safe single-acting operation of linear control valves, with or without a handwheel.",
   ["Direct- or reverse-acting fail-safe action","Available with or without handwheel","Manual override and position indicator"],
   brand="unicorn",
   specs=[("Type","Pneumatic spring diaphragm, single acting"),("Models","UA-11 (direct acting), UA-12 (reverse acting)"),
          ("Sizes","30, 35, 40, 45, 50"),("Spring range","3–15 psi, 6–30 psi, 12–30 psi"),
          ("Design pressure","Up to 5 bar g"),("Travel","19.05 mm – 101.6 mm")],
   features=["With or without handwheel","Manual override","Position indicator","Adjustable mechanical stopper"], apps=_UV_APPS),
 P("pneumatic-piston-cylinder-actuators","Pneumatic Piston Cylinder Actuators — UA-30/31/32 Series","valves","Unicorn single- & double-acting piston actuators",
   "Unicorn Valves UA-30/31/32 pneumatic piston-cylinder actuators deliver high thrust and long strokes for large and high-pressure control valves, in double-acting and single-acting (direct or reverse) versions.",
   ["Thrust up to 100,000 N","Strokes from 15 mm to 250 mm","Backup system for guaranteed fail action"],
   brand="unicorn",
   specs=[("Type","Pneumatic piston cylinder, single or double acting"),
          ("Models","UA-30 (double acting), UA-31 (single acting direct), UA-32 (single acting reverse)"),
          ("Sizes","7.5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60"),("Stroke","15 mm – 250 mm"),
          ("Thrust","Up to 100,000 N"),("Design pressure","Up to 10 bar g")],
   features=["Side-mounted handwheel","Manual override","Position indicator","Backup system for achieving fail action"], apps=_UV_APPS),
 P("pumps","Pumps","valves","Process, submersible & dosing pumps",
   "Process, submersible and dosing pumps for water, wastewater and industrial duties — selected and supported for your application.",
   ["Right pump for the duty","Efficient, reliable operation","Spares & service support"]),
 P("process-skids-oil-gas","Process Skids for Oil & Gas","fabrication","Modular, tested process packages",
   "Modular process skids are engineered, fabricated and factory-tested as complete packages for fast, low-risk deployment in oil & gas and process plants.",
   ["Factory-tested packages","Fast site deployment","Full documentation & traceability"], True),
 P("sewage-treatment-solutions","Sewage Treatment Solutions","water","Packaged STP & wastewater plants",
   "Packaged sewage treatment plants (STP) and wastewater solutions treat effluent to reuse or discharge standards in a compact, reliable package.",
   ["Compliant effluent quality","Compact packaged plant","Low operator intervention"], True),
 P("flow-measurement-instruments","Flow Measurement Instruments","electrical","Meters for liquid & gas flow",
   "Flow meters and measurement instruments provide accurate monitoring of liquid and gas flow for process control and reporting.",
   ["Accurate flow measurement","Wide range of technologies","Control-system ready"]),
 P("hoists-lifting-accessories","Hoists & Lifting Accessories","lifting","Chain & electric hoists, rigging",
   "Chain and electric hoists plus rigging accessories for safe, certified lifting across maintenance and installation tasks.",
   ["Certified lifting equipment","Manual & electric options","Full range of accessories"]),
 P("couplings","Couplings","valves","Pipe couplings, clamps & fittings",
   "Pipe couplings, clamps and fittings provide fast, reliable, leak-tight pipe connections and repairs.",
   ["Fast, secure connections","Wide size range","Reliable sealing"]),
 P("hydraulics","Hydraulics","valves","Cylinders, power packs & hardware",
   "Hydraulic cylinders, power packs and components deliver controlled force for industrial lifting, actuation and process equipment.",
   ["Controlled high-force output","Custom power packs","Reliable components"]),
 P("vfd-electrical-components","VFD & Electrical Components","electrical","Drives, PLCs & switchgear",
   "Variable frequency drives, PLCs and switchgear from leading brands, supplied and integrated into your control systems.",
   ["Energy-saving motor control","Quality branded components","Integration & support"]),
 P("pressure-measurement-instruments","Pressure Measurement Instruments","electrical","Gauges, transmitters & switches",
   "Pressure gauges, transmitters and switches for accurate monitoring and protection of process systems.",
   ["Accurate pressure monitoring","Gauges, transmitters & switches","Process protection"]),
]
PROD = {p["slug"]: p for p in PRODUCTS}

# Services: slug, name, tagline, image, problem, overview, process[(t,d)], capabilities[], industries[], faqs[]
def S(**k): return k
SERVICES = [
 S(slug="valve-supply-maintenance", name="Valve Supply, Installation & Maintenance", short="Sealed tight. Proven to last.",
   image="solutions/valves-maintenance.jpg", icon="gear",
   problem="Leaking, seized or mismatched valves cause downtime, safety risks and lost product.",
   overview="Trivex supplies, installs, tests and maintains valves of every type — gate, globe, ball, butterfly and control — matched to your media, pressure class and duty. From single replacements to full plant packages, we keep your flow control reliable.",
   process=[("Assess","Survey the line, media and duty to select the right valve and material."),
            ("Supply","Source certified valves and actuation from trusted manufacturers."),
            ("Install","Install, actuate and pressure-test to the applicable code."),
            ("Maintain","Scheduled servicing, spares and rapid breakdown support.")],
   capabilities=["Gate, globe, ball & butterfly valves","Pneumatic & electric actuation","On-site installation & testing","Preventive maintenance contracts","Emergency valve replacement","Spares & obsolescence management"],
   industries=["water-utilities","oil-gas","manufacturing","buildings"],
   faqs=[("Do you handle emergency valve failures?","Yes — we provide rapid supply and on-site replacement to minimise downtime."),
         ("Can you service valves from any manufacturer?","Yes — our team services and refurbishes valves across major brands and types.")]),
 S(slug="industrial-installations", name="Industrial Installations", short="Precision meets flawless execution.",
   image="solutions/industrial-installations.jpg", icon="factory",
   problem="Poorly executed installations lead to rework, delays and long-term reliability problems.",
   overview="We install industrial equipment, pipework and packages on-site with disciplined planning, skilled crews and rigorous QA — commissioning systems that work first time and keep working.",
   process=[("Plan","Method statements, risk assessments and schedule."),
            ("Mobilise","Skilled crews, tools and lifting equipment on site."),
            ("Install","Mechanical installation, alignment and connection."),
            ("Commission","Testing, commissioning and handover documentation.")],
   capabilities=["Mechanical equipment installation","Pipework & spool erection","Alignment & mechanical completion","Testing & pre-commissioning","HSE-led site delivery","As-built documentation"],
   industries=["oil-gas","water-utilities","manufacturing","mining"],
   faqs=[("Do you work as a subcontractor to EPCs?","Yes — we deliver installation packages for EPC contractors and end users alike."),
         ("Is HSE integrated into your delivery?","Yes — every installation is delivered under method statements and risk assessments.")]),
 S(slug="manufacturing-assembly", name="Manufacturing & Assembly", short="Engineered, built and delivered.",
   image="solutions/manufacturing-assembly.jpg", icon="wrench",
   problem="Off-the-shelf equipment rarely fits the exact duty, footprint or code you need.",
   overview="From our SAIF Zone workshop we fabricate, weld, assemble and test custom equipment, skids and structures to your drawings — with material traceability and in-house QA at every stage.",
   process=[("Engineer","Review drawings, materials and codes."),
            ("Fabricate","Cutting, welding and machining in-house."),
            ("Assemble","Mechanical assembly and integration."),
            ("Test","NDT, hydro and functional testing before dispatch.")],
   capabilities=["Custom fabrication & welding","Skid & package assembly","NDT & hydro testing","Coating & finishing","Material traceability","Transport-ready modules"],
   industries=["oil-gas","water-utilities","manufacturing","mining"],
   faqs=[("Do you fabricate to client drawings and codes?","Yes — we build to your drawings and applicable codes with full traceability."),
         ("Can you deliver complete tested packages?","Yes — we deliver factory-tested skids and packages ready for installation.")]),
 S(slug="water-wastewater-treatment", name="Water & Wastewater Treatment", short="Strategy. Synergy. Strength.",
   image="solutions/water-treatment.jpg", icon="drop",
   problem="Meeting discharge, reuse and quality standards reliably — without excessive cost or complexity.",
   overview="We design, supply and deliver water and wastewater treatment solutions — from screening and clarification to biological treatment, RO and reuse — engineered for compliant, cost-effective operation.",
   process=[("Analyse","Characterise the flow, load and target quality."),
            ("Design","Select the right process train and equipment."),
            ("Build","Fabricate, supply and install the plant."),
            ("Operate","Commission, optimise and support operation.")],
   capabilities=["Screening & grit removal","Clarification & DAF","Biological treatment & aeration","Reverse osmosis & reuse","Sludge dewatering","Packaged STP plants"],
   industries=["water-utilities","manufacturing","buildings","marine"],
   faqs=[("Can you deliver a complete treatment plant?","Yes — from process design through fabrication, installation and commissioning."),
         ("Do you support water reuse?","Yes — our solutions are designed for recovery and reuse where feasible.")]),
 S(slug="troubleshooting-support", name="Troubleshooting & Support", short="Exact. Every time.",
   image="solutions/troubleshooting.jpg", icon="clock",
   problem="When equipment fails or underperforms, every hour of downtime costs money.",
   overview="Our engineers diagnose and resolve mechanical, process and control problems fast — restoring performance and preventing recurrence with practical, on-site support.",
   process=[("Respond","Rapid response and on-site assessment."),
            ("Diagnose","Root-cause analysis of the fault."),
            ("Fix","Repair, replace or re-engineer as needed."),
            ("Prevent","Recommendations to stop it recurring.")],
   capabilities=["Rapid on-site response","Root-cause diagnosis","Mechanical & process repair","Control & instrumentation support","Spares & replacement","Preventive recommendations"],
   industries=["water-utilities","oil-gas","manufacturing","mining"],
   faqs=[("How quickly can you respond?","We prioritise breakdowns and mobilise as fast as your situation requires."),
         ("Do you support ongoing maintenance?","Yes — we offer maintenance contracts to prevent unplanned downtime.")]),
 S(slug="mining-equipment-solutions", name="Mining Equipment Solutions", short="Precision, perfected.",
   image="solutions/mining-solutions.jpg", icon="cube",
   problem="Mining and minerals processing demand rugged, reliable equipment that survives harsh duty.",
   overview="We supply, fabricate and support equipment for mining and minerals handling — screening, classification, dewatering, pumping and structural fabrication built for abrasive, high-load service.",
   process=[("Understand","Assess the duty, materials and environment."),
            ("Specify","Select rugged equipment and materials."),
            ("Supply","Fabricate and deliver to site."),
            ("Support","Commission, service and supply spares.")],
   capabilities=["Screening & classification","Grit & solids dewatering","Heavy-duty fabrication","Slurry & process pumping","Lifting & handling equipment","On-site support"],
   industries=["mining","manufacturing","oil-gas"],
   faqs=[("Is equipment built for abrasive service?","Yes — materials and designs are selected for abrasive, high-load mining duty."),
         ("Do you support remote sites?","Yes — we plan supply, spares and support around remote operations.")]),
 S(slug="control-panel-manufacturing", name="Control Panel Manufacturing", short="Plan. Execute. Deliver.",
   image="solutions/control-panel-assembly.jpg", icon="bolt",
   problem="Control systems must be reliable, safe and exactly matched to your process and standards.",
   overview="We design, build, wire and test control panels and motor-control centres to your control philosophy — using quality components, clear documentation and rigorous factory testing.",
   process=[("Design","Schematics, GA and component selection."),
            ("Build","Panel building and wiring in-house."),
            ("Test","Factory acceptance testing (FAT)."),
            ("Commission","Site integration and support.")],
   capabilities=["PLC & motor-control panels","Switchgear assembly","VFD integration","Factory acceptance testing","As-built documentation","On-site commissioning"],
   industries=["water-utilities","manufacturing","oil-gas","buildings"],
   faqs=[("Do you test panels before delivery?","Yes — every panel undergoes factory acceptance testing and is fully documented."),
         ("Can you integrate with our SCADA?","Yes — panels are designed to integrate with your control system and SCADA.")]),
 S(slug="air-monitoring-solutions", name="Air Monitoring Solutions", short="Insight. Impact. Control.",
   image="solutions/air-monitoring.jpg", icon="shield",
   problem="Uncontrolled emissions and unsafe air put people, compliance and the environment at risk.",
   overview="We provide air monitoring and control solutions — from gas detection and instrumentation to odour control — helping you protect people, meet limits and respond with confidence.",
   process=[("Assess","Identify hazards and monitoring points."),
            ("Specify","Select detection and control equipment."),
            ("Install","Install and calibrate instrumentation."),
            ("Monitor","Ongoing calibration and support.")],
   capabilities=["Gas detection & monitoring","Odour control systems","Instrumentation & calibration","Emissions control support","Safety compliance","Ongoing service"],
   industries=["oil-gas","water-utilities","manufacturing","mining"],
   faqs=[("Do you supply odour control with monitoring?","Yes — we combine monitoring with scrubbing and dosing systems for effective control."),
         ("Do you calibrate installed instruments?","Yes — we provide installation, calibration and ongoing service.")]),
]
SERV = {s["slug"]: s for s in SERVICES}

# Industries
INDUSTRIES = [
 dict(slug="water-utilities", name="Water & Wastewater Utilities", icon="drop",
      desc="Screening, treatment, reuse and control systems that keep municipal and utility water infrastructure compliant and reliable.",
      provides=["Sewage treatment plants","Screening & grit systems","Reverse osmosis & reuse","Pumping & control panels"], img="solutions/water-treatment.jpg"),
 dict(slug="oil-gas", name="Oil & Gas", icon="bolt",
      desc="Fabrication, process skids, valves and installations engineered for the safety and reliability demands of oil, gas and petrochemical.",
      provides=["Process skids & packages","Pipe spools & fabrication","Valves & flow control","Site installation"], img="solutions/industrial-installations.jpg"),
 dict(slug="mining-minerals", name="Mining & Minerals", icon="cube",
      desc="Rugged screening, classification, dewatering and handling equipment built for abrasive, high-load minerals processing.",
      provides=["Screening & classification","Dewatering equipment","Heavy fabrication","Lifting & handling"], img="solutions/mining-solutions.jpg"),
 dict(slug="manufacturing-process", name="Manufacturing & Process", icon="factory",
      desc="Custom equipment, filtration, control panels and maintenance that keep process and manufacturing plants running efficiently.",
      provides=["Custom fabrication","Filtration & strainers","Control panels & drives","Maintenance & support"], img="solutions/manufacturing-assembly.jpg"),
 dict(slug="buildings-facilities", name="Buildings & Facilities", icon="building",
      desc="Water treatment, pumping, valves and plant-room solutions for developments, hotels and large facilities.",
      provides=["Water treatment & RO","Pumping & valves","Plant-room fabrication","Maintenance contracts"], img="bg/products-1.jpg"),
 dict(slug="marine-desalination", name="Marine & Desalination", icon="anchor",
      desc="Corrosion-resistant filtration, RO and fabrication for marine, coastal and desalination applications.",
      provides=["Reverse osmosis plants","Stainless filtration","Corrosion-resistant fabrication","Instrumentation"], img="solutions/water-treatment.jpg"),
]
IND = {i["slug"]: i for i in INDUSTRIES}

# Projects gallery (real photos; honest, non-fabricated captions)
PROJECTS = [
 ("solutions/water-treatment.jpg","Water & wastewater treatment plant","water"),
 ("products/reverse-osmosis-plants.jpg","Reverse osmosis plant","water"),
 ("solutions/manufacturing-assembly.jpg","In-house manufacturing & welding","fabrication"),
 ("products/process-skids-oil-gas.jpg","Modular process skids","fabrication"),
 ("solutions/industrial-installations.jpg","On-site industrial installation","installation"),
 ("scene/about-workers.jpg","Field service & commissioning","installation"),
 ("solutions/control-panel-assembly.jpg","Control-panel manufacturing","electrical"),
 ("products/control-panels.jpg","Motor-control panel build","electrical"),
 ("products/daf-systems.jpg","DAF clarification system","water"),
 ("solutions/mining-solutions.jpg","Mining equipment solutions","mining"),
 ("products/gantry-cranes.jpg","Gantry crane fabrication","lifting"),
 ("bg/products-2.jpg","Process conveying systems","installation"),
 ("products/filter-press.jpg","Sludge dewatering filter press","water"),
 ("solutions/air-monitoring.jpg","Air monitoring & safety","electrical"),
 ("bg/products-3.jpg","Stainless fabrication stock","fabrication"),
 ("products/sewage-treatment-solutions.jpg","Packaged sewage treatment","water"),
]
PROJECT_CATS = [("all","All"),("water","Water & Wastewater"),("fabrication","Fabrication"),
 ("installation","Installations"),("electrical","Control & Instrumentation"),("mining","Mining"),("lifting","Lifting")]

CLIENTS = [("arada","Arada"),("sewa","Sharjah Electricity, Water & Gas Authority"),
 ("etihadwe","Etihad Water & Electricity"),("farnek","Farnek"),
 ("saifzone","SAIF Zone"),("desertgroup","Desert Group"),("emrill","Emrill"),
 ("cummins","Cummins"),("atlascopco","Atlas Copco"),
 ("alhabtoor-autograph","Al Habtoor Grand, Autograph Collection"),
 ("voco","voco, an IHG Hotel"),("dewa","Dubai Electricity & Water Authority")]
CLIENT_W = {"arada":501,"sewa":309,"etihadwe":313,"farnek":618,"saifzone":469,
 "desertgroup":124,"emrill":138,"cummins":121,"atlascopco":250,
 "alhabtoor-autograph":126,"voco":272,"dewa":418,"aquax":552}

# Homepage bento tiles (PDF-faithful "explore" grid) and sustainability mosaic
BENTO = [
 ("Team &amp; Updates","/about/","feature"),
 ("Case Studies","/projects/","white"),("Project Gallery","/projects/","white"),("Hiring","/contact/","white"),
 ("Innovative Products","/products/","green"),("Sustainability Initiatives","/industries/","green"),("Collab Marketing","/contact/","green"),
]
MOSAIC = [f"mosaic/m{i:02d}.jpg" for i in range(1,17)]

WHY_US = [
 ("layers","End-to-end capability","Engineering, manufacturing, supply, installation and maintenance — one accountable partner for the whole lifecycle."),
 ("factory","Built in-house","Fabrication, assembly and testing under one roof at our SAIF Zone facility for consistent, traceable quality."),
 ("shield","Reliability first","Rugged designs, quality components and rigorous testing built for continuous industrial duty."),
 ("gear","Engineered to fit","Every product and system is engineered to your process, materials and site — not off-the-shelf compromise."),
 ("clock","Responsive support","Fast troubleshooting, spares and maintenance keep your operation running."),
 ("drop","Built responsibly","Solutions designed for water reuse, energy efficiency and safe, low-impact operation."),
]

NAV = [("Home","/","home"),("About","/about/","about"),("Products","/products/","products"),
       ("Services","/services/","services"),("Industries","/industries/","industries"),
       ("Projects","/projects/","projects"),("Contact","/contact/","contact")]

# =====================================================================
#  COMPONENTS
# =====================================================================
def head(title, desc, path, og_image="/assets/img/brand/og-cover.jpg", ld=None, preload_hero=False):
    canonical = SITE + path
    jsonlds = [{"@context":"https://schema.org","@type":"Organization","name":"Trivex Industrial Solutions FZC",
        "alternateName":"Trivex","url":SITE+"/","logo":SITE+"/assets/img/brand/favicon-512.png",
        "email":EMAIL,"telephone":PHONE_TEL,"foundingDate":"2025","slogan":"Complete Industrial Solutions",
        "address":{"@type":"PostalAddress","streetAddress":"Warehouse Q3-65, SAIF Zone","addressLocality":"Sharjah","addressCountry":"AE"},
        "areaServed":"AE"}]
    if ld: jsonlds.append(ld)
    ld_tags = "".join(f'<script type="application/ld+json">{json.dumps(l)}</script>' for l in jsonlds)
    preload = '<link rel="preload" as="image" href="/assets/img/bg/hero.jpg" fetchpriority="high">' if preload_hero else ""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<script>(function(l){{var h=l.hostname;if(h==="localhost"||h==="127.0.0.1")return;if(l.protocol==="http:"||h.slice(0,4)==="www.")l.replace("https://"+h.replace(/^www\\./,"")+l.pathname+l.search+l.hash)}})(location);</script>
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#37a109">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Trivex Industrial Solutions">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{SITE}{og_image}">
<meta property="og:url" content="{canonical}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/assets/img/brand/favicon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="/assets/img/brand/favicon-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300..700&family=Manrope:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
{preload}
<link rel="stylesheet" href="/assets/css/styles.css?v={CSS_VER}">
{ld_tags}
</head>'''

def header(active, home=False):
    def link(t,h,key):
        cur = ' aria-current="page"' if key==active else ""
        return f'<a href="{h}"{cur}>{t}</a>'
    # products mega dropdown
    prod_cols = "".join(
        f'<a class="mega__item" href="/products/#{c[0]}"><span class="mega__ico">{IC[c[2]]}</span>'
        f'<span><b>{c[1]}</b><small>{c[3]}</small></span></a>' for c in PRODUCT_CATEGORIES)
    prod_menu = f'''<div class="dropdown__panel mega" role="menu">
      <div class="mega__grid">{prod_cols}</div>
      <a class="mega__all" href="/products/">Browse all {len(PRODUCTS)} products {IC['arrow']}</a>
    </div>'''
    serv_items = "".join(
        f'<a class="dd__item" href="/services/{s["slug"]}/" role="menuitem"><span class="dd__ico">{IC[s["icon"]]}</span>{s["name"]}</a>'
        for s in SERVICES)
    serv_menu = f'<div class="dropdown__panel dd" role="menu">{serv_items}<a class="dd__all" href="/services/">All services {IC["arrow"]}</a></div>'
    return f'''<header class="site-header{' site-header--solid' if not home else ''}" id="siteHeader">
  <div class="container container--wide nav-wrap">
    <a class="brand" href="/" aria-label="Trivex Industrial Solutions — home">{logo("brand__logo")}</a>
    <nav class="mainnav" aria-label="Primary">
      {link("Home","/","home")}
      {link("About","/about/","about")}
      <div class="dropdown" data-dropdown>
        <a href="/products/" class="dropdown__toggle{' is-current' if active=='products' else ''}" aria-haspopup="true" aria-expanded="false">Products {IC['chevron']}</a>
        {prod_menu}
      </div>
      <div class="dropdown" data-dropdown>
        <a href="/services/" class="dropdown__toggle{' is-current' if active=='services' else ''}" aria-haspopup="true" aria-expanded="false">Services {IC['chevron']}</a>
        {serv_menu}
      </div>
      {link("Industries","/industries/","industries")}
      {link("Projects","/projects/","projects")}
      {link("Contact","/contact/","contact")}
    </nav>
    <a class="btn btn--solid header-cta" href="/contact/">Get a quote {IC['arrow']}</a>
    <button class="nav-toggle" id="navToggle" aria-label="Open menu" aria-expanded="false" aria-controls="mobileMenu"><span></span></button>
  </div>
</header>
{mobile_menu(active)}'''

def mobile_menu(active):
    prod_sub = "".join(f'<a href="/products/#{c[0]}">{c[1]}</a>' for c in PRODUCT_CATEGORIES) + '<a href="/products/">All products →</a>'
    serv_sub = "".join(f'<a href="/services/{s["slug"]}/">{s["name"]}</a>' for s in SERVICES)
    return f'''<nav class="mobile-menu" id="mobileMenu" aria-label="Mobile">
  <button class="mobile-menu__close" id="menuClose" aria-label="Close menu">&times;</button>
  <div class="mobile-menu__scroll">
    <a href="/" class="mm-link">Home</a>
    <a href="/about/" class="mm-link">About</a>
    <div class="mm-group" data-mm-group>
      <button class="mm-link mm-toggle" aria-expanded="false">Products {IC['chevron']}</button>
      <div class="mm-sub">{prod_sub}</div>
    </div>
    <div class="mm-group" data-mm-group>
      <button class="mm-link mm-toggle" aria-expanded="false">Services {IC['chevron']}</button>
      <div class="mm-sub">{serv_sub}</div>
    </div>
    <a href="/industries/" class="mm-link">Industries</a>
    <a href="/projects/" class="mm-link">Projects</a>
    <a href="/contact/" class="mm-link">Contact</a>
    <a href="/contact/" class="btn btn--solid" style="margin-top:1.5rem">Get a quote {IC['arrow']}</a>
  </div>
  <div class="mobile-menu__foot">TRIVEX Industrial Solutions FZC · SAIF Zone, Sharjah, UAE<br><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a> · <a href="tel:{PHONE2_TEL}">{PHONE2_DISPLAY}</a></div>
</nav>'''

def whatsapp(msg):
    return (f'<a class="wa-float" href="{wa_link(msg)}" target="_blank" rel="noopener" '
            f'aria-label="Chat with Trivex on WhatsApp">{IC["whatsapp"]}<span class="wa-float__tip">Chat with us</span></a>')

def breadcrumbs(items):
    # items: list of (label, href|None)
    li = []
    for i,(label,href) in enumerate(items):
        if href and i < len(items)-1:
            li.append(f'<li><a href="{href}">{label}</a>{IC["chevron-r"]}</li>')
        else:
            li.append(f'<li aria-current="page">{label}</li>')
    ld = {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":i+1,"name":lbl,**({"item":SITE+href} if href else {})} for i,(lbl,href) in enumerate(items)]}
    return f'<nav class="breadcrumbs" aria-label="Breadcrumb"><div class="container container--wide"><ol>{"".join(li)}</ol></div></nav>', ld

def page_hero(eyebrow, title, sub, img=None, cls=""):
    media = f'<div class="phero__media"><img src="/assets/img/{img}" alt="" loading="eager"></div>' if img else ""
    return f'''<section class="phero {cls}{' phero--img' if img else ''}">
  {media}
  <div class="container container--wide phero__inner">
    <span class="eyebrow{' eyebrow--light' if img else ''}">{eyebrow}</span>
    <h1>{title}</h1>
    {f'<p class="phero__sub">{sub}</p>' if sub else ''}
  </div>
</section>'''

def section_head(eyebrow, title, sub="", center=False):
    return f'''<div class="section-head{' section-head--center' if center else ''} reveal">
    <span class="eyebrow">{eyebrow}</span>
    <h2 class="section-title" style="margin-top:.55rem">{title}</h2>
    {f'<p class="lead" style="margin-top:1rem">{sub}</p>' if sub else ''}
  </div>'''

def cta_section(title, sub, primary=("Request a quote","/contact/"), whatsapp_msg=None):
    wa = f'<a class="btn btn--ghost btn--lg" href="{wa_link(whatsapp_msg)}" target="_blank" rel="noopener">{IC["whatsapp"]} WhatsApp us</a>' if whatsapp_msg else ""
    return f'''<section class="cta-band">
  <div class="container container--wide cta-band__inner reveal">
    <div>
      <h2>{title}</h2>
      <p>{sub}</p>
    </div>
    <div class="cta-band__actions">
      <a class="btn btn--solid btn--lg" href="{primary[1]}">{primary[0]} {IC['arrow']}</a>
      {wa}
    </div>
  </div>
</section>'''

def product_card(p, reveal=True):
    return f'''<a class="product-card{' reveal' if reveal else ''}" href="/products/{p['slug']}/" data-cat="{p['cat']}" aria-label="{esc(p['name'])}">
  <div class="product-card__media">
    <img src="{prod_img(p['slug'])}" alt="{esc(p['name'])} — Trivex Industrial Solutions" loading="lazy" decoding="async" width="820" height="615">
    <span class="product-card__cat">{CAT_LABEL[p['cat']]}</span>
  </div>
  <div class="product-card__body"><h3>{p['name']}</h3><p>{p['short']}</p>
    <span class="product-card__link">View product {IC['arrow']}</span></div>
</a>'''

def service_card(s):
    return f'''<a class="service-card reveal" href="/services/{s['slug']}/">
  <span class="service-card__ico">{IC[s['icon']]}</span>
  <h3>{s['name']}</h3>
  <p>{s['short']}</p>
  <span class="service-card__link">Explore service {IC['arrow']}</span>
</a>'''

def industry_card(i):
    return f'''<a class="industry-card reveal" href="/industries/#{i['slug']}">
  <div class="industry-card__media"><img src="/assets/img/{i['img']}" alt="{esc(i['name'])}" loading="lazy" width="760" height="500"></div>
  <div class="industry-card__body"><span class="industry-card__ico">{IC[i['icon']]}</span><h3>{i['name']}</h3><p>{i['desc']}</p></div>
</a>'''

# ----- Homepage (PDF tile layout) helpers -----
def bento_tile(t, href, kind):
    if kind == "feature":
        return (f'<a class="tile tile--feature reveal" href="{href}">'
                f'<span class="plus" aria-hidden="true">{IC["plus"]}</span>'
                f'<h3>{t}</h3>'
                f'<span class="icon-btn icon-btn--arrow on-green tile__arrow" aria-hidden="true">{IC["arrow"]}</span></a>')
    cls = "tile--green" if kind == "green" else "tile--white"
    return (f'<a class="tile {cls} reveal" href="{href}">'
            f'<span class="plus" aria-hidden="true">{IC["plus"]}</span><h3>{t}</h3></a>')

def home_product_card(p):
    return (f'<a class="product-card reveal" href="/products/{p["slug"]}/" data-cat="{p["cat"]}" aria-label="{esc(p["name"])}">'
            f'<div class="product-card__media">'
            f'<img src="{prod_img(p["slug"])}" alt="{esc(p["name"])} — Trivex Industrial Solutions" loading="lazy" decoding="async" width="820" height="615">'
            f'<span class="plus" aria-hidden="true">{IC["plus"]}</span></div>'
            f'<div class="product-card__body"><h3>{p["name"]}</h3><p>{p["short"]}</p></div></a>')

def home_solution_card(i, s):
    return (f'<a class="solution reveal" href="/services/{s["slug"]}/">'
            f'<div class="solution__head"><h3>{s["name"]}</h3><p>{s["short"]}</p></div>'
            f'<div class="solution__media"><span class="solution__num">{i:02d}</span>'
            f'<img src="/assets/img/{s["image"]}" alt="" loading="lazy" decoding="async" width="760" height="1000"></div></a>')

def gallery_fig(item):
    img, cap = item
    return (f'<figure class="reveal"><img src="/assets/img/{img}" alt="" loading="lazy" decoding="async">'
            f'<figcaption>{cap}</figcaption></figure>')

def faq_accordion(faqs):
    items = "".join(f'''<div class="acc__item">
      <button class="acc__q" aria-expanded="false"><span>{q}</span>{IC['chevron']}</button>
      <div class="acc__a"><div class="acc__a-inner"><p>{a}</p></div></div>
    </div>''' for q,a in faqs)
    ld = {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]}
    return f'<div class="acc">{items}</div>', ld

def client_marquee():
    """Seamless infinite-scroll strip of client logos (content duplicated once
    so translateX(-50%) loops without a visible seam)."""
    def cells(hidden=False):
        h = ' aria-hidden="true"' if hidden else ''
        return "".join(
            f'<div class="cell"{h}><img src="/assets/img/clients/{s}.jpg" alt="{esc(n)}" loading="lazy" decoding="async" width="{round(CLIENT_W[s]*34/120)}" height="34"></div>'
            for s,n in CLIENTS)
    return f'<div class="logo-marquee"><div class="logo-track">{cells()}{cells(hidden=True)}</div></div>'

def clients_strip(label="Trusted across the region"):
    return f'''<div class="clients reveal">
    <p class="clients__label">{label}</p>
    {client_marquee()}
  </div>'''

def footer():
    prod_links = "".join(f'<a href="/products/#{c[0]}">{c[1]}</a>' for c in PRODUCT_CATEGORIES)
    serv_links = "".join(f'<a href="/services/{s["slug"]}/">{s["name"]}</a>' for s in SERVICES[:6])
    return f'''<footer class="site-footer">
  <div class="container container--wide">
    <div class="footer-grid">
      <div class="footer-brand">
        {logo("footer-word")}
        <p>Complete industrial solutions — engineering, manufacturing, supply, installation and maintenance for water, wastewater, oil &amp; gas and heavy industry. Based in SAIF Zone, Sharjah, UAE.</p>
        <div class="footer-contact-inline">
          <a href="tel:{PHONE_TEL}">{IC['phone']} {PHONE_DISPLAY}</a>
          <a href="tel:{PHONE2_TEL}">{IC['phone']} {PHONE2_DISPLAY}</a>
          <a href="mailto:{EMAIL}">{IC['mail']} {EMAIL}</a>
        </div>
      </div>
      <div class="footer-col"><h2>Products</h2>{prod_links}</div>
      <div class="footer-col"><h2>Services</h2>{serv_links}</div>
      <div class="footer-col"><h2>Company</h2>
        <a href="/about/">About us</a><a href="/industries/">Industries</a><a href="/projects/">Projects</a><a href="/contact/">Contact</a>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© {YEAR} Trivex Industrial Solutions FZC. All rights reserved.</span>
      <div class="socials">
        <a href="mailto:{EMAIL}" aria-label="Email Trivex">{IC['mail']}</a>
        <a href="tel:{PHONE_TEL}" aria-label="Call Trivex">{IC['phone']}</a>
        <a href="{wa_link('Hello, I would like to know more about your products and services.')}" target="_blank" rel="noopener" aria-label="WhatsApp Trivex">{IC['whatsapp']}</a>
        <a href="{SITE}" aria-label="Trivex website">{IC['globe']}</a>
      </div>
    </div>
  </div>
</footer>'''

SYMBOL = f'<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><symbol id="trivexLogo" viewBox="{_logo_vb}" fill="currentColor">{_logo_inner}</symbol></svg>'

def shell(head_html, body, active, home=False, wa_msg="Hello, I would like to know more about your products and services.", splash=False):
    splash_html = f'<div id="splash" aria-hidden="true">{logo("splash-mark")}</div>' if splash else ""
    return f'''{head_html}
<body{' class="is-home"' if home else ''}>
{SYMBOL}
{splash_html}
<a class="skip-link" href="#main">Skip to content</a>
{header(active, home)}
<main id="main">
{body}
</main>
{footer()}
{whatsapp(wa_msg)}
<div class="lightbox" id="lightbox" role="dialog" aria-modal="true" aria-label="Image preview">
  <button class="lightbox__close" id="lightboxClose" aria-label="Close">&times;</button>
  <figure><img id="lightboxImg" src="" alt=""><figcaption><h3 id="lightboxTitle"></h3><p id="lightboxSpec"></p></figcaption></figure>
</div>
<script src="/assets/js/main.js?v={JS_VER}" defer></script>
</body>
</html>'''

# =====================================================================
#  PAGE BUILDERS
# =====================================================================
def write(path, content):
    if BASE:  # prefix internal root-relative paths for sub-path hosting (e.g. GitHub Pages)
        content = (content.replace('href="/', f'href="{BASE}/')
                          .replace('src="/', f'src="{BASE}/')
                          .replace('data-img="/', f'data-img="{BASE}/'))
    full = os.path.join(ROOT, path.strip("/"), "index.html") if path != "/" else os.path.join(ROOT, "index.html")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w").write(content)

PAGES = []  # (path, priority) for sitemap

def page_home():
    featured = [p for p in PRODUCTS if p["featured"]][:8]
    hero_slides = [("bg/hero.jpg","Trivex industrial manufacturing facility with automated process lines"),
                   ("bg/hero-alt.jpg","Automated robotic assembly on the production line"),
                   ("bg/products-1.jpg","Aerial view of a large-scale industrial production floor"),
                   ("bg/products-2.jpg","Process conveying and material-handling systems")]
    slides = "".join(
        f'<img class="hero-slide{" is-active" if i==0 else ""}" src="/assets/img/{img}" alt="{esc(alt) if i==0 else ""}"{" fetchpriority=\"high\"" if i==0 else " loading=\"lazy\" aria-hidden=\"true\""} width="1800" height="1200">'
        for i,(img,alt) in enumerate(hero_slides))
    dots = "".join(f'<button role="tab" aria-label="Slide {i+1}"{" aria-selected=\"true\"" if i==0 else ""}></button>' for i in range(len(hero_slides)))
    stats = "".join(f'<div class="stat reveal" data-delay="{i}"><b data-count="{v}" data-suffix="{suf}">{v}{suf}</b><span>{l}</span></div>'
                    for i,(v,suf,l) in enumerate([(str(len(PRODUCTS)),"+","Engineered product lines"),("8","","Specialist services"),("6","","Industries served"),("360","°","Design · build · maintain")]))
    bento_html = "".join(bento_tile(*b) for b in BENTO)
    filters = "".join(
        f'<button role="tab" data-filter="{k}"{" class=\"is-active\" aria-selected=\"true\"" if k=="all" else " aria-selected=\"false\""}>{lbl}</button>'
        for k,lbl in [("all","All products")] + [(c[0],c[1]) for c in PRODUCT_CATEGORIES])
    products_html = "".join(home_product_card(p) for p in PRODUCTS)
    solutions_html = "".join(home_solution_card(i+1,s) for i,s in enumerate(SERVICES))
    future_imgs = "".join(f'<figure class="reveal" data-delay="{i}"><img src="/assets/img/cta/cta-{i+1}.jpg" alt="Advanced industrial engineering at Trivex" loading="lazy" width="700" height="700"></figure>' for i in range(4))
    gallery_html = "".join(gallery_fig((img,cap)) for img,cap,_ in PROJECTS[:12])
    mosaic_html = "".join(f'<img src="/assets/img/{m}" alt="" loading="lazy">' for m in MOSAIC)
    pillars = "".join(f'<div class="pillar"><span class="tick">{IC["check"]}</span><div><b>{t}</b><p>{d}</p></div></div>'
        for t,d in [("Engineered in-house","Fabrication, assembly and testing under one roof for consistent, traceable quality."),
                    ("Complete lifecycle","From concept and supply through to installation, commissioning and upkeep."),
                    ("Built for regional industry","Serving utilities, free-zone developers and process plants across the UAE and GCC.")])
    body = f'''
  <section class="hero" id="home">
    <div class="hero__media" id="heroSlides" aria-label="Facility image slideshow" role="group">{slides}</div>
    <div class="container container--wide hero__inner">
      <h1>Complete <em>Industrial</em> Solutions</h1>
      <p class="hero__sub">Engineering, manufacturing, supply, installation and maintenance — delivered end-to-end from our SAIF Zone facility in Sharjah for water, wastewater, oil &amp; gas, mining and heavy process industries.</p>
      <div class="hero__actions">
        <a class="btn btn--solid btn--lg" href="/products/">Explore products {IC['arrow']}</a>
        <a class="btn btn--ghost btn--lg" href="/contact/">Talk to our team</a>
      </div>
      <div class="hero__dots" id="heroDots" role="tablist" aria-label="Choose slide">{dots}</div>
    </div>
  </section>
  <div class="stat-ribbon"><div class="container container--wide">{stats}</div></div>

  <!-- ABOUT -->
  <section class="section" id="about">
    <div class="container container--wide">
      <div class="about__intro">
        <div class="section-head reveal">
          <span class="eyebrow">Who we are</span>
          <h2 class="section-title" style="margin-top:.6rem">About us</h2>
          <p class="lead" style="margin-top:1rem">Trivex Industrial Solutions is a Sharjah-based industrial partner delivering the complete lifecycle — engineering, manufacturing, supply, installation and maintenance — for water and wastewater treatment, oil &amp; gas, mining and heavy process industries.</p>
          <p class="muted" style="margin-top:1rem">From our SAIF Zone facility we fabricate, assemble and service a broad catalogue of process equipment, backed by control-panel manufacturing, valve supply and responsive on-site troubleshooting.</p>
          <a class="btn btn--outline" style="margin-top:1.5rem" href="/about/">More about us {IC['arrow']}</a>
        </div>
        <div class="pillars reveal" data-delay="1">{pillars}</div>
      </div>
      <div class="clients reveal">
        <p class="clients__label">Our clients</p>
        {client_marquee()}
        <div class="partner-row"><p class="clients__label" style="margin:0">Our channel partners</p><a href="https://aquaxuae.com/" target="_blank" rel="noopener" aria-label="Aqua X"><img src="/assets/img/clients/aquax.jpg" alt="Aqua X" loading="lazy" decoding="async" width="138" height="30"></a><a href="https://www.unicorn-valves.com/" target="_blank" rel="noopener" aria-label="Unicorn Valves"><img class="partner-row__tall" src="/assets/img/clients/unicorn-valves.png" alt="Unicorn Valves" loading="lazy" decoding="async" width="104" height="44"></a></div>
      </div>
      <div class="bento">{bento_html}</div>
    </div>
  </section>

  <!-- PRODUCTS -->
  <section class="section section--tint" id="products">
    <div class="container container--wide">
      <div class="products__head">
        <div class="products__tag reveal"><h2>Products</h2><span class="icon-btn icon-btn--arrow on-green" aria-hidden="true">{IC['arrow']}</span></div>
        <div class="section-head reveal" data-delay="1">
          <span class="eyebrow">What we deliver</span>
          <p class="lead" style="margin-top:.6rem">A comprehensive catalogue of process equipment — engineered, fabricated and supplied for water, wastewater, oil &amp; gas and heavy industry. Filter by category to explore.</p>
        </div>
      </div>
      <div class="filter-bar" role="tablist" aria-label="Filter products">{filters}</div>
      <div class="product-grid" id="productGrid">{products_html}</div>
      <p class="product-empty" id="productEmpty" hidden>No products in this category.</p>
      <div class="products__more"><a class="btn btn--outline" href="/products/">View all products {IC['arrow']}</a></div>
    </div>
  </section>

  <!-- SOLUTIONS -->
  <section class="section solutions" id="solutions">
    <div class="container container--wide">
      <div class="section-head reveal">
        <span class="eyebrow">How we help</span>
        <h2 class="section-title" style="margin-top:.6rem">Solutions</h2>
        <p class="lead" style="margin-top:1rem">Eight capability areas that take a project from first drawing to dependable, long-term operation.</p>
      </div>
      <div class="solution-grid">{solutions_html}</div>
    </div>
  </section>

  <!-- DESIGN THE FUTURE -->
  <section class="section future">
    <div class="container container--wide">
      <div class="future__band reveal">
        {logo("future__logo")}
        <h2 class="future__title">Design <span class="arrow">{IC['arrow']}</span> the <em>future</em></h2>
        <a class="btn btn--outline future__cta" href="/contact/">Work with us</a>
      </div>
      <div class="future__gallery">{future_imgs}</div>
    </div>
  </section>

  <!-- GALLERY -->
  <section class="section section--tint" id="gallery">
    <div class="container container--wide">
      <div class="section-head reveal">
        <span class="eyebrow">Our work</span>
        <h2 class="section-title" style="margin-top:.6rem">Project <strong>gallery</strong></h2>
        <p class="lead" style="margin-top:1rem">A look at the equipment, installations and process systems we design, build and maintain.</p>
      </div>
      <div class="gallery__grid">{gallery_html}</div>
      <div class="products__more" style="margin-top:2rem"><a class="btn btn--outline" href="/projects/">View all projects {IC['arrow']}</a></div>
    </div>
  </section>

  <!-- PLANET -->
  <section class="planet" id="planet">
    <div class="planet__mosaic" aria-hidden="true">{mosaic_html}</div>
    <div class="container container--wide">
      <div class="planet__content reveal">
        <span class="eyebrow eyebrow--light">Responsibility</span>
        <h2 style="margin-top:.6rem">Our policies, <strong>our planet</strong></h2>
        <p>Clean water and responsible industry sit at the heart of what we build. We design for recovery and reuse, energy efficiency and safe, low-impact operation — because the systems we deliver today shape the resources of tomorrow.</p>
        <div class="planet__badges">
          <div class="planet__badge"><b>Water</b><span>Designed for reuse &amp; recovery</span></div>
          <div class="planet__badge"><b>Energy</b><span>Efficient by design</span></div>
          <div class="planet__badge"><b>Safety</b><span>HSE-led delivery</span></div>
        </div>
      </div>
    </div>
    <div class="planet__powered">powered by {logo("planet__logo")}</div>
  </section>

  <!-- CONTACT -->
  <section class="section contact" id="contact">
    <img class="contact__pin" src="/assets/img/scene/pin.png" alt="" aria-hidden="true" loading="lazy">
    <div class="container container--wide">
      <div class="contact__grid">
        <div class="reveal">
          <span class="eyebrow">Get in touch</span>
          <h2 class="contact__title" style="margin-top:.6rem">Contact us</h2>
          <p class="lead" style="margin-top:1rem;max-width:44ch">Tell us about your project — supply, fabrication, installation or maintenance. Our team will get back to you.</p>
          <div class="contact-details">
            <div class="contact-item"><span class="ci-ico">{IC['pin']}</span><div><h3>UAE Office</h3><address>Trivex Industrial Solutions FZC<br>Warehouse Q3-65, SAIF Zone<br>Sharjah, United Arab Emirates</address></div></div>
            <div class="contact-item"><span class="ci-ico">{IC['phone']}</span><div><h3>Telephone</h3><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a><br><a href="tel:{PHONE2_TEL}">{PHONE2_DISPLAY}</a></div></div>
            <div class="contact-item"><span class="ci-ico">{IC['mail']}</span><div><h3>Email</h3><a href="mailto:{EMAIL}">{EMAIL}</a></div></div>
            <div class="contact-item"><span class="ci-ico">{IC['whatsapp']}</span><div><h3>WhatsApp</h3><a href="{wa_link('Hello, I would like to know more about your products and services.')}" target="_blank" rel="noopener">Chat with our team</a></div></div>
          </div>
        </div>
        {contact_form("        ")}
      </div>
    </div>
  </section>
'''
    h = head("Trivex Industrial Solutions | Complete Industrial Solutions — Sharjah, UAE",
             "Trivex Industrial Solutions FZC — complete industrial solutions from Sharjah, UAE. Engineering, manufacturing, supply, installation and maintenance for water & wastewater, oil & gas, mining and heavy industry.",
             "/", preload_hero=True)
    write("/", shell(h, body, "home", home=True, splash=True))
    PAGES.append(("/", "1.0"))

def page_about():
    bc, bc_ld = breadcrumbs([("Home","/"),("About",None)])
    pillars = "".join(f'<div class="pillar reveal"><span class="tick">{IC["check"]}</span><div><b>{t}</b><p>{d}</p></div></div>'
        for t,d in [("Engineered in-house","Fabrication, assembly and testing under one roof for consistent, traceable quality."),
                    ("Complete lifecycle","From concept and supply through to installation, commissioning and upkeep."),
                    ("Built for regional industry","Serving utilities, free-zone developers and process plants across the UAE and GCC.")])
    vals = "".join(f'<div class="why-card reveal" data-delay="{n%3}"><span class="why-card__ico">{IC[ic]}</span><h3>{t}</h3><p>{d}</p></div>' for n,(ic,t,d) in enumerate(WHY_US))
    body = f'''
  {page_hero("Who we are","Complete industrial solutions, delivered end-to-end",
    "Trivex Industrial Solutions is a Sharjah-based industrial partner delivering engineering, manufacturing, supply, installation and maintenance across water, oil &amp; gas, mining and process industries.",
    img="scene/about-workers.jpg")}
  {bc}
  <section class="section">
    <div class="container container--wide about__intro">
      <div class="reveal">
        <span class="eyebrow">Our story</span>
        <h2 class="section-title" style="margin-top:.55rem">One partner for the whole lifecycle</h2>
        <p class="lead" style="margin-top:1rem">From our SAIF Zone facility we fabricate, assemble and service a broad catalogue of process equipment, backed by control-panel manufacturing, valve supply and responsive on-site troubleshooting.</p>
        <p class="muted" style="margin-top:1rem">We exist to make industrial delivery simpler: one accountable team that can engineer a solution, build it, install it and keep it running — so our clients spend less time coordinating suppliers and more time operating.</p>
      </div>
      <div class="pillars reveal" data-delay="1">{pillars}</div>
    </div>
  </section>
  <section class="section section--dark why">
    <div class="container container--wide">
      {section_head("What drives us","Values that shape every project","", center=True)}
      <div class="why-grid">{vals}</div>
    </div>
  </section>
  <section class="section section--tint"><div class="container container--wide">{clients_strip("Trusted by leading organisations")}</div></section>
  {cta_section("Work with a partner who owns the outcome","From first drawing to long-term maintenance, Trivex delivers.", whatsapp_msg="Hello, I would like to know more about Trivex Industrial Solutions.")}
'''
    h = head("About Trivex Industrial Solutions | Sharjah, UAE",
             "Trivex Industrial Solutions FZC is a Sharjah-based industrial partner delivering engineering, manufacturing, supply, installation and maintenance across water, oil & gas, mining and process industries.",
             "/about/", og_image="/assets/img/scene/about-workers.jpg", ld=bc_ld)
    write("/about/", shell(h, body, "about"))
    PAGES.append(("/about/","0.8"))

def page_products():
    bc, bc_ld = breadcrumbs([("Home","/"),("Products",None)])
    filters = "".join(
        f'<button role="tab" data-filter="{k}"{" class=\"is-active\" aria-selected=\"true\"" if k=="all" else " aria-selected=\"false\""}>{lbl}</button>'
        for k,lbl in [("all","All products")] + [(c[0],c[1]) for c in PRODUCT_CATEGORIES])
    grid = "".join(product_card(p) for p in PRODUCTS)
    body = f'''
  {page_hero("Products","Process equipment engineered for industry",
    f"{len(PRODUCTS)} product lines across water &amp; wastewater, filtration, valves &amp; flow, lifting, fabrication and control — engineered, fabricated and supplied to your requirement.", img="bg/products-1.jpg")}
  {bc}
  <section class="section">
    <div class="container container--wide">
      <div class="filter-bar" role="tablist" aria-label="Filter products" id="productFilter">{filters}</div>
      <div class="product-grid" id="productGrid">{grid}</div>
      <p class="product-empty" id="productEmpty" hidden>No products in this category.</p>
    </div>
  </section>
  {cta_section("Can't find exactly what you need?","We engineer and fabricate to specification. Send us your requirement for a tailored proposal.", primary=("Request the catalogue","/contact/"), whatsapp_msg="Hello, I would like to request the Trivex product catalogue.")}
'''
    ld = {"@context":"https://schema.org","@type":"CollectionPage","name":"Products","url":SITE+"/products/"}
    h = head("Products | Trivex Industrial Solutions",
             f"Browse {len(PRODUCTS)} industrial product lines from Trivex — water & wastewater treatment, filtration & screening, valves & flow, lifting & cranes, fabrication and instrumentation.",
             "/products/", ld=bc_ld)
    write("/products/", shell(h, body, "products", wa_msg="Hello, I would like to know more about your products."))
    PAGES.append(("/products/","0.9"))

def page_product(p):
    bc, bc_ld = breadcrumbs([("Home","/"),("Products","/products/"),(p["name"],None)])
    related = [q for q in PRODUCTS if q["cat"]==p["cat"] and q["slug"]!=p["slug"]][:4]
    if len(related) < 4:
        related += [q for q in PRODUCTS if q["slug"]!=p["slug"] and q not in related][:4-len(related)]
    benefits = "".join(f'<li><span class="tick">{IC["check"]}</span><div>{b}</div></li>' for b in p["benefits"])
    brand = BRANDS.get(p["brand"])
    features = "".join(f'<li>{IC["check"]}<span>{esc(f)}</span></li>' for f in p["features"] or CAT_FEATURES[p["cat"]])
    specs = "".join(f'<tr><th>{lbl}</th><td>{esc(val)}</td></tr>' for lbl,val in p["specs"] or CAT_SPECS[p["cat"]])
    apps = "".join(f'<div class="app-chip">{IC["chevron-r"]}<span>{a}</span></div>' for a in p["apps"] or CAT_APPLICATIONS[p["cat"]])
    faqs = cat_faqs(p["name"], p["cat"])
    if brand:
        faqs = [(f"Who manufactures the {p['name']}?",
                 f"{brand['about']} Trivex Industrial Solutions is a channel partner for {brand['name']} in the UAE, handling selection, supply and support.")] + faqs
    spec_note = (f'Data from the {brand["name"]} product brochure. Contact us for a datasheet and sizing matched to your duty.' if brand
                 else "Specifications are engineered to each project. Contact us for a datasheet matched to your duty.")
    brochure_btn = (f'<a class="btn btn--outline" href="{brand["brochure"]}" target="_blank" rel="noopener">{IC["arrow-ur"]} {brand["name"]} brochure (PDF)</a>'
                    if brand else "")
    why = ([("factory","Authorised channel partner",f"Genuine {brand['name']} equipment supplied through Trivex in the UAE."),
            ("gear","Selected to fit","Sized and configured to your process conditions, materials and piping."),
            ("clock","Supported for life","Installation, spares and maintenance keep it running.")] if brand else
           [("factory","Built in-house","Engineered and fabricated at our SAIF Zone facility with full traceability."),
            ("gear","Engineered to fit","Configured to your process, materials and installation constraints."),
            ("clock","Supported for life","Installation, spares and maintenance keep it running.")])
    why_html = "".join(f'<div><span class="why-card__ico">{IC[i]}</span><b>{t}</b><p>{d}</p></div>' for i,t,d in why)
    faq_html, faq_ld = faq_accordion(faqs)
    rel_html = "".join(product_card(q) for q in related)
    wa_msg = f"Hello, I am interested in {p['name']}. I would like to know more about this product."
    tabs = f'''<div class="tabs" data-tabs>
      <div class="tabs__nav" role="tablist" aria-label="Product details">
        <button role="tab" aria-selected="true" data-tab="overview">Overview</button>
        <button role="tab" aria-selected="false" data-tab="features">Features</button>
        <button role="tab" aria-selected="false" data-tab="specs">Specifications</button>
        <button role="tab" aria-selected="false" data-tab="apps">Applications</button>
      </div>
      <div class="tabs__panel is-active" data-panel="overview">
        <p class="lead">{p['long']}</p>
        <h3 class="tabs__sub">Key benefits</h3>
        <ul class="benefit-list">{benefits}</ul>
      </div>
      <div class="tabs__panel" data-panel="features">
        <h3 class="tabs__sub">Features &amp; capabilities</h3>
        <ul class="feature-list">{features}</ul>
      </div>
      <div class="tabs__panel" data-panel="specs">
        <h3 class="tabs__sub">Technical specifications</h3>
        <table class="spec-table">{specs}</table>
        <p class="muted" style="margin-top:1rem">{spec_note}</p>
      </div>
      <div class="tabs__panel" data-panel="apps">
        <h3 class="tabs__sub">Applications &amp; use cases</h3>
        <div class="app-grid">{apps}</div>
      </div>
    </div>'''
    enquiry_card = f'''<aside class="enquiry-card">
      <span class="enquiry-card__cat">{CAT_LABEL[p['cat']]}</span>
      <h2>Enquire about the {p['name']}</h2>
      <p>Get a tailored specification, datasheet and quotation for your project.</p>
      <a class="btn btn--solid btn--lg" href="/contact/?product={p['slug']}">Request a quote {IC['arrow']}</a>
      <a class="btn btn--wa btn--lg" href="{wa_link(wa_msg)}" target="_blank" rel="noopener">{IC['whatsapp']} Enquire on WhatsApp</a>
      {brochure_btn}
      <a class="btn btn--ghost-dark" href="/products/">{IC['chevron']} All products</a>
      <div class="enquiry-card__contact">
        <a href="tel:{PHONE_TEL}">{IC['phone']} {PHONE_DISPLAY}</a>
        <a href="tel:{PHONE2_TEL}">{IC['phone']} {PHONE2_DISPLAY}</a>
        <a href="mailto:{EMAIL}">{IC['mail']} Email us</a>
      </div>
    </aside>'''
    body = f'''
  {bc}
  <section class="pd-hero">
    <div class="container container--wide pd-hero__grid">
      <div class="pd-hero__media reveal"><img src="{prod_img(p['slug'])}" alt="{esc(p['name'])} — Trivex Industrial Solutions" width="820" height="615" fetchpriority="high"></div>
      <div class="pd-hero__body reveal" data-delay="1">
        <span class="eyebrow">{CAT_LABEL[p['cat']]}{' · ' + brand['name'] if brand else ''}</span>
        <h1>{p['name']}</h1>
        <p class="lead">{p['short']}. {p['long']}</p>
        <div class="pd-hero__actions">
          <a class="btn btn--solid btn--lg" href="/contact/?product={p['slug']}">Request a quote {IC['arrow']}</a>
          <a class="btn btn--wa btn--lg" href="{wa_link(wa_msg)}" target="_blank" rel="noopener">{IC['whatsapp']} WhatsApp</a>
        </div>
      </div>
    </div>
  </section>
  <section class="section pd-main">
    <div class="container container--wide pd-main__grid">
      <div><h2 class="sr-only">Product information</h2>{tabs}
        <div class="pd-why reveal">
          <h3 class="tabs__sub">Why choose Trivex for the {p['name']}</h3>
          <div class="pd-why__grid">{why_html}</div>
        </div>
      </div>
      {enquiry_card}
    </div>
  </section>
  <section class="section section--tint">
    <div class="container container--wide">
      {section_head("Questions","Frequently asked questions")}
      {faq_html}
    </div>
  </section>
  <section class="section">
    <div class="container container--wide">
      {section_head("Related","Related products")}
      <div class="product-grid product-grid--home">{rel_html}</div>
    </div>
  </section>
  {cta_section(f"Ready to specify your {p['name']}?","Our engineers will help you select and configure the right solution.", primary=("Request a quote","/contact/?product="+p['slug']), whatsapp_msg=wa_msg)}
'''
    prod_ld = {"@context":"https://schema.org","@type":"Product","name":p["name"],
        "description":p["long"],"category":CAT_LABEL[p["cat"]],
        "image":SITE+prod_img(p['slug']),
        "brand":{"@type":"Brand","name":brand["name"] if brand else "Trivex Industrial Solutions"},
        "url":SITE+f"/products/{p['slug']}/"}
    h = head(f"{p['name']} | Trivex Industrial Solutions",
             f"{p['name']} — {p['short']}. {p['long'][:120]}",
             f"/products/{p['slug']}/", og_image=prod_img(p['slug']),
             ld={"@context":"https://schema.org","@graph":[bc_ld, prod_ld, faq_ld]})
    write(f"/products/{p['slug']}/", shell(h, body, "products", wa_msg=wa_msg))
    PAGES.append((f"/products/{p['slug']}/","0.7"))

def page_services():
    bc, bc_ld = breadcrumbs([("Home","/"),("Services",None)])
    grid = "".join(f'''<a class="service-card service-card--lg reveal" href="/services/{s['slug']}/">
      <div class="service-card__media"><img src="/assets/img/{s['image']}" alt="{esc(s['name'])}" loading="lazy" width="760" height="500"></div>
      <div class="service-card__body"><span class="service-card__ico">{IC[s['icon']]}</span><h3>{s['name']}</h3><p>{s['short']}</p>
      <span class="service-card__link">Explore service {IC['arrow']}</span></div>
    </a>''' for s in SERVICES)
    body = f'''
  {page_hero("Services","Capability across the industrial lifecycle",
    "Eight specialist services that take a project from first drawing to dependable, long-term operation.", img="bg/hero-alt.jpg")}
  {bc}
  <section class="section"><div class="container container--wide"><div class="service-grid service-grid--lg">{grid}</div></div></section>
  {cta_section("Not sure which service you need?","Tell us the challenge and our team will point you to the right solution.", primary=("Talk to an expert","/contact/"), whatsapp_msg="Hello, I would like to discuss your services.")}
'''
    h = head("Services | Trivex Industrial Solutions",
             "Trivex services: valve supply & maintenance, industrial installations, manufacturing & assembly, water & wastewater treatment, troubleshooting, mining solutions, control-panel manufacturing and air monitoring.",
             "/services/", ld=bc_ld)
    write("/services/", shell(h, body, "services", wa_msg="Hello, I would like to know more about your services."))
    PAGES.append(("/services/","0.9"))

def page_service(s):
    bc, bc_ld = breadcrumbs([("Home","/"),("Services","/services/"),(s["name"],None)])
    steps = "".join(f'''<div class="timeline__step reveal" data-delay="{n%3}">
      <span class="timeline__num">{n+1:02d}</span>
      <div><h3>{t}</h3><p>{d}</p></div></div>''' for n,(t,d) in enumerate(s["process"]))
    caps = "".join(f'<li>{IC["check"]}<span>{c}</span></li>' for c in s["capabilities"])
    inds = "".join(f'<a class="pill-link" href="/industries/#{IND[i]["slug"]}">{IND[i]["name"]}</a>' for i in s["industries"] if i in IND)
    faq_html, faq_ld = faq_accordion(s["faqs"])
    others = [x for x in SERVICES if x["slug"]!=s["slug"]][:3]
    others_html = "".join(service_card(x) for x in others)
    wa_msg = f"Hello, I would like to know more about your {s['name']} service."
    body = f'''
  {page_hero(s["short"], s["name"], s["overview"], img=s["image"])}
  {bc}
  <section class="section">
    <div class="container container--wide sv-grid">
      <div class="reveal">
        <span class="eyebrow">The challenge</span>
        <h2 class="section-title" style="margin-top:.55rem;font-size:var(--fs-h3)">{s['problem']}</h2>
        <p class="lead" style="margin-top:1rem">{s['overview']}</p>
        <h3 class="tabs__sub" style="margin-top:2rem">Key capabilities</h3>
        <ul class="feature-list feature-list--2">{caps}</ul>
        <h3 class="tabs__sub" style="margin-top:2rem">Industries served</h3>
        <div class="pill-links">{inds}</div>
      </div>
      <aside class="enquiry-card enquiry-card--sticky">
        <span class="enquiry-card__cat">{s['short']}</span>
        <h2>Talk to us about {s['name']}</h2>
        <p>Tell us your challenge and our engineers will propose the right approach.</p>
        <a class="btn btn--solid btn--lg" href="/contact/?service={s['slug']}">Request a consultation {IC['arrow']}</a>
        <a class="btn btn--wa btn--lg" href="{wa_link(wa_msg)}" target="_blank" rel="noopener">{IC['whatsapp']} WhatsApp us</a>
        <div class="enquiry-card__contact">
          <a href="tel:{PHONE_TEL}">{IC['phone']} {PHONE_DISPLAY}</a>
          <a href="tel:{PHONE2_TEL}">{IC['phone']} {PHONE2_DISPLAY}</a>
          <a href="mailto:{EMAIL}">{IC['mail']} Email us</a>
        </div>
      </aside>
    </div>
  </section>
  <section class="section section--tint">
    <div class="container container--wide">
      {section_head("How we work","Our process","A disciplined, transparent workflow from first contact to handover.")}
      <div class="timeline">{steps}</div>
    </div>
  </section>
  <section class="section">
    <div class="container container--wide">
      {section_head("Questions","Frequently asked questions")}
      {faq_html}
    </div>
  </section>
  <section class="section section--tint">
    <div class="container container--wide">
      {section_head("More","Other services")}
      <div class="service-grid">{others_html}</div>
    </div>
  </section>
  {cta_section(f"Ready to move forward with {s['name']}?","Talk to an expert about your requirement today.", primary=("Talk to an expert","/contact/?service="+s['slug']), whatsapp_msg=wa_msg)}
'''
    serv_ld = {"@context":"https://schema.org","@type":"Service","serviceType":s["name"],
        "provider":{"@type":"Organization","name":"Trivex Industrial Solutions"},
        "areaServed":"AE","description":s["overview"],"url":SITE+f"/services/{s['slug']}/"}
    h = head(f"{s['name']} | Trivex Industrial Solutions",
             f"{s['name']} — {s['overview'][:150]}",
             f"/services/{s['slug']}/", og_image=f"/assets/img/{s['image']}",
             ld={"@context":"https://schema.org","@graph":[bc_ld, serv_ld, faq_ld]})
    write(f"/services/{s['slug']}/", shell(h, body, "services", wa_msg=wa_msg))
    PAGES.append((f"/services/{s['slug']}/","0.7"))

def page_industries():
    bc, bc_ld = breadcrumbs([("Home","/"),("Industries",None)])
    sections = ""
    for n,i in enumerate(INDUSTRIES):
        provides = "".join(f'<li>{IC["check"]}<span>{x}</span></li>' for x in i["provides"])
        flip = " ind-row--flip" if n%2 else ""
        sections += f'''<div class="ind-row{flip} reveal" id="{i['slug']}">
          <div class="ind-row__media"><img src="/assets/img/{i['img']}" alt="{esc(i['name'])}" loading="lazy" width="760" height="560"></div>
          <div class="ind-row__body">
            <span class="why-card__ico">{IC[i['icon']]}</span>
            <h2>{i['name']}</h2>
            <p class="lead">{i['desc']}</p>
            <ul class="feature-list feature-list--2">{provides}</ul>
            <a class="btn btn--outline" href="/contact/?industry={i['slug']}">Discuss your project {IC['arrow']}</a>
          </div>
        </div>'''
    body = f'''
  {page_hero("Industries &amp; solutions","Tailored to the sectors we serve",
    "From utilities and oil &amp; gas to mining, manufacturing, facilities and marine — equipment and services matched to each industry's demands.", img="bg/products-3.jpg")}
  {bc}
  <section class="section"><div class="container container--wide ind-rows">{sections}</div></section>
  {cta_section("Every industry is different. So is every solution.","Tell us your sector and challenge — we'll tailor the right equipment and service.", whatsapp_msg="Hello, I would like to discuss a solution for my industry.")}
'''
    h = head("Industries & Solutions | Trivex Industrial Solutions",
             "Trivex serves water & wastewater utilities, oil & gas, mining & minerals, manufacturing, buildings & facilities and marine & desalination with tailored industrial equipment and services.",
             "/industries/", ld=bc_ld)
    write("/industries/", shell(h, body, "industries", wa_msg="Hello, I would like to know more about your industry solutions."))
    PAGES.append(("/industries/","0.8"))

def page_projects():
    bc, bc_ld = breadcrumbs([("Home","/"),("Projects",None)])
    filters = "".join(
        f'<button role="tab" data-filter="{k}"{" class=\"is-active\" aria-selected=\"true\"" if k=="all" else " aria-selected=\"false\""}>{lbl}</button>'
        for k,lbl in PROJECT_CATS)
    tiles = "".join(
        f'''<button class="proj-tile reveal" data-cat="{cat}" data-img="/assets/img/{img}" data-name="{esc(cap)}" aria-label="{esc(cap)}">
          <img src="/assets/img/{img}" alt="" loading="lazy" width="600" height="450">
          <span class="proj-tile__cap">{cap}</span></button>''' for img,cap,cat in PROJECTS)
    body = f'''
  {page_hero("Our work","Project gallery",
    "Equipment, installations and process systems we have designed, fabricated, installed and maintained.", img="bg/products-2.jpg")}
  {bc}
  <section class="section">
    <div class="container container--wide">
      <div class="filter-bar" role="tablist" aria-label="Filter projects" id="projectFilter">{filters}</div>
      <div class="proj-grid" id="projectGrid">{tiles}</div>
    </div>
  </section>
  {cta_section("Have a project in mind?","From a single equipment package to a full plant, Trivex delivers end-to-end.", whatsapp_msg="Hello, I would like to discuss a project with Trivex.")}
'''
    h = head("Projects & Gallery | Trivex Industrial Solutions",
             "A gallery of Trivex projects — water & wastewater treatment, fabrication, industrial installations, control panels, mining and lifting equipment.",
             "/projects/", ld=bc_ld)
    write("/projects/", shell(h, body, "projects", wa_msg="Hello, I would like to know more about your projects."))
    PAGES.append(("/projects/","0.7"))

def page_contact():
    bc, bc_ld = breadcrumbs([("Home","/"),("Contact",None)])
    body = f'''
  {page_hero("Get in touch","Let's talk about your project",
    "Tell us what you need — supply, fabrication, installation or maintenance — and our team will respond within one business day.", img="bg/products-4.jpg")}
  {bc}
  <section class="section contact">
    <div class="container container--wide contact__grid">
      <div class="reveal">
        <div class="contact-details">
          <div class="contact-item"><span class="ci-ico">{IC['pin']}</span><div><h3>UAE Office</h3><address>Trivex Industrial Solutions FZC<br>Warehouse Q3-65, SAIF Zone<br>Sharjah, United Arab Emirates</address></div></div>
          <div class="contact-item"><span class="ci-ico">{IC['phone']}</span><div><h3>Telephone</h3><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a><br><a href="tel:{PHONE2_TEL}">{PHONE2_DISPLAY}</a></div></div>
          <div class="contact-item"><span class="ci-ico">{IC['mail']}</span><div><h3>Email</h3><a href="mailto:{EMAIL}">{EMAIL}</a></div></div>
          <div class="contact-item"><span class="ci-ico">{IC['whatsapp']}</span><div><h3>WhatsApp</h3><a href="{wa_link('Hello, I would like to know more about your products and services.')}" target="_blank" rel="noopener">Chat with our team</a></div></div>
        </div>
        <div class="contact-map reveal">
          <iframe title="Trivex Industrial Solutions (FZC) — SAIF Zone, Sharjah" loading="lazy" referrerpolicy="no-referrer-when-downgrade"
            src="https://www.google.com/maps?q=Trivex+Industrial+Solutions+%28FZC%29,+SAIF+Zone,+Sharjah&output=embed"></iframe>
        </div>
      </div>
      {contact_form("      ")}
    </div>
  </section>
'''
    h = head("Contact | Trivex Industrial Solutions — Sharjah, UAE",
             "Contact Trivex Industrial Solutions FZC — SAIF Zone, Sharjah, UAE. Request a quote for industrial products, fabrication, installation or maintenance. Call +971 6 534 6311.",
             "/contact/", ld=bc_ld)
    write("/contact/", shell(h, body, "contact", wa_msg="Hello, I would like to get in touch with Trivex."))
    PAGES.append(("/contact/","0.8"))

def build_sitemap():
    urls = "".join(f'  <url><loc>{SITE}{path}</loc><changefreq>monthly</changefreq><priority>{pri}</priority></url>\n' for path,pri in PAGES)
    xml = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n'
    open(os.path.join(ROOT,"sitemap.xml"),"w").write(xml)

def build_robots():
    open(os.path.join(ROOT,"robots.txt"),"w").write(
        f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")

def main():
    page_home(); page_about(); page_products()
    for p in PRODUCTS: page_product(p)
    page_services()
    for s in SERVICES: page_service(s)
    page_industries(); page_projects(); page_contact()
    build_sitemap(); build_robots()
    print(f"Built {len(PAGES)} pages:")
    print(f"  1 home + about + products({len(PRODUCTS)}) + services({len(SERVICES)}) + industries + projects + contact")
    print(f"  sitemap.xml with {len(PAGES)} URLs")

if __name__ == "__main__":
    main()
