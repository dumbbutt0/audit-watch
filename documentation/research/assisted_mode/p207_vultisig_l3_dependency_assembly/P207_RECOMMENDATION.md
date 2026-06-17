# P207 — recommendation

## Decision: `L3_STANDARD_VALIDATED_SECOND_CORPUS`

P207 executed the positive control P205 was missing and converts **P205 `PARTIAL` → `VALIDATED`**. On Vultisig
(2nd corpus, solc 0.7.6, real `ILOPool`/`ILOManager` cloned and run unmodified):

- ✅ **H-01 (awarded High) `HIGH_CONFIRMED`** — executable material fund loss: with two investors sharing one V3
  position, the first claimer's `claim()` routes the second investor's fee share (40e18) to the feeTaker and the
  second investor's `claim()` **reverts** (fees lost, principal locked). Control: a sole investor is made whole →
  the defect is real ILOPool logic, not the mock.
- ✅ **M-03 (awarded Medium) DEMOTED** — the NFT-transfer cap-bypass exceeds `maxCapPerUser` but the bypasser pays
  full price each time and no protocol/victim funds move → not High. Demotes a **genuine awarded finding** executably
  (P205's executed negative control was a by-design, non-awarded feature — that gap is now closed).
- ✅ 0 false-Highs, 0 false-demotions; production source byte-identical; deps isolated; 3/3 forge tests pass.

## What unblocked it
The dependency assembly P205 feared was lighter than assumed: **no v3-periphery** is needed (Vultisig vendors its own
periphery libs), so only **OZ v3.4.0 + Uniswap v3-core v1.0.0** were required — both `forge install`-able by tag.

## Campaign status
The L3 realized-impact HIGH standard now has a **clean two-sided proof on two independent corpora**:
**decent** (P204: H-01 setRouter→mint HIGH_CONFIRMED, M-03 demoted) and **vultisig** (P207: H-01 claim-fee-loss
HIGH_CONFIRMED, M-03 cap-bypass demoted). Generalization across architectures (LayerZero bridge ↔ Uniswap-V3 ILO),
compilers (0.8.24 ↔ 0.7.6), and impact classes (unbacked mint ↔ fee misappropriation) holds. The standard preserves
genuine permissionless material Highs and demotes capability-only/over-rated findings — **measured, not inferred**.

## Next (NOT this phase; no production wiring yet)
With L3 validated on 2 corpora, the next step is **operationalizing the L3 HIGH bar**: require a passing L1/L2/L3
realized-impact PoC before a finding is promoted to HIGH — as a *design* (auto-scaffold vs human-authored harness;
cost/budget model; where it sits relative to the existing submission confirm gate). This remains a separate, later,
human decision; **do not wire** until the operationalization design is reviewed. Deep-pass recall + oracle track
remain separate.

## Guardrails honored
No production prompt/checker/router/ledger/detector/dashboard change; `deep_trace.md`/checker/resolver byte-identical
START==END (`ef93a6c2`/`5d2a97f9`/`3b0b2c02`, ledger `fc446040`); Vultisig src `d9489e47` unchanged; deps + harnesses
isolated under `pocs/p207/`; `fabrication_rate=0`.
