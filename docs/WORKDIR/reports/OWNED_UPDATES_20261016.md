# Project presentation, APK updater and owner-hosted Android resources

Branch: `codex/project-docs-and-owned-updates`, based on the unmerged r11 release branch. Main remains `9e372c9` (r9). No owner acceptance inferred from screenshots. No new APK or Actions run in this iteration.

## Delivered

- Russian README and equivalent English README, concise mod-specific features, installation and limitations; four owner-supplied tablet screenshots.
- `docs/WORKDIR/publication/4PDA_POST_RU.txt`: ready-to-copy IP.Board/4PDA BBCode. Image links use the immutable documentation commit. The post is an artifact, not a message posted to the forum.
- Independent launcher APK updates from realkot/GeneralsX Releases: startup check enabled by default, manual check, stable/test channel selection, bilingual UI, release notes, explicit download, progress, size/SHA256/package/version/signing checks, standard Android permission and installation UI. No silent install. Verified cached downloads survive the install-permission round trip; rejected caches are preserved and retried. A new APK must be built to deliver this feature; published r11 is unchanged.
- `resources` branch holds the twelve existing language packs; runtime download endpoints point there. All twelve verified over HTTPS against the original Git blobs.
- Owner resource release: https://github.com/realkot/GeneralsX/releases/tag/android-dependencies-20261016 . Source snapshot, unchanged font/Turnip/validation archives, original notices and checksums; CMake and packaging use owner mirrors. No graphics, gameplay or AI behavior changes intended.
- Immutable `update.json` metadata attached to r11, matching its existing APK digest, bytes, package and version. Reusable publisher helper and release policy document the same step for every future APK release.

## Explicit exclusions

The owner said **do not touch GeneralsOnline**. Its activities, session, datapack installer, UpdateManager, UpdateTrust, signed config/key, authentication, services and endpoints are unchanged from the r11 baseline. APK startup preferences and check logic are separate. The CDN HTTP 403 remains an audit observation, not a pending migration or claimed fix.

Official SDK/NDK/JDK, Gradle/Maven/vcpkg tooling/distribution infrastructure and live gaming services remain external. Inactive platform/reference-only dependency declarations are inventoried, not rewritten. This is not a claim of an entirely offline fresh build; the owner-source snapshot restores the known Android build inputs, and a fresh native build still needs validation.

## Evidence

- Final Android test task: 55 tests, 0 failures, 0 errors, 0 skips. UI construction/persistence suites plus candidate channel/package/version/digest guards, signing identity mismatch and corrupt downloads. No live system-installer or new APK/device test claimed.
- Source archive: 193,233,284 bytes, SHA256 `5e0df096ae074d050a8d9908832b9aac081ad54723426082d0bc07e93ab8cba3`. Integrity, safe extraction, CMake source mappings and edited shell syntax passed. Existing caches/DXVK were retained.
- Mirrored Turnip and four Liberation fonts compare byte-identical to the existing r11 APK.
- All 12 owner-hosted language files compare byte-identical to repository blobs. Live r11 update.json agrees with GitHub's uploaded APK digest/size; no APK replacement.
- README local links and post spoiler/image structure verified. Source/resource licenses and provenance are recorded in the dependency audit and mirror manifest.

## Rollback

| Feature | Commit |
|---|---|
| Bilingual presentation and screenshots | `9ddae60` |
| APK updater, separate preferences and metadata publisher | `5cf06cb` plus the cache-retry follow-up |
| Language/resource mirrors and Android source preparation | `c5dfdb4` |

Revert the relevant feature and its associated tests/docs on a new branch; do not rewrite published history. Keep `resources` and resource release assets available for already delivered clients. Source preparation and the source manifest belong together. Preserved WSL, SDKs, Gradle, native build trees, dependency caches and old APKs were not deleted or recreated.
