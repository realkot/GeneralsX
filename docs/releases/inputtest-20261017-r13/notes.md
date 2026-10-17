# GeneralsX r13 — эксперимент 120 FPS

## Новое относительно r12

- В разделе «Графика» добавлена отдельная частота отрисовки: Штатный / 30 / 60 / 90 / 120 FPS. По умолчанию остаётся штатный режим.
- Частота симуляции не меняется: прежние движки 30/60 Гц. В экспериментальном режиме дополнительные кадры не создают дополнительные игровые такты и не запускают механизм ускорения боя.
- Эксперимент действует только в офлайн-схватке/кампании на обычной скорости. Сеть, реплеи, изменённая скорость и ускоренные скрипты сохраняют прежний режим. Лимит FPS не ниже частоты симуляции: 30 FPS с движком 60 Гц означает предел 60 FPS.
- Android получает запрос поддерживаемой частоты экрана в текущем физическом разрешении и, на Android 11+, подсказку частоты для Surface. Это запрос, а не гарантия: ограничения системы, нагрузка и нагрев могут снизить FPS.
- Нативные проверки реального FramePacer и функции допуска игровых тактов охватывают оба движка, все четыре лимита, штатный режим, реплеи, сеть, паузу и ускорение. Android-тесты проверяют настройки, запуск и выбор доступной частоты.

Генерация кадров и интерполяция не добавлялись. Анимации, привязанные к игровым тактам, могут оставаться 30/60 Гц. Шейдеры, графические бэкенды и GeneralsOnline не менялись.

## Как проверить

1. Лаунчер → Графика: симуляция **60 Гц**, частота отрисовки **120 FPS**.
2. Полностью закройте и запустите игру. Начните обычную офлайн-схватку.
3. Сравните таймер и время строительства одного здания за 60 секунд с режимом «Штатный». Скорость боя не должна увеличиться. Проверьте курсор, камеру и анимации.
4. Сообщите FPS игры, модель устройства, графический режим, частоту симуляции, нагрев и замеченные проблемы. 120 Гц экрана не подтверждают 120 FPS игры.

Если появились проблемы, выберите «Штатный» и перезапустите игру либо откатитесь на r12 через ADB с сохранением данных. Физический тест 120 FPS пока не подтверждён. Версия `1.4.4-inputtest.20261017-r13`, versionCode `10313`, пакет и подпись прежние. Код main не изменён.

---

# GeneralsX r13 — experimental 120 FPS

## Changes since r12

- A separate render setting under Graphics: Default / 30 / 60 / 90 / 120 FPS. Legacy behaviour remains the default.
- Simulation remains on the existing 30/60 Hz engines. Extra rendered frames do not generate extra logic ticks or trigger game-speed catch-up.
- Applies only to normal-speed offline skirmish/campaign. Network games, replays, custom game speeds and fast scripts retain existing timing. The render limit cannot be lower than simulation Hz: selecting 30 FPS with the 60 Hz engine yields a 60 FPS limit.
- Android receives a supported display-rate request at the existing physical resolution and, on Android 11+, a Surface frame-rate hint. These are advisory; system policy, load and thermal throttling may lower actual FPS.
- Native regressions compile the actual FramePacer and logic gate for both engines, all four limits, default behaviour, replay/network, pause and fast modes. Android tests cover persistence, launching and supported display-rate selection.

No frame generation or interpolation was added. Logic-tied animations may still update at 30/60 Hz. Shaders, rendering backends and GeneralsOnline are unchanged.

## How to test

1. Launcher → Graphics: choose **60 Hz simulation** and **120 FPS rendering**.
2. Completely close/relaunch the game and start a normal-speed offline skirmish.
3. Compare the timer and one building construction over 60 seconds against Default. Game speed must not increase. Check cursor, camera and animations.
4. Report actual game FPS, device, graphics backend, simulation rate, heat and any problems. A 120 Hz screen does not prove 120 game FPS.

For problems, switch to Default and restart, or use the data-preserving ADB rollback to r12. Physical-device 120 FPS validation is pending. Version `1.4.4-inputtest.20261017-r13`, versionCode `10313`, unchanged package/signing identity. Main code is unchanged.


## Verification / Проверки

58 Android tests passed, plus native simulation-clock/logic-gate and release-parser checks. APK identity, existing signing certificate and both compiled engine libraries verified. Physical-device 120 FPS testing remains pending.

58 Android-тестов и нативные проверки прошли. Проверены пакет, прежняя подпись и обе библиотеки движка. Достижение 120 FPS на планшете пока не подтверждено.
