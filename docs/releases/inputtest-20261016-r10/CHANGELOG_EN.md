# GeneralsX r10 — test candidate

- New bilingual Tablet controls launcher screen. Preferences save automatically and require a full game-process restart.
- Optional default attack-move. Existing force-move shortcuts and contextual actions retain their behavior.
- Configure army-button size, width, background opacity, offsets, individual visibility and collapse. Fit captions using actual measured text width.
- A normal plus tap toggles control groups; right-click or hold plus to collapse/expand the army column.
- Physical cursor size 100–250 percent with optional contrast outline. Software-touchpad cursor settings remain separate.
- Exact numeric Extras fields, +/- buttons and 400/1000/2000/3600 camera presets. Manual maximum height uses the existing four-unit storage quantum; ceiling remains 3600.
- Opt-in private order diagnostics, bounded at 512 KiB, excludes typed text and pointer motion; view the log inside the launcher.
- Ignore unmatched releases after pointer cancellation to prevent stale clicks after backgrounding or device removal.

Package `com.generalsx.zerohour.inputtest`, version `1.4.1-inputtest.20261016-r10`, code `10310`. Retain the right HUD and six HD panel atlases. No renderer or AI behavior changes; the high-camera strip and Satellite Hack 2 are not claimed fixed.

This candidate awaits explicit owner testing. Main remains r9 until acceptance. Supply original game data separately and back up settings/saves before replacing an installed version.

Validation: both engines built, 49 Android tests and host regressions passed; 30/60 Hz skirmishes launched in MuMu. Actual tablet/mouse acceptance remains pending.
