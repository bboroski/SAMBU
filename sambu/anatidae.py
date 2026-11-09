"""Parameterized Anatidae models for comparative avian physiology.

This module deliberately requires explicit, caller-supplied measurements and
assumptions. It does not turn species-specific or disputed claims into universal
constants for all ducks and geese.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math
from typing import Callable

from .values import (
    ENERGY, PRESSURE, SPEED, TEMP, TIME, Quantity, Record,
    number_value, require_quantity,
)

POWER = (1, 2, -3, 0, 0)
DISTANCE = (0, 1, 0, 0, 0)


def _number(value: object, name: str, *, minimum: float | None = None) -> float:
    result = number_value(value, name)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    if minimum is not None and result < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    return result


def _whole(value: object, name: str, minimum: int, maximum: int | None = None) -> int:
    if isinstance(value, bool):
        raise TypeError(f"{name} must be an integer")
    numeric = _number(value, name)
    if not numeric.is_integer():
        raise TypeError(f"{name} must be an integer-valued number")
    result = int(numeric)
    if result < minimum or (maximum is not None and result > maximum):
        limit = f" and at most {maximum}" if maximum is not None else ""
        raise ValueError(f"{name} must be at least {minimum}{limit}")
    return result


def _ratio(value: object, name: str) -> float:
    result = _number(value, name)
    if not 0.0 <= result <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1")
    return result


def _positive_quantity(
    value: object,
    dims: tuple[int, int, int, int, int],
    name: str,
    *,
    allow_zero: bool = False,
) -> Quantity:
    quantity = require_quantity(value, dims, name)
    if quantity.value < 0 or (quantity.value == 0 and not allow_zero):
        qualifier = "non-negative" if allow_zero else "positive"
        raise ValueError(f"{name} must be {qualifier}")
    return quantity


def _countercurrent_exchange(args: list[object]) -> Record:
    if len(args) != 3:
        raise TypeError("countercurrent_exchange(arterial_temperature, venous_temperature, efficiency) expects 3 arguments")
    arterial = _positive_quantity(args[0], TEMP, "arterial temperature")
    venous = _positive_quantity(args[1], TEMP, "venous temperature")
    efficiency = _ratio(args[2], "exchange efficiency")
    gradient = arterial.value - venous.value
    return Record({
        "temperature_gradient": Quantity(gradient, TEMP),
        "arterial_outlet": Quantity(arterial.value - efficiency * gradient, TEMP),
        "venous_return": Quantity(venous.value + efficiency * gradient, TEMP),
        "efficiency": efficiency,
        "model": "equal_heat_capacity_effectiveness",
    })


def _plumage_insulation(args: list[object]) -> Record:
    if len(args) != 3:
        raise TypeError("plumage_insulation(baseline_index, compression_ratio, wetness_ratio) expects 3 arguments")
    baseline = _number(args[0], "baseline insulation index", minimum=0.0)
    compression = _ratio(args[1], "compression ratio")
    wetness = _ratio(args[2], "wetness ratio")
    effective = baseline * (1.0 - compression) * (1.0 - wetness)
    return Record({
        "baseline_index": baseline,
        "effective_index": effective,
        "retained_fraction": effective / baseline if baseline else 0.0,
        "loss_fraction": 1.0 - (effective / baseline) if baseline else 0.0,
        "model": "multiplicative_illustrative_insulation_index",
    })


def _feather_barrier_profile(args: list[object]) -> Record:
    if len(args) != 5:
        raise TypeError("feather_barrier_profile(baseline, loft, oiling, wetness, compression) expects 5 arguments")
    baseline = _number(args[0], "baseline feather index", minimum=0.0)
    loft = _ratio(args[1], "loft fraction")
    oiling = _ratio(args[2], "oil coverage fraction")
    wetness = _ratio(args[3], "wetness fraction")
    compression = _ratio(args[4], "compression fraction")
    air_retention = loft * (1.0 - compression)
    hydrophobic_factor = 0.5 + 0.5 * oiling
    dryness_factor = 1.0 - wetness
    effective = baseline * air_retention * hydrophobic_factor * dryness_factor
    return Record({
        "effective_insulation_index": effective,
        "air_retention_fraction": air_retention,
        "hydrophobic_factor": hydrophobic_factor,
        "dryness_factor": dryness_factor,
        "assumptions": "normalized comparative index; not a measured thermal conductivity",
    })


def _flight_energy_budget(args: list[object]) -> Record:
    if len(args) != 3:
        raise TypeError("flight_energy_budget(power, duration, available_energy) expects 3 arguments")
    power = _positive_quantity(args[0], POWER, "flight power")
    duration = _positive_quantity(args[1], TIME, "flight duration", allow_zero=True)
    reserve = _positive_quantity(args[2], ENERGY, "available energy", allow_zero=True)
    required = power * duration
    remaining = reserve - required
    used = required.value / reserve.value if reserve.value else (0.0 if required.value == 0 else None)
    return Record({
        "energy_required": required,
        "energy_remaining": remaining,
        "is_sufficient": remaining.value >= 0,
        "fraction_used": used,
    })


def _flight_muscle_profile(args: list[object]) -> Record:
    if len(args) != 4:
        raise TypeError("flight_muscle_profile(aerobic_power, anaerobic_power, duration, fat_share) expects 4 arguments")
    aerobic = _positive_quantity(args[0], POWER, "aerobic power", allow_zero=True)
    anaerobic = _positive_quantity(args[1], POWER, "anaerobic power", allow_zero=True)
    duration = _positive_quantity(args[2], TIME, "flight duration", allow_zero=True)
    fat_share = _ratio(args[3], "aerobic fat share")
    aerobic_energy = aerobic * duration
    anaerobic_energy = anaerobic * duration
    total = aerobic_energy + anaerobic_energy
    return Record({
        "aerobic_energy": aerobic_energy,
        "anaerobic_energy": anaerobic_energy,
        "total_energy": total,
        "fat_oxidation_energy_estimate": Quantity(aerobic_energy.value * fat_share, ENERGY),
        "carbohydrate_and_other_aerobic_energy_estimate": Quantity(aerobic_energy.value * (1.0-fat_share), ENERGY),
        "anaerobic_fraction": anaerobic_energy.value / total.value if total.value else 0.0,
        "fat_share_assumption": fat_share,
    })


def _migration_speed(args: list[object]) -> Quantity:
    if len(args) != 2:
        raise TypeError("migration_speed(distance, duration) expects 2 arguments")
    distance = _positive_quantity(args[0], DISTANCE, "migration distance", allow_zero=True)
    duration = _positive_quantity(args[1], TIME, "migration duration")
    return Quantity(distance.value / duration.value, SPEED)


def _oxygen_pressure_ratio(args: list[object]) -> float:
    if len(args) != 2:
        raise TypeError("oxygen_pressure_ratio(partial_pressure, reference_pressure) expects 2 arguments")
    partial = _positive_quantity(args[0], PRESSURE, "oxygen partial pressure")
    reference = _positive_quantity(args[1], PRESSURE, "reference oxygen pressure")
    return partial.value / reference.value


def _avian_gas_exchange(args: list[object]) -> Record:
    if len(args) != 4:
        raise TypeError("avian_gas_exchange(ventilation_rate, inspired_oxygen_fraction, extraction_fraction, inspired_pressure) expects 4 arguments")
    ventilation = _number(args[0], "ventilation rate", minimum=0.0)
    oxygen_fraction = _ratio(args[1], "inspired oxygen fraction")
    extraction = _ratio(args[2], "oxygen extraction fraction")
    pressure = _positive_quantity(args[3], PRESSURE, "inspired oxygen partial pressure", allow_zero=True)
    inspired_flow = ventilation * oxygen_fraction
    uptake = inspired_flow * extraction
    return Record({
        "ventilation_rate": ventilation,
        "inspired_oxygen_flow": inspired_flow,
        "oxygen_uptake_proxy": uptake,
        "oxygen_pressure": pressure,
        "relative_delivery_proxy": uptake * pressure.value,
        "model": "steady_flow_fraction_model_not_avian_lung_simulation",
    })


def _bill_lamella_filter(args: list[object]) -> Record:
    if len(args) != 3:
        raise TypeError("bill_lamella_filter(particle_diameter, lamella_gap, incoming_particle_rate) expects 3 arguments")
    particle = _number(args[0], "particle diameter", minimum=0.0)
    gap = _number(args[1], "lamella gap", minimum=0.0)
    incoming = _number(args[2], "incoming particle rate", minimum=0.0)
    if particle == 0.0:
        retention = 0.0
    else:
        retention = min(1.0, max(0.0, 1.0 - gap / particle))
    return Record({
        "retention_fraction": retention,
        "captured_particle_rate": incoming * retention,
        "passed_particle_rate": incoming * (1.0-retention),
        "model": "continuous_sieve_approximation",
    })


def _salt_balance(args: list[object]) -> Record:
    if len(args) != 3:
        raise TypeError("salt_balance(intake_rate, renal_excretion_rate, salt_gland_excretion_rate) expects 3 arguments")
    intake = _number(args[0], "salt intake rate", minimum=0.0)
    renal = _number(args[1], "renal salt excretion rate", minimum=0.0)
    gland = _number(args[2], "salt gland excretion rate", minimum=0.0)
    balance = intake - renal - gland
    return Record({
        "net_salt_balance_rate": balance,
        "is_balanced_or_negative": balance <= 0.0,
        "renal_fraction_of_excretion": renal/(renal+gland) if renal+gland else 0.0,
        "salt_gland_fraction_of_excretion": gland/(renal+gland) if renal+gland else 0.0,
        "units": "caller-defined consistent salt-mass or molar amount per time",
    })


def _flock_flight_budget(args: list[object]) -> Record:
    if len(args) != 5:
        raise TypeError("flock_flight_budget(individual_power, duration, bird_count, leader_count, follower_saving_fraction) expects 5 arguments")
    power = _positive_quantity(args[0], POWER, "individual flight power")
    duration = _positive_quantity(args[1], TIME, "flight duration", allow_zero=True)
    bird_count = _whole(args[2], "bird_count", 1)
    leaders = _whole(args[3], "leader_count", 1)
    if leaders > bird_count:
        raise ValueError("leader_count cannot exceed bird_count")
    saving = _ratio(args[4], "follower saving fraction")
    baseline = power * duration * bird_count
    saved = power * duration * (bird_count - leaders) * saving
    return Record({
        "baseline_energy": baseline,
        "estimated_energy_saved": saved,
        "formation_energy": baseline - saved,
        "relative_saving": saved.value / baseline.value if baseline.value else 0.0,
        "leader_count": leaders,
        "follower_count": bird_count - leaders,
        "assumption": "user-specified follower saving; no universal V-formation saving is assumed",
    })


def _visual_system_profile(args: list[object]) -> Record:
    if len(args) != 4:
        raise TypeError("visual_system_profile(horizontal_fov_degrees, acuity_index, ultraviolet_sensitive, underwater_mode) expects 4 arguments")
    fov = _number(args[0], "horizontal field of view", minimum=0.0)
    if fov > 360.0:
        raise ValueError("horizontal field of view cannot exceed 360 degrees")
    acuity = _number(args[1], "acuity index", minimum=0.0)
    ultraviolet = args[2]
    underwater = args[3]
    if not isinstance(ultraviolet, bool) or not isinstance(underwater, bool):
        raise TypeError("ultraviolet_sensitive and underwater_mode must be booleans")
    return Record({
        "horizontal_fov_degrees": fov,
        "acuity_index": acuity,
        "ultraviolet_sensitive": ultraviolet,
        "underwater_mode": underwater,
        "panoramic_fraction": fov / 360.0,
        "sensor_model": "caller_parameterized_visual_profile",
    })


def _imprinting_window(args: list[object]) -> Record:
    if len(args) != 3:
        raise TypeError("imprinting_window(age_hours, window_start_hours, window_end_hours) expects 3 arguments")
    age = _number(args[0], "age hours", minimum=0.0)
    start = _number(args[1], "window start", minimum=0.0)
    end = _number(args[2], "window end", minimum=0.0)
    if end < start:
        raise ValueError("window end must be greater than or equal to window start")
    inside = start <= age <= end
    return Record({
        "age_hours": age,
        "window_start_hours": start,
        "window_end_hours": end,
        "inside_configured_window": inside,
        "window_remaining_hours": max(0.0, end-age) if inside else 0.0,
        "warning": "sensitive period is species- and protocol-dependent",
    })


def _hemispheric_sleep_budget(args: list[object]) -> Record:
    if len(args) != 3:
        raise TypeError("hemispheric_sleep_budget(flock_size, edge_bird_fraction, vigilant_hemisphere_fraction) expects 3 arguments")
    flock_size = _whole(args[0], "flock_size", 1)
    edge_fraction = _ratio(args[1], "edge bird fraction")
    vigilant = _ratio(args[2], "vigilant hemisphere fraction")
    edge_count = min(flock_size, round(flock_size * edge_fraction))
    return Record({
        "flock_size": flock_size,
        "edge_bird_count_estimate": edge_count,
        "edge_hemisphere_vigilance_fraction": vigilant,
        "central_bird_count_estimate": flock_size-edge_count,
        "model": "illustrative_group_vigilance_allocation",
    })


def _magnetic_heading(args: list[object]) -> Record:
    if len(args) != 3:
        raise TypeError("magnetic_heading(geographic_heading, declination_degrees, cue_confidence) expects 3 arguments")
    heading = _number(args[0], "geographic heading") % 360.0
    declination = _number(args[1], "magnetic declination")
    confidence = _ratio(args[2], "magnetic cue confidence")
    correction = declination * confidence
    return Record({
        "corrected_heading_degrees": (heading-correction) % 360.0,
        "declination_degrees": declination,
        "cue_confidence": confidence,
        "model": "simple_heading_correction_not_a_magnetoreception_mechanism",
    })


def _digestive_grinding(args: list[object]) -> Record:
    if len(args) != 3:
        raise TypeError("digestive_grinding(particle_size, grinding_ratio, passes) expects 3 arguments")
    particle = _number(args[0], "particle size", minimum=0.0)
    reduction = _ratio(args[1], "per-pass size reduction")
    passes = _whole(args[2], "passes", 0, 100)
    remaining = particle * ((1.0-reduction) ** passes)
    return Record({
        "initial_particle_size": particle,
        "estimated_particle_size": remaining,
        "total_reduction_fraction": 1.0-(remaining/particle) if particle else 0.0,
        "passes": passes,
        "model": "illustrative_mechanical_grinding_proxy",
    })



def _avian_air_sac_cycle(args: list[object]) -> Record:
    if len(args) != 3:
        raise TypeError("avian_air_sac_cycle(inspired_volume, air_sac_count, parabronchial_transfer_fraction) expects 3 arguments")
    volume = _number(args[0], "inspired air volume", minimum=0.0)
    count = _whole(args[1], "air_sac_count", 5, 14)
    transfer = _ratio(args[2], "parabronchial transfer fraction")
    lung_volume = volume * transfer
    phases = [
        Record({
            "phase": "first_inspiration",
            "flow": "environment_to_posterior_air_sacs",
            "fresh_air_volume": volume,
            "parabronchial_transfer_volume": 0.0,
        }),
        Record({
            "phase": "first_expiration",
            "flow": "posterior_air_sacs_through_palaeopulmonic_parabronchi",
            "fresh_air_volume": 0.0,
            "parabronchial_transfer_volume": lung_volume,
        }),
        Record({
            "phase": "second_inspiration",
            "flow": "parabronchi_to_anterior_sacs_and_new_air_to_posterior_sacs",
            "fresh_air_volume": volume,
            "parabronchial_transfer_volume": 0.0,
        }),
        Record({
            "phase": "second_expiration",
            "flow": "anterior_air_sacs_to_environment",
            "fresh_air_volume": 0.0,
            "parabronchial_transfer_volume": lung_volume,
        }),
    ]
    return Record({
        "air_sac_count_assumption": count,
        "inspired_volume_per_phase": volume,
        "modeled_parabronchial_transfer_volume": lung_volume,
        "phase_count": 4,
        "phases": phases,
        "directional_pathway": "posterior_to_anterior",
        "model": "idealized_palaeopulmonic_airflow_cycle",
        "caveat": "air-sac number and neopulmonic flow patterns vary across bird taxa",
    })


@dataclass(frozen=True, slots=True)
class AnatidaeProfile:
    """Explicit comparative profile; values are inputs, not taxonomic defaults."""

    taxon: str
    foraging_mode: str
    diving_mode: str
    bill_lamella_spacing: float | None = None
    countercurrent_efficiency: float | None = None
    horizontal_fov_degrees: float | None = None
    ultraviolet_sensitive: bool | None = None
    salt_gland_capacity: float | None = None
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.taxon.strip() or not self.foraging_mode.strip() or not self.diving_mode.strip():
            raise ValueError("taxon, foraging_mode and diving_mode are required")
        if self.bill_lamella_spacing is not None and (
            not math.isfinite(self.bill_lamella_spacing) or self.bill_lamella_spacing < 0
        ):
            raise ValueError("bill_lamella_spacing must be finite and non-negative")
        if self.countercurrent_efficiency is not None:
            _ratio(self.countercurrent_efficiency, "countercurrent_efficiency")
        if self.horizontal_fov_degrees is not None and not 0 <= self.horizontal_fov_degrees <= 360:
            raise ValueError("horizontal_fov_degrees must be between 0 and 360")
        if self.ultraviolet_sensitive is not None and not isinstance(self.ultraviolet_sensitive, bool):
            raise TypeError("ultraviolet_sensitive must be a bool or None")
        if self.salt_gland_capacity is not None and (
            not math.isfinite(self.salt_gland_capacity) or self.salt_gland_capacity < 0
        ):
            raise ValueError("salt_gland_capacity must be finite and non-negative")

    def to_record(self) -> Record:
        values = asdict(self)
        values["evidence_refs"] = list(self.evidence_refs)
        values["profile_status"] = "parameterized_not_taxonomically_verified"
        return Record(values)


ANATIDAE_BUILTINS: dict[str, Callable[[list[object]], object]] = {
    "countercurrent_exchange": _countercurrent_exchange,
    "plumage_insulation": _plumage_insulation,
    "feather_barrier_profile": _feather_barrier_profile,
    "flight_energy_budget": _flight_energy_budget,
    "flight_muscle_profile": _flight_muscle_profile,
    "migration_speed": _migration_speed,
    "oxygen_pressure_ratio": _oxygen_pressure_ratio,
    "avian_gas_exchange": _avian_gas_exchange,
    "avian_air_sac_cycle": _avian_air_sac_cycle,
    "bill_lamella_filter": _bill_lamella_filter,
    "salt_balance": _salt_balance,
    "flock_flight_budget": _flock_flight_budget,
    "visual_system_profile": _visual_system_profile,
    "imprinting_window": _imprinting_window,
    "hemispheric_sleep_budget": _hemispheric_sleep_budget,
    "magnetic_heading": _magnetic_heading,
    "digestive_grinding": _digestive_grinding,
}

__all__ = ["AnatidaeProfile", "ANATIDAE_BUILTINS"]
