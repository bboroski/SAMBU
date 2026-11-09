# Comparative Anatidae models

SAMBU 0.11 expands the Anatidae domain layer into configurable, inspectable calculation primitives. The models can be used for comparative ecology, teaching, hypothesis exploration and synthetic experiments. They are not a veterinary diagnostic system or a species-specific physiology database.

## Design rule: measurements in, assumptions visible

The source research brief contains a mixture of well-established avian adaptations and numerical claims that depend on species, population, conditions or study design. SAMBU does not hard-code claims such as a fixed migration speed, 30% V-formation saving, a universal imprinting window, a universal nine-air-sac anatomy, or a uniform UV/magnetic sensory profile. Those must be supplied as measured parameters or explicitly labelled assumptions.

## Thermoregulation and feather barrier

~~~sambu
let limb = countercurrent_exchange(310 * K, 280 * K, 75%)
let coat = feather_barrier_profile(1, 90%, 80%, 10%, 20%)
print(limb.venous_return)
print(limb.arterial_outlet)
print(coat.effective_insulation_index)
~~~

countercurrent_exchange is an equal-heat-capacity effectiveness model. feather_barrier_profile forms a normalized comparison index from caller-supplied loft, oil coverage, wetness and compression fractions. Neither returns measured thermal conductivity or predicts tissue temperature.

## Vision and sensory profile

~~~sambu
let vision = visual_system_profile(330, 0.8, true, true)
print(vision.panoramic_fraction)
print(vision.ultraviolet_sensitive)
~~~

Field of view, acuity index, UV sensitivity and underwater mode are explicit profile fields. The function does not derive species visual acuity or prove a magnetic-reception mechanism.

magnetic_heading(geographic_heading, declination, cue_confidence) is a simple compass-correction demonstration. It is not a model of cryptochrome radical-pair chemistry, neural processing or a bird's actual navigation decision.

## Respiratory system and gas exchange

~~~sambu
let cycle = avian_air_sac_cycle(100, 9, 80%)
let gas = avian_gas_exchange(100, 21%, 40%, 20 * Pa)
print(cycle.phase_count)
print(cycle.phases[1].flow)
print(gas.oxygen_uptake_proxy)
~~~

The four-phase airflow model illustrates an idealized palaeopulmonic pathway: first inspiration moves air toward posterior sacs; first expiration moves air through exchange tissue; the following inspiration moves it toward anterior sacs while fresh air enters posterior sacs; the following expiration expels air from the anterior group. The model's air-sac count is an explicit input because the number and fusion pattern vary among bird taxa. Some neopulmonic regions can exhibit bidirectional flow, so the simplified caudocranial model is not a complete model of every avian lung.

The gas-exchange function is a steady-flow proxy. It does not calculate blood-gas diffusion, haemoglobin affinity, ventilation-perfusion distribution, oxygen saturation or tissue hypoxia.

## Bill filtration and salt balance

~~~sambu
let filter = bill_lamella_filter(2, 0.5, 100)
let salt = salt_balance(20, 5, 16)
print(filter.retention_fraction)
print(filter.captured_particle_rate)
print(salt.net_salt_balance_rate)
~~~

bill_lamella_filter is a continuous sieving approximation. Real bill lamellae, prey sizes, fluid dynamics, flow rates and feeding strategies vary across dabbling ducks, diving ducks and specialized fish-eaters.

salt_balance compares caller-supplied intake and two excretion rates in a consistent user-defined unit. It does not infer whether the bird has functional nasal salt glands. Salt-gland physiology differs by taxon and habitat; comparative studies of wild ducks show that renal and salt-gland contributions need to be evaluated by species and condition.

## Flight energetics and flocking

~~~sambu
let muscles = flight_muscle_profile(
    (8 * J) / (1 * s),
    (2 * J) / (1 * s),
    5 * s,
    75%
)
let formation = flock_flight_budget(
    (10 * J) / (1 * s),
    10 * s,
    12,
    2,
    20%
)
print(muscles.total_energy)
print(muscles.fat_oxidation_energy_estimate)
print(formation.relative_saving)
~~~

The muscle model separates supplied aerobic and anaerobic power and allocates a supplied fraction of aerobic energy to fatty-acid oxidation. The flock model calculates the effect of an assumed follower saving and explicit leader count. Neither assumes every flock achieves a fixed energy reduction or that a particular heart-mass increase applies to all migrating ducks.

migration_speed(distance, duration) is dimension-checked. oxygen_pressure_ratio(partial_pressure, reference_pressure) compares pressures only; it does not infer haemoglobin saturation or altitude tolerance.

## Behaviour: imprinting and sleep

~~~sambu
let window = imprinting_window(14, 12, 16)
let vigilance = hemispheric_sleep_budget(20, 10%, 100%)
print(window.inside_configured_window)
print(vigilance.edge_bird_count_estimate)
~~~

Both functions are parameterized accounting models. They do not infer a universal sensitive period, prove a particular neural circuit, or determine how a real flock allocates vigilance. Use species-specific studies and observed conditions when assigning inputs.

## Comparative profile object

~~~python
from sambu.anatidae import AnatidaeProfile

profile = AnatidaeProfile(
    taxon="Anatidae / population under study",
    foraging_mode="dabbling",
    diving_mode="surface",
    evidence_refs=("field-study:2026-01",),
)
record = profile.to_record()
~~~

Missing values remain None; the profile status explicitly says parameterized_not_taxonomically_verified.

## Research references

- Schachner & Moore (2025), Structure and function of the avian respiratory system: https://pmc.ncbi.nlm.nih.gov/articles/PMC11864839/
- Schachner et al. (2025), Avian air sacs and neopulmo: their evolution, form and function: https://pmc.ncbi.nlm.nih.gov/articles/PMC11864834/
- Bennett & Hughes (2003), Comparison of renal and salt gland function in three species of wild ducks: https://pubmed.ncbi.nlm.nih.gov/12909708/

These references support comparative context, not every numeric value from the original brief.
