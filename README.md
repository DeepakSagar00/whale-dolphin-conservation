# WhaleAI Conservation — Marine Intelligence Platform

A multi-page marine conservation platform built for capstone **ASAC-CP-141**:
*Listen → Recognise → Predict → Warn*.

Live site: https://deepaksagar00.github.io/whale-dolphin-conservation/

## Pages

| Page | Purpose |
|---|---|
| `index.html` | Minimal homepage — mission, featured species, conservation initiatives |
| `species.html` | Species Explorer — search, filter and browse the species directory |
| `species-detail.html?id=<id>` | Individual species record (habitat, distribution, status, threats) |
| `conservation.html` | Threats, conservation strategies and priority species |
| `research.html` | Research & Insights — datasets, method, findings, publications, downloads |
| `gis.html` | GIS Marine Explorer — interactive Leaflet map of real OBIS occurrence records |
| `ai.html` | AI Conservation — working in-browser audio species classifier |
| `dashboard.html` | Researcher Dashboard — analytics, charts and sighting records (sign-in gated) |
| `about.html` | About, mission, technology, team and contact form |
| `privacy.html` | Privacy policy |

## Structure

```
css/style.css        shared design system
js/data.js           generated — species, real OBIS sightings, model metrics
js/main.js           shared behaviour (nav, reveal animations, helpers)
js/*.js              per-page logic
assets/species/      species illustrations (SVG)
assets/logo.svg      whale & dolphin mark
model.json           trained browser-side classifier weights
downloads/           real project artefacts offered for download
```

## Data provenance

All figures published on this site come from the project itself:

- **Sighting records** — Ocean Biodiversity Information System (OBIS): 720 sampled
  records drawn from the 10,000 humpback whale and 1,500 spinner dolphin records in
  the working dataset.
- **Risk model metrics** — `backend/ml/ml_metrics.json` (99.3% accuracy, 0.993 weighted F1).
- **Grid risk classes** — 12,856 cells from `data/processed/features_grid.csv`.

## AI classifier

`model.json` holds a logistic regression over 64 mel-spaced frequency bands
(mean and standard deviation across a 5-second window, 128 features), trained by
`train_web_model.py`. The website reproduces the training feature extraction exactly
in JavaScript, so browser inference matches the Python model.

Rebuild the model with:

```bash
python train_web_model.py
```

## Build scripts

The static pages are generated so the shared header, footer and navigation stay
consistent across every page:

```bash
python build_data.py       # regenerate js/data.js from the project data
python build_assets.py     # regenerate species illustrations
python build_pages.py      # regenerate all HTML pages
python build_downloads.py  # refresh downloadable artefacts
```

## Licence

Demonstration build. Sighting records are published under the OBIS data-sharing
terms. All other code in this repository is provided for academic capstone review.
