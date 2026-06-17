# P206 — screening protocol

## Goal
Select a corpus lighter than Vultisig where P207 can build (1) a positive-control High harness proving executable
material theft/permanent-loss/insolvency/unauthorized-privileged-control, and (2) a negative-control Medium/false-High
harness showing no realized material impact.

## Firewall rules (carried from PCS lesson: screening subagents over-returned and contaminated the orchestrator)
1. Orchestrator reads **counts + source metadata only** (severities, file names, pragmas, import roots). It does NOT
   read finding bodies/titles of the eligible candidates.
2. Any title/summary-level classification is delegated to a **JSON-only firewall subagent**:
   - Output is a strict JSON array; **no prose preamble**, **no verbatim finding titles**, **no source loci**.
   - Per-High metadata fields only (see below).
   - If the subagent emits any prose/titles/loci → its output is **discarded** and rerun with stricter instruction;
     the discard is logged in `SCREENING_OUTPUTS.json` (`discarded_runs`).
3. Loci, if ever needed, go only into a separate sealed screening artifact — not into the orchestrator transcript.

## Step 3 — count-level screening (done)
From summary headers only: munchables 2H/4M; pooltogether 1H/8M; badger 0H/2M; kleidi 0H/3M.

## Step 4 — contract-level High viability (JSON-only firewall subagent)
For each awarded High of munchables (2) and pooltogether (1), classify into metadata ONLY:
`contract_level` (true/false) · `source_reachable` (true/false) · `permissionless` (permissionless/trusted_prereq/
unsure) · `impact_class` (theft/permanent_loss/insolvency/privileged_control/dos/auth_only/other) ·
`harness_complexity` (low/med/high) · `dependency_blocker` (none/minor/major) · `rng_or_oracle_path` (true/false) ·
`positive_control_suitable` (yes/no/unsure). Also a count of Medium/false-High **negative-control** candidates per
corpus (metadata only).

## Step 5 — harness feasibility smoke check (non-mutating)
Top candidate(s) only: throwaway foundry project under this dir; remap `@openzeppelin`/`openzeppelin-contracts`/
`openzeppelin-contracts-upgradeable`/`forge-std` to local copies; attempt `forge build` on the High-bearing
contract(s) in isolation (byte-identical copies). Record pass/fail + exact remapping. **No exploit PoC built.**

## Step 6 — ranking & labels
`ACCEPT_FOR_P207` · `FALLBACK` · `REJECT_TOO_THIN` · `REJECT_DEPENDENCY_HEAVY` · `REJECT_OFFCHAIN_DOMINATED` ·
`REJECT_ALREADY_USED` · `REJECT_FIREWALL_COMPROMISED`.
