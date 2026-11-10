"""Bounded discrete statistical and open-system models for SAMBU.

These helpers are small, deterministic numerical models. They deliberately do
not claim to be a general-purpose quantum simulator or a full Lindblad solver.
"""
from __future__ import annotations

import math
from typing import Callable

from .values import ENERGY, TEMP, TIME, Quantity, Record, number_value, require_quantity

BOLTZMANN_CONSTANT = 1.380649e-23
PLANCK_TIME_SECONDS = 5.391247e-44
_FREQUENCY = (0, 0, -1, 0, 0)
_ENERGY_PER_TEMPERATURE = (1, 2, -2, -1, 0)
_MAX_STATES = 4096
_MAX_TRANSPORT_DIMENSION = 32


def _energy_levels(value: object) -> list[Quantity]:
    if not isinstance(value, list) or not value:
        raise TypeError("energy_levels must be a non-empty array")
    if len(value) > _MAX_STATES:
        raise ValueError(f"energy_levels accepts at most {_MAX_STATES} states")
    return [require_quantity(item, ENERGY, "energy level") for item in value]


def _number_array(value: object, what: str, *, maximum: int = _MAX_STATES) -> list[float]:
    if not isinstance(value, list) or not value:
        raise TypeError(f"{what} must be a non-empty array")
    if len(value) > maximum:
        raise ValueError(f"{what} accepts at most {maximum} items")
    result = [number_value(item, what) for item in value]
    if any(not math.isfinite(item) for item in result):
        raise ValueError(f"{what} must contain only finite values")
    return result


def _probabilities(value: object, expected: int | None = None) -> list[float]:
    values = _number_array(value, "probabilities")
    if expected is not None and len(values) != expected:
        raise ValueError("probability count must match the energy-level count")
    if any(item < 0.0 for item in values):
        raise ValueError("probabilities cannot be negative")
    total = math.fsum(values)
    if not math.isclose(total, 1.0, rel_tol=1e-9, abs_tol=1e-9):
        raise ValueError("probabilities must sum to 1")
    return [item / total for item in values]


def _rate_and_time(rate_value: object, time_value: object) -> tuple[float, float]:
    rate = require_quantity(rate_value, _FREQUENCY, "rate")
    elapsed = require_quantity(time_value, TIME, "elapsed time")
    if rate.value < 0.0:
        raise ValueError("rate cannot be negative")
    if elapsed.value < 0.0:
        raise ValueError("elapsed time cannot be negative")
    return rate.value, elapsed.value


def planck_time(args: list[object]) -> Quantity:
    """Return the Planck time scale in SI seconds."""
    if args:
        raise TypeError("planck_time() expects no arguments")
    return Quantity(PLANCK_TIME_SECONDS, TIME)


def canonical_ensemble(args: list[object]) -> Record:
    """Calculate stable canonical probabilities and thermodynamic moments."""
    if len(args) != 2:
        raise TypeError("canonical_ensemble(energy_levels, temperature) expects 2 arguments")
    energies = _energy_levels(args[0])
    temperature = require_quantity(args[1], TEMP, "temperature")
    if temperature.value <= 0.0:
        raise ValueError("temperature must be greater than zero kelvin")

    thermal_energy = BOLTZMANN_CONSTANT * temperature.value
    reference = min(item.value for item in energies)
    weights = [math.exp(-((item.value - reference) / thermal_energy)) for item in energies]
    partition_relative = math.fsum(weights)
    if not math.isfinite(partition_relative) or partition_relative <= 0.0:
        raise ValueError("canonical partition sum is not numerically representable")
    probabilities = [weight / partition_relative for weight in weights]

    mean_energy = math.fsum(p * item.value for p, item in zip(probabilities, energies))
    energy_variance = math.fsum(
        p * (item.value - mean_energy) ** 2
        for p, item in zip(probabilities, energies)
    )
    entropy_nats = -math.fsum(p * math.log(p) for p in probabilities if p > 0.0)
    free_energy = mean_energy - thermal_energy * entropy_nats
    heat_capacity = energy_variance / (
        BOLTZMANN_CONSTANT * temperature.value * temperature.value
    )

    return Record({
        "partition_relative": partition_relative,
        "reference_energy": Quantity(reference, ENERGY),
        "probabilities": probabilities,
        "mean_energy": Quantity(mean_energy, ENERGY),
        "energy_variance": Quantity(energy_variance, (2, 4, -4, 0, 0)),
        "entropy_nats": entropy_nats,
        "entropy": Quantity(BOLTZMANN_CONSTANT * entropy_nats, _ENERGY_PER_TEMPERATURE),
        "free_energy": Quantity(free_energy, ENERGY),
        "heat_capacity": Quantity(heat_capacity, _ENERGY_PER_TEMPERATURE),
        "effective_state_count": math.exp(entropy_nats),
        "state_count": len(energies),
        "model": "finite_discrete_canonical_ensemble",
    })


def microcanonical_ensemble(args: list[object]) -> Record:
    """Assign equal weights to states within a supplied energy window."""
    if len(args) != 3:
        raise TypeError(
            "microcanonical_ensemble(energy_levels, target_energy, tolerance) expects 3 arguments"
        )
    energies = _energy_levels(args[0])
    target = require_quantity(args[1], ENERGY, "target energy")
    tolerance = require_quantity(args[2], ENERGY, "energy tolerance")
    if tolerance.value < 0.0:
        raise ValueError("energy tolerance cannot be negative")

    selected = [
        index for index, item in enumerate(energies)
        if abs(item.value - target.value) <= tolerance.value
    ]
    if not selected:
        raise ValueError("no microstates fall within the supplied energy window")
    probability = 1.0 / len(selected)
    populations = [
        probability if index in set(selected) else 0.0
        for index in range(len(energies))
    ]
    mean_energy = math.fsum(energies[index].value for index in selected) / len(selected)
    entropy_nats = math.log(len(selected))
    return Record({
        "selected_indices": selected,
        "probabilities": populations,
        "degeneracy": len(selected),
        "mean_energy": Quantity(mean_energy, ENERGY),
        "entropy_nats": entropy_nats,
        "model": "finite_window_microcanonical_ensemble",
    })


def markov_relaxation(args: list[object]) -> Record:
    """Relax populations analytically toward a canonical stationary distribution.

    This is a reversible continuous-time Markov reset model with detailed
    balance, not a quantum Lindblad evolution.
    """
    if len(args) != 5:
        raise TypeError(
            "markov_relaxation(energy_levels, initial_populations, temperature, rate, elapsed) "
            "expects 5 arguments"
        )
    energies = _energy_levels(args[0])
    initial = _probabilities(args[1], expected=len(energies))
    temperature = args[2]
    rate, elapsed = _rate_and_time(args[3], args[4])
    equilibrium_record = canonical_ensemble([energies, temperature])
    equilibrium = equilibrium_record.get("probabilities")
    factor = math.exp(-(rate * elapsed))
    populations = [
        target + (start - target) * factor
        for start, target in zip(initial, equilibrium)
    ]
    total = math.fsum(populations)
    populations = [item / total for item in populations]

    mean_energy = math.fsum(
        p * energy.value for p, energy in zip(populations, energies)
    )
    entropy_nats = -math.fsum(
        p * math.log(p) for p in populations if p > 0.0
    )
    return Record({
        "initial_populations": initial,
        "equilibrium_populations": equilibrium,
        "populations": populations,
        "relaxation_factor": factor,
        "mean_energy": Quantity(mean_energy, ENERGY),
        "entropy_nats": entropy_nats,
        "rate": args[3],
        "elapsed": args[4],
        "model": "detailed_balance_markov_relaxation",
    })


def lindblad_dephase(args: list[object]) -> Record:
    """Apply a trace-preserving two-level pure-dephasing Lindblad channel.

    The supported density matrix is real and symmetric; complex coherences and
    Hamiltonian evolution are intentionally outside this small API.
    """
    if len(args) != 3:
        raise TypeError("lindblad_dephase(density_matrix, rate, elapsed) expects 3 arguments")
    matrix = args[0]
    if (
        not isinstance(matrix, list) or len(matrix) != 2
        or any(not isinstance(row, list) or len(row) != 2 for row in matrix)
    ):
        raise TypeError("density_matrix must be a 2x2 array")
    p0 = number_value(matrix[0][0], "density matrix element")
    c01 = number_value(matrix[0][1], "density matrix element")
    c10 = number_value(matrix[1][0], "density matrix element")
    p1 = number_value(matrix[1][1], "density matrix element")
    values = (p0, c01, c10, p1)
    if any(not math.isfinite(value) for value in values):
        raise ValueError("density matrix elements must be finite")
    if not math.isclose(c01, c10, rel_tol=1e-9, abs_tol=1e-12):
        raise ValueError("real density matrix must be symmetric")
    if p0 < 0.0 or p1 < 0.0 or not math.isclose(p0 + p1, 1.0, abs_tol=1e-9):
        raise ValueError("density matrix must have non-negative populations and unit trace")
    coherence = 0.5 * (c01 + c10)
    if p0 * p1 - coherence * coherence < -1e-12:
        raise ValueError("density matrix must be positive semidefinite")

    rate, elapsed = _rate_and_time(args[1], args[2])
    factor = math.exp(-(rate * elapsed))
    decayed = coherence * factor
    result_matrix = [[p0, decayed], [decayed, p1]]
    purity = p0 * p0 + p1 * p1 + 2.0 * decayed * decayed
    return Record({
        "matrix": result_matrix,
        "trace": p0 + p1,
        "purity": purity,
        "coherence_before": coherence,
        "coherence_after": decayed,
        "dephasing_factor": factor,
        "rate": args[1],
        "elapsed": args[2],
        "model": "two_level_real_pure_dephasing_lindblad_channel",
    })


def onsager_flux(args: list[object]) -> Record:
    """Calculate linear-response fluxes for a symmetric Onsager matrix."""
    if len(args) != 2:
        raise TypeError("onsager_flux(gradients, coefficients) expects 2 arguments")
    gradients = _number_array(args[0], "gradients", maximum=_MAX_TRANSPORT_DIMENSION)
    matrix = args[1]
    size = len(gradients)
    if (
        not isinstance(matrix, list) or len(matrix) != size
        or any(not isinstance(row, list) or len(row) != size for row in matrix)
    ):
        raise ValueError("Onsager coefficient matrix must be square and match the gradient count")
    coefficients = [
        [number_value(value, "Onsager coefficient") for value in row]
        for row in matrix
    ]
    if any(not math.isfinite(value) for row in coefficients for value in row):
        raise ValueError("Onsager coefficients must be finite")
    for i in range(size):
        for j in range(i + 1, size):
            if not math.isclose(
                coefficients[i][j], coefficients[j][i], rel_tol=1e-9, abs_tol=1e-12
            ):
                raise ValueError("Onsager coefficient matrix must be symmetric")

    fluxes = [
        -math.fsum(coefficients[i][j] * gradients[j] for j in range(size))
        for i in range(size)
    ]
    entropy_production = -math.fsum(
        gradients[index] * fluxes[index] for index in range(size)
    )
    scale = max(1.0, math.fsum(abs(g * f) for g, f in zip(gradients, fluxes)))
    if entropy_production < -1e-12 * scale:
        raise ValueError("Onsager coefficients produce negative dissipation for this gradient")
    entropy_production = max(0.0, entropy_production)
    return Record({
        "fluxes": fluxes,
        "entropy_production": entropy_production,
        "dimension": size,
        "model": "symmetric_linear_onsager_response",
    })


def phonon_decay(args: list[object]) -> object:
    """Apply exponential amplitude relaxation to a scalar phonon mode."""
    if len(args) != 3:
        raise TypeError("phonon_decay(amplitude, rate, elapsed) expects 3 arguments")
    amplitude = args[0]
    if isinstance(amplitude, Quantity):
        if not math.isfinite(amplitude.value):
            raise ValueError("amplitude must be finite")
    else:
        amplitude = number_value(amplitude, "amplitude")
        if not math.isfinite(amplitude):
            raise ValueError("amplitude must be finite")
    rate, elapsed = _rate_and_time(args[1], args[2])
    return amplitude * math.exp(-(rate * elapsed))


OPEN_SYSTEM_BUILTINS: dict[str, Callable[[list[object]], object]] = {
    "planck_time": planck_time,
    "canonical_ensemble": canonical_ensemble,
    "microcanonical_ensemble": microcanonical_ensemble,
    "markov_relaxation": markov_relaxation,
    "lindblad_dephase": lindblad_dephase,
    "onsager_flux": onsager_flux,
    "phonon_decay": phonon_decay,
}


__all__ = [
    "BOLTZMANN_CONSTANT", "OPEN_SYSTEM_BUILTINS", "PLANCK_TIME_SECONDS",
    "canonical_ensemble", "lindblad_dephase", "markov_relaxation",
    "microcanonical_ensemble", "onsager_flux", "phonon_decay", "planck_time",
]
