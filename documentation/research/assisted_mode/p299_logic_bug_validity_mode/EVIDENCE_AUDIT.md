# P299 — EVIDENCE_AUDIT

## Logic confirmations (bug test PASS + corrected-control PASS + L3 + assertion_map; verbatim source)
- **LG-001 ReseedField.init** — bug test: the verbatim nested loop `for (uint j; j < accountPlots[i].plots.length;
  i++)` (ReseedField.sol:49) reverts/bricks migration for multi-plot accounts (migratedPlots < originalPlots).
  control: the corrected `j++` loop migrates all plots. Divergence = bricked vs complete migration. assertion_map ties
  it. → confirmed_by_logic_differential (no attacker — a migration logic bug).
- **PC-001 SeasonGettersFacet.totalDeltaB** — bug test: verbatim body `deltaB = LibWellMinting.check(C.BEAN_ETH_WELL)`
  returns one well; control: corrected getter sums all whitelisted wells. Divergence = reported (d1) vs true (d1+d2),
  asserted. → confirmed_by_logic_differential (a view-getter correctness bug).
- **SN-001 LibFlood.balanceOfPlenty** — bug test: trailing branch uses LIVE `s.accts[account].roots` over the
  `rain.roots` snapshot divisor → 2x over-payment; control: consistent snapshot → fair plenty. Divergence asserted.
  → confirmed_by_logic_differential.

## FP guards (proven in test_p299, synthetic)
- **no passing control** → setup_only (the differential is required; a bug value alone is not a confirmation).
- **failing bug test** → refuted_by_execution (logic mode can never rescue a failing bug test; the refuted branch runs
  before the logic branch).
- **no assertion_map** → setup_only (the divergence must be tied to the awarded bug).
So a logic confirmation cannot be obtained without a real, passing bug-vs-corrected-reference divergence + the map.

## Exploit track invariance (the additive change is field-gated)
All prior PoCs lack `validity_mode`, so they take the unchanged exploit path. Live re-verify: p286 / p294 / p287 /
p281 / p298-AC-001 / p298-AC-003 → confirmed_by_execution + attacker_verified=True (identical); p290 →
refuted_by_execution. exploit_track_unchanged.json all_unchanged=true.

## Integrity
confirmed-FP=0. verifier hash bumped a1280b2a→1a005811 (additive logic branch + validity_confirmed/logic_verified/
validity_mode fields; pins updated in test_p294-298, all hash-only since the exploit track is preserved). Forbidden 5
byte-identical; symlink unchanged; un-wired from confirm gates. P298 outputs/manifests/test NOT mutated (pre-logic-mode
snapshot preserved); the 3 logic loci re-judged via COPIES under pocs/p299/.
