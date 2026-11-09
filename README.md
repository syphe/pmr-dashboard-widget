# PMR dashboard widget

58 dashboard profiles select automatically by exact vehicle ID, including the
DLC AUS V8 Evo Mustang and Camaro. Textures, fonts, gauge atlases and runtime
metadata are included in `assets/`. No asset setup, Python installation, DLC
export or debugger is needed to use the widget.

Analogue recreations and replacement artwork remain excluded. The Corvette C5R
and MX-5 use their original digital panels only.

## Run

Download or clone the repository and keep its folders together. Set PMR's startup
script to the absolute path of **`script.lua`**. For example, in Steam's launch
options:

```text
-script "D:/Mods/pmr-dashboard-widget/script.lua"
```

The script discovers its own directory. A mod loader can instead supply
`g_currentModDirectory` or set `DashboardMod.root` before loading it. An existing
`local_bootstrap.lua` still works, but is no longer needed or generated.

Enter a driving session in a supported car. The widget selects its main-page
profile automatically, including the two supported DLC cars. Other DLC cars
still need their own profiles and assets.

The widget ID is `hudDashboard`. Use the native HUD layout editor to move it and
save its position. Its default width is 32% of the screen. It hides during pause,
HUD hiding and finished sessions. Resources and readings clear when the car
changes. Each dash stays on its first main page, independently of cockpit page
switches or popups. Unsupported cars hide the widget.

Restart PMR after changing startup files: native `source()` was observed to cache
loaded scripts. The IDE's **FS Lua: Reload Script in Game** remains useful for
optional development and tuning.

## Repository contents

Commit the runtime `assets/` textures and metadata alongside profiles, renderer
code, tools and tests. Source archives (`assets/library/`, `catalog/sources/`,
`catalog/geometry/`), inspection images/dumps, generated capture reports and
machine-specific legacy setup files stay ignored. The old per-install setup
script and asset availability manifest are no longer part of the runtime.

`python tools/check_repo_assets.py` checks that runtime assets are tracked and
local research files are excluded.

## Tune a profile

Profiles are named `profiles/<vehicle ID>.lua`. They define telemetry bindings,
positions, formatting, colour thresholds and references to bundled artwork.
Coordinates use the original texture's top-left origin; the renderer handles
cropping, normalized screen coordinates and aspect ratio.

```lua
{id='pressureFL', param='wheel1.tyre_pressure', x=199,y=420,height=25,
 align='right', dx=0,dy=0, scale=.00001,offset=0, format='%.2f'}
```

Bindings support `param`, `method` or `constant`; conversions support `scale`,
`offset` and an optional Lua `convert` function. `widthScale`, `heightScale`,
`dx` and `dy` tune individual readouts. Formatting supports numeric formats, gear
and lap times. Missing/invalid telemetry displays `--`. Pressure converts Pa to
bar, speed uses `getForwardSpeedKPH()`, and lap times use `timeSeconds`.

Most imported profiles still need visual calibration. Some warning icons and
colour/visibility controls have not been animated. The earlier in-game checks
are documented in [MOTEC_FINDINGS.md](MOTEC_FINDINGS.md),
[MUSTANG_FINDINGS.md](MUSTANG_FINDINGS.md) and
[CAMARO_FINDINGS.md](CAMARO_FINDINGS.md); they do not validate every profile.

## Development checks and previews

Python is only needed for development:

```powershell
python -m pip install --target .tools/python -r requirements-dev.txt
python tests/test_dashboard.py
python tests/test_bundle.py
python tests/test_catalog.py
python tools/check_repo_assets.py
python tools/preview_catalog.py
```

The portable-bundle test loads all profiles without a game installation, setup
scripts, source archives or generated bootstrap. It checks standard Lua and
PMR-style source-path discovery, mod-loader paths and script reloads. Catalogue
checks exercise every profile's asset references and draw path. The preview
gallery is generated at `inspection/catalog.html` and stays ignored.

The optional research/conversion tools remain for adding or updating dashboards.
`tools/vehicle_catalog.py` captures loose-file main-page definitions and assets;
`tools/editor_geometry_export.lua` exports mesh vertices/UVs through GIANTS Editor.
`tools/prepare_supra.py` and `tools/prepare_v8_supercar.py` rebuild the hand-tuned
textures. DLC export helpers in `inspection/` support development recaptures.
`tools/refine_catalog.py` applies `catalog/calibrations.json` adjustments, and
`tools/report_catalog.py` generates a capture report. None of these tools needs
to run before using the bundled widget.
