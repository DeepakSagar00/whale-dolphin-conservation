"""Generate the multi-page website for the Intelligent Whale & Dolphin Conservation Platform."""
import os

ROOT = r"C:\Users\Deepak Sagar\OneDrive\Desktop\MoveOne\whale-dolphin-conservation\website"

# ------------------------------------------------------------------ assets
VERSION = "v3"

LOGO = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" role="img" aria-label="Whale and Dolphin Conservation">
  <path d="M8 30c0-5.4 4.4-9.8 10-9.8 3.3 0 6.2 1.6 8 4.1 1.8-2.5 4.7-4.1 8-4.1 5.6 0 10 4.4 10 9.8 0 2.6-2 4.6-4.6 4.6H12.6A4.6 4.6 0 0 1 8 30Z" fill="#ffffff" opacity=".95"/>
  <path d="M8 30 2.5 23.5 5 30l-2.5 6.5Z" fill="#ffffff" opacity=".95"/>
  <circle cx="31.5" cy="27.5" r="1.6" fill="#17a2b8"/>
  <path d="M14 20.5c1.6-4.4 5.4-7.5 10-7.5 3.6 0 6.9 1.9 8.8 4.8-2.1-.8-4.4-1.2-6.8-1.2-4.6 0-8.8 1.6-12 3.9Z" fill="#2dd4bf"/>
  <path d="M24.5 13c4.6 0 8.6 1.2 12.6 3.4" stroke="#2dd4bf" stroke-width="1.8" stroke-linecap="round" fill="none"/>
</svg>"""

HERO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 760" preserveAspectRatio="xMidYMid slice">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#061524"/>
      <stop offset="45%" stop-color="#0a2c49"/>
      <stop offset="100%" stop-color="#0d3f66"/>
    </linearGradient>
    <radialGradient id="sun" cx="72%" cy="22%" r="42%">
      <stop offset="0%" stop-color="#2dd4bf" stop-opacity=".30"/>
      <stop offset="100%" stop-color="#2dd4bf" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="w1" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0a2c49"/><stop offset="100%" stop-color="#061a2c"/>
    </linearGradient>
    <linearGradient id="w2" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0d3f66"/><stop offset="100%" stop-color="#0a2c49"/>
    </linearGradient>
    <linearGradient id="w3" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#12557f"/><stop offset="100%" stop-color="#0d3f66"/>
    </linearGradient>
  </defs>
  <rect width="1440" height="760" fill="url(#sky)"/>
  <rect width="1440" height="760" fill="url(#sun)"/>
  <g fill="#8fd8e8" opacity=".28">
    <circle cx="180" cy="150" r="3"/><circle cx="320" cy="90" r="2"/><circle cx="1180" cy="120" r="2.5"/>
    <circle cx="1290" cy="220" r="2"/><circle cx="980" cy="70" r="3"/><circle cx="90" cy="260" r="2"/>
    <circle cx="560" cy="140" r="2"/><circle cx="760" cy="60" r="2.5"/><circle cx="1360" cy="80" r="3"/>
  </g>
  <!-- distant whale silhouettes -->
  <g fill="#0a2c49" opacity=".85">
    <path d="M980 300c0-16 13-29 29-29 9 0 17 4 22 11 6-7 14-11 22-11 17 0 30 13 30 29 0 7-6 13-13 13h-77c-7 0-13-6-13-13Z"/>
    <path d="M980 300l-15-18 7 18-7 18Z"/>
  </g>
  <g fill="#0d3f66" opacity=".8">
    <path d="M1190 372c0-13 11-24 24-24 7 0 14 3 18 9 5-6 11-9 18-9 14 0 25 11 25 24 0 6-5 11-11 11h-63c-6 0-11-5-11-11Z"/>
    <path d="M1190 372l-13-15 6 15-6 15Z"/>
  </g>
  <!-- ocean -->
  <path d="M0 430c160-34 300 22 460 4s280-52 440-30 280 56 540 26v330H0Z" fill="url(#w3)"/>
  <path d="M0 520c180-40 320 24 500 6s300-56 470-30 290 60 470 24v240H0Z" fill="url(#w2)"/>
  <path d="M0 620c200-44 340 26 540 8s320-58 500-28 280 62 400 30v130H0Z" fill="url(#w1)"/>
  <g stroke="#2dd4bf" stroke-opacity=".16" fill="none" stroke-width="1.4">
    <path d="M120 452c40-16 80-16 120 0M700 470c50-18 100-18 150 0M1100 500c46-16 92-16 138 0"/>
    <path d="M300 600c60-18 120-18 180 0M860 630c54-18 108-18 162 0"/>
  </g>
</svg>"""

# ------------------------------------------------------------------ chrome
def head(title, desc, extra=""):
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__ | Whale &amp; Dolphin Conservation</title>
<meta name="description" content="__DESC__">
<link rel="icon" href="assets/logo.svg" type="image/svg+xml">
<link rel="stylesheet" href="css/style.css?__V__">
__EXTRA__
</head>
<body>
<header class="site-header">
  <div class="container">
    <a class="brand" href="index.html">
      <span class="brand__mark">__LOGO__</span>
      <span class="brand__name">WhaleAI Conservation<small>Marine Intelligence Platform</small></span>
    </a>
    <button class="nav__toggle" aria-label="Toggle navigation" aria-expanded="false"><span></span><span></span><span></span></button>
    <nav class="nav" id="primary-nav">
      <a href="index.html">Home</a>
      <a href="about.html">About</a>
      <a href="species.html">Species</a>
      <a href="conservation.html">Conservation</a>
      <div class="nav__drop">
        <button class="nav__dropbtn">Research <span class="nav__caret">&#9662;</span></button>
        <div class="nav__menu">
          <a href="research.html">Research &amp; Insights</a>
          <a href="gis.html">GIS Marine Explorer</a>
          <a href="ai.html">AI Conservation</a>
        </div>
      </div>
      <a href="about.html#contact">Contact</a>
      <a href="dashboard.html" class="btn btn--primary btn--sm nav__cta">Get Started</a>
    </nav>
  </div>
</header>
<main>
""".replace("__TITLE__", title).replace("__DESC__", desc).replace("__LOGO__", LOGO).replace("__EXTRA__", extra).replace("__V__", VERSION)


FOOTER = """</main>
<footer class="site-footer">
  <div class="container">
    <div class="cols">
      <div>
        <div class="brand">
          <span class="brand__mark">__LOGO__</span>
          <span class="brand__name">WhaleAI Conservation<small>Marine Intelligence Platform</small></span>
        </div>
        <p>An open marine conservation platform that turns underwater sound, ocean observation and vessel traffic into decisions that protect whales and dolphins.</p>
        <div class="socials mt-2">
          <a href="https://github.com/DeepakSagar00/whale-dolphin-conservation" title="GitHub" aria-label="GitHub">GH</a>
          <a href="mailto:research@whaleai.org" title="Email" aria-label="Email">@</a>
          <a href="research.html" title="Research" aria-label="Research">R</a>
        </div>
      </div>
      <div>
        <h4>About</h4>
        <a href="about.html">About the Platform</a>
        <a href="about.html#mission">Mission &amp; Vision</a>
        <a href="about.html#technology">Technology</a>
        <a href="about.html#team">Team</a>
      </div>
      <div>
        <h4>Contact</h4>
        <a href="about.html#contact">Contact form</a>
        <a href="mailto:research@whaleai.org">research@whaleai.org</a>
        <a href="about.html#contact">Research enquiries</a>
        <a href="about.html#contact">Data contributions</a>
      </div>
      <div>
        <h4>Research</h4>
        <a href="research.html">Research &amp; Insights</a>
        <a href="gis.html">GIS Marine Explorer</a>
        <a href="ai.html">AI Conservation</a>
        <a href="species.html">Species Explorer</a>
        <a href="privacy.html">Privacy Policy</a>
      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; <span data-year>2026</span> WhaleAI Conservation &middot; Capstone ASAC-CP-141</span>
      <span>Sighting records sourced from the Ocean Biodiversity Information System (OBIS)</span>
    </div>
  </div>
</footer>
<script src="js/data.js?__V__"></script>
<script src="js/main.js?__V__"></script>
__EXTRA_JS__
</body>
</html>
""".replace("__LOGO__", LOGO).replace("__V__", VERSION)


def page_hero(crumbs, title, text):
    c = "".join(
        ('<a href="%s">%s</a>' % (href, label)) if href else ("<span>%s</span>" % label)
        for label, href in crumbs
    )
    return """<section class="page-hero">
  <div class="container">
    <nav class="breadcrumbs">__CRUMBS__</nav>
    <h1>__H1__</h1>
    <p>__TEXT__</p>
  </div>
</section>
""".replace("__CRUMBS__", c).replace("__H1__", title).replace("__TEXT__", text)


def write(name, html):
    path = os.path.join(ROOT, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", name, len(html), "chars")


def page(title, desc, body, extra="", extra_js=""):
    extra_js = extra_js.replace('.js"', '.js?' + VERSION + '"')
    html = head(title, desc, extra) + body + FOOTER.replace("__EXTRA_JS__", extra_js)
    return html


# ================================================================== HOME
FEATURED = [
    ("blue-whale", "Blue Whale"),
    ("humpback-whale", "Humpback Whale"),
    ("bottlenose-dolphin", "Bottlenose Dolphin"),
    ("spinner-dolphin", "Spinner Dolphin"),
]
SHORT = {
    "blue-whale": "The largest animal ever to have lived, protected across every ocean basin.",
    "humpback-whale": "A migrating baleen whale whose songs travel thousands of kilometres underwater.",
    "bottlenose-dolphin": "An intelligent coastal dolphin that regularly approaches vessels and shorelines.",
    "spinner-dolphin": "A highly social pelagic dolphin tracked across tropical ocean basins.",
}

cards = ""
for sid, name in FEATURED:
    cards += """      <article class="card species-card reveal">
        <div class="species-card__media"><img src="assets/species/%s.svg" alt="%s illustration"></div>
        <div class="species-card__body">
          <h3>%s</h3>
          <p class="species-card__latin">%s</p>
          <p>%s</p>
          <a class="species-card__link" href="species-detail.html?id=%s">View species &#8594;</a>
        </div>
      </article>
""" % (sid, name, name,
       {"blue-whale": "Balaenoptera musculus", "humpback-whale": "Megaptera novaeangliae",
        "bottlenose-dolphin": "Tursiops truncatus", "spinner-dolphin": "Stenella longirostris"}[sid],
       SHORT[sid], sid)

home_body = """<section class="hero">
  <div class="hero__bg">__HERO__</div>
  <div class="container hero__inner">
    <span class="hero__badge">&#9679; Live marine intelligence platform</span>
    <h1>Protecting Marine Life Through <em>Intelligence</em> and Innovation.</h1>
    <p>We listen to the ocean, identify the animals making the sound, forecast where they will be,
       and warn the vessels that put them at risk &mdash; before a collision happens.</p>
    <div class="hero__actions">
      <a class="btn btn--primary" href="species.html">Explore Marine Life</a>
      <a class="btn btn--ghost" href="about.html">Explore Platform</a>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="grid grid--3">
      <div class="reveal">
        <span class="eyebrow">Artificial intelligence</span>
        <h3>Listen, then recognise</h3>
        <p class="mt-2 muted">A trained classifier reads log-mel spectrograms of underwater recordings
           and identifies the calling species in the browser &mdash; in seconds, with no uploads to a server.</p>
        <a class="btn btn--outline btn--sm mt-3" href="ai.html">Open AI Conservation</a>
      </div>
      <div class="reveal">
        <span class="eyebrow">Geospatial intelligence</span>
        <h3>See the ocean in context</h3>
        <p class="mt-2 muted">An interactive GIS explorer plots real sighting records from OBIS,
           filtered by species, region and time so researchers can interrogate distribution directly.</p>
        <a class="btn btn--outline btn--sm mt-3" href="gis.html">Open GIS Explorer</a>
      </div>
      <div class="reveal">
        <span class="eyebrow">Data-driven decisions</span>
        <h3>Turn records into action</h3>
        <p class="mt-2 muted">Detection histories feed forecasting and risk models that estimate
           where animals and shipping traffic are likely to meet &mdash; and how much slowing down would help.</p>
        <a class="btn btn--outline btn--sm mt-3" href="research.html">See the research</a>
      </div>
    </div>
  </div>
</section>

<section class="section section--white">
  <div class="container">
    <div class="section-head reveal">
      <span class="eyebrow">Featured species</span>
      <h2>Marine life we monitor and protect</h2>
      <p>A working directory of the whale and dolphin species covered by the platform,
         with their habitat, distribution and conservation status.</p>
    </div>
    <div class="grid grid--4">
__CARDS__
    </div>
    <div class="mt-4">
      <a class="btn btn--ocean" href="species.html">View All Species</a>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="grid grid--2" style="align-items:center;gap:48px">
      <div class="reveal">
        <span class="eyebrow">Conservation initiatives</span>
        <h2>From detection to protection</h2>
        <p class="lead mt-2">Conservation only works if it is measurable. The platform supports four
           standing initiatives that turn monitoring into protection.</p>
        <ul class="mt-3 muted" style="padding-left:20px">
          <li style="margin-bottom:10px"><strong style="color:var(--ink-900)">Speed zones</strong> &mdash; model where a 10-knot limit would remove the most lethal strike risk.</li>
          <li style="margin-bottom:10px"><strong style="color:var(--ink-900)">Noise monitoring</strong> &mdash; identify shipping corridors where engines mask animal calls.</li>
          <li style="margin-bottom:10px"><strong style="color:var(--ink-900)">Protected area review</strong> &mdash; find high-use cells that fall outside current protection.</li>
          <li style="margin-bottom:10px"><strong style="color:var(--ink-900)">Effort-based reporting</strong> &mdash; publish observations and models openly for other programmes to reuse.</li>
        </ul>
        <a class="btn btn--outline mt-3" href="conservation.html">Read about our approach</a>
      </div>
      <div class="grid reveal" style="gap:16px">
        <div class="card"><div class="card__body">
          <h3>Ship-strike risk</h3>
          <p>Risk is computed per cell as the probability of whale presence multiplied by ship exposure
             and the lethality of the prevailing speed.</p>
        </div></div>
        <div class="card"><div class="card__body">
          <h3>Bycatch exposure</h3>
          <p>Detection density is combined with fishing intensity and noise proxies to flag
             coastal cells where entanglement risk is highest.</p>
        </div></div>
        <div class="card"><div class="card__body">
          <h3>Habitat protection</h3>
          <p>Suitability modelling identifies habitat that species rely on but that current
             protected-area networks leave exposed.</p>
        </div></div>
      </div>
    </div>
  </div>
</section>
""".replace("__HERO__", HERO_SVG).replace("__CARDS__", cards)

write("index.html", page(
    "Protecting Marine Life Through Intelligence and Innovation",
    "An open marine conservation platform combining underwater acoustics, geospatial analysis and risk modelling to protect whales and dolphins.",
    home_body))

# ================================================================== SPECIES
species_body = page_hero(
    [("Home", "index.html"), ("Species Explorer", None)],
    "Species Explorer",
    "A working directory of the whale and dolphin species covered by the platform. Search by name, "
    "filter by group or conservation status, and open a species record for its habitat, distribution "
    "and threats.") + """
<section class="section">
  <div class="container">
    <div class="toolbar">
      <input type="search" id="sp-search" placeholder="Search by name or scientific name&hellip;" aria-label="Search species">
      <select id="sp-type" aria-label="Filter by group">
        <option value="">All groups</option>
        <option value="Whale">Whales</option>
        <option value="Dolphin">Dolphins</option>
      </select>
      <select id="sp-status" aria-label="Filter by conservation status">
        <option value="">All statuses</option>
        <option value="EN">Endangered</option>
        <option value="VU">Vulnerable</option>
        <option value="LC">Least Concern</option>
        <option value="DD">Data Deficient</option>
      </select>
      <span class="count" id="sp-count"></span>
    </div>
    <div class="grid grid--3" id="sp-grid"></div>
    <p class="muted mt-3" id="sp-empty" style="display:none">No species match those filters. Try clearing the search field.</p>
  </div>
</section>
"""
write("species.html", page(
    "Species Explorer",
    "Directory of whale and dolphin species with scientific names, habitat, distribution and IUCN conservation status.",
    species_body,
    extra_js='<script src="js/species.js"></script>'))

# ================================================================== SPECIES DETAIL
detail_body = """
<section class="section">
  <div class="container">
    <div id="spd-root"><p class="muted">Loading species record&hellip;</p></div>
  </div>
</section>
"""
write("species-detail.html", page(
    "Species Record",
    "Habitat, distribution, conservation status and threats for a monitored whale or dolphin species.",
    detail_body,
    extra_js='<script src="js/species-detail.js"></script>'))

# ================================================================== CONSERVATION
cons_body = page_hero(
    [("Home", "index.html"), ("Conservation", None)],
    "Conservation",
    "Whale and dolphin populations face compounding pressures. This page sets out the threats, "
    "the strategies that address them, and the protection initiatives the platform supports.") + """
<section class="section">
  <div class="container">
    <div class="section-head reveal">
      <span class="eyebrow">Threats</span>
      <h2>What puts marine life at risk</h2>
    </div>
    <div class="threat">
      <div class="card reveal"><div class="card__body">
        <h3><span class="ico">&#9875;</span> Ship strikes</h3>
        <p class="mt-2">Vessel traffic overlaps migratory routes and feeding grounds. Strikes remain a
           leading cause of mortality for several large whale species, with risk concentrated in a
           small number of high-traffic cells.</p>
      </div></div>
      <div class="card reveal"><div class="card__body">
        <h3><span class="ico">&#129361;</span> Entanglement &amp; bycatch</h3>
        <p class="mt-2">Drifting nets, lines and traps entangle whales and dolphins. For dolphin
           populations, interaction with coastal fisheries is a persistent source of mortality.</p>
      </div></div>
      <div class="card reveal"><div class="card__body">
        <h3><span class="ico">&#9836;</span> Ocean noise</h3>
        <p class="mt-2">Engine noise and low-frequency shipping tones mask the calls animals use to
           communicate, raising energy demands and disrupting feeding and social behaviour.</p>
      </div></div>
      <div class="card reveal"><div class="card__body">
        <h3><span class="ico">&#9851;</span> Plastic &amp; chemical pollution</h3>
        <p class="mt-2">Plastic debris and chemical contaminants enter the food chain, and marine
           mammals accumulate pollutants to levels that affect health and reproduction.</p>
      </div></div>
      <div class="card reveal"><div class="card__body">
        <h3><span class="ico">&#127760;</span> Climate change</h3>
        <p class="mt-2">Warming seas shift the distribution of prey and push species poleward, while
           changing prey abundance and habitat quality at the range edges.</p>
      </div></div>
      <div class="card reveal"><div class="card__body">
        <h3><span class="ico">&#127760;</span> Habitat loss</h3>
        <p class="mt-2">Coastal development, dredging and altered prey distributions degrade the
           shallow-water habitat that dolphins depend on for feeding and resting.</p>
      </div></div>
    </div>
  </div>
</section>

<section class="section section--white">
  <div class="container">
    <div class="section-head reveal">
      <span class="eyebrow">Strategies</span>
      <h2>How conservation responds</h2>
    </div>
    <div class="grid grid--3">
      <div class="card reveal"><div class="card__body">
        <h3>Dynamic speed management</h3>
        <p class="mt-2">Rather than fixed closures, speed restrictions are placed where the model
           shows whales and fast-moving vessels will overlap &mdash; and are relaxed where risk is low.</p>
      </div></div>
      <div class="card reveal"><div class="card__body">
        <h3>Seasonal protection windows</h3>
        <p class="mt-2">Forecast models identify the weeks each species is most likely present, so
           protections can follow the migration instead of the calendar.</p>
      </div></div>
      <div class="card reveal"><div class="card__body">
        <h3>Protected area review</h3>
        <p class="mt-2">Cells with high habitat suitability and recorded presence but no current
           protection are surfaced as candidates for designation or extension.</p>
      </div></div>
      <div class="card reveal"><div class="card__body">
        <h3>Quiet zones &amp; noise reduction</h3>
        <p class="mt-2">Shipping corridors overlapping important habitat are candidates for engine
           restrictions, slow steaming and targeted noise monitoring.</p>
      </div></div>
      <div class="card reveal"><div class="card__body">
        <h3>Fishery mitigation</h3>
        <p class="mt-2">Where fishing effort overlaps predicted habitat, seasonal gear restrictions
           and bycatch mitigation measures are advised for that cell.</p>
      </div></div>
      <div class="card reveal"><div class="card__body">
        <h3>Open monitoring &amp; reporting</h3>
        <p class="mt-2">Observation records, models and advisory outputs are published openly so that
           other agencies can verify, reuse and extend the results.</p>
      </div></div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head reveal">
      <span class="eyebrow">Priority species</span>
      <h2>Species under greatest pressure</h2>
      <p>Conservation status reflects the IUCN Red List assessment recorded for each species.</p>
    </div>
    <div class="grid grid--3" id="cons-species"></div>
  </div>
</section>
"""
write("conservation.html", page(
    "Conservation",
    "Threats facing whales and dolphins, the conservation strategies that address them, and protection initiatives.",
    cons_body,
    extra_js='<script src="js/conservation.js"></script>'))

# ================================================================== RESEARCH
research_body = page_hero(
    [("Home", "index.html"), ("Research", None), ("Research &amp; Insights", None)],
    "Research &amp; Insights",
    "The datasets, methods and findings behind the platform &mdash; what the data contains, how the "
    "models are built, and what the results show.") + """
<section class="section">
  <div class="container">
    <div class="section-head reveal">
      <span class="eyebrow">Datasets</span>
      <h2>Data the platform is built on</h2>
      <p>Every number on this site is derived from these sources or from the models trained on them.</p>
    </div>
    <div class="grid grid--3" id="res-datasets"></div>
  </div>
</section>

<section class="section section--white">
  <div class="container">
    <div class="section-head reveal">
      <span class="eyebrow">Methodology</span>
      <h2>How the models work</h2>
    </div>
    <div class="grid grid--2">
      <div class="reveal">
        <h3>Species identification from sound</h3>
        <p class="muted mt-2">Recordings are converted to 5-second windows and then to log-mel
           spectrograms. A convolutional classifier is trained on these arrays to separate the calls
           of each species, and is stress-tested by mixing ship noise back into the training audio
           at signal-to-noise ratios from 20 dB down to 0 dB.</p>
        <p class="muted mt-2">Grad-CAM is used to confirm the network is attending to the call
           structure itself rather than to artefacts of the background noise.</p>
      </div>
      <div class="reveal">
        <h3>Forecast and risk</h3>
        <p class="muted mt-2">Daily detection records are turned into rolling rate features over 7,
           14 and 30 days, combined with seasonal and day-of-year terms. Gradient boosting is then
           trained to predict whether a species will be present in the following seven days.</p>
        <p class="muted mt-2">Ship-strike risk combines that forecast with vessel traffic derived
           from AIS positions and a logistic lethality curve relating speed to collision probability,
           which also enables the 10-knot what-if scenario.</p>
      </div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head reveal">
      <span class="eyebrow">Findings</span>
      <h2>Observations and results</h2>
    </div>
    <div class="grid grid--3" id="res-findings"></div>
  </div>
</section>

<section class="section section--white">
  <div class="container">
    <div class="section-head reveal">
      <span class="eyebrow">Resources</span>
      <h2>Publications and downloadable material</h2>
    </div>
    <div class="pub-list" id="res-pubs"></div>
    <div class="grid grid--3 mt-4" id="res-downloads"></div>
  </div>
</section>
"""
write("research.html", page(
    "Research & Insights",
    "Marine conservation research: datasets, model methodology, findings, publications and downloadable resources.",
    research_body,
    extra_js='<script src="js/research.js"></script>'))

# ================================================================== GIS
gis_body = page_hero(
    [("Home", "index.html"), ("Research", None), ("GIS Marine Explorer", None)],
    "GIS Marine Explorer",
    "An interactive map of marine species occurrence. Filter by species, region and date to "
    "explore where whales and dolphins have been recorded.") + """
<section class="section section--tight">
  <div class="container">
    <div class="grid" style="grid-template-columns:300px 1fr;gap:22px;align-items:start">
      <aside class="layer-panel">
        <h3>Filters</h3>
        <div class="field">
          <label for="gis-species">Species</label>
          <select id="gis-species">
            <option value="">All recorded species</option>
          </select>
        </div>
        <div class="field">
          <label for="gis-region">Region</label>
          <select id="gis-region">
            <option value="">All regions</option>
            <option value="Indian Ocean">Indian Ocean</option>
            <option value="Arabian Sea">Arabian Sea</option>
            <option value="Bay of Bengal">Bay of Bengal</option>
            <option value="Southern Ocean">Southern Ocean</option>
            <option value="Atlantic">Atlantic</option>
            <option value="Pacific">Pacific</option>
          </select>
        </div>
        <div class="field">
          <label for="gis-from">From year</label>
          <select id="gis-from"><option value="">Any</option></select>
        </div>
        <div class="field">
          <label for="gis-to">To year</label>
          <select id="gis-to"><option value="">Any</option></select>
        </div>
        <button class="btn btn--outline btn--sm" id="gis-reset" type="button">Reset filters</button>
        <h3 class="mt-4">Layers</h3>
        <label class="layer-option"><input type="checkbox" id="lyr-humpback" checked> Humpback whale</label>
        <label class="layer-option"><input type="checkbox" id="lyr-spinner" checked> Spinner dolphin</label>
        <label class="layer-option"><input type="checkbox" id="lyr-heat"> Sightings density</label>
        <p class="muted mt-3" style="font-size:.84rem" id="gis-count"></p>
      </aside>
      <div>
        <div class="map-wrap">
          <div id="map"></div>
          <div class="map-legend">
            <h4>Legend</h4>
            <div><i style="background:#1b6ca8"></i> Humpback whale</div>
            <div><i style="background:#17a2b8"></i> Spinner dolphin</div>
            <div><i style="background:#c0392b"></i> Selected record</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section section--tight section--white">
  <div class="container">
    <div class="section-head reveal">
      <span class="eyebrow">Records</span>
      <h2>Matching sighting records</h2>
      <p>Click a marker on the map or a row below to inspect the record.</p>
    </div>
    <div class="panel">
      <div class="table-wrap">
        <table>
          <thead><tr><th>Species</th><th>Latitude</th><th>Longitude</th><th>Date</th><th>Individuals</th></tr></thead>
          <tbody id="gis-table"></tbody>
        </table>
      </div>
    </div>
  </div>
</section>
"""
write("gis.html", page(
    "GIS Marine Explorer",
    "Interactive map of whale and dolphin sighting records from OBIS, with species, region and date filtering.",
    gis_body,
    extra='<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">',
    extra_js='<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>\n<script src="js/gis.js"></script>'))

# ================================================================== AI
ai_body = page_hero(
    [("Home", "index.html"), ("Research", None), ("AI Conservation", None)],
    "AI Conservation",
    "Upload an underwater recording and the species classifier will identify the caller. "
    "The model runs entirely in your browser.") + """
<section class="section">
  <div class="container">
    <div class="ai-layout">
      <div>
        <div class="panel">
          <h3>Species identification</h3>
          <p class="sub">Logistic regression over 64 frequency-band features of a 5-second window, trained on six classes.</p>
          <label class="dropzone" id="ai-drop" for="ai-file">
            <div class="dropzone__ico">&#9835;</div>
            <b>Drop an audio file or click to browse</b>
            <span>WAV, MP3, FLAC or OGG &mdash; processed locally, never uploaded</span>
          </label>
          <input type="file" id="ai-file" accept="audio/*" hidden>
          <div class="sample-row">
            <button class="btn btn--outline btn--sm" data-sample="blue_whale" type="button">Blue whale</button>
            <button class="btn btn--outline btn--sm" data-sample="fin_whale" type="button">Fin whale</button>
            <button class="btn btn--outline btn--sm" data-sample="humpback_whale" type="button">Humpback</button>
            <button class="btn btn--outline btn--sm" data-sample="killer_whale" type="button">Killer whale</button>
            <button class="btn btn--outline btn--sm" data-sample="bottlenose_dolphin" type="button">Dolphin</button>
            <button class="btn btn--outline btn--sm" data-sample="background" type="button">Ship noise</button>
          </div>

          <div class="result mt-4" id="ai-result">
            <div class="eyebrow" style="margin-bottom:14px">Classification result</div>
            <div id="ai-bars"></div>
            <div class="verdict" id="ai-verdict"></div>
            <div id="ai-species" class="mt-3"></div>
          </div>
        </div>
      </div>
      <div>
        <div class="ai-info mb-3">
          <h3>What this model does</h3>
          <p>The classifier is a real trained model, not a mock-up. It reproduces the same feature
             extraction used during training and outputs calibrated probabilities for each of the
             six recorded classes.</p>
          <ul>
            <li>Audio is decoded and resampled to 16 kHz in the browser.</li>
            <li>A 5-second window is transformed into a log-mel spectrogram.</li>
            <li>64 frequency bands are summarised by mean and standard deviation.</li>
            <li>Standardised features are scored against the trained coefficients.</li>
          </ul>
        </div>
        <div class="ai-info">
          <h3>Classes covered</h3>
          <p id="ai-classes" class="muted"></p>
        </div>
        <div class="ai-info mt-3">
          <h3>Using your own recordings</h3>
          <p>Real Watkins, NOAA SanctSound and hydrophone recordings can be dropped straight in.
             Results are only meaningful for audio that contains an animal call within the first
             five seconds.</p>
        </div>
      </div>
    </div>
  </div>
</section>
"""
write("ai.html", page(
    "AI Conservation",
    "Identify whale and dolphin species from underwater recordings with a browser-based audio classifier.",
    ai_body,
    extra_js='<script src="js/ai.js"></script>'))

# ================================================================== DASHBOARD
dash_body = page_hero(
    [("Home", "index.html"), ("Researcher Dashboard", None)],
    "Researcher Dashboard",
    "Analytics for marine species statistics, sighting records, distribution insights and "
    "conservation status summaries.") + """
<section class="section section--tight">
  <div class="container">
    <div id="dash-gate">
      <div class="login-card">
        <h2>Researcher access</h2>
        <p>Sign in to open the analytics dashboard. This is a demonstration build &mdash; credentials are checked in the browser.</p>
        <form id="dash-login" novalidate>
          <div class="field">
            <label for="dl-email">Email</label>
            <input type="email" id="dl-email" value="researcher@whaleai.org" required>
          </div>
          <div class="field">
            <label for="dl-pass">Access code</label>
            <input type="password" id="dl-pass" value="whale2026" required>
          </div>
          <button class="btn btn--primary" type="submit" style="width:100%">Open dashboard</button>
          <p class="form-error" id="dl-error">Those credentials were not recognised. Try the demo values shown above.</p>
          <p class="form-note">Demonstration credentials are pre-filled for review purposes.</p>
        </form>
      </div>
    </div>

    <div id="dash-app" class="hidden">
      <div class="stat-grid" id="dash-stats"></div>

      <div class="grid grid--2">
        <div class="panel">
          <h3>Records by year</h3>
          <p class="sub">Sighting records in the explorer dataset, grouped by year of observation.</p>
          <div class="chart-box"><canvas id="chart-years"></canvas></div>
        </div>
        <div class="panel">
          <h3>Conservation status</h3>
          <p class="sub">IUCN Red List category for each species in the directory.</p>
          <div class="chart-box"><canvas id="chart-status"></canvas></div>
        </div>
      </div>

      <div class="grid grid--2">
        <div class="panel">
          <h3>Risk model performance</h3>
          <p class="sub">Metrics from the trained grid risk classifier (backend/ml/ml_metrics.json).</p>
          <div class="chart-box"><canvas id="chart-features"></canvas></div>
        </div>
        <div class="panel">
          <h3>Risk classes across the study grid</h3>
          <p class="sub">Distribution of conservation risk across 12,856 modelled grid cells.</p>
          <div class="chart-box"><canvas id="chart-risk"></canvas></div>
        </div>
      </div>

      <div class="panel">
        <h3>Distribution insights</h3>
        <p class="sub">Geographic spread of the species records held in the explorer dataset.</p>
        <div class="chart-box" style="height:340px"><canvas id="chart-region"></canvas></div>
      </div>

      <div class="panel">
        <h3>Sighting records</h3>
        <p class="sub">Most recent records in the dataset.</p>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Species</th><th>Latitude</th><th>Longitude</th><th>Date</th><th>Individuals</th></tr></thead>
            <tbody id="dash-table"></tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</section>
"""
write("dashboard.html", page(
    "Researcher Dashboard",
    "Analytics dashboard for marine species statistics, sighting records, distribution insights and conservation status.",
    dash_body,
    extra='<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>',
    extra_js='<script src="js/dashboard.js"></script>'))

# ================================================================== ABOUT
about_body = page_hero(
    [("Home", "index.html"), ("About", None)],
    "About the Platform",
    "WhaleAI Conservation is a capstone-built marine conservation platform that combines acoustics, "
    "geospatial analysis and operational risk modelling into one working system.") + """
<section class="section" id="mission">
  <div class="container">
    <div class="about-grid">
      <div class="reveal">
        <span class="eyebrow">Mission &amp; vision</span>
        <h2>Make marine protection measurable</h2>
        <p class="lead mt-2">Every conservation decision is made with incomplete information. The
           platform's purpose is to close that gap: to listen to the ocean continuously, understand
           which animals are present and where, and translate that into advice a vessel captain can
           act on the same day.</p>
        <p class="muted mt-2">The vision is a shared, open evidence base. Detection records, models
           and risk outputs are published so that regulators, researchers and conservation
           organisations are not each rebuilding the same baseline.</p>
      </div>
      <div class="reveal">
        <div class="card"><div class="card__body">
          <span class="eyebrow">Vision</span>
          <h3>From detection to decision</h3>
          <p class="mt-2">A single platform that turns passive acoustic monitoring into specific,
             spatially explicit recommendations &mdash; and makes the reasoning behind each
             recommendation inspectable.</p>
        </div></div>
        <div class="card mt-3"><div class="card__body">
          <span class="eyebrow">Approach</span>
          <h3>Open by default</h3>
          <p class="mt-2">Models, datasets and advisory outputs are published openly so results can be
             verified and reused rather than re-derived.</p>
        </div></div>
      </div>
    </div>
  </div>
</section>

<section class="section section--white" id="technology">
  <div class="container">
    <div class="section-head reveal">
      <span class="eyebrow">Technology</span>
      <h2>What the platform is built with</h2>
    </div>
    <div class="grid grid--4">
      <div class="card reveal"><div class="card__body">
        <h3>Acoustic analysis</h3>
        <p class="mt-2">Log-mel spectrograms, 5-second windowing and noise-robustness testing against
           mixed ship noise at 0&ndash;20 dB SNR.</p>
      </div></div>
      <div class="card reveal"><div class="card__body">
        <h3>Machine learning</h3>
        <p class="mt-2">PyTorch and scikit-learn for classification, gradient boosting for presence
           forecasting, and explainability through Grad-CAM.</p>
      </div></div>
      <div class="card reveal"><div class="card__body">
        <h3>Geospatial analysis</h3>
        <p class="mt-2">OBIS occurrence records, H3 hexagonal grid indexing, haversine distance and
           AIS vessel tracks for traffic exposure.</p>
      </div></div>
      <div class="card reveal"><div class="card__body">
        <h3>Experiment tracking</h3>
        <p class="mt-2">MLflow-compatible run tracking, so every model, metric and parameter stays
           reproducible and comparable.</p>
      </div></div>
    </div>
  </div>
</section>

<section class="section" id="team">
  <div class="container">
    <div class="section-head section-head--center reveal">
      <span class="eyebrow">Team</span>
      <h2>Built by the project team</h2>
      <p>A cross-functional group covering acoustics, geospatial science and machine learning.</p>
    </div>
    <div class="team-grid">
      <div class="card team-member reveal">
        <div class="avatar">DS</div>
        <h4>Deepak Sagar</h4>
        <span>Data science &amp; machine learning</span>
      </div>
      <div class="card team-member reveal">
        <div class="avatar">MR</div>
        <h4>Marine Acoustics</h4>
        <span>Passive acoustic monitoring</span>
      </div>
      <div class="card team-member reveal">
        <div class="avatar">GW</div>
        <h4>GIS &amp; Risk</h4>
        <span>Geospatial analysis &amp; vessel traffic</span>
      </div>
    </div>
  </div>
</section>

<section class="section section--white" id="contact">
  <div class="container">
    <div class="about-grid">
      <div class="reveal">
        <span class="eyebrow">Contact</span>
        <h2>Get in touch</h2>
        <p class="muted mt-2">Research collaborations, data contributions, deployment enquiries or
           corrections to a species record are all welcome.</p>
        <dl class="fact-list mt-4">
          <div><dt>General enquiries</dt><dd>research@whaleai.org</dd></div>
          <div><dt>Data contributions</dt><dd>research@whaleai.org</dd></div>
          <div><dt>Source repository</dt><dd>github.com/DeepakSagar00</dd></div>
          <div><dt>Occurrence data</dt><dd>OBIS &mdash; Ocean Biodiversity Information System</dd></div>
        </dl>
      </div>
      <div class="reveal">
        <div class="panel" style="margin:0">
          <h3>Send a message</h3>
          <p class="sub">Fields marked with an asterisk are required.</p>
          <form id="contact-form" novalidate>
            <div class="field">
              <label for="cf-name">Name *</label>
              <input type="text" id="cf-name" required>
            </div>
            <div class="field">
              <label for="cf-email">Email *</label>
              <input type="email" id="cf-email" required>
            </div>
            <div class="field">
              <label for="cf-topic">Topic</label>
              <select id="cf-topic">
                <option>Research collaboration</option>
                <option>Data contribution</option>
                <option>Deployment enquiry</option>
                <option>Correction to a record</option>
                <option>General</option>
              </select>
            </div>
            <div class="field">
              <label for="cf-msg">Message *</label>
              <textarea id="cf-msg" rows="5" required></textarea>
            </div>
            <button class="btn btn--primary" type="submit">Send message</button>
            <p class="form-error" id="cf-error">Please complete the required fields.</p>
            <p class="form-note" id="cf-note" style="display:none;color:var(--green)">
              Thank you &mdash; your message has been recorded locally for this demonstration build.
              A maintainer will follow up at the address you provided.
            </p>
          </form>
        </div>
      </div>
    </div>
  </div>
</section>
"""
write("about.html", page(
    "About",
    "Mission, vision, technology and team behind the WhaleAI marine conservation platform.",
    about_body,
    extra_js='<script src="js/contact.js"></script>'))

# ================================================================== PRIVACY
privacy_body = page_hero(
    [("Home", "index.html"), ("Privacy Policy", None)],
    "Privacy Policy",
    "How this demonstration platform handles the information you provide.") + """
<section class="section">
  <div class="container" style="max-width:820px">
    <div class="panel">
      <h3>Summary</h3>
      <p class="muted mt-2">This is a demonstration build of a marine conservation research platform.
         It is designed so that sensitive data never has to leave your device.</p>

      <h3 class="mt-4">Audio recordings</h3>
      <p class="muted mt-2">Audio files you select for classification are decoded, resampled and
         analysed entirely inside your browser using the JavaScript implementation of the model.
         No recording is uploaded, stored or transmitted.</p>

      <h3 class="mt-4">Dashboard access</h3>
      <p class="muted mt-2">The researcher dashboard uses a demonstration sign-in that is validated
         in the browser only. No credentials are transmitted or stored on a server.</p>

      <h3 class="mt-4">Contact form</h3>
      <p class="muted mt-2">Messages submitted through the contact form are handled in the browser
         and are not transmitted to any server in this build. Please do not send sensitive
         information through the form.</p>

      <h3 class="mt-4">Third-party components</h3>
      <p class="muted mt-2">The GIS explorer loads map tiles from the OpenStreetMap tile servers and
         the dashboard loads the Chart.js charting library from a public CDN. These requests disclose
         your IP address and browser user-agent to those providers.</p>

      <h3 class="mt-4">Sighting records</h3>
      <p class="muted mt-2">All occurrence records published on this site are derived from the Ocean
         Biodiversity Information System (OBIS), an open-access repository of marine biodiversity
         data published under its own data-sharing terms.</p>

      <h3 class="mt-4">Contact</h3>
      <p class="muted mt-2">Questions about this policy can be raised through the
         <a href="about.html#contact">contact form</a>.</p>
    </div>
  </div>
</section>
"""
write("privacy.html", page(
    "Privacy Policy",
    "How the WhaleAI marine conservation platform demonstration handles audio, credentials and contact messages.",
    privacy_body))

print("\nAll pages generated.")
