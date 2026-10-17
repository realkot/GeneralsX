# r13 resume speed-up investigation

## Evidence and boundaries

The owner reports acceleration after lock/unlock or minimising/restoring. Exact APK/settings and whether acceleration persists are still unconfirmed; a clarification was requested. No physical-device reproduction or causal lifecycle log is available in this iteration.

A deterministic r13 defect is reproduced: `isRenderOnlyRateActive()` depends on both mutable legacy FPS-limit flags through `isActualFramesPerSecondLimitEnabled()`. Clearing either disables fixed simulation timing, allowing one logic tick per rendered frame. A regression expecting the independent clock to survive fails against r13, then passes after the fix. This confirms a failure mode, not that Android clears that flag in the reported case.

Separately, mobile lifecycle handling skips simulation/render updates without resetting presentation interval, fractional logic time or accelerated-game catch-up debt. Suspended wall time could reach the resumed update. The existing min/clamp bounds this, so it is not proof of a sustained acceleration on its own.

## Changes

- Separate explicit fast-time overrides from legacy FPS-enable flags. The opted-in normal-speed offline render clock no longer drops its simulation cap when a limiter flag changes. Default mode, explicit fast modes/custom game speed, network and replay behaviour retain their prior paths.
- Add a monotonic presentation timer reset and initialise its delta to one finite nominal frame, avoiding division by zero in client FPS queries.
- Queue lifecycle reset requests atomically in the SDL watcher; apply only on the engine thread. Reset fractional logic accumulation and catch-up debt for offline non-replay sessions, including focus loss/gain, background/foreground and minimise/restore.
- Add bounded lifecycle timing diagnostics: render limit, original game-speed FPS, simulation/logic Hz, independent-mode status and limiter flags. No per-frame logging or user input content.

## Validation

Production FramePacer, actual regular-logic gate, catch-up routine, SDL lifecycle watcher and resume-consumption block are compiled into a host regression harness. Checks pass for both 30/60 Hz clocks, all four render targets, both dropped limiter flags, 50 ms / 5 s / 120 s suspended intervals, repeated and same-poll minimise/restore, finite reset deltas, cleared catch-up debt and network/replay exclusions. Parser release/debug preprocessing checks also pass. A separate harness executes the actual monotonic FrameRateLimit implementation across a 150 ms wall-time pause: reset returned a finite 0.008333 s frame interval, matching 0.008334 s spent waiting, without incorporating the paused interval.

Four actual Android NDK release objects compile: FramePacer, FrameRateLimit, GameEngine and SDL3GameEngine. Java/resources are unchanged, so Android UI tests were not repeated. No new APK was built or published; r13 tag/assets and main are unchanged. Existing WSL/toolchains/caches/logs remain intact. Fix source is in `codex/fix-render-resume-timing` and requires a future explicitly requested candidate build plus owner device testing.
