# Android input test r7

## Changes

- Center the bottom control bar in its original 4:3 proportions. Its artwork and window hit rectangles use the same GXUiScale transform, including at 100% launcher UI scale. Keep army shortcuts on the screen's left edge. Render the 3D scene to the bottom wherever the centered panel leaves side gaps.
- Optional 4x HUD reconstruction: six named retail atlases for USA, China and GLA. RGB was processed locally using the official Real-ESRGAN portable v0.2.5.0 package, `realesrgan-x4plus`, tile 256. Transparency is the original mask resized separately with Lanczos. Normalized UVs, logical image dimensions and command icons remain unchanged. Optional assets have unique `gx_hd_` names, retail fallback, and update on APK upgrades.
- Double native physical-mouse cursor art and hotspots on Android; retain original software-touchpad art and original-size fallback on allocation failure.
- Skip only the Android EA startup logo; retain the existing intro/sizzle state transitions and launcher preferences.
- Refresh double-click press anchors in MetaEventTranslator and SelectionTranslator so a nearby quick repeated order is not measured from the previous click position.

## Evidence boundaries

The owner's thin strip persists in r6 on Lone Eagle (4), GLES, above nominal camera height. The r6 depth-bias candidate was insufficient. No additional speculative renderer change is included solely to hide it. Its cause and correction remain under investigation; do not call it fixed.

Host tests compile actual production input/layout code with service mocks; they do not establish physical mouse reliability or tablet GPU rendering. Native build, unit tests, packaging checks and MuMu visual validation are recorded separately under workspace `validation-r7/`.

## Asset provenance

Original assets came from the user's installed licensed game data. This test APK contains reconstructed HUD derivatives, not the rest of the game. The six original and output hashes and dimensions are recorded in the workspace `validation-r7/hd-assets-manifest.json`. The installed portable upscaler and all existing build tools/caches are retained. No environment cleanup, deletion, push or CI run is requested.

Upscaler source: https://github.com/xinntao/Real-ESRGAN

## Final validation

- Official dual-Hz native build passed. Final resource/Java follow-ups reused every native library byte-for-byte; no native edit occurred between engine passes.
- 45 Android tests passed, including installation/update of only the six owned atlases into the selected game folder, preservation of unrelated textures and shared-root handling.
- Existing production input/selection/Extras/font/loading/render-upload regression suites passed. New compiled production press cases and the complete GXUiScale parser/transform passed five aspect ratios at 100/125/150/200/300 percent UI scale.
- All 193 changed native/Java/resource files, including six binary TGA assets, match the WSL build tree. APK signature matches the previous test releases; package/authorities, alignment, ZIP CRC, ARM64 dependencies, JNI, distinct 30/60 engines and exact asset contents passed.
- MuMu displayed the centered GLA HUD in the 30 Hz engine and China HUD in the 60 Hz engine at internal 3048x2032, letterboxed into its 2560x1080 window. Actual loading of both corresponding HD atlas pairs is logged. Options button placement, Extras presentation/application and return to battle were exercised. USA assets have offline reconstruction/packaging checks, not a separate displayed USA battle check in this pass.
- GLES in MuMu also showed intermittent large scene polygons/terrain patches, including with the control r6 before installation of r7. A subsequent frame after temporary camera-limit adjustment and the nominal-height China run were clean. This is not an isolated reproduction of the owner's thin strip: camera pose was not instrumented/locked, so no cause or fix is claimed.
- Native physical cursor dimensions/hotspots are doubled in the source and both binaries. Host press regressions establish the corrected anchor behavior; the Logitech/tablet physical-device path still needs owner validation.
- Startup with the launcher intro preference enabled reached the 60 Hz menu. The Android build excludes the EA-logo calls; this check did not independently record every startup frame or establish sizzle-video playback.

Final test identity: `com.generalsx.zerohour.inputtest`, `10307`, `1.4.0-inputtest.20261015-r7`.
APK SHA-256: `01c93485d1ea4880146e53541603eb0fef28ccdc8222f02ae448aa3562b33c1a` (87,223,063 bytes).
