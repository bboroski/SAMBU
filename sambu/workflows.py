"""Deterministic workflow primitives for SAMBU.

These functions model transactions and processing plans. They do not send gifts,
publish reports, issue credentials, execute parallel jobs, or access networks.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date
from hashlib import sha256
import math
import re
from typing import Callable

from .lexer import SambuSyntaxError, tokenize
from .parser import parse_ast
from .textcraft import _words, _rhyme_key
from .values import Record, number_value


_MAX_ROWS = 100_000
_MAX_TEXT = 1_000_000
_WORD_PAIR_RE = re.compile(r"[^\W\d_]+(?:[’'\-][^\W\d_]+)*", re.UNICODE)


def _arity(args: list[object], allowed: set[int], signature: str) -> None:
    if len(args) not in allowed:
        expected = " or ".join(str(n) for n in sorted(allowed))
        raise TypeError(f"{signature} expects {expected} arguments")


def _string(value: object, what: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{what} must be a non-empty string")
    return value.strip()


def _finite(value: object, what: str) -> float:
    result = number_value(value, what)
    if not math.isfinite(result):
        raise ValueError(f"{what} must be finite")
    return result


def _fraction(value: object, what: str) -> float:
    result = _finite(value, what)
    if not 0.0 <= result <= 1.0:
        raise ValueError(f"{what} must be between 0 and 1")
    return result


def _date(value: object, what: str) -> date:
    raw = _string(value, what)
    try:
        parsed = date.fromisoformat(raw)
    except ValueError as exc:
        raise ValueError(f"{what} must use ISO format YYYY-MM-DD") from exc
    if parsed.isoformat() != raw:
        raise ValueError(f"{what} must use canonical ISO format YYYY-MM-DD")
    return parsed


def _balances(rows: object) -> dict[str, float]:
    if not isinstance(rows, list):
        raise TypeError("balances must be an array of [owner, amount] rows")
    if len(rows) > _MAX_ROWS:
        raise ValueError(f"balances may contain at most {_MAX_ROWS:,} rows")
    result: dict[str, float] = {}
    for row in rows:
        if not isinstance(row, list) or len(row) != 2:
            raise ValueError("each balance must be [owner, amount]")
        owner = _string(row[0], "balance owner")
        amount = _finite(row[1], "balance amount")
        if amount < 0:
            raise ValueError("balance amount cannot be negative")
        if owner in result:
            raise ValueError(f"duplicate balance owner {owner!r}")
        result[owner] = amount
    return result


def _gift_batch(transfers: object, balance_rows: object) -> Record:
    if not isinstance(transfers, list):
        raise TypeError("gift transfers must be an array")
    if not 1 <= len(transfers) <= _MAX_ROWS:
        raise ValueError(f"gift batch must contain 1 to {_MAX_ROWS:,} transfers")
    balances = _balances(balance_rows)
    seen_ids: set[str] = set()
    transaction_records: list[Record] = []
    staged = dict(balances)
    total = 0.0

    # Validate and stage every transfer first. Nothing is mutated on failure.
    for row in transfers:
        if not isinstance(row, list) or len(row) != 4:
            raise ValueError("each gift must be [gift_id, giver, recipient, amount]")
        gift_id = _string(row[0], "gift id")
        giver = _string(row[1], "gift giver")
        recipient = _string(row[2], "gift recipient")
        amount = _finite(row[3], "gift amount")
        if gift_id in seen_ids:
            raise ValueError(f"duplicate gift id {gift_id!r} within batch")
        seen_ids.add(gift_id)
        if giver == recipient:
            raise ValueError("gift giver and recipient must differ")
        if amount <= 0:
            raise ValueError("gift amount must be greater than zero")
        if giver not in staged:
            raise ValueError(f"missing balance for gift giver {giver!r}")
        if recipient not in staged:
            raise ValueError(f"missing balance for gift recipient {recipient!r}")
        if staged[giver] < amount:
            raise ValueError(f"insufficient balance for gift giver {giver!r}")
        staged[giver] -= amount
        staged[recipient] += amount
        total += amount
        transaction_records.append(Record({
            "gift_id": gift_id,
            "giver": giver,
            "recipient": recipient,
            "amount": amount,
            "status": "previewed",
            "idempotency_key": f"gift:{gift_id}",
        }))

    updated_balances = [
        Record({"owner": owner, "balance": amount})
        for owner, amount in sorted(staged.items())
    ]
    return Record({
        "valid": True,
        "execution": "preview_only",
        "atomic": True,
        "transaction_count": len(transaction_records),
        "total_gifted": total,
        "transactions": transaction_records,
        "balances": updated_balances,
    })


def gift_batch(args: list[object]) -> Record:
    """Validate an all-or-nothing gift batch and return a preview ledger."""
    _arity(args, {2}, "gift_batch(transfers, balances)")
    return _gift_batch(args[0], args[1])


def gift_transfer(args: list[object]) -> Record:
    """Preview one gift using the same validation and atomicity rules as gift_batch."""
    _arity(args, {5}, "gift_transfer(gift_id, giver, recipient, amount, balances)")
    gift = [args[0], args[1], args[2], args[3]]
    result = _gift_batch([gift], args[4])
    transaction = result.get("transactions")[0]
    return Record({
        "valid": result.get("valid"),
        "execution": result.get("execution"),
        "atomic": result.get("atomic"),
        "transaction": transaction,
        "balances": result.get("balances"),
    })


def accreditation_record(args: list[object]) -> Record:
    """Create a structured accreditation record; verification remains explicit."""
    _arity(args, {7}, "accreditation_record(subject, standard, issuer, issued_on, expires_on, evidence, verified)")
    subject = _string(args[0], "accredited subject")
    standard = _string(args[1], "accreditation standard")
    issuer = _string(args[2], "accreditation issuer")
    issued = _date(args[3], "issue date")
    expires = _date(args[4], "expiry date")
    if expires < issued:
        raise ValueError("accreditation expiry date cannot precede issue date")
    evidence = args[5]
    if not isinstance(evidence, list) or not evidence:
        raise ValueError("accreditation evidence must be a non-empty array")
    normalized_evidence = [_string(item, "evidence reference") for item in evidence]
    if not isinstance(args[6], bool):
        raise TypeError("verified must be true or false")
    return Record({
        "subject": subject,
        "standard": standard,
        "issuer": issuer,
        "issued_on": issued.isoformat(),
        "expires_on": expires.isoformat(),
        "evidence": normalized_evidence,
        "verified": args[6],
        "record_status": "verified_record" if args[6] else "pending_verification",
        "credential_claim": "recorded_not_independently_certified",
    })


def accreditation_status(args: list[object]) -> Record:
    """Evaluate a recorded accreditation on an explicitly supplied date."""
    _arity(args, {2}, "accreditation_status(record, as_of)")
    record, as_of = args
    if not isinstance(record, Record):
        raise TypeError("accreditation_status expects an accreditation record")
    required = ("issued_on", "expires_on", "verified", "evidence")
    if any(name not in record.fields for name in required):
        raise ValueError("record is missing accreditation fields")
    current = _date(as_of, "assessment date")
    issued = _date(record.get("issued_on"), "issue date")
    expires = _date(record.get("expires_on"), "expiry date")
    verified = record.get("verified")
    evidence = record.get("evidence")
    if not isinstance(verified, bool) or not isinstance(evidence, list):
        raise ValueError("record has invalid verification metadata")
    if current < issued:
        status = "not_yet_valid"
    elif current > expires:
        status = "expired"
    elif not verified or not evidence:
        status = "unverified"
    else:
        status = "active"
    return Record({
        "status": status,
        "active": status == "active",
        "as_of": current.isoformat(),
        "issuer": record.get("issuer"),
        "subject": record.get("subject"),
        "standard": record.get("standard"),
    })


def associate(args: list[object]) -> Record:
    """Record a documented relationship without asserting that it proves causation."""
    _arity(args, {5, 6}, "associate(source, target, relation, evidence, confidence, verified=false)")
    source = _string(args[0], "association source")
    target = _string(args[1], "association target")
    relation = _string(args[2], "association relation")
    evidence = _string(args[3], "association evidence")
    confidence = _fraction(args[4], "association confidence")
    verified = args[5] if len(args) == 6 else False
    if not isinstance(verified, bool):
        raise TypeError("verified must be true or false")
    if source == target:
        raise ValueError("association endpoints must differ")
    fingerprint = sha256(
        "\0".join((source, target, relation, evidence)).encode("utf-8")
    ).hexdigest()[:20]
    return Record({
        "association_id": fingerprint,
        "source": source,
        "target": target,
        "relation": relation,
        "evidence": evidence,
        "confidence": confidence,
        "verified": verified,
        "status": "verified" if verified else "unverified",
        "causation_claimed": False,
    })


def signal_report(args: list[object]) -> Record:
    """Create a non-accusatory, evidence-linked report for human review."""
    _arity(args, {6, 7}, "signal_report(reporter, subject, category, claim, evidence, severity, confidence=0.5)")
    reporter = _string(args[0], "reporter")
    subject = _string(args[1], "subject")
    category = _string(args[2], "report category")
    claim = _string(args[3], "reported claim")
    evidence = args[4]
    if not isinstance(evidence, list) or not evidence:
        raise ValueError("a signal report requires at least one evidence reference")
    evidence_refs = [_string(item, "evidence reference") for item in evidence]
    severity = _string(args[5], "severity").lower()
    if severity not in {"low", "medium", "high", "critical"}:
        raise ValueError("severity must be low, medium, high, or critical")
    confidence = _fraction(args[6], "confidence") if len(args) == 7 else 0.5
    report_id = sha256(
        "\0".join((reporter, subject, category, claim, *evidence_refs)).encode("utf-8")
    ).hexdigest()[:20]
    return Record({
        "report_id": report_id,
        "reporter": reporter,
        "subject": subject,
        "category": category,
        "claim": claim,
        "evidence": evidence_refs,
        "severity": severity,
        "confidence": confidence,
        "status": "unverified_requires_review",
        "finding": None,
        "automated_action": "none",
    })


def pitch_score(args: list[object]) -> Record:
    """Rank a proposal transparently from impact, confidence, effort and risk inputs."""
    _arity(args, {4}, "pitch_score(impact, confidence, effort, risk)")
    impact, confidence, effort, risk = (
        _fraction(value, name)
        for value, name in zip(args, ("impact", "confidence", "effort", "risk"))
    )
    score = impact * confidence * (1.0 - risk) / (1.0 + effort)
    return Record({
        "score": score,
        "impact": impact,
        "confidence": confidence,
        "effort": effort,
        "risk": risk,
        "formula": "impact * confidence * (1 - risk) / (1 + effort)",
        "decision": "human_review_required",
    })


def blast_plan(args: list[object]) -> Record:
    """Build a bounded chunk/concurrency/retry plan without executing work."""
    _arity(args, {3, 4}, "blast_plan(total_items, chunk_size, max_in_flight, max_attempts=1)")
    total = number_value(args[0], "total items")
    chunk_size = number_value(args[1], "chunk size")
    max_in_flight = number_value(args[2], "max in flight")
    max_attempts = number_value(args[3], "max attempts") if len(args) == 4 else 1
    for value, label, minimum, maximum in (
        (total, "total items", 0, 1_000_000),
        (chunk_size, "chunk size", 1, 10_000),
        (max_in_flight, "max in flight", 1, 1_000),
        (max_attempts, "max attempts", 1, 20),
    ):
        if not math.isfinite(value) or int(value) != value or not minimum <= value <= maximum:
            raise ValueError(f"{label} must be an integer from {minimum} to {maximum}")
    chunk_count = math.ceil(total / chunk_size) if total else 0
    return Record({
        "total_items": int(total),
        "chunk_size": int(chunk_size),
        "chunk_count": chunk_count,
        "max_in_flight": min(int(max_in_flight), chunk_count) if chunk_count else 0,
        "max_attempts": int(max_attempts),
        "requires_idempotency": True,
        "requires_dead_letter_policy": max_attempts > 1,
        "execution": "plan_only",
        "estimated_wave_count": math.ceil(chunk_count / max_in_flight) if chunk_count else 0,
    })


def parse_report(args: list[object]) -> Record:
    """Analyze syntax and AST size without executing the supplied SAMBU program."""
    _arity(args, {1}, "parse_report(source)")
    source = args[0]
    if not isinstance(source, str):
        raise TypeError("parse_report expects source text")
    if len(source) > _MAX_TEXT:
        raise ValueError(f"source may contain at most {_MAX_TEXT:,} characters")
    try:
        tokens = tokenize(source)
        program = parse_ast(source)
    except SambuSyntaxError as exc:
        return Record({
            "valid": False,
            "error_code": exc.code,
            "message": exc.message,
            "line": exc.line,
            "column": exc.column,
            "token_count": None,
            "statement_count": None,
            "execution": "not_run",
        })
    return Record({
        "valid": True,
        "error_code": None,
        "message": None,
        "line": None,
        "column": None,
        "token_count": max(0, len(tokens) - 1),
        "statement_count": len(program.statements),
        "execution": "not_run",
    })


def mine_patterns(args: list[object]) -> Record:
    """Mine repeated words, adjacent word pairs and approximate rhyme families."""
    _arity(args, {1, 2}, "mine_patterns(text, min_frequency=2)")
    source = args[0]
    if not isinstance(source, str):
        raise TypeError("mine_patterns expects text")
    if len(source) > _MAX_TEXT:
        raise ValueError(f"text may contain at most {_MAX_TEXT:,} characters")
    min_frequency = number_value(args[1], "minimum frequency") if len(args) == 2 else 2
    if not math.isfinite(min_frequency) or int(min_frequency) != min_frequency or not 1 <= min_frequency <= 1000:
        raise ValueError("minimum frequency must be an integer from 1 to 1000")
    words = _words(source)
    unigrams = Counter(words)
    bigrams = Counter(zip(words, words[1:]))
    rhymes: dict[str, Counter[str]] = {}
    for word in words:
        key = _rhyme_key(word)
        if key:
            rhymes.setdefault(key, Counter())[word] += 1
    repeated_words = [
        Record({"pattern": word, "frequency": count})
        for word, count in sorted(unigrams.items(), key=lambda item: (-item[1], item[0]))
        if count >= min_frequency
    ][:50]
    repeated_pairs = [
        Record({"pattern": f"{left} {right}", "frequency": count})
        for (left, right), count in sorted(bigrams.items(), key=lambda item: (-item[1], item[0]))
        if count >= min_frequency
    ][:50]
    rhyme_families = [
        Record({
            "key": key,
            "words": list(sorted(forms)),
            "token_count": sum(forms.values()),
        })
        for key, forms in sorted(rhymes.items())
        if len(forms) >= 2 and sum(forms.values()) >= min_frequency
    ][:50]
    return Record({
        "word_count": len(words),
        "repeated_words": repeated_words,
        "repeated_bigrams": repeated_pairs,
        "rhyme_families": rhyme_families,
        "method": "deterministic_surface_pattern_mining",
    })


def cluster_glue(args: list[object]) -> Record:
    """Merge items into connected clusters when their tag sets overlap."""
    _arity(args, {1}, "cluster_glue(items)")
    rows = args[0]
    if not isinstance(rows, list):
        raise TypeError("cluster_glue expects an array of [item, tags] rows")
    if len(rows) > _MAX_ROWS:
        raise ValueError(f"cluster_glue accepts at most {_MAX_ROWS:,} items")
    labels: list[str] = []
    tags_by_item: list[set[str]] = []
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, list) or len(row) != 2 or not isinstance(row[1], list):
            raise ValueError("each cluster item must be [item_name, tags_array]")
        label = _string(row[0], "cluster item")
        if label in seen:
            raise ValueError(f"duplicate cluster item {label!r}")
        seen.add(label)
        tags = {_string(tag, "cluster tag").casefold() for tag in row[1]}
        labels.append(label)
        tags_by_item.append(tags)
    parent = list(range(len(labels)))

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(left: int, right: int) -> None:
        a, b = find(left), find(right)
        if a != b:
            parent[max(a, b)] = min(a, b)

    tag_owner: dict[str, int] = {}
    for index, tags in enumerate(tags_by_item):
        for tag in tags:
            if tag in tag_owner:
                union(index, tag_owner[tag])
            else:
                tag_owner[tag] = index
    groups: dict[int, list[int]] = {}
    for index in range(len(labels)):
        groups.setdefault(find(index), []).append(index)
    clusters = []
    for members in sorted(groups.values(), key=lambda values: labels[values[0]].casefold()):
        shared_tags = set.intersection(*(tags_by_item[index] for index in members)) if len(members) > 1 else set()
        all_tags = set.union(*(tags_by_item[index] for index in members)) if members else set()
        clusters.append(Record({
            "items": [labels[index] for index in members],
            "shared_tags": sorted(shared_tags),
            "all_tags": sorted(all_tags),
            "size": len(members),
        }))
    return Record({
        "cluster_count": len(clusters),
        "item_count": len(labels),
        "clusters": clusters,
        "method": "connected_components_by_shared_tags",
    })


WORKFLOW_BUILTINS: dict[str, Callable[[list[object]], object]] = {
    "gift_transfer": gift_transfer,
    "gift_batch": gift_batch,
    "accreditation_record": accreditation_record,
    "accreditation_status": accreditation_status,
    "associate": associate,
    "signal_report": signal_report,
    "pitch_score": pitch_score,
    "blast_plan": blast_plan,
    "parse_report": parse_report,
    "mine_patterns": mine_patterns,
    "cluster_glue": cluster_glue,
}
