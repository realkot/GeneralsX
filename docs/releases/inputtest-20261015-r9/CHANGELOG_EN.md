# GeneralsX r9 — changelog

- Retain the right-aligned HUD and its six HD atlases, bottom-left army/group controls, 2x cursor, mouse/keyboard support, Extras and the 3600 camera ceiling.
- Revert the broad r8 upscale: exclude 97 additional UI atlases and restore all 14 launcher rasters to r7.
- Revert additional renderer/GLES ZBIAS, terrain/light/HLOD/shadow, AI/pathfinding/script-priority and projectile-shroud changes. Rendering baseline is koreazolfakar-droid main.
- Validate package/signature/engines/assets; rollback sources passed 47 Android tests and production-code regressions. MuMu checks cover a GLA skirmish, right HUD, selectors and the 60 Hz engine launch.
- The GLES high-camera strip is not claimed fixed. Satellite Hack 2 is unchanged. Compatibility with every mod, multiplayer session and device is not established.

Package: `com.generalsx.zerohour.inputtest`; version `1.4.0-inputtest.20261015-r9` (10309). Android 9+, ARM64, 30/60 Hz simulation engines; this does not guarantee frame rate. Supply original game data separately. Back up settings/saves before replacing an installed version; Android may reject a lower versionCode.

This is the previously validated r9 APK, not a rebuild. The current source snapshot corresponds to r9; subsequent publication changes affect documentation and screenshots.

SHA-256: `e9dcf0c55300f6c1f8590458fa85387c2bac93205f9131bf25b0ab5319d3d4ae`
