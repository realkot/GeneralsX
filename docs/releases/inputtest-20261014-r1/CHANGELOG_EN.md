# GeneralsX r1 — changelog

- Separate buttons select combat units on screen or across the map, using native ownership and availability filters.
- Physical mouse support: left/right buttons, wheel zoom and held-middle-button camera panning; mouse and touch routing are separated.
- Expanded keyboard handling, corrected DIK codes, modifiers and held-state reset; Android text editing integration.
- First isolated ARM64 test package with 30/60 Hz engines. Initial validation did not cover a complete battle or all physical peripherals.

Package: `com.generalsx.zerohour.inputtest`; version `1.3.0-inputtest.20261014` (10301). Android 9+, ARM64, 30/60 Hz simulation engines; this does not guarantee frame rate. Supply original game data separately. Back up settings/saves before replacing an installed version; Android may reject a lower versionCode.

This publishes an existing APK without rebuilding. The archival publication tag points to the current r9 source/documentation snapshot; GitHub-generated source archives are not exact historical build trees. The corresponding current source snapshot is published for r9.

SHA-256: `6cfefca456624555d99969bb91a454675f497394a19ea3119afd83377e6a1f75`
