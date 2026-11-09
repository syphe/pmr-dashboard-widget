# DLC Camaro dashboard

Inspected 10 November 2026 through the connected PMR debugger while driving the
AUS V8 Evo Camaro. The exact actor ID is `Chevrolet_Camaro_V8Supercar_2024`;
the model root is `Chevrolet_Camaro_V8Supercar_2024.i3d`.

## Original assets

The live main-page palette binding is `CHEV_CAMARO_SUPERCAR_DISPLAY1`. Its
material exposes these mounted textures:

```text
dlcS/s1_dlc3/vehicles/Chevrolet_Camaro_V8Supercar_2024/Textures/t_chev_camaro_supercar_display1_glow.png
dlcS/s1_dlc3/vehicles/Chevrolet_Camaro_V8Supercar_2024/Textures/t_chev_camaro_supercar_display_mask1.png
```

PMR's `copyFile()` successfully exported the corresponding `.dds` resources.
Both decode as 1024 x 512. Their SHA-256 hashes match the earlier Mustang exports:
background `94907551087803446661754f41cf1140915b454482522ffe5624180241d1ab88`;
mask `6c0360f1c7e531ba1e69872d24a867869b5ba243886b0e5bd970f61ce871c7c2`.
This export used the owned game's mounted resource API; no package was decrypted
or unpacked externally. Textures, derived metadata, dumps and previews remain
ignored local files.

Run [inspection/export-camaro-assets.lua](inspection/export-camaro-assets.lua)
after loading the local bootstrap while driving this car. Then run
`python tools/setup_assets.py --dlc-export inspection` to prepare available
profiles, including this Camaro. It also works with
`--vehicle Chevrolet_Camaro_V8Supercar_2024`; the shared Supra/DDU10 font
dependency is prepared automatically. Mustang exports are not required.

## Layout and bindings

The bounded live inspection captured the always-on TopPage and first main page.
All 125 captured type, parameter, position, scale, font, precision, alignment and
threshold settings match the Mustang capture. The Camaro therefore uses the same
calibrated coordinates, with its own exact-ID profile and local asset directory.

| Display | Native binding |
| --- | --- |
| Gear | `gear` |
| Best lap | `bestLap`, LapTime object, one decimal |
| Gain/loss | `lapDelta`, signed hundredths |
| Position / lap | `pos` / `lap` |
| Engine temperature | `engine_temp`, warning above 115 |
| Brake bias | `brakebias`, one decimal |
| Engine map | `map` |
| Session label | `israce`, `isqualifying`, `ispractice` |
| Headlight / wiper | `lights` / `wiper` |
| Front / rear lock lamps | `frontLocked` / `rearLocked` |
| Four shift lamps | `revs`, 6000 / 6450 / 6900 / 7350 |

The live map getter returned `3`, brake bias approximately `65`, and gear `0`.
Main-page rendering is independent of cockpit popups or page changes. Missing
valid lap timing displays `--` using the shared renderer's existing guards.

## Validation

The profile selected automatically in the running Camaro. The in-game widget
showed neutral, position 17, lap 0, engine temperature 115 (red), brake bias 65.0
and map 3. A bounded probe completed 60 native telemetry updates and 60 draws,
then restored both callbacks. Three overlays were cached: background, icons and
shared font. Pausing hid the widget; the game was left paused.

Local tests cover independent Camaro export setup in a clean authored-files-only
checkout, missing DLC exports, exact vehicle selection, switching from Mustang
without stale readings/resources, profile reload and the shared draw path.
Completed laps, full RPM range and light/wiper/lock transitions have not been
visually exercised for this car.
