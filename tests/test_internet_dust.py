import math
import pytest

from sambu.internet_dust import (
    DustProfile, Particle, rayleigh_relative_intensity, simulate,
)


def particle(**overrides):
    values = dict(
        particle_id="p1", position_m=(0.0, 0.0, 0.0),
        velocity_m_s=(0.0, 0.0, 0.0), mass_kg=1e-12,
        radius_m=1e-6, charge_c=0.0,
    )
    values.update(overrides)
    return Particle(**values)


def profile(**overrides):
    values = dict(viscosity_pa_s=1.81e-5, temperature_k=0.0,
                  gravity_m_s2=(0.0, 0.0, 0.0))
    values.update(overrides)
    return DustProfile(**values)


def test_zero_force_state_is_reproducible():
    p = particle()
    a = simulate([p], profile(), dt_s=0.01, steps=10, seed=7)
    b = simulate([p], profile(), dt_s=0.01, steps=10, seed=7)
    assert a == b
    assert a.particles[0].position_m == (0.0, 0.0, 0.0)


def test_electric_field_changes_velocity_in_expected_direction():
    p = particle(mass_kg=1e-9, charge_c=1e-12)
    result = simulate([p], profile(electric_field_v_m=(100.0, 0.0, 0.0)),
                      dt_s=1e-4, steps=1, seed=1)
    assert result.particles[0].velocity_m_s[0] > 0


def test_thermal_noise_is_seed_reproducible():
    p = particle()
    a = simulate([p], profile(temperature_k=293.15), dt_s=1e-4, steps=2, seed=9)
    b = simulate([p], profile(temperature_k=293.15), dt_s=1e-4, steps=2, seed=9)
    assert a == b


@pytest.mark.parametrize("kwargs", [
    {"dt_s": 0.0, "steps": 1},
    {"dt_s": 0.2, "steps": 1},
    {"dt_s": 0.01, "steps": 10001},
])
def test_bounds_are_enforced(kwargs):
    args = dict(dt_s=0.01, steps=1, seed=1)
    args.update(kwargs)
    with pytest.raises(ValueError):
        simulate([particle()], profile(), **args)


def test_rejects_stokes_model_outside_declared_regime():
    fast = particle(velocity_m_s=(10.0, 0.0, 0.0))
    with pytest.raises(ValueError, match="outside Stokes regime"):
        simulate([fast], profile(), dt_s=0.001, steps=1, seed=1)


def test_rayleigh_domain_is_enforced():
    assert rayleigh_relative_intensity(1e-9, 500e-9) > 0
    with pytest.raises(ValueError):
        rayleigh_relative_intensity(100e-9, 500e-9)
