# Deployment Guide

Two components make up the platform:

| Component | Where it runs | Public URL |
|---|---|---|
| Front end (static site) | GitHub Pages | https://deepaksagar00.github.io/whale-dolphin-conservation/ |
| API (FastAPI + models + PostgreSQL) | Any container/serverless host | see below |

---

## 1. Front end — already deployed

GitHub Pages serves the repository root. Every push to `main` rebuilds it.

```bash
cd website
git add -A
git commit -m "..."
git push origin main
```

The site reads the API address from `website/js/config.js`:

```js
var DEFAULT_API = 'https://your-api-host.example.com';
```

You can also override it at runtime without rebuilding:

```
https://deepaksagar00.github.io/whale-dolphin-conservation/index.html?api=https://other-host.example.com
```

The override is remembered in `localStorage`.

---

## 2. API — deploy to Vercel (recommended)

The repository already contains everything Vercel needs:

```
api/index.py        FastAPI entry point
api/app/            application package
api/ml/             trained models
api/data/           ocean grid used by the risk model
requirements.txt    runtime dependencies
vercel.json         routing + function configuration
```

### Steps

1. **Sign in** — <https://vercel.com/signup> (use the Google account you already use).
2. **Add a new project** → *Import* → select `DeepakSagar00/whale-dolphin-conservation`.
3. Vercel detects `api/index.py` and the `vercel.json`. Keep **Framework Preset = Other**
   and the root directory as the repository root.
4. **Deploy.** You get a URL such as `https://whale-dolphin-conservation.vercel.app`.
5. **Point the front end at it** — put the URL in `website/js/config.js` (`DEFAULT_API`)
   and push again. The site can also be told at runtime with `?api=<url>`.

### Environment variables (optional but recommended)

| Variable | Purpose |
|---|---|
| `DATABASE_URL` | Hosted PostgreSQL connection string. Without it the API still serves every model-backed feature, but it cannot persist analysis history or read the sighting tables. |
| `JWT_SECRET` | Signing key for authentication tokens. Set this in production. |

---

## 3. API — deploy to Render (alternative)

`render.yaml` is included as a Render blueprint.

1. Sign in at <https://render.com>.
2. **New → Blueprint** → select the repository. Render detects `render.yaml`.
3. Set `DATABASE_URL` and `JWT_SECRET` when prompted.
4. Copy the resulting URL into `website/js/config.js`.

---

## 4. API — run locally (development)

```bash
# 1. start the portable PostgreSQL (port 5433)
cd whale-dolphin-conservation
.\start_all.ps1

# 2. start the API
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --app-dir backend
```

The front end automatically uses `http://127.0.0.1:8000` when it is served from
`localhost` or `127.0.0.1`.

---

## 5. Hosted PostgreSQL

Any managed PostgreSQL works. The API reads `DATABASE_URL`; if it is absent it falls
back to the local `PGHOST` / `PGPORT` / `PGDATABASE` / `PGUSER` variables.

Free options: Neon, Supabase, Aiven, or Render's own PostgreSQL.

The schema is in `database/schema.sql` and is idempotent — it can be applied to an
empty database with:

```sql
-- e.g. with psql
psql "$DATABASE_URL" -f database/schema.sql
```

The platform stores:

| Table | Contents |
|---|---|
| `users` | Researcher accounts (PBKDF2-hashed passwords) |
| `species` | Species reference |
| `sightings` | OBIS occurrence records |
| `grid_cells` | Ocean grid with risk class per cell |
| `incidents` | Historical mortality events |
| `protected_areas`, `corridors` | Protection and movement context |
| `risk_predictions`, `recommendations` | Model outputs |
| `recordings`, `audio_analyses` | Uploaded audio and its analysis results |
| `image_predictions` | Image identification history |
| `simulations` | Communication simulator runs |

---

## 6. Rebuilding the models

```bash
# audio classifier (exported to website/model.json + backend/ml/audio_model.json)
website/train_web_model.py

# reference images from Wikimedia Commons
scripts/09_fetch_species_images.py

# image classifier
scripts/10_train_image_model.py

# sample recordings + API validation
scripts/12_make_samples.py

# serverless bundle
scripts/13_build_api_bundle.py

# static pages
website/build_pages.py
```

---

## 7. Verifying a deployment

```bash
curl https://<api-host>/api/health
curl https://<api-host>/api/models/status
curl https://<api-host>/api/public/stats
```

Then open the front-end URL, go to **Research → Marine Bioacoustics**, load a reference
recording and confirm the banner reports "Backend connected" and the result identifies
the correct species.
