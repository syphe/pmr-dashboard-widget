"""Write a local research report alongside the portable-bundle coverage report."""
from pathlib import Path
import json
from collections import Counter
from profile_coverage import audit,main as coverage_report

ROOT=Path(__file__).resolve().parents[1]


def main():
    coverage_report()
    coverage=audit()
    source=ROOT/'catalog/vehicles.json'
    rows=json.loads(source.read_text()) if source.exists() else []
    active=[r for r in coverage if r['active']]
    counts=Counter(r['status'] for r in active)
    text=['# Dashboard source capture','',
          f'{len(active)} active official vehicles: {counts["profile"]} digital profiles and '
          f'{counts["excluded-analogue"]} analogue exclusions. '
          'See [PROFILE_COVERAGE.md](PROFILE_COVERAGE.md) for every vehicle and '
          '`profile-coverage.json` for each profile\'s actual runtime asset references.','',
          'Coverage is not fidelity validation. Imported telemetry bindings come from the '
          'selected top page and first main page. Readable base-game meshes provide UV mappings; '
          'packaged DLC meshes provided mounted bounding spheres but no readable vertex/UV arrays. '
          'New profiles have explicit artwork-based anchors and sizes in `calibrations.json`, '
          'reviewed using sample telemetry. They still need comparison in each live car. '
          'Some warning/colour/visibility controls are not animated; missing telemetry displays `--`.','',
          'The hand-tuned Supra and DLC V8 Supercars are preserved. Their live checks are '
          'documented separately in the findings files. Analogue clusters have no runtime profiles '
          'or prepared assets. Mixed cockpits use only their genuine digital screens.','',
          '## Locally imported source records','',
          'This table includes available importer records, not every raw catalogue capture. '
          'The live catalogue and coverage report are the complete official vehicle lists.','',
          '| Vehicle ID | Main page | Layout status | Source widgets |',
          '| --- | --- | --- | ---: |']
    for r in rows:
        text.append(f'| `{r["id"]}` | {r["mainPage"]} | {r["layoutStatus"]} | {len(r["widgets"])} |')
    text+=['','## Development inputs','',
           '- `catalog/vehicles.json` and `catalog/sources/`: selected widgets, defaults, transforms and original layout baselines.',
           '- `catalog/geometry/`: editor mesh/UV exports where readable; transform-only exports do not supply UVs.',
           '- `inspection/live-catalog/`: mounted-resource capture, provenance/hashes and bounded scene-sphere captures.',
           '- `catalog/calibrations.json`: repeatable per-vehicle digit anchors, sizes and panel crop overrides.',
           '- `inspection/catalog.html`: all enabled profiles through the actual Lua renderer with sample telemetry.',
           '', 'These research inputs are ignored. Prepared runtime assets and profiles are bundled; users need no importer or setup script.','']
    (ROOT/'catalog/REPORT.md').write_text('\n'.join(text),encoding='utf-8')
    print('Wrote catalog/REPORT.md')


if __name__=='__main__':main()
