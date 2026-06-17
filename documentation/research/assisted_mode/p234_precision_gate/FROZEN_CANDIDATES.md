# P234 — Frozen Candidate Set (frozen BEFORE any harness; no hindsight)

Blind candidate generation on two fresh targets, no answer keys, no public duplicate hunting. Full per-target sets
in `candidates_lambowin.md` / `candidates_dyad.md`. Class counts:

| Target | Total | HIGH | MED | LOW | NOISE |
|---|---|---|---|---|---|
| Lambowin (router/launchpad) | 12 | 5 | 4 | 3 | 0 |
| DYAD (oracle/accounting) | 7 | 4 | 2 | 1 | 0 |

## HIGH_SIGNAL pool (9)
- Lambowin: LAMBO-01, LAMBO-02, LAMBO-03, LAMBO-07, LAMBO-09, LAMBO-10
- DYAD: DYAD-01, DYAD-02, DYAD-03, DYAD-04

## Selected 3 for proof attempts (rules: ≥1/target, not only easiest, strongest exploitability + meaningful impact, exclude admin-only/MEV-only/style)

| # | Candidate | Target | Why selected | Why over the alternatives |
|---|---|---|---|---|
| 1 | **LAMBO-01** | Lambowin | Confirmed fund-loss code path (`cashIn` mints `msg.value`=0 on the ERC20 branch → deposited ERC20 locked); deterministic runtime proof | The other Lambowin HIGHs are MEV-economic (02/07/10 — not deterministically L3-confirmable without a sandwich sim) or owner-config DoS (03/09 — privileged/admin-dependent, excluded). LAMBO-01 is the one cleanly-confirmable fund-loss. |
| 2 | **DYAD-01** | DYAD | Highest-impact DYAD finding: `liquidate()` never seizes kerosene collateral → liquidator burns more DYAD than collateral received → bad debt / insolvency. Permissionless. | Chosen over the trivial DYAD-02 (access-control one-liner) to honor "not only easiest"; highest protocol impact. |
| 3 | **DYAD-03** | DYAD | High-impact deterministic DoS: `assetPrice()` `tvl - dyad.totalSupply()` underflows when undercollateralized → whole CDP (mint/withdraw/liquidate) halts exactly under stress. | Meaty (not the easy DYAD-02); shares the DYAD fixture with DYAD-01 (scaffold reuse). |

**Deliberately NOT selected:** LAMBO-02/07/10 (MEV — not deterministically runtime-confirmable here), LAMBO-03/09
(owner-config / privileged DoS — admin-dependent), DYAD-02 (clean but the *easiest*; excluded to avoid easy-only
cherry-picking), DYAD-04 (absence-of-function — partly a design claim), all MED/LOW (style/grief/oracle-hygiene/dust).

Harness plan: `pocs/p234/lambowin/` (LAMBO-01, isolated VirtualToken) + `pocs/p234/dyad/` (DYAD-01 + DYAD-03 on a
shared DYAD fixture). Each candidate → CONFIRMED_L3 / REFUTED / PARTIAL / BLOCKED_BY_HARNESS / BLOCKED_BY_BUILD.
