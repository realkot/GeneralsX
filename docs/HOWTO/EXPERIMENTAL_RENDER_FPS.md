# Experimental render FPS / Экспериментальная частота отрисовки

Launcher → Graphics → Render FPS (experimental). Choose Default / 30 / 60 / 90 / 120, then completely close and restart the game. Default keeps the old behaviour. This is a render target, not a 120 Hz simulation engine, frame generation or a measured performance promise.

Лаунчер → Графика → Частота отрисовки FPS (эксперимент). Выберите Штатный / 30 / 60 / 90 / 120 и полностью перезапустите игру. Для первого теста рекомендуются 60 Гц симуляции и 120 FPS отрисовки. «Штатный» возвращает прежнее поведение.

- Applies only to offline skirmish/campaign at normal game speed. Existing network, replay, accelerated game-speed and script-fast behaviour is retained.
- Симуляция сохраняет выбранные 30/60 Гц. Лимит отрисовки не ниже частоты симуляции: выбор 30 FPS с движком 60 Гц фактически даёт предел 60 FPS.
- This first experiment does not add interpolation or frame generation. Animations tied to logic ticks may still update at 30/60 Hz even when rendering is faster.
- В обычной скорости бой не должен ускоряться. Сравните таймер и время строительства одного здания за 60 секунд с режимом «Штатный», затем проверьте камеру, курсор и анимации. При ускорении игры или артефактах верните «Штатный» и сообщите карту, APK, частоты симуляции/отрисовки и GLES/ANGLE/Vulkan.
- Android gets a preferred supported display mode at the existing physical resolution and a Surface frame-rate hint (API 30+). This is advisory: OEM settings, display modes, thermal throttling and load can keep actual FPS lower. No vsync/shader/backend changes.
- Настройка частоты экрана Android и FPS-счётчик игры показывают разные вещи. 120 Гц экрана не подтверждают 120 кадров игры. На планшете включите высокую частоту экрана и сравните лёгкую и загруженную сцену.

Android API reference: [Frame rate](https://developer.android.com/media/optimize/performance/frame-rate).

Native regression compiles the actual FramePacer and offline logic gate for both simulation clocks and checks ten-second render schedules, default/invalid input, replay/network/custom speed, script fast mode and pause. Android tests cover persisted selection, independent simulation, replay launch reset and unsupported display rates. These checks do not replace an actual device run.

Rollback: choose Default, or use the previous r12 APK with the data-preserving ADB rollback helper. The feature is isolated in its own commit/branch; no application code is merged into main without owner acceptance.

## Pending resume fix / Исправление возобновления в исходниках

The published r13 APK is unchanged. Branch `codex/fix-render-resume-timing` removes the simulation clock dependency on mutable legacy FPS-limit flags and resets offline frame/logic/catch-up timing on focus/background/restore transitions. A fixed render target now remains independent even if the old limiter flag is cleared. Explicit fast modes, custom game speed, network and replay behaviour remain legacy.

Опубликованный r13 содержит прежний код. Исправление пока только в исходниках: независимый игровой такт сохраняется при сбросе FPS-флагов, а после сворачивания сбрасываются временные накопители. При повторном тесте нужны версия APK, симуляция/FPS и сведения, проходит ли ускорение само. Для диагностики добавлены строки `[GX-LIFECYCLE-TIMING]` с частотами и состоянием FPS-флагов. До новой тестовой сборки при проблеме используйте «Штатный» либо предыдущий APK.
