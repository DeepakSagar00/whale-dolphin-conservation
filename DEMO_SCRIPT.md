# Demo script — Intelligent Whale & Dolphin Conservation Platform

**Website:** https://deepaksagar00.github.io/whale-dolphin-conservation/
**Sign in:** `researcher` / `researcher`

Run this before you present:

```powershell
cd C:\Users\Deepak Sagar\OneDrive\Desktop\MoveOne\whale-dolphin-conservation
.\start_platform.ps1
```

It starts PostgreSQL, the FastAPI service and the public tunnel, then republishes
the site with the new API address. About 60 seconds.

---

## The 8-minute walkthrough

### 1. Overview — the pitch (30 seconds)
`index.html`

Open on the hero. Say:

> "Whale and dolphin populations are declining, and the decisions that protect them are made with
> incomplete information. This platform listens to the ocean, identifies the animals making the
> sound, maps where they occur, and warns the vessels that put them at risk."

Point at the three numbered panels (problem → data collection → AI + GIS) and the live figures:
**411 observations · 6,847 incidents · 12,856 modelled cells**.

### 2. Dashboard — the operational view (60 seconds)
`dashboard.html` → sign in with `researcher` / `researcher`

- Four KPI tiles computed straight from PostgreSQL
- **Important alerts** — real, derived from the incidents and risk tables, each with its source
- Conservation status table per species
- Recent sightings and recent mortality incidents
- Marine activity overview: incidents by severity and by cause

### 3. GIS Marine Map — the centrepiece (2 minutes)
`gis.html`

The map opens already fitted to the data. Show:

1. **The context strip** over the map: records shown, species, year range, data source
2. **Filters** — uncheck *Spinner dolphin* and watch 77 markers disappear; set a year range
3. **Marker inspection** — click a marker (or a row in the table) for the full record
4. **Collection workflow** — the money shot:
   - Click **+ Add observation**
   - Click anywhere on the map → a pin is placed, the panel switches to *Step 2*
   - Fill species / date / individuals / notes, press **Store observation**
   - It is written to PostgreSQL and the marker appears immediately
   - Show it in `observations.html` and in the Dashboard's platform-submissions count

### 4. Marine bioacoustics — the AI differentiator (90 seconds)
`bioacoustics.html`

- Click a reference recording (or play it)
- The server runs real DSP: log-mel spectrogram, dominant frequency, bandwidth, pulse rate,
  spectral flatness, tonality
- Species classification with confidence and a ranked probability bar chart
- The acoustic pattern label: *Humpback whale → Harmonic / song-like structure (750 Hz)*,
  *Bottlenose dolphin → Tonal whistle (5.4 kHz)*, *Ship noise → Ambient / broadband noise*
- **Marine Communication Simulator** — pick Dolphin → Bottlenose dolphin → Generate. Emphasise the
  label: *AI-generated educational simulation, not a decoded translation*.

### 5. AI species identification (45 seconds)
`identify.html`

- Click one of the reference photographs (e.g. killer whale) → species + confidence
- Show **Identification history** (records stored against the signed-in account)
- State the honest limitation: ~73% held-out accuracy, whales reliable, the two dolphin
  classes are often confused with each other.

### 6. Conservation analytics (45 seconds)
`analytics.html`

Six charts from the database: sightings by year, incidents by cause and severity, conservation
risk classes, geographical distribution, species share, plus the status table.

### 7. Research & data (45 seconds)
`research.html`

- Datasets, methodology, measured findings
- **Complete dataset catalogue** — 43 files, 135,603 rows, with a *Get* button per file
- **Download complete dataset (ZIP)** button
- Downloadable artefacts

### 8. Close on the mission (20 seconds)
`about.html` — mission, technology, team, contact form.

---

## Things you can say with confidence

- Every number is computed from the platform PostgreSQL database — nothing is hard-coded.
- Sighting records come from **OBIS**; the grid, pressure layers and risk model are this
  project's own pipeline.
- The acoustic classifier is a real trained model (logistic regression over 64 mel-spaced
  frequency bands) that reproduces its training feature extraction identically in the browser and
  on the server.
- The image classifier is a real trained model with a **published, honest** accuracy of ~73%.
- Platform submissions are labelled distinctly from verified OBIS records.

## If something goes wrong

| Symptom | Fix |
|---|---|
| Top bar shows **API offline** | Run `.\start_platform.ps1` again — it republishes automatically |
| Page looks stale | Hard refresh: `Ctrl` + `Shift` + `R` |
| Map shows no markers | The API is offline; the site falls back to its bundled database snapshot |
| Sign-in fails | Use `researcher` / `researcher` |

## If you have five minutes to spare

Deploy the API to Vercel so the demo does not depend on your laptop being on:
<https://vercel.com> → sign in → import `DeepakSagar00/whale-dolphin-conservation` → deploy.
Then send me the URL and I will point the site at it.
