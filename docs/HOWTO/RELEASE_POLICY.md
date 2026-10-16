# Owner release policy

Effective 16 October 2026; this explicit owner instruction supersedes older branch,
APK cleanup and publication examples in AGENTS.md and inherited guides.

- Develop on `codex/<feature>` branches. Commit each independently reversible
  feature separately and push completed changes to realkot/GeneralsX.
- Build candidate APKs locally from `release/<version>`, with an unchanged tree
  throughout the official dual-Hz build. Assign a strictly increasing versionCode,
  unique versionName, tag, bilingual notes and SHA-256 to every delivered candidate.
- Publish candidates as prereleases. Never infer owner acceptance from passing
  tests, emulator checks, elapsed time or download activity.
- Merge a candidate into main only after the owner explicitly confirms successful
  testing of that exact release. Until then main remains the last accepted version.
- Preserve APKs, signing material, WSL, SDK/NDK, Gradle and dependency/build caches.
  Deleting or recreating the build environment requires separate owner permission.
- Roll back one feature through its documented `git revert` commit and its runtime
  switch where applicable. Do not rewrite published history or reuse a release tag.
- Do not dispatch GitHub Actions. Preserve upstream licenses and attribution.

Current baseline: r9, main `9e372c9`. Latest published candidate: r11, versionCode 10311,
versionName `1.4.2-inputtest.20261016-r11`, test package unchanged.
The APK updater and owner-resource migration are newer source changes, not included in r11.

## Launcher APK update metadata

Every future application release must attach `update.json` after uploading the APK.
Use `scripts/update/publish-apk-update-metadata.py --tag TAG --package PACKAGE --code CODE --version VERSION --apk ASSET_NAME`
with a short-lived `GH_TOKEN`/`GITHUB_TOKEN` in the environment, never in command text or Git.
The metadata takes size and SHA-256 from GitHub's uploaded asset, is immutable once
published, and must describe the verified APK manifest. It does not publish a new
release, merge main, rebuild the APK or silently install anything on a device.
The launcher only accepts assets from realkot/GeneralsX, higher versionCode,
matching package and signing identity. Test prereleases are enabled by default
only for the input-test package. Stable-channel selection excludes prereleases.
Publish both Russian and English notes in the release body and as attachments.

Source/resource snapshots live in the `resources` branch and the
`android-dependencies-20261016` resource release. Do not label that release as a
new game APK or mark it latest. See the external dependency audit for the owner-excluded
GeneralsOnline datapack and the intentionally retained official toolchains/services.
