"""Generate js/data.js from real project data (OBIS sightings + species info)."""
import json
from pathlib import Path

import pandas as pd
import urllib.request

ROOT = Path(r"C:\Users\Deepak Sagar\OneDrive\Desktop\MoveOne\whale-dolphin-conservation")
OUT = ROOT / "website" / "js" / "data.js"

# ---- species directory (factual, from public conservation references) ----
SPECIES = [
    {
        "id": "blue-whale",
        "name": "Blue Whale",
        "latin": "Balaenoptera musculus",
        "type": "Whale",
        "status": "EN",
        "statusLabel": "Endangered",
        "population": "~10,000–25,000",
        "length": "Up to 30 m",
        "weight": "Up to 180 tonnes",
        "habitat": "Open ocean, from polar to tropical waters",
        "distribution": "Worldwide, except the Arctic; migratory between feeding and breeding grounds",
        "diet": "Krill",
        "description": "The blue whale is the largest animal known to have lived on Earth. Its calls are among the loudest sounds made by any animal and can travel hundreds of kilometres underwater.",
        "threats": ["Ship strikes", "Entanglement in fishing gear", "Ocean noise", "Climate-driven krill decline"],
    },
    {
        "id": "fin-whale",
        "name": "Fin Whale",
        "latin": "Balaenoptera physalus",
        "type": "Whale",
        "status": "VU",
        "statusLabel": "Vulnerable",
        "population": "~100,000",
        "length": "Up to 26 m",
        "weight": "Up to 80 tonnes",
        "habitat": "Offshore and open ocean, deep waters",
        "distribution": "Worldwide in all major oceans, mostly in temperate to polar zones",
        "diet": "Krill, small schooling fish",
        "description": "The fin whale is the second-largest animal on Earth and one of the fastest swimmers among great whales, reaching speeds of up to 40 km/h.",
        "threats": ["Ship strikes", "Entanglement", "Historical whaling", "Ocean noise"],
    },
    {
        "id": "humpback-whale",
        "name": "Humpback Whale",
        "latin": "Megaptera novaeangliae",
        "type": "Whale",
        "status": "LC",
        "statusLabel": "Least Concern",
        "population": "~80,000",
        "length": "Up to 16 m",
        "weight": "Up to 40 tonnes",
        "habitat": "Coastal and open ocean; shelf and shelf-edge waters",
        "distribution": "Worldwide; long migrations between polar feeding grounds and tropical breeding areas",
        "diet": "Krill, small schooling fish",
        "description": "Humpback whales are known for their complex songs, long pectoral fins and spectacular breaching. They are among the most studied great whales.",
        "threats": ["Ship strikes", "Entanglement", "Ocean noise", "Climate change"],
    },
    {
        "id": "killer-whale",
        "name": "Killer Whale",
        "latin": "Orcinus orca",
        "type": "Whale",
        "status": "DD",
        "statusLabel": "Data Deficient",
        "population": "~50,000",
        "length": "Up to 9 m",
        "weight": "Up to 6 tonnes",
        "habitat": "All oceans, from tropical seas to polar waters",
        "distribution": "Worldwide, in both coastal and offshore waters",
        "diet": "Fish, seals, other cetaceans (varies by population)",
        "description": "The killer whale, or orca, is the largest member of the dolphin family. Different populations have distinct cultures, diets and vocal dialects.",
        "threats": ["Prey depletion", "Pollution", "Noise disturbance", "Capture legacy"],
    },
    {
        "id": "bottlenose-dolphin",
        "name": "Bottlenose Dolphin",
        "latin": "Tursiops truncatus",
        "type": "Dolphin",
        "status": "LC",
        "statusLabel": "Least Concern",
        "population": "~600,000",
        "length": "Up to 4 m",
        "weight": "Up to 650 kg",
        "habitat": "Temperate and tropical seas, coastal and offshore",
        "distribution": "Worldwide in warm-temperate and tropical waters",
        "diet": "Fish, squid, crustaceans",
        "description": "The bottlenose dolphin is one of the best-known cetaceans, recognised for its intelligence, curiosity and frequent presence near coasts and vessels.",
        "threats": ["Bycatch", "Pollution", "Habitat degradation", "Boat traffic"],
    },
    {
        "id": "spinner-dolphin",
        "name": "Spinner Dolphin",
        "latin": "Stenella longirostris",
        "type": "Dolphin",
        "status": "LC",
        "statusLabel": "Least Concern",
        "population": "~1,000,000",
        "length": "Up to 2.4 m",
        "weight": "Up to 79 kg",
        "habitat": "Tropical and subtropical pelagic waters",
        "distribution": "Worldwide in tropical and warm-temperate oceans",
        "diet": "Small fish, squid",
        "description": "The spinner dolphin is named for its acrobatic spinning leaps. It rests in sheltered bays during the day and feeds offshore at night.",
        "threats": ["Bycatch in tuna fisheries", "Habitat degradation", "Disturbance from tourism"],
    },
]

# ---- real OBIS sightings, sampled for the web map ----
def load_sightings(path, species_id, species_name, n, seed=42):
    df = pd.read_csv(path)
    df = df.dropna(subset=["decimalLatitude", "decimalLongitude"])
    df = df[(df.decimalLatitude.between(-60, 60)) & (df.decimalLongitude.between(-180, 180))]
    if len(df) > n:
        df = df.sample(n=n, random_state=seed)
    return [
        {
            "lat": round(float(r.decimalLatitude), 4),
            "lon": round(float(r.decimalLongitude), 4),
            "date": str(r.eventDate)[:10],
            "count": (None if pd.isna(r.individualCount) else int(r.individualCount)),
            "species": species_name,
            "speciesId": species_id,
        }
        for r in df.itertuples()
    ]


sightings = []
sightings += load_sightings(
    (ROOT / "data" / "raw" / "Megaptera_novaeangliae.csv"), "humpback-whale", "Humpback Whale", 420)
sightings += load_sightings(
    (ROOT / "data" / "raw" / "Stenella_longirostris.csv"), "spinner-dolphin", "Spinner Dolphin", 300)

# ---- real model metrics from the project ----
metrics = json.load(open((ROOT / "backend" / "ml" / "ml_metrics.json"), encoding="utf-8"))

# ---- real sightings exactly as the API returns them (database record) ----
proc = ROOT / "data" / "processed" / "sightings_clean.csv"
db_sightings = []
if proc.exists():
    import pandas as pd
    df = pd.read_csv(proc)
    df = df.dropna(subset=["lat", "lon"])
    species_map = {"humpback_whale": "Humpback whale", "spinner_dolphin": "Spinner dolphin"}
    sci_map = {"humpback_whale": "Megaptera novaeangliae", "spinner_dolphin": "Stenella longirostris"}
    for i, r in enumerate(df.itertuples(), start=1):
        sp = getattr(r, "species", None) or "humpback_whale"
        db_sightings.append({
            "id": i,
            "species_id": 1 if sp == "humpback_whale" else 2,
            "common_name": species_map.get(sp, "Unidentified"),
            "scientific_name": sci_map.get(sp, ""),
            "event_date": str(r.date)[:10] if hasattr(r, "date") else "",
            "lat": float(r.lat),
            "lon": float(r.lon),
            "individual_count": None if getattr(r, "individuals", None) is None else float(r.individuals),
            "source": "OBIS",
        })

# ---- database aggregates so the dashboard renders without the API ----
dashboard = {}
ov_path = ROOT / "website" / "js" / "_overview.json"
try:
    import urllib.request
    req = urllib.request.Request("http://127.0.0.1:8000/api/dashboard/overview")
    with urllib.request.urlopen(req, timeout=30) as r:
        dashboard = json.loads(r.read().decode())
except Exception:
    try:
        dashboard = json.loads(ov_path.read_text(encoding="utf-8"))
    except Exception:
        dashboard = {}

data = {
    "species": SPECIES,
    "sightings": sightings,
    "dbSightings": db_sightings,
    "dashboard": dashboard,
    "metrics": {
        "accuracy": round(metrics["accuracy"] * 100, 1),
        "f1": round(metrics["f1_weighted"], 3),
        "rocAuc": round(metrics["roc_auc_ovr"], 3),
        "featureImportance": metrics["feature_importance"],
        "classes": metrics["classes"],
    },
    "gridRisk": {"total": 12856, "Low": 3248, "Moderate": 3225, "High": 3206, "Critical": 3177},
}

with open(OUT, "w", encoding="utf-8") as f:
    f.write("/* Generated from real project data (OBIS + backend/ml). */\n")
    f.write("window.SITE_DATA = ")
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write(";\n")

print("species:", len(SPECIES))
print("sightings:", len(sightings))
print("written:", OUT)


