# P147 — Runtime Result

| field | value |
|---|---|
| harness_type | **real_contract** (real `UserEscrow` deployed; real `transferIn`/`transferOut` called) |
| tests | 4 passed / 0 failed / 0 skipped |
| entitled subject | `destination` 0xDDDD (`destinations[token][destination]`) |
| paid subject (vulnerable) | `receiver` 0xBEEF (1000e18) — destination got 0 |
| corrected reference | `receiver == destination` → **reverts** (no redirect) |
| control | `receiver == destination` → pays destination; no divergence |
| repeat | receiver gets 2000e18 (allowance never reduced) |
| runtime_status | **runtime_confirmed** |
| runtime_confidence | high |
| duplicate_status | **duplicate_unknown** (holdout; no local answer key) |

## What this proves
The real `UserEscrow.transferOut` redirects funds escrowed for `destination` to an unrelated `receiver` whose only
link is a stale/unrelated infinite ERC20 allowance — a validated-subject ≠ paid-subject recipient-provenance
divergence — and the escrow never reduces that allowance, enabling repeated redirects. The corrected reference and
non-redirect control isolate the cause. This is the first runtime-confirmed panel row that is **not**
`duplicate_known`.

## What it does NOT prove (kept honest)
- **Severity / validity** — the NatSpec frames the `receiver != destination` path as "additional protection," so
  this is **intent-dependent**; whether the weak `allowance == max` proxy is a vulnerability or intended
  flexibility is a **human decision** (`requires_human_review`, `requires_poc_review`).
- **Novelty** — `duplicate_status=duplicate_unknown` only (no local answer key); no claim of novel/awarded.
- Not submission-ready.
