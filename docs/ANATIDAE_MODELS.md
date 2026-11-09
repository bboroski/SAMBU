# Anatidae-inspired scientific models

SAMBU 0.10 includes a small set of configurable models inspired by the supplied Anatidae research brief. The functions are generic calculation templates: values such as heat-exchange efficiency, plumage compression, wetness, flight power and reserve energy must be supplied by the caller.

## Counter-current heat exchange

~~~sambu
let limb = countercurrent_exchange(310 * K, 280 * K, 75%)
print(limb.venous_return)
print(limb.arterial_outlet)
~~~

The simple equal-capacity model interpolates between arterial and venous inlet temperatures using a dimensionless efficiency from 0% to 100%. It illustrates the direction and sensitivity of heat exchange; it is not a species-specific physiological model.

## Plumage insulation index

~~~sambu
let coat = plumage_insulation(0.9, 25%, 10%)
print(coat.effective_index)
~~~

The returned normalized index is the supplied baseline multiplied by the uncompressed and dry fractions. It is not a measured thermal resistance or a substitute for feather-material testing.

## Flight energy and migration

~~~sambu
let budget = flight_energy_budget((10 * J) / (1 * s), 5 * s, 60 * J)
print(budget.energy_required)
print(budget.energy_remaining)
print(budget.is_sufficient)
print(migration_speed(150 * km, 10800 * s))
~~~

Power, time, energy, distance and speed are dimension-checked. The model compares an explicitly supplied flight-energy requirement with an available-energy reserve. It does not infer metabolic power, migration altitude, oxygen affinity, or real-world endurance.

## Relative oxygen pressure

oxygen_pressure_ratio(altitude_partial_pressure, reference_partial_pressure) returns a ratio of two positive pressure quantities. This is a pressure comparison only—not a prediction of haemoglobin saturation, tissue oxygenation, or flight performance.

## Scientific caution

Anatidae is a diverse family. Plumage, diving, feeding, salt excretion, vision, flight performance, air-sac anatomy and behaviour differ among taxa and conditions. The report that motivated these utilities contains some highly specific claims that should not be promoted to universal constants without a species-specific source. SAMBU therefore keeps the models parameterized and exposes assumptions to the caller.
