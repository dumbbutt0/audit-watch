# P296 — DESIGN

## The loop
`emit` → for each tractable backlog locus, write a build-spec (`pocs/p296/<id>/SPEC.md` + build_specs.json) carrying
the locus, the recorded mechanism hint (from the reveal/lens notes — mitigates cold-start), the source to read, the
L1/L2/L3 contract, the Tier-C rules, and the manifest schema (incl. `assertion_map`).
(build) → a PoC is produced by ANY means (this phase: spawned `general-purpose` subagents following the SPEC +
`runtime_poc_agent`/`poc_writer` guidance) writing only under its `pocs/p296/<id>/` dir.
`judge` → the P294 verifier runs over each dir = the REAL verdict; the builder's `agent_report.json` is recorded as
`agent_claimed` but NEVER trusted.

## Why this is safe to automate (the keystone)
Precision comes from executed PROOF, not from the builder. A confirmation requires the verifier's
`attacker_verified=True` (a real exploit-test forge PASS + L1+L2+L3) AND a manifest `assertion_map` tying the
assertion to the candidate. So a cold/wrong-mechanism builder simply refutes — cold-start costs RECALL, never
PRECISION. confirmed-FP=0 by construction.

## assertion_map (refinement #3)
A forge PASS alone may not prove the INTENDED bug (a test could pass on an incidental/tautological assert). Each
exploit test must declare in the manifest what it asserts and how that proves the awarded candidate's bug. A
verifier-PASS without an assertion_map is flagged `confirmed_but_unmapped` and is not counted as a clean confirmation
(and is treated as an FP risk).

## Negative control
The salty Pools.deposit refutation PoC is re-judged each run — it must stay not-confirmed (the FP oracle refuses a
non-bug). The synthetic anti-fabrication test proves a builder claiming "confirmed" on a FAILING exploit is overridden
by the verifier.
