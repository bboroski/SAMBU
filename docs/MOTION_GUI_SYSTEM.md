# Motion & GUI system — SAMBU

**Version:** 1.0  
**Adoption type:** repository-scoped presentation contract  
**Status:** design and engineering requirements; runtime capabilities must be verified independently.

## 1. Purpose and scope

This contract unifies animation, motion design, dynamic visualization, rendering, user-interface behavior and interaction feedback without turning independent products into one runtime. The vocabulary includes animation/multiplication, movement, kinetic response, morphing, transformation, interpolation, rendering, simulation, deformation, frame-based motion, micro-interactions, transitions, motion effects, dynamic graphics, computer animation, GUI, user interface, visual interface, application shell, control panel, workspace, screen environment, navigation and interaction surfaces.

The vocabulary describes possible presentation techniques and product surfaces; it is not a requirement to implement every technique in every binary. A repository adopts only the capabilities supported by its actual product, platform and safety boundary.

## 2. Layering and invariants

Use the following direction of dependency:

`domain state → presentation model → interaction controller → renderer`

- Domain logic owns facts, lifecycle, evidence, device state and business outcomes.
- The presentation model maps domain facts to labels, values, accessible names and visual states.
- The interaction controller handles input and schedules optional visual changes.
- The renderer draws the current state. It must not infer domain truth from animation progress.
- Animation is decorative or explanatory presentation. It must never trigger a destructive action, alter a deadline, delay a safety interlock, or imply that an operation succeeded before its real result is available.
- Keep UI dependencies out of firmware, kernel, portable ABI, integrity, validation and other non-presentation cores.

## 3. Motion primitives and timing

Use motion only where it improves orientation, causality or feedback:

| Token | Default | Intended use |
|---|---:|---|
| `motion-none` | `0 ms` | Reduced motion, critical state changes, static fallback |
| `motion-fast` | `110 ms` | Press/release and focus feedback |
| `motion-standard` | `180 ms` | Hover, selection and small state transitions |
| `motion-slow` | `240 ms` | Panel reveal, route/view change and short disclosure |
| `motion-max` | `320 ms` | Upper bound for ordinary interface transitions |

Use a monotonic clock for timed animation. Prefer opacity and transform over layout-affecting properties. Keep interpolation bounded and deterministic; cancel superseded transitions. Avoid spring overshoot, parallax, large zooms and perpetual motion by default. Any longer explanatory sequence must be user-started, pausable and skippable.

Supported techniques are: keyframe animation, interpolation/easing, transform, morphing between compatible visual states, frame-by-frame playback, progress visualization and simulation. Each technique must have a static equivalent and a clear relationship to the underlying data.

## 4. Interaction and visual states

Every interactive component must define the applicable states explicitly: idle, hover, keyboard focus, pressed, selected, pending, success, warning, error and disabled. Do not rely on hover alone. Pending must not be presented as success; unknown must remain distinct from failure.

Prefer small feedback cues: a visible focus ring, a restrained press response, a state-label change, a short reveal, or an explicit progress indicator. Keep important information visible while motion runs. For async operations, progress must come from real work signals or be labelled indeterminate; never fabricate a percentage.

## 5. GUI and accessibility contract

- Preserve semantic controls, accessible names, keyboard operation, logical focus order and visible focus.
- Use text or an icon in addition to color for status, warning, selection and failure.
- Maintain the repository's existing design tokens and native platform conventions; do not introduce a second competing theme.
- Support resizing, text scaling, high contrast and touch targets appropriate to the platform.
- Honor the platform's reduced-motion preference. On the web, implement `prefers-reduced-motion: reduce`; on desktop, honor the operating-system accessibility setting where available.
- Reduced-motion mode must remove or instantly settle decorative transforms, parallax, morphing and nonessential autoplay while preserving information, navigation, focus, progress and task completion.
- Auto-updating or looping motion must be avoidable and, when it persists, provide a pause/stop mechanism.

## 6. Rendering and lifecycle

Rendering must be non-blocking and bounded. Do not run animation work on a critical worker, interrupt, device callback or real-time lifecycle path. Stop timers, animation frames and callbacks when a view is hidden, replaced or disposed. Avoid unnecessary redraws; pause work in background tabs/windows. Degrade to a static state when a renderer, GPU feature or animation API is unavailable.

For browser surfaces, prefer CSS transitions/keyframes for simple UI motion and reserve `requestAnimationFrame` for genuinely frame-driven visualizations. For native surfaces, use the platform's existing event loop and accessibility APIs. Never add a browser engine, graphics library, scheduler or runtime dependency solely to satisfy this document.

## 7. Verification and acceptance

A UI or motion change is acceptable only when:
1. the same task is usable with motion disabled;
2. keyboard focus and keyboard-only operation remain correct;
3. the reduced-motion path is explicitly checked;
4. state labels and status values reflect real application state;
5. animation callbacks are cancelled on navigation/teardown and do not leak;
6. scaling, narrow layouts and high-contrast behavior are checked where applicable;
7. the relevant project build/tests and documentation checks pass.

Prefer deterministic tests with a controllable clock or scheduler. Test state transitions and cancellation directly; avoid flaky tests that depend on real-time frame timing. Visual previews are not proof of a running feature, and host tests are not hardware qualification.

## 8. Repository integration profile

SAMBU має Python-based IDE/Studio з Tkinter GUI та окремий CLI. Візуальні переходи дозволені лише у presentation layer Tkinter; застосовувати cancellable after()-callbacks на UI thread, не блокувати event loop і скасовувати всі відкладені callbacks під час закриття вікна. Спільний duck-ui.css не керує Tkinter-віджетами. До появи runtime-реалізації базовий режим — статичний інтерфейс із коротким, ненав'язливим відгуком.

## 9. Rollout boundary

This contract is introduced as an isolated, reviewable change. It does not claim that all listed animation types, GUIs, renderers or client applications already exist. Implementations must be added in the owning presentation layer, tested against the checks above, and documented as implemented only after runtime evidence exists. Existing APIs, ABI, formats, build targets, permissions and repository responsibilities remain unchanged.
