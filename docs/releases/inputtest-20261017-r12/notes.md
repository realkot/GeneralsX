# GeneralsX r12 — тестовый prerelease

## Новое относительно r11

- Обновления APK прямо из лаунчера: автоматическая проверка наличия, ручная загрузка и подтверждение установки через Android. Источник — только Releases проекта realkot/GeneralsX.
- Стабильный/тестовый канал, описание изменений; проверка размера, SHA-256, имени пакета, версии и подписи APK перед установкой. Для тестового пакета prerelease включены по умолчанию.
- Языковые пакеты и используемые Android-ресурсы/исходники зависимостей перенесены в собственный репозиторий и ресурсный релиз. GeneralsOnline исключён из переноса; официальные инструменты SDK/NDK/JDK, Gradle/Maven остаются на своих источниках.
- Дополнен русский перевод лаунчера: 39 строк раздела модов, импорта, ошибок и подзаголовка.
- Добавлены инструкция и Windows-скрипт отката тестовых APK без удаления данных через ADB `install -r -d`. Обычный установщик Android не разрешает понижение версии; автоматический установщик предлагает только новые версии.
- Обновлены равнозначные README RU/EN и галерея: настройки планшета, моды, диагностика, Extras и два режима экранных кнопок.

Сохранены функции r11: мышь и клавиатура, выбор армии и групп, настройки курсора/кнопок, опциональная атака в движении, точные настройки камеры до 3600, панель справа и шесть атласов панели ×4. Графика, AI и GeneralsOnline этой версией не изменялись.

## Установка и статус

`1.4.3-inputtest.20261017-r12`, versionCode `10312`, пакет `com.generalsx.zerohour.inputtest`. ARM64, Android 9+, движки 30/60 Гц. Оригинальные данные Zero Hour нужны отдельно. Подпись сохраняется для установки поверх предыдущих тестовых APK; перед обновлением сохраните важные настройки и сохранения.

Локальная сборка в сохранённом WSL-окружении. Проверки и фактическое время приведены в отчёте релиза. Тест на физическом планшете и полный сценарий установки следующей версии через обновлятор ожидают проверки пользователем. Код main остаётся на принятой базе r9; этот prerelease не означает подтверждения теста.

---

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


## Verification / Проверки

55 Android tests: 0 failures, 0 errors, 0 skips. APK manifest, existing signing identity, ZIP alignment/CRC, ARM64 library dependencies, both distinct engines, six retained HUD atlases and compiled Russian strings passed. MuMu ADB was unavailable; no emulator/gameplay test is claimed.

Локальная финальная сборка: **2m 29s**; GitHub r11: **44m 07s** на соответствующий этап, **49m 14s** на всю задачу. С учётом первой неудачной попытки, тестов и исправления локально: **9m 02s**. Кеши и исходники отличаются — [подробный отчёт](https://github.com/realkot/GeneralsX/blob/release/1.4.3-inputtest-r12/docs/releases/inputtest-20261017-r12/BUILD_COMPARISON.md).

Successful local dual build: **2m 29s**; corresponding GitHub r11 phase: **44m 07s**, full job: **49m 14s**. Including the failed first attempt, tests and repair interval, local elapsed time was **9m 02s**. Hardware, sources and caches differ; see the report.
