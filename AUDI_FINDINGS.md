# Audi R8 LMS GT3 Evo calibration

Vehicle ID: `Audi_R8_LMS_GT3_EVO`. Main page: `P1`.

The running cockpit reference showed green healthy-pressure/fuel/engine regions,
blue cold-tyre temperature regions, white cold-temperature digits and green
`0.00` gain/loss before a lap. The captured session had approximately 39 C tyre
temperatures and 1.59/1.51 bar front/rear pressures.

The earlier import baked normal palette colours into the background, used
linear colour values directly for overlay artwork, centred default numeric
anchors, and suppressed lap delta when no best lap existed.

The updated profile:

- Uses 23 live colour controls from the actor's original main/top-page widgets.
  Their shapes are extracted from the two original DDS shader masks into
  `assets/vehicles/Audi_R8_LMS_GT3_EVO/palette.dds`.
- Preserves shader-layer occlusion, including static text and the gear outline.
  Dynamic palette tints retain authored linear RGB for `Overlay:setColor`;
  the game performs display encoding. Baked DDS pixels require display RGB
  instead. Pre-encoding the overlay tint made the gear fill grey and the
  cold-temperature blue too bright; the live comparison exposed this mistake.
- Uses the original low/high thresholds: tyre temperature 75/105 C, tyre pressure
  1.5 bar, fuel 10 L, fuel pressure 2.8 bar and engine temperature 115 C.
- Shows green `0.00` before a valid best lap, preserving other profiles' delta
  behaviour. Missing delta after a valid best lap remains `--`.
- Fits 17 numeric readouts inside their original artwork boxes, reducing glyph
  size uniformly for long values. The gear remains centred.

Alignment is left=0, centre=1, right=2. Explicit attributes in the captured
Mustang/Camaro actors and their live widget dumps establish this mapping:
their centre-aligned brake-bias widget reports 1. Importer and audit defaults
have been corrected. Calibrated 2D anchors remain separate from native glyph
placement.

`tools/calibrate_audi.py` regenerates the palette atlas, writes the repeatable
configuration in `catalog/calibrations.json`, refines only this profile and
prepares a cache-safe profile/renderer/audit reload. Saved HUD placement is
retained. Normal startup uses the bundled profile and assets directly.

Automated checks cover cold/normal/hot colours, pre-lap delta, invalid telemetry
and long strings inside all 17 boxes. Previews use the actual Lua renderer.
The corrected profile was hot-reloaded into the running Audi session on
2026-11-10. The matching live Motec capture includes all 23 palette getters;
the telemetry/source audit and mounted-scene audit pass without findings.
Saved HUD placement is retained. Screen capture recovered after Windows was
unlocked, and the corrected palette was reloaded and compared beside the
cockpit dash. Both show cold blue tyre-temperature boxes with white digits,
green front pressures, red low rear pressures, and green `0.00` pre-lap delta.
The gear fill is dark and the visible readouts stay inside their boxes.
The captured stationary state was about 34 C, 1.56/1.48 bar, 59.9 L, 78 C
engine temperature and 1505 rpm. The widget's flat colours are not a guarantee
of pixel-identical brightness under cockpit lighting/exposure. Completed-lap
and hot-warning transitions still need driving-session visual checks; its
calibration label remains `preview-calibrated`, separately from its passing
`runtime-audited` telemetry validation.
