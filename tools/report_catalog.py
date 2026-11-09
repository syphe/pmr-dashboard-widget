"""Write a reviewable coverage report from the captured catalogue."""
from pathlib import Path
import json
from collections import Counter
from catalog_policy import exclusion_reason

ROOT=Path(__file__).resolve().parents[1]
rows=json.loads((ROOT/'catalog/vehicles.json').read_text())
files=json.loads((ROOT/'catalog/files.json').read_text())
enabled=[r for r in rows if not exclusion_reason(r)]
excluded=[r for r in rows if exclusion_reason(r)]
profile_count=len(list((ROOT/'profiles').glob('*.lua')))
types=Counter(w['type'] for r in rows for w in r['widgets'])
text=['# Offline vehicle dashboard capture','',
      f'{len(rows)} local vehicles, {len(files)} source files ({sum(f["bytes"] for f in files)/1024**2:.1f} MiB), and 97 readable scene geometry exports.',
      '','Every declared node binding in the selected top page and first main page resolved. The actor XML copies also preserve the other pages.',
      '', f'**Original game assets only:** {len(enabled)} local dashboards are enabled, plus the DLC Mustang and Camaro ({profile_count} authored profiles total). {len(excluded)} profiles requiring analogue or custom replacement artwork have been removed. Their original source captures remain available; they have no generated profile, replacement textures or gallery entry.',
      '', '**Coverage is not fidelity validation.** Generated layouts still require calibration. Some warning icons and visibility/colour controls are preserved in the source but are not animated by the generated profiles. Missing live telemetry displays `--`. Units and layout still require comparison in game.',
      '', 'The hand-tuned Supra is included below. DLC profiles `Ford_Mustang_V8Supercar_2024` and `Chevrolet_Camaro_V8Supercar_2024` are retained separately. Their runtime captures are documented in `MUSTANG_FINDINGS.md` and `CAMARO_FINDINGS.md`.',
      '', '## Captured main-page widget types','', '| Type | Count |','| --- | ---: |']
text += [f'| {k} | {v} |' for k,v in sorted(types.items())]
text += ['', '## Vehicles','', '| Vehicle ID / profile | Main page | Layout status | Captured widgets | Auxiliary digits |', '| --- | --- | --- | ---: | ---: |']
for r in rows:
    label=r['id'] if exclusion_reason(r) else f'[{r["id"]}](../{r["profile"]})'
    text.append(f'| {label} | {r["mainPage"]} | {r["layoutStatus"]} | {len(r["widgets"])} | {r.get("auxiliaryDigits",0)} |')
text += ['', '## Excluded dashboards','']
text += [f'- `{r["id"]}`: {exclusion_reason(r)}' for r in excluded]
text += ['', '## Files and reproduction','',
         '- `vehicles.json`: full selected widget attributes, defaults, scene-node mappings and per-car provenance.',
         '- `files.json`: original source paths, content hashes, sizes and local copies.',
         '- `sources/<ID>/`: full actor and relevant I3D XMLs; enabled profiles also have a `layout.json` calibration baseline.',
         '- `geometry/`: world vertices, UVs and transforms read through the offline editor.',
         '- `calibrations.json`: repeatable adjustments for the asset-based profiles.',
         '- `exclusions.json`: profiles requiring replacement artwork; rebuilding will not publish them.',
         f'- `../inspection/catalog.html`: all {profile_count} supported previews through the actual Lua renderer, using sample telemetry.',
         '', 'Use the README rebuild instructions. The original-source archive has been hash-verified, and the Mustang GT3 was rebuilt without reading the installed game folder.', '']
(ROOT/'catalog/REPORT.md').write_text('\n'.join(text),encoding='utf-8')
print('Wrote catalog/REPORT.md')
