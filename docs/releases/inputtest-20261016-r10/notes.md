# GeneralsX r10 — тестовый кандидат

- Новый раздел «Управление на планшете» в лаунчере; настройки сохраняются автоматически и применяются после полного перезапуска игры.
- Переключатель атаки в движении по умолчанию. Штатная команда принудительного движения и контекстные действия сохранены.
- Настройки кнопок армии: размер, ширина, прозрачность фона, отступы, отдельное скрытие и сворачивание. Подписи подбираются по измеренной ширине текста.
- Обычное нажатие «+» переключает группы; ПКМ или удержание «+» скрывает/показывает армейские кнопки.
- Размер физического курсора 100–250%, необязательная контрастная обводка. Виртуальный курсор тачпада настраивается отдельно.
- В Extras добавлены числовой ввод, кнопки «−/+» и пресеты высоты камеры 400/1000/2000/3600. Максимальная высота хранится с шагом 4; предел 3600 сохранён.
- Диагностика приказов включается из лаунчера: локальный журнал до 512 КиБ без вводимого текста и движения курсора, просмотр в приложении.
- После сброса ввода отбрасываются отпускания мыши без нового нажатия — защита от случайных действий при возврате из фона и отключении устройства.

Пакет `com.generalsx.zerohour.inputtest`, версия `1.4.1-inputtest.20261016-r10`, код `10310`. Панель справа и шесть HD-атласов сохранены. Рендеринг и AI этой итерацией не менялись; полоска высокой камеры и «Взлом спутников 2» не объявляются исправленными.

Это кандидат для проверки пользователем. Main остаётся на r9 до явного подтверждения успешного теста. Данные игры нужно предоставить отдельно. Перед заменой версии сохраните настройки и сохранения.

Проверено: оба движка собраны, 49 Android-тестов и регрессионные проверки пройдены; в MuMu запущены схватки 30/60 Гц. Проверка физической мыши и планшета ожидается от пользователя.

---

# GeneralsX r10 — test candidate

- New bilingual Tablet controls launcher screen. Preferences save automatically and require a full game-process restart.
- Optional default attack-move. Existing force-move shortcuts and contextual actions retain their behavior.
- Configure army-button size, width, background opacity, offsets, individual visibility and collapse. Fit captions using actual measured text width.
- A normal plus tap toggles control groups; right-click or hold plus to collapse/expand the army column.
- Physical cursor size 100–250 percent with optional contrast outline. Software-touchpad cursor settings remain separate.
- Exact numeric Extras fields, +/- buttons and 400/1000/2000/3600 camera presets. Manual maximum height uses the existing four-unit storage quantum; ceiling remains 3600.
- Opt-in private order diagnostics, bounded at 512 KiB, excludes typed text and pointer motion; view the log inside the launcher.
- Ignore unmatched releases after pointer cancellation to prevent stale clicks after backgrounding or device removal.

Package `com.generalsx.zerohour.inputtest`, version `1.4.1-inputtest.20261016-r10`, code `10310`. Retain the right HUD and six HD panel atlases. No renderer or AI behavior changes; the high-camera strip and Satellite Hack 2 are not claimed fixed.

This candidate awaits explicit owner testing. Main remains r9 until acceptance. Supply original game data separately and back up settings/saves before replacing an installed version.

Validation: both engines built, 49 Android tests and host regressions passed; 30/60 Hz skirmishes launched in MuMu. Actual tablet/mouse acceptance remains pending.
