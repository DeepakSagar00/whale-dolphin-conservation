# WhaleAI Conservation — Marine Intelligence Platform

An intelligent marine conservation platform for capstone **ASAC-CP-141**:
*Listen → Recognise → Predict → Warn*.

- **Front end (live):** https://deepaksagar00.github.io/whale-dolphin-conservation/
- **API source:** `api/` in this repository (FastAPI, deployable to Vercel or Render)
- **Deployment guide:** [DEPLOYMENT.md](DEPLOYMENT.md)

---

## Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│  Static front end (GitHub Pages)                                   │
│  index · species · bioacoustics · identify · gis · research ·      │
│  conservation · dashboard · about · privacy                         │
└──────────────┬─────────────────────────────────────────────────────┘
               │  fetch  (js/api.js)
┌──────────────▼─────────────────────────────────────────────────────┐
│  FastAPI service  (api/ → Vercel serverless or Render)             │
│  ├─ /api/audio/analyze      real DSP + species classification      │
│  ├─ /api/image/identify     photographic species classification     │
│  ├─ /api/simulator/*        research-grounded communication model   │
│  ├─ /api/risk/*             grid risk prediction (Random Forest)    │
│  ├─ /api/species/directory  species reference                      │
│  └─ /api/public/*           sightings, statistics, model status     │
└──────────────┬─────────────────────────────────────────────────────┘
               │  psycopg2
┌──────────────▼─────────────────────────────────────────────────────┐
│  PostgreSQL — database/schema.sql                                  │
│  sightings · grid_cells · incidents · species · protected_areas ·  │
│  corridors · risk_predictions · recommendations · recordings ·      │
│  audio_analyses · image_predictions · simulations · users           │
└────────────────────────────────────────────────────────────────────┘
```

## Pages

| Page | Purpose |
|---|---|
| `index.html` | Minimal homepage — mission, featured species, conservation initiatives |
| `species.html` | Species Explorer — search, group/status filters, species directory |
| `species-detail.html?id=<id>` | Individual species record — habitat, distribution, status, threats |
| `bioacoustics.html` | **Marine Bioacoustics** — upload, waveform, spectrogram, pattern analysis, explorer, simulator |
| `identify.html` | **AI Species Identification** — photograph upload, classification, confidence |
| `gis.html` | **GIS Marine Explorer** — interactive Leaflet map of real OBIS records, filters, layers |
| `ai.html` | Audio species classifier running in the browser (same model as the server) |
| `research.html` | Research & Insights — datasets, methodology, findings, publications, downloads |
| `conservation.html` | Threats, conservation strategies, priority species |
| `dashboard.html` | **Researcher Dashboard** — real API sign-in, live database statistics, analysis history |
| `about.html` | Mission, vision, technology, team, contact form |
| `privacy.html` | Privacy policy |

## Models

| Model | Technique | Artefact | Accuracy |
|---|---|---|---|
| Audio species classifier | Logistic regression over 64 mel-spaced bands (mean + std per 5 s window) | `api/ml/audio_model.json` | separates all 6 classes on held-out reference recordings |
| Image species classifier | HOG + colour histogram → multinomial logistic regression | `api/ml/image_model.joblib` | 73% held-out (whales 0.82–0.94 F1; dolphins weaker) |
| Grid risk model | Random Forest over ocean grid features | `api/ml/model.pkl` | 99.3% accuracy, 0.993 weighted F1 |

The audio classifier's feature extraction is implemented identically in
`website/js/dsp.js` (browser), `backend/app/bioacoustics.py` (server) and
`website/train_web_model.py` (training), so all three agree exactly.

## Acoustic pattern analysis

The platform labels a recording's acoustic *structure* — never a translation of meaning:

| Pattern | Measured signature |
|---|---|
| Low-frequency call | dominant frequency < 200 Hz, narrow band (blue and fin whale) |
| Tonal whistle | band < 200 Hz wide, tonality > 60, above 400 Hz (dolphin) |
| Harmonic / song structure | moderate band, repeated phrases (humpback, killer whale) |
| Broadband click train | high pulse rate, wide band |
| Ambient / broadband noise | full-band energy, almost no tonal peak (ship noise) |

Every interpretation is labelled as research-based; the semantic content of
individual calls is not established and the interface says so.

## Data provenance

- **Sighting records** — Ocean Biodiversity Information System (OBIS): 10,000 humpback
  whale and 1,500 spinner dolphin records in the working dataset; 720 published on the site.
- **Grid and risk** — 12,856 modelled ocean grid cells from `data/processed/features_grid.csv`.
- **Incidents** — 6,847 historical mortality records.
- **Reference photographs** — 378 openly-licensed Wikimedia Commons images.
- **Reference recordings** — synthesised samples that reproduce each class's spectral signature.

## Repository layout

```
api/               serverless API bundle (app package, models, grid data)
api/index.py       FastAPI entry point
css/style.css      design system
js/                api client · dsp · config · per-page controllers
assets/species/    species illustrations
samples/           reference recordings and photographs
downloads/         published research artefacts
database/          SQL schema
scripts/           data pipeline, model training and test scripts
```

## Local development

```bash
# 1. portable PostgreSQL + API
.\start_all.ps1

# 2. static site
python -m http.server 8080 --directory website

# 3. open http://127.0.0.1:8080
```

The front end automatically targets `http://127.0.0.1:8000` when served from localhost.
