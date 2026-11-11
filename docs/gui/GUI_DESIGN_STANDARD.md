# GUI / Visual System Standard

> Shared contract for application surfaces. This document is a design specification, not evidence that every repository ships a GUI.

## 1. Visual identity

| Token | Value | Use |
|---|---|---|
| Primary yellow | `#FFCC00` | Main action, selected object, key emphasis |
| Highlight yellow | `#FFE600` | Hover, active progress, focused controls |
| Deep black | `#000000` | Strong contrast, outlines, icon strokes |
| Graphite | `#1A1A1A` | Headers, panels, navigation and neutral surfaces |
| Alert red | `#E53935` | Errors, destructive warnings and critical states only |
| Signal cyan | `#29B6F6` | Live activity, data flow and non-error telemetry |
| White | `#FFFFFF` | Text and high-contrast details |

**Duck compatibility:** existing `design/duck-ui.tokens.json`, `assets/duck-ui/duck-ui.css` and the repository's duck mark remain the canonical shared implementation where already present. The colors above extend the visual brief; do not silently fork shared tokens or replace existing marks. A token migration must update the source tokens, CSS, previews, GUI code and quality checks together.

## 2. Reference workspace

- **Header:** left application mark; central system status, measured progress/load and activity trace; right local time in `HH:MM`.
- **Main workspace:** primary data canvas with optional dot grid, object/outline pane and free-input or annotation surface only where the product supports it.
- **Control region:** contextual actions and secondary controls, separated from the data canvas.
- **Footer/pager:** page or workspace navigation only when the application has multiple views.

The sample values `55`, `~~~~` and `21:33` are wireframe placeholders, never hard-coded production telemetry. Display real measurements with units, source and stale/unknown states. Do not animate a fabricated progress bar.

## 3. Interaction and feedback

- Long-running work is asynchronous, cancellable where safe, and reports queued/running/succeeded/failed states.
- Latency is measured and communicated; never rename a slow operation as a performance feature without evidence.
- Freehand/vector input preserves the original stroke and exposes validation or conversion results. Do not claim neural processing unless a tested model actually performs it.
- Headless-first modules expose documented CLI/API contracts. A GUI is an optional client/adapter, not an implied capability of a library or kernel.
- Critical/error state uses red; live telemetry uses cyan; yellow remains the primary action/focus color. Never encode state by color alone.

## 4. Accessibility and responsive behavior

Use visible keyboard focus, semantic labels, text/icon status cues, scalable layouts, high-contrast text and reduced-motion support. Target WCAG AA contrast (4.5:1 normal text, 3:1 large text). Controls should provide at least 44×44 CSS-pixel touch targets where touch input applies. Test keyboard-only operation, 200% zoom, narrow windows and reduced motion.

## 5. Repository-specific implementation boundary

- A desktop/web application may implement this layout with its native UI framework.
- A native library, firmware layer or runtime without GUI must document its host-facing API and may supply a demonstrator; it must not pretend to contain a GUI.
- A specification-only repository records the proposed GUI as a future contract. It must not imply a bootable OS, hardware support or runtime that does not exist.
- Put real screenshots and vector assets under `docs/gui/` or the existing asset structure. Label conceptual wireframes as **concept** and capture actual GUI only from a runnable build.

## 6. Release gate

A GUI change is ready when the changed surface has a documented purpose, keyboard/focus behavior, loading/empty/error states, responsive behavior, accessibility notes and a real screenshot or a clearly labelled wireframe. Update the relevant product README and localized README variants in the same change.

---

## Українська

Чорний і графітовий кольори формують основу; жовтий `#FFCC00` є головним акцентом, `#FFE600` — підсвічуванням, червоний `#E53935` — помилками, блакитний `#29B6F6` — активністю та потоками даних. Верхня панель показує реальний статус, виміряний прогрес і локальний час; центральна область містить робоче полотно; нижня — контекстні дії та навігацію. Значення `55 / ~~~ / 21:33` є лише прикладом макета. Для headless-бібліотек і системних компонентів GUI не вигадується: документуються CLI/API та зовнішні клієнти. Помилки, завантаження, порожні стани, клавіатурний фокус, масштабування й reduced motion є обов'язковими частинами специфікації.

## Русский

Чёрный и графитовый цвета образуют основу; жёлтый `#FFCC00` — главный акцент, `#FFE600` — подсветка, красный `#E53935` — ошибки, голубой `#29B6F6` — активность и потоки данных. Верхняя панель показывает реальный статус, измеренный прогресс и локальное время; центральная область содержит рабочее полотно; нижняя — контекстные действия и навигацию. Значения `55 / ~~~ / 21:33` являются только примером макета. Для headless-библиотек и системных компонентов GUI не выдумывается: документируются CLI/API и внешние клиенты. Ошибки, загрузка, пустые состояния, клавиатурный фокус, масштабирование и reduced motion входят в обязательную спецификацию.
