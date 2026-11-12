"""Assemble the complete platform dataset bundle.

Exports every PostgreSQL table to CSV, copies the raw/processed/simulated/GeoJSON
files, writes a catalogue, and produces one downloadable ZIP.
"""
import csv
import json
import os
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(r"C:\Users\Deepak Sagar\OneDrive\Desktop\MoveOne\whale-dolphin-conservation")
WEB = ROOT / "website"
DL = WEB / "downloads" / "datasets"
STAGE = Path(os.environ.get("TEMP", r"C:\Windows\Temp")) / "whale_dataset_bundle"

sys.path.insert(0, str(ROOT / "backend"))
from app import db  # noqa: E402

DB_TABLES = [
    ("users", "Platform accounts (usernames, roles and hashed passwords)"),
    ("species", "Species reference table with IUCN category"),
    ("sightings", "Sighting records loaded from OBIS"),
    ("grid_cells", "Modelled ocean grid: depth, SST, vessel, fishing, noise, risk class"),
    ("incidents", "Historical mortality incidents with cause and severity"),
    ("protected_areas", "Marine protected areas in the study region"),
    ("corridors", "Predicted movement corridors between hotspots"),
    ("risk_predictions", "Grid risk predictions with confidence"),
    ("recommendations", "Conservation advisories generated from the risk model"),
    ("recordings", "Uploaded audio recordings analysed by the platform"),
    ("audio_analyses", "Bioacoustic analysis results per recording"),
    ("image_predictions", "Photographic species identification history"),
    ("simulations", "Marine communication simulator runs"),
    ("observations", "Observations submitted through the GIS collection workflow"),
]

FILES = [
    ("data/raw/Megaptera_novaeangliae.csv", "raw", "OBIS occurrence records - humpback whale (10,000)"),
    ("data/raw/Stenella_longirostris.csv", "raw", "OBIS occurrence records - spinner dolphin (1,500)"),
    ("data/raw/download_metadata.json", "raw", "OBIS download provenance"),
    ("data/processed/sightings_clean.csv", "processed", "Cleaned sighting table loaded into the database (411)"),
    ("data/processed/features_grid.csv", "processed", "Modelled ocean grid with risk class per cell (12,856)"),
    ("data/processed/features_metadata.json", "processed", "Grid feature definitions and sources"),
    ("data/processed/dbscan_clusters.csv", "processed", "DBSCAN sighting hotspot clusters"),
    ("data/processed/kde_density.csv", "processed", "Kernel density estimate per grid cell"),
    ("data/processed/corridors.csv", "processed", "Predicted corridors (summary)"),
    ("data/processed/corridors_polyline.json", "processed", "Predicted corridor geometries"),
    ("data/processed/environment_0.5.csv", "processed", "Environmental layer grid"),
    ("data/processed/environment_metadata.json", "processed", "Environmental layer provenance"),
    ("data/simulated/simulated_layers.csv", "simulated", "Simulated human-pressure layers"),
    ("data/simulated/vessel_intensity.csv", "simulated", "Vessel intensity per grid cell"),
    ("data/simulated/fishing_intensity.csv", "simulated", "Fishing intensity per grid cell"),
    ("data/simulated/noise_proxy.csv", "simulated", "Anthropogenic noise proxy per grid cell"),
    ("data/simulated/protected_areas.csv", "simulated", "Protected area definitions"),
    ("data/simulated/SIMULATION_METADATA.json", "simulated", "Simulation method and parameters"),
    ("data/geojson/sightings.geojson", "geojson", "Sighting records as GeoJSON"),
    ("data/geojson/risk_cells.geojson", "geojson", "Risk classification polygons"),
    ("data/geojson/hotspots.geojson", "geojson", "Sighting hotspot polygons"),
    ("data/geojson/mpas.geojson", "geojson", "Marine protected area polygons"),
    ("data/geojson/corridors.geojson", "geojson", "Predicted corridor lines"),
    ("data/geojson/incidents.geojson", "geojson", "Incident points"),
    ("data/geojson/vessels.geojson", "geojson", "Vessel traffic positions"),
    ("database/schema.sql", "database", "PostgreSQL schema for the platform"),
    ("backend/ml/ml_metrics.json", "models", "Grid risk model metrics"),
    ("backend/ml/audio_model.json", "models", "Audio species classifier weights"),
    ("backend/ml/image_model_metrics.json", "models", "Image classifier metrics"),
]


def export_tables():
    out_dir = STAGE / "database_export"
    out_dir.mkdir(parents=True, exist_ok=True)
    catalogue = []
    for table, description in DB_TABLES:
        rows = db.safe_fetch_all("SELECT * FROM " + table)
        path = out_dir / (table + ".csv")
        if rows:
            cols = list(rows[0].keys())
            with open(path, "w", encoding="utf-8", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=cols)
                w.writeheader()
                for r in rows:
                    w.writerow({k: ("" if r[k] is None else r[k]) for k in cols})
        catalogue.append({
            "name": "%s.csv" % table, "group": "database",
            "rows": len(rows), "description": description,
        })
        print("  %-26s %6s rows" % (table, format(len(rows), ",")))
    return catalogue


def main():
    if STAGE.exists():
        shutil.rmtree(STAGE)
    STAGE.mkdir(parents=True)

    print("exporting database tables:")
    catalogue = export_tables()

    print("copying project files:")
    for rel, group, description in FILES:
        src = ROOT / rel
        if not src.exists():
            print("  MISSING", rel)
            continue
        dest = STAGE / group / Path(rel).name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        rows = ""
        if dest.suffix.lower() == ".csv":
            with open(dest, encoding="utf-8", errors="ignore") as fh:
                n = max(0, sum(1 for _ in fh) - 1)
            rows = n
        catalogue.append({
            "name": "%s/%s" % (group, Path(rel).name), "group": group,
            "rows": rows, "description": description,
        })
        print("  %-52s %s" % (rel, ("%s rows" % format(rows, ",")) if rows != "" else ""))

    # write the catalogue
    cat = {
        "project": "WhaleAI Conservation - Intelligent Whale and Dolphin Conservation Platform",
        "capstone": "ASAC-CP-141",
        "generated": "database export + project files",
        "files": catalogue,
        "total_files": len(catalogue),
        "total_rows": sum(c["rows"] for c in catalogue if isinstance(c["rows"], int)),
    }
    with open(STAGE / "DATASET_CATALOG.json", "w", encoding="utf-8") as fh:
        json.dump(cat, fh, indent=2)

    with open(STAGE / "README.md", "w", encoding="utf-8") as fh:
        fh.write("# WhaleAI Conservation - Complete Dataset\n\n"
                 "Capstone ASAC-CP-141. Every dataset used by the platform.\n\n"
                 "See `DATASET_CATALOG.json` for the description, row count and provenance of each file.\n\n"
                 "## Groups\n\n"
                 "- `database_export/` - every PostgreSQL table as CSV\n"
                 "- `raw/` - original OBIS occurrence downloads\n"
                 "- `processed/` - cleaned and modelled tables\n"
                 "- `simulated/` - human-pressure layers used by the risk model\n"
                 "- `geojson/` - map layers served by the API\n"
                 "- `models/` - trained model weights and metrics\n"
                 "- `database/` - SQL schema\n\n"
                 "Occurrence records come from the Ocean Biodiversity Information System (OBIS)\n"
                 "under their own data-sharing terms.\n")

    # publish to the website
    if DL.exists():
        shutil.rmtree(DL)
    shutil.copytree(STAGE, DL)

    # one-click zip
    zip_path = WEB / "downloads" / "WhaleAI_Complete_Dataset.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(STAGE.rglob("*")):
            if f.is_file():
                z.write(f, Path("WhaleAI_Complete_Dataset") / f.relative_to(STAGE))
    print("\nzip: %s (%.1f MB)" % (zip_path, zip_path.stat().st_size / 1048576))
    print("published %d files to %s" % (len(catalogue), DL))


if __name__ == "__main__":
    main()
