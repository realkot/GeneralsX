# Test APK rollback without uninstalling

Android permits `adb install -r -d` for debuggable packages. `-r` replaces the existing application, and `-d` requests versionCode downgrade. The normal APK installer and an unprivileged launcher cannot grant this permission to themselves.

Reference: https://android.googlesource.com/platform/packages/modules/adb/+/refs/heads/main/docs/user/adb.1.md

## Windows / PowerShell

Enable USB debugging (or pair wireless debugging), authorize the PC, and download the older original test APK from this repository's Releases. No root is needed for this ADB path.

```powershell
# Direct command, with platform-tools/adb on PATH:
adb install -r -d "C:\Downloads\GeneralsZH-InputTest-20261016-r10.apk"

# Repository helper: discovers Android Studio's SDK and checks package/debuggable status:
.\scripts\update\install-test-apk.ps1 -Apk "C:\Downloads\GeneralsZH-InputTest-20261016-r10.apk"

# Multiple connected devices:
.\scripts\update\install-test-apk.ps1 -Apk "C:\Downloads\older.apk" -Serial DEVICE_SERIAL

# Validate the APK and display arguments without installing anything:
.\scripts\update\install-test-apk.ps1 -Apk "C:\Downloads\older.apk" -DryRun
```

The target must be the same `com.generalsx.zerohour.inputtest` package and signing identity. Published test builds are debuggable; new debug builds explicitly preserve this setting. Android checks the installed signing identity. If installation fails, the helper does not uninstall, clear data or re-sign/repackage the APK. The versionCode remains honest; a historical APK is not relabelled as a newer release.

A successful replacement retains app-private preferences, external game data and saves, though compatibility of newer settings/save formats with an older game build still needs testing. Return to the newer APK by installing it normally. Automatic APK updates continue to offer only higher versionCode; downgrades use the explicit ADB path. GeneralsOnline is unchanged.
