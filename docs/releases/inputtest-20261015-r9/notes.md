# GeneralsX r9 — изменения

- Сохранены панель справа, её шесть HD-атласов, нижние левые кнопки армии/групп, курсор x2, управление мышью и клавиатурой, Extras и предел камеры 3600.
- Отменён массовый апскейл r8: удалены из активной поставки 97 дополнительных атласов; 14 изображений лаунчера возвращены к r7.
- Отменены дополнительные изменения рендеринга, GLES ZBIAS, terrain/light/HLOD/shadow, AI/поиска пути/приоритета скриптов и раскрытия тумана попаданиями. Графическая основа — main koreazolfakar-droid.
- Сборка прошла проверки пакета/подписи/движков/ресурсов; исходники отката — 47 Android-тестов и проверки реального кода. В MuMu проверены схватка ГЛА, панель справа, кнопки и запуск движка 60 Гц.
- Полоска высокой камеры GLES не объявляется исправленной. «Взлом спутников 2» не менялся. Полная совместимость всех модов, мультиплеера и устройств не подтверждена.

Пакет: `com.generalsx.zerohour.inputtest`; версия `1.4.0-inputtest.20261015-r9` (10309). Android 9+, ARM64, движки 30/60 Гц; это частота симуляции, не гарантия FPS. Данные оригинальной игры нужно предоставить отдельно. Перед заменой установленной версии сохраните свои настройки и сохранения; Android может отклонить установку старого versionCode.

Это ранее проверенный APK r9 без пересборки. Текущий снимок исходников соответствует r9; последующие изменения этой публикации касаются документации и скриншотов.

SHA-256: `e9dcf0c55300f6c1f8590458fa85387c2bac93205f9131bf25b0ab5319d3d4ae`

---

# GeneralsX r9 — changelog

- Retain the right-aligned HUD and its six HD atlases, bottom-left army/group controls, 2x cursor, mouse/keyboard support, Extras and the 3600 camera ceiling.
- Revert the broad r8 upscale: exclude 97 additional UI atlases and restore all 14 launcher rasters to r7.
- Revert additional renderer/GLES ZBIAS, terrain/light/HLOD/shadow, AI/pathfinding/script-priority and projectile-shroud changes. Rendering baseline is koreazolfakar-droid main.
- Validate package/signature/engines/assets; rollback sources passed 47 Android tests and production-code regressions. MuMu checks cover a GLA skirmish, right HUD, selectors and the 60 Hz engine launch.
- The GLES high-camera strip is not claimed fixed. Satellite Hack 2 is unchanged. Compatibility with every mod, multiplayer session and device is not established.

Package: `com.generalsx.zerohour.inputtest`; version `1.4.0-inputtest.20261015-r9` (10309). Android 9+, ARM64, 30/60 Hz simulation engines; this does not guarantee frame rate. Supply original game data separately. Back up settings/saves before replacing an installed version; Android may reject a lower versionCode.

This is the previously validated r9 APK, not a rebuild. The current source snapshot corresponds to r9; subsequent publication changes affect documentation and screenshots.

SHA-256: `e9dcf0c55300f6c1f8590458fa85387c2bac93205f9131bf25b0ab5319d3d4ae`
