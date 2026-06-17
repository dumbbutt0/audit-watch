# P206 — Lightweight second positive-control corpus selection for L3 validation

## Context
P205 validated the **demotion** side of the P204 L3 realized-impact HIGH standard on a 2nd corpus (Vultisig) but
left the **positive High-preservation** side `HARNESS_INCONCLUSIVE` — blocked purely by Vultisig's solc-0.7.6 +
Uniswap-V3/periphery + OZ-3.4 dependency web (no locally-compatible deps), not by the standard. Before any
operationalization/wiring we still need **one clean second-corpus positive-control High harness**. P206 does **not**
assemble Vultisig's dep web; instead it **selects a lighter corpus** where a contract-level High can be harnessed
quickly and honestly, plus a Medium/false-High negative control. This is a **corpus-selection/screening phase only**.

## Strict scope (no execution beyond read-only screening + a tiny compile smoke test)
No L3 wiring; no changes to production prompts/checkers/routers/ledgers/detectors/dashboards; no patch to
`prompts/deep_trace.md`; no submit/route/promote/demote; no full PoCs (only a non-mutating compile smoke test for
viability); firewall discipline preserved (count-only orchestrator exposure; any title/summary classification via
**JSON-only** firewall subagents; discard+rerun on prose leakage).

## Reconnaissance already done (read-only, count-only, firewall-clean)
Sealed holdouts present: badger, centrifuge, decent, kleidi, munchables, pooltogether, predy, vultisig, zetachain.
Used in decisive validation set → `REJECT_ALREADY_USED`: decent (P202/P204), vultisig (P205), zetachain (P201),
centrifuge (P198), predy (P200). Count-only severities + deps for the remaining candidates:

| corpus | High | Med | solc | framework | deps (external) | vendored locally? | note |
|---|---|---|---|---|---|---|---|
| **munchables-2024-05** | **2** | **4** | **0.8.25** | foundry | OZ + OZ-upgradeable + forge-std; 1× `@api3` (only `rng/RNGProxyAPI3.sol`) | not in audit dir, but OZ 0.8.x/upgradeable/forge-std all available elsewhere in repo | modular (managers/proxy/overlords/…); LockManager/MigrationManager = likely contract-level High loci; **materially lighter than Vultisig** |
| pooltogether-2024-03 | 1 | 8 | 0.8.24 | foundry | `openzeppelin/` + `owner-manager-contracts/` | OZ 0.8.x available | very light (6 in-scope `.sol`) but only **1 High** → thin positive-control redundancy |
| badger-2024-06 | 0 | 2 | 0.8.x | foundry | — | — | `REJECT_TOO_THIN` (0 High) |
| kleidi-2024-10 | 0 | 3 | 0.8.x | foundry | — | — | `REJECT_TOO_THIN` (0 High) |

**Leading candidate: munchables-2024-05** (2H/4M, solc 0.8.25, standard OZ deps locally satisfiable, no V3 web, no
split-codebase, no off-chain dominance). **Fallback: pooltogether-2024-03** (lightest deps but only 1 High).
Munchables was only *screened* in PCS (never used for a decisive validation run) → eligible.

## Execution sequence (when approved)
Work dir: `documentation/research/assisted_mode/p206_lightweight_corpus_selection/`. All deliverables there.

1. **Integrity precheck** (`INTEGRITY_PRECHECK.md`): record START md5-first-8 for `prompts/deep_trace.md`
   (`ef93a6c2`), `scripts/validate_deep_pass_mechanisms.py` (`5d2a97f9`), `scripts/eval_locus_resolver.py`
   (`3b0b2c02`), hermes `ledger`; confirm no production files modified; confirm all candidate answer keys remain
   sealed before screening.
2. **Candidate inventory** (`CANDIDATE_INVENTORY.md`): the table above, expanded — corpus name · source path ·
   answer-key path · compiler · framework · approx source size · dependency burden · vendored? · smoke-testable? ·
   already-used-in (P186/P189/P198/P200/P201/P202/P204/P205).
3. **Controlled count-level screening** (`SCREENING_PROTOCOL.md` + tallies in `SCREENING_OUTPUTS.json`): severity
   counts only (already gathered for the viable set); no finding bodies. Keep orchestrator exposure count-only.
4. **Contract-level High viability screening** — **JSON-only firewall subagent(s)** classify each High of
   munchables (and pooltogether) into metadata only: contract-level vs off-chain · source-reachable? ·
   permissionless vs trusted-prereq · impact class (theft/permanent-loss/insolvency/privileged-control/DoS/auth-only/
   other) · harness complexity (low/med/high) · dependency blocker (none/minor/major) · positive-control suitability
   (yes/no/unsure). **No prose preamble, no verbatim titles, no loci** (loci only in a sealed screening artifact if
   strictly needed). Leakage → discard + rerun stricter. Persist structured rows into `SCREENING_OUTPUTS.json`.
   Orchestrator does **not** read munchables finding titles itself (PCS contamination lesson).
5. **Harness feasibility smoke check** (`HARNESS_FEASIBILITY.md`) — top candidate(s) only, non-mutating: confirm
   solc 0.8.25 compiles; set up a throwaway foundry project remapping `@openzeppelin`/`openzeppelin-contracts(-upgradeable)`/
   `forge-std` to local copies (e.g. `sentiment-v2`/`dyad` `lib/openzeppelin-contracts`, `plaza-finance`
   `lib/openzeppelin-contracts-upgradeable`, any `lib/forge-std`); attempt to compile the High-bearing manager
   contract(s) in isolation. **No exploit PoC built.** Record whether a minimal isolated harness can import the real
   contracts without large dep reconstruction. (Smoke-test artifacts isolated under the p206 dir.)
6. **Ranking** (`CORPUS_RANKING.md`): rank by positive-control High quality · negative-control availability · harness
   simplicity · source reachability · dependency readiness · architecture diversity · firewall cleanliness. Labels:
   `ACCEPT_FOR_P207` · `FALLBACK` · `REJECT_TOO_THIN` · `REJECT_DEPENDENCY_HEAVY` · `REJECT_OFFCHAIN_DOMINATED` ·
   `REJECT_ALREADY_USED` · `REJECT_FIREWALL_COMPROMISED`.
7. **Recommendation + metrics + integrity** (`P206_RECOMMENDATION.md`, `metrics.json`, `integrity_checks.md`):
   end-state hashes byte-identical to START; JSON valid; keys re-confirmed sealed (count-only access).
8. **Copy this plan to** `P206_PLAN.md`.

## Final decision (one of)
`ACCEPT_LIGHTWEIGHT_POSITIVE_CONTROL_CORPUS` · `FALLBACK_TO_VULTISIG_DEPENDENCY_ASSEMBLY` · `DATASET_TOO_THIN` ·
`FIREWALL_COMPROMISED` · `INVALID_RUN`. **Expected:** `ACCEPT_LIGHTWEIGHT_POSITIVE_CONTROL_CORPUS` → munchables-2024-05
(fallback pooltogether-2024-03), *contingent on* step-4 firewall screening confirming ≥1 contract-level,
source-reachable, permissionless, non-RNG/non-trusted High + a Medium/false-High negative-control candidate, and
step-5 confirming the manager contract compiles against local OZ deps.

## Acceptance criteria
Vultisig not primary unless no lighter corpus exists; selected corpus has ≥1 strong contract-level High for an
executable L3 harness + ≥1 Medium/false-High negative control; dependency burden materially lighter than Vultisig;
JSON-only firewall outputs for any title/summary exposure; no production files modified; production hashes
byte-identical START==END; JSON valid.

## Deliverables
`P206_PLAN.md` · `INTEGRITY_PRECHECK.md` · `CANDIDATE_INVENTORY.md` · `SCREENING_PROTOCOL.md` ·
`SCREENING_OUTPUTS.json` · `HARNESS_FEASIBILITY.md` · `CORPUS_RANKING.md` · `P206_RECOMMENDATION.md` ·
`metrics.json` · `integrity_checks.md`. Memory: `project_phase206_*` + one-line MEMORY.md pointer on completion.

## Verification
`metrics.json`/`SCREENING_OUTPUTS.json` parse as valid JSON; production hashes match START
(`ef93a6c2`/`5d2a97f9`/`3b0b2c02`) at END; every candidate answer key still sealed (count-only access logged);
smoke-test compile result recorded with the exact remapping used; firewall subagent outputs contain no prose/titles
(else marked discarded+rerun).

## Follow-on (NOT this phase)
P207 = full L3 second-corpus positive-control validation run on the accepted corpus (blind threat-ceiling →
post-freeze key map → build ≥1 positive-control High harness + ≥1 negative control → score). Only after a positive
High is harness-confirmed on a 2nd corpus → consider operationalizing the L3 HIGH bar. Deep-pass recall + oracle
track remain separate.
