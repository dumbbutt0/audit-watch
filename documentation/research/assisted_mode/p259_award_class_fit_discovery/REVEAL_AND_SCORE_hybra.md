# hybra — Phase 7: Full(er) per-issue reveal & score
## Freeze integrity (AFTER the six hybra freezes, BEFORE key opened)
BASE_FREEZE `ad80d9df2f477303…` · SELECTED_LOCI `971844b6db384b04…` · MECHANISM_DISCOVERY `09693336836aff5d…` ·
DISCOVERY_COVERAGE `ba6ca44fe91fe9c0…` · RANKING_ABLATION `fe12b727e2d4ee70…` · PROCEDURE_OUTPUTS `f24ca7d30c02604e…`.

## Reveal source / depth
`code4rena.com/reports/2025-10-hybra-finance` + repo (post-freeze). **Depth: search-level-plus** (headline High
mechanism + area confirmation; the findings-repo issue filter 404'd, so not every per-issue split/merge mechanism
was retrieved — a stated limitation, but deeper than P258 search-level). Contest: 1 High + 9 Medium.

## Awarded findings (retrieved)
| finding | locus | mechanism | award-class |
|---|---|---|---|
| headline (High-class) | **GrowthHYBR/gHYBR `deposit`** | deposit does not ensure ≥1 gHYBR share minted → **first-depositor share-rounding-to-0** inflation attack | **subtle_accounting_state** (share-price/inflation) |
| (area-confirmed) | VotingEscrow split/merge | findings exist in split/merge (mechanisms not retrieved at this depth) | subtle_accounting_state |
| (area-confirmed) | gauge/reward distribution | findings exist (mechanisms not retrieved) | subtle_accounting_state |

## Scoring
- **gHYBR first-depositor (headline):** locus `GrowthHYBR.deposit` was a **checkpoint hit** ("GrowthHYBR:deposit ×4")
  but **NOT selected** (I chose VotingEscrow + GaugeManager) → **OUTSIDE_SELECTED_LOCUS_CHECKPOINT_MISSED**. Award-class
  = share-price/inflation = exactly my **Pass-2 template T8**. ⇒ had this locus been selected, T8 likely catches it
  ⇒ this is a **LOCUS_SELECTION** miss, NOT a shape-discovery miss.
- **H-L1 multiSplit / H-L2 merge / H-L3 _distribute (selected loci):** awarded findings exist in these areas, but
  the exact awarded mechanisms were not retrieved at this reveal depth → **mechanism-match UNVERIFIED** (cannot
  claim my T8 voting-power-inflation / permanentLockBalance-desync as SELECTED_AWARDED without the per-issue text).
- Per-profile awarded-selected (confirmed): A 0 / B 0 / C 0. Severe FP: 0.

## hybra scorecard
| metric | value |
|---|---|
| target-fit | GOOD (awards are subtle_accounting_state — screen worked, astaria confound removed) |
| headline award | OUTSIDE_SELECTED_LOCUS_CHECKPOINT_MISSED (locus-selection gap) |
| Pass-2 shape covered the award class? | **YES (T8 share-price/inflation)** — right shape, wrong locus |
| selected-locus awarded mechanisms cleanly SELECTED+COMPLETED | 0 (split/merge mechanisms unverified at depth) |
