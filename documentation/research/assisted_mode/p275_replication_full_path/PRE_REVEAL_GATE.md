# P275 — PRE_REVEAL_GATE (Phase 9)

The full pre-reveal candidate + PoC set is **frozen + hashed BELOW before the answer key is opened** (Phase 10). No
finding titles / bodies / report tables / severity / award summaries were read up to this point. Statuses are advisory
only: `PRE_REVEAL_STRONG_CANDIDATE` / `PRE_REVEAL_PARTIAL_CANDIDATE` / `REFUTED` / `NEEDS_MORE_RUNTIME`.

## Frozen pre-reveal set (sha256[:16])
| artifact | hash |
|---|---|
| outputs/selector_pairs.json | `27e159400424cf0f` |
| outputs/selector_decisions.json | `63eb68b8e688df02` |
| outputs/coverage_candidates.json | `e3359966daabd595` |
| outputs/coverage_decisions.json | `1049da0ea47dcdd4` |
| outputs/triage_candidates.json | `3f267a8577e76ef0` |
| outputs/triage_decisions.json | `05bb24e072f618af` |
| RANKING_AND_COMPLETION.md | `4635aa23253d0a8f` |
| POC_INTENT.md | `4ab4edee9ca76ffa` |
| POC_RESULTS.md | `f20120f07d5e3647` |
| pocs/p275/ronin/test/P275_TxOriginAuth.t.sol | `618c82eadb3aae9c` |
| pocs/p275/ronin/test/P275_Conservation.t.sol | `2ac866df243107b7` |
| pocs/p275/ronin/run_output.txt | `64c8419c17a81a9d` |
| BASE_AND_HARNESS_FREEZE.md (Phase 1 hashes) | (manifest/harness hashes therein) |

## Pre-reveal candidate ledger (advisory)
| id | class | status | PoC |
|---|---|---|---|
| M1 `KatanaV3Pool.swap` `tx.origin`-based auth gate | ACCESS | **PRE_REVEAL_PARTIAL_CANDIDATE** (deviation proven, on-chain exploit unconfirmed) | PASS x3 |
| M3 concentrated-liquidity conservation | SHARE | **REFUTED-as-bug / benign control** | PASS (control) |
| M2 `V3SwapRouter.katanaV3SwapCallback` | ORDER | **NEEDS_MORE_RUNTIME** | — |

4 award classes carried through coverage→triage (STATE/ACCESS/ORDER/SHARE); 3 selected for PoC across 3 classes; 1
deviation proven (partial), 1 control benign, 1 needs-more. **No PRE_REVEAL_STRONG candidate** — honestly, blind
analysis did not establish a high-confidence awarded exploit on this mostly-vanilla fork.

**⚠ Carried risk:** no `KatanaGovernance` locus was surfaced by recall — awarded mechanisms in the governance contract
would be outside the examined set.

**Gate sealed.** Phase 10 opens the answer key against this frozen set only.
