"""SAMBU Machine: layered architecture, quality sampling and failure memory.

This module provides deterministic project inspection and evidence records.
It does not execute arbitrary shell commands or claim static type analysis.
"""
from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, fields, is_dataclass
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Iterable, Mapping

from . import ast as language_ast
from .lexer import SambuSyntaxError
from .parser import parse_ast


MAX_GHOSTS = 10_000
MAX_SOURCE_BYTES = 2_000_000
MAX_TOTAL_SOURCE_BYTES = 32_000_000
MAX_SAMPLE_EXCERPT_BYTES = 8_192
MAX_WORKSPACE_FILES = 500
_EXCLUDED_DIRS = {".git", ".venv", "__pycache__", "node_modules", "build", "dist"}
_SECRET_PATTERNS = (
    re.compile(r"(?i)(password|passwd|token|secret|api[_-]?key|authorization)\s*[:=]\s*([^\s,;]+)"),
    re.compile(r"(https?://)[^/@\s:]+:[^/@\s]+@", re.IGNORECASE),
)
_STATEMENT_TYPES = (
    language_ast.LetStatement, language_ast.SetFieldStatement,
    language_ast.FunctionStatement, language_ast.ClassStatement,
    language_ast.InterfaceStatement, language_ast.TraitStatement,
    language_ast.ReturnStatement, language_ast.IfStatement,
    language_ast.ForStatement, language_ast.ExpressionStatement,
)


class MachineError(RuntimeError):
    """Base error for SAMBU Machine services."""


class CapabilityDeniedError(MachineError):
    """The selected Machine profile does not grant the requested capability."""


@dataclass(frozen=True, slots=True)
class MachineProfile:
    """A named, explicit capability ceiling for SAMBU Machine operations."""

    name: str
    level: int
    capabilities: frozenset[str]

    LEVELS = {
        "sealed": frozenset({"workspace.read", "source.sample", "architecture.inspect"}),
        "sandbox": frozenset({
            "workspace.read", "source.sample", "architecture.inspect", "source.execute",
        }),
        "host": frozenset({
            "workspace.read", "source.sample", "architecture.inspect", "source.execute",
            "host.adapter",
        }),
        "device": frozenset({
            "workspace.read", "source.sample", "architecture.inspect", "source.execute",
            "host.adapter", "device.adapter",
        }),
    }

    @classmethod
    def named(cls, name: str = "sandbox") -> "MachineProfile":
        levels = {"sealed": 0, "sandbox": 1, "host": 2, "device": 3}
        try:
            level = levels[name]
            capabilities = cls.LEVELS[name]
        except KeyError as exc:
            raise ValueError(
                "Machine profile must be sealed, sandbox, host, or device"
            ) from exc
        return cls(name, level, capabilities)

    def allows(self, capability: str) -> bool:
        return capability in self.capabilities

    def require(self, capability: str) -> None:
        if not self.allows(capability):
            raise CapabilityDeniedError(
                f"profile {self.name!r} (level {self.level}) does not grant {capability!r}"
            )


class PlywoodDesignError(MachineError):
    """A layered design violates its declared dependencies or contracts."""


class CodeSamplingError(MachineError):
    """A code sample could not be produced safely."""


@dataclass(frozen=True, slots=True)
class PlywoodLayer:
    """One replaceable board in a layered software design."""

    name: str
    role: str
    depends_on: tuple[str, ...] = ()
    provides: tuple[str, ...] = ()
    requires: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class PlywoodValidation:
    valid: bool
    order: tuple[str, ...]
    issues: tuple[str, ...]


class PlywoodDesign:
    """A dependency-checked laminate of replaceable software layers.

    The metaphor is a layered board: each layer has a declared role, provides
    named capabilities and depends only on explicit lower-level layers.
    """

    ROLES = {
        "foundation", "core", "domain", "service", "adapter",
        "interface", "tooling", "verification",
    }

    def __init__(self, layers: Iterable[PlywoodLayer], *, max_layers: int = 64):
        if isinstance(max_layers, bool) or not isinstance(max_layers, int) or not 1 <= max_layers <= 256:
            raise ValueError("max_layers must be an integer from 1 to 256")
        self.layers = tuple(layers)
        self.max_layers = max_layers

    def _order(self) -> tuple[tuple[str, ...], list[str]]:
        issues: list[str] = []
        names: dict[str, PlywoodLayer] = {}
        for layer in self.layers:
            if not isinstance(layer, PlywoodLayer):
                issues.append(f"unexpected layer object: {type(layer).__name__}")
                continue
            if not layer.name or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.-]{0,63}", layer.name):
                issues.append(f"invalid layer name: {layer.name!r}")
            if layer.name in names:
                issues.append(f"duplicate layer name: {layer.name}")
            names[layer.name] = layer
            if layer.role not in self.ROLES:
                issues.append(f"{layer.name}: unsupported role {layer.role!r}")
            for label, values in (
                ("depends_on", layer.depends_on),
                ("provides", layer.provides),
                ("requires", layer.requires),
            ):
                if len(values) != len(set(values)):
                    issues.append(f"{layer.name}: duplicate {label} entries")
                if any(not isinstance(v, str) or not v.strip() for v in values):
                    issues.append(f"{layer.name}: {label} entries must be non-empty strings")
        if len(self.layers) > self.max_layers:
            issues.append(f"layer count {len(self.layers)} exceeds limit {self.max_layers}")

        indegree = {name: 0 for name in names}
        followers = {name: [] for name in names}
        for name, layer in names.items():
            for dependency in layer.depends_on:
                if dependency not in names:
                    issues.append(f"{name}: unknown dependency {dependency!r}")
                    continue
                if dependency == name:
                    issues.append(f"{name}: cannot depend on itself")
                    continue
                indegree[name] += 1
                followers[dependency].append(name)

        ready = [name for name in names if indegree[name] == 0]
        order: list[str] = []
        while ready:
            current = ready.pop(0)
            order.append(current)
            for follower in followers[current]:
                indegree[follower] -= 1
                if indegree[follower] == 0:
                    ready.append(follower)
        if len(order) != len(names):
            cyclic = sorted(name for name, degree in indegree.items() if degree > 0)
            issues.append("dependency cycle detected: " + ", ".join(cyclic))
            return tuple(order), issues
        return tuple(order), issues

    def validate(self) -> PlywoodValidation:
        order, issues = self._order()
        by_name = {layer.name: layer for layer in self.layers if isinstance(layer, PlywoodLayer)}
        providers: dict[str, list[str]] = {}
        for layer in by_name.values():
            for capability in layer.provides:
                providers.setdefault(capability, []).append(layer.name)
        for capability, owners in providers.items():
            if len(owners) > 1:
                issues.append(
                    f"capability {capability!r} has ambiguous providers: {', '.join(owners)}"
                )

        ancestors: dict[str, set[str]] = {}
        for name in order:
            inherited: set[str] = set()
            for dependency in by_name[name].depends_on:
                if dependency not in by_name:
                    continue
                inherited.add(dependency)
                inherited.update(ancestors.get(dependency, set()))
            ancestors[name] = inherited
            available = {
                capability
                for ancestor in inherited
                for capability in by_name[ancestor].provides
            }
            missing = sorted(set(by_name[name].requires) - available)
            if missing:
                issues.append(
                    f"{name}: required capabilities are not supplied by dependencies: "
                    + ", ".join(missing)
                )
        return PlywoodValidation(not issues, order, tuple(issues))

    def topological_order(self) -> tuple[str, ...]:
        result = self.validate()
        if not result.valid:
            raise PlywoodDesignError("; ".join(result.issues))
        return result.order

    def to_dict(self) -> dict[str, object]:
        validation = self.validate()
        return {
            "valid": validation.valid,
            "order": list(validation.order),
            "issues": list(validation.issues),
            "layers": [
                {
                    "name": layer.name,
                    "role": layer.role,
                    "depends_on": list(layer.depends_on),
                    "provides": list(layer.provides),
                    "requires": list(layer.requires),
                }
                for layer in self.layers if isinstance(layer, PlywoodLayer)
            ],
        }


def default_plywood_design() -> PlywoodDesign:
    """Return the reference layered architecture used by SAMBU Machine."""
    return PlywoodDesign((
        PlywoodLayer("source_surface", "interface", provides=("source-text",)),
        PlywoodLayer(
            "syntax_foundation", "foundation",
            depends_on=("source_surface",), requires=("source-text",),
            provides=("typed-ast", "source-spans"),
        ),
        PlywoodLayer(
            "runtime_core", "core",
            depends_on=("syntax_foundation",), requires=("typed-ast",),
            provides=("runtime-values", "execution"),
        ),
        PlywoodLayer(
            "domain_services", "domain",
            depends_on=("runtime_core",), requires=("runtime-values",),
            provides=("domain-operations",),
        ),
        PlywoodLayer(
            "machine_control", "service",
            depends_on=("syntax_foundation", "runtime_core"),
            requires=("typed-ast", "execution"),
            provides=("workspace-checks", "failure-ledger"),
        ),
        PlywoodLayer(
            "ide_services", "tooling",
            depends_on=("syntax_foundation", "machine_control"),
            requires=("typed-ast", "source-spans", "workspace-checks"),
            provides=("diagnostics", "outline", "completion"),
        ),
        PlywoodLayer(
            "verification", "verification",
            depends_on=("runtime_core", "domain_services", "machine_control"),
            requires=("execution", "domain-operations", "failure-ledger"),
            provides=("quality-evidence",),
        ),
    ))


def _statement_nodes(value: object) -> Iterable[object]:
    """Walk typed AST dataclasses and yield each statement exactly once."""
    seen: set[int] = set()

    def visit(item: object):
        identity = id(item)
        if identity in seen:
            return
        if isinstance(item, _STATEMENT_TYPES):
            seen.add(identity)
            yield item
        if isinstance(item, (tuple, list)):
            for child in item:
                yield from visit(child)
        elif is_dataclass(item) and not isinstance(item, type):
            seen.add(identity)
            for field in fields(item):
                if field.name != "span":
                    yield from visit(getattr(item, field.name))

    yield from visit(value)


@dataclass(frozen=True, slots=True)
class CodeSample:
    path: str
    statement_type: str
    start_line: int
    end_line: int
    fingerprint: str
    excerpt: str


@dataclass(frozen=True, slots=True)
class CodeSamplingReport:
    files_scanned: int
    statements_found: int
    statements_sampled: int
    denominator: int
    seed: int
    samples: tuple[CodeSample, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "files_scanned": self.files_scanned,
            "statements_found": self.statements_found,
            "statements_sampled": self.statements_sampled,
            "ratio": f"1:{self.denominator}",
            "seed": self.seed,
            "samples": [
                {
                    "path": sample.path,
                    "statement_type": sample.statement_type,
                    "start_line": sample.start_line,
                    "end_line": sample.end_line,
                    "fingerprint": sample.fingerprint,
                    "excerpt": sample.excerpt,
                }
                for sample in self.samples
            ],
        }


class CodeSampler:
    """Deterministically sample typed AST statements, never arbitrary raw bytes.

    The 1-in-N rule is applied independently per file. Every non-empty source
    file contributes at least one sample; selection is stable across runs.
    """

    def __init__(
        self,
        *,
        max_files: int = MAX_WORKSPACE_FILES,
        max_source_bytes: int = MAX_SOURCE_BYTES,
        max_total_source_bytes: int = MAX_TOTAL_SOURCE_BYTES,
    ):
        self.max_files = _bounded_int(max_files, "max_files", 1, 10_000)
        self.max_source_bytes = _bounded_int(max_source_bytes, "max_source_bytes", 1, 16_000_000)
        self.max_total_source_bytes = _bounded_int(
            max_total_source_bytes, "max_total_source_bytes", 1, 256_000_000
        )

    def _source_files(self, path: str | Path) -> tuple[Path, ...]:
        target = Path(path).expanduser()
        if target.is_symlink():
            raise CodeSamplingError(f"refusing to sample symlink: {target}")
        if not target.exists():
            raise CodeSamplingError(f"path does not exist: {target}")
        if target.is_file():
            if target.suffix != ".sambu":
                raise CodeSamplingError("source file must have the .sambu extension")
            return (target,)
        if not target.is_dir():
            raise CodeSamplingError("sampling target must be a .sambu file or directory")
        found: list[Path] = []
        for candidate in sorted(target.rglob("*.sambu")):
            try:
                relative = candidate.relative_to(target)
            except ValueError:
                continue
            if candidate.is_symlink() or any(part in _EXCLUDED_DIRS or part.startswith(".") for part in relative.parts[:-1]):
                continue
            found.append(candidate)
            if len(found) > self.max_files:
                raise CodeSamplingError(f"workspace exceeds the {self.max_files}-file limit")
        return tuple(found)

    def sample(
        self,
        path: str | Path,
        *,
        denominator: int = 100,
        seed: int = 0,
        max_samples: int = 2_000,
    ) -> CodeSamplingReport:
        ratio = _bounded_int(denominator, "denominator", 1, 100_000)
        if isinstance(seed, bool) or not isinstance(seed, int) or not -(2**63) <= seed < 2**63:
            raise ValueError("seed must be a signed 64-bit integer")
        sample_limit = _bounded_int(max_samples, "max_samples", 1, 20_000)
        files = self._source_files(path)
        all_samples: list[CodeSample] = []
        statement_total = 0
        total_source_bytes = 0
        base = Path(path).expanduser()
        base = base if base.is_dir() else base.parent
        for file_path in files:
            try:
                file_size = file_path.stat().st_size
                if file_size > self.max_source_bytes:
                    raise CodeSamplingError(
                        f"{file_path}: source exceeds {self.max_source_bytes} bytes"
                    )
                total_source_bytes += file_size
                if total_source_bytes > self.max_total_source_bytes:
                    raise CodeSamplingError(
                        f"workspace source exceeds {self.max_total_source_bytes} total bytes"
                    )
                source = file_path.read_text(encoding="utf-8")
                program = parse_ast(source)
            except (OSError, UnicodeError, ValueError, TypeError, SambuSyntaxError, RecursionError) as exc:
                raise CodeSamplingError(f"{file_path}: {exc}") from exc
            nodes = list(_statement_nodes(program))
            statement_total += len(nodes)
            if not nodes:
                continue
            count = max(1, math.ceil(len(nodes) / ratio))
            ranked: list[tuple[str, object]] = []
            relative = file_path.relative_to(base).as_posix()
            for node in nodes:
                span = node.span
                key = f"{seed}|{relative}|{span.start.offset}|{type(node).__name__}"
                digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
                ranked.append((digest, node))
            chosen = sorted(ranked, key=lambda pair: pair[0])[:count]
            source_hash = hashlib.sha256(source.encode("utf-8")).hexdigest()
            for digest, node in sorted(chosen, key=lambda pair: pair[1].span.start.offset):
                span = node.span
                start = span.start.line
                end = span.end.line
                excerpt = source[span.start.offset:span.end.offset]
                encoded_excerpt = excerpt.encode("utf-8")
                if len(encoded_excerpt) > MAX_SAMPLE_EXCERPT_BYTES:
                    excerpt = (
                        encoded_excerpt[:MAX_SAMPLE_EXCERPT_BYTES]
                        .decode("utf-8", errors="ignore")
                        + "\\n… <sample truncated>"
                    )
                all_samples.append(CodeSample(
                    relative,
                    type(node).__name__,
                    start,
                    end,
                    hashlib.sha256(f"{source_hash}:{digest}".encode("ascii")).hexdigest(),
                    excerpt,
                ))
                if len(all_samples) > sample_limit:
                    raise CodeSamplingError(f"sample exceeds max_samples={sample_limit}")
        return CodeSamplingReport(
            len(files), statement_total, len(all_samples), ratio, seed, tuple(all_samples)
        )


@dataclass(frozen=True, slots=True)
class GhostRecord:
    fingerprint: str
    error_type: str
    category: str
    message: str
    source_hash: str
    context: str
    occurrences: int = 1


def _redact(text: str) -> str:
    value = str(text)
    for pattern in _SECRET_PATTERNS:
        if pattern.pattern.startswith("(https"):
            value = pattern.sub(r"\1<redacted>@", value)
        else:
            value = pattern.sub(r"\1=<redacted>", value)
    value = re.sub(r"(?i)bearer\s+[A-Za-z0-9._~+/-]+=*", "Bearer <redacted>", value)
    return value[:512]


class GhostLedger:
    """A bounded, deduplicating ledger of up to ten thousand failure signatures.

    It stores redacted messages and source hashes, not source files or local
    variables. It stays in memory unless the caller explicitly exports JSON.
    """

    def __init__(self, *, capacity: int = MAX_GHOSTS):
        self.capacity = _bounded_int(capacity, "capacity", 1, MAX_GHOSTS)
        self._records: OrderedDict[str, GhostRecord] = OrderedDict()

    def record(
        self,
        error: BaseException | str,
        *,
        source: str = "",
        category: str = "runtime",
        context: str = "",
    ) -> GhostRecord:
        error_type = type(error).__name__ if isinstance(error, BaseException) else "Failure"
        message = _redact(str(error))
        safe_category = _redact(category)[:64]
        safe_context = _redact(context)[:128]
        source_hash = hashlib.sha256(source.encode("utf-8")).hexdigest()
        fingerprint = hashlib.sha256(
            f"{error_type}\0{safe_category}\0{message}\0{source_hash}\0{safe_context}".encode("utf-8")
        ).hexdigest()
        previous = self._records.get(fingerprint)
        if previous is not None:
            updated = GhostRecord(
                previous.fingerprint, previous.error_type, previous.category,
                previous.message, previous.source_hash, previous.context,
                previous.occurrences + 1,
            )
            self._records[fingerprint] = updated
            self._records.move_to_end(fingerprint)
            return updated
        item = GhostRecord(
            fingerprint, error_type, safe_category, message,
            source_hash, safe_context, 1,
        )
        self._records[fingerprint] = item
        if len(self._records) > self.capacity:
            self._records.popitem(last=False)
        return item

    def snapshot(self) -> tuple[GhostRecord, ...]:
        return tuple(self._records.values())

    @property
    def count(self) -> int:
        return len(self._records)

    def to_json(self) -> str:
        return json.dumps(
            {
                "schema_version": 1,
                "capacity": self.capacity,
                "records": [
                    {
                        "fingerprint": item.fingerprint,
                        "error_type": item.error_type,
                        "category": item.category,
                        "message": item.message,
                        "source_hash": item.source_hash,
                        "context": item.context,
                        "occurrences": item.occurrences,
                    }
                    for item in self._records.values()
                ],
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )

    @classmethod
    def from_json(cls, raw: str) -> "GhostLedger":
        if not isinstance(raw, str) or len(raw.encode("utf-8")) > 32_000_000:
            raise ValueError("ghost ledger JSON must be text no larger than 32 MB")
        payload = json.loads(raw)
        if (
            not isinstance(payload, dict)
            or type(payload.get("schema_version")) is not int
            or payload.get("schema_version") != 1
        ):
            raise ValueError("unsupported ghost ledger schema")
        capacity = _bounded_int(payload.get("capacity"), "capacity", 1, MAX_GHOSTS)
        records = payload.get("records")
        if not isinstance(records, list) or len(records) > capacity:
            raise ValueError("invalid or oversized ghost record list")
        ledger = cls(capacity=capacity)
        for entry in records:
            if not isinstance(entry, dict):
                raise ValueError("ghost entry must be an object")
            fields_required = ("fingerprint", "error_type", "category", "message", "source_hash", "context")
            if any(not isinstance(entry.get(key), str) for key in fields_required):
                raise ValueError("ghost record text fields are malformed")
            fingerprint = entry["fingerprint"]
            source_hash = entry["source_hash"]
            if not re.fullmatch(r"[0-9a-f]{64}", fingerprint):
                raise ValueError("ghost fingerprint is malformed")
            if not re.fullmatch(r"[0-9a-f]{64}", source_hash):
                raise ValueError("ghost source hash is malformed")
            error_type = _redact(entry["error_type"])[:128]
            category = _redact(entry["category"])[:64]
            message = _redact(entry["message"])
            context = _redact(entry["context"])[:128]
            expected = hashlib.sha256(
                f"{error_type}\0{category}\0{message}\0{source_hash}\0{context}".encode("utf-8")
            ).hexdigest()
            if expected != fingerprint:
                raise ValueError("ghost fingerprint does not match its redacted record")
            occurrences = _bounded_int(entry.get("occurrences"), "occurrences", 1, 2**31 - 1)
            ledger._records[fingerprint] = GhostRecord(
                fingerprint, error_type, category, message, source_hash,
                context, occurrences,
            )
        return ledger


@dataclass(frozen=True, slots=True)
class MetricGain:
    name: str
    baseline: float
    candidate: float
    improvement_percent: float


@dataclass(frozen=True, slots=True)
class AmplificationReport:
    accepted: bool
    mean_improvement_percent: float
    effort_hours: float
    amplification_index: float
    regressions: tuple[str, ...]
    tests_passed: int
    tests_total: int
    metrics: tuple[MetricGain, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "accepted": self.accepted,
            "mean_improvement_percent": self.mean_improvement_percent,
            "effort_hours": self.effort_hours,
            "amplification_index_percent_per_hour": self.amplification_index,
            "regressions": list(self.regressions),
            "tests_passed": self.tests_passed,
            "tests_total": self.tests_total,
            "metrics": [
                {
                    "name": metric.name,
                    "baseline": metric.baseline,
                    "candidate": metric.candidate,
                    "improvement_percent": metric.improvement_percent,
                }
                for metric in self.metrics
            ],
        }


class EffortAmplification:
    """Evaluate whether extra engineering effort produced verified leverage."""

    @staticmethod
    def evaluate(
        baseline: Mapping[str, float],
        candidate: Mapping[str, float],
        *,
        effort_hours: float,
        lower_is_better: Iterable[str] = (),
        tests_passed: int,
        tests_total: int,
    ) -> AmplificationReport:
        if not baseline or set(baseline) != set(candidate):
            raise ValueError("baseline and candidate must contain the same non-empty metric names")
        if any(not isinstance(name, str) or not name.strip() for name in baseline):
            raise ValueError("metric names must be non-empty strings")
        if isinstance(lower_is_better, str):
            lower = {lower_is_better}
        else:
            try:
                lower = set(lower_is_better)
            except TypeError as exc:
                raise ValueError("lower_is_better must be an iterable of metric names") from exc
        if any(not isinstance(name, str) for name in lower):
            raise ValueError("lower_is_better entries must be metric names")
        unknown_directions = lower - set(baseline)
        if unknown_directions:
            raise ValueError(
                "lower_is_better contains unknown metrics: "
                + ", ".join(sorted(unknown_directions))
            )
        if not isinstance(effort_hours, (int, float)) or isinstance(effort_hours, bool) or not math.isfinite(effort_hours) or effort_hours <= 0:
            raise ValueError("effort_hours must be finite and positive")
        if isinstance(tests_passed, bool) or not isinstance(tests_passed, int):
            raise ValueError("tests_passed must be an integer")
        if isinstance(tests_total, bool) or not isinstance(tests_total, int) or tests_total < 1:
            raise ValueError("tests_total must be a positive integer")
        if not 0 <= tests_passed <= tests_total:
            raise ValueError("tests_passed must be between zero and tests_total")
        metrics: list[MetricGain] = []
        regressions: list[str] = []
        for name in sorted(baseline):
            before, after = baseline[name], candidate[name]
            if any(
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or not math.isfinite(value)
                or value <= 0
                for value in (before, after)
            ):
                raise ValueError(f"metric {name!r} values must be finite and positive")
            change = (before - after) / before * 100.0 if name in lower else (after - before) / before * 100.0
            metrics.append(MetricGain(name, float(before), float(after), change))
            if change < 0:
                regressions.append(name)
        mean_gain = sum(item.improvement_percent for item in metrics) / len(metrics)
        index = mean_gain / float(effort_hours)
        accepted = tests_passed == tests_total and not regressions and mean_gain > 0
        return AmplificationReport(
            accepted, mean_gain, float(effort_hours), index,
            tuple(regressions), tests_passed, tests_total, tuple(metrics),
        )


@dataclass(frozen=True, slots=True)
class WorkspaceIssue:
    path: str
    code: str
    message: str
    line: int
    column: int


@dataclass(frozen=True, slots=True)
class WorkspaceCheckReport:
    root: str
    files_checked: int
    valid_files: int
    issues: tuple[WorkspaceIssue, ...]
    architecture: PlywoodValidation

    @property
    def valid(self) -> bool:
        return not self.issues and self.architecture.valid

    def to_dict(self) -> dict[str, object]:
        return {
            "root": self.root,
            "files_checked": self.files_checked,
            "valid_files": self.valid_files,
            "valid": self.valid,
            "issues": [
                {
                    "path": issue.path,
                    "code": issue.code,
                    "message": issue.message,
                    "line": issue.line,
                    "column": issue.column,
                }
                for issue in self.issues
            ],
            "architecture": {
                "valid": self.architecture.valid,
                "order": list(self.architecture.order),
                "issues": list(self.architecture.issues),
            },
        }


def _bounded_int(value: object, name: str, minimum: int, maximum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise ValueError(f"{name} must be an integer from {minimum} to {maximum}")
    return value


class SambuMachine:
    """Headless project control plane for sampling, checks and failure evidence."""

    def __init__(
        self, *, ghost_capacity: int = MAX_GHOSTS, profile: str = "sandbox"
    ):
        self.ghosts = GhostLedger(capacity=ghost_capacity)
        self.sampler = CodeSampler()
        self.design = default_plywood_design()
        self.profile = MachineProfile.named(profile)

    def sample_code(
        self, path: str | Path, *, denominator: int = 100, seed: int = 0
    ) -> CodeSamplingReport:
        self.profile.require("source.sample")
        return self.sampler.sample(path, denominator=denominator, seed=seed)

    def check_workspace(self, path: str | Path) -> WorkspaceCheckReport:
        self.profile.require("workspace.read")
        root = Path(path).expanduser()
        if root.is_symlink() or not root.is_dir():
            raise MachineError("workspace must be an existing directory, not a symlink")
        candidates = []
        for item in sorted(root.rglob("*.sambu")):
            relative = item.relative_to(root)
            if item.is_symlink() or any(
                part in _EXCLUDED_DIRS or part.startswith(".")
                for part in relative.parts[:-1]
            ):
                continue
            candidates.append(item)
            if len(candidates) > MAX_WORKSPACE_FILES:
                raise MachineError(f"workspace exceeds {MAX_WORKSPACE_FILES} source files")
        issues: list[WorkspaceIssue] = []
        valid_files = 0
        total_source_bytes = 0
        for item in candidates:
            relative = item.relative_to(root).as_posix()
            try:
                file_size = item.stat().st_size
                if file_size > MAX_SOURCE_BYTES:
                    raise ValueError(f"source exceeds {MAX_SOURCE_BYTES} bytes")
                total_source_bytes += file_size
                if total_source_bytes > MAX_TOTAL_SOURCE_BYTES:
                    raise MachineError(
                        f"workspace source exceeds {MAX_TOTAL_SOURCE_BYTES} total bytes"
                    )
                source = item.read_text(encoding="utf-8")
                parse_ast(source)
            except Exception as exc:
                code = getattr(exc, "code", "SAMBU-M001")
                line = getattr(exc, "line", 1)
                column = getattr(exc, "column", 1)
                issues.append(WorkspaceIssue(relative, str(code), str(exc)[:512], int(line), int(column)))
                self.ghosts.record(exc, source="", category="syntax", context=relative)
            else:
                valid_files += 1
        return WorkspaceCheckReport(
            str(root.resolve()), len(candidates), valid_files,
            tuple(issues), self.design.validate(),
        )

    def run_source(self, source: str, *, context: str = "<memory>", output=print) -> object:
        self.profile.require("source.execute")
        from .interpreter import execute
        try:
            return execute(source, output=output)
        except Exception as exc:
            self.ghosts.record(exc, source=source, category="execution", context=context)
            raise
