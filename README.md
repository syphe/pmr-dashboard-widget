# PMR dashboard widget

81 dashboard profiles select automatically by exact vehicle ID, covering all
active digital dashboards in the captured base-game and DLC catalogue. Textures, fonts, gauge atlases and runtime
metadata are included in `assets/`. No asset setup, Python installation, DLC
export or debugger is needed to use the widget.

31 analogue clusters remain excluded. The Corvette C5R, MX-5 and TA2 Camaro
use their original digital panels only. See the per-vehicle
[coverage report](catalog/PROFILE_COVERAGE.md), including inactive entries.

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
profile automatically. Each DLC variant has its own exact vehicle-ID profile.

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

The Audi R8 LMS GT3 Evo uses `textBounds` to fit long readings within their boxes
and `paletteControls` to recolour original shader-mask regions from live tyre
temperatures, pressures, fuel and engine temperature. It shows green `0.00`
before a valid best lap. Reproduce the prepared palette and calibration with
`python tools/calibrate_audi.py`; it prints a cache-safe live reload command that
retains the HUD placement. See [AUDI_FINDINGS.md](AUDI_FINDINGS.md).

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
colour/visibility controls have not been animated. New DLC profiles marked
`asset-calibrated-unverified` use digit anchors and sizes adjusted against their
original artwork in sample previews. Their initial projection used mounted bounds
because DLC screen UVs could not be exported. They still need comparison in each
live car. The earlier in-game checks
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
python tests/test_live_catalog.py
python tests/test_runtime_audit.py
python tests/test_audi.py
python tools/profile_coverage.py
python tools/check_repo_assets.py
python tools/preview_catalog.py
```

The portable-bundle test loads all profiles without a game installation, setup
scripts, source archives or generated bootstrap. It checks standard Lua and
PMR-style source-path discovery, mod-loader paths and script reloads. Catalogue
checks exercise every profile's asset references and draw path. The preview
gallery is generated at `inspection/catalog.html` and stays ignored.

## Runtime audit before hand tuning

The gallery now separates **capture method**, **calibration** and **live validation**.
`generated` and `preview-calibrated` describe visual work; `hand-tuned` remains
independent of the fresh runtime audit. All 81 supported digital dashboards passed
mounted source/scene checks. The Audi R8 LMS GT3 Evo also has a live Motec audit;
other cars remain `pending-runtime-audit` until loaded and captured.

[RUNTIME_AUDIT.md](catalog/RUNTIME_AUDIT.md) lists the results and findings.
`runtime-audited` checks actual main/top-page widgets, resolved nodes, fonts,
alignment, configured thresholds and available telemetry/conversions. It does
not verify pixel accuracy, every warning transition or a completed lap. Cosmetic
formatting differences and unavailable valid samples remain notes; substantial
numeric/unit differences require review. Changing a profile invalidates its audit
until fresh evidence matches its file hash.

The optional recorder is a developer tool. Normal startup through `script.lua`
never enables it and still needs no setup or Python. To prepare an audit using the
local source capture:

```powershell
python tools/runtime_audit.py prepare
```

Run the printed cache-safe `source(...)` command through the connected game
console. It captures the current car and then captures each new player actor as
you load cars, preserving cockpit pages and gameplay state. Run these bounded
scene batches once for the prepared 81-profile plan:

```lua
DashboardRuntimeAudit:runScenes(1,40)
DashboardRuntimeAudit:runScenes(41,81)
```

Prepared jobs skip inactive and modded cars. Scene inspection loads unlinked
meshes without physics/onCreate callbacks and deletes them afterward. A scene
pass alone never awards `runtime-audited`. Raw captures stay under the ignored
`inspection/runtime-audit/` directory; only the portable summary is tracked.

To import captures and refresh gallery badges automatically for one hour:

```powershell
python tools/runtime_audit.py watch --seconds 3600
```

For a single refresh, run `python tools/runtime_audit.py ingest`,
`python tools/profile_coverage.py`, and
`python tools/preview_catalog.py --gallery-only`. After changing profile files,
prepare and load a fresh plan. Full preview rendering is needed after visual or
binding changes; badge-only refreshes reuse existing sample images.

The recorder stops with `DashboardRuntimeAudit:stop()` or a game restart.
An already loaded car can be recaptured with `DashboardRuntimeAudit:captureCurrent()`.
The watcher stops after its time limit, with Ctrl+C in its terminal, or when
`inspection/runtime-audit/stop-watch` exists. For an optional audit session
without a debugger, launch PMR with `-script "<repo>/inspection/audit-startup.lua"`
after preparing jobs; normal sessions should keep the usual `script.lua` entry.

The initial audit confirmed that fuel/oil pressure needs Pa-to-bar conversion
with Motec's override enabled. That conversion is now included in 35 affected
profiles and their generators.

The optional research/conversion tools remain for adding or updating dashboards.
`tools/vehicle_catalog.py` captures loose-file main-page definitions and assets;
`tools/editor_geometry_export.lua` exports mesh vertices/UVs through GIANTS Editor.
`tools/prepare_supra.py` and `tools/prepare_v8_supercar.py` rebuild the hand-tuned
textures. DLC export helpers in `inspection/` support development recaptures.
`tools/refine_catalog.py` applies `catalog/calibrations.json` adjustments, and
`tools/report_catalog.py` generates a capture report. None of these tools needs
to run before using the bundled widget.

`tools/build_active_profiles.py build` imports missing active digital profiles
from an existing mounted-resource capture, retaining existing tuned profiles.
For development, its `geometry` action prepares stripped scenes for the editor;
when packaged shapes have no readable UVs, `bounds` prepares a bounded game-side
capture for `inspection/capture-dashboard-bounds.lua`. These helpers load and
delete unlinked dashboard meshes without physics or actor callbacks. They do not
switch cars or change availability. The resulting captures stay ignored.
Use `python tools/refine_catalog.py --vehicle <ID>` to reapply an individual
profile's saved artwork calibration without regenerating textures.

## Live vehicle catalogue and capture

[catalog/GAME_VEHICLES.md](catalog/GAME_VEHICLES.md) lists the live catalogue,
including DLC and inactive entries. Vehicle mods and custom liveries are excluded.
The same records are available as
[CSV](catalog/game-vehicles.csv) and [JSON](catalog/game-vehicles.json).

Raw live captures are in the ignored `inspection/live-catalog/` directory:
vehicle/actor XML, scene definitions, dashboard textures, fonts and mesh binaries,
plus source paths and content hashes. They are research inputs for future
profiles; the bundled runtime assets are unchanged by a capture.

The developer helpers `inspection/vehicle-catalog-capture.lua` and
`inspection/capture-vehicle-assets.lua` run through the connected game's console.
`tools/live_catalog.py refresh --log <PMR log>` reads their output, `plan` creates
a dependency-copy job list, `verify` checks the saved files, and `report` writes
the catalogue and hashed asset inventory. These are optional research tools.
