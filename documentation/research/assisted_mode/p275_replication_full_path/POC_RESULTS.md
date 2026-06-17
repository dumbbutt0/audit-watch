# P275 — POC_RESULTS (Phase 8)

Isolated foundry project `pocs/p275/ronin/` (forge-std only; Tier-C faithful reproductions — the real
KatanaV3Pool/KatanaGovernance need factory/beacon/governance/permit2 (via-IR) wiring disproportionate to proving these
specific guards). `forge test`: **4 passed, 0 failed**. Run log: `pocs/p275/ronin/run_output.txt`.

| PoC | mech / class | tier | result | proves |
|---|---|---|---|---|
| `test_enforced_when_txorigin_nonzero_and_caller_not_router` | M1 / ACCESS | C | **PASS** | reverts `IR` — router restriction enforced in normal txs (tx.origin≠0) |
| `test_passes_when_caller_is_router` | M1 / ACCESS | C | **PASS** | router caller passes |
| `test_skipped_when_txorigin_zero` | M1 / ACCESS | C | **PASS** | with `tx.origin==0` a non-router caller passes — the `tx.origin`-based auth **deviation** is real |
| `test_roundtrip_conserves_no_value_creation` | M3 / SHARE | C (control) | **PASS** | Uni-V3-style mint(round-up)/burn(round-down) conserves → pool math is **not** the bug |

## Reading (pre-reveal, no answer key)
- **M1 (tx.origin auth):** the deviation is **real and reproduced** — authorization on `swap` is gated by `tx.origin`,
  and the router restriction is skipped when `tx.origin == 0`. **But on-chain exploitability is unconfirmed**: a
  state-changing transaction always has `tx.origin != 0`, so the router restriction holds for real attackers; the
  bypass only manifests under simulation (`eth_call`), which does not persist state. I found **no** on-chain path to
  `tx.origin == 0`. → **PRE_REVEAL_PARTIAL_CANDIDATE** (deviation proven, exploit unproven).
- **M3 (conservation):** control holds — pool math matches canonical Uniswap V3; not the bug.
- **M2 (swap_callback):** NEEDS_MORE_RUNTIME (no exact hypothesis; callback validation matches canonical Uniswap).

## Honest limitations
- Tier-C reproductions prove the **logic of the guards I identified**, not a real-deployment exploit. No real
  KatanaV3Pool/KatanaGovernance was deployed.
- The leading risk (BASE freeze ⚠): the recall harness surfaced **no `KatanaGovernance` locus**, so any awarded
  mechanism living in the governance/authorization contract proper would be **outside the examined set** — a recall
  gap that the reveal will test.

## Pre-reveal candidate strength (advisory, no severity)
| mech | class | strength |
|---|---|---|
| M1 pool.swap tx.origin auth | ACCESS | **PARTIAL** (deviation proven, exploit unconfirmed) |
| M3 conservation | SHARE | BENIGN (control holds) |
| M2 swap_callback | ORDER | NONE (NEEDS_MORE_RUNTIME) |

Next: Phase 9 — freeze + hash the full pre-reveal set.
