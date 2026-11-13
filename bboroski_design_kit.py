"""Generate and validate the BBOROSKI design kit for this repository."""
import json
import pathlib
import html
import zipfile
import xml.etree.ElementTree as ET

CONFIG = {"id":"sambu","name":"SAMBU","tag":"Scientific Modeling & Automation Environment","language":"Python · C11","motif":"voxel","radius":12,"grid":8,"colors":{"canvas":"#070B12","surface":"#0E1524","raised":"#16203A","edge":"#26365C","text":"#EAF1FF","muted":"#93A6C8","accent":"#3DDCFF","accent2":"#7C5CFF","third":"#37E0A0","ok":"#4ADE80","warn":"#FFC24B","danger":"#FF5A5A","info":"#63B3FF"}}
ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "design-kit"

def svg_mark():
    c = CONFIG["colors"]
    name = html.escape(CONFIG["name"])
    motif = html.escape(CONFIG["motif"])
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" role="img" aria-labelledby="title">
<title id="title">{name} — {motif}</title>
<defs><linearGradient id="accent" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="{c["accent"]}"/><stop offset="1" stop-color="{c["accent2"]}"/>
</linearGradient></defs>
<rect width="256" height="256" rx="{CONFIG["radius"]*2}" fill="{c["canvas"]}"/>
<rect x="1" y="1" width="254" height="254" rx="{CONFIG["radius"]*2}" fill="none" stroke="{c["edge"]}" stroke-width="2"/>
<circle cx="128" cy="128" r="76" fill="none" stroke="url(#accent)" stroke-width="8"/>
<path d="M128 48V208M48 128H208M72 72L184 184M184 72L72 184" stroke="{c["third"]}" stroke-width="3" opacity=".8"/>
<rect x="108" y="108" width="40" height="40" rx="6" fill="{c["accent"]}"/>
</svg>'''

def main():
    c = CONFIG["colors"]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "assets").mkdir(exist_ok=True)
    (OUT / "tokens").mkdir(exist_ok=True)
    mark = svg_mark()
    (OUT / "assets" / "mark.svg").write_text(mark, encoding="utf-8")
    banner = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 320">
<rect width="1280" height="320" fill="{c["canvas"]}"/>
<rect width="1280" height="4" fill="{c["accent"]}"/>
<text x="64" y="140" font-family="Inter, sans-serif" font-size="58" font-weight="800" fill="{c["text"]}">{html.escape(CONFIG["name"])}</text>
<text x="66" y="190" font-family="Inter, sans-serif" font-size="24" fill="{c["muted"]}">{html.escape(CONFIG["tag"])}</text>
<text x="66" y="260" font-family="monospace" font-size="17" fill="{c["accent"]}">{html.escape(CONFIG["language"])} · BBOROSKI DESIGN KIT</text>
</svg>'''
    (OUT / "assets" / "banner.svg").write_text(banner, encoding="utf-8")
    tokens = {
        "schema_version": "1.0.0",
        "design_system": "BBOROSKI/" + CONFIG["name"].upper(),
        "repository": CONFIG["name"],
        "colors": c,
        "geometry": {"grid_unit_px": CONFIG["grid"], "panel_radius_px": CONFIG["radius"], "silhouette": CONFIG["motif"]},
        "motion": {"state_transition_ms": [120, 240], "reduced_motion": "disable nonessential motion"},
        "accessibility": {"minimum_control_height_px": 40, "normal_text_contrast_ratio": 4.5, "keyboard_focus_visible": True},
        "evidence_states": ["VERIFIED", "PARTIAL", "PLANNED", "UNKNOWN", "NOT TESTED", "BLOCKED"]
    }
    (OUT / "tokens" / "tokens.json").write_text(json.dumps(tokens, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    css = f''':root[data-repo="{CONFIG["id"]}"]{{--canvas:{c["canvas"]};--surface:{c["surface"]};--raised:{c["raised"]};--edge:{c["edge"]};--text:{c["text"]};--muted:{c["muted"]};--accent:{c["accent"]};--accent-2:{c["accent2"]};--third:{c["third"]};--radius:{CONFIG["radius"]}px;--grid:{CONFIG["grid"]}px}}
[data-repo="{CONFIG["id"]}"] .panel{{background:var(--surface);border:1px solid var(--edge);border-radius:var(--radius)}}
[data-repo="{CONFIG["id"]}"] .btn-primary{{background:var(--accent);color:var(--canvas);border:0;min-height:40px;font-weight:650}}
[data-repo="{CONFIG["id"]}"] :focus-visible{{outline:2px solid var(--accent);outline-offset:2px}}
@media(prefers-reduced-motion:reduce){{[data-repo="{CONFIG["id"]}"] *{{animation:none!important;transition:none!important}}}}
'''
    (OUT / "tokens" / "tokens.css").write_text(css, encoding="utf-8")
    readme = f"""# {CONFIG["name"]} Design Kit

{CONFIG["tag"]}

- Motif: `{CONFIG["motif"]}`
- Accent: `{c["accent"]}`
- Grid: {CONFIG["grid"]} px
- Panel radius: {CONFIG["radius"]} px

Use `assets/mark.svg`, `assets/banner.svg`, `tokens/tokens.json` and `tokens/tokens.css`.
Evidence must be labelled VERIFIED, PARTIAL, PLANNED, UNKNOWN, NOT TESTED or BLOCKED.
"""
    (OUT / "README.md").write_text(readme, encoding="utf-8")
    for f in (OUT / "assets").glob("*.svg"):
        ET.parse(f)
    with zipfile.ZipFile(ROOT / "bboroski-design-kit.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(OUT.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(ROOT))
    print(f'{CONFIG["name"]}: SVG/XML valid; tokens and CSS generated; ZIP ready')

if __name__ == "__main__":
    main()
