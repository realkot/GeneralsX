# Owner-hosted resources and external dependency audit

Scope: Android application downloads and the active dual-Hz Android build. Historical documentation, inactive Apple/Windows/Linux targets and reference-only submodules are inventoried separately, not silently rewritten. No original commercial game data is redistributed.

| Dependency | Previous source | Owner location / treatment |
|---|---|---|
| APK updates | Test APK disabled; signed engine-only parent updates | `realkot/GeneralsX` Releases, `update.json` and exact APK asset; package/version/digest/signature validation |
| 12 language packs | MYSOREZ main | `resources/languages` in this repository, preserving existing translations and attribution |
| SDL3 3.4.2, SDL3_image 3.4.0, OpenAL Soft 1.24.2 | GitHub FetchContent/git | Pinned owner-hosted source snapshot, revision manifest, original licenses retained |
| GamespySDK, lzhl, adrenotools and nested sources | Upstream Git repositories | Same source snapshot from the retained build; CMake source overrides |
| DXVK fork and nested sources | fbraz3 submodule | Same source snapshot, including the already applied platform patches; no renderer behavior change intended |
| vcpkg third-party source archives (FFmpeg, OpenSSL, protobuf, GameNetworkingSockets, etc.) | Multiple original download URLs | Retained source-download cache mirrored in the snapshot; `VCPKG_DOWNLOADS` points there; installed-port copyright notices included |
| Liberation 2.1.5 fonts | liberationfonts GitHub | Original archive mirrored unchanged; existing SHA-256 retained, OFL notices inside archive |
| Turnip 25.3.0 R11 | K11MCH1 release | Original binary archive mirrored unchanged, now checksum-pinned. Mesa/KIMCHI attribution preserved; binary archive does not include a separate license file |
| Vulkan validation 1.4.357.0 | KhronosGroup release | Original diagnostic archive mirrored unchanged, now checksum-pinned; Khronos/Apache licensing remains upstream |
| Legacy signed config used by GeneralsOnline | koreazolfakar updates branch/key | Retained unchanged at the owner's explicit request not to touch GeneralsOnline. Launcher APK updates are independent; native updates remain disabled for the test package |
| GeneralsOnline community datapack | cdn.playgenerals.online | **Excluded by explicit owner instruction:** do not change GeneralsOnline. Existing code, manifest and endpoint retained; observed HTTP 403 is only an audit finding |
| Login/API/STUN/TURN and CnC-online | Live third-party game services | Services, not downloadable files; retained. Hosting these services requires a separate backend project |
| Android SDK/NDK, JDK, Gradle/Maven, vcpkg tool/registry, apt packages | Official vendors | Toolchain/distribution infrastructure, retained as agreed. Not presented as fully offline or entirely self-hosted |
| Apple/Linux/Windows-only dependencies and reference submodules | Various original sources | Not active Android downloads. Retained and listed by the generated URL inventory; no untested platform rewrites |

## Snapshot provenance

`Dependencies/android-mirrors.json` records bytes, SHA-256, source revisions and owner download URLs. The source snapshot was made from the preserved r11 build environment, not reconstructed from unverified latest branches. Existing source patches are included. `.git`, credentials, signing material, SDKs and game data are excluded. Original license files inside source trees/archives and vcpkg copyright notices are retained. Files retain original authorship; mirroring does not transfer copyright.

The build uses owner-hosted archives by default via `prepare-owned-dependencies.py`. Existing DXVK checkout, dependency caches and build environment are preserved; nonempty incompatible directories fail rather than being deleted. A hash mismatch fails closed. New transitive dependency versions require refreshing the mirrored source cache; otherwise a tool may still need its vendor distribution. No claim of a fully offline fresh build is made without a fresh-build test.

## Validation and limits

No APK or Actions build was requested for this iteration. Java/Robolectric tests, metadata checks, source-archive integrity, preparation smoke tests and script syntax checks are recorded in the follow-up report. A future release must be built and tested before these launcher changes are advertised as available in an APK. Published r11 remains unchanged. Main remains owner-gated.
