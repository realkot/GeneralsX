# Android input test r9 — graphics/AI rollback build

Built locally on 2026-10-15 with the preserved official dual-Hz pipeline.
Package `com.generalsx.zerohour.inputtest`, versionCode 10309,
versionName `1.4.0-inputtest.20261015-r9`. This higher code refreshes the asset
extraction manifest on installations upgraded from r8.

The source is the approved graphics/AI rollback described in
ANDROID_GRAPHICS_AI_ROLLBACK.md. Twenty-five restored files equal upstream main
3793ab15e7b8eecd9e2f8c3cec9b5b8a6c74bf0c. Retained UI/input changes include the
right-aligned proportional HUD, bottom-left selectors, plus above the army column,
six unchanged r7 HD control-panel atlases, enlarged mouse cursor, input fixes,
manual camera ceiling 3600, Extras, owner labels and EA-logo skip.

The 97 additional r8 game UI atlases are absent from the APK. All 14 launcher
rasters match r7. The retained delivery filter excludes stale r8 menu atlases left
on external storage. Scene upscaling/render worker, terrain/light/HLOD/shadow
changes and added AI policies are reverted as documented in the rollback report.

Both engines are built from the same stable source/resource tree. APK verification
passes for package/version, signing compatibility, alignment, ZIP CRC, ARM64
dependencies, JNI exports, distinct built 30/60 Hz engines, WND overrides,
exactly six expected HD atlases with original hashes, and 14 restored launcher
resources. The rollback source already passed 47 Android tests, production host
regressions and native compile/link checks before this packaging run.

APK: 87,110,860 bytes. SHA-256:
`e9dcf0c55300f6c1f8590458fa85387c2bac93205f9131bf25b0ab5319d3d4ae`.

MuMu Android 15/GLES validation: the update installs over r8 without clearing
data. A GLA skirmish on Lone Eagle (4) at native emulator resolution 2560x1080
shows the proportional right HUD, readable bottom-left selectors and the group
grid above the plus toggle. Logs select only the retained panel HD atlases.
The 60 Hz engine explicitly loads libmain60.so and renders the main menu.
Original launcher/options/language settings are restored and temporary QA text
is archived outside the game folder. Installed and delivered APK hashes match.

The restored main renderer scales the whole frame when a saved resolution has a
different aspect ratio from the surface; native resolution was used for the HUD
visual check. No physical tablet or multiplayer compatibility result is inferred.
The owner's high-camera GLES artifact is not claimed fixed by the rollback.

WSL, SDK/NDK, Gradle, dependency caches, rollback snapshots and older APKs remain
available. No CI, remote push or public release is performed.
