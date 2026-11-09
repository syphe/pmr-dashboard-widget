# PMR dashboard widget

Two main-page profiles are implemented: **Toyota GR Supra GT4 Evo** and **AUS V8
Evo Mustang** (`Ford_Mustang_V8Supercar_2024`). They use original display artwork,
DDU10 glyphs and live vehicle bindings. Each always shows Page1 regardless of the
cockpit dash's current page or popup. The Supra model is also used by the
referenced V8 Supra mod.

Other cars hide the widget until they have a profile. The renderer detects the
player's vehicle and discards the previous car's readings/resources on a change.

## Run

Use this repository's `script.lua` as the game script, as with the original
prototype. Its root directory is set near the top of that file. No Python package
is required to run the widget in PMR; the prepared DDS assets are included.

The widget ID remains `hudDashboard`. It registers separate gameplay and HUD
layout-editor containers. Its position can be moved and saved by the game's
layout editor. It hides during pause, stock HUD hiding and completed sessions.
The default width is 32% of the screen, with aspect-correct height.

## Tune a dashboard

Edit [profiles/supra.lua](profiles/supra.lua) or
[profiles/mustang.lua](profiles/mustang.lua). Coordinates refer to each original
1024 x 512 texture with a top-left origin; the renderer handles the cropped
background and the game's bottom-left normalized coordinates. Profiles select
their own assets, lamps and indicators. Reloading one preserves the other.

```lua
{id='pressureFL', param='wheel1.tyre_pressure',
 x=199, y=420, height=25, align='right',
 dx=0, dy=0, widthScale=1, heightScale=1,
 scale=.00001, offset=0, format='%.2f'}
```

| Setting | Effect |
| --- | --- |
| `param` / `method` / `constant` | Named vehicle parameter, actor getter, or fixed label |
| `x`, `y`, `dx`, `dy` | Anchor and additional per-field pixel offsets |
| `height`, `heightScale`, `widthScale` | Digit size and proportions |
| `align` | `left`, `right`, or centred by default |
| `scale`, `offset` | Displayed value = raw value × scale + offset |
| `convert` | Optional `function(value, actor)` after scale/offset |
| `format`, `kind` | Lua numeric format, `time`, or `gear` |
| `color`, `high`, `low` | Normal colour and warning thresholds |

Tyre pressure converts Pa to bar. Speed uses `getForwardSpeedKPH()` and absolute
value to match the km/h label. Temperatures and brake bias use named getters in
their observed Celsius/percentage units. LapTime objects use `timeSeconds`;
invalid best laps and unavailable readings show `--`. Delta uses the live
`lapDelta` parameter and requires a valid best lap. Negative fuel-used readings
during reset/out-lap are hidden. The original `PwrStr` and `Thrtl` entries are
fixed at zero in the actor XML, so those labels retain zero here.

Supra gauges have separate `min`, `max`, colours and warning thresholds. They use
65 cached fill states extracted from the original shader masks. Shift lights
use the current actor's shift-light range. The Mustang uses four recovered shift
thresholds, lock lamps and headlight/wiper icons. The Supra caches six overlays;
the Mustang caches three. Textures are not created per field or per frame.

For code changes, open the changed Lua file and run **FS Lua: Reload Script in
Game** through the GIANTS IDE extension. Reload `dashboard_widget.lua` after
profile changes to apply them immediately. Plain `source()` caches loaded files
in the inspected PMR session; `loadfile()` and `reloadResource()` did not execute
updated Lua as expected. Repeated renderer reloads preserve widget placement and
do not stack update hooks or add duplicate editor entries.

To change the widget's default size/position, edit `mod.config` in
`dashboard_widget.lua`. A persisted game placement takes precedence over defaults.
In a running session, `DashboardMod.config.width = .36` changes the width on the
next update; config is retained across renderer reloads.

## Prepare assets and check locally

The converter reads the installed game under the `DATA` path in
`tools/prepare_supra.py`. It generates the cropped background, gauge frame atlases,
font and metadata. DDS files include BC3 compression and complete mip chains.
The sharp source font lacks the actor's degree symbol; the converter adds that
small glyph to its empty slot.

Mustang textures were read from the running game's mounted DLC resources. See
[MUSTANG_FINDINGS.md](MUSTANG_FINDINGS.md). To refresh them, run
`inspection/export-mustang-assets.lua` through the connected console while in
the Mustang, then run `python tools/prepare_mustang.py`. Prepared assets are
already present for normal use.

```powershell
python -m pip install --target .tools/python -r requirements-dev.txt
python tools/prepare_supra.py
python tests/test_dashboard.py
python tools/preview_supra.py
python tools/preview_supra.py --profile mustang
```

The preview executes the actual Lua drawing functions and writes
[inspection/supra-preview.png](inspection/supra-preview.png).

## Validation

Verified in the running game on 9 November 2026: the final DDS build rendered
60 native draw calls and received 60 native telemetry updates, with exactly one
layout-editor entry. Gear, TC, ABS, tyre pressures and temperatures agreed with
the stock HUD while stationary. Pause hiding was visually checked. Native
evidence is in [inspection/supra-runtime.txt](inspection/supra-runtime.txt).

The Mustang also completed 60 native updates/draws with three overlays and one
editor entry. Its gear, position, lap, engine temperature, brake bias and map were
checked in game. See [inspection/mustang-runtime.txt](inspection/mustang-runtime.txt)
and [inspection/mustang-preview.png](inspection/mustang-preview.png).

Local regression checks cover unit/offset conversion, lap-time objects and
rounding, missing/invalid telemetry, car replacement, update ownership,
registration/reload idempotency, saved placement and pause/finish hiding.
They also cover Mustang asset selection, shared-font lookup, boolean indicators,
session labels, one-decimal timing and independent profile reloads.

A driven lap, physical layout-editor dragging/save, full game restart, and
selection of the V8 mod have not been tested during this implementation. Gauge
fill and shift-light behaviour across the full driving range still need that
comparison. The widget does not switch the cockpit Motec page or modify its data.
