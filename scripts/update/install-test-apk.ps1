# GeneralsX @feature Codex 16/10/2026 Replace/downgrade test APKs without uninstalling or clearing data.
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$Apk,
    [string]$Serial,
    [string]$Adb,
    [string]$Aapt,
    [switch]$DryRun
)
$ErrorActionPreference = 'Stop'
$apkFile = Get-Item -LiteralPath $Apk
if ($apkFile.PSIsContainer -or $apkFile.Extension -ne '.apk') { throw 'Specify a single APK file.' }
$sdkRoots = @($env:ANDROID_SDK_ROOT, $env:ANDROID_HOME,
    (Join-Path $env:LOCALAPPDATA 'Android/Sdk'),
    (Join-Path ([Environment]::GetFolderPath('UserProfile')) 'AppData/Local/Android/Sdk')) |
    Where-Object { $_ } | Select-Object -Unique
$sdk = $sdkRoots | Where-Object { Test-Path -LiteralPath (Join-Path $_ 'platform-tools/adb.exe') } | Select-Object -First 1
if (-not $sdk) { $sdk = $sdkRoots | Select-Object -First 1 }
if (-not $Adb) {
    $candidate = Join-Path $sdk 'platform-tools/adb.exe'
    if (Test-Path -LiteralPath $candidate) { $Adb = $candidate }
    else { $Adb = (Get-Command adb -ErrorAction Stop).Source }
}
if (-not $Aapt) {
    $Aapt = Get-ChildItem -LiteralPath (Join-Path $sdk 'build-tools') -Filter aapt.exe -Recurse |
        Sort-Object FullName -Descending | Select-Object -First 1 -ExpandProperty FullName
}
if (-not $Aapt) { throw 'Android SDK aapt.exe is required; pass -Aapt with its full path.' }
$badging = & $Aapt dump badging $apkFile.FullName 2>&1
if ($LASTEXITCODE -ne 0) { throw "Could not read APK: $badging" }
$text = $badging -join "`n"
if ($text -notmatch "package: name='com.generalsx.zerohour.inputtest'") { throw 'Only the GeneralsX input-test package is allowed.' }
if ($text -notmatch '(?m)^application-debuggable\s*$') { throw 'The target APK must be debuggable for Android to allow a downgrade.' }
$installArgs = @('install','-r','-d',$apkFile.FullName)
if ($DryRun) {
    [pscustomobject]@{ Adb=$Adb; Serial=$Serial; Arguments=$installArgs; Package='com.generalsx.zerohour.inputtest'; PreservesData=$true }
    return
}
$devices = & $Adb devices
if ($LASTEXITCODE -ne 0) { throw 'ADB device discovery failed.' }
$ready = @($devices | ForEach-Object { if ($_ -match '^(\S+)\s+device\s*$') { $Matches[1] } })
if ($Serial) {
    if ($Serial -notin $ready) { throw 'The requested device is not connected and authorized.' }
} else {
    if ($ready.Count -ne 1) { throw 'Connect exactly one authorized device, or pass -Serial from adb devices.' }
    $Serial = $ready[0]
}
$output = & $Adb -s $Serial @installArgs 2>&1
$code = $LASTEXITCODE
$output | Write-Output
if ($code -ne 0 -or ($output -join "`n") -notmatch '(?m)^Success\s*$') {
    throw 'Android rejected replacement. Nothing was uninstalled or cleared. Check signing identity, debuggable status and the selected device.'
}
Write-Output 'Test APK replaced successfully; no uninstall or data-clear command was issued.'
