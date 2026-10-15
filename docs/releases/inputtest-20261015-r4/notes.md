# GeneralsX r4 — изменения

- Восстановлены цифры групп 0–9 вместо MISSING; исправлены подписи кнопок и масштабирование шрифтов относительно разрешения.
- Раскрытая панель групп не перекрывает наземную кнопку. Extras оформлено в стиле штатных настроек: чёрный фон, синяя рамка, сегментные шкалы.
- Убраны избыточные перерисовки загрузки, обслуживание звука и ввода сохранено; ожидание брифинга сокращено со 100 до 16 мс.
- Оба движка собраны и проверены; ускорение любой загрузки на каждом устройстве не гарантируется.

Пакет: `com.generalsx.zerohour.inputtest`; версия `1.4.0-inputtest.20261015-r4` (10304). Android 9+, ARM64, движки 30/60 Гц; это частота симуляции, не гарантия FPS. Данные оригинальной игры нужно предоставить отдельно. Перед заменой установленной версии сохраните свои настройки и сохранения; Android может отклонить установку старого versionCode.

Это публикация ранее собранного APK без пересборки. Тег архивной публикации указывает на текущий снимок исходников r9 и документацию; автоматически сформированный GitHub архив исходников не является точным деревом старой сборки. Для r9 опубликован соответствующий текущий снимок исходников.

SHA-256: `a941829c432a7f2b2e815ab3e8f7f1288b050db6150f7150bcfee078bf157a6f`

---

# GeneralsX r4 — changelog

- Restore literal group digits 0–9 instead of MISSING; fix button captions and resolution-based font scaling.
- Keep the expanded group panel clear of the ground selector. Style Extras with the stock black/blue palette and segmented sliders.
- Coalesce redundant loading redraws while retaining audio/input service; shorten briefing waits from 100 to 16 ms.
- Build and validate both engines; no universal loading-time or frame-rate improvement is guaranteed.

Package: `com.generalsx.zerohour.inputtest`; version `1.4.0-inputtest.20261015-r4` (10304). Android 9+, ARM64, 30/60 Hz simulation engines; this does not guarantee frame rate. Supply original game data separately. Back up settings/saves before replacing an installed version; Android may reject a lower versionCode.

This publishes an existing APK without rebuilding. The archival publication tag points to the current r9 source/documentation snapshot; GitHub-generated source archives are not exact historical build trees. The corresponding current source snapshot is published for r9.

SHA-256: `a941829c432a7f2b2e815ab3e8f7f1288b050db6150f7150bcfee078bf157a6f`
