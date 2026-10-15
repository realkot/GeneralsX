# Android input test r3 — 2026-10-15

Base: koreazolfakar-droid main `3793ab15`, retaining the approved r2 integration (candidates 1–7 and 9–20). Package: `com.generalsx.zerohour.inputtest`; version code 10303; version name `1.4.0-inputtest.20261015-r3`.

## Changes

- Five narrow buttons form a vertical column on the left above the minimap. Short labels retain the stock font size. The Ground button selects locally controlled combat units without aircraft, builders or harvesters: first press selects on screen, next press selects across the map. Another selection resets the cycle. Existing screen/map army and plane/helicopter buttons remain available.
- Ordinary positional orders for combat selections use the existing native attack-move command. Target interaction, waypoint, force-move and special contextual commands retain their existing paths. The native group implementation moves passive members normally in mixed groups; no new network message or AI behavior is introduced.
- The manual camera limit doubles relative to r2 (four times the original nominal range). Initial zoom and scripted camera behavior remain unchanged.
- Extras opens its bundled layout as a modal over Options instead of changing the shell stack. Its button uses scaled coordinates in the free header area. Apply updates the five camera/render settings and the Options draft; Cancel and Escape restore focus. The popup controls maximum/minimum camera height, camera pitch, scroll speed and terrain draw distance. Visual QA also exposed custom child system callbacks swallowing native label/slider setter messages, invalid slider/status/style tokens and malformed static-text data in the inherited Extras layout. Native child callbacks and valid retail fields now handle values and text. Army buttons likewise retain their native label handler and deliver selection to the parent owner.
- Mouse motion is coalesced only between adjacent compatible motion events. Button transitions use a non-lossy queue. Exact-capacity mouse frames retain the final event. A newly queued selection group can receive its first positional command before the translator cache catches up. Click and drag tolerances share one predicate scaled from display/viewport pixels to input-window pixels; time and camera-motion guards remain active.

## Diagnostics and evidence

Create `gx_input_trace.txt` in the game working directory and restart to enable right-button down/up diagnostics. Logging is disabled by default and does not log mouse motion. The queue, selection-cache and resolution issues are demonstrated by production-code regression fixtures; they are possible causes of the user's intermittent first-click problem, not a recorded trace of their physical mouse.

Production-code host tests cover event order and bursts, keyboard mapping, hover construction preview, aircraft/ground filtering, selection cycles, command routing, click tolerances, camera bounds, Extras lifetime/draft persistence and renderer policy. APK and emulator results are recorded in the accompanying Russian implementation report after validation. These tests do not establish real-phone behavior, multiplayer compatibility or performance gains.

## Visual validation

MuMu produced stretched geometry or a black scene in several runs. Some r2 and r3 controls rendered correctly, but font, upload synchronization, VAO lifetime and emulator restart trials did not establish a single cause. Experimental renderer changes were rejected. The final source preserves the r2 renderer, Mouse vtable and SDL3Mouse/InGameUI field layouts. The non-lossy queue and selection revision live outside those legacy objects. Overlay fonts retain their stock sizes, and Extras reuses the Options button font. The final combination rendered the GLA test scene for over five game minutes without the earlier artifacts; Extras applied settings and returned to the running battle. This establishes the tested final combination, not a unique cause for every rejected trial. Device results and limits are recorded separately in the Russian report.

## Persistent build environment

The existing WSL toolchain, SDK/NDK, dependency checkouts, native build tree, Gradle cache and compiler cache are reused. Packaging stages are moved into `build/packaging-history` rather than removed. `GX_PRESERVE_BUILD_ENV=1` stops on dependency mismatches before destructive repair. Compiler cache size is unlimited. Previous test APKs and source archives remain available for rollback. No WSL cleanup is performed.
