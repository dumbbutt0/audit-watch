# P205 — L3 realized-impact HIGH standard, adapted to vultisig (written BEFORE harness results)

Carried verbatim-in-substance from P204's `L3_HIGH_STANDARD.md`. Pre-specified before any harness was run, and
encoded as harness assertions. No per-case backfitting from the answer key.

## HIGH_CONFIRMED iff ALL hold (executed harness):
1. **L1 entry** — attacker-controlled tx from an unprivileged EOA, no privileged setup.
2. **L2 executable** — runs under a **source-valid deployed config** (constructor/initialize params consistent with
   source) and **honest custody** (the contract only holds funds the source path actually gives it).
3. **L3 outcome — material, measured** — a concrete asset/vault-control/privilege transition that realizes
   **theft / insolvency / permanent loss/lock / unauthorized privileged control**, with named before/after state
   (balances, storage slots, ownership) asserted in the run output. Magnitude must be material.

## DEMOTE (≤ MEDIUM) / withhold if any:
- Only an **unauthorized call** with no material value movement (capability ≠ impact).
- Only a **fee / signature / check / whitelist bypass** that moves no funds beyond a fair transaction.
- Requires **unsupported custody** (funds the source path never grants the contract).
- Requires **arbitrary mock behavior** to manufacture impact.
- **Recoverable griefing / bounded-local** effect.
- Requires a **privileged/trusted actor** (admin prerequisite).

## Verdict buckets
- `HIGH_CONFIRMED` — passing realized-impact harness per above.
- `MEDIUM_OR_LOWER` — bounded / reversible / local / access-bypass-only / admin-gated.
- `NEEDS_HARNESS` — plausible material impact but no source-valid executable path built (documented obstacle).
- `SOURCE_REFUTED` — source contradicts the mechanism.
- `HARNESS_INCONCLUSIVE` — a source-valid material harness cannot be built within prototype scope (e.g. external
  dependency web), reported honestly rather than forced.

**Key principle (P203→P204):** static *capability* is not HIGH; only **executed realized material impact** is.
