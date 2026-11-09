# Live PMR vehicle catalogue

Captured from the running game at 2026-11-10 08:40:29: **123 base-game and DLC cars**.
Includes inactive definitions; an entry is not proof that the car is available to drive.
IDs below are actor-folder IDs used by dashboard profiles; the CSV/JSON also preserve the separate catalogue IDs.

| Package / entitlement key | Entries | Active |
| --- | ---: | ---: |
| Base game | 71 | 71 |
| V8PowerPack | 9 | 9 |
| WorldEndurancePack | 11 | 0 |
| fordfalcon | 2 | 2 |
| group5RevivalPack | 5 | 5 |
| gtLegendsPack | 9 | 9 |
| gteDecadePack | 7 | 7 |
| japaneseGT500Pack | 9 | 9 |

## Asset capture

2744 successful resource exports; 0 failed attempts.
Raw files and the source/destination manifest are in `inspection/live-catalog/`.
Actor, vehicle-definition and I3D XML were read and reserialized through PMR; they are not byte-identical copies.
Textures and geometry binaries use the mounted-resource copy API. Resources were also readable for inactive catalogue entries; no Active flags or entitlements were changed, and no vehicle actors were spawned.
Capture focuses on dashboard/instrument dependencies, not complete playable vehicle packages.

## Base game (71)

| Manufacturer | Car | Year | Class | Actor-folder ID | Active |
| --- | --- | ---: | --- | --- | --- |
| Acura | ARX-06 | 2023 | LMDh | `Acura_ARX-06_2023` | Yes |
| Acura | NSX GT3 Evo 22 | 2022 | GT3 | `Honda_NSX_GT3` | Yes |
| Alpine | A110 GT4 | 2020 | GT4 | `Alpine_A110_GT4_2020` | Yes |
| Alpine | A424 Beta | 2024 | LMDh | `Alpine_A424_2024` | Yes |
| Aston Martin | AMR Vantage GT3 | 2024 | GT3 | `Aston_Martin_Vantage_GT3_Evo` | Yes |
| Aston Martin | AMR Vantage GT3 2022 | 2022 | GT3 | `Aston_Martin_Vantage_GT3` | Yes |
| Aston Martin | AMR Vantage GT4 | 2020 | GT4 | `Aston_Martin_Vantage_AMR_GT4` | Yes |
| Aston Martin | DBR9 | 2005 | GT | `Aston_Martin_DBR9_2005` | Yes |
| Aston Martin | Valkyrie Hypercar | 2025 | LMDh | `Aston_Martin_Valkyrie_LMH_2025` | Yes |
| Audi | 90 IMSA GTO | 1989 | GTO | `Audi_90_IMSA_GTO_1989` | Yes |
| Audi | R8 (LMP900) | 2002 | LMP | `Audi_R8_LMP900_2002` | Yes |
| Audi | R8 GT3 Evo II | 2022 | GT3 | `Audi_R8_LMS_GT3_EVO` | Yes |
| Audi | R8 LMS GT4 Evo | 2020 | GT4 | `Audi_R8_LMS_GT4_EVO` | Yes |
| BMW | M Hybrid V8 | 2023 | LMDh | `BMW_M_Hybrid_V8` | Yes |
| BMW | M3 GTR (E46) | 2004 | N-GT | `BMW_M3_E46_GTR` | Yes |
| BMW | M4 GT3 EVO | 2025 | GT3 | `BMW_M4_GT3` | Yes |
| BMW | M4 GT4 EVO | 2025 | GT4 | `BMW_M4_GT4` | Yes |
| BMW | V12 LMR | 1999 | LMP | `BMW_V12_LMR` | Yes |
| Cadillac | Northstar LMP-02 | 2002 | LMP | `Cadillac_Northstar_LMP900` | Yes |
| Cadillac | V-Series.R | 2023 | LMDh | `Cadillac_V_SeriesR` | Yes |
| Chevrolet | Camaro Z28 GTO | 1989 | GTO | `Chevrolet_Camaro_Z28_GTO_1989` | Yes |
| Chevrolet | Camaro ZL-1 GT4.R | 2017 | GT4 | `Chevrolet_Camaro_ZL-1_GT4_2017` | Yes |
| Chevrolet | Corvette C5.R | 2004 | GT | `Chevrolet_Corvette_C5R` | Yes |
| Chevrolet | Corvette C6.R | 2005 | GT | `Chevrolet_Corvette_C6R` | Yes |
| Chevrolet | Corvette Z06 GT3.R | 2023 | GT3 | `Chevrolet_Corvette_Z06_GT3_2024` | Yes |
| Chrysler | Viper GTS-R | 2003 | GT | `Chrysler_Viper_GTS-R` | Yes |
| Dodge | Viper Competition Coupe | 2004 | N-GT | `Dodge_Viper_CC` | Yes |
| Ford | Mustang GT3 | 2023 | GT3 | `Ford_Mustang_GT3_2023` | Yes |
| Ford | Mustang GT4 | 2024 | GT4 | `Ford_Mustang_GT4_2024` | Yes |
| Gillet | Vertigo | 2004 | N-GT | `Gillet_Vertigo_2004` | Yes |
| Jaguar | XJR-9 | 1990 | Group C | `Jaguar_XJR-9` | Yes |
| Lamborghini | Huracán GT3 Evo2 | 2022 | GT3 | `Lamborghini_Huracan_GT3_Evo_2022` | Yes |
| Lamborghini | Murcielago R-GT | 2004 | GT | `Lamborghini_Murcielago_R-GT_2004` | Yes |
| Lamborghini | SC63 LMDh | 2024 | LMDh | `Lamborghini_SC63_LMDh_2024` | Yes |
| Lamborghini | Temerario | 2026 | Track Day | `Lamborghini_Temerario_2026` | Yes |
| Lister | Storm GT | 2004 | GT | `Lister_storm_gt` | Yes |
| Lola | T70 Mk3B GT | 1970 | Sports Car 70 | `Lola_T70_MK3B_1970` | Yes |
| Lotus | Elise GT1 | 1997 | GT1 | `Lotus_Elise_GT1_1997` | Yes |
| Marcos | Mantara LM600 | 2004 | N-GT | `Marcos_Mantara_LM600_GT2_2004` | Yes |
| Maserati | MC12 GT1 | 2004 | GT | `Maserati_MC12_GT1` | Yes |
| Mazda | 787B | 1991 | Group C | `Mazda_787B_1991` | Yes |
| Mazda | MX-5 Spec | 2017 | MX5 Trophy | `Mazda_MX-5_Cup_2017` | Yes |
| Mazda | RX-7 GTO | 1989 | GTO | `Mazda_RX-7_GTO_1989` | Yes |
| Mercedes-AMG | GT3 | 2020 | GT3 | `Mercedes_AMG_GT3_Evo_2020` | Yes |
| Mercedes-AMG | GT4 | 2020 | GT4 | `Mercedes_AMG_GT4` | Yes |
| Mercedes-Benz | CLK-LM | 1998 | GT1 | `Mercedes_CLK-LM_1998` | Yes |
| Mercedes-Benz | Sauber C9 | 1989 | Group C | `Sauber_C9_1989` | Yes |
| Mercury | Cougar XR-7 GTO | 1989 | GTO | `Mercury_Cougar_XR-7_GTO_1989` | Yes |
| Morgan | Aero 8 GT(N) | 2004 | N-GT | `Morgan_Aero_8_GTN` | Yes |
| Mosler | MT900R | 2004 | N-GT | `Mosler_MT900R_2004` | Yes |
| Nissan | 300ZX Turbo GTO | 1989 | GTO | `Nissan_300ZX_IMSA_GTO_1989` | Yes |
| Nissan | R390 GT1 | 1998 | GT1 | `Nissan_R390_GT1` | Yes |
| Nissan | R89C | 1989 | Group C | `Nissan_R89C` | Yes |
| Nissan | Z GT4 | 2023 | GT4 | `Nissan_Z_GT4_2023` | Yes |
| Panoz | Esperante GTR-1 | 1998 | GT1 | `Panoz_Esperante_GTR1` | Yes |
| Panoz | LMP1 Roadster S | 1999 | LMP | `Panoz_LMP1_Roadster_S_99` | Yes |
| Peugeot | 9X8 | 2024 | LMDh | `Peugeot_9X8_2024` | Yes |
| Porsche | 718 Cayman GT4 Clubsport | 2020 | GT4 | `Porsche_Cayman_GT4_Clubsport_2022` | Yes |
| Porsche | 911 Carrera Cup (964) | 1990 | 964 Trophy | `Porsche_Carrera_Cup_1990` | Yes |
| Porsche | 911 GT1-98 | 1998 | GT1 | `Porsche_911_GT1_98` | Yes |
| Porsche | 911 GT3 Cup (992) | 2024 | 992 Trophy | `Porsche_911_GT3_Cup_2022` | Yes |
| Porsche | 911 GT3 R (992) | 2023 | GT3 | `Porsche_992_GT3R` | Yes |
| Porsche | 911 GT3-RSR (996) | 2004 | N-GT | `Porsche_911_GT3-RSR_2004` | Yes |
| Porsche | 917K | 1970 | Sports Car 70 | `Porsche_917K_1970` | Yes |
| Porsche | 962C | 1988 | Group C | `Porsche_962C_88` | Yes |
| Porsche | 963 | 2023 | LMDh | `Porsche_963` | Yes |
| Saleen | S7R | 2004 | GT | `Saleen_S7R` | Yes |
| TVR | Tuscan T400R | 2004 | N-GT | `TVR_Tuscan_T400R_2002` | Yes |
| Toyota | GR Supra GT4 EVO | 2023 | GT4 | `Toyota_Supra_GT4` | Yes |
| Toyota | GR010 Hybrid | 2023 | LMDh | `Toyota_GR010` | Yes |
| Toyota | GT-One | 1998 | GT1 | `Toyota_GT-One_TS020` | Yes |

## V8PowerPack (9)

| Manufacturer | Car | Year | Class | Actor-folder ID | Active |
| --- | --- | ---: | --- | --- | --- |
| AMC | Javelin | 1971 | Historic USV8 | `AMC_Javelin_Trans_Am_1971` | Yes |
| Chevrolet | Camaro | 1969 | Historic USV8 | `Chevrolet_Camaro_Z28_Trans_Am_1969` | Yes |
| Chevrolet | Camaro | 2022 | USV8 | `TA2_Chevrolet_Camaro_2024` | Yes |
| Chevrolet | Camaro AU | 2023 | AUS V8 Evo | `Chevrolet_Camaro_V8Supercar_2024` | Yes |
| Dodge | Challenger | 2022 | USV8 | `TA2_Dodge_Challenger_2024` | Yes |
| Ford | Mustang | 2022 | USV8 | `TA2_Ford_Mustang_2024` | Yes |
| Ford | Mustang AU | 2023 | AUS V8 Evo | `Ford_Mustang_V8Supercar_2024` | Yes |
| Ford | Mustang Boss 302 | 1970 | Historic USV8 | `Ford_Mustang_Boss_302_Trans_Am_1970` | Yes |
| Plymouth | Barracuda | 1970 | Historic USV8 | `Plymouth_Barracuda_Trans_Am_1970` | Yes |

## WorldEndurancePack (11)

| Manufacturer | Car | Year | Class | Actor-folder ID | Active |
| --- | --- | ---: | --- | --- | --- |
| Audi | R18 | 2016 | LMP1 | `Audi_R18_etron_LMP1_2016` | No |
| BMW | March GTP | 1986 | GTP | `BMW_March_GTP_1986` | No |
| Chevrolet | Corvette C4 GTP | 1986 | GTP | `Chevrolet_Corvette_C4_GTP_1986` | No |
| Ford | Probe GTP | 1986 | GTP | `Ford_Probe_GTP_1986` | No |
| Jaguar | XJR-9 GTP | 1988 | GTP | `Jaguar_XJR9_IMSA_GTP_1988` | No |
| Nissan | GTP ZX-Turbo | 1988 | GTP | `Nissan_GTP_ZX_Turbo_1988` | No |
| Olivera | P2-13 | 2013 | LMP2 | `Olivera_13_LMP2_2013` | No |
| Olivera | P2-26 EVO | 2026 | LMP2 Evo | `Olivera_26_LMP2_2026` | No |
| Porsche | 919 Hybrid | 2016 | LMP1 | `Porsche_919_LMP1_2016` | No |
| Porsche | 962 GTP | 1988 | GTP | `Porsche_962_GTP_1988` | No |
| Toyota | TS050 | 2016 | LMP1 | `Toyota_TS050_LMP1_2016` | No |

## fordfalcon (2)

| Manufacturer | Car | Year | Class | Actor-folder ID | Active |
| --- | --- | ---: | --- | --- | --- |
| Ford | Falcon FG COTF | 2013 | AUS V8 | `Ford_Falcon_FG_V8Supercar_2013` | Yes |
| Holden | Commodore COTF | 2013 | AUS V8 | `Holden_Commodore_VF_V8Supercar_2013` | Yes |

## group5RevivalPack (5)

| Manufacturer | Car | Year | Class | Actor-folder ID | Active |
| --- | --- | ---: | --- | --- | --- |
| BMW | 320 Turbo Group 5 | 1978 | Group 5 | `BMW_320_Turbo_Group5` | Yes |
| Ford | Capri Group 5 | 1980 | Group 5 | `Ford_Zakspeed_Capri_Group5` | Yes |
| Nissan | Datsun 280 ZX Turbo | 1981 | Group 5 | `Nissan_280ZX_IMSA` | Yes |
| Nissan | Skyline Super Silhouette | 1983 | Group 5 | `Nissan_Skyline_KDR30` | Yes |
| Porsche | 935/80 | 1979 | Group 5 | `Porsche_935_80` | Yes |

## gtLegendsPack (9)

| Manufacturer | Car | Year | Class | Actor-folder ID | Active |
| --- | --- | ---: | --- | --- | --- |
| Chaparral | 2F | 1967 | Sports Car 67 | `Chaparral_2F_1967` | Yes |
| Chevrolet | Corvette C3 | 1973 | GT 70 | `Chevrolet_Corvette_C3_1973` | Yes |
| Chevrolet | Corvette Grand Sport | 1963 | GT 60 | `Chevrolet_Corvette_Grand_Sport_1963` | Yes |
| Ford | Capri RS3100 | 1973 | GT 70 | `Ford_Capri_RS3100_1973` | Yes |
| Ford | GT40 Mk.IV | 1967 | Sports Car 67 | `Ford_GT40_MkIV_1967` | Yes |
| Jaguar | E-Type Lightweight | 1964 | GT 60 | `Jaguar_E-Type_Lightweight_1964` | Yes |
| Lola | T70 Mk3 | 1967 | Sports Car 67 | `Lola_T70_MK3_67` | Yes |
| Porsche | 911 Carrera RSR 3.0 | 1974 | GT 70 | `Porsche_911_RSR_1974` | Yes |
| Shelby | Daytona Coupe | 1964 | GT 60 | `Shelby_Daytona_Coupe_1964` | Yes |

## gteDecadePack (7)

| Manufacturer | Car | Year | Class | Actor-folder ID | Active |
| --- | --- | ---: | --- | --- | --- |
| Aston Martin | AMR Vantage GTE | 2020 | GTE | `Aston_Martin_Vantage_GTE_2020` | Yes |
| BMW | M8 GTE | 2020 | GTE | `BMW_M8_GTE` | Yes |
| Chevrolet | Corvette C7.R | 2017 | GTE | `Chevrolet_Corvette_C7R_GTE` | Yes |
| Chevrolet | Corvette C8.R | 2020 | GTE | `Chevrolet_Corvette_C8R_GTE_2020` | Yes |
| Dodge | SRT Viper GTS-R | 2014 | GTE | `Dodge_SRT_Viper_GTS-R` | Yes |
| Ford | GTLM GTE | 2017 | GTE | `Ford_GTLM_GTE_2022` | Yes |
| Porsche | 911 RSR GTE | 2020 | GTE | `Porsche_911_RSR_GTE_2020` | Yes |

## japaneseGT500Pack (9)

| Manufacturer | Car | Year | Class | Actor-folder ID | Active |
| --- | --- | ---: | --- | --- | --- |
| Honda | Civic JP1 | 2024 | JP1 | `Honda_Civic_Type-R_GT500` | Yes |
| Honda | NSX JP1 | 2023 | JP1 | `Honda_NSX_GT500_2023` | Yes |
| Honda | NSX JP2 | 2003 | JP2 | `Honda_NSX_JGTC_2003` | Yes |
| Nissan | Calsonic Impul Z JP1 | 2022 | JP1 | `Nissan_Z_GT500` | Yes |
| Nissan | Fairlady Z (Z33) JP2 | 2004 | JP2 | `Nissan_350Z_GT500_2004` | Yes |
| Nissan | Motul Autech GT-R JP1 | 2021 | JP1 | `Nissan_GTR_R35_GT500` | Yes |
| Nissan | Skyline GT-R (R34) JP2 | 2003 | JP2 | `Nissan_GT-R_R34_JGTC_2003` | Yes |
| Toyota | GR Supra JP1 | 2022 | JP1 | `Toyota_GR_Supra_GT500` | Yes |
| Toyota | Supra JP2 | 2003 | JP2 | `Toyota_Supra_JGTC_2003` | Yes |
