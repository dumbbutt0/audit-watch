# P259 — TARGET_FIT_SCREEN (content-safe; no award content fetched)

Award-class-fit screen: classify candidates by **likely award class** from architecture only, to avoid P258's
astaria failure (mechanical/access-control awards). SELECT subtle-accounting-fit; REJECT wrong-class/contaminated.

| candidate | architecture | reveal exists (content-safe) | likely subtle-accounting awards? | likely mechanical/access-control-dominated? | prior exposure | decision |
|---|---|---|---|---|---|---|
| **hybra-finance-2025-10** | C4 ve(3,3)+CL AMM (VotingEscrow split/merge, GaugeManager reward distribution, CLPool, GrowthHYBR) | YES (`code-423n4/2025-10-hybra-finance` README scope) | **YES** (ve-accounting, reward/gauge distribution, CL invariant, split/merge value conservation) | low | p161 examined ONE locus (`RewardsDistributor.claimMany` parity) | **SELECT** (exclude claimMany) |
| **sentiment-v2-2024-08** | Sherlock lending (Pool, SuperPool queues, PositionManager liquidation, RiskEngine, bad-debt) | YES (`sherlock-audit/2024-08-sentiment-v2`) | **YES (strong)** (share/debt/interest, liquidation, bad-debt socialization, queue accounting) | low | **#541 leaked in P257** (interest-distribution via asset-transfer+fee-accrual) + p242 Family-A/B + p239 listing | **CONTAMINATED → included disclosed**, #541 area + max*/preview* HARD-EXCLUDED |
| olas-2024-05 | service/agent registries, bonding | n/a | NO (registry/governance/tokenomics) | **yes** (access-control/registry) | p196/p212 | REJECT (wrong class) |
| recall-2025-02 | subnet/diamond/multisig (IPC) | n/a | partial | yes (governance/diamond) | p197/p206/p212 | REJECT (wrong class + contaminated) |
| maia-talos / velodrome / panoptic / renzo / tokemak / beanstalk / k2 | (various subtle) | — | — | — | **answer-key/heavy-use phases** (p168–199/p171) | REJECT (award-revealed) |
| dyad / wildcat / fenix / ramses | (various subtle) | — | — | — | contaminated (p234/p239/p241/p105–161) | REJECT |
| P253–P258 contests; reNFT/PoolTogether/Salty/Spectra; P246 | — | — | — | — | used / barred / revealed | REJECT |

## Corpus-exhaustion note
Only **hybra** is a clean award-class-fit SELECT; **sentiment** is the only other subtle-fit option and is
contaminated (disclosed). The clean held-out subtle corpus is **depleted** — a first-class build-direction input.

## Resolved (operator-approved): hybra (SELECT) + sentiment-v2 (disclosed-contaminated, #541 + max*/preview* excluded).
