# GeneralsX r13 — experimental 120 FPS

## Changes since r12

- A separate render setting under Graphics: Default / 30 / 60 / 90 / 120 FPS. Legacy behaviour remains the default.
- Simulation remains on the existing 30/60 Hz engines. Extra rendered frames do not generate extra logic ticks or trigger game-speed catch-up.
- Applies only to normal-speed offline skirmish/campaign. Network games, replays, custom game speeds and fast scripts retain existing timing. The render limit cannot be lower than simulation Hz: selecting 30 FPS with the 60 Hz engine yields a 60 FPS limit.
- Android receives a supported display-rate request at the existing physical resolution and, on Android 11+, a Surface frame-rate hint. These are advisory; system policy, load and thermal throttling may lower actual FPS.
- Native regressions compile the actual FramePacer and logic gate for both engines, all four limits, default behaviour, replay/network, pause and fast modes. Android tests cover persistence, launching and supported display-rate selection.

No frame generation or interpolation was added. Logic-tied animations may still update at 30/60 Hz. Shaders, rendering backends and GeneralsOnline are unchanged.

## How to test

1. Launcher → Graphics: choose **60 Hz simulation** and **120 FPS rendering**.
2. Completely close/relaunch the game and start a normal-speed offline skirmish.
3. Compare the timer and one building construction over 60 seconds against Default. Game speed must not increase. Check cursor, camera and animations.
4. Report actual game FPS, device, graphics backend, simulation rate, heat and any problems. A 120 Hz screen does not prove 120 game FPS.

For problems, switch to Default and restart, or use the data-preserving ADB rollback to r12. Physical-device 120 FPS validation is pending. Version `1.4.4-inputtest.20261017-r13`, versionCode `10313`, unchanged package/signing identity. Main code is unchanged.
