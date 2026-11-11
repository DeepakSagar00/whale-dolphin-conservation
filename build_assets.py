"""Generate stylised species illustrations + logo as standalone SVG assets."""
import os

OUT = r"C:\Users\Deepak Sagar\OneDrive\Desktop\MoveOne\whale-dolphin-conservation\website\assets\species"

HEADER = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300" '
    'preserveAspectRatio="xMidYMid slice" role="img" aria-label="{label}">\n'
    '  <defs>\n'
    '    <linearGradient id="sea" x1="0" y1="0" x2="0" y2="1">\n'
    '      <stop offset="0%" stop-color="#0d3a5c"/>\n'
    '      <stop offset="55%" stop-color="#12557f"/>\n'
    '      <stop offset="100%" stop-color="#0a2b46"/>\n'
    '    </linearGradient>\n'
    '    <linearGradient id="body" x1="0" y1="0" x2="1" y2="1">\n'
    '      <stop offset="0%" stop-color="{c1}"/>\n'
    '      <stop offset="100%" stop-color="{c2}"/>\n'
    '    </linearGradient>\n'
    '    <radialGradient id="glow" cx="50%" cy="40%" r="60%">\n'
    '      <stop offset="0%" stop-color="#2dd4bf" stop-opacity=".22"/>\n'
    '      <stop offset="100%" stop-color="#2dd4bf" stop-opacity="0"/>\n'
    '    </radialGradient>\n'
    '  </defs>\n'
    '  <rect width="400" height="300" fill="url(#sea)"/>\n'
    '  <rect width="400" height="300" fill="url(#glow)"/>\n'
)

FOOTER = "</svg>\n"

# shared body silhouette (facing right), tail on the left
BODY = (
    "M 46,150 C 66,120 118,104 186,102 "
    "C 238,100 288,108 326,122 C 344,129 350,140 346,150 "
    "C 350,160 344,171 326,178 C 288,192 238,200 186,198 "
    "C 118,196 66,180 46,150 Z"
)
TAIL = "M 56,150 C 42,141 22,126 8,116 C 21,135 28,145 32,150 C 28,155 21,165 8,184 C 22,174 42,159 56,150 Z"
BELLY = "M 86,166 C 130,186 200,192 268,180 C 240,194 150,198 96,180 Z"

FILES = {}

# ---------------- Blue whale ----------------
FILES["blue-whale.svg"] = HEADER.format(
    label="Blue whale illustration", c1="#5b7f9e", c2="#2c4a63"
) + f"""
  <path d="{TAIL}" fill="#2c4a63"/>
  <path d="{BODY}" fill="url(#body)"/>
  <path d="{BELLY}" fill="#7f9db5" opacity=".55"/>
  <path d="M 268,106 L 280,94 L 284,107 Z" fill="#2c4a63"/>
  <path d="M 262,186 L 248,212 L 282,190 Z" fill="#3a5c78"/>
  <g fill="#8fb0c6" opacity=".45">
    <circle cx="150" cy="140" r="4"/><circle cx="182" cy="162" r="3"/>
    <circle cx="126" cy="158" r="2.5"/><circle cx="205" cy="132" r="3.5"/>
    <circle cx="222" cy="168" r="2.5"/><circle cx="100" cy="145" r="2"/>
    <circle cx="238" cy="146" r="2"/><circle cx="168" cy="176" r="2"/>
  </g>
  <circle cx="322" cy="138" r="3.4" fill="#0a2b46"/>
""" + FOOTER

# ---------------- Fin whale ----------------
FILES["fin-whale.svg"] = HEADER.format(
    label="Fin whale illustration", c1="#4f6f8b", c2="#27405a"
) + f"""
  <path d="{TAIL}" fill="#27405a"/>
  <path d="{BODY}" fill="url(#body)"/>
  <path d="{BELLY}" fill="#8aa4ba" opacity=".5"/>
  <path d="M 252,104 L 272,84 L 276,106 Z" fill="#27405a"/>
  <path d="M 258,186 L 244,210 L 278,190 Z" fill="#36506b"/>
  <path d="M 300,178 C 320,182 336,176 346,166 C 340,178 322,186 300,184 Z" fill="#e8eef3" opacity=".85"/>
  <circle cx="320" cy="136" r="3.2" fill="#0a2b46"/>
""" + FOOTER

# ---------------- Humpback whale ----------------
FILES["humpback-whale.svg"] = HEADER.format(
    label="Humpback whale illustration", c1="#3f5f7d", c2="#20384f"
) + f"""
  <path d="{TAIL}" fill="#20384f"/>
  <path d="{BODY}" fill="url(#body)"/>
  <path d="{BELLY}" fill="#7893aa" opacity=".5"/>
  <path d="M 262,187 C 240,206 206,232 168,246 C 186,222 210,200 232,184 Z" fill="#35536e"/>
  <path d="M 300,185 C 288,214 262,244 232,262 C 252,234 268,208 278,183 Z" fill="#3c5c79"/>
  <path d="M 238,104 L 256,88 L 262,106 Z" fill="#20384f"/>
  <g fill="#7e99b0" opacity=".38">
    <circle cx="120" cy="136" r="4"/><circle cx="146" cy="158" r="3.5"/>
    <circle cx="186" cy="128" r="3"/><circle cx="214" cy="172" r="2.5"/>
  </g>
  <circle cx="322" cy="136" r="3.2" fill="#0a2b46"/>
""" + FOOTER

# ---------------- Killer whale ----------------
FILES["killer-whale.svg"] = HEADER.format(
    label="Killer whale illustration", c1="#22303f", c2="#0d1620"
) + f"""
  <path d="{TAIL}" fill="#0d1620"/>
  <path d="{BODY}" fill="url(#body)"/>
  <path d="M 236,102 L 262,58 L 272,104 Z" fill="#0d1620"/>
  <path d="M 258,186 L 242,214 L 282,190 Z" fill="#16222e"/>
  <ellipse cx="330" cy="150" rx="30" ry="20" fill="#f2f6f9"/>
  <ellipse cx="330" cy="176" rx="34" ry="12" fill="#f2f6f9"/>
  <ellipse cx="306" cy="128" rx="10" ry="6" fill="#f2f6f9"/>
  <circle cx="314" cy="136" r="3.2" fill="#0a2b46"/>
""" + FOOTER

# ---------------- Bottlenose dolphin ----------------
FILES["bottlenose-dolphin.svg"] = HEADER.format(
    label="Bottlenose dolphin illustration", c1="#7e9db5", c2="#4a6a86"
) + f"""
  <path d="M 52,150 L 18,120 L 38,150 L 18,180 Z" fill="#4a6a86"/>
  <path d="M 40,150 C 60,124 108,108 172,106 C 224,104 266,112 300,124
           C 316,130 322,138 318,148 C 314,158 300,164 284,168
           C 240,178 180,186 120,182 C 80,178 52,166 40,150 Z" fill="url(#body)"/>
  <path d="M 300,124 C 318,126 336,132 350,140 C 336,150 316,154 296,152
           C 306,144 306,132 300,124 Z" fill="#8fb0c6"/>
  <path d="M 226,110 C 236,92 254,80 268,80 C 254,92 246,102 244,112 Z" fill="#5b7f9e"/>
  <path d="M 240,178 C 232,194 216,206 204,208 C 218,196 226,186 230,176 Z" fill="#5b7f9e"/>
  <path d="M 96,166 C 140,180 208,180 258,170 C 220,182 140,186 100,176 Z" fill="#c9dbe6" opacity=".7"/>
  <circle cx="330" cy="141" r="3" fill="#0a2b46"/>
""" + FOOTER

# ---------------- Spinner dolphin ----------------
FILES["spinner-dolphin.svg"] = HEADER.format(
    label="Spinner dolphin illustration", c1="#8fb0c6", c2="#567a95"
) + f"""
  <path d="M 48,150 L 14,122 L 34,150 L 14,178 Z" fill="#567a95"/>
  <path d="M 38,150 C 58,128 102,114 162,112 C 210,110 250,118 282,130
           C 298,136 304,143 300,152 C 296,161 282,167 264,170
           C 220,178 160,184 108,180 C 72,176 48,164 38,150 Z" fill="url(#body)"/>
  <path d="M 282,130 C 302,132 322,138 338,146 C 322,156 300,160 278,158
           C 288,150 288,140 282,130 Z" fill="#a3c1d3"/>
  <path d="M 210,116 C 220,96 240,82 256,80 C 240,92 230,104 228,118 Z" fill="#5b7f9e"/>
  <path d="M 228,172 C 220,188 204,200 192,202 C 208,190 216,180 218,168 Z" fill="#5b7f9e"/>
  <path d="M 92,166 C 130,178 194,178 240,168 C 206,180 132,182 96,174 Z" fill="#d5e5ee" opacity=".75"/>
  <circle cx="316" cy="147" r="2.8" fill="#0a2b46"/>
""" + FOOTER

# ---------------- logo ----------------
LOGO_DIR = r"C:\Users\Deepak Sagar\OneDrive\Desktop\MoveOne\whale-dolphin-conservation\website\assets"
os.makedirs(OUT, exist_ok=True)
os.makedirs(LOGO_DIR, exist_ok=True)

for name, content in FILES.items():
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", name)

# whale-and-dolphin mark: dolphin arc over a whale
LOGO = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" role="img" aria-label="Whale and Dolphin Conservation">
  <path d="M8 30c0-5.4 4.4-9.8 10-9.8 3.3 0 6.2 1.6 8 4.1 1.8-2.5 4.7-4.1 8-4.1 5.6 0 10 4.4 10 9.8 0 2.6-2 4.6-4.6 4.6H12.6A4.6 4.6 0 0 1 8 30Z" fill="#ffffff" opacity=".95"/>
  <path d="M8 30 2.5 23.5 5 30l-2.5 6.5Z" fill="#ffffff" opacity=".95"/>
  <circle cx="31.5" cy="27.5" r="1.6" fill="#17a2b8"/>
  <path d="M14 20.5c1.6-4.4 5.4-7.5 10-7.5 3.6 0 6.9 1.9 8.8 4.8-2.1-.8-4.4-1.2-6.8-1.2-4.6 0-8.8 1.6-12 3.9Z" fill="#2dd4bf"/>
  <path d="M24.5 13c4.6 0 8.6 1.2 12.6 3.4" stroke="#2dd4bf" stroke-width="1.8" stroke-linecap="round" fill="none"/>
  <path d="M14 20.5c1.6-4.4 5.4-7.5 10-7.5 3.6 0 6.9 1.9 8.8 4.8-2.1-.8-4.4-1.2-6.8-1.2-4.6 0-8.8 1.6-12 3.9Z" fill="#2dd4bf" opacity=".25"/>
</svg>
"""
with open(os.path.join(LOGO_DIR, "logo.svg"), "w", encoding="utf-8") as f:
    f.write(LOGO)
print("wrote logo.svg")
