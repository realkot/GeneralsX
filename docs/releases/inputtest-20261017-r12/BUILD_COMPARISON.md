# Local r12 / GitHub r11 build timing

| Measurement | Local r12, retained WSL caches | GitHub r11 |
|---|---:|---:|
| Dual-engine build including configuration and APK packaging | 2m 29s | 44m 07s |
| Source sync + tests + successful dual build / entire GitHub job | 3m 10s | 49m 14s |

Local successful build phase was 17.66x faster in these runs. This is an observed result, not a controlled equal-cache benchmark.

## Failed first attempt and limits / Первая попытка и ограничения

- First local attempt: build 2m 07s, tests 0m 41s, source sync 0m 34s. It exposed a missing legacy LZHL include alias in the owned source mirror. The alias fix is commit `12dd033`; source archive bytes and compression logic were not changed.
- Elapsed from the start of the first local source sync to the final APK, including tests, failure and repair interval: **9m 02s**. This broader figure avoids hiding the first attempt and its cache warm-up.
- Local uses the existing WSL SDK/NDK/Gradle/vcpkg/ccache environment, 12 build workers; the successful retry reuses outputs from the failed attempt. No clean/rebuild or cache deletion was performed.
- Cloud source is r11; local source is r12. Hardware, source paths, cache state and dependency preparation differ. GitHub job includes checkout, SDK/cache preparation and artifact upload; local tests and source sync are separately measured.
- API evidence: [GitHub run 38907550035](https://github.com/realkot/GeneralsX/actions/runs/38907550035). No new Actions build dispatched.
- Локальная сборка использует сохранённые кеши, в том числе результаты неудачной первой попытки. Числа показывают практическое время двух разных запусков; это не сравнение на одинаковом оборудовании и с одинаковыми кешами.

## Successful local stage intervals

| Milestone until next milestone | Duration |
|---|---:|
| pass 1 of 2: 60 Hz engine | 0m 00s |
| [1/8] apt: ccache | 0m 00s |
| [2/8] Android SDK (cmdline-tools + NDK + platform-35 + build-tools) | 0m 00s |
| [3/8] ccache config | 0m 00s |
| [4/8] Bootstrap vcpkg (pinned commit 42e4e33e1505c9f47b58c21e0f557c1571b751ee) + sandbox patches | 0m 00s |
| [5/8] Pre-fetch CMake FetchContent sources vcpkg's patches don't cover | 0m 00s |
| [6/8] Configure CMake (Android) | 0m 35s |
| [7/8] Build z_generals + DXVK d3d8/d3d9 + hooks | 0m 04s |
| [8/8] Verify, strip, package APK | 0m 12s |
| BUILD SUCCEEDED: /opt/generals-input-test/GeneralsXZH-android-local.apk (65M) | 0m 00s |
| pass 2 of 2: 30 Hz engine, then package both | 0m 00s |
| [1/8] apt: ccache | 0m 00s |
| [2/8] Android SDK (cmdline-tools + NDK + platform-35 + build-tools) | 0m 00s |
| [3/8] ccache config | 0m 00s |
| [4/8] Bootstrap vcpkg (pinned commit 42e4e33e1505c9f47b58c21e0f557c1571b751ee) + sandbox patches | 0m 00s |
| [5/8] Pre-fetch CMake FetchContent sources vcpkg's patches don't cover | 0m 00s |
| [6/8] Configure CMake (Android) | 0m 35s |
| [7/8] Build z_generals + DXVK d3d8/d3d9 + hooks | 0m 58s |
| [8/8] Verify, strip, package APK | 0m 03s |
| BUILD SUCCEEDED: /opt/generals-input-test/GeneralsXZH-android-local.apk (84M) | 0m 00s |
| done: the APK carries libmain.so (30 Hz) and libmain60.so (60 Hz) | 0m 00s |
