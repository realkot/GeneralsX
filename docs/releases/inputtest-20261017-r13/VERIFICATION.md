# r13 experimental rendering verification

- Source commit: `f509ec1e858e407903cd81d9dee6713a3394907c`. Both simulation engines built locally from this immutable candidate, package `com.generalsx.zerohour.inputtest`, versionCode 10313, versionName `1.4.4-inputtest.20261017-r13`.
- Final dual-Hz build: 138.7 seconds with preserved caches. Preliminary/superseded attempts and their logs/APKs are retained locally; this figure is only the final successful build.
- Android regression suite: 58 tests, no failures/errors/skips.
- Native tests compile the production FramePacer and actual regular-logic gate for 30/60 Hz engines. Ten-second schedules at 30/60/90/120 render targets retain their simulation tick counts, within one accumulated float tick. Network/replay/default/invalid/custom speed/fast script/pause cases pass.
- Preprocess the actual command registration table and implementation in release/debug configurations; real NDK release parser object also compiles. Both shipped engine libraries contain `-gxRenderFps`.
- APK package/version/debuggable identity, previous signing certificate, ZIP CRC/alignment, ARM64 architecture and DT_NEEDED dependencies, distinct 30/60 Hz engines, JNI, army/Extras WNDs, all six retained HUD atlases and old launcher artwork passed.
- Compiled RU/EN rendering labels verified. Same test package/signing key, no data clearing.
- No shader/backend, GeneralsOnline, network protocol or simulation-rate constant changes. Network/updater source diff against r12 is empty.
- Physical-device FPS, smoothness, battery/thermal behaviour and visual animation quality are **not validated**. No interpolation/frame generation is claimed. Menu/network/replay/custom-speed behaviour remains legacy; only normal-speed offline battles opt in. Unsupported OEM/display policies may keep frame rate lower.
- Default remains legacy. Choose Default and restart to disable, or use ADB rollback to r12. Main code is unchanged and owner acceptance is pending.

## Feature rollback

Revert feature `f1e6c46` together with the release-parser follow-ups `29d4db5` and `f509ec1` on a new branch, then remove associated candidate-only notes if needed. Do not rewrite published tags or APK identity. Runtime fallback: Default.
