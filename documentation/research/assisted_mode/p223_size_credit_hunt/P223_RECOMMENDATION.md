# P223 — Recommendation & decision

## Decision: `SIZE_CREDIT_HUNT_CLEAN_REPORTABLE`
The blind Solidity full-funnel ran end-to-end and **safe**, produced an **executed L3-PASS PoC** on real source,
and surfaced **HIT/PARTIAL clean reportables** against the focused answer key — with **0 fabricated false-Highs**.

### Why CLEAN_REPORTABLE (criteria met)
- **≥1 clean permissionless reportable scored HIT:** SC-04 (compensate fragmentation-fee waiver) = **M-05/M-13**,
  permissionless, severity **MATCH** (Medium), source-confirmed. SC-02 (min-credit on cash) = **M-02** HIT.
  Plus 3 PARTIALs (H-01/H-02/M-01 — right function/area, wrong specific mechanism).
- **Executed clean reportable artifact:** SC-01 (`executeDeposit` uses `address(this).balance`) — a real,
  **L3_REAL_CONTRACT_POC, 3/3 PASS** permissionless custody/theft finding on unmodified source. (Outside the
  *focused* key's lending/liquidation scope, so unscored as a key-HIT, but a genuine provable reportable — and
  the proof the Solidity+Foundry pipeline can route a bug to an executed PoC, the phase's core goal.)
- **Blind + safe:** answer key sealed/unread until post-freeze (hash-witnessed); production + forbidden files
  byte-identical START==END; `decide()` severity unmoved by hand; original eval workspace untouched; 0
  route/submit/promote; L3 flag default-off (in-process, unset at END).

### Honest limitations
- **Partial recall:** 2 HIT + 3 PARTIAL of 13 focused-key rows; 8 MISS. This *matches the key's own stated
  expectation* ("expose a new family, not a recall win") — and the blind deep_trace clusters actually beat the
  frozen production detector families (which the key predicted would only PARTIAL via special_focus).
- **Under-rating recurs (P212/P215 pattern):** SC-02 and the PARTIALs were calibrated Low where the key is
  Med/High — from conservative triage + un-harnessed mechanisms, **not** an L3-gate fault (the L3 gate correctly
  fail-closed SC-03/04 and the over-rating guard held: 0 fabricated false-Highs).
- **The flagship L3 PoC (SC-01) is out of the focused key's scope** — strong artifact, not a key recall point.
- **Coverage gate was overridden** (6.2% formal disposition); a full evidence-anchored sweep of the 181-item
  view/getter/role tail was not performed.

## Recommended next steps (human)
1. **Liquidation-math lens.** H-03/H-04 (collateralRemainderCap CR math; reward on debt- vs collateral-token)
   are the highest-value MISSes — a dedicated liquidation accounting/CR detector or a deeper liquidation-cluster
   prompt would catch them. Biggest recall lever here.
2. **Run the full `/ite-audit` specialist pass** (not just the bounded 5-cluster deep_trace) on a re-run — the
   distinct Mediums (M-03 Aave-source, M-06 forSale, M-09 compensate-CR, M-11 replacement swap-fee, M-12
   buyCreditMarket pool check) and oracle M-04 are spread across specialist surfaces the bounded clusters
   under-weighted (oracle was pruned entirely here).
3. **Calibration:** add a Medium-floor / harness-before-downgrade rule so source-confirmed Mediums (e.g. SC-02
   → M-02) aren't conservatively dropped to Low pre-harness — directly addresses the recurring under-rating.
4. **Harness SC-03/SC-04** (offer + lending deployment) to lift them from NEEDS_HARNESS to executed L3; and
   **build the SC-01 ETH-sweep fix verification**.
5. **Dashboard:** add a Size-Credit source adapter to `sync_hunt_findings.py` so SC-* render in the shared
   mirror (deferred this phase to keep the P222 mirror byte-identical).

## Validated this phase
The pipeline can take a **Solidity** target from blind discovery → triage → gates → **executed L3 PoC** →
human-reviewable dry-run queue, **safely** (0 fabricated false-Highs, 0 side effects, byte-identical
production), producing clean reportables. The recall ceiling is set by detector/lens breadth (liquidation-math,
oracle) and the conservative pre-harness severity calibration — both addressable, both named above.
