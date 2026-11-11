"""Bounded, deterministic Langevin reference model for fictional Internet Dust.

This module is a computational model, not a claim that Internet Dust exists.
It intentionally supports only low-Reynolds-number Stokes drag (Re <= 0.1).
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Iterable

BOLTZMANN = 1.380649e-23
MODEL_ID = "internet-dust.langevin-stokes.v1"
MAX_PARTICLES = 1024
MAX_STEPS = 10000
MAX_DT_S = 0.1


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _vector3(value: Iterable[float], name: str) -> tuple[float, float, float]:
    parts = tuple(_finite(v, name) for v in value)
    if len(parts) != 3:
        raise ValueError(f"{name} must contain exactly 3 values")
    return parts  # type: ignore[return-value]


@dataclass(frozen=True)
class DustProfile:
    viscosity_pa_s: float
    temperature_k: float
    fluid_velocity_m_s: tuple[float, float, float] = (0.0, 0.0, 0.0)
    gravity_m_s2: tuple[float, float, float] = (0.0, 0.0, -9.80665)
    electric_field_v_m: tuple[float, float, float] = (0.0, 0.0, 0.0)
    magnetic_field_t: tuple[float, float, float] = (0.0, 0.0, 0.0)
    max_reynolds: float = 0.1

    def __post_init__(self) -> None:
        if _finite(self.viscosity_pa_s, "viscosity_pa_s") <= 0:
            raise ValueError("viscosity_pa_s must be positive")
        if _finite(self.temperature_k, "temperature_k") < 0:
            raise ValueError("temperature_k must be non-negative")
        if not 0 < _finite(self.max_reynolds, "max_reynolds") <= 0.1:
            raise ValueError("max_reynolds must be in (0, 0.1]")
        for field in ("fluid_velocity_m_s", "gravity_m_s2",
                      "electric_field_v_m", "magnetic_field_t"):
            object.__setattr__(self, field, _vector3(getattr(self, field), field))


@dataclass(frozen=True)
class Particle:
    particle_id: str
    position_m: tuple[float, float, float]
    velocity_m_s: tuple[float, float, float]
    mass_kg: float
    radius_m: float
    charge_c: float = 0.0

    def __post_init__(self) -> None:
        if not self.particle_id:
            raise ValueError("particle_id must not be empty")
        object.__setattr__(self, "position_m", _vector3(self.position_m, "position_m"))
        object.__setattr__(self, "velocity_m_s", _vector3(self.velocity_m_s, "velocity_m_s"))
        if _finite(self.mass_kg, "mass_kg") <= 0:
            raise ValueError("mass_kg must be positive")
        if _finite(self.radius_m, "radius_m") <= 0:
            raise ValueError("radius_m must be positive")
        object.__setattr__(self, "charge_c", _finite(self.charge_c, "charge_c"))


@dataclass(frozen=True)
class SimulationResult:
    particles: tuple[Particle, ...]
    time_s: float
    steps: int
    seed: int
    model_id: str = MODEL_ID
    evidence: str = "simulated"


def reynolds_number(particle: Particle, profile: DustProfile) -> float:
    """Particle Reynolds number using diameter and relative fluid speed."""
    relative = tuple(particle.velocity_m_s[i] - profile.fluid_velocity_m_s[i]
                     for i in range(3))
    speed = math.sqrt(sum(v * v for v in relative))
    # Air density is not guessed: this reference profile requires the caller
    # to supply it in a future extension. Use the dimensionless Stokes check
    # only when density is supplied by the explicit helper below.
    return speed


def simulate(
    particles: Iterable[Particle],
    profile: DustProfile,
    *,
    dt_s: float,
    steps: int,
    seed: int,
    fluid_density_kg_m3: float = 1.204,
) -> SimulationResult:
    """Advance a bounded particle ensemble with Euler-Maruyama integration.

    The default density is a declared reference value (dry air near room
    temperature), not a measurement. Set it explicitly for other media.
    """
    dt = _finite(dt_s, "dt_s")
    density = _finite(fluid_density_kg_m3, "fluid_density_kg_m3")
    if not 0 < dt <= MAX_DT_S:
        raise ValueError(f"dt_s must be in (0, {MAX_DT_S}]")
    if not isinstance(steps, int) or not 0 <= steps <= MAX_STEPS:
        raise ValueError(f"steps must be an integer in [0, {MAX_STEPS}]")
    if not isinstance(seed, int):
        raise ValueError("seed must be an integer")
    if density <= 0:
        raise ValueError("fluid_density_kg_m3 must be positive")

    state = tuple(particles)
    if len(state) > MAX_PARTICLES:
        raise ValueError(f"particle count exceeds {MAX_PARTICLES}")
    if len({p.particle_id for p in state}) != len(state):
        raise ValueError("particle_id values must be unique")

    rng = random.Random(seed)
    current = list(state)
    for _ in range(steps):
        updated: list[Particle] = []
        for p in current:
            gamma = 6.0 * math.pi * profile.viscosity_pa_s * p.radius_m
            rel = tuple(p.velocity_m_s[i] - profile.fluid_velocity_m_s[i]
                        for i in range(3))
            speed = math.sqrt(sum(v * v for v in rel))
            reynolds = density * speed * (2.0 * p.radius_m) / profile.viscosity_pa_s
            if reynolds > profile.max_reynolds:
                raise ValueError(
                    f"particle {p.particle_id} outside Stokes regime: Re={reynolds:.6g}"
                )

            # Lorentz force q(E + v x B), plus gravity and Stokes drag.
            vx, vy, vz = p.velocity_m_s
            bx, by, bz = profile.magnetic_field_t
            ex, ey, ez = profile.electric_field_v_m
            lorentz = (
                p.charge_c * (ex + vy * bz - vz * by),
                p.charge_c * (ey + vz * bx - vx * bz),
                p.charge_c * (ez + vx * by - vy * bx),
            )
            thermal_sigma = math.sqrt(
                2.0 * BOLTZMANN * profile.temperature_k * gamma / dt
            ) if profile.temperature_k else 0.0
            acceleration = []
            for i in range(3):
                deterministic_force = (
                    p.mass_kg * profile.gravity_m_s2[i]
                    - gamma * rel[i]
                    + lorentz[i]
                )
                thermal_force = thermal_sigma * rng.gauss(0.0, 1.0)
                acceleration.append(
                    (deterministic_force + thermal_force) / p.mass_kg
                )
            velocity = tuple(p.velocity_m_s[i] + acceleration[i] * dt
                             for i in range(3))
            position = tuple(p.position_m[i] + velocity[i] * dt
                             for i in range(3))
            updated.append(Particle(
                p.particle_id, position, velocity, p.mass_kg,
                p.radius_m, p.charge_c
            ))
        current = updated

    return SimulationResult(tuple(current), steps * dt, steps, seed)


def rayleigh_relative_intensity(radius_m: float, wavelength_m: float) -> float:
    """Return a normalized Rayleigh scaling proxy, valid only for x << 1."""
    radius = _finite(radius_m, "radius_m")
    wavelength = _finite(wavelength_m, "wavelength_m")
    if radius <= 0 or wavelength <= 0:
        raise ValueError("radius_m and wavelength_m must be positive")
    size_parameter = 2.0 * math.pi * radius / wavelength
    if size_parameter >= 0.1:
        raise ValueError("Rayleigh approximation requires 2*pi*r/lambda < 0.1")
    return (radius / wavelength) ** 6
