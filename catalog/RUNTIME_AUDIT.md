# Runtime dashboard audit

Capture method, layout calibration and runtime validation are independent. `runtime-audited` requires a matching current-profile capture of the actual player Motec component and telemetry getters, plus a passing mounted-scene/source comparison. It does not establish visual fidelity or full-range warning behaviour. Formatting differences and unavailable samples remain visible as notes.

The initial live Audi R8 LMS GT3 Evo audit exposed missing Pa-to-bar conversion. The native pressure helper returned 3.272 for 327200 Pa with the Motec override enabled. Fuel/oil pressure conversions were corrected in 35 profiles and in their generators; that correction does not mean all 35 cars have received live Motec audits.

| Vehicle | Mounted scenes | Live Motec | Findings |
| --- | --- | --- | ---: |
| `Acura_ARX-06_2023` | passed | pending-runtime-audit | 0 |
| `Alpine_A110_GT4_2020` | passed | pending-runtime-audit | 0 |
| `Alpine_A424_2024` | passed | pending-runtime-audit | 0 |
| `Aston_Martin_DBR9_2005` | passed | pending-runtime-audit | 0 |
| `Aston_Martin_Valkyrie_LMH_2025` | passed | pending-runtime-audit | 0 |
| `Aston_Martin_Vantage_AMR_GT4` | passed | pending-runtime-audit | 0 |
| `Aston_Martin_Vantage_GT3` | passed | pending-runtime-audit | 0 |
| `Aston_Martin_Vantage_GT3_Evo` | passed | pending-runtime-audit | 0 |
| `Aston_Martin_Vantage_GTE_2020` | passed | pending-runtime-audit | 0 |
| `Audi_R8_LMP900_2002` | passed | pending-runtime-audit | 0 |
| `Audi_R8_LMS_GT3_EVO` | passed | runtime-audited | 0 |
| `Audi_R8_LMS_GT4_EVO` | passed | pending-runtime-audit | 0 |
| `BMW_M3_E46_GTR` | passed | pending-runtime-audit | 0 |
| `BMW_M4_GT3` | passed | pending-runtime-audit | 0 |
| `BMW_M4_GT4` | passed | pending-runtime-audit | 0 |
| `BMW_M8_GTE` | passed | pending-runtime-audit | 0 |
| `BMW_M_Hybrid_V8` | passed | pending-runtime-audit | 0 |
| `BMW_V12_LMR` | passed | pending-runtime-audit | 0 |
| `Cadillac_Northstar_LMP900` | passed | pending-runtime-audit | 0 |
| `Cadillac_V_SeriesR` | passed | pending-runtime-audit | 0 |
| `Chevrolet_Camaro_V8Supercar_2024` | passed | runtime-audit-findings | 6 |
| `Chevrolet_Camaro_ZL-1_GT4_2017` | passed | pending-runtime-audit | 0 |
| `Chevrolet_Corvette_C5R` | passed | pending-runtime-audit | 0 |
| `Chevrolet_Corvette_C6R` | passed | pending-runtime-audit | 0 |
| `Chevrolet_Corvette_C7R_GTE` | passed | pending-runtime-audit | 0 |
| `Chevrolet_Corvette_C8R_GTE_2020` | passed | pending-runtime-audit | 0 |
| `Chevrolet_Corvette_Z06_GT3_2024` | passed | pending-runtime-audit | 0 |
| `Chrysler_Viper_GTS-R` | passed | pending-runtime-audit | 0 |
| `Dodge_SRT_Viper_GTS-R` | passed | pending-runtime-audit | 0 |
| `Dodge_Viper_CC` | passed | pending-runtime-audit | 0 |
| `Ford_Falcon_FG_V8Supercar_2013` | passed | pending-runtime-audit | 0 |
| `Ford_GTLM_GTE_2022` | passed | pending-runtime-audit | 0 |
| `Ford_Mustang_GT3_2023` | passed | pending-runtime-audit | 0 |
| `Ford_Mustang_GT4_2024` | passed | pending-runtime-audit | 0 |
| `Ford_Mustang_V8Supercar_2024` | passed | pending-runtime-audit | 0 |
| `Gillet_Vertigo_2004` | passed | pending-runtime-audit | 0 |
| `Holden_Commodore_VF_V8Supercar_2013` | passed | runtime-audit-findings | 3 |
| `Honda_Civic_Type-R_GT500` | passed | pending-runtime-audit | 0 |
| `Honda_NSX_GT3` | passed | pending-runtime-audit | 0 |
| `Honda_NSX_GT500_2023` | passed | pending-runtime-audit | 0 |
| `Honda_NSX_JGTC_2003` | passed | pending-runtime-audit | 0 |
| `Lamborghini_Huracan_GT3_Evo_2022` | passed | pending-runtime-audit | 0 |
| `Lamborghini_Murcielago_R-GT_2004` | passed | pending-runtime-audit | 0 |
| `Lamborghini_SC63_LMDh_2024` | passed | pending-runtime-audit | 0 |
| `Lister_storm_gt` | passed | pending-runtime-audit | 0 |
| `Lotus_Elise_GT1_1997` | passed | pending-runtime-audit | 0 |
| `Marcos_Mantara_LM600_GT2_2004` | passed | pending-runtime-audit | 0 |
| `Maserati_MC12_GT1` | passed | pending-runtime-audit | 0 |
| `Mazda_787B_1991` | passed | pending-runtime-audit | 0 |
| `Mazda_MX-5_Cup_2017` | passed | pending-runtime-audit | 0 |
| `Mercedes_AMG_GT3_Evo_2020` | passed | pending-runtime-audit | 0 |
| `Mercedes_AMG_GT4` | passed | pending-runtime-audit | 0 |
| `Mercedes_CLK-LM_1998` | passed | pending-runtime-audit | 0 |
| `Morgan_Aero_8_GTN` | passed | pending-runtime-audit | 0 |
| `Mosler_MT900R_2004` | passed | pending-runtime-audit | 0 |
| `Nissan_350Z_GT500_2004` | passed | pending-runtime-audit | 0 |
| `Nissan_GT-R_R34_JGTC_2003` | passed | pending-runtime-audit | 0 |
| `Nissan_GTR_R35_GT500` | passed | pending-runtime-audit | 0 |
| `Nissan_R390_GT1` | passed | pending-runtime-audit | 0 |
| `Nissan_Z_GT4_2023` | passed | pending-runtime-audit | 0 |
| `Nissan_Z_GT500` | passed | pending-runtime-audit | 0 |
| `Panoz_Esperante_GTR1` | passed | pending-runtime-audit | 0 |
| `Panoz_LMP1_Roadster_S_99` | passed | pending-runtime-audit | 0 |
| `Peugeot_9X8_2024` | passed | pending-runtime-audit | 0 |
| `Porsche_911_GT1_98` | passed | pending-runtime-audit | 0 |
| `Porsche_911_GT3-RSR_2004` | passed | pending-runtime-audit | 0 |
| `Porsche_911_GT3_Cup_2022` | passed | pending-runtime-audit | 0 |
| `Porsche_911_RSR_GTE_2020` | passed | pending-runtime-audit | 0 |
| `Porsche_963` | passed | pending-runtime-audit | 0 |
| `Porsche_992_GT3R` | passed | runtime-audited | 0 |
| `Porsche_Cayman_GT4_Clubsport_2022` | passed | pending-runtime-audit | 0 |
| `Saleen_S7R` | passed | pending-runtime-audit | 0 |
| `TA2_Chevrolet_Camaro_2024` | passed | pending-runtime-audit | 0 |
| `TA2_Dodge_Challenger_2024` | passed | pending-runtime-audit | 0 |
| `TA2_Ford_Mustang_2024` | passed | pending-runtime-audit | 0 |
| `TVR_Tuscan_T400R_2002` | passed | pending-runtime-audit | 0 |
| `Toyota_GR010` | passed | pending-runtime-audit | 0 |
| `Toyota_GR_Supra_GT500` | passed | pending-runtime-audit | 0 |
| `Toyota_GT-One_TS020` | passed | pending-runtime-audit | 0 |
| `Toyota_Supra_GT4` | passed | pending-runtime-audit | 0 |
| `Toyota_Supra_JGTC_2003` | passed | pending-runtime-audit | 0 |

## Chevrolet_Camaro_V8Supercar_2024

- best: telemetry getter unavailable
- brakeBias: profile alignment differs from live alignment
- engineTemp: profile alignment differs from live alignment
- gear: gear/neutral text differs: profile 'N', native '0'
- map: profile alignment differs from live alignment
- map: profile value '3' differs from native '0'; conversion/units need review
- best: no valid numeric sample in this session
- brakeBias: formatting differs: profile '0.0', native '0'
- delta: formatting differs: profile '+0.00', native '0'
- position: formatting differs: profile '1', native '0'

## Holden_Commodore_VF_V8Supercar_2013

- gear_digit: gear/neutral text differs: profile 'N', native '0'
- gear_digit: profile alignment differs from live alignment
- laptime_digit: telemetry getter unavailable
- fuel_digit: formatting differs: profile '0.0', native '0'
- laptime_digit: no valid numeric sample in this session

## Porsche_992_GT3R

- laptime_digit: formatting differs: profile '0:07.92', native '0:07.93'
