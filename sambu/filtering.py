"""04coq: declarative, bounded filtering for SAMBU.

Rules are data, never executable code. The engine reads only explicit record,
mapping, and sequence paths; it never evaluates source strings or invokes
arbitrary attributes.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import math
from numbers import Real
from typing import Callable

from .values import Quantity, Record, ZERO


_MAX_ITEMS = 100_000
_MAX_RULES = 256
_MAX_STAGES = 64
_MAX_PATH_LENGTH = 1_024
_MAX_PATH_DEPTH = 32
_MAX_MEMBERSHIP = 10_000

_UNARY_OPERATORS = {
    "exists", "missing", "is_null", "not_null", "truthy", "falsy",
}
_VALUE_OPERATORS = {
    "eq", "ne", "gt", "gte", "lt", "lte",
    "contains", "not_contains", "icontains",
    "in", "not_in",
    "starts_with", "ends_with", "istarts_with", "iends_with",
    "between",
    "length_eq", "length_gt", "length_gte", "length_lt", "length_lte",
}
_OPERATORS = _UNARY_OPERATORS | _VALUE_OPERATORS


class FilterConfigurationError(ValueError):
    """Raised when a filter policy is malformed or exceeds a safe limit."""


class _IncompatibleTypes(Exception):
    """Internal marker for values that cannot be compared by a safe operator."""


@dataclass(frozen=True)
class FilterRule:
    """One immutable field-path predicate.

    Set has_expected=False only for unary operators such as exists or truthy.
    """
    path: str
    operator: str
    expected: object = None
    has_expected: bool = True


@dataclass(frozen=True)
class RuleEvaluation:
    """Explainable result for one predicate."""
    index: int
    path: str
    operator: str
    actual: object
    expected: object
    exists: bool
    matched: bool
    reason: str


@dataclass(frozen=True)
class FilterEvaluation:
    """Explainable result for a complete all/any rule set."""
    matched: bool
    mode: str
    results: tuple[RuleEvaluation, ...]


def _mode(value: object) -> str:
    if not isinstance(value, str):
        raise TypeError("filter mode must be 'all' or 'any'")
    normalized = value.strip().lower()
    if normalized not in {"all", "any"}:
        raise FilterConfigurationError("filter mode must be 'all' or 'any'")
    return normalized


def _path(value: object) -> str:
    if not isinstance(value, str):
        raise TypeError("filter path must be a string")
    result = value.strip()
    if not result or len(result) > _MAX_PATH_LENGTH:
        raise FilterConfigurationError(
            f"filter path must contain 1 to {_MAX_PATH_LENGTH:,} characters"
        )
    if result != "$":
        parts = result.split(".")
        if len(parts) > _MAX_PATH_DEPTH or any(not part for part in parts):
            raise FilterConfigurationError(
                f"filter path must contain at most {_MAX_PATH_DEPTH} non-empty segments"
            )
        if any(part.startswith("__") or part.endswith("__") for part in parts):
            raise FilterConfigurationError("dunder path segments are not allowed")
    return result


def _operator(value: object) -> str:
    if not isinstance(value, str):
        raise TypeError("filter operator must be a string")
    result = value.strip().lower()
    if result not in _OPERATORS:
        allowed = ", ".join(sorted(_OPERATORS))
        raise FilterConfigurationError(f"unsupported filter operator {result!r}; use: {allowed}")
    return result


def _integer(value: object, what: str, *, minimum: int = 0, maximum: int = _MAX_MEMBERSHIP) -> int:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{what} must be an integer")
    number = float(value)
    if not math.isfinite(number) or int(number) != number or not minimum <= number <= maximum:
        raise FilterConfigurationError(f"{what} must be an integer from {minimum} to {maximum}")
    return int(number)


def _parse_rule(raw: object) -> FilterRule:
    if isinstance(raw, FilterRule):
        rule = raw
    elif isinstance(raw, Record):
        fields = raw.fields
        if "path" not in fields or "operator" not in fields:
            raise FilterConfigurationError("rule records require path and operator fields")
        has_expected = "expected" in fields
        rule = FilterRule(
            fields["path"], fields["operator"], fields.get("expected"), has_expected
        )
    elif isinstance(raw, (list, tuple)):
        if len(raw) not in {2, 3}:
            raise FilterConfigurationError("each rule must be [path, operator] or [path, operator, expected]")
        rule = FilterRule(
            raw[0], raw[1], raw[2] if len(raw) == 3 else None, len(raw) == 3
        )
    else:
        raise TypeError("each rule must be a two/three-item array, FilterRule, or rule record")

    path = _path(rule.path)
    operator = _operator(rule.operator)
    if operator in _UNARY_OPERATORS:
        if rule.has_expected:
            raise FilterConfigurationError(f"{operator} does not accept an expected value")
        expected = None
        has_expected = False
    else:
        if not rule.has_expected:
            raise FilterConfigurationError(f"{operator} requires an expected value")
        expected = rule.expected
        has_expected = True
        if operator in {"in", "not_in"}:
            if not isinstance(expected, list):
                raise TypeError(f"{operator} expects an array of candidate values")
            if len(expected) > _MAX_MEMBERSHIP:
                raise FilterConfigurationError(
                    f"membership lists may contain at most {_MAX_MEMBERSHIP:,} values"
                )
        elif operator == "between":
            if not isinstance(expected, list) or len(expected) != 2:
                raise TypeError("between expects [inclusive_minimum, inclusive_maximum]")
            try:
                if _ordered_compare(expected[0], expected[1]) > 0:
                    raise FilterConfigurationError("between minimum cannot exceed maximum")
            except _IncompatibleTypes as exc:
                raise FilterConfigurationError("between bounds must be comparable values") from exc
        elif operator in {
            "starts_with", "ends_with", "istarts_with", "iends_with", "icontains",
        }:
            if not isinstance(expected, str):
                raise TypeError(f"{operator} expects a string value")
        elif operator.startswith("length_"):
            _integer(expected, "length comparison value")

    return FilterRule(path, operator, expected, has_expected)


def _normalise_rules(raw_rules: object) -> tuple[FilterRule, ...]:
    if not isinstance(raw_rules, (list, tuple)):
        raise TypeError("filter rules must be an array")
    if not 1 <= len(raw_rules) <= _MAX_RULES:
        raise FilterConfigurationError(f"filter rules must contain 1 to {_MAX_RULES} entries")
    return tuple(_parse_rule(item) for item in raw_rules)


def _resolve_path(item: object, path: str) -> tuple[bool, object]:
    if path == "$":
        return True, item
    current = item
    for segment in path.split("."):
        if isinstance(current, Record):
            if segment not in current.fields:
                return False, None
            current = current.fields[segment]
        elif isinstance(current, Mapping) and type(current) is dict:
            if segment not in current:
                return False, None
            current = current[segment]
        elif isinstance(current, (list, tuple)):
            if not segment.isdecimal():
                return False, None
            index = int(segment)
            if index >= len(current):
                return False, None
            current = current[index]
        else:
            return False, None
    return True, current


def _safe_equal(left: object, right: object) -> bool:
    if isinstance(left, Quantity) or isinstance(right, Quantity):
        if isinstance(left, Quantity) and isinstance(right, Quantity):
            return left.dims == right.dims and left.value == right.value
        quantity = left if isinstance(left, Quantity) else right
        scalar = right if isinstance(left, Quantity) else left
        if quantity.dims != ZERO or isinstance(scalar, bool) or not isinstance(scalar, Real):
            return False
        if not math.isfinite(float(scalar)):
            return False
        return quantity.value == float(scalar)
    if isinstance(left, bool) or isinstance(right, bool):
        return isinstance(left, bool) and isinstance(right, bool) and left is right
    if isinstance(left, Real) or isinstance(right, Real):
        if not isinstance(left, Real) or not isinstance(right, Real):
            return False
        return math.isfinite(float(left)) and math.isfinite(float(right)) and float(left) == float(right)
    if left is None or right is None:
        return left is None and right is None
    if isinstance(left, str) or isinstance(right, str):
        return isinstance(left, str) and isinstance(right, str) and left == right
    return left is right


def _ordered_compare(left: object, right: object) -> int:
    if isinstance(left, Quantity) or isinstance(right, Quantity):
        if isinstance(left, Quantity) and isinstance(right, Quantity):
            if left.dims != right.dims:
                raise _IncompatibleTypes
            a, b = left.value, right.value
        else:
            quantity = left if isinstance(left, Quantity) else right
            scalar = right if isinstance(left, Quantity) else left
            if quantity.dims != ZERO or isinstance(scalar, bool) or not isinstance(scalar, Real):
                raise _IncompatibleTypes
            a, b = (quantity.value, float(scalar)) if isinstance(left, Quantity) else (float(scalar), quantity.value)
    elif (
        isinstance(left, Real) and not isinstance(left, bool)
        and isinstance(right, Real) and not isinstance(right, bool)
    ):
        a, b = float(left), float(right)
    elif isinstance(left, str) and isinstance(right, str):
        a, b = left, right
    else:
        raise _IncompatibleTypes
    if isinstance(a, float) and not math.isfinite(a):
        raise _IncompatibleTypes
    if isinstance(b, float) and not math.isfinite(b):
        raise _IncompatibleTypes
    return (a > b) - (a < b)


def _contains(container: object, expected: object) -> bool:
    if isinstance(container, str):
        if not isinstance(expected, str):
            raise _IncompatibleTypes
        return expected in container
    if isinstance(container, (list, tuple)):
        return any(_safe_equal(item, expected) for item in container)
    if isinstance(container, Record):
        return isinstance(expected, str) and expected in container.fields
    if type(container) is dict:
        try:
            return expected in container
        except TypeError as exc:
            raise _IncompatibleTypes from exc
    raise _IncompatibleTypes


def _evaluate_rule(item: object, rule: FilterRule, index: int) -> RuleEvaluation:
    exists, actual = _resolve_path(item, rule.path)
    operator = rule.operator
    expected = rule.expected
    if operator == "exists":
        matched, reason = exists, "matched" if exists else "path_missing"
    elif operator == "missing":
        matched, reason = not exists, "matched" if not exists else "path_present"
    elif not exists:
        matched, reason = False, "path_missing"
    elif operator == "is_null":
        matched, reason = actual is None, "matched" if actual is None else "not_null"
    elif operator == "not_null":
        matched, reason = actual is not None, "matched" if actual is not None else "is_null"
    elif operator == "truthy":
        matched, reason = bool(actual), "matched" if bool(actual) else "falsy"
    elif operator == "falsy":
        matched, reason = not bool(actual), "matched" if not bool(actual) else "truthy"
    else:
        try:
            if operator == "eq":
                matched = _safe_equal(actual, expected)
            elif operator == "ne":
                matched = not _safe_equal(actual, expected)
            elif operator in {"gt", "gte", "lt", "lte"}:
                comparison = _ordered_compare(actual, expected)
                matched = {
                    "gt": comparison > 0,
                    "gte": comparison >= 0,
                    "lt": comparison < 0,
                    "lte": comparison <= 0,
                }[operator]
            elif operator in {"contains", "not_contains"}:
                contains = _contains(actual, expected)
                matched = contains if operator == "contains" else not contains
            elif operator == "icontains":
                if not isinstance(actual, str):
                    raise _IncompatibleTypes
                matched = expected.casefold() in actual.casefold()
            elif operator in {"in", "not_in"}:
                contains = any(_safe_equal(actual, candidate) for candidate in expected)
                matched = contains if operator == "in" else not contains
            elif operator in {"starts_with", "ends_with", "istarts_with", "iends_with"}:
                if not isinstance(actual, str) or not isinstance(expected, str):
                    raise _IncompatibleTypes
                left = actual.casefold() if operator.startswith("i") else actual
                right = expected.casefold() if operator.startswith("i") else expected
                if operator.endswith("starts_with"):
                    matched = left.startswith(right)
                else:
                    matched = left.endswith(right)
            elif operator == "between":
                matched = (
                    _ordered_compare(actual, expected[0]) >= 0
                    and _ordered_compare(actual, expected[1]) <= 0
                )
            elif operator.startswith("length_"):
                if not isinstance(actual, (str, list, tuple, Mapping, Record)):
                    raise _IncompatibleTypes
                size = len(actual.fields) if isinstance(actual, Record) else len(actual)
                bound = int(expected)
                matched = {
                    "length_eq": size == bound,
                    "length_gt": size > bound,
                    "length_gte": size >= bound,
                    "length_lt": size < bound,
                    "length_lte": size <= bound,
                }[operator]
            else:
                raise FilterConfigurationError(f"unsupported filter operator {operator!r}")
            reason = "matched" if matched else "not_matched"
        except _IncompatibleTypes:
            matched, reason = False, "type_mismatch"

    return RuleEvaluation(
        index=index,
        path=rule.path,
        operator=operator,
        actual=actual if exists else None,
        expected=expected,
        exists=exists,
        matched=matched,
        reason=reason,
    )


class FilteringEngine:
    """Pure, deterministic 04coq engine for filtering in-memory SAMBU values."""

    def _evaluate_normalized(
        self, item: object, rules: tuple[FilterRule, ...], mode: str
    ) -> FilterEvaluation:
        results = tuple(
            _evaluate_rule(item, rule, index)
            for index, rule in enumerate(rules)
        )
        values = [result.matched for result in results]
        matched = all(values) if mode == "all" else any(values)
        return FilterEvaluation(matched, mode, results)

    def evaluate(
        self, item: object, rules: object, mode: str = "all"
    ) -> FilterEvaluation:
        normalized_mode = _mode(mode)
        normalized_rules = _normalise_rules(rules)
        return self._evaluate_normalized(item, normalized_rules, normalized_mode)

    def filter(
        self, items: object, rules: object, mode: str = "all"
    ) -> Record:
        if not isinstance(items, list):
            raise TypeError("coq_filter expects an array of items")
        if len(items) > _MAX_ITEMS:
            raise FilterConfigurationError(f"coq_filter accepts at most {_MAX_ITEMS:,} items")
        normalized_mode = _mode(mode)
        normalized_rules = _normalise_rules(rules)
        accepted: list[object] = []
        rejected: list[object] = []
        for item in items:
            evaluation = self._evaluate_normalized(item, normalized_rules, normalized_mode)
            (accepted if evaluation.matched else rejected).append(item)
        return Record({
            "items": accepted,
            "rejected": rejected,
            "input_count": len(items),
            "matched_count": len(accepted),
            "rejected_count": len(rejected),
            "mode": normalized_mode,
            "execution": "in_memory_pure_filter",
            "mutated_input": False,
        })

    def pipeline(self, items: object, stages: object) -> Record:
        if not isinstance(items, list):
            raise TypeError("coq_pipeline expects an array of items")
        if len(items) > _MAX_ITEMS:
            raise FilterConfigurationError(f"coq_pipeline accepts at most {_MAX_ITEMS:,} input items")
        if not isinstance(stages, list) or not 1 <= len(stages) <= _MAX_STAGES:
            raise FilterConfigurationError(
                f"coq_pipeline accepts 1 to {_MAX_STAGES} stages (at most {_MAX_STAGES})"
            )
        current = list(items)
        summaries: list[Record] = []
        for index, stage in enumerate(stages):
            if not isinstance(stage, (list, tuple)) or len(stage) != 2:
                raise FilterConfigurationError("each pipeline stage must be [mode, rules]")
            mode, rules = stage
            result = self.filter(current, rules, mode)
            next_items = result.get("items")
            summaries.append(Record({
                "stage": index + 1,
                "mode": result.get("mode"),
                "input_count": result.get("input_count"),
                "output_count": result.get("matched_count"),
                "dropped_count": result.get("rejected_count"),
            }))
            current = next_items
        return Record({
            "items": current,
            "input_count": len(items),
            "output_count": len(current),
            "stages": summaries,
            "execution": "in_memory_pure_pipeline",
            "mutated_input": False,
        })


_ENGINE = FilteringEngine()


def coq_rule(args: list[object]) -> Record:
    """Build a validated, reusable 04coq rule record."""
    if len(args) not in {2, 3}:
        raise TypeError("coq_rule(path, operator, expected?) expects 2 or 3 arguments")
    has_expected = len(args) == 3
    rule = _parse_rule(FilterRule(args[0], args[1], args[2] if has_expected else None, has_expected))
    fields: dict[str, object] = {"path": rule.path, "operator": rule.operator}
    if rule.has_expected:
        fields["expected"] = rule.expected
    return Record(fields)


def coq_match(args: list[object]) -> bool:
    """Return whether one item satisfies a declarative 04coq rule set."""
    if len(args) not in {2, 3}:
        raise TypeError("coq_match(item, rules, mode='all') expects 2 or 3 arguments")
    mode = args[2] if len(args) == 3 else "all"
    return _ENGINE.evaluate(args[0], args[1], mode).matched


def coq_explain(args: list[object]) -> Record:
    """Return a full per-rule trace for one item without changing it."""
    if len(args) not in {2, 3}:
        raise TypeError("coq_explain(item, rules, mode='all') expects 2 or 3 arguments")
    mode = args[2] if len(args) == 3 else "all"
    evaluation = _ENGINE.evaluate(args[0], args[1], mode)
    return Record({
        "matched": evaluation.matched,
        "mode": evaluation.mode,
        "rules_checked": len(evaluation.results),
        "results": [
            Record({
                "index": result.index,
                "path": result.path,
                "operator": result.operator,
                "actual": result.actual,
                "expected": result.expected,
                "exists": result.exists,
                "matched": result.matched,
                "reason": result.reason,
            })
            for result in evaluation.results
        ],
    })


def coq_filter(args: list[object]) -> Record:
    """Filter an array, preserving accepted and rejected items in their input order."""
    if len(args) not in {2, 3}:
        raise TypeError("coq_filter(items, rules, mode='all') expects 2 or 3 arguments")
    mode = args[2] if len(args) == 3 else "all"
    return _ENGINE.filter(args[0], args[1], mode)


def coq_pipeline(args: list[object]) -> Record:
    """Apply sequential filtering stages; each stage receives only prior survivors."""
    if len(args) != 2:
        raise TypeError("coq_pipeline(items, stages) expects 2 arguments")
    return _ENGINE.pipeline(args[0], args[1])


FILTERING_BUILTINS: dict[str, Callable[[list[object]], object]] = {
    "coq_rule": coq_rule,
    "coq_match": coq_match,
    "coq_explain": coq_explain,
    "coq_filter": coq_filter,
    "coq_pipeline": coq_pipeline,
}
