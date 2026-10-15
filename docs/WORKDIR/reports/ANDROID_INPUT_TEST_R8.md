# Android input test r8 — 2026-10-15

## Scope

The owner approved building r8 after requesting no earlier APK build. The test
application remains `com.generalsx.zerohour.inputtest`, versionCode 10308.

- Cap manually controlled Android camera height at 3600; clamp legacy stored
  nominal maximum values to 900. Initial and scripted camera policies stay intact.
- Anchor the proportional control bar to the right. The world remains playable in
  the left gap. Put the army selector column at the bottom left and the group
  toggle above it; use a readable fallback above the HUD when the gap is narrow.
- Change the main-menu footer to
  `GeneralsX [mod by realkot] github.com/realkot/GeneralsX` and the Options author
  prefix to `GeneralsX [mod by realkot]`, retaining CRC/version diagnostics.
- Supply 103 optional UI atlases at exactly four times the source dimensions.
  RGB reconstruction uses the preserved Real-ESRGAN x4plus model; original alpha
  is resampled separately. Six r7 atlases are reused byte-for-byte. Normalized
  image coordinates and logical widget sizes are unchanged.
- Reconstruct all 14 Android launcher WebP raster resources at 4x as well.
  Vector resources and text remain resolution independent.
- Extract the large pack once per APK version. Copy to the selected game folder
  only when the fingerprint changes or a delivered file is missing/truncated;
  never advance the fingerprint on an incomplete copy.

## Coverage and limitations

The supplied base-game and Zero Hour archives contain 103 of 121 texture names
referenced by the 18 mapped-image INIs. Eighteen names have no source file in
those archives; six are overridden completely, and twelve retain legacy mapped
definitions but no static WND reference. This does not prove they are unreachable
from game code or mods. Dynamic radar/maps, videos and generated font glyphs are
not offline raster textures. No unavailable texture is invented or silently
reported as upscaled. Resource inventory, output hashes and coverage details are
recorded in the accompanying validation directory.

The TGA pack occupies 1,370,108,163 bytes before APK compression. Its full set would
require about 2.52 GiB of uncompressed pixel storage if resident simultaneously;
actual runtime residency depends on the screens visited and engine caching.
Upscaling does not recover the original lost artwork and can sharpen small
raster lettering imperfectly. Full physical-tablet validation is still required.

The owner's high-camera GLES strip on Lone Eagle (4) remains unresolved. r8 does
not introduce a speculative renderer fix or claim that the camera cap fixes it.

## Validation

Production-code host regressions pass, including right-aligned HUD geometry and
the camera/army layout policy across screen and font scales. All 47 Android tests
pass. The actual UI texture substitution helper passes checks for all 103 entries,
case/path handling, missing-resource fallback and exclusion of world textures.
The official dual-Hz build completed successfully from one stable source/resource
tree. All 310 changed build-relevant files match the Linux build tree.

APK validation passes: package/version/label, unchanged debug certificate,
alignment, ZIP CRC, ARM64 dependencies, JNI exports, distinct built 30/60 Hz
engines, Window overrides and all 103 texture SHA-256 hashes. The APK is
846,484,722 bytes (807.27 MiB), SHA-256
`a09fb51c207b6aa7c861bb128981512ce343761016b8f0d3015fc180d426c0ca`.

MuMu Android 15/GLES checks covered the Russian main menu and both new labels,
Options, Extras open/apply/return, skirmish setup and completed skirmish loading.
China at 30 Hz and GLA at 60 Hz display the proportional HUD at the right and
readable selectors at the bottom left. The plus button opens a nonoverlapping
two-column group grid above the army column. Runtime logs confirm actual 4x
texture selection for visited screens and both factions. The 60 Hz run explicitly
loaded libmain60.so; tick rate is not an FPS guarantee. The internal game
resolution was 3048x2032 inside the 2560x1080 emulator surface.

The maximum-camera endpoint is established by production-code regression tests;
an injected touch in Extras saved nominal 461 (effective 1844), so that UI action
does not establish a measured 3600 camera height. No physical mouse/tablet test
or exhaustive visual traversal of every campaign/network/result menu is claimed.
Existing GLES world-geometry corruption was also visible during the 60 Hz shell
animation and near the upper edge of the GLA scene; it is distinct from UI
texture substitution and is not claimed fixed. The prior r7 validation already
recorded world-geometry artifacts. No renderer change was added in r8.

For this emulator run Android reported 769663 KiB total PSS in the GLA scene;
this is not a measurement of the complete host GPU allocation. Original test
settings and language are restored after QA; the temporary Russian text archive
is moved out of the game folder. The installed APK hash matches the delivered APK.

The persistent WSL installation, SDK/NDK, Gradle, dependency caches, upscaler and
all prior APKs are retained. No push, CI workflow or public release is requested.
