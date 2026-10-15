# Graphics and AI rollback after input test r8

Date: 2026-10-15. The owner approved a source rollback, without a new APK.

## Baseline and scope

Fetched `main` directly from koreazolfakar-droid/GeneralsZH-Android-Port. Its tip is
3793ab15e7b8eecd9e2f8c3cec9b5b8a6c74bf0c, identical to this checkout's integration
base. Restore renderer/AI changes against that exact revision, while retaining
the owner's control-panel, input, camera and UI work.

## Reverted

- The r8 mass reconstruction of 97 additional game UI textures; their active
  mappings and packaged files are removed. All 14 Android launcher WebP resources
  are restored byte-for-byte from the pre-upscale r7 APK, with original hashes.
- GLES renderer changes: render worker, buffer snapshots/upload changes,
  terrain/light reuse, scene upscaling and custom present uncapping, sorting and
  depth-bias modifications. Restore associated CMake configuration to main.
- Adaptive HLOD and additional world-scene/shadow instrumentation. Keep only the
  six approved panel texture substitutions in the otherwise baseline W3DDisplay.
- Vehicle blocked-path retry policy; Project X skirmish-side expansion and
  archive-before-loose AI-script priority. AI update/pathfinding diagnostics and
  additional per-phase logic profiling are removed as well.
- Projectile-impact shroud reveal, restoring baseline visibility behavior.
- The GLES scene-upscaling launcher section and native Options-to-environment
  wiring. Existing backend selection remains available as in main.

Twenty-five complete source/build files now equal main. Shared files are edited
selectively. Inactive added sources/tests and textures are archived outside the
checkout rather than destroyed; the complete pre-rollback changed-file snapshot
is retained under the workspace's rollback-r8-graphics-ai/before directory.

## Preserved

- Right-aligned proportional HUD, playable left gap, bottom-left army selectors,
  plus toggle above them, group layout and interface scaling.
- Six r7 HD panel atlases, byte-identical, and their normalized UV/logical sizes.
- Physical mouse/keyboard support, cursor enlargement, click fixes, building
  hover preview and attack-move default. These are player input policies rather
  than autonomous AI modifications.
- Extras styling and behavior, manual camera ceiling 3600, owner-approved menu
  labels, startup EA-logo skip and previous loading-screen UI responsiveness fixes.
- Independent save/mod/audio/network/security improvements. CRC/replay revision
  handling remains; it is not AI decision logic.

The selected-folder delivery filter now admits only the six panel atlas names.
This also prevents stale r8 menu textures left in external storage from being
copied again. Such prefixed stale files are not selected by the six-entry native
mapping. No user data or build dependency environment is deleted.

## Validation and delivery boundary

The rollback audit verifies baseline equality for the 25 restored files, unchanged
hashes for 16 protected input/UI files, all six panel hashes, exactly six active
replacement entries and all 14 restored launcher hashes. Production host input,
camera, Extras, loading and layout regressions pass. All 47 Android tests pass,
including stale r8 menu-atlas exclusion during retained HUD delivery. The final
native compile/link check passes with the restored HLOD implementation. All 254
remaining files in the synchronized change set match the persistent WSL tree.
The delivered r8 APK hash is unchanged. No application APK assembly, installation or device rendering test is
performed for this source-only rollback; the previous installed r8 is unchanged.

The next explicitly requested test APK must use a new versionCode (10309 or later)
so the runtime extraction version gate refreshes the six-entry asset manifest.
Preserve the existing WSL/toolchains, dependency caches and old APKs.
