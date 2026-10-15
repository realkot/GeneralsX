# Android tablet controls r10 candidate

Version: `1.4.1-inputtest.20261016-r10`, versionCode `10310`.
Package: `com.generalsx.zerohour.inputtest`.
Release branch: `release/1.4.1-inputtest-r10`. Owner acceptance: **pending**.
Main remains r9 (`9e372c9`) until explicit owner confirmation of this candidate.

## Scope

- Bilingual launcher tablet-control screen with atomic, bounded startup preferences.
- Opt-in local button/translation/click/order/dispatch tracing, wrapped at 512 KiB;
  no typed text or continuous pointer motion. View the private log from the launcher.
- Optional default attack-move; the existing force-move and contextual paths remain.
- Army button scale, width, background opacity, offsets, individual visibility,
  startup collapse and measured caption fitting. Normal plus tap toggles groups;
  right-click or a long press on plus toggles the army column.
- Physical cursor 100–250 percent, consistent hotspot and optional contrast outline.
  The existing software-touchpad cursor remains separate.
- Extras exact numeric fields, +/- steps and 400/1000/2000/3600 camera presets.
  Existing camera storage quantizes manual maximum height to multiples of four.
- Reject unmatched physical releases after focus/device/gesture cancellation.

Close the game process completely before applying changed launcher settings.
The right-aligned HUD, six HD panel atlases, renderer/AI rollback and 3600 ceiling
remain. The high-camera strip and Satellite Hack 2 are outside this iteration.

## Feature rollback

Runtime rollback: turn off diagnostics, attack-move, caption fitting and outline
individually; restore panel defaults or set cursor to 200 percent. Reset restores
the candidate's baseline preferences without clearing game data.

Source rollback: revert feature commits in a new branch, preserving published
history. Use the matching regression changes and rerun tests. Shared preference
and trace interfaces are dependencies: retain those interfaces if later features
still call them; do not delete shared headers while reverting only their hooks.

| Change | Primary commit(s) |
|---|---|
| Shared preference contract and release policy | `83deaf5` |
| Launcher screen and persistence | `8bb9f96` |
| Diagnostic hooks and private path | `7967057`, `0a8440b` |
| Default attack-move setting | `7f68f45` |
| Physical cursor | `2a150ad` |
| Army panel and preserved colors | `1e9d144`, `0bed112` |
| Exact Extras controls | `394dfe6` |
| Orphan-release handling | `5023023` |

Every delivered replacement APK must receive a higher versionCode and a fresh tag;
an older release remains available for recovery but Android may reject a downgrade.

## Validation

Host production-code regressions and Android UI tests passed before native release
building. Native build, package verification and emulator checks are recorded after
completion. Emulator/host tests do not establish Logitech/tablet hardware behavior,
all mods or multiplayer compatibility. No owner acceptance is inferred from tests.
