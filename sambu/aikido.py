"""Aikido: provider-neutral, policy-driven neural model orchestration.

Aikido never opens a network connection by itself. Hosts inject provider adapters,
which own credentials, transport security, timeouts and provider-specific protocols.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Mapping, Protocol, Any
import time
import uuid


class AikidoError(RuntimeError):
    """Base class for orchestration failures."""


class NoModelAvailable(AikidoError):
    """No enabled model satisfies the requested capability and budget."""


class InferenceExhausted(AikidoError):
    """All selected adapters failed after the configured retry policy."""

    def __init__(self, message: str, failures: tuple[str, ...] = ()):
        self.failures = failures
        super().__init__(message)


class BudgetExceeded(AikidoError):
    """An inference result exceeds the request's maximum estimated spend."""


@dataclass(frozen=True, slots=True)
class ModelProfile:
    identifier: str
    provider: str
    capabilities: frozenset[str] = frozenset({"chat"})
    context_window: int = 32_000
    max_output_tokens: int = 4_000
    input_cost_per_1k: float = 0.0
    output_cost_per_1k: float = 0.0
    priority: int = 100
    latency_hint_ms: int = 1_000
    enabled: bool = True
    fallback_models: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.identifier.strip() or not self.provider.strip():
            raise ValueError("model identifier and provider are required")
        if self.context_window < 1 or self.max_output_tokens < 1:
            raise ValueError("model token limits must be positive")
        if self.max_output_tokens > self.context_window:
            raise ValueError("max_output_tokens cannot exceed context_window")
        if self.input_cost_per_1k < 0 or self.output_cost_per_1k < 0:
            raise ValueError("model costs cannot be negative")
        if self.latency_hint_ms < 0:
            raise ValueError("latency hint cannot be negative")


@dataclass(frozen=True, slots=True)
class InferenceRequest:
    prompt: str
    task: str = "chat"
    required_capabilities: frozenset[str] = frozenset({"chat"})
    preferred_model: str | None = None
    estimated_input_tokens: int = 1_000
    max_output_tokens: int = 1_000
    temperature: float = 0.2
    max_cost: float | None = None
    timeout_seconds: float = 30.0
    max_retries: int = 1
    route_strategy: str = "balanced"
    inputs: Mapping[str, object] = field(default_factory=dict)
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.prompt and not self.inputs:
            raise ValueError("request must include prompt text or structured inputs")
        if self.estimated_input_tokens < 0 or self.max_output_tokens < 1:
            raise ValueError("token estimates must be non-negative and output limit positive")
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("temperature must be between 0 and 2")
        if self.max_cost is not None and self.max_cost < 0:
            raise ValueError("max_cost cannot be negative")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.max_retries < 0 or self.max_retries > 5:
            raise ValueError("max_retries must be between 0 and 5")
        if self.route_strategy not in {"balanced", "lowest_cost", "lowest_latency"}:
            raise ValueError("route_strategy must be balanced, lowest_cost, or lowest_latency")


@dataclass(frozen=True, slots=True)
class InferenceResult:
    content: object
    model_id: str
    provider: str
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0
    finish_reason: str = "stop"
    estimated_cost: float = 0.0
    request_id: str | None = None


@dataclass(frozen=True, slots=True)
class TelemetryEvent:
    request_id: str
    model_id: str
    provider: str
    status: str
    latency_ms: int
    input_tokens: int
    output_tokens: int
    estimated_cost: float
    error_type: str | None = None


class ModelAdapter(Protocol):
    """Adapter boundary implemented by a local runtime or a remote provider."""

    def infer(self, model: ModelProfile, request: InferenceRequest) -> InferenceResult:
        """Run one inference and enforce request.timeout_seconds in its transport."""


class AikidoHub:
    """Model registry, capability router, retry/fallback coordinator and cost guard."""

    def __init__(self) -> None:
        self._models: dict[str, ModelProfile] = {}
        self._adapters: dict[str, ModelAdapter] = {}
        self._telemetry: list[TelemetryEvent] = []

    @property
    def models(self) -> Mapping[str, ModelProfile]:
        return dict(self._models)

    @property
    def telemetry(self) -> tuple[TelemetryEvent, ...]:
        return tuple(self._telemetry)

    def register_adapter(self, provider: str, adapter: ModelAdapter) -> "AikidoHub":
        if not provider.strip():
            raise ValueError("provider name cannot be empty")
        self._adapters[provider] = adapter
        return self

    def register_model(self, model: ModelProfile) -> "AikidoHub":
        if model.identifier in self._models:
            raise ValueError(f"model {model.identifier!r} is already registered")
        self._models[model.identifier] = model
        return self

    def replace_model(self, model: ModelProfile) -> "AikidoHub":
        if model.identifier not in self._models:
            raise KeyError(model.identifier)
        self._models[model.identifier] = model
        return self

    def _estimated_cost(self, model: ModelProfile, request: InferenceRequest) -> float:
        return (
            request.estimated_input_tokens * model.input_cost_per_1k
            + request.max_output_tokens * model.output_cost_per_1k
        ) / 1_000.0

    def _candidates(self, request: InferenceRequest) -> list[ModelProfile]:
        if request.preferred_model is not None:
            if request.preferred_model not in self._models:
                raise NoModelAvailable(f"preferred model {request.preferred_model!r} is not registered")
            primary = self._models[request.preferred_model]
            ordered_ids = [primary.identifier, *primary.fallback_models]
            ordered: list[ModelProfile] = []
            seen: set[str] = set()
            for identifier in ordered_ids:
                if identifier in seen:
                    continue
                seen.add(identifier)
                candidate = self._models.get(identifier)
                if candidate is not None:
                    ordered.append(candidate)
            candidates = ordered
        else:
            candidates = list(self._models.values())

        eligible = [
            model for model in candidates
            if model.enabled
            and request.required_capabilities.issubset(model.capabilities)
            and request.max_output_tokens <= model.max_output_tokens
            and request.estimated_input_tokens + request.max_output_tokens <= model.context_window
            and (
                request.max_cost is None
                or self._estimated_cost(model, request) <= request.max_cost
            )
        ]
        if request.route_strategy == "lowest_cost":
            eligible.sort(key=lambda item: (
                self._estimated_cost(item, request), -item.priority, item.latency_hint_ms,
            ))
        elif request.route_strategy == "lowest_latency":
            eligible.sort(key=lambda item: (
                item.latency_hint_ms, -item.priority, self._estimated_cost(item, request),
            ))
        elif request.preferred_model is None:
            eligible.sort(key=lambda item: (
                -item.priority, self._estimated_cost(item, request), item.latency_hint_ms,
            ))
        return eligible

    def complete(self, request: InferenceRequest) -> InferenceResult:
        request_id = uuid.uuid4().hex
        candidates = self._candidates(request)
        if not candidates:
            raise NoModelAvailable(
                "no enabled model satisfies capabilities, context size, output limit and preflight budget"
            )

        failures: list[str] = []
        for model in candidates:
            adapter = self._adapters.get(model.provider)
            if adapter is None:
                failures.append(f"{model.identifier}: no adapter registered for provider {model.provider}")
                self._telemetry.append(TelemetryEvent(
                    request_id, model.identifier, model.provider, "adapter_missing",
                    0, 0, 0, 0.0, "AdapterMissing",
                ))
                continue

            for attempt in range(request.max_retries + 1):
                started = time.monotonic()
                try:
                    result = adapter.infer(model, request)
                    latency = result.latency_ms or int((time.monotonic() - started) * 1_000)
                    if not isinstance(result, InferenceResult):
                        raise TypeError("adapter must return InferenceResult")
                    if result.input_tokens < 0 or result.output_tokens < 0:
                        raise ValueError("adapter returned negative token usage")
                    actual_cost = (
                        result.input_tokens * model.input_cost_per_1k
                        + result.output_tokens * model.output_cost_per_1k
                    ) / 1_000.0
                    if request.max_cost is not None and actual_cost > request.max_cost:
                        raise BudgetExceeded(
                            f"{model.identifier} estimated cost {actual_cost:.6g} exceeds "
                            f"request budget {request.max_cost:.6g}"
                        )
                    normalized = replace(
                        result,
                        model_id=model.identifier,
                        provider=model.provider,
                        latency_ms=latency,
                        estimated_cost=actual_cost,
                        request_id=request_id,
                    )
                    self._telemetry.append(TelemetryEvent(
                        request_id, model.identifier, model.provider, "success",
                        latency, result.input_tokens, result.output_tokens, actual_cost,
                    ))
                    return normalized
                except Exception as exc:
                    latency = int((time.monotonic() - started) * 1_000)
                    failures.append(
                        f"{model.identifier} attempt {attempt + 1}: {type(exc).__name__}: {exc}"
                    )
                    self._telemetry.append(TelemetryEvent(
                        request_id, model.identifier, model.provider, "failed",
                        latency, 0, 0, 0.0, type(exc).__name__,
                    ))
                    # Provider exceptions may opt out of retries with retryable=False.
                    if getattr(exc, "retryable", True) is False:
                        break

        raise InferenceExhausted(
            f"all {len(candidates)} candidate model(s) failed", tuple(failures)
        )


class Aikido:
    """Namespace-style factory for the neural orchestration hub."""

    @staticmethod
    def hub() -> AikidoHub:
        return AikidoHub()


__all__ = [
    "AikidoError", "NoModelAvailable", "InferenceExhausted", "BudgetExceeded",
    "ModelProfile", "InferenceRequest", "InferenceResult", "TelemetryEvent",
    "ModelAdapter", "AikidoHub", "Aikido",
]
