# Android input test r6 — wider selectors and GLES depth bias

User report: Xiaomi Pad 6S Pro, Logitech MX 3S mouse and tablet keyboard cover. The user identified r5 and stated that the rectangular artifact appears when the camera goes above the original height range. These are owner observations, not independent hardware validation. The exact map/save and selected renderer were requested.

## Changes

- Army selectors are 80 rather than 60 creation pixels wide (+33.3%). Their vertical placement and font size are unchanged. The expanded group row moves 20 creation pixels right and the parent bounds grow accordingly. This addresses text exceeding the button width without shrinking readable Russian labels. Existing resolution scaling is retained; it was not a text-to-button fitting algorithm.
- GLES now converts D3D8 ZBIAS to constant 24-bit depth-buffer units using the local DXVK D3D8 contract (`references/fbraz3-dxvk/src/d3d8/d3d8_device.cpp`, ZBIAS_SCALE `-0.000005`). The old conversion used two depth steps per unit and an additional slope term, whereas D3D8's value represents constant normalized depth. The old constant component was about 42 times weaker for 24-bit depth. Valid values 0–16 are bounded. Both the requested SDL depth buffer and offscreen renderbuffers are 24-bit in this backend.
- No camera limits, camera scripts, game logic, input routing, legacy class fields or virtual slots were changed. Vulkan/DXVK rendering is unchanged. r5's invisible Extras thumb decorations remain.

## Evidence and limits

The different depth-bias conversion is a demonstrated implementation discrepancy and a plausible cause of coplanar surface conflicts at greater viewing distances. It is not proof that the specific rectangular artifact in the owner's screenshot has been reproduced or eliminated. The view already computes its far clipping plane from terrain bounds, so no speculative far-plane expansion was added.

The original rectangular strip has not been independently reproduced on the tablet. MuMu is Android 15 with ARM64 translation and is not equivalent to the physical GPU. Do not claim a confirmed hardware fix from these checks. A temporary public repository Russian text BIG was used solely for QA and is not bundled in the APK. A separate temporary retail-data camera-height override was explored but did not establish an actual camera height; its screenshots are not proof of an 800-unit camera test.

## Validation

- Official dual-Hz build from one unchanged native/resource tree, using the preserved WSL setup and caches.
- APK manifest/version/signature/alignment/ZIP/native dependencies/JNI and exact WND resource checks passed.
- All 185 changed native/Java/resource files match the built Linux tree.
- 44 Android tests and production input, selection, camera, command, Extras, render-thread policy and upload regressions passed. Updated the pre-existing layout assertion for the new approved 80-pixel width.
- New test compiles the production depth-bias helper and checks normalized sign/scale, zero, every valid value and invalid-value bounds against the DXVK conversion.
- Russian selector labels were visually checked on the snowy Lone Eagle map, with the resource-only control APK first. Labels fit with padding; final native rendering checks are recorded in the enclosing workspace's validation-r6 evidence.

All earlier APKs, build directories, SDK/NDK/JDK/vcpkg/Gradle installations and caches remain. Temporary QA files and settings are archived/restored separately, without deleting the build environment. Private saves and retail reference data are excluded from the source delivery.

Final r6 native rendering was visually checked in the normal snowy scene at 3048×2032; Russian selector labels fit. Synthetic emulator wheel/keyboard input did not establish a reliable, stationary high-camera comparison, so the zoomed screenshots are not a confirmation that the owner's strip is fixed. The final installed APK is checked by hash separately from the earlier resource-only control. Original Options/language are restored and the temporary QA BIGs are moved into the QA archive before handoff.
