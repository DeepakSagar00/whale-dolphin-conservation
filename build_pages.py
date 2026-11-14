"""Generate the marine-science dashboard site.

Pages share one shell: a fixed top bar, a left navigation rail and a content
column. Every page is generated so the chrome can never drift out of sync.
"""
import hashlib
import os

ROOT = r"C:\Users\Deepak Sagar\OneDrive\Desktop\MoveOne\whale-dolphin-conservation\website"


def _asset_version():
    h = hashlib.md5()
    targets = [os.path.join(ROOT, "css", "style.css")]
    jsdir = os.path.join(ROOT, "js")
    for name in sorted(os.listdir(jsdir)):
        if name.endswith(".js"):
            targets.append(os.path.join(jsdir, name))
    for t in targets:
        try:
            with open(t, "rb") as f:
                h.update(f.read())
        except OSError:
            pass
    return "v" + h.hexdigest()[:8]


VERSION = _asset_version()

LOGO = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" role="img" aria-label="Whale and Dolphin Conservation">
  <path d="M8 30c0-5.4 4.4-9.8 10-9.8 3.3 0 6.2 1.6 8 4.1 1.8-2.5 4.7-4.1 8-4.1 5.6 0 10 4.4 10 9.8 0 2.6-2 4.6-4.6 4.6H12.6A4.6 4.6 0 0 1 8 30Z" fill="#ffffff"/>
  <path d="M8 30 2.5 23.5 5 30l-2.5 6.5Z" fill="#ffffff"/>
  <circle cx="31.5" cy="27.5" r="1.6" fill="#12a8b8"/>
  <path d="M14 20.5c1.6-4.4 5.4-7.5 10-7.5 3.6 0 6.9 1.9 8.8 4.8-2.1-.8-4.4-1.2-6.8-1.2-4.6 0-8.8 1.6-12 3.9Z" fill="#35d6c4"/>
  <path d="M24.5 13c4.6 0 8.6 1.2 12.6 3.4" stroke="#35d6c4" stroke-width="1.8" stroke-linecap="round" fill="none"/>
</svg>"""

# ---- navigation ------------------------------------------------------------
ICON = {
    "overview": '<path d="M3 9.5 12 3l9 6.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1Z"/>',
    "dashboard": '<path d="M4 4h7v7H4zM13 4h7v4h-7zM13 10h7v10h-7zM4 13h7v7H4z"/>',
    "map": '<path d="M9 3 3 5.5v15L9 18l6 3 6-2.5v-15L15 6Zm0 0v15m6-12v15"/>',
    "observe": '<path d="M12 5a7 7 0 1 0 0 14 7 7 0 0 0 0-14Zm0 3a4 4 0 1 1 0 8 4 4 0 0 1 0-8Zm9 9-3.5-3.5"/>',
    "ai": '<path d="M12 2a3 3 0 0 0-3 3v1a3 3 0 0 0-1 5.8V15a3 3 0 0 0 2 2.8V19a2 2 0 0 0 4 0v-1.2a3 3 0 0 0 2-2.8v-3.2A3 3 0 0 0 15 6V5a3 3 0 0 0-3-3ZM9 12h6v3H9z"/>',
    "wave": '<path d="M2 12c2.5-4 5-4 7.5 0S15 16 17.5 12 20 8 22 12"/>',
    "chart": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    "species": '<path d="M12 21c-4 0-7-2.5-7-6 0-4 4-8 9-9 .8 3.5 2.5 4 5 4.5C21 11 20 15 16 18c-1 1.5-2.5 2-4 3Z"/>',
    "research": '<path d="M6 3h9l5 5v13a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Zm9 1.5V9h4.5M8 13h8M8 17h5"/>',
    "shield": '<path d="M12 2 4 5v7c0 5 3.5 8.5 8 10 4.5-1.5 8-5 8-10V5Z"/>',
    "info": '<path d="M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20Zm0-14v.5m0 3.5v6"/>',
    "search": '<path d="M11 4a7 7 0 1 0 0 14 7 7 0 0 0 0-14Zm9 16-4.5-4.5"/>',
    "menu": '<path d="M3 6h18M3 12h18M3 18h18"/>',
}


def icon(name):
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
            'stroke-linecap="round" stroke-linejoin="round">' + ICON[name] + "</svg>")


NAV = [
    ("Platform", [
        ("index.html", "overview", "Overview"),
        ("dashboard.html", "dashboard", "Dashboard"),
    ]),
    ("Observe", [
        ("gis.html", "map", "GIS Marine Map"),
        ("observations.html", "observe", "Observations"),
    ]),
    ("Analyse", [
        ("identify.html", "ai", "AI Identification"),
        ("bioacoustics.html", "wave", "Bioacoustics"),
        ("analytics.html", "chart", "Conservation Analytics"),
    ]),
    ("Reference", [
        ("species.html", "species", "Species Directory"),
        ("research.html", "research", "Research"),
        ("conservation.html", "shield", "Conservation"),
    ]),
    ("About", [
        ("about.html", "info", "About & Contact"),
    ]),
]


def sidebar(active):
    groups = []
    for label, items in NAV:
        links = []
        for href, ico, name in items:
            cls = ' class="active"' if href == active else ""
            links.append('<a href="%s"%s>%s<span>%s</span></a>' % (href, cls, icon(ico), name))
        groups.append('<div class="sidebar__group"><div class="sidebar__label">%s</div>%s</div>'
                      % (label, "".join(links)))
    return """<aside class="sidebar" id="sidebar">
  %s
  <div class="sidebar__foot">
    Capstone ASAC-CP-141<br>
    Whale &amp; Dolphin Conservation Platform
  </div>
</aside>
<div class="sidebar-scrim" id="sidebar-scrim"></div>
""" % "".join(groups)


def topbar(active):
    return """<header class="topbar">
  <button class="nav__toggle sidebar-toggle" id="sidebar-toggle" aria-label="Toggle navigation">%s</button>
  <a class="topbar__brand" href="index.html">
    <span class="topbar__mark">%s</span>
    <span class="topbar__name">WhaleAI&nbsp;Conservation</span>
  </a>
  <span class="topbar__sep"></span>
  <div class="topbar__search">
    %s
    <input type="search" id="global-search" placeholder="Search species, pages and observations&hellip;" aria-label="Search">
  </div>
  <div class="topbar__right">
    <span class="conn" id="conn-status"><i></i><span>checking</span></span>
    <a class="topbar__user" id="user-chip" href="dashboard.html">
      <span class="topbar__avatar" id="user-initial">R</span>
      <span id="user-name">Researcher</span>
    </a>
  </div>
</header>
""" % (icon("menu"), LOGO, icon("search"))


def head(title, desc, extra=""):
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__ &middot; WhaleAI Conservation</title>
<meta name="description" content="__DESC__">
<link rel="icon" href="assets/logo.svg" type="image/svg+xml">
<link rel="stylesheet" href="css/style.css?__V__">
__EXTRA__
</head>
<body>
<div class="app">
__TOPBAR__
__SIDEBAR__
<div class="main">
<main class="content __CONTENTCLASS__">
""".replace("__TITLE__", title).replace("__DESC__", desc).replace("__V__", VERSION) \
   .replace("__EXTRA__", extra).replace("__TOPBAR__", topbar("__ACTIVE__")) \
   .replace("__SIDEBAR__", sidebar("__ACTIVE__")).replace("__ACTIVE__", "") \
   .replace("__CONTENTCLASS__", "")


FOOTER = """</main>
</div>
</div>
<script src="js/data.js?__V__"></script>
<script src="js/main.js?__V__"></script>
__EXTRA_JS__
</body>
</html>
""".replace("__V__", VERSION)


def write(name, html):
    with open(os.path.join(ROOT, name), "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", name, len(html), "chars")


def page(name, title, desc, body, active, extra="", extra_js="", content_class=""):
    h = head(title, desc, extra)
    h = h.replace('__ACTIVE__', active).replace("__CONTENTCLASS__", content_class)
    h = h.replace("__TOPBAR__", topbar(active)).replace("__SIDEBAR__", sidebar(active))
    extra_js = extra_js.replace('.js"', '.js?' + VERSION + '"')
    write(name, h + body + FOOTER.replace("__EXTRA_JS__", extra_js))


def pagehead(crumbs, title, subtitle, actions=""):
    c = "".join(
        ('<a href="%s">%s</a>' % (href, label)) if href else ("<span>%s</span>" % label)
        for label, href in crumbs
    )
    return """<div class="pagehead">
  <div class="pagehead__title">
    <nav class="crumbs">%s</nav>
    <h1>%s</h1>
    <p>%s</p>
  </div>
  %s
</div>
""" % (c, title, subtitle, ('<div class="pagehead__actions">%s</div>' % actions) if actions else "")


# ===================================================================== OVERVIEW
overview_body = """
<section class="hero">
  <h1>Protecting marine life by turning sound and location into action</h1>
  <p>Whale and dolphin populations are declining, and the decisions that protect them are made with
     incomplete information. This platform listens to the ocean, identifies the animals making the
     sound, maps where they occur, and warns the vessels that put them at risk.</p>
  <div class="hero__stats" id="hero-stats">
    <div class="hero__stat"><div class="v">&mdash;</div><div class="k">Observations</div></div>
    <div class="hero__stat"><div class="v">&mdash;</div><div class="k">Incidents recorded</div></div>
    <div class="hero__stat"><div class="v">&mdash;</div><div class="k">Risk cells modelled</div></div>
    <div class="hero__stat"><div class="v">&mdash;</div><div class="k">Species covered</div></div>
  </div>
  <div class="hero__actions">
    <a class="btn btn--primary" href="gis.html">Open the GIS map</a>
    <a class="btn btn--ghost" href="dashboard.html">View the dashboard</a>
  </div>
</section>

<section class="mb-3">
  <div class="threecol">
    <div class="pillar reveal">
      <div class="pillar__n">1</div>
      <h3>The problem</h3>
      <p>Ship strikes, entanglement and noise are the leading human causes of mortality for large
         whales. Protection depends on knowing where animals are and where vessels will be, in
         near real time &mdash; which is exactly what is missing.</p>
    </div>
    <div class="pillar reveal">
      <div class="pillar__n">2</div>
      <h3>How data is collected</h3>
      <p>Underwater microphones record vocalizations, hydrophones and observers log sightings,
         AIS archives carry vessel positions, and ocean grids carry depth, temperature and human
         pressure. All of it lands in one PostgreSQL record.</p>
    </div>
    <div class="pillar reveal">
      <div class="pillar__n">3</div>
      <h3>How AI and GIS help</h3>
      <p>A trained classifier identifies the calling species from its spectrogram, a forecast model
         predicts presence over the coming week, and the GIS layer combines both with vessel
         traffic to rank the cells where strikes are most likely.</p>
    </div>
  </div>
</section>

<section class="grid grid--3">
  <a class="modcard reveal" href="gis.html">
    <div class="modcard__icon">%s</div>
    <h3>GIS Marine Map</h3>
    <p>The core workspace. Plot every observation, filter by species and region, and submit a new
       sighting straight from the map.</p>
    <div class="modcard__meta">Explore &amp; collect &rarr;</div>
  </a>
  <a class="modcard reveal" href="identify.html">
    <div class="modcard__icon">%s</div>
    <h3>AI Species Identification</h3>
    <p>Upload a photograph and a trained classifier returns the species with a confidence score.
       Every identification is kept in a searchable history.</p>
    <div class="modcard__meta">Classify &rarr;</div>
  </a>
  <a class="modcard reveal" href="bioacoustics.html">
    <div class="modcard__icon">%s</div>
    <h3>Marine Bioacoustics</h3>
    <p>Load a recording to see its waveform, log-mel spectrogram, measured frequency structure and
       the acoustic pattern the classifier recognised.</p>
    <div class="modcard__meta">Analyse sound &rarr;</div>
  </a>
  <a class="modcard reveal" href="observations.html">
    <div class="modcard__icon">%s</div>
    <h3>Observation Management</h3>
    <p>A structured form for submitting a sighting with species, position, date and optional
       media, with validation and a live table of everything submitted.</p>
    <div class="modcard__meta">Record &rarr;</div>
  </a>
  <a class="modcard reveal" href="analytics.html">
    <div class="modcard__icon">%s</div>
    <h3>Conservation Analytics</h3>
    <p>Charts of incident severity, sighting trends over time, risk distribution and the
       geographical spread of the record.</p>
    <div class="modcard__meta">Analyse trends &rarr;</div>
  </a>
  <a class="modcard reveal" href="dashboard.html">
    <div class="modcard__icon">%s</div>
    <h3>Professional Dashboard</h3>
    <p>The operational view: totals, conservation status, recent activity and the alerts that
       need attention first.</p>
    <div class="modcard__meta">Monitor &rarr;</div>
  </a>
</section>

<section class="mt-4">
  <div class="panel">
    <div class="panel__head">
      <div><h2>Data provenance</h2><p class="sub">What the platform holds and where it came from</p></div>
    </div>
    <div class="panel__body" id="provenance"></div>
  </div>
</section>
""" % (icon("map"), icon("ai"), icon("wave"), icon("observe"), icon("chart"), icon("dashboard"))

page("index.html", "Overview",
     "Marine conservation platform combining underwater acoustics, geospatial analysis and "
     "vessel-traffic risk modelling for whales and dolphins.",
     overview_body, "index.html",
     extra_js='<script src="js/config.js"></script>\n<script src="js/api.js"></script>\n'
              '<script src="js/overview.js"></script>')

# ===================================================================== DASHBOARD
dash_body = pagehead(
    [("Platform", None), ("Dashboard", None)],
    "Conservation dashboard",
    "Operational view of the platform record: totals, conservation status, recent activity and "
    "the alerts that need attention. Every figure is read from the platform database.") + """
<div id="dash-gate" class="panel" style="max-width:420px;margin:40px auto">
  <div class="panel__body">
    <h2>Researcher sign-in</h2>
    <p class="muted small" style="margin:6px 0 16px">Sign in against the platform API to load the
      dashboard and your own analysis history.</p>
    <form id="dash-login" novalidate>
      <div class="field">
        <label for="dl-email">Username</label>
        <input type="text" id="dl-email" value="researcher" required>
      </div>
      <div class="field">
        <label for="dl-pass">Password</label>
        <input type="password" id="dl-pass" value="researcher" required>
      </div>
      <button class="btn btn--primary btn--block" type="submit">Sign in</button>
      <p class="err" id="dl-error" style="display:none;color:var(--red);font-size:.78rem;margin-top:9px"></p>
      <p class="field__hint">Demonstration account: researcher / researcher</p>
    </form>
  </div>
</div>

<div id="dash-app" class="hidden">
  <div class="notice notice--warn" id="dash-offline" style="display:none"></div>
  <div class="kpis" id="dash-kpis"></div>

  <div class="grid grid--map mt-3">
    <div class="sidepanel">
      <div class="panel">
        <div class="panel__head"><h3>Important alerts</h3></div>
        <div class="panel__body"><div class="alert-list" id="dash-alerts"></div></div>
      </div>
      <div class="panel">
        <div class="panel__head"><h3>Conservation status</h3></div>
        <div class="panel__body panel__body--flush">
          <table><tbody id="dash-species"></tbody></table>
        </div>
      </div>
    </div>

    <div class="grid" style="gap:14px;align-content:start">
      <div class="panel">
        <div class="panel__head">
          <div><h3>Recent sightings</h3><p class="sub">Latest records in the platform database</p></div>
          <a class="btn btn--ghost btn--sm" href="gis.html">Open map</a>
        </div>
        <div class="panel__body panel__body--flush">
          <div class="tablewrap">
            <table>
              <thead><tr><th>Species</th><th>Date</th><th>Latitude</th><th>Longitude</th><th class="num">Count</th></tr></thead>
              <tbody id="dash-recent"></tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="panel">
        <div class="panel__head">
          <div><h3>Marine activity overview</h3><p class="sub">Recorded incidents by severity and cause</p></div>
        </div>
        <div class="panel__body">
          <div class="grid grid--2">
            <div class="chartbox"><canvas id="chart-severity"></canvas></div>
            <div class="chartbox"><canvas id="chart-cause"></canvas></div>
          </div>
        </div>
      </div>

      <div class="panel">
        <div class="panel__head">
          <div><h3>Recent mortality incidents</h3><p class="sub">Latest recorded events with cause and severity</p></div>
        </div>
        <div class="panel__body panel__body--flush">
          <div class="tablewrap">
            <table>
              <thead><tr><th>Date</th><th>Species</th><th>Cause</th><th>Severity</th><th>Latitude</th><th>Longitude</th></tr></thead>
              <tbody id="dash-incidents"></tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
"""
page("dashboard.html", "Dashboard",
     "Operational dashboard of marine observation totals, conservation status, recent activity "
     "and alerts, computed from the platform database.",
     dash_body, "dashboard.html",
     extra='<script src="vendor/chart.umd.min.js"></script>',
     extra_js='<script src="js/config.js"></script>\n<script src="js/api.js"></script>\n'
              '<script src="js/dashboard.js"></script>')

print("core pages generated")

# ===================================================================== GIS MAP
gis_body = pagehead(
    [("Observe", None), ("GIS Marine Map", None)],
    "GIS Marine Map",
    "The operational centre of the platform. Every observation is plotted by position; filter by "
    "species, region and date, open a marker for its full record, or submit a new observation "
    "directly on the map.",
    actions='<button class="btn btn--primary" id="btn-collect">+ Add observation</button>'
            '<button class="btn btn--ghost" id="btn-fit">Fit all records</button>') + """
<div class="toolbar">
  <input type="search" id="gis-search" placeholder="Filter by species or location&hellip;" aria-label="Filter records">
  <select id="gis-region" aria-label="Region">
    <option value="">All regions</option>
    <option value="Indian Ocean">Indian Ocean</option>
    <option value="Arabian Sea">Arabian Sea</option>
    <option value="Bay of Bengal">Bay of Bengal</option>
    <option value="Southern Ocean">Southern Ocean</option>
    <option value="Atlantic">Atlantic</option>
    <option value="Pacific">Pacific</option>
  </select>
  <select id="gis-species" aria-label="Species"><option value="">All species</option></select>
  <select id="gis-from" aria-label="From year"><option value="">From: any year</option></select>
  <select id="gis-to" aria-label="To year"><option value="">To: any year</option></select>
  <span class="count" id="gis-count">loading&hellip;</span>
</div>

<div class="grid grid--map">
  <div class="sidepanel">
    <div class="panel">
      <div class="panel__head">
        <h3>Species layers</h3>
        <button class="btn btn--quiet btn--sm" id="gis-all">All</button>
      </div>
      <div class="panel__body"><div class="filterlist" id="gis-species-list"></div></div>
    </div>

    <div class="panel" id="gis-detail-panel" style="display:none">
      <div class="panel__head">
        <div><h3 id="gis-detail-title">Record</h3><p class="sub" id="gis-detail-sub"></p></div>
        <button class="btn btn--quiet btn--sm" id="gis-detail-close">&times;</button>
      </div>
      <div class="panel__body"><div class="detailcard" id="gis-detail"></div></div>
    </div>

    <div class="panel" id="gis-collect-panel" style="display:none">
      <div class="panel__head">
        <div><h3>New observation</h3><p class="sub" id="collect-step">Step 1 &mdash; click the map to place the record</p></div>
        <button class="btn btn--quiet btn--sm" id="collect-cancel">&times;</button>
      </div>
      <div class="panel__body">
        <form id="collect-form" novalidate>
          <div class="field">
            <label for="cf-species">Species <span class="req">*</span></label>
            <select id="cf-species"></select>
            <div class="err">Select the species that was observed.</div>
          </div>
          <div class="formrow">
            <div class="field">
              <label for="cf-lat">Latitude <span class="req">*</span></label>
              <input type="number" id="cf-lat" step="0.0001" min="-90" max="90" placeholder="-19.3750">
              <div class="err">Latitude between -90 and 90 is required.</div>
            </div>
            <div class="field">
              <label for="cf-lon">Longitude <span class="req">*</span></label>
              <input type="number" id="cf-lon" step="0.0001" min="-180" max="180" placeholder="49.1250">
              <div class="err">Longitude between -180 and 180 is required.</div>
            </div>
          </div>
          <div class="formrow">
            <div class="field">
              <label for="cf-date">Date observed <span class="req">*</span></label>
              <input type="date" id="cf-date">
              <div class="err">A valid date is required.</div>
            </div>
            <div class="field">
              <label for="cf-count">Individuals</label>
              <input type="number" id="cf-count" min="1" max="5000" value="1">
            </div>
          </div>
          <div class="field">
            <label for="cf-notes">Notes</label>
            <textarea id="cf-notes" rows="3" placeholder="Behaviour, group size, conditions, how the record was made&hellip;"></textarea>
          </div>
          <div class="field">
            <label for="cf-media">Photograph or recording (optional)</label>
            <input type="file" id="cf-media" accept="image/*,audio/*">
            <div class="field__hint">The file name is stored with the record. File content is not uploaded.</div>
          </div>
          <label class="filterrow" style="padding-left:0">
            <input type="checkbox" id="cf-confirmed" checked>
            <span>Count is independently verified</span>
          </label>
          <div id="collect-auth" class="panel" style="display:none;margin-top:12px">
            <div class="panel__body">
              <h3>Researcher sign-in</h3>
              <p class="small muted" style="margin:4px 0 10px">Sign in to store observations
                against your account.</p>
              <div class="formrow">
                <div class="field" style="margin:0">
                  <label for="ca-user">Username</label>
                  <input type="text" id="ca-user" value="researcher">
                </div>
                <div class="field" style="margin:0">
                  <label for="ca-pass">Password</label>
                  <input type="password" id="ca-pass" value="researcher">
                </div>
              </div>
              <button class="btn btn--primary btn--sm mt-2" id="ca-login" type="button">Sign in</button>
              <p class="field__hint mt-2">Demonstration account: researcher / researcher</p>
            </div>
          </div>
          <button class="btn btn--primary btn--block mt-3" type="submit" id="collect-submit">Store observation</button>
          <p class="field__hint mt-2">Records are written to the platform PostgreSQL database and appear
             on the map immediately.</p>
        </form>
      </div>
    </div>
  </div>

  <div>
    <div class="mapframe">
      <div id="map"></div>
      <div class="mapstats" id="map-stats">
        <div><span class="k">Records shown</span><span class="v" id="ms-records">-</span></div>
        <div><span class="k">Species</span><span class="v" id="ms-species">-</span></div>
        <div><span class="k">Year range</span><span class="v" id="ms-years">-</span></div>
        <div><span class="k">Source</span><span class="v" id="ms-source">-</span></div>
      </div>
      <div class="maptools">
        <button class="btn btn--ghost btn--sm" id="map-recenter" title="Recentre">Recentre</button>
        <button class="btn btn--ghost btn--sm" id="map-fit" title="Fit all records">Fit</button>
      </div>
      <div class="maplegend">
        <h4>Legend</h4>
        <div><i style="background:#1b80c4"></i> Humpback whale</div>
        <div><i style="background:#12a8b8"></i> Spinner dolphin</div>
        <div><i style="background:#35d6c4"></i> Platform submission</div>
        <div><i style="background:#c0392b"></i> Selected record</div>
      </div>
    </div>
    <div class="panel mt-3">
      <div class="panel__head">
        <div><h3>Matching records</h3><p class="sub" id="gis-table-sub">Click a row to open the record on the map</p></div>
      </div>
      <div class="panel__body panel__body--flush">
        <div class="tablewrap" style="max-height:340px;overflow-y:auto">
          <table>
            <thead><tr><th>Species</th><th>Date</th><th>Latitude</th><th>Longitude</th><th class="num">Count</th><th>Source</th></tr></thead>
            <tbody id="gis-table"></tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</div>
"""
page("gis.html", "GIS Marine Map",
     "Interactive GIS map of whale and dolphin observations with species, region and date filtering, "
     "record details and an on-map observation submission workflow.",
     gis_body, "gis.html",
     extra='<link rel="stylesheet" href="vendor/leaflet/leaflet.css">',
     extra_js='<script src="vendor/leaflet/leaflet.js"></script>\n'
              '<script src="js/config.js"></script>\n<script src="js/api.js"></script>\n'
              '<script src="js/gis.js"></script>')

# ===================================================================== OBSERVATIONS
obs_body = pagehead(
    [("Observe", None), ("Observations", None)],
    "Observation management",
    "Submit a structured sighting record and review everything that has been stored. Validation "
    "runs on the form and again on the server.") + """
<div class="grid grid--map">
  <div class="sidepanel">
    <div class="panel">
      <div class="panel__head"><h3>Submit an observation</h3></div>
      <div class="panel__body">
        <form id="obs-form" novalidate>
          <div class="field">
            <label for="of-species">Species <span class="req">*</span></label>
            <select id="of-species"></select>
            <div class="err">Select the species that was observed.</div>
          </div>
          <div class="formrow">
            <div class="field">
              <label for="of-lat">Latitude <span class="req">*</span></label>
              <input type="number" id="of-lat" step="0.0001" min="-90" max="90" placeholder="-19.3750">
              <div class="err">Latitude must be between -90 and 90.</div>
            </div>
            <div class="field">
              <label for="of-lon">Longitude <span class="req">*</span></label>
              <input type="number" id="of-lon" step="0.0001" min="-180" max="180" placeholder="49.1250">
              <div class="err">Longitude must be between -180 and 180.</div>
            </div>
          </div>
          <div class="formrow">
            <div class="field">
              <label for="of-date">Date observed <span class="req">*</span></label>
              <input type="date" id="of-date">
              <div class="err">A valid date is required.</div>
            </div>
            <div class="field">
              <label for="of-count">Individuals <span class="req">*</span></label>
              <input type="number" id="of-count" min="1" max="5000" value="1">
              <div class="err">Enter a count between 1 and 5000.</div>
            </div>
          </div>
          <div class="field">
            <label for="of-notes">Observation notes</label>
            <textarea id="of-notes" rows="4" placeholder="Behaviour, group composition, sea state, how the record was made&hellip;"></textarea>
          </div>
          <div class="field">
            <label for="of-media">Photograph or recording (optional)</label>
            <input type="file" id="of-media" accept="image/*,audio/*">
            <div class="field__hint">The file name is stored with the record. File content is not uploaded.</div>
          </div>
          <label class="filterrow" style="padding-left:0">
            <input type="checkbox" id="of-confirmed" checked>
            <span>Count is independently verified</span>
          </label>
          <div id="obs-auth" class="panel" style="display:none;margin-top:12px">
            <div class="panel__body">
              <h3>Researcher sign-in</h3>
              <p class="small muted" style="margin:4px 0 10px">Sign in to store observations
                against your account.</p>
              <div class="formrow">
                <div class="field" style="margin:0">
                  <label for="oa-user">Username</label>
                  <input type="text" id="oa-user" value="researcher">
                </div>
                <div class="field" style="margin:0">
                  <label for="oa-pass">Password</label>
                  <input type="password" id="oa-pass" value="researcher">
                </div>
              </div>
              <button class="btn btn--primary btn--sm mt-2" id="oa-login" type="button">Sign in</button>
              <p class="field__hint mt-2">Demonstration account: researcher / researcher</p>
            </div>
          </div>
          <button class="btn btn--primary btn--block mt-3" type="submit" id="obs-submit">Store observation</button>
          <p class="field__hint mt-2">Records are written to the platform PostgreSQL database and
             appear on the GIS map immediately.</p>
        </form>
      </div>
    </div>
  </div>

  <div class="grid" style="gap:14px;align-content:start">
    <div class="panel">
      <div class="panel__head">
        <div><h3>Submitted observations</h3><p class="sub" id="obs-count">Loading&hellip;</p></div>
        <button class="btn btn--ghost btn--sm" id="obs-refresh">Refresh</button>
      </div>
      <div class="panel__body panel__body--flush">
        <div class="tablewrap">
          <table>
            <thead><tr><th>Date</th><th>Species</th><th>Latitude</th><th>Longitude</th><th class="num">Count</th><th>Verified</th><th></th></tr></thead>
            <tbody id="obs-table"></tbody>
          </table>
        </div>
      </div>
    </div>
    <div class="panel">
      <div class="panel__head"><h3>Record provenance</h3></div>
      <div class="panel__body">
        <p class="small muted">Observations submitted through this form are platform submissions and
          are marked accordingly. The verified sighting records loaded from OBIS are a separate
          dataset and are shown on the GIS map, not in this table.</p>
      </div>
    </div>
  </div>
</div>
"""
page("observations.html", "Observations",
     "Submit and review marine observation records with validated species, position, date and media.",
     obs_body, "observations.html",
     extra_js='<script src="js/config.js"></script>\n<script src="js/api.js"></script>\n'
              '<script src="js/observations.js"></script>')

print("observe pages generated")

# ===================================================================== AI IDENTIFY
identify_body = pagehead(
    [("Analyse", None), ("AI Species Identification", None)],
    "AI species identification",
    "Upload a photograph of a whale or dolphin. A trained classifier returns the most likely "
    "species with a confidence score, and every identification is kept in a reviewable history.",
    actions='<button class="btn btn--ghost btn--sm" id="id-history-toggle">Show history</button>') + """
<div class="grid grid--map">
  <div class="sidepanel">
    <div class="panel">
      <div class="panel__head"><h3>Upload a photograph</h3></div>
      <div class="panel__body">
        <label class="dropzone" id="id-drop" for="id-file">
          <div class="dropzone__ico">&#128247;</div>
          <b>Drop an image or click to browse</b>
          <span>JPG, PNG or WEBP &middot; up to 8 MB</span>
        </label>
        <input type="file" id="id-file" accept="image/*" hidden>
        <div class="mt-2" id="id-preview" style="border:1px solid var(--line);border-radius:8px;overflow:hidden;aspect-ratio:4/3;background:#f7fafc;display:grid;place-items:center">
          <span class="muted small">Image preview appears here</span>
        </div>
      </div>
    </div>
  </div>

  <div class="grid" style="gap:14px;align-content:start">
    <div class="panel">
      <div class="panel__head">
        <div><h3>Identification result</h3><p class="sub">Predicted species with confidence score</p></div>
      </div>
      <div class="panel__body">
        <div class="empty" id="id-empty">No image analysed yet.</div>
        <div id="id-loading" class="empty" style="display:none">
          <span class="spinner spinner--dark" style="display:inline-block;vertical-align:-3px;margin-right:8px"></span>
          Classifying&hellip;
        </div>
        <div id="id-result" style="display:none">
          <div class="result-head">
            <span class="name" id="id-species">-</span>
            <span class="conf" id="id-confidence">-</span>
            <span class="src" id="id-source"></span>
          </div>
          <p class="muted small" style="font-style:italic;margin-bottom:12px" id="id-latin"></p>
          <div id="id-bars"></div>
          <div class="patternbox">
            <h4>How to read this result</h4>
            <p id="id-note"></p>
            <p class="interp">Photographic identification is a model estimate on reference imagery.
               It supports triage of large image collections and is not a substitute for
               identification by a trained observer.</p>
          </div>
          <a class="btn btn--ghost btn--sm mt-3" id="id-species-link" href="species.html">Open the species record</a>
        </div>
      </div>
    </div>

    <div class="panel" id="id-history-panel" style="display:none">
      <div class="panel__head">
        <div><h3>Identification history</h3><p class="sub">Your previous identifications</p></div>
        <button class="btn btn--quiet btn--sm" id="id-history-close">&times;</button>
      </div>
      <div class="panel__body panel__body--flush">
        <div class="tablewrap">
          <table>
            <thead><tr><th>File</th><th>Species</th><th class="num">Confidence</th><th>When</th></tr></thead>
            <tbody id="id-history"></tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="panel__head">
        <div><h3>Reference photographs</h3><p class="sub">Openly-licensed images the classifier was trained on</p></div>
      </div>
      <div class="panel__body">
        <div class="grid grid--4" id="id-reference"></div>
        <p class="field__hint mt-3">Photographs come from Wikimedia Commons contributors under their
          respective free licences. Held-out accuracy is about 73%: the baleen whale classes are
          reliable, while the two dolphin classes are frequently confused with one another.</p>
      </div>
    </div>
  </div>
</div>
"""
page("identify.html", "AI Species Identification",
     "Identify whale and dolphin species from photographs with a trained classifier, with confidence "
     "scores and a reviewable identification history.",
     identify_body, "identify.html",
     extra_js='<script src="js/config.js"></script>\n<script src="js/api.js"></script>\n'
              '<script src="js/identify.js"></script>')

# ===================================================================== BIOACOUSTICS
bio_body = pagehead(
    [("Analyse", None), ("Marine Bioacoustics", None)],
    "Marine bioacoustics",
    "Load an underwater recording to see its waveform, log-mel spectrogram, measured frequency "
    "structure, species classification and the acoustic pattern the classifier recognised.") + """
<div class="grid grid--map">
  <div class="sidepanel">
    <div class="panel">
      <div class="panel__head"><h3>Upload a recording</h3></div>
      <div class="panel__body">
        <label class="dropzone" id="bio-drop" for="bio-file">
          <div class="dropzone__ico">&#9835;</div>
          <b>Drop an audio file or click to browse</b>
          <span>WAV, FLAC, OGG, MP3 or AIFF &middot; up to 25 MB</span>
        </label>
        <input type="file" id="bio-file" accept="audio/*,.wav,.flac,.ogg,.mp3,.aiff" hidden>
        <div id="file-meta" class="fact-grid mt-3" style="display:none">
          <div class="fact"><div class="k">File</div><div class="v" id="file-name">-</div></div>
          <div class="fact"><div class="k">Size</div><div class="v" id="file-size">-</div></div>
          <div class="fact"><div class="k">Duration</div><div class="v" id="file-duration">-</div></div>
          <div class="fact"><div class="k">Sample rate</div><div class="v" id="file-rate">-</div></div>
        </div>
        <div id="player-wrap" style="margin-top:10px;display:none">
          <audio id="player" controls preload="metadata" style="width:100%"></audio>
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="panel__head">
        <div><h3>Reference recordings</h3><p class="sub">Select to load into the analyser</p></div>
      </div>
      <div class="panel__body"><div class="sample-list" id="sample-list"></div></div>
    </div>
  </div>

  <div class="grid" style="gap:14px;align-content:start">
    <div class="panel">
      <div class="panel__head">
        <div><h3>Analysis result</h3><p class="sub">Measured features from the classifier and the acoustic-pattern analyser</p></div>
      </div>
      <div class="panel__body">
        <div class="empty" id="analysis-empty">No recording analysed yet.</div>
        <div class="empty" id="analysis-loading" style="display:none">
          <span class="spinner spinner--dark" style="display:inline-block;vertical-align:-3px;margin-right:8px"></span>
          Analysing&hellip;
        </div>
        <div id="analysis-result" style="display:none">
          <div class="result-head">
            <span class="name" id="a-species">-</span>
            <span class="conf" id="a-confidence">-</span>
            <span class="src" id="a-source"></span>
          </div>
          <div id="a-bars"></div>
          <div class="patternbox">
            <h4 id="a-pattern-label">-</h4>
            <p id="a-pattern-desc"></p>
            <p class="interp" id="a-pattern-interpretation"></p>
          </div>
          <div class="fact-grid mt-3">
            <div class="fact"><div class="k">Dominant frequency</div><div class="v" id="a-dom-freq">-</div></div>
            <div class="fact"><div class="k">Spectral centroid</div><div class="v" id="a-centroid">-</div></div>
            <div class="fact"><div class="k">Bandwidth</div><div class="v" id="a-bandwidth">-</div></div>
            <div class="fact"><div class="k">Pulse rate</div><div class="v" id="a-pulse">-</div></div>
            <div class="fact"><div class="k">Spectral flatness</div><div class="v" id="a-flatness">-</div></div>
            <div class="fact"><div class="k">Tonality</div><div class="v" id="a-tonality">-</div></div>
            <div class="fact"><div class="k">Signal-to-noise</div><div class="v" id="a-snr">-</div></div>
            <div class="fact"><div class="k">Recording length</div><div class="v" id="a-duration">-</div></div>
          </div>
          <div class="mt-3">
            <div class="viz__caption">Waveform</div>
            <div class="viz viz--wave"><canvas id="a-waveform" width="900" height="120"></canvas></div>
            <div class="viz__caption mt-3">Log-mel spectrogram</div>
            <div class="viz viz--spec"><canvas id="a-spectrogram" width="900" height="240"></canvas></div>
          </div>
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="panel__head">
        <div><h3>Marine communication simulator</h3><p class="sub">A research-informed simulation of an interaction between two animals</p></div>
      </div>
      <div class="panel__body">
        <div class="grid grid--3" style="gap:10px;align-items:end">
          <div class="field" style="margin:0">
            <label for="sim-group">Group</label>
            <select id="sim-group"><option value="whale">Whale</option><option value="dolphin">Dolphin</option></select>
          </div>
          <div class="field" style="margin:0">
            <label for="sim-species">Species</label>
            <select id="sim-species"></select>
          </div>
          <div class="field" style="margin:0">
            <label for="sim-turns">Turns</label>
            <select id="sim-turns"><option>4</option><option selected>6</option><option>8</option><option>10</option></select>
          </div>
        </div>
        <button class="btn btn--primary mt-3" id="sim-run" type="button">Generate simulation</button>

        <div class="empty" id="sim-empty" style="padding:20px 0 4px">Choose a group and generate.</div>
        <div id="sim-result" style="display:none" class="mt-3">
          <div class="result-head">
            <span class="name" id="sim-species">-</span>
            <span class="conf" id="sim-latin" style="font-style:italic;font-weight:400"></span>
            <span class="src" id="sim-source"></span>
          </div>
          <div class="fact-grid mt-2">
            <div class="fact"><div class="k">Call band</div><div class="v" id="sim-band">-</div></div>
            <div class="fact"><div class="k">Pulse rate</div><div class="v" id="sim-rate">-</div></div>
            <div class="fact"><div class="k">Signal structure</div><div class="v" id="sim-structure" style="font-size:.78rem"></div></div>
          </div>
          <p class="muted small mt-2" id="sim-context"></p>
          <div class="mt-3" id="sim-utterances"></div>
          <div class="panel mt-3">
            <div class="panel__head"><h3>Documented functions of these call types</h3></div>
            <div class="panel__body"><ul class="muted small" style="padding-left:18px" id="sim-functions"></ul></div>
          </div>
          <div class="disclaimer" id="sim-disclaimer"></div>
        </div>
      </div>
    </div>
  </div>
</div>
"""
page("bioacoustics.html", "Marine Bioacoustics",
     "Analyse whale and dolphin vocalizations: waveform, log-mel spectrogram, frequency structure, "
     "species classification and acoustic-pattern interpretation.",
     bio_body, "bioacoustics.html",
     extra_js='<script src="js/config.js"></script>\n<script src="js/api.js"></script>\n'
              '<script src="js/model.js"></script>\n<script src="js/dsp.js"></script>\n'
              '<script src="js/bioacoustics.js"></script>')

# ===================================================================== ANALYTICS
analytics_body = pagehead(
    [("Analyse", None), ("Conservation Analytics", None)],
    "Conservation and analytics",
    "Charts of incident severity and cause, sighting trends over time, the distribution of "
    "conservation risk and the geographical spread of the record. Every series is computed from the "
    "platform database.") + """
<div class="kpis" id="ana-kpis"></div>

<div class="grid grid--2 mt-3">
  <div class="panel">
    <div class="panel__head"><div><h3>Sighting records by year</h3><p class="sub">Observation frequency over time</p></div></div>
    <div class="panel__body"><div class="chartbox"><canvas id="ana-years"></canvas></div></div>
  </div>
  <div class="panel">
    <div class="panel__head"><div><h3>Incidents by cause</h3><p class="sub">Recorded mortality causes</p></div></div>
    <div class="panel__body"><div class="chartbox"><canvas id="ana-cause"></canvas></div></div>
  </div>
</div>

<div class="grid grid--2 mt-3">
  <div class="panel">
    <div class="panel__head"><div><h3>Incidents by severity</h3><p class="sub">Distribution of recorded event severity</p></div></div>
    <div class="panel__body"><div class="chartbox"><canvas id="ana-severity"></canvas></div></div>
  </div>
  <div class="panel">
    <div class="panel__head"><div><h3>Conservation risk classes</h3><p class="sub">Ocean grid cells assigned to each risk class</p></div></div>
    <div class="panel__body"><div class="chartbox"><canvas id="ana-risk"></canvas></div></div>
  </div>
</div>

<div class="grid grid--2 mt-3">
  <div class="panel">
    <div class="panel__head"><div><h3>Geographical distribution</h3><p class="sub">Sighting records by ocean region</p></div></div>
    <div class="panel__body"><div class="chartbox"><canvas id="ana-region"></canvas></div></div>
  </div>
  <div class="panel">
    <div class="panel__head"><div><h3>Species observation share</h3><p class="sub">Records per species</p></div></div>
    <div class="panel__body"><div class="chartbox"><canvas id="ana-species"></canvas></div></div>
  </div>
</div>

<div class="panel mt-3">
  <div class="panel__head">
    <div><h3>Conservation status by species</h3><p class="sub">IUCN Red List category held in the platform reference table</p></div>
  </div>
  <div class="panel__body panel__body--flush">
    <div class="tablewrap">
      <table>
        <thead><tr><th>Species</th><th>Scientific name</th><th>Status</th><th class="num">Records</th><th>Note</th></tr></thead>
        <tbody id="ana-species-table"></tbody>
      </table>
    </div>
  </div>
</div>
"""
page("analytics.html", "Conservation Analytics",
     "Charts of incident severity and cause, sighting trends, conservation risk distribution and "
     "the geographical spread of marine observation records.",
     analytics_body, "analytics.html",
     extra='<script src="vendor/chart.umd.min.js"></script>',
     extra_js='<script src="js/config.js"></script>\n<script src="js/api.js"></script>\n'
              '<script src="js/analytics.js"></script>')

print("analysis pages generated")

# ===================================================================== SPECIES DETAIL
detail_body = pagehead(
    [("Reference", None), ("Species Directory", None)],
    "Species record",
    "Habitat, distribution, conservation status, principal threats and the acoustic signature "
    "this species produces.") + """
<div id="spd-root"><div class="empty">Loading species record&hellip;</div></div>
"""
page("species-detail.html", "Species Record",
     "Habitat, distribution, conservation status and threats for a monitored whale or dolphin species.",
     detail_body, "species.html",
     extra_js='<script src="js/config.js"></script>\n<script src="js/api.js"></script>\n'
              '<script src="js/species-detail.js"></script>')

# ===================================================================== SPECIES
species_body = pagehead(
    [("Reference", None), ("Species Directory", None)],
    "Species directory",
    "A working directory of the whale and dolphin species covered by the platform, with habitat, "
    "distribution, conservation status and the acoustic signature each one produces.") + """
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
<p class="empty" id="sp-empty" style="display:none">No species match those filters.</p>
"""
page("species.html", "Species Directory",
     "Directory of whale and dolphin species with scientific names, habitat, distribution and "
     "IUCN conservation status.",
     species_body, "species.html",
     extra_js='<script src="js/config.js"></script>\n<script src="js/api.js"></script>\n'
              '<script src="js/species.js"></script>')

# ===================================================================== RESEARCH
research_body = pagehead(
    [("Reference", None), ("Research &amp; Insights", None)],
    "Research and insights",
    "The datasets, methods and findings behind the platform. Every figure here comes from the "
    "project data or from the models trained on it.") + """
<div class="panel">
  <div class="panel__head"><div><h2>Datasets</h2><p class="sub">What the platform is built on</p></div></div>
  <div class="panel__body"><div class="grid grid--3" id="res-datasets"></div></div>
</div>

<div class="grid grid--2 mt-3">
  <div class="panel">
    <div class="panel__head"><h2>Species identification from sound</h2></div>
    <div class="panel__body">
      <p class="small muted">Recordings are converted to 5-second windows and then to log-mel
        spectrograms over 64 mel-spaced frequency bands. A logistic regression trained on these
        arrays separates the calls of each species and is stress-tested by mixing ship noise back
        into the training audio at signal-to-noise ratios from 20 dB down to 0 dB.</p>
      <p class="small muted mt-2">Grad-CAM is used to confirm the network attends to the call
        structure rather than to artefacts of the background noise. The same feature extraction is
        implemented identically in Python and in the browser, so on-server and in-browser
        inference agree exactly.</p>
    </div>
  </div>
  <div class="panel">
    <div class="panel__head"><h2>Forecast and risk</h2></div>
    <div class="panel__body">
      <p class="small muted">Daily detection records become rolling rate features over 7, 14 and 30
        days, combined with seasonal and day-of-year terms. Gradient boosting predicts whether a
        species will be present in the following seven days, trained only on earlier years.</p>
      <p class="small muted mt-2">Ship-strike risk combines that forecast with vessel traffic
        derived from AIS positions and a logistic lethality curve relating speed to collision
        probability, which also enables the 10-knot what-if scenario.</p>
    </div>
  </div>
</div>

<div class="mt-3">
  <div class="panel__head" style="padding:0 0 10px"><div><h2>Findings</h2><p class="sub">Measured results from the trained models</p></div></div>
  <div class="grid grid--3" id="res-findings"></div>
</div>

<div class="mt-3">
  <div class="panel__head" style="padding:0 0 10px"><div><h2>Publications and references</h2><p class="sub">Methods references and data sources used by the project</p></div></div>
  <div class="pub-list" id="res-pubs"></div>
</div>

<div class="mt-3">
  <div class="panel__head" style="padding:0 0 10px"><div><h2>Downloadable resources</h2><p class="sub">Project artefacts published for reuse</p></div></div>
  <div class="grid grid--4" id="res-downloads"></div>
</div>

<div class="panel mt-3">
  <div class="panel__head">
    <div><h2>Complete dataset catalogue</h2><p class="sub" id="cat-total">Every dataset behind the platform, with row counts and direct downloads</p></div>
    <a class="btn btn--primary btn--sm" href="downloads/WhaleAI_Complete_Dataset.zip" download>Download complete dataset (ZIP)</a>
  </div>
  <div class="panel__body">
    <div class="tablewrap">
      <table>
        <thead><tr><th>File</th><th>Group</th><th class="num">Rows</th><th>Description</th><th></th></tr></thead>
        <tbody id="res-catalogue"></tbody>
      </table>
    </div>
    <p class="field__hint mt-3">Occurrence records are published by the Ocean Biodiversity Information
      System (OBIS) under their own data-sharing terms. Every other table is produced by this
      project's pipeline.</p>
  </div>
</div>
"""
page("research.html", "Research and Insights",
     "Marine conservation research: datasets, model methodology, measured findings, references "
     "and downloadable resources.",
     research_body, "research.html",
     extra_js='<script src="js/config.js"></script>\n<script src="js/api.js"></script>\n'
              '<script src="js/research.js"></script>')

# ===================================================================== CONSERVATION
conservation_body = pagehead(
    [("Reference", None), ("Conservation", None)],
    "Conservation",
    "The pressures on whale and dolphin populations, the strategies that address them and the "
    "protection initiatives the platform supports.") + """
<div class="panel__head" style="padding:0 0 10px"><div><h2>Threats</h2><p class="sub">What drives marine mammal mortality</p></div></div>
<div class="grid grid--3" id="cons-threats"></div>

<div class="mt-4">
  <div class="panel__head" style="padding:0 0 10px"><div><h2>Conservation strategies</h2><p class="sub">How the platform supports each response</p></div></div>
  <div class="grid grid--3" id="cons-strategies"></div>
</div>

<div class="mt-4">
  <div class="panel__head" style="padding:0 0 10px">
    <div><h2>Priority species</h2><p class="sub">Ordered by conservation status</p></div>
  </div>
  <div class="grid grid--3" id="cons-species"></div>
</div>
"""
page("conservation.html", "Conservation",
     "Threats to whales and dolphins, conservation strategies and marine protection initiatives.",
     conservation_body, "conservation.html",
     extra_js='<script src="js/config.js"></script>\n<script src="js/api.js"></script>\n'
              '<script src="js/conservation.js"></script>')

# ===================================================================== ABOUT
about_body = pagehead(
    [("About", None), ("About &amp; Contact", None)],
    "About the platform",
    "WhaleAI Conservation is a capstone-built marine conservation platform that combines "
    "acoustics, geospatial analysis and operational risk modelling into one working system.") + """
<div class="grid grid--2">
  <div class="panel">
    <div class="panel__head"><h2>Mission and vision</h2></div>
    <div class="panel__body">
      <p class="small muted">Every conservation decision is made with incomplete information. The
        platform's purpose is to close that gap: to listen to the ocean continuously, understand
        which animals are present and where, and translate that into advice a vessel captain can
        act on the same day.</p>
      <p class="small muted mt-2">The vision is a shared, open evidence base. Detection records,
        models and risk outputs are published so regulators, researchers and conservation
        organisations are not each rebuilding the same baseline.</p>
    </div>
  </div>
  <div class="panel">
    <div class="panel__head"><h2>Technology</h2></div>
    <div class="panel__body">
      <ul class="small muted" style="padding-left:18px">
        <li style="margin-bottom:7px"><strong>Acoustic analysis</strong> &mdash; log-mel spectrograms, 5-second windowing, noise robustness against mixed ship noise at 0&ndash;20 dB SNR</li>
        <li style="margin-bottom:7px"><strong>Machine learning</strong> &mdash; scikit-learn and PyTorch for classification, gradient boosting for presence forecasting</li>
        <li style="margin-bottom:7px"><strong>Geospatial analysis</strong> &mdash; OBIS occurrence records, H3 hexagonal indexing, haversine distance, AIS vessel tracks</li>
        <li style="margin-bottom:7px"><strong>Data platform</strong> &mdash; PostgreSQL with a Bronze/Silver/Gold layering and full run traceability</li>
      </ul>
    </div>
  </div>
</div>

<div class="panel mt-3">
  <div class="panel__head"><h2>Team</h2></div>
  <div class="panel__body">
    <div class="grid grid--3">
      <div>
        <h3>Deepak Sagar</h3>
        <p class="small muted">Data science and machine learning &mdash; model development, feature engineering and the web platform</p>
      </div>
      <div>
        <h3>Marine acoustics</h3>
        <p class="small muted">Passive acoustic monitoring, spectrogram design and the noise-robustness protocol</p>
      </div>
      <div>
        <h3>GIS and risk</h3>
        <p class="small muted">Geospatial modelling, AIS traffic exposure and the ship-strike risk engine</p>
      </div>
    </div>
  </div>
</div>

<div class="grid grid--2 mt-3">
  <div class="panel">
    <div class="panel__head"><h2>Contact</h2></div>
    <div class="panel__body">
      <dl class="fact-list">
        <div><dt>General enquiries</dt><dd>research@whaleai.org</dd></div>
        <div><dt>Data contributions</dt><dd>research@whaleai.org</dd></div>
        <div><dt>Source repository</dt><dd>github.com/DeepakSagar00</dd></div>
        <div><dt>Occurrence data</dt><dd>OBIS</dd></div>
      </dl>
    </div>
  </div>
  <div class="panel">
    <div class="panel__head"><h2>Send a message</h2></div>
    <div class="panel__body">
      <form id="contact-form" novalidate>
        <div class="formrow">
          <div class="field">
            <label for="cf-name">Name <span class="req">*</span></label>
            <input type="text" id="cf-name">
            <div class="err">Name is required.</div>
          </div>
          <div class="field">
            <label for="cf-email">Email <span class="req">*</span></label>
            <input type="email" id="cf-email">
            <div class="err">A valid email address is required.</div>
          </div>
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
          <label for="cf-msg">Message <span class="req">*</span></label>
          <textarea id="cf-msg" rows="4"></textarea>
          <div class="err">Message is required.</div>
        </div>
        <button class="btn btn--primary" type="submit">Send message</button>
        <p class="field__hint mt-2" id="cf-note" style="display:none;color:var(--green)">
          Thank you &mdash; your message has been recorded locally for this demonstration build.
        </p>
      </form>
    </div>
  </div>
</div>
"""
page("about.html", "About and Contact",
     "Mission, vision, technology, team and contact details for the WhaleAI marine conservation "
     "platform.",
     about_body, "about.html",
     extra_js='<script src="js/config.js"></script>\n<script src="js/api.js"></script>\n'
              '<script src="js/contact.js"></script>')

# ===================================================================== PRIVACY
privacy_body = pagehead(
    [("About", None), ("Privacy Policy", None)],
    "Privacy policy",
    "How this platform handles the information you provide.") + """
<div class="panel" style="max-width:900px">
  <div class="panel__body">
    <h2 class="mb-2">Summary</h2>
    <p class="small muted mb-3">This is a demonstration build of a marine conservation research
      platform. It is designed so that sensitive data never has to leave your device.</p>

    <h2 class="mb-2">Audio recordings</h2>
    <p class="small muted mb-3">Audio files selected for classification are decoded, resampled and
      analysed either inside your browser or on the platform API. The browser path never uploads
      the file. When the server path is used the file is processed in memory for the analysis and
      is not stored.</p>

    <h2 class="mb-2">Photographs</h2>
    <p class="small muted mb-3">Images are sent to the API for classification and the file name is
      recorded against the result so the identification history stays meaningful.</p>

    <h2 class="mb-2">Submitted observations</h2>
    <p class="small muted mb-3">Observations you submit are written to the platform database and
      become part of the shared record. They are labelled as platform submissions so they are
      never confused with independently verified sighting data.</p>

    <h2 class="mb-2">Dashboard access</h2>
    <p class="small muted mb-3">The researcher dashboard uses the platform API for authentication.
      Credentials are sent to the API for verification and a session token is held in the browser
      only.</p>

    <h2 class="mb-2">Third-party components</h2>
    <p class="small muted mb-3">The GIS explorer loads map tiles from the OpenStreetMap tile
      servers and the dashboard loads the Chart.js charting library from a public CDN. Those
      requests disclose your IP address and browser user-agent to those providers.</p>

    <h2 class="mb-2">Sighting records</h2>
    <p class="small muted mb-3">All occurrence records published here are derived from the Ocean
      Biodiversity Information System (OBIS), an open-access repository of marine biodiversity data
      published under its own data-sharing terms.</p>
  </div>
</div>
"""
page("privacy.html", "Privacy Policy",
     "How the WhaleAI marine conservation platform handles audio, photographs, observations and "
     "dashboard access.",
     privacy_body, "about.html")

print("\nAll pages generated.")



