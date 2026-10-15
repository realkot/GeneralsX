# GeneralsX r4 — changelog

- Restore literal group digits 0–9 instead of MISSING; fix button captions and resolution-based font scaling.
- Keep the expanded group panel clear of the ground selector. Style Extras with the stock black/blue palette and segmented sliders.
- Coalesce redundant loading redraws while retaining audio/input service; shorten briefing waits from 100 to 16 ms.
- Build and validate both engines; no universal loading-time or frame-rate improvement is guaranteed.

Package: `com.generalsx.zerohour.inputtest`; version `1.4.0-inputtest.20261015-r4` (10304). Android 9+, ARM64, 30/60 Hz simulation engines; this does not guarantee frame rate. Supply original game data separately. Back up settings/saves before replacing an installed version; Android may reject a lower versionCode.

This publishes an existing APK without rebuilding. The archival publication tag points to the current r9 source/documentation snapshot; GitHub-generated source archives are not exact historical build trees. The corresponding current source snapshot is published for r9.

SHA-256: `a941829c432a7f2b2e815ab3e8f7f1288b050db6150f7150bcfee078bf157a6f`
