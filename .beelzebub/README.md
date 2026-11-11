# Beelzebub — repository security baseline

**Protocol:** Beelzebub / Sambo Defensive Control v1  
**Mode:** read-only scan + CI gate  
**Data policy:** no source upload to an external analysis service; findings report rule IDs and locations, never matched secret values.

## Purpose

Beelzebub gives this repository a repeatable first line of defense. It is intentionally a small, portable baseline that runs with Python 3's standard library and does not alter source files. It is not an endpoint antivirus product and does not claim to detect every malware family.

## Sambo defensive model

The Sambo metaphor is translated into safe engineering controls:

1. **Stance and balance — secure defaults.** CI permissions are read-only, the checkout action is pinned to a commit, and the scanner does not execute project code.
2. **Kuzushi — remove an attacker's leverage.** High-confidence credential exposures fail the gate; suspicious code patterns are surfaced for review rather than treated as proof of malware.
3. **Grip and control — least privilege.** The workflow receives only contents: read; checkout credentials are not persisted.
4. **Immobilization — contain, do not destroy.** A confirmed credential finding blocks this security job. Beelzebub does not delete files, rewrite commits, disable accounts, or automatically roll back branches.
5. **Escape and recovery — restore safely.** Revoke and rotate leaked credentials, remove them from the working tree and history using a reviewed procedure, then rebuild from a trusted commit.
6. **Randori — repeated practice.** The workflow self-tests the detection rules on every run and scans on pushes, pull requests, manual dispatch, and a weekly schedule.

## What is active

- High-confidence pattern checks for common GitHub, AWS, Google API, Slack credentials and private-key headers.
- A conservative generic credential-assignment heuristic.
- Non-blocking review signals for dynamic execution (eval/exec), shell=True, Python pickle deserialization, and yaml.load.
- A warning for a workflow combining pull_request_target with permissions: write-all.
- A CI gate that fails for credential findings and leaves ambiguous findings to maintainers.
- A weekly scan plus commit/PR checks.

## Local use

~~~bash
python3 .beelzebub/scan.py --self-test
python3 .beelzebub/scan.py --root .
~~~

Exit codes: 0 means no high-confidence credential match; 1 means a credential finding needs remediation; 2 means the scan could not start. Advisories are non-blocking and require context-aware human review.

## Incident response

1. Treat a detected credential as compromised. Revoke it at its issuer and create a replacement.
2. Remove the secret from the current tree and rotate any dependent credentials.
3. If it was committed, arrange a reviewed history cleanup; deleting the current file alone does not erase Git history or invalidate the credential.
4. Review recent commits, workflow permissions, package changes and release artifacts.
5. Re-run the scanner and the repository's normal tests. Record the resolution without copying secret values into issues or logs.

## Current limits — important

This v1 baseline is **not** the complete manifesto architecture:

- It scans the checked-out working tree, not every historical Git blob.
- It is a text-pattern and static-heuristic scanner, not a malware-signature engine, binary disassembler, dynamic sandbox, or host/endpoint antivirus.
- It does not yet build a full dependency graph or query a live CVE database. Enable GitHub Dependabot alerts and dependency review for package-specific vulnerability intelligence.
- It does not perform P2P gossip, distributed quorum, global threat memory, federated learning, IDE integration, runtime syscall monitoring, or automatic patching.
- A clean result is not a proof that a repository is secure. Keep code review, tests, secret scanning, dependency alerts, signed releases and least-privilege repository settings enabled.

The next safe expansion is dependency-aware scanning and signed threat-intelligence exchange with explicit schema, provenance, expiry and human appeal. No remote source-code collection or automatic destructive remediation is part of this baseline.
