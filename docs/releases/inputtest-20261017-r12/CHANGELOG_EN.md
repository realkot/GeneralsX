# GeneralsX r12 — test prerelease

## Changes since r11

- In-launcher APK updates: automatic availability checks, manual downloads and Android-confirmed installation. Only Releases from realkot/GeneralsX are used.
- Stable/test channel selection and release notes; APK size, SHA-256, package, version and signing identity verification before installation. Prereleases are enabled by default for the test package.
- Language packs and used Android dependency sources/resources are hosted in our repository and resource release. GeneralsOnline is excluded; official SDK/NDK/JDK tooling and Gradle/Maven keep their own distribution sources.
- Completed Russian launcher localisation: 39 mod-manager, import, error and subtitle strings.
- Added a Windows helper and instructions for data-preserving test APK rollback using ADB `install -r -d`. Android normal installation cannot downgrade; the automatic updater offers newer versions only.
- Updated equivalent RU/EN READMEs and screenshots covering tablet controls, mods, diagnostics, Extras and both on-screen button modes.

All r11 features remain: mouse/keyboard controls, army/groups selection, cursor/button settings, optional default attack-move, exact camera settings up to 3600, right-aligned HUD and six HUD atlases upscaled ×4. No graphics, AI or GeneralsOnline changes in this release.

## Installation and status

`1.4.3-inputtest.20261017-r12`, versionCode `10312`, package `com.generalsx.zerohour.inputtest`. ARM64, Android 9+, both 30/60 Hz engines. Original Zero Hour data is required separately. The existing signing identity is retained for installation over previous test APKs; back up important settings and saves first.

Built locally in the preserved WSL environment. Verification and measured build times are recorded in the release report. Physical tablet testing and the complete next-version updater installation flow await owner testing. Main application code remains based on accepted r9; publishing this prerelease does not constitute acceptance.
