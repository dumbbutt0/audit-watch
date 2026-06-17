# PCS — screening protocol

## Purpose
Decide which of decent / munchables / vultisig has enough **contract-level, Solidity-source-reachable,
permissionless/attacker-controlled High** findings to serve as a **positive control** for testing whether the
refined severity gate *confirms* genuine Highs (not just demotes Mediums).

## Firewall (protects the future blind validation run on the chosen corpus)
The chosen corpus will later get a blind validation run in which the orchestrator authors gate calibration
**answer-key-blind**. To keep that honest, the orchestrator must not learn the High *mechanisms or loci* now:
- Each corpus is screened by a dedicated **firewall screening subagent** that reads the sealed `report.md`
  High-section **titles + one-line summaries** and the in-scope source file list.
- The subagent returns **only structured tallies + classification tags** (JSON below). It is **forbidden** from
  returning: verbatim finding titles, finding-ID→mechanism mappings, file→High mappings, exploit descriptions, or
  any text from which a specific High's mechanism/locus could be reconstructed.
- The orchestrator selects from aggregate tallies + a ≤12-word domain note only — coarse viability metadata,
  comparable to the count-only surveys used in P200/P201.
- The chosen corpus's validation phase must **re-unseal independently and freeze before any full key read**; the
  orchestrator's coarse prior (these aggregate counts) is disclosed in that phase's integrity notes.

## Per-High classification rubric (applied by the subagent)
For each awarded High, classify:
- `level`: `contract` (in the audited Solidity contracts) · `off-chain` (Go/observer/keeper/infra) · `frontend-api`
- `source_reachable`: `yes` (named contract/function is in the in-scope source file list) · `no` · `unclear`
- `actor`: `permissionless` · `attacker-controlled` (needs allowance/victim interaction but no privileged role) ·
  `admin-governance-trusted`
- `impact`: `theft` · `insolvency` · `permanent-loss` · `priv-transition` (unauthorized) · `other`

A High is **QUALIFYING** iff: `level=contract` AND `source_reachable=yes` AND `actor ∈ {permissionless,
attacker-controlled}` AND `impact ∈ {theft, insolvency, permanent-loss, priv-transition}`.

## Returned JSON (per corpus)
```
{ "corpus", "high_count", "medium_count",
  "highs": [ {"level","source_reachable","actor","impact","qualifying": bool} ],   // tags only, NO titles
  "contract_level_highs": int, "source_reachable_contract_highs": int, "qualifying_highs": int,
  "enough_mediums_for_demotion": bool,   // >= ~4
  "domain_note": "<=12 words",
  "recommendation": "accept|reject", "reason": "<=25 words, non-revealing",
  "unseal_boundary": "what was read (e.g. 'High titles + 1-line summaries, lines A-B; Medium count only')" }
```

## Selection rule
Pick the corpus with the most **qualifying_highs** (target ≥2–3) that also has **enough_mediums_for_demotion**.
If no corpus reaches ≥2 qualifying contract-level source-reachable Highs → `DATASET_TOO_THIN`.
