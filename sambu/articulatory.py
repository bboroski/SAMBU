"""SAMBU's 200-word articulatory lexicon and deterministic word morphology.

The orthography is generated from:
    semantic onset + articulation grade + grammatical coda

Ten onsets × five grades × four codas = exactly 200 distinct two-syllable
lexemes. A subset is wired to parser keywords and runtime built-ins; the rest
are reserved vocabulary with published meanings, not fake implementations.
"""
from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Iterable


@dataclass(frozen=True, slots=True)
class _Root:
    code: str
    name: str
    meaning: str


@dataclass(frozen=True, slots=True)
class _Grade:
    code: str
    name: str
    meaning: str


@dataclass(frozen=True, slots=True)
class _Coda:
    suffix: str
    name: str
    meaning: str


ROOTS = (
    _Root("k", "structure", "shape, declaration and architecture"),
    _Root("t", "flow", "sequence, branching and control"),
    _Root("r", "value", "payload, number and stored data"),
    _Root("m", "memory", "state, identity and continuity"),
    _Root("s", "safeguard", "logic, truth and constraint"),
    _Root("v", "measure", "quantity, physics and calculation"),
    _Root("d", "evidence", "diagnosis, signal and proof"),
    _Root("n", "coordination", "messages, concurrency and supervision"),
    _Root("p", "transform", "space, geometry and composition"),
    _Root("l", "language", "sound, symbol, text and expression"),
)

GRADES = (
    _Grade("a", "opening", "initiate, declare or create"),
    _Grade("e", "inspection", "observe, check or validate"),
    _Grade("i", "transformation", "calculate, convert or transform"),
    _Grade("o", "composition", "combine, group or contain"),
    _Grade("u", "completion", "finish, release or close"),
)

CODAS = (
    _Coda("va", "action", "an operation or directive"),
    _Coda("ven", "entity", "a named object, type or resource"),
    _Coda("vir", "relation", "a link, rule or connection"),
    _Coda("vum", "state", "a value, condition or result"),
)

# Every alias is a newly coined SAMBU word. The parser canonicalizes these
# spellings to existing grammar terminals while retaining the original lexeme
# and its source span on the token.
_KEYWORD_ALIASES = {
    # K: structure and declarations
    "kava": "let",
    "kaven": "class",
    "kavir": "extends",
    "kavum": "static",
    "keva": "interface",
    "keven": "trait",
    "kevir": "implements",
    "kevum": "abstract",
    "kiva": "final",
    "kiven": "public",
    "kivir": "private",
    "kivum": "protected",
    "kova": "uses",
    # T: flow and control
    "tava": "fn",
    "taven": "for",
    "tavir": "in",
    "tavum": "return",
    "teva": "if",
    "teven": "else",
    # R: values and logical articulation
    "rava": "and",
    "raven": "or",
    "ravir": "not",
    "ravum": "true",
    "reva": "false",
    "reven": "null",
}
KEYWORD_ALIASES = MappingProxyType(_KEYWORD_ALIASES)

# Targets are allocated within their matching sound families. A word's
# onset therefore remains a useful mnemonic for the operation it names.
_BUILTIN_TARGETS_BY_FAMILY = {
    # Scientific quantities and scalar computation.
    "v": (
        "maxwell", "boltzmann", "thermal_energy", "partition", "entropy",
        "sample_maxwell", "mean", "variance", "sqrt", "exp", "log", "abs",
        "count", "len", "range", "sum", "min", "max",
        "canonical_ensemble", "microcanonical_ensemble",
    ),
    # Actors, supervisors and typed channels.
    "n": (
        "actor", "actor_send", "actor_drain", "actor_state", "supervisor",
        "supervise", "supervisor_status", "channel", "channel_send",
        "channel_receive",
    ),
    # Sparse voxel and spatial operations.
    "p": (
        "voxel_grid", "voxel_set", "voxel_remove", "voxel_get", "voxel_count",
        "voxel_mesh", "voxel_chunks", "voxel_frame_plan", "voxel_raycast",
        "voxel_octree", "voxel_octree_get", "voxel_export",
        "voxel_spectral_profile", "voxel_solve_field", "voxel_sparsify", "craft_cut",
    ),
    # Rules, filters and evidence reports.
    "d": (
        "coq_rule", "coq_match", "coq_explain", "coq_filter", "coq_pipeline",
        "parse_report", "mine_patterns", "cluster_glue", "pitch_score", "craft_master",
    ),
    # Text, articulation and the wordbook itself.
    "l": (
        "print", "syllables", "rhyme_key", "text_profile", "prosody_profile",
        "word_info", "wordbook", "audio_profile", "studio_offer",
        "capture_node", "order_pipeline", "package_pricing", "unit_economics", "craft_source",
        "hook_profile",
    ),
    # Workflow memory and ecosystem models.
    "m": (
        "gift_transfer", "gift_batch", "accreditation_record",
        "accreditation_status", "associate", "signal_report", "blast_plan",
        "mimic_profile", "mimic_distance", "imprint_closure",
        "v_vector_stream", "countercurrent_sync", "biometric_taxonomy_sort",
        "wetland_ecosystem_loop", "markov_relaxation", "lindblad_dephase",
        "onsager_flux", "phonon_decay", "planck_time",
    ),
    # Domain systems and planning operations.
    "t": (
        "network", "network_metrics", "influence", "funnel", "ab_test",
        "weekly_schedule", "attendance", "capture_tower", "allocate",
        "negotiate", "channel_metrics", "queue_profile", "retry_schedule",
        "idempotency_key",
    ),
    # Deterministic game-state operations.
    "k": (
        "rps_round", "tic_tac_toe_state", "tic_tac_toe_move",
        "tic_tac_toe_best_move", "craft_token",
    ),
    # Percentage and ratio arithmetic.
    "r": (
        "percent_of", "apply_percent", "reduce_by_percent", "percentage",
        "percent_change", "percent_to_ratio", "ratio_to_percent",
        "percentage_points", "clamp_percent", "craft_assemble",
    ),
    # Comparative waterfowl physiology models.
    "s": (
        "countercurrent_exchange", "plumage_insulation",
        "feather_barrier_profile", "flight_energy_budget",
        "flight_muscle_profile", "migration_speed", "oxygen_pressure_ratio",
        "avian_gas_exchange", "avian_air_sac_cycle", "bill_lamella_filter",
        "salt_balance", "flock_flight_budget", "visual_system_profile",
        "imprinting_window", "hemispheric_sleep_budget", "magnetic_heading",
        "digestive_grinding", "craft_rule",
    ),
}


@dataclass(frozen=True, slots=True)
class ArticulatoryWord:
    word: str
    pronunciation: str
    family_code: str
    family: str
    grade_code: str
    grade: str
    coda: str
    grammatical_role: str
    meaning: str
    status: str
    target: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return {
            "word": self.word,
            "pronunciation": self.pronunciation,
            "family_code": self.family_code,
            "family": self.family,
            "grade_code": self.grade_code,
            "grade": self.grade,
            "coda": self.coda,
            "grammatical_role": self.grammatical_role,
            "meaning": self.meaning,
            "status": self.status,
            "target": self.target,
        }


def _build_wordbook() -> tuple[ArticulatoryWord, ...]:
    candidates: dict[str, list[str]] = {}
    for root in ROOTS:
        candidates[root.code] = [
            root.code + grade.code + coda.suffix
            for grade in GRADES
            for coda in CODAS
            if root.code + grade.code + coda.suffix not in KEYWORD_ALIASES
        ]

    builtin_aliases: dict[str, str] = {}
    for family, targets in _BUILTIN_TARGETS_BY_FAMILY.items():
        available = candidates[family]
        if len(targets) > len(available):
            raise RuntimeError(f"articulatory family {family!r} has insufficient word slots")
        for word, target in zip(available, targets):
            builtin_aliases[word] = target

    if len(set(builtin_aliases.values())) != len(builtin_aliases):
        raise RuntimeError("articulatory built-in aliases must have unique canonical targets")

    entries: list[ArticulatoryWord] = []
    for root in ROOTS:
        for grade in GRADES:
            for coda in CODAS:
                word = root.code + grade.code + coda.suffix
                target = KEYWORD_ALIASES.get(word) or builtin_aliases.get(word)
                status = (
                    "keyword" if word in KEYWORD_ALIASES
                    else "builtin" if word in builtin_aliases
                    else "reserved"
                )
                entries.append(ArticulatoryWord(
                    word=word,
                    pronunciation=word[:2] + "-" + word[2:],
                    family_code=root.code,
                    family=root.name,
                    grade_code=grade.code,
                    grade=grade.name,
                    coda=coda.name,
                    grammatical_role=coda.meaning,
                    meaning=f"{root.meaning}; {grade.meaning}; {coda.meaning}",
                    status=status,
                    target=target,
                ))

    if len(entries) != 200 or len({entry.word for entry in entries}) != 200:
        raise RuntimeError("SAMBU articulatory wordbook must contain exactly 200 unique words")
    return tuple(entries)


ARTICULATORY_WORDS = _build_wordbook()
_WORD_BY_NAME = MappingProxyType({entry.word: entry for entry in ARTICULATORY_WORDS})

_BUILTIN_ALIASES = {
    entry.word: entry.target
    for entry in ARTICULATORY_WORDS
    if entry.status == "builtin" and entry.target is not None
}
BUILTIN_ALIASES = MappingProxyType(_BUILTIN_ALIASES)

ACTIVE_WORDS = tuple(
    entry.word for entry in ARTICULATORY_WORDS
    if entry.status in {"keyword", "builtin"}
)
RESERVED_WORDS = tuple(
    entry.word for entry in ARTICULATORY_WORDS if entry.status == "reserved"
)


def lookup_articulatory_word(word: str) -> ArticulatoryWord | None:
    """Look up a lexeme by its lowercase SAMBU spelling."""
    if not isinstance(word, str):
        raise TypeError("articulatory word must be text")
    return _WORD_BY_NAME.get(word.casefold())


def filter_articulatory_words(
    *,
    family: str | None = None,
    status: str | None = None,
) -> tuple[ArticulatoryWord, ...]:
    """Filter the fixed 200-word lexicon by family code/name and maturity."""
    family_key = family.casefold() if family is not None else None
    status_key = status.casefold() if status is not None else None
    valid_statuses = {"active", "keyword", "builtin", "reserved"}
    if status_key is not None and status_key not in valid_statuses:
        raise ValueError("status must be active, keyword, builtin or reserved")
    root_names = {root.code: root.name for root in ROOTS}
    if family_key is not None:
        family_key = root_names.get(family_key, family_key)
        if family_key not in set(root_names.values()):
            raise ValueError("unknown articulatory family")
    selected = []
    for entry in ARTICULATORY_WORDS:
        if family_key is not None and entry.family != family_key:
            continue
        if status_key == "active" and entry.status == "reserved":
            continue
        if status_key in {"keyword", "builtin", "reserved"} and entry.status != status_key:
            continue
        selected.append(entry)
    return tuple(selected)


__all__ = [
    "ACTIVE_WORDS", "ARTICULATORY_WORDS", "BUILTIN_ALIASES",
    "KEYWORD_ALIASES", "RESERVED_WORDS", "ArticulatoryWord",
    "filter_articulatory_words", "lookup_articulatory_word",
]
