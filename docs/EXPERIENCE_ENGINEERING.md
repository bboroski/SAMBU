# Experience engineering

SAMBU exposes `sambu.experience.ExperienceJournal` for measuring workflow friction without turning the language runtime into a tracking service.

- Recording is off by default and requires explicit local opt-in.
- The buffer is bounded, in-memory only, and cleared when consent is withdrawn.
- Events accept short machine codes and aggregate durations; identities and free-form notes are rejected.
- Summaries expose completion/failure rates, median duration, and recurring friction codes.
- Small samples are marked non-actionable; metrics are descriptive, not guarantees or user-quality scores.

```python
from sambu.experience import ExperienceJournal
journal = ExperienceJournal(opt_in=True, minimum_sample=5)
journal.record("compile", "failed", duration_ms=420, friction_code="missing_dependency")
print(journal.summary())
print(journal.next_actions())
```

The module does not persist, upload, fingerprint, or inspect source/device data.
