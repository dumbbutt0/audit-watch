# P145 — Decision

## Decision: **RUNTIME_CONFIRMED**

A Foundry test deploys the **real blackhole `RewardsDistributor`** and calls its real public entrypoints. For an
AVM-managed tokenId with an expired non-permanent lock and a nonzero claimable amount, `claim` pays the original
owner (`getOriginalOwner`, 0xBEEF, 1e18) while `claim_many` pays the AVM manager (`ownerOf`, 0xA814, 1e18) — a
clear wrong-recipient divergence between the sibling functions, with a non-AVM control showing no divergence. The
prompt-derived sibling-parity mechanism is confirmed at runtime.

### Rubric
- **RUNTIME_CONFIRMED** ✅: real `claim_many` executes the wrong-recipient behavior; clear divergence vs the real
  `claim` and the non-AVM control.
- Not RUNTIME_PARTIAL: full real-contract deployment was achieved (no wrapper needed).
- Not RUNTIME_KILLED: `claim_many` does not apply the AVM correction — source and runtime agree on the defect.
- Not RUNTIME_BLOCKED: deps resolved; the test compiles and runs.

## Final response

**What this phase tested** — pivoting the P143 runtime-PoC method to blackhole B5: does the real `claim_many`
misdirect an AVM-managed reward (`ownerOf`/AVM manager) vs the sibling `claim` (`getOriginalOwner`/original owner)?

**Harness** — real-contract Foundry PoC (`audits/blackhole-2025-05-eval/pocs/p145/`): real `RewardsDistributor` +
mock VE/AVM/ERC20; corrected reference = the protocol's own `claim`; + non-AVM control.

**Runtime result** — 4/4 pass; `claim`→original owner (1e18), `claim_many`→AVM manager (1e18 misdirected),
recipients diverge, non-AVM control matches.

**Prompt vs runtime status** — prompt_decision=finding / prompt_status=completed (unchanged) recorded **separately**
from runtime_status=runtime_confirmed (research-only sidecar, now B1+B5); prompt metrics untouched.

**Limitations** — mechanism proven, not severity/magnitude or AVM-manager redistribution; mock VE/AVM; amount
synthetic; corrected reference is the sibling `claim`.

**Safety** — no submission; not submission-ready; no production contract/detector/severity/gate change; known M-04
(duplicate); human + PoC review still mandatory; active audit unchanged.

**Tests / integrity** — `forge test` 4 passed; `RewardsDistributor.sol` byte-identical; no Python production code
touched (full pytest unaffected); `output/` symlink still quantamm-2024-12-eval.

**Decision** — RUNTIME_CONFIRMED.

**Next recommended phase (P146)** — the runtime-PoC method is now validated on **two architectures** (noya B1,
blackhole B5) across two bug classes (value-loop provenance, sibling recipient parity). Options: (a) add an
optional research-only **runtime panel** to the P142 scorecard (default `not_run`) reporting prompt-derived vs
runtime-confirmed side-by-side without blurring; or (b) take a **non-duplicate** corpus item to runtime PoC to
produce a genuinely novel runtime-confirmed advisory; or (c) human reachability/severity review of B5 (analogous
to P144) — confirming whether AVM-managed expired-lock claims occur and whether the AVM manager redistributes.
