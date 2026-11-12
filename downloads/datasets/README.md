# WhaleAI Conservation - Complete Dataset

Capstone ASAC-CP-141. Every dataset used by the platform.

See `DATASET_CATALOG.json` for the description, row count and provenance of each file.

## Groups

- `database_export/` - every PostgreSQL table as CSV
- `raw/` - original OBIS occurrence downloads
- `processed/` - cleaned and modelled tables
- `simulated/` - human-pressure layers used by the risk model
- `geojson/` - map layers served by the API
- `models/` - trained model weights and metrics
- `database/` - SQL schema

Occurrence records come from the Ocean Biodiversity Information System (OBIS)
under their own data-sharing terms.
