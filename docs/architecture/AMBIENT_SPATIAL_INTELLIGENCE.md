# Ambient + Spatial Intelligence: repository implementation profile

> Status: **proposal / implementation workstream**. This document defines ownership and acceptance criteria; it does not claim that the capabilities are already implemented.

## Program context

This profile combines two user-provided visual references into one product direction:

1. **Contextual system surface**: clock/date, grouped notifications, media controls, weather/context cards, quick actions and trusted emergency alerts.
2. **Spatial/environmental intelligence**: image and scene processing, lighting and reflection analysis, surface/material cues, geometry, camera/sensor abstractions and optional 3D reconstruction.

The target is a modular capability layer for NUN, not a clone of a mobile lock screen. Existing repository identity, license, language, build system and release process remain authoritative.

## Cross-cutting architecture

- **Contracts first:** versioned schemas and ABI definitions are owned by Kloz.
- **Kernel stays small:** NUN exposes bounded primitives only; policy, AI and providers remain user-space services.
- **UI stays replaceable:** Luci supplies components; NUNLauncher consumes them only in a qualified user-session target.
- **No assumed hardware:** camera, GPU/NPU, sensors, network and location are optional capabilities discovered at runtime.
- **Provenance is mandatory:** every external datum carries source, timestamp, expiry and trust state.
- **Emergency truth is fail-safe:** stale, missing or unauthenticated data is never presented as a verified all-clear.
- **Privacy by default:** no face identification, covert capture, or remote upload without explicit opt-in and an auditable permission boundary.
- **Evidence-based maturity:** planned, specified, implemented, tested and integrated are separate states.

## Common event envelope

Every event should carry: schema version, event ID, source ID, event type, monotonic and wall-clock timestamps where available, priority, payload reference, expiry, privacy classification, provenance/trust status and correlation ID. Payload sizes and queue depth must be bounded. Consumers must tolerate duplicate, delayed, out-of-order and unknown-version events.

## Common spatial data envelope

Spatial data must declare coordinate frame, units, handedness, origin, timestamp, sensor/source identity, confidence, calibration revision and validity interval. Image buffers must declare pixel format, dimensions, plane layout, stride, memory ownership, synchronization/fence state and lifetime. No implicit coordinate conversion or buffer ownership transfer is allowed.

## Delivery sequence

1. Contracts and fixtures.
2. Host-side validators and deterministic simulators.
3. Runtime adapters and bounded queues.
4. Accessible dashboard components.
5. Optional vision/spatial providers.
6. Hardware qualification and federation.

## Release gates

- Existing tests and build targets remain green.
- New APIs are versioned and have positive/negative fixtures.
- Unsupported hardware is reported as unavailable, not simulated as present.
- Privacy, provenance, expiry, resource bounds and failure behavior are tested.
- Documentation distinguishes prototype, host-tested, emulator-tested and hardware-qualified behavior.

## Repository ownership

**Primary responsibility:** SDK, language tooling and application integration.

**Implementation boundary:** Provide typed libraries and developer tools so applications consume stable contracts without depending on NUN internals.

### Initial work package
- Define SDK packages for events, widgets, media sessions, environmental data, spatial primitives, camera sessions, permissions and automation
- provide sample apps and schema/code generation.

### Explicit non-goals
No kernel implementation, privileged camera access, or silently networked telemetry.

### Acceptance criteria
Compile-time API compatibility tests; deterministic fixtures; schema validation; sample app build and test in CI.

## Workstream map (18 × 37)

The program backlog is organized into 18 workstreams with 37 independently tracked items each (666 total for this repository). Items must be written as repository-owned deliverables with an ID, contract/dependency, test evidence and status; no generic duplicate shells are accepted. Workstreams:

1. Context/event model
2. Notification lifecycle
3. Emergency provenance and expiry
4. Media/session integration
5. Clock/calendar/context providers
6. Widget/component contracts
7. Spatial coordinate model
8. Image/frame-buffer pipeline
9. Camera/sensor capability model
10. Lighting and photometric analysis
11. Reflection and surface cues
12. Material and object metadata
13. Scene graph and geometry
14. Optional 3D reconstruction
15. Privacy and permission boundaries
16. Resource limits and degraded mode
17. Diagnostics, simulation and test evidence
18. Federation, packaging and release compatibility

The 666-item backlog is a planning target, not a claim that 666 implementations exist. Promote each item only when its acceptance evidence is attached.
