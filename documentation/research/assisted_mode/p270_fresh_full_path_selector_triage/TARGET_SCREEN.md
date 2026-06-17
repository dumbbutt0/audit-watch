# P270 — TARGET_SCREEN (content-safe; existence not content)

Fresh external scored contest, zero prior exposure. Findings-repo availability via `git ls-remote` (refs only,
`GIT_TERMINAL_PROMPT=0`, control = benddao-findings). No finding titles/bodies/report tables/severity/awards opened.

## Decision: **SELECT `code-423n4/2024-02-wise-lending`**
| criterion | status |
|---|---|
| EVM / Solidity | **yes** (solc 0.8.24, evm shanghai, OZ ^4.9.3, foundry) |
| answer key retrievable | **PUBLIC** — `2024-02-wise-lending-findings` (control benddao-findings confirms probe) |
| in this repo? | **NO** — cloned fresh, source-only, to `/tmp/p270_fresh/wise` |
| prior-phase exposure | **NONE** (no match in `documentation/research/assisted_mode/`) |
| used in P260–P269 scoring? | **NO** (P254–269 used loopfi/basin/bakerfi/plaza/concrete/notional/reserve/astaria/ethos/hybra/sentiment/benddao/monetrix/phi/karak) |
| accounting/state/asset-flow surface | **rich** — lending/borrow/withdraw shares, **liquidation** (WiseCore), **bad debt** (FeeManager), fee accrual, oracle hub, Pendle power-farm share/reward token, position NFTs |
| PoC feasibility | feasible but **heavy** (WiseLending 1596L + MainHelper 1209L + WiseSecurity 1123L + WiseCore 687L deeply interlinked) → exercises the P269 HEAVY/PARTIAL-runtime routing (the designed mitigation) |

In-scope (scope.txt, 75 .sol): WiseLending · WiseCore · MainHelper · WiseSecurity(+Helper) · WiseLowLevelHelper ·
FeeManager(+Helper) · WiseOracleHub/OracleHelper · WrapperHub/AaveHub(+Helper) · PositionNFTs · PoolManager ·
PendlePowerFarm{,Controller,Token,Math,Leverage} · declarations.

## Rejected / not chosen (recorded)
- In-repo / contaminated: all of §P266–P269's saturated set (phi P266-scored; karak P268-scored; dyad/wildcat/fenix/
  ramses P259; centrifuge/predy P129+P200; munchables/decent/kleidi/vultisig P239; traitforge/nextgen/dittoeth P242).
- Other clean externals considered (PUBLIC findings, zero exposure): **gondi** (2024-04, NFT lending — smaller, the
  fallback), **init-capital** (2024-01 invitational — fewer wardens → sparser awards), **krystal-defi** (2024-06).
- Non-EVM / unsuitable probes: chakra (Cairo), kakarot (zkEVM), thorchain (Go), superposition (Stylus), opus (Cairo).

## Confounds recorded (disclosed)
- **Training-confound:** wise-lending is 2024-02, pre-cutoff, public ⇒ awards may be in training. Accepted as in
  P263/P266/P268; selector + triage decisions are made BLIND, pre-reveal.
- **PoC-heaviness:** the protocol is large/interlinked → full deposit/borrow/liquidate harness is heavy; partial-
  runtime (isolating the awarded accounting invariant) is the planned route per P269. This is a feature of the test,
  not a defect (it genuinely stresses the heavy/partial routing).

## Pre-reveal forbidden (held)
No finding titles / issue bodies / report finding tables / severity tables / award summaries / award-bearing searches
before Phase 9. If award content leaks before freeze: mark contaminated, exclude, fall back to gondi.
