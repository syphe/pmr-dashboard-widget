# DLC Mustang dashboard

Inspected 9 November 2026 through the connected, running game. The car identified
itself as `Ford_Mustang_V8Supercar_2024.i3d` (AUS V8 Evo Mustang).

## Asset source

The earlier Supra conversion read loose DDS files from the installed game.
For the Mustang, material and widget information came from the live actor.
The dashboard background and icon mask were copied through **PMR's mounted
resource API**, using `copyFile()` with their DDS resource names. No external
tool opened, decrypted or unpacked the original package.

The Page1 palette binding `FOR_MUS_V8_DISPLAY1` resolved to a shape with one
material using `data/shaders/str4_MotecShader.xml`. The named maps were:

```text
backgroundMap:
dlcS/s1_dlc3/vehicles/Ford_Mustang_V8Supercar_2024/Textures/t_ford_mustang_supercar_display1_glow.png
maskMap1:
dlcS/s1_dlc3/vehicles/Ford_Mustang_V8Supercar_2024/Textures/t_ford_mustang_supercar_display_mask1.png
```

The material references end in `.png`; the successfully copied resources end in
`.dds`. Both decode as 1024 x 512 RGBA textures. The packaged background also
loaded directly through `Overlay.new()` with nonzero ID `1363689`. A filesystem
lookup for the PNG path failed. This is evidence for these two mounted textures
in this session, not a guarantee that every packaged file can be exported.
No actor XML or model file was successfully copied; neither is needed here.

[inspection/export-mustang-assets.lua](inspection/export-mustang-assets.lua)
contains the bounded export helper. `tools/prepare_mustang.py` copies the
background and converts the two mask icons to a white alpha atlas with mipmaps.
DDU10 is a shared base-game font, reused from the prepared Supra font.

The named-map convention was checked against the
[GIANTS material reference](https://gdn.giants-software.com/documentation_scripting_fs25.php?category=22&function=598&version=engine)
and then verified directly in PMR.

## Main-page bindings

The live component exposes always-on widgets in `masterPage.widgets` and the
main-page widgets in `pages[1].widgets`. Binding/geometry evidence is preserved
in [inspection/mustang-runtime.txt](inspection/mustang-runtime.txt).

| Display element | Confirmed vehicle parameter |
| --- | --- |
| Gear | `gear` |
| Best lap | `bestLap`, native LapTime object; one decimal on this dash |
| Gain/loss | `lapDelta` |
| Position / lap | `pos` / `lap` |
| Engine temperature | `engine_temp`, warning above 115 |
| Brake bias | `brakebias`, one decimal |
| Engine map | `map` |
| Session label | `israce`, `isqualifying`, `ispractice` |
| Headlight / wiper | `lights` / `wiper` |
| Front / rear lock lamps | `frontLocked` / `rearLocked` |
| Four shift lamps | `revs`, thresholds 6000 / 6450 / 6900 / 7350 |

The map getter returned `true, 3`. It is available on this car/build, even though
the earlier Supra survey had not found it. The profile uses original background
and icon art with individually tuned 2D anchors/sizes. Physical lamps are arranged
in the widget's top strip. It always draws Page1 without changing the cockpit page.

## Validation and limits

The profile selected `mustang_v8_evo` automatically. Bounded probes completed
60 native telemetry updates and 60 draws, then restored themselves. There were
three cached overlays (background, font, icons) and one editor entry. The in-game
view showed neutral gear, position 17, lap 0, map 3, brake bias 65.0 and engine
temperature about 108 C. The game was left paused with the widget hidden.

Local checks cover both profiles, asset selection, shared-font lookup, indicator
booleans, session labels, one-decimal timing, car rebinding and profile reloads.
The same draw path produced [inspection/mustang-preview.png](inspection/mustang-preview.png).

A completed lap, full-range shift lights, wheel-lock transitions, light/wiper
toggles, physical editor dragging/save and full game restart have not been
visually tested for this profile. The timing preview uses sample values because
the inspected session had no valid best lap.
