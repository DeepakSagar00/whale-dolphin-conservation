# WhaleAI Conservation — Marine Intelligence Platform

An intelligent marine conservation platform for capstone **ASAC-CP-141**:
*Listen → Recognise → Predict → Warn*.

- **Front end (live):** https://deepaksagar00.github.io/whale-dolphin-conservation/
- **API source:** `api/` in this repository (FastAPI + PostgreSQL, deployable to Vercel or Render)
- **Deployment guide:** [DEPLOYMENT.md](DEPLOYMENT.md)

---

## Application structure

A fixed top bar and a grouped navigation rail wrap every page, so the interface
reads as one application rather than a set of linked documents.

```
┌────────────────────────────────────────────────────────────────────┐
│ Top bar: brand · global search · API status · signed-in researcher   │
├──────────────┬─────────────────────────────────────────────────────┤
│ Platform     │  Page header: breadcrumb · title · actions           │
│  Overview    │  ─────────────────────────────────────────────────  │
│  Dashboard   │                                                     │
│ Observe      │  Content                                           │
│  GIS Map     │                                                     │
│  Observations│                                                     │
│ Analyse      │                                                     │
│  AI ID       │                                                     │
│  Bioacoustics│                                                     │
│  Analytics   │                                                     │
│ Reference    │                                                     │
│  Species     │                                                     │
│  Research    │                                                     │
│  Conservation│                                                     │
│ About        │                                                     │
└──────────────┴─────────────────────────────────────────────────────┘
```

| Page | Purpose |
|---|---|
| `index.html` | Overview — the problem, how data is collected, how AI and GIS help |
| `dashboard.html` | Professional dashboard — totals, status, recent activity, alerts, charts |
| `gis.html` | **GIS Marine Map** — plot every observation, filter, inspect, and submit on the map |
| `observations.html` | Observation management — validated submission form and stored-records table |
| `identify.html` | AI species identification — photo upload, confidence, identification history |
| `bioacoustics.html` | Marine bioacoustics — waveform, spectrogram, pattern analysis, simulator |
| `analytics.html` | Conservation analytics — six charts plus the status table |
| `species.html` / `species-detail.html` | Species directory and individual species records |
| `research.html` | Datasets, methodology, findings, references, downloads |
| `conservation.html` | Threats, strategies and priority species |
| `about.html` / `privacy.html` | Mission, technology, team, contact, privacy |

## The GIS observation workflow

1. **Visualise** — 411 verified OBIS records plus any platform submissions are
   plotted with species, region, year and text filters, and a live layer list.
2. **Inspect** — clicking a marker or a table row opens the full record:
   position, date, individuals, region, source and verification state.
3. **Collect** — *Add observation* switches the map into capture mode. Clicking
   the map drops a pin; the form is validated in the browser and again on the
   server; the record is written to PostgreSQL and appears on the map at once.

## Backend

FastAPI + PostgreSQL with JWT authentication, CORS, upload validation and
graceful degradation when the database is unreachable.

| Area | Endpoints |
|---|---|
| Bioacoustics | `POST /api/audio/analyze`, `POST /api/audio/classify`, `GET /api/audio/history` |
| Image ID | `POST /api/image/identify`, `GET /api/image/history` |
| Simulator | `POST /api/simulator/conversation`, `GET /api/simulator/species` |
| Observations | `POST /api/observations`, `GET /api/observations`, `DELETE /api/observations/{id}` |
| Dashboard | `GET /api/dashboard/overview` |
| Reference | `GET /api/species/directory`, `GET /api/public/stats`, `GET /api/public/sightings` |
| Risk | `GET /api/risk/predict`, `GET /api/risk/summary`, `GET /api/recommendations` |
| Auth | `POST /api/auth/login`, `POST /api/auth/register` |

### Database tables

`users` · `species` · `sightings` · `grid_cells` · `incidents` · `protected_areas` ·
`corridors` · `risk_predictions` · `recommendations` · `recordings` · `audio_analyses` ·
`image_predictions` · `simulations` · **`observations`** (GIS collection)

## Models

| Model | Technique | Artefact | Measured accuracy |
|---|---|---|---|
| Audio species classifier | Logistic regression over 64 mel-spaced bands (mean + std per 5 s window) | `api/ml/audio_model.json` | separates all 6 classes; 12/12 on held-out reference recordings |
| Image species classifier | HOG + colour histogram → multinomial logistic regression | `api/ml/image_model.joblib` | 73% held-out (whales 0.82–0.94 F1, dolphins weaker) |
| Grid risk model | Random Forest over ocean grid features | `api/ml/model.pkl` | 99.3% accuracy, 0.993 weighted F1 |

The audio feature extraction is implemented identically in
`website/js/dsp.js` (browser), `backend/app/bioacoustics.py` (server) and
`website/train_web_model.py` (training), so all three agree exactly.

## Resilience

- The front end bundles a snapshot of the platform database, so the map,
  dashboard and analytics still render real figures if the API is unreachable.
- Audio analysis falls back to the same trained model running in the browser.
- The API client fails over between known endpoints and times out quickly.

## Running it locally

```powershell
.\start_platform.ps1        # PostgreSQL + FastAPI + public tunnel, writes the API URL into config.js
.\stop_platform.ps1         # stop the API and tunnel
```

Or manually:

```bash
.\start_all.ps1                        # portable PostgreSQL + FastAPI on :8000
python -m http.server 8080 --directory website
```

Sign in with `researcher` / `researcher`.

## Repository layout

```
api/               serverless API bundle (app package, models, grid data)
css/style.css      design system
js/                api client · dsp · config · per-page controllers
assets/species/    species illustrations
samples/           reference recordings and photographs
downloads/         published research artefacts
database/          SQL schema
scripts/           data pipeline, model training and test scripts
```
