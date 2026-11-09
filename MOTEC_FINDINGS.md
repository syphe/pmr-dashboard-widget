# Motec dashboard widget investigation

**Implementation update:** The Supra main page has now been recreated as a 2D
widget and verified in game. See [README.md](README.md) for use, tuning and limits.
The investigation below records the earlier camera-portal research.

Inspected 9 November 2026 in the connected PMR session. Raw, filtered evidence:
[inspection/motec-runtime.txt](inspection/motec-runtime.txt). `script.lua` and
`dashboard_widget.lua` were not changed. No functional portal was installed.

## Result

A dashboard that changes with the player's car is feasible as a **2D recreation**
using loaded Motec metadata and original assets. A **literal live view of the
existing 3D dashboard is not established**: every camera-overlay allocation tested
returned `0`, including the controlled test with the renderer ready. Do not build
the widget around `createRenderOverlay` until a working PMR invocation is found.
The failures do not prove every native or future engine route is impossible.

## How the actual dashboard works

The supplied V8 Supra actor uses the stock
`$data/vehicles/Toyota_Supra_GT4/Toyota_Supra_GT4_Evo.i3d`. That model references
`Toyota_Supra_GT4_Evo_Display.i3d`, separately from the cockpit model.
The display contains page meshes, digit anchors, lamps and a `Display Cam`.

The actor XML defines bindings, data sources, formatting, thresholds and pages.
It does **not** supply a complete 2D layout. Digit positions/scales are in the
I3D scene; page backgrounds and masks are textures; gauges use
`data/shaders/str4_MotecShader.xml`. Digits use `alphabetShader.xml` and the DDU10
font atlas. A background texture alone omits dynamic digits, gauges and lamps.

The running car was the **stock GR Supra GT4 Evo**, not the V8 mod. Its actor
component was available at:

```lua
local actor = g_racingManager.playerVehicleData.vehicleActor
local motec = actor.components.motec
```

Confirmed loaded fields:

| Object | Useful fields |
| --- | --- |
| Motec component | `componentType`, `ref`, `masterPage`, `pages`, `currentPage`, `popups`, `activePopup`, `flagPopups`, `popupparent` |
| Page | `name`, `pageNode`, `widgets`, `defaultPaletteBindingId` |
| Digit widget | `node`, `nodeName`, `fontName`, `fontMaterial`, `characterLine`, `vehicleParam`, `previousText`, `updateText`, `updateColour`, `numChars`, `align` |
| Palette gauge | `pageSpecificBindings`, `shaderParameter`, `minValue`, `maxValue`, thresholds and colours |
| Shift light | `node`, colour/threshold fields, `previousColour`, `previousEmissive` |

For example, the loaded gear widget had `fontName="DDU10"`, `previousText="N"`
and `updateText="N"`. `characterLine` exposes character instances, text size,
alignment and colour. Its font object exposes character mappings and spacing.
These are inspected fields, not a validated general-purpose 2D font API.

`currentPage=1` coexisted with `activePopup="Limiter"` and hidden Page1 geometry.
Selecting only `pages[currentPage]` would therefore miss the visible popup.
The display's `interior` ancestor was also hidden in the pre-drive menu.

There was no discovered Motec `draw()` method or final-display overlay ID.
`MotecWidget*` classes update scene objects; they are not `GuiElement` widgets.

## Camera rendering tests

Tracing PMR's actual `RenderElement.createOverlay` with intercepted calls showed
12 arguments beginning with **camera**, followed by aspect, pixel width/height,
alpha, shape/light masks and quality flags. The interception was restored before
the query returned. The trace deliberately returned `0`; its logged allocation
error was expected and is not evidence of a native allocation failure.

A subsequent native error identified argument 1 as `rootId`, suggesting a mismatch
between bundled Lua and the native engine. The current
[GIANTS RenderElement reference](https://gdn.giants-software.com/documentation_scripting_fs25.php?category=43&class=480&version=engine)
passes scene root **then camera**. That reference informed further tests; it does
not establish PMR support.

Actual native results:

| Test | Result |
| --- | --- |
| Existing display camera, bundled PMR call convention | `0` |
| Isolated cloned display, bundled convention | `0` |
| Bundled convention inside real draw/update callbacks | `0` (see ordering issue below) |
| Explicit root + camera, hidden cloned display | `0` |
| Explicit root + camera, visible cloned display, alpha off | `0` |
| Explicit world root + original display camera | `0` |
| Image overlay control, same native update as the final three tests | `464102` |
| `g_rendererReady` and `isRendererReady()` | both `true` |

The final rooted tests used a 512 x 256 target and the documented 14-argument
convention. Code is retained in
[inspection/portal-final-probe.lua](inspection/portal-final-probe.lua).
Image allocation succeeded; final visual image output was not tested.
No camera target was created, so no portal pixels or live page rendering could
be validated. No driving or car-switch visual test was performed.

One earlier one-shot callback deleted its clone in draw before update used it,
causing an unknown-entity error and debugger stop. Execution was resumed; that
probe was removed. The final controlled probe has only an update callback and
cleans up sequentially. Cleanup verification reported original update/draw
callbacks restored, and checked earlier owned entities no longer existed.

PMR-specific `setVirtualRearViewMirrorOverlay*` functions and actor mirror
viewport methods exist. No general-purpose viewport constructor was discovered.
Their signatures/behaviour remain untested; they are not a confirmed alternative
and may interfere with the stock virtual mirror.

## Integration approach if a 2D recreation is acceptable

1. Resolve the player's actor each update. Scan `actor.components` for
   `componentType == "MotecComponent"`; do not assume every component is named
   `motec`. Rebind on actor/component replacement, including session changes.
2. Resolve the active page, popup and always-on widgets from the loaded component.
   Read the stock widget's prepared values/colours after stock updates where
   possible. Treat these fields as optional because other widget types differ.
3. Supply display profiles (or an asset conversion step) mapping mesh anchors,
   backgrounds, masks and font atlas glyphs into widget coordinates. Reproduce
   supported gauge/lamp types using 2D drawing. This is the substantial missing
   work; XML bindings alone cannot draw the original appearance automatically.
4. Register matching containers in the HUD and placement editor using CustomHud's
   `hud_widget.lua` pattern. Draw in `draw()`, use absolute normalized bounds,
   preserve physical aspect, and apply the pause/menu/session-finished guards
   from `hud.lua`. Cache overlays and release owned resources on rebind/unload.
5. Validate one Supra profile visually, then a different display family and an
   actual car/session change before claiming generic support.

Static inspection found 70 stock actor files with Motec components; their default
fonts differ (DDU10, DDU9, Marelli, genuine Motec, Arial, dot-matrix and others),
and some omit a default font. Display cameras are not uniformly named or present.
A universal camera-name or font assumption would not cover the available cars.

For another read-only runtime inventory, use
[inspection/motec-probe.lua](inspection/motec-probe.lua). `source()` cached an
already-loaded filename in this session; use the IDE's script reload to execute
an edited version. All experimental draw/update wrappers were removed. No stock
vehicle assets, saved widget placements, or gameplay settings were edited.
