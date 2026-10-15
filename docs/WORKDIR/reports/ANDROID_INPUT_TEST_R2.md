# Android input test r2 integration

Base: koreazolfakar-droid main 3793ab15e7b8eecd9e2f8c3cec9b5b8a6c74bf0c.
Package: com.generalsx.zerohour.inputtest. Version: 10302 / 1.4.0-inputtest.20261014-r2.

The approved integration includes candidates 1–7 and 9–20 from the external branch audit, including save safety, campaign flow, command pages, bundled fonts, HUD scaling, HTTPS/bounds validation, audio, mods/ProjectX, responsive launcher, rendering/terrain buffers, guarded offline gameplay fixes, HLOD diagnostics, intro skipping, custom maps/virtual touchpad and touch momentum. Candidate 8 is excluded. File provenance is preserved in the external integration-files.json and branch patches. UpdateManager's progress API and its public verification key are launcher dependencies; engine OTA remains disabled in this test build.

Physical pointer ownership is represented by Mouse::hasContinuousPointer(). SDL3Mouse reports physical mouse or enabled virtual cursor; touch-only devices retain the touch aim. InGameUI uses this decision for placement ghosts and area previews. Modal windows suppress virtual touchpad gestures. Input lifecycle cancellation runs on the game thread.

Army buttons use width 78 and height 34 in the 800x600 WND coordinate system (previous width 122). Two new map selectors require AIRCRAFT and CAN_ATTACK and separate PRODUCED_AT_HELIPAD; the normal selectable-object filter remains responsible for ownership, dead/contained state and limits. A blanket TRANSPORT exclusion would incorrectly reject armed Helix units.

The Android user camera height limit is twice the nominal maximum. Initial zoom, scripted camera and explicit GameData overrides retain their semantics. Scoped private paths use GX_ANDROID_APP_ID so pre-bootstrap crash/logging and settings also resolve to the test package.

Verification: official dual-Hz build, APK signing/alignment/ZIP/native dependency checks, production input and selection/preview/camera fixtures, 14 QA suites, 44 Java/Robolectric tests. Negative TLS cases verify trust, hostname and redirect downgrade. Host tests do not demonstrate displayed gameplay, actual physical input dispatch or multiplayer compatibility. See external validation-next artifacts and the Russian delivery report for device results and limitations.

Visual bring-up caught a WND header error: this retail parser skips a fixed byte count and cannot accept a leading comment. Removed the comment and added a first-byte assertion. Repeated the complete dual-Hz build. MuMu displayed both engine menus and a 30 Hz skirmish; synthetic input remains separate from physical peripheral validation.

A controlled GLA comparison found stretched geometry with the GLES worker enabled and no such artifacts when only that worker was disabled. Keep the worker off by default; gx_gles_thread.txt is an explicit experimental opt-in and gx_gles_noopt.txt retains override precedence. Other graphics optimizations remain enabled. Both engines were rebuilt after this change. This is a default-policy mitigation, not a proven driver/root-cause repair. Production switch tests cover default, opt-in and override behavior.
