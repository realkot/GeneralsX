# GeneralsX r1 — изменения

- Две отдельные кнопки: боевая армия на экране и на всей карте; штатные фильтры принадлежности и доступности.
- Физическая мышь: ЛКМ/ПКМ, колесо для масштаба и удержание средней кнопки для перемещения камеры; разделение мыши и касаний.
- Расширена обработка клавиатуры, исправлены DIK-коды, модификаторы и сброс удержаний; добавлен Android-редактор текста.
- Первая отдельная тестовая сборка ARM64 с движками 30/60 Гц. Первоначальная проверка не охватывала весь бой и физическую периферию.

Пакет: `com.generalsx.zerohour.inputtest`; версия `1.3.0-inputtest.20261014` (10301). Android 9+, ARM64, движки 30/60 Гц; это частота симуляции, не гарантия FPS. Данные оригинальной игры нужно предоставить отдельно. Перед заменой установленной версии сохраните свои настройки и сохранения; Android может отклонить установку старого versionCode.

Это публикация ранее собранного APK без пересборки. Тег архивной публикации указывает на текущий снимок исходников r9 и документацию; автоматически сформированный GitHub архив исходников не является точным деревом старой сборки. Для r9 опубликован соответствующий текущий снимок исходников.

SHA-256: `6cfefca456624555d99969bb91a454675f497394a19ea3119afd83377e6a1f75`

---

# GeneralsX r1 — changelog

- Separate buttons select combat units on screen or across the map, using native ownership and availability filters.
- Physical mouse support: left/right buttons, wheel zoom and held-middle-button camera panning; mouse and touch routing are separated.
- Expanded keyboard handling, corrected DIK codes, modifiers and held-state reset; Android text editing integration.
- First isolated ARM64 test package with 30/60 Hz engines. Initial validation did not cover a complete battle or all physical peripherals.

Package: `com.generalsx.zerohour.inputtest`; version `1.3.0-inputtest.20261014` (10301). Android 9+, ARM64, 30/60 Hz simulation engines; this does not guarantee frame rate. Supply original game data separately. Back up settings/saves before replacing an installed version; Android may reject a lower versionCode.

This publishes an existing APK without rebuilding. The archival publication tag points to the current r9 source/documentation snapshot; GitHub-generated source archives are not exact historical build trees. The corresponding current source snapshot is published for r9.

SHA-256: `6cfefca456624555d99969bb91a454675f497394a19ea3119afd83377e6a1f75`
