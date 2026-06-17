# P215 — TRIAGE RESULTS (real zero-API path: _decisions.json → triage_write.py)

ICE re-scored from scratch (I≥Medium AND C≥High AND traced path to advance). Buckets written to
`data/triage/{submit,poc_required,downgraded,rejected}.jsonl` + per-finding `<ID>.md`. No safety-net reroutes
(rejected candidate carried a disproof).

| ID | status | rec. sev | ICE (I/C/E) | reason (short) |
|----|--------|----------|-------------|----------------|
| ZETA-01 | poc_required | Medium | High/High/Conditional | withdraw raw-amount vs deposit-delta; needs FoT insolvency PoC |
| ZETA-02 | downgraded | Low | Low/Medium/Conditional | zetaFee accounting drift only; below advance bar |
| ZETA-03 | downgraded | Low | High/High/**Privileged** | TSS rotation no timelock — centralization; privileged |
| ZETA-04 | **submit** | Medium | Medium/High/Conditional | onReceive lacks whenNotPaused (source-proven) |
| ZETA-05 | poc_required | Medium | High/High/**Privileged** | no replay dedup; needs double-mint PoC |
| ZETA-06 | poc_required | Medium | Medium/Medium/Conditional | empty-bytes interactor bypass; needs PoC |
| ZETA-07 | downgraded | Low | Low/High/**Privileged** | zero gas fee only if GAS_LIMIT=0 (privileged misconfig) |
| ZETA-08 | downgraded | Low | High/High/**Privileged** | mutable mint authority; QA zero-guard; privileged |
| ZETA-09 | **rejected** | Low | Low/High/Permissionless | rogue connector = by-design; disproof recorded |
| ZETA-10 | poc_required | High | High/Medium/Permissionless | nonReentrant gap; realized theft UNCLEAR → needs harness |
| ZETA-11 | poc_required | Medium | Medium/Medium/Conditional | unvalidated getPools()[0]; needs PoC |
| ZETA-12 | **submit** | Medium | Medium/High/Permissionless | deadline=block.timestamp+200 weak MEV (source-proven) |

**Distribution:** submit 2 · poc_required 5 · downgraded 4 · rejected 1 · merged 0 · human_review_queue 0.

Observation for FUNNEL_EFFECTIVENESS: ICE correctly diverted the 4 privileged/centralization candidates (ZETA-03/05/08
and the GAS_LIMIT misconfig ZETA-07) away from submit, and held the permissionless High (ZETA-10) at poc_required
pending realized-impact proof.
