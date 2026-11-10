# Dashboard profile coverage

Against the saved live catalogue: **112 active official vehicles**, **81 bundled digital profiles**, **31 analogue exclusions**. 11 inactive entries are outside the active-vehicle target.

Every enabled profile is registered and its referenced background, fonts, gauges and icons exist as nonempty DDS files. The bundle runs without the game installation, raw captures or setup scripts.

Coverage does not establish visual fidelity. `geometry-unverified` uses readable mesh UVs; `bounds-unverified` estimates a rectangular screen from live mounted bounding spheres and digit transforms. The latter cannot recover UV crops or aspect ratios and needs visual calibration. `asset-calibrated-unverified` adds explicit digit anchors/sizes matched to the original artwork in sample previews; it has not been verified in each live car. Some warning/visibility/colour controls are not animated; missing telemetry displays `--`. Mixed cockpits expose only their original digital panel.

Regenerate and validate with `python tools/profile_coverage.py`. Raw scene bounds and archives remain ignored; only prepared runtime assets are bundled.

Capture method and runtime validation are listed separately. See [RUNTIME_AUDIT.md](RUNTIME_AUDIT.md) for findings.

| Vehicle ID | Package | Active | Coverage | Calibration | Live validation |
| --- | --- | --- | --- | --- | --- |
| [Acura_ARX-06_2023](../profiles/Acura_ARX-06_2023.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Honda_NSX_GT3](../profiles/Honda_NSX_GT3.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Alpine_A110_GT4_2020](../profiles/Alpine_A110_GT4_2020.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Alpine_A424_2024](../profiles/Alpine_A424_2024.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Aston_Martin_Vantage_GT3_Evo](../profiles/Aston_Martin_Vantage_GT3_Evo.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Aston_Martin_Vantage_GT3](../profiles/Aston_Martin_Vantage_GT3.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Aston_Martin_Vantage_AMR_GT4](../profiles/Aston_Martin_Vantage_AMR_GT4.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Aston_Martin_DBR9_2005](../profiles/Aston_Martin_DBR9_2005.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Aston_Martin_Valkyrie_LMH_2025](../profiles/Aston_Martin_Valkyrie_LMH_2025.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| `Audi_90_IMSA_GTO_1989` | Base game | Yes | excluded-analogue |  |  |
| [Audi_R8_LMP900_2002](../profiles/Audi_R8_LMP900_2002.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Audi_R8_LMS_GT3_EVO](../profiles/Audi_R8_LMS_GT3_EVO.lua) | Base game | Yes | profile | preview-calibrated | runtime-audited |
| [Audi_R8_LMS_GT4_EVO](../profiles/Audi_R8_LMS_GT4_EVO.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [BMW_M_Hybrid_V8](../profiles/BMW_M_Hybrid_V8.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [BMW_M3_E46_GTR](../profiles/BMW_M3_E46_GTR.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [BMW_M4_GT3](../profiles/BMW_M4_GT3.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [BMW_M4_GT4](../profiles/BMW_M4_GT4.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [BMW_V12_LMR](../profiles/BMW_V12_LMR.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Cadillac_Northstar_LMP900](../profiles/Cadillac_Northstar_LMP900.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Cadillac_V_SeriesR](../profiles/Cadillac_V_SeriesR.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| `Chevrolet_Camaro_Z28_GTO_1989` | Base game | Yes | excluded-analogue |  |  |
| [Chevrolet_Camaro_ZL-1_GT4_2017](../profiles/Chevrolet_Camaro_ZL-1_GT4_2017.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Chevrolet_Corvette_C5R](../profiles/Chevrolet_Corvette_C5R.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Chevrolet_Corvette_C6R](../profiles/Chevrolet_Corvette_C6R.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Chevrolet_Corvette_Z06_GT3_2024](../profiles/Chevrolet_Corvette_Z06_GT3_2024.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Chrysler_Viper_GTS-R](../profiles/Chrysler_Viper_GTS-R.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Dodge_Viper_CC](../profiles/Dodge_Viper_CC.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Ford_Mustang_GT3_2023](../profiles/Ford_Mustang_GT3_2023.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Ford_Mustang_GT4_2024](../profiles/Ford_Mustang_GT4_2024.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Gillet_Vertigo_2004](../profiles/Gillet_Vertigo_2004.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| `Jaguar_XJR-9` | Base game | Yes | excluded-analogue |  |  |
| [Lamborghini_Huracan_GT3_Evo_2022](../profiles/Lamborghini_Huracan_GT3_Evo_2022.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Lamborghini_Murcielago_R-GT_2004](../profiles/Lamborghini_Murcielago_R-GT_2004.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Lamborghini_SC63_LMDh_2024](../profiles/Lamborghini_SC63_LMDh_2024.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| `Lamborghini_Temerario_2026` | Base game | Yes | excluded-analogue |  |  |
| [Lister_storm_gt](../profiles/Lister_storm_gt.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| `Lola_T70_MK3B_1970` | Base game | Yes | excluded-analogue |  |  |
| [Lotus_Elise_GT1_1997](../profiles/Lotus_Elise_GT1_1997.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Marcos_Mantara_LM600_GT2_2004](../profiles/Marcos_Mantara_LM600_GT2_2004.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Maserati_MC12_GT1](../profiles/Maserati_MC12_GT1.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Mazda_787B_1991](../profiles/Mazda_787B_1991.lua) | Base game | Yes | profile | preview-calibrated | pending-runtime-audit |
| [Mazda_MX-5_Cup_2017](../profiles/Mazda_MX-5_Cup_2017.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| `Mazda_RX-7_GTO_1989` | Base game | Yes | excluded-analogue |  |  |
| [Mercedes_AMG_GT3_Evo_2020](../profiles/Mercedes_AMG_GT3_Evo_2020.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Mercedes_AMG_GT4](../profiles/Mercedes_AMG_GT4.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Mercedes_CLK-LM_1998](../profiles/Mercedes_CLK-LM_1998.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| `Sauber_C9_1989` | Base game | Yes | excluded-analogue |  |  |
| `Mercury_Cougar_XR-7_GTO_1989` | Base game | Yes | excluded-analogue |  |  |
| [Morgan_Aero_8_GTN](../profiles/Morgan_Aero_8_GTN.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Mosler_MT900R_2004](../profiles/Mosler_MT900R_2004.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| `Nissan_300ZX_IMSA_GTO_1989` | Base game | Yes | excluded-analogue |  |  |
| [Nissan_R390_GT1](../profiles/Nissan_R390_GT1.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| `Nissan_R89C` | Base game | Yes | excluded-analogue |  |  |
| [Nissan_Z_GT4_2023](../profiles/Nissan_Z_GT4_2023.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Panoz_Esperante_GTR1](../profiles/Panoz_Esperante_GTR1.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Panoz_LMP1_Roadster_S_99](../profiles/Panoz_LMP1_Roadster_S_99.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Peugeot_9X8_2024](../profiles/Peugeot_9X8_2024.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Porsche_Cayman_GT4_Clubsport_2022](../profiles/Porsche_Cayman_GT4_Clubsport_2022.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| `Porsche_Carrera_Cup_1990` | Base game | Yes | excluded-analogue |  |  |
| [Porsche_911_GT1_98](../profiles/Porsche_911_GT1_98.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Porsche_911_GT3_Cup_2022](../profiles/Porsche_911_GT3_Cup_2022.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Porsche_992_GT3R](../profiles/Porsche_992_GT3R.lua) | Base game | Yes | profile | preview-calibrated | runtime-audited |
| [Porsche_911_GT3-RSR_2004](../profiles/Porsche_911_GT3-RSR_2004.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| `Porsche_917K_1970` | Base game | Yes | excluded-analogue |  |  |
| `Porsche_962C_88` | Base game | Yes | excluded-analogue |  |  |
| [Porsche_963](../profiles/Porsche_963.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Saleen_S7R](../profiles/Saleen_S7R.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [TVR_Tuscan_T400R_2002](../profiles/TVR_Tuscan_T400R_2002.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Toyota_Supra_GT4](../profiles/Toyota_Supra_GT4.lua) | Base game | Yes | profile | hand-tuned | pending-runtime-audit |
| [Toyota_GR010](../profiles/Toyota_GR010.lua) | Base game | Yes | profile | generated | pending-runtime-audit |
| [Toyota_GT-One_TS020](../profiles/Toyota_GT-One_TS020.lua) | Base game | Yes | profile | preview-calibrated | pending-runtime-audit |
| `AMC_Javelin_Trans_Am_1971` | V8PowerPack | Yes | excluded-analogue |  |  |
| `Chevrolet_Camaro_Z28_Trans_Am_1969` | V8PowerPack | Yes | excluded-analogue |  |  |
| [TA2_Chevrolet_Camaro_2024](../profiles/TA2_Chevrolet_Camaro_2024.lua) | V8PowerPack | Yes | profile | preview-calibrated | pending-runtime-audit |
| [Chevrolet_Camaro_V8Supercar_2024](../profiles/Chevrolet_Camaro_V8Supercar_2024.lua) | V8PowerPack | Yes | profile | hand-tuned | runtime-audit-findings |
| [TA2_Dodge_Challenger_2024](../profiles/TA2_Dodge_Challenger_2024.lua) | V8PowerPack | Yes | profile | preview-calibrated | pending-runtime-audit |
| [TA2_Ford_Mustang_2024](../profiles/TA2_Ford_Mustang_2024.lua) | V8PowerPack | Yes | profile | preview-calibrated | pending-runtime-audit |
| [Ford_Mustang_V8Supercar_2024](../profiles/Ford_Mustang_V8Supercar_2024.lua) | V8PowerPack | Yes | profile | hand-tuned | pending-runtime-audit |
| `Ford_Mustang_Boss_302_Trans_Am_1970` | V8PowerPack | Yes | excluded-analogue |  |  |
| `Plymouth_Barracuda_Trans_Am_1970` | V8PowerPack | Yes | excluded-analogue |  |  |
| `Audi_R18_etron_LMP1_2016` | WorldEndurancePack | No | inactive |  |  |
| `BMW_March_GTP_1986` | WorldEndurancePack | No | inactive |  |  |
| `Chevrolet_Corvette_C4_GTP_1986` | WorldEndurancePack | No | inactive |  |  |
| `Ford_Probe_GTP_1986` | WorldEndurancePack | No | inactive |  |  |
| `Jaguar_XJR9_IMSA_GTP_1988` | WorldEndurancePack | No | inactive |  |  |
| `Nissan_GTP_ZX_Turbo_1988` | WorldEndurancePack | No | inactive |  |  |
| `Olivera_13_LMP2_2013` | WorldEndurancePack | No | inactive |  |  |
| `Olivera_26_LMP2_2026` | WorldEndurancePack | No | inactive |  |  |
| `Porsche_919_LMP1_2016` | WorldEndurancePack | No | inactive |  |  |
| `Porsche_962_GTP_1988` | WorldEndurancePack | No | inactive |  |  |
| `Toyota_TS050_LMP1_2016` | WorldEndurancePack | No | inactive |  |  |
| [Ford_Falcon_FG_V8Supercar_2013](../profiles/Ford_Falcon_FG_V8Supercar_2013.lua) | fordfalcon | Yes | profile | preview-calibrated | pending-runtime-audit |
| [Holden_Commodore_VF_V8Supercar_2013](../profiles/Holden_Commodore_VF_V8Supercar_2013.lua) | fordfalcon | Yes | profile | preview-calibrated | runtime-audit-findings |
| `BMW_320_Turbo_Group5` | group5RevivalPack | Yes | excluded-analogue |  |  |
| `Ford_Zakspeed_Capri_Group5` | group5RevivalPack | Yes | excluded-analogue |  |  |
| `Nissan_280ZX_IMSA` | group5RevivalPack | Yes | excluded-analogue |  |  |
| `Nissan_Skyline_KDR30` | group5RevivalPack | Yes | excluded-analogue |  |  |
| `Porsche_935_80` | group5RevivalPack | Yes | excluded-analogue |  |  |
| `Chaparral_2F_1967` | gtLegendsPack | Yes | excluded-analogue |  |  |
| `Chevrolet_Corvette_C3_1973` | gtLegendsPack | Yes | excluded-analogue |  |  |
| `Chevrolet_Corvette_Grand_Sport_1963` | gtLegendsPack | Yes | excluded-analogue |  |  |
| `Ford_Capri_RS3100_1973` | gtLegendsPack | Yes | excluded-analogue |  |  |
| `Ford_GT40_MkIV_1967` | gtLegendsPack | Yes | excluded-analogue |  |  |
| `Jaguar_E-Type_Lightweight_1964` | gtLegendsPack | Yes | excluded-analogue |  |  |
| `Lola_T70_MK3_67` | gtLegendsPack | Yes | excluded-analogue |  |  |
| `Porsche_911_RSR_1974` | gtLegendsPack | Yes | excluded-analogue |  |  |
| `Shelby_Daytona_Coupe_1964` | gtLegendsPack | Yes | excluded-analogue |  |  |
| [Aston_Martin_Vantage_GTE_2020](../profiles/Aston_Martin_Vantage_GTE_2020.lua) | gteDecadePack | Yes | profile | preview-calibrated | pending-runtime-audit |
| [BMW_M8_GTE](../profiles/BMW_M8_GTE.lua) | gteDecadePack | Yes | profile | preview-calibrated | pending-runtime-audit |
| [Chevrolet_Corvette_C7R_GTE](../profiles/Chevrolet_Corvette_C7R_GTE.lua) | gteDecadePack | Yes | profile | preview-calibrated | pending-runtime-audit |
| [Chevrolet_Corvette_C8R_GTE_2020](../profiles/Chevrolet_Corvette_C8R_GTE_2020.lua) | gteDecadePack | Yes | profile | preview-calibrated | pending-runtime-audit |
| [Dodge_SRT_Viper_GTS-R](../profiles/Dodge_SRT_Viper_GTS-R.lua) | gteDecadePack | Yes | profile | preview-calibrated | pending-runtime-audit |
| [Ford_GTLM_GTE_2022](../profiles/Ford_GTLM_GTE_2022.lua) | gteDecadePack | Yes | profile | preview-calibrated | pending-runtime-audit |
| [Porsche_911_RSR_GTE_2020](../profiles/Porsche_911_RSR_GTE_2020.lua) | gteDecadePack | Yes | profile | preview-calibrated | pending-runtime-audit |
| [Honda_Civic_Type-R_GT500](../profiles/Honda_Civic_Type-R_GT500.lua) | japaneseGT500Pack | Yes | profile | preview-calibrated | pending-runtime-audit |
| [Honda_NSX_GT500_2023](../profiles/Honda_NSX_GT500_2023.lua) | japaneseGT500Pack | Yes | profile | preview-calibrated | pending-runtime-audit |
| [Honda_NSX_JGTC_2003](../profiles/Honda_NSX_JGTC_2003.lua) | japaneseGT500Pack | Yes | profile | preview-calibrated | pending-runtime-audit |
| [Nissan_Z_GT500](../profiles/Nissan_Z_GT500.lua) | japaneseGT500Pack | Yes | profile | preview-calibrated | pending-runtime-audit |
| [Nissan_350Z_GT500_2004](../profiles/Nissan_350Z_GT500_2004.lua) | japaneseGT500Pack | Yes | profile | preview-calibrated | pending-runtime-audit |
| [Nissan_GTR_R35_GT500](../profiles/Nissan_GTR_R35_GT500.lua) | japaneseGT500Pack | Yes | profile | preview-calibrated | pending-runtime-audit |
| [Nissan_GT-R_R34_JGTC_2003](../profiles/Nissan_GT-R_R34_JGTC_2003.lua) | japaneseGT500Pack | Yes | profile | preview-calibrated | pending-runtime-audit |
| [Toyota_GR_Supra_GT500](../profiles/Toyota_GR_Supra_GT500.lua) | japaneseGT500Pack | Yes | profile | preview-calibrated | pending-runtime-audit |
| [Toyota_Supra_JGTC_2003](../profiles/Toyota_Supra_JGTC_2003.lua) | japaneseGT500Pack | Yes | profile | preview-calibrated | pending-runtime-audit |
