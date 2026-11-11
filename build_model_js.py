"""Generate js/model.js from model.json so the classifier works offline too."""
import json

ROOT = r"C:\Users\Deepak Sagar\OneDrive\Desktop\MoveOne\whale-dolphin-conservation\website"

with open(ROOT + r"\model.json", encoding="utf-8") as f:
    model = json.load(f)

payload = json.dumps(model, separators=(",", ":"))

with open(ROOT + r"\js\model.js", "w", encoding="utf-8") as f:
    f.write("/* Trained species classifier weights - generated from model.json.\n")
    f.write("   Loaded as a script so the site works offline (file://) as well as over HTTP. */\n")
    f.write("window.MODEL = " + payload + ";\n")

print("js/model.js written:", len(payload), "chars")
