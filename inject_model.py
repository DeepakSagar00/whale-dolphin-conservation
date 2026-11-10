"""Inject model.json into index.html so the site is fully self-contained.

Re-runnable: replaces whatever is inside the model-data script tag.
"""
import json
import re

HTML = r"C:\Users\Deepak Sagar\OneDrive\Desktop\MoveOne\whale-dolphin-conservation\website\index.html"
MODEL = r"C:\Users\Deepak Sagar\OneDrive\Desktop\MoveOne\whale-dolphin-conservation\website\model.json"

with open(MODEL, encoding="utf-8") as f:
    model_json = json.dumps(json.load(f), separators=(",", ":"))

with open(HTML, encoding="utf-8") as f:
    html = f.read()

pattern = re.compile(
    r'(<script id="model-data" type="application/json">)(.*?)(</script>)',
    re.DOTALL,
)

if not pattern.search(html):
    raise SystemExit("model-data script tag not found")

html, n = pattern.subn(lambda m: m.group(1) + model_json + m.group(3), html, count=1)

with open(HTML, "w", encoding="utf-8") as f:
    f.write(html)

print(f"injected model ({n} replacement), {len(model_json)} chars")
print("index.html size:", len(html), "chars")
