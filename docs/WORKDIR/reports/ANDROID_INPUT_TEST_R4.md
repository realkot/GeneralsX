# Android input test r4 — UI text and loading follow-up

Base: koreazolfakar main `3793ab15e7b8eecd9e2f8c3cec9b5b8a6c74bf0c`, cumulative approved r2/r3 changes.
Package: `com.generalsx.zerohour.inputtest`; version code 10304; version `1.4.0-inputtest.20261015-r4`.

## Changes

- Assign group numbers 0–9 through the native literal-text message. Numeric WND TEXT values were being interpreted as localization keys and displayed as `MISSING`.
- Scale GroupPanel and Extras fonts once while parsing their layouts, using the smaller ratio to the 800×600 creation resolution, combined with the existing interface scale and capped at 100 points. Keep retail layouts unchanged and avoid live font mutation or legacy class/vtable layout changes.
- Place the expanded control-group row to the right of the army column. The ground selector remains reachable.
- Keep Extras buttons' native system callback so literal labels are applied and owner notifications reach the existing modal controller. Use the stock filled/empty slider segment artwork, a black background, blue frame/section rules and matching action buttons. Existing apply/cancel/defaults behavior remains.
- Coalesce Android loading redraws within 33 ms while servicing platform events and audio on every callback. Always draw completion notifications. This removes redundant GPU submissions without delaying loader work with sleeps.
- Replace explicit 100 ms briefing waits with 16 ms waits and platform/audio servicing. Guard progress division for very short movies. The two-general screenshot belongs to the Challenge loading path; ordinary skirmish uses MultiPlayerLoadScreen.

## Validation

- Official dual-Hz build completed from one unchanged native/resource tree. Both ARM64 engines packaged.
- APK package/version, matching signing certificate, alignment, ZIP CRC, native dependency closure, JNI entry points, distinct 30/60 Hz engines and exact WND assets passed.
- All 185 changed native/Java/resource files match the Linux build tree.
- 44 Android unit tests passed, as did production input, mouse ordering/tolerance, selection/camera, command routing, Extras lifecycle, renderer and upload regressions.
- New host fixture compiles the actual production font and loading functions. At a fixed clock, 1000 intermediate progress callbacks submit no additional frames after the first, while audio and input receive every callback. Tests cover the next timed frame, immediate completion, clock rollover and quitting.
- MuMu VM 0, Android 15 with ARM64 translation: 3048×2032 internal render resolution on a 1920×1080 window. English Extras labels and stock-style sliders are readable; Escape returns to Options. The 30 Hz GLA skirmish reaches battle and literal group digits are visible without covering the ground selector.
- Russian Extras literal labels were visually checked, including the long camera labels and all three buttons. A forced Russian test language initially had no matching retail table; the added loose STR was not resolved by the existing game-data localization path, so full Russian menu localization is not claimed. Temporary language settings/files are archived and original language restored.

## Evidence limits and preservation

The 60 Hz Challenge with Granger reached battle at 3048×2032 but showed a stretched polygon. A control run using the preserved, hash-verified r3 APK, the same resolution/settings/general/difficulty also failed to render the world correctly after its intro (black world with visible HUD). The two runs establish instability in this MuMu scenario; they do not isolate a unique cause or prove identical defects. No renderer changes were made for r4. This scenario is not certified clean. The r4 30 Hz GLA skirmish screenshots show a correctly rendered scene. Final r4 was reinstalled after the control and the original Options/launcher settings were restored and compared byte-for-byte.

The loading changes remove demonstrated redundant rendering and a hardcoded 10 fps briefing wait. They do not make synchronous map/resource loading asynchronous. Emulator screenshots are not a frametime comparison on the user's physical device, and do not prove that all reported stutter is eliminated. Long-duration, physical mouse and multiplayer certification are outside this follow-up.

Existing WSL source/build directories, SDK/NDK/JDK/vcpkg/Gradle installations and caches remain. r3/r2 artifacts remain. Test settings and saves were backed up before updating MuMu. Private backups and retail reference assets are excluded from the distributed source archive.
