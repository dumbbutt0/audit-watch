# P280 — SETUP (small diagnostic PoC sweep on the 3 P279 READY candidates)

SUPERVISED_EVAL / POC_SWEEP / RESEARCH_ONLY. Question: are auto-derived READY candidates runnable AND useful? NOT a
broad campaign; NOT production authority. No candidate becomes reportable/confirmed/submission-ready/severity.

## Scope: exactly the 3 P279 READY candidates (frozen; no additions/widening/deriver tuning)
1. IBeanstalk.cancelPodListing (beanstalk-2024-05-eval2) — ORDER
2. L2Governor.execute (blackhole-2025-05-eval) — ACCESS
3. V3Vault.transform (revert-lend-2024-03-strict-eval) — ACCESS

## Allowed: pocs/p280/ + this doc dir + tests/research/test_p280_ready_poc_sweep.py.
## Byte-identical (verified): P260/P262/P264/P267/P269/P271/P273 router code 6debb753+config 91f9deac/P277 + P279
deriver (completion_evidence_deriver.py) + poc_readiness_evidence_gate.py + P278 glue + forbidden 5. Active audit
symlink -> audits/size-credit-2024-06-blind/output. PoCs are Tier-C faithful reproductions (forge-std only); no contest
source mutated.
