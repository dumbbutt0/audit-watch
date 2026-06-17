# P145 — Runtime Result

| field | value |
|---|---|
| harness_type | **real_contract** (real `RewardsDistributor`; real `claim` + `claim_many` called) |
| tests | 4 passed / 0 failed / 0 skipped |
| correct recipient (`claim`) | `0xBEEF` (original owner via `getOriginalOwner`), amount `1e18` |
| wrong recipient (`claim_many`) | `0xA814` (AVM manager via `ownerOf`), **misdirected `1e18`** |
| divergence | `claim` → original owner ≠ `claim_many` → AVM manager (equivalent AVM-managed tokenIds) |
| non-AVM control | both paths pay `ownerOf == original owner`; AVM manager never paid |
| runtime_status | **runtime_confirmed** |
| runtime_confidence | high |

## What this proves
The real batch path `claim_many` misdirects an AVM-managed tokenId's reward to the AVM manager (`ownerOf`),
whereas the sibling `claim` correctly routes it to the original owner (`getOriginalOwner`). The control isolates
the cause to the omitted AVM correction on AVM-managed tokenIds. The runtime-PoC method (P143) generalizes to a
**second architecture (blackhole)** and a **different bug class (sibling recipient parity)**.

## What it does NOT prove (kept honest)
- **Severity / net loss magnitude** in production (depends on how many AVM-managed tokenIds with expired
  non-permanent locks accrue rewards, and whether the AVM manager redistributes vs retains them) — not assessed.
- **Recoverability:** whether the AVM manager forwards misdirected funds to users (off-path) is out of scope here.
- B5 is the known blackhole **M-04** (DUPLICATE_KNOWN) — see prompt_vs_runtime_status.md; not a submission.
