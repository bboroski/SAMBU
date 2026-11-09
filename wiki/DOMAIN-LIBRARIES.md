# Domain libraries

SAMBU contains deterministic calculators and bounded models for several application areas. The presence of a model does not imply a live connection to the external service, device or institution named in a scenario.

## Percentage arithmetic

The percentage layer provides an attached postfix literal:

```sambu
let rate = 15%
let price = 240
let savings = percent_of(price, 15)
let final_price = price - savings

print(rate)       # 0.15
print(final_price) # 204
```

The postfix literal converts percentage points to a ratio. The spaced infix operator `10 % 3` is modulo. Helpers include `percent_of`, `apply_percent`, `reduce_by_percent`, `percentage`, `percent_change`, `percent_to_ratio`, `ratio_to_percent`, `percentage_points` and `clamp_percent`.

Inputs are checked for finiteness and dimensional validity. A zero-to-nonzero percentage change is undefined and raises an error.

## Anatidae comparative models

The Anatidae module contains configurable models inspired by waterfowl biology, including:
- counter-current heat exchange;
- feather-barrier and insulation indices;
- visual and sensory profiles;
- idealized avian air-sac cycles;
- gas-exchange proxies;
- bill-lamella filtration;
- salt-balance rates;
- flight-energy accounting;
- flock-flight budget estimates;
- migration-speed calculations;
- imprinting-window and sleep-budget models.

These are parameterized teaching and comparison models, not veterinary diagnostics or a species-specific physiology database. They must not be interpreted as universal properties of all ducks or geese. Species-specific coefficients require suitable evidence.

## Strategy, network and community models

The domain library also includes deterministic models for:
- directed networks, network metrics and bounded influence propagation;
- bargaining-range overlap;
- proportional resource allocation;
- funnels and channel metrics;
- simple A/B test screening calculations;
- recurring weekly schedules and capacity;
- package pricing and unit economics;
- one-step territory or node capture mechanics;
- production-brief metadata.

These functions calculate values from supplied inputs. They do not contact customers, accept payments, schedule real calendar events, render audio or implement a complete real-time game.

## Commerce planning

The queue and checkout models provide planning primitives:
- queue capacity estimates;
- bounded exponential retry schedules;
- idempotency-key construction;
- explicit order-pipeline invariant checklists.

A passing pipeline checklist means declared assumptions satisfy the model; it does not prove that an external system implements them. A durable outbox, database uniqueness, inventory reservation, payment semantics and authoritative order state remain responsibilities of the host integration.

## Workflow and record models

The workflow layer includes:
- previewed gift-transfer calculations;
- accreditation records with explicit dates and evidence fields;
- evidence-linked associations and signal reports;
- transparent proposal scoring;
- bounded batch plans;
- syntax inspection without execution;
- structural text and pattern analysis.

The module does not send money or gifts, issue recognized credentials, make factual accusations, execute external jobs or access external systems.

## How to use this library responsibly

1. Identify the model's declared inputs and units.
2. Read the assumptions and numerical limitations.
3. Supply evidence-backed parameters where the domain requires them.
4. Keep model output separate from real-world authorization or execution.
5. Validate the result independently when it informs a high-impact decision.

## Related pages

- [Scientific computing](SCIENTIFIC-COMPUTING.md)
- [Frameworks](FRAMEWORKS.md)
- [Trust and evidence](TRUST-AND-EVIDENCE.md)
- [Workflows and chunking](WORKFLOWS-AND-CHUNKING.md)
