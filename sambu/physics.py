"""Deterministic SI physics and bounded motion helpers for SAMBU.

These are reference models, not a real-time solver or hardware controller.
All functions are pure: they do not mutate inputs, access devices, or allocate
unbounded state.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class MotionSample:
    """Position, velocity and acceleration at one sampled instant."""

    position: float
    velocity: float
    acceleration: float


def _finite(*values: float) -> bool:
    return all(math.isfinite(float(value)) for value in values)


def newton_force(mass_kg: float, acceleration_m_s2: float) -> float:
    """Return force in newtons from mass (kg) and acceleration (m/s²)."""
    if not _finite(mass_kg, acceleration_m_s2) or mass_kg < 0:
        raise ValueError("mass must be finite and non-negative; acceleration finite")
    return mass_kg * acceleration_m_s2


def kinetic_energy(mass_kg: float, velocity_m_s: float) -> float:
    """Return translational kinetic energy in joules."""
    if not _finite(mass_kg, velocity_m_s) or mass_kg < 0:
        raise ValueError("mass must be finite and non-negative; velocity finite")
    return 0.5 * mass_kg * velocity_m_s * velocity_m_s


def spring_damper_force(
    displacement_m: float,
    velocity_m_s: float,
    stiffness_n_m: float,
    damping_n_s_m: float,
) -> float:
    """Return the linear spring-damper restoring force in newtons."""
    if not _finite(displacement_m, velocity_m_s, stiffness_n_m, damping_n_s_m):
        raise ValueError("spring-damper inputs must be finite")
    if stiffness_n_m < 0 or damping_n_s_m < 0:
        raise ValueError("stiffness and damping must be non-negative")
    return -(stiffness_n_m * displacement_m + damping_n_s_m * velocity_m_s)


def constant_acceleration(
    position_m: float,
    velocity_m_s: float,
    acceleration_m_s2: float,
    elapsed_s: float,
) -> MotionSample:
    """Evaluate one-dimensional constant-acceleration kinematics."""
    if not _finite(position_m, velocity_m_s, acceleration_m_s2, elapsed_s):
        raise ValueError("kinematic inputs must be finite")
    if elapsed_s < 0:
        raise ValueError("elapsed time must be non-negative")
    return MotionSample(
        position=position_m + velocity_m_s * elapsed_s
        + 0.5 * acceleration_m_s2 * elapsed_s * elapsed_s,
        velocity=velocity_m_s + acceleration_m_s2 * elapsed_s,
        acceleration=acceleration_m_s2,
    )


def first_order_response(
    initial_value: float,
    target_value: float,
    time_constant_s: float,
    elapsed_s: float,
) -> float:
    """Evaluate y(t)=target+(initial-target)*exp(-t/tau), for tau > 0."""
    if not _finite(initial_value, target_value, time_constant_s, elapsed_s):
        raise ValueError("response inputs must be finite")
    if time_constant_s <= 0 or elapsed_s < 0:
        raise ValueError("time constant must be positive and elapsed time non-negative")
    return target_value + (initial_value - target_value) * math.exp(
        -elapsed_s / time_constant_s
    )


def thermal_response(
    temperature_c: float,
    ambient_c: float,
    time_constant_s: float,
    elapsed_s: float,
) -> float:
    """Return a lumped first-order body's temperature in degrees Celsius."""
    return first_order_response(temperature_c, ambient_c, time_constant_s, elapsed_s)


def rc_voltage(
    initial_voltage_v: float,
    target_voltage_v: float,
    resistance_ohm: float,
    capacitance_f: float,
    elapsed_s: float,
) -> float:
    """Evaluate an ideal first-order RC voltage response (R in Ω, C in F)."""
    if not _finite(resistance_ohm, capacitance_f) or resistance_ohm <= 0 or capacitance_f <= 0:
        raise ValueError("resistance and capacitance must be finite and positive")
    return first_order_response(
        initial_voltage_v, target_voltage_v, resistance_ohm * capacitance_f, elapsed_s
    )


def sample_quintic_trajectory(
    start_position: float,
    end_position: float,
    duration_s: float,
    elapsed_s: float,
) -> MotionSample:
    """Sample a C²-continuous rest-to-rest quintic trajectory.

    The requested time is clamped to [0, duration]. Endpoint velocity and
    acceleration are zero; position, velocity and acceleration use the same
    deterministic analytic profile on every call.
    """
    if not _finite(start_position, end_position, duration_s, elapsed_s):
        raise ValueError("trajectory inputs must be finite")
    if duration_s <= 0 or elapsed_s < 0:
        raise ValueError("duration must be positive and elapsed time non-negative")

    t = min(elapsed_s, duration_s)
    u = t / duration_s
    u2, u3 = u * u, u * u * u
    u4, u5 = u3 * u, u3 * u2
    delta = end_position - start_position
    blend = 10.0 * u3 - 15.0 * u4 + 6.0 * u5
    blend_rate = 30.0 * u2 - 60.0 * u3 + 30.0 * u4
    blend_accel = 60.0 * u - 180.0 * u2 + 120.0 * u3
    return MotionSample(
        position=start_position + delta * blend,
        velocity=delta * blend_rate / duration_s,
        acceleration=delta * blend_accel / (duration_s * duration_s),
    )


def sample_animatronic_joint(
    start_angle_rad: float,
    target_angle_rad: float,
    elapsed_s: float,
    duration_s: float,
    min_angle_rad: float,
    max_angle_rad: float,
    max_velocity_rad_s: float,
    max_acceleration_rad_s2: float,
) -> MotionSample:
    """Sample a bounded animatronic joint trajectory without commanding hardware.

    The rest-to-rest quintic trajectory's exact peak factors are 1.875 for
    velocity and 10/sqrt(3) for acceleration. Infeasible plans are rejected
    before a sample is returned.
    """
    values = (
        start_angle_rad, target_angle_rad, elapsed_s, duration_s,
        min_angle_rad, max_angle_rad, max_velocity_rad_s, max_acceleration_rad_s2,
    )
    if not _finite(*values):
        raise ValueError("joint trajectory inputs must be finite")
    if min_angle_rad > max_angle_rad or not (
        min_angle_rad <= start_angle_rad <= max_angle_rad
        and min_angle_rad <= target_angle_rad <= max_angle_rad
    ):
        raise ValueError("joint angles must remain inside the configured range")
    if max_velocity_rad_s <= 0 or max_acceleration_rad_s2 <= 0:
        raise ValueError("joint velocity and acceleration limits must be positive")
    if duration_s <= 0:
        raise ValueError("duration must be positive")

    distance = abs(target_angle_rad - start_angle_rad)
    required_velocity = 1.875 * distance / duration_s
    required_acceleration = (10.0 / math.sqrt(3.0)) * distance / (duration_s * duration_s)
    tolerance = 1e-12
    if required_velocity > max_velocity_rad_s + tolerance:
        raise ValueError("trajectory exceeds the joint velocity limit")
    if required_acceleration > max_acceleration_rad_s2 + tolerance:
        raise ValueError("trajectory exceeds the joint acceleration limit")
    return sample_quintic_trajectory(start_angle_rad, target_angle_rad, duration_s, elapsed_s)
