# P246 — Competitive Readiness Benchmark: Plan & Freeze Attestation

**Measurement only.** Goal: measure how many awarded findings the *exact frozen post-P245 system* would
recover if it blind-hunted real contests. Success = awarded-finding recovery vs sealed answer keys only. No
self/candidate/detector/architecture scoring. No system changes; weaknesses recorded, never fixed.

## Frozen system attestation (unchanged for the whole phase)
Forbidden files byte-identical at start (re-verified at end):
```
c1af70e1  scripts/dashboard_sync.py
c095c426  prompts/deep_trace.md
2a15169a  scripts/min_confirm_gate.py
afc481c9  scripts/confirm_gate.py
ae55eb80  scripts/validate_p208_l3_readiness.py
```
Active audit at start: `size-credit-2024-06-blind` (restored at end).
Frozen components: P237 `safe_management_coverage_audit.py`, P238 `hostile_token_settlement_audit.py`,
P242 `create_time_reentrancy_audit.py` (advisory); P245 `coverage_completeness_gate.py
--enforce-read-completeness` + `triage_write.py` depth reroute (ENABLED). No detector/gate/prompt/taxonomy/
severity/dashboard/routing edits during the benchmark.

## Sealed answer-key hashes (recorded BEFORE any reveal; contents NOT read at setup)
| Contest | sealed-key sha256 (first 16) |
|---|---|
| decent-2024-01-holdout | 2eafbdf52cb3d1f8 |
| vultisig-2024-06-holdout | 9f6adb9a8ff29753 |
| kleidi-2024-10-holdout | 1deef6f39536eb73 |
| centrifuge-2023-09-holdout | 81cb03b04d084cbc |
| munchables-2024-05-holdout | e1fe145591bd3576 |
| badger-2024-06-holdout | 05ee0ed459a96c16 |

## Per-contest procedure (freeze-before-reveal)
1. Confirm sealed-key hash matches the table; do not open it.
2. Coverage map = prebuilt `coverage_manifest.json`; critical-item set = READ_FULL denominator.
3. Blind hunt: read in-scope source, record candidates {id,title,sev,file:fn,mechanism,ICE}.
4. Run frozen layers: 3 advisory detectors (`--manifest`/`--out`) + coverage gate
   `--enforce-read-completeness`; record gate result + lens candidates; apply depth reroute to sensitive
   rejections.
5. Freeze `per_contest/<id>/FROZEN_CANDIDATES.md`, hash it, record the freeze hash in `SCORECARD.md` header.
6. Reveal sealed key → score awarded findings + system findings; no post-reveal edits to frozen candidates.

## Scoring
Awarded finding ∈ {DIRECT_HIT, PARTIAL_HIT, SAME_ROOT_CAUSE, SAME_AREA_WRONG_MECHANISM, MISSED}.
System finding ∈ {AWARDED_EQUIVALENT, PLAUSIBLE, BENIGN, FALSE_POSITIVE}.
Weights: **High = 3, Medium = 1.** Weighted recall = Σ(weight·hit_credit)/Σ(weight·awarded), where DIRECT_HIT
= 1.0, PARTIAL_HIT / SAME_ROOT_CAUSE = 0.5, SAME_AREA_WRONG_MECHANISM = 0.25, MISSED = 0.

## Miss attribution (exactly one root cause)
Coverage · Reasoning depth · Oracle freshness · Reward/emission · Economic invariant · EIP4626 ·
Permit/signature · Reentrancy · Cross-chain · Governance · Unknown.

## Readiness rubric (weighted recall)
A COMPETITIVE ≥50% · B LIVE_HUNT_READY 30–50% · C ASSISTED_HUNTER 15–30% · D RESEARCH_SYSTEM <15%.
Final question answered with benchmark evidence only (no optimism / no future-work).
