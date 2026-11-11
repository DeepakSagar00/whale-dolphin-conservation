"""Copy real project artefacts into the website downloads folder."""
import json
import os
import shutil

ROOT = r"C:\Users\Deepak Sagar\OneDrive\Desktop\MoveOne\whale-dolphin-conservation"
DL = os.path.join(ROOT, "website", "downloads")
os.makedirs(DL, exist_ok=True)

# 1. sighting sample from the published dataset
data = json.load(open(os.path.join(ROOT, "website", "js", "data.js").replace("js/data.js", "js/data.js"), encoding="utf-8")) \
    if False else None

import re
raw = open(os.path.join(ROOT, "website", "js", "data.js"), encoding="utf-8").read()
payload = raw.split("window.SITE_DATA = ", 1)[1].rsplit(";", 1)[0]
site = json.loads(payload)

rows = ["species,scientific_name,decimalLatitude,decimalLongitude,eventDate,individualCount,region"]
LATIN = {"humpback-whale": "Megaptera novaeangliae", "spinner-dolphin": "Stenella longirostris"}


def region_of(lat, lon):
    if lat < -35:
        return "Southern Ocean"
    if lon < -30:
        return "Atlantic"
    if lon > 130:
        return "Pacific"
    if 5 <= lat <= 25 and 50 <= lon <= 78:
        return "Arabian Sea"
    if 5 <= lat <= 23 and 79 <= lon <= 98:
        return "Bay of Bengal"
    return "Indian Ocean"


for s in site["sightings"]:
    rows.append("%s,%s,%.5f,%.5f,%s,%s,%s" % (
        s["species"], LATIN.get(s["speciesId"], ""), s["lat"], s["lon"], s["date"],
        "" if s["count"] is None else s["count"], region_of(s["lat"], s["lon"])))

with open(os.path.join(DL, "sightings_sample.csv"), "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(rows) + "\n")
print("sightings_sample.csv", len(site["sightings"]), "records")

# 2. model metrics
shutil.copyfile(
    os.path.join(ROOT, "backend", "ml", "ml_metrics.json"),
    os.path.join(DL, "ml_metrics.json"))
print("ml_metrics.json")

# 3. feature grid sample
import csv
src = os.path.join(ROOT, "data", "processed", "features_grid.csv")
with open(src, encoding="utf-8", newline="") as f:
    reader = csv.reader(f)
    header = next(reader)
    sample = []
    for i, row in enumerate(reader):
        if i % 6 == 0:
            sample.append(row)
        if len(sample) >= 2000:
            break
with open(os.path.join(DL, "features_grid_sample.csv"), "w", encoding="utf-8", newline="\n") as f:
    w = csv.writer(f)
    w.writerow(header)
    w.writerows(sample)
print("features_grid_sample.csv", len(sample), "rows")

# 4. research notebook
nb = os.path.join(ROOT, "notebooks", "Whale_Dolphin_Capstone_Colab.ipynb")
if os.path.exists(nb):
    shutil.copyfile(nb, os.path.join(DL, "Whale_Dolphin_Capstone_Colab.ipynb"))
    print("Whale_Dolphin_Capstone_Colab.ipynb")

for f in sorted(os.listdir(DL)):
    print("  %-42s %8.1f KB" % (f, os.path.getsize(os.path.join(DL, f)) / 1024))
