# GeneralsX — concise changelog

Compared with koreazolfakar-droid main (`3793ab15`) and MYSOREZ main (`576e2265`). The former is the direct baseline; selected parent-branch improvements retain their original attribution.


## Test candidates r10–r12

- **r12:** in-launcher APK updates with channels and integrity/signature checks; owner-hosted language packs and Android dependency resources; completed Russian mod-manager translation; data-preserving ADB rollback instructions/helper; refreshed RU/EN screenshot gallery.
- **r11:** immediate Extras slider-to-number synchronisation and prevention of stale values being applied.
- **r10:** army-button size, width, background, position, visibility and caption fitting; 100–250% cursor and outline; attack-move toggle and order logging; exact camera input, minus/plus controls and presets.

These are test candidates. Main game code remains based on accepted r9 pending explicit owner acceptance. No GeneralsOnline, graphics or AI changes in r12. [Full r12 changelog](docs/releases/inputtest-20261017-r12/CHANGELOG_EN.md).

## Current r9

- Army selectors: screen/map/planes/helicopters; ground combat cycles screen → map; groups 0–9 through the plus toggle.
- Physical mouse/keyboard routing, wheel zoom, middle-button camera panning and 2x cursor; corrections for event queues, first orders and hover building previews.
- Default ordinary combat movement uses attack-move; contextual and forced orders retain their behavior.
- Proportional right-aligned HUD, bottom-left controls and six retained 4x USA/China/GLA HD panel atlases.
- Manual camera ceiling 3600. Functional Extras styled like Options, without square thumb markers.
- Overlay captions/font scaling, literal group digits, loading redraws, EA-logo skip and realkot branding.
- Selected mod/launcher/theme, save/map, command-page, audio and network-safety backports.
- Broad r8 upscaling and additional renderer/AI experiments reverted; HUD positioning and HD panel assets retained.

## Version history

| Build | Main changes |
|---|---|
| r1 | Physical input, two army buttons, isolated test package |
| r2 | Branch integration, plane/helicopter selectors, building previews, camera |
| r3 | Vertical army controls, ground units, attack-move, functional Extras, mouse queues |
| r4 | Group digits/font scaling, Extras styling, loading redraws |
| r5 | Remove Extras thumb decorations; engines match r4 |
| r6 UI-control | Wider-button control build without the new native GLES change |
| r6 | Wider Russian buttons and experimental GLES ZBIAS; the latter later reverted |
| r7 | Centered proportional HUD, six 4x atlases, 2x cursor, EA-logo skip, repeated clicks |
| r8 | Right HUD, bottom-left controls, 3600 camera, branding; rejected broad upscale |
| r9 | Retain HUD/input; revert broad upscale and additional rendering/AI changes |

See [Releases](https://github.com/realkot/GeneralsX/releases) for every APK, bilingual notes and SHA-256, and [README](README.md) for screenshots. The high-camera GLES strip is not claimed fixed. Satellite Hack 2 is unchanged. Tests/MuMu do not certify every device, mod or multiplayer session. Archival tags mark publication of existing APKs, not exact historical source trees.
