# GeneralsX r11 — test prerelease

## Changes since r10

- Fixed all five Extras sliders updating their numeric fields immediately on clicks, dragging and keyboard changes.
- Apply no longer restores an outdated value from a stale numeric field.
- Clicking the current position refreshes that field while preserving unfinished edits in other fields.
- Added production callback regressions for every slider and immediate Apply without a periodic layout update.

Retains r10 features: army-button and physical-cursor settings, default attack-move toggle, mouse-order diagnostics, exact Extras values and camera presets, right-aligned HUD and six HD HUD atlases. No renderer or AI changes in this version.

## Build and validation

Version `1.4.2-inputtest.20261016-r11`, versionCode `10311`, test package `com.generalsx.zerohour.inputtest`. Includes 30 and 60 Hz engines. Signing matches previous test APKs, allowing in-place updates.

[GitHub Actions: successful build and package checks](https://github.com/realkot/GeneralsX/actions/runs/38907550035). Source regressions passed. Actual tablet/mouse testing and confirmation of the fix in the installed APK remain pending; a successful build is not gameplay acceptance.

This is a test candidate. Main stays on r9 until explicit owner acceptance. Original Zero Hour game data is required separately. Previous builds are retained; Android may reject an in-place downgrade.
