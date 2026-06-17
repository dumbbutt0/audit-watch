# P276 — CLASS_BREAKDOWN (locus-mapped 144 awarded H/M)

Class inferred from award title+root_cause via the FROZEN P273 keyword taxonomy (read-only).

| award class | total | surfaced | routed | mech-gen | surfaced% |
|---|---|---|---|---|---|
| ACCOUNTING_LIQUIDATION_BAD_DEBT | 44 | 35 | 22 | 22 | 80% |
| UNKNOWN_OTHER | 36 | 20 | 8 | 8 | 56% |
| ACCESS_CONTROL_AUTHORIZATION | 29 | 19 | 12 | 12 | 66% |
| DOS_LIVENESS | 13 | 9 | 6 | 6 | 69% |
| ORDER_VALIDATION | 5 | 4 | 2 | 2 | 80% |
| SHARE_ROUNDING_PRECISION | 5 | 5 | 3 | 3 | 100% |
| ORACLE_PRICING | 4 | 0 | 0 | 0 | **0%** |
| STATE_MACHINE_LIFECYCLE | 3 | 2 | 1 | 1 | 67% |
| REWARDS_CLAIMS | 3 | 3 | 3 | 3 | 100% |
| EXTERNAL_INTEGRATION | 2 | 1 | 0 | 0 | **50%** |

## Reading
- **Strong classes:** accounting (80% surfaced, 22 routed), share-rounding (100%), rewards (100%) — the checkpoint-
  driven recall + P273 taxonomy cover these well.
- **Weak classes (repair targets):** **ORACLE_PRICING 0/4 surfaced** and **EXTERNAL_INTEGRATION 1/2** — thin
  checkpoint/template coverage (backlog R4). `UNKNOWN_OTHER` (36, 56% surfaced) is the taxonomy-classification residue:
  awards whose class the keyword taxonomy can't infer from title alone — many surface but don't route (8/36), pointing
  at the body-signal coverage gap (R1).
- **Routing drop** (surfaced→routed) is the largest leak across classes: 96 surfaced → 57 routed. This is the
  COVERAGE_CLASS_GAP (R1) — class signals derived from names/titles, not mechanism bodies.
