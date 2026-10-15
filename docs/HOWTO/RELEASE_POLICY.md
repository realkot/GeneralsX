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

Current baseline: r9, main `9e372c9`. Next candidate: r10, versionCode 10310,
versionName `1.4.1-inputtest.20261016-r10`, test package unchanged.
