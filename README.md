# PMR dashboard widget

Dashboard profiles select by exact vehicle ID, including separate Mustang GT3,
GT4 and V8 Supercar dashboards. There are 56 supported local digital panels plus
optional DLC Mustang and Camaro profiles. Analogue recreations and replacement artwork
are excluded. The Corvette C5R and MX-5 use their original digital panels only.

**Game artwork is not distributed with this repository.** Each user prepares
textures, fonts and shader-mask atlases from their own installation. The game
and GIANTS Editor can both be closed during setup.

## Set up local assets

Install Python and the build dependencies, then run:

```powershell
python -m pip install --target .tools/python -r requirements-dev.txt
python tools/setup_assets.py
```

The script finds PMR through Steam, including secondary Steam libraries. To
select an installation explicitly:

```powershell
python tools/setup_assets.py --game "D:/SteamLibrary/steamapps/common/Project Motor Racing"
```

`PMR_INSTALL_DIR` is also supported. The source installation is read only. Setup
reads the original main-page materials and fonts, converts overlays locally, and
validates texture dimensions and gauge mappings against the authored profiles.
It does not require copied actor XMLs, an asset archive or editor geometry exports
from another computer, and does not overwrite the profile code.

Generated files go into `assets/`. `assets/setup-report.json` lists prepared and
skipped cars. A car missing from the local installation, or whose artwork no
longer matches its profile, is skipped with a reason. No replacement dashboard
is generated. Use `--vehicle Ford_Mustang_GT3_2023` to prepare only one profile;
this replaces the available-profile list until setup is rerun for all cars.

## Run

Use the generated **`local_bootstrap.lua`** as the game startup script. It supplies
the absolute path to this checkout, then loads `script.lua` and only those
profiles whose assets were prepared successfully. It is machine-specific and
ignored by Git. Alternatively a mod loader can set `DashboardMod.root` or supply
`g_currentModDirectory` before loading `script.lua`.

The widget ID is `hudDashboard`. It uses the native HUD layout editor for moving
and saving its position, and hides during pause, HUD hiding and finished sessions.
The default width is 32% of the screen. Resource caches and readings are cleared
when the player's car changes. Each dash stays on its first main page regardless
of cockpit page switches or popups. Unsupported/unprepared cars hide the widget.

Restart the game after changing the asset availability list: native `source()`
was observed to cache loaded scripts. The IDE's **FS Lua: Reload Script in Game**
can reload an individual profile and `dashboard_widget.lua` for layout tuning.

## Optional DLC V8 Supercars

The DLC Mustang and Camaro textures are in an encrypted mounted package, so ordinary file
copying cannot prepare those cars. Default setup skips them and still prepares the
loose-file cars. If you have exported the textures locally through your installed
game's mounted-resource API, supply that directory:

```powershell
python tools/setup_assets.py --dlc-export "D:/My local PMR exports"
```

For the Mustang, supply `mustang-background.dds` and `mustang-mask.dds`;
for the Camaro, supply `camaro-background.dds` and `camaro-mask.dds`. Either
pair works independently; both can share the same folder.
[inspection/export-mustang-assets.lua](inspection/export-mustang-assets.lua) and
[inspection/export-camaro-assets.lua](inspection/export-camaro-assets.lua) are
console helpers to obtain these from the owned, mounted car. Load the local
bootstrap first; then run the corresponding helper while driving that car. Their
outputs stay in the ignored `inspection/` directory. Setup also builds the shared
Supra/DDU10 font dependency. It does not decrypt packages or download assets.

## What to commit

Commit authored Lua profiles, renderer code, setup/conversion tools, tests,
`catalog/vehicles.lua`, `catalog/exclusions.json` and `catalog/calibrations.json`.
The following are private local outputs and are ignored:

- `assets/`, including original copies, converted textures and font metadata.
- `catalog/sources/`, `catalog/geometry/`, `catalog/vehicles.json`, `catalog/files.json`
  and the generated capture report.
- Inspection images, previews, runtime dumps and resource lists.
- `local_bootstrap.lua`, `.tools/` and generated editor job lists.

Before committing, check the Git index:

```powershell
python tools/check_repo_assets.py
```

Ignoring files does not remove copies already present in earlier commits. This
change removes them from current tracking; existing Git history is not rewritten.

## Tune a profile

Profiles are named `profiles/<vehicle ID>.lua`. They contain bindings, positions,
formatting, colour thresholds and references to locally generated artwork.
Coordinates use each original texture's top-left origin; the renderer handles
cropping, normalized screen coordinates and aspect ratio.

```lua
{id='pressureFL', param='wheel1.tyre_pressure', x=199,y=420,height=25,
 align='right', dx=0,dy=0, scale=.00001,offset=0, format='%.2f'}
```

Bindings support `param`, `method` or `constant`; conversions support `scale`,
`offset` and an optional Lua `convert` function. `widthScale`, `heightScale`,
`dx` and `dy` tune individual readouts. Formatting supports numeric formats, gear
and lap-time values. Missing/invalid telemetry displays `--`. Known pressure
bindings convert Pa to bar, speed uses `getForwardSpeedKPH()`, and lap-time objects
use `timeSeconds`. Units outside the previously checked getters need verification.

Most profiles are experimental projections and still need visual calibration and
live comparisons. Some warning icons and colour/visibility controls have not yet
been animated. The Supra and DLC Mustang have earlier in-game checks documented
in [MOTEC_FINDINGS.md](MOTEC_FINDINGS.md) and [MUSTANG_FINDINGS.md](MUSTANG_FINDINGS.md).
The Camaro's capture and in-game check are documented in
[CAMARO_FINDINGS.md](CAMARO_FINDINGS.md). Those checks do not validate every
generated profile.

## Checks and previews

```powershell
python tests/test_dashboard.py
python tests/test_asset_setup.py
python tests/test_catalog.py
python tools/preview_catalog.py
```

The behavior tests use metadata-only fixtures and do not require game artwork.
Setup tests check Steam discovery and, when PMR is installed, build and load a
clean checkout containing authored files only. Catalogue checks and previews
require local asset setup. The generated gallery is `inspection/catalog.html`.

## Optional development capture

The original research tools remain available for developing additional mappings.
`tools/vehicle_catalog.py` captures local main-page definitions and source assets;
`tools/editor_geometry_export.lua` exports vertices/UVs through the installed PMR
GIANTS Editor. All copied source data and geometry stay in ignored directories.
After a local capture, `tools/refine_catalog.py` applies field adjustments from
`catalog/calibrations.json` and `tools/report_catalog.py` generates a capture report.
These development captures are not a prerequisite for end-user asset setup.
