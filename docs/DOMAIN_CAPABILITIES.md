# Domain Capabilities: terminology converted into software

This document maps the supplied Reaper/Mass Effect and academic biology vocabulary
to implemented, reviewable SAMBU functions. The terms are design inspiration; they
are not executable instructions and do not establish real-world physics or biology.

## Available APIs

| Term families | Implemented capability | Public API |
|---|---|---|
| Genetic archive, cellular transformation, genome restructuring | Evidence-bearing data promotion gate | `evaluate_evolution_gate` |
| Mass-effect field, gravimetric anomaly, thermal envelope | Unit-aware measurement classification | `assess_metric` |
| Kinetic barrier, hull integrity, sensor integrity | Configured operating-envelope check; read-only | `assess_metric` |
| Harvest cycle, core reconstruction, hibernation/recovery | Explicit lifecycle state machine | `advance_cycle` |
| Geth consensus, collective consciousness, networked intelligence | Unique-node quorum decision helper | `decide_consensus` |
| Genetic drift, mutation, evolutionary guidance | Evidence-gated model/configuration promotion | `evaluate_evolution_gate` |

## Running the capability tests

```sh
python -m unittest tests.test_reaper_domain
```

## Engineering boundaries

- Units and limits must come from the actual instrument, protocol, or system profile.
- Missing calibration or insufficient samples produce an incomplete result, never a healthy result.
- Consensus counts at most one vote per node and does not provide transport, identity, or cryptographic authentication.
- Lifecycle transitions are explicit; invalid transitions are rejected.
- Evolution promotion requires all declared evidence and a ready rollback path.
- No function actuates hardware, modifies organisms, controls weapons, or claims consciousness.

The catalogue in `data/reaper/engineering_patterns_50.tsv` remains a curated subset,
not a complete transcription of every supplied lore term.
