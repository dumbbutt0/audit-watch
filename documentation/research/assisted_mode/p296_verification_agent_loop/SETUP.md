# P296 — SETUP

**Phase:** Verification-agent loop over the P295 PoC backlog. Research-only, advisory, production authority WITHHELD.
**Loop:** emit per-locus build-spec → a PoC is produced (agent-agnostic) under `pocs/p296/<audit>__<id>/` → the P294
executed-PoC verifier JUDGES it (sole confirmer; builder self-report untrusted).

## User refinements (applied)
1. Agent-agnostic — success = spec→PoC→verdict (not "must be subagents"). This phase used spawned subagents.
2. confirmed-FP=0 tied to VERIFIER-confirmed only; builder claims are advisory (`agent_claimed`).
3. Every PoC manifest must carry an `assertion_map` (each exploit test → assertion → bug it proves); a verifier-PASS
   without it = `confirmed_but_unmapped` (not a clean confirmation).
4. Pass bar: ≥3 attempted AND ≥1 new verifier confirmation, confirmed-FP=0.

## New files only (zero cascade)
`scripts/research/verification_agent_loop.py` (emit/judge) · `config/research_verification_agent_loop.json`
(tractable allowlist + per-locus mechanism hint + source paths + manifest schema w/ assertion_map) ·
`pocs/p296/<audit>__<id>/*` (subagent output: foundry harness + test + manifest + agent_report) ·
`tests/research/test_p296_verification_agent_loop.py` + this docs dir.

## Reused (byte-identical)
P294 `executed_poc_verifier.py` (the judge), forge 1.5.1, `pocs/p286/lib` (forge-std), forbidden 5.

## Reproduce
`python3 scripts/research/verification_agent_loop.py emit` then (build PoCs) then
`python3 scripts/research/verification_agent_loop.py judge`.
