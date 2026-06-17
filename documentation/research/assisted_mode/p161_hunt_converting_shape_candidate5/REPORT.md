# P161 — Option-A candidate #5 · hunt for the converting shape · strict pre-screen

**Phase:** P161 · **Candidate:** `H9-hybra-rewardsdistributor-claimmany-parity`
(audit `hybra-finance-2025-10-strict-eval`, arch `hybra` ve(3,3) Solidly fork — NEW) ·
**Decision:** `SOURCE_REFUTED_NO_HARNESS` · **Outcome:** `STATIC_FALSE_POSITIVE` ·
**Duplicate:** `duplicate_unknown` · research_only=true / routing_allowed=false / submission_ready=false.

**Purpose:** test whether *actively hunting* for the known converting shape (claim/claim_many recipient parity,
the B5/H2 family) outside the depleted shortlist beats the cheap filters. Result: hunting found the exact
shape, but the strict pre-screen still refuted it from source — because the *mechanism* that makes the shape a
bug (a recipient-correction layer omitted by one sibling) is architecturally absent in this fork.

---

## 1. Candidate selected
**hybra `RewardsDistributor.sol`** (`…/ve33/contracts/RewardsDistributor.sol`) — `claim(_tokenId)` vs
`claim_many(uint[])`, the direct analog of the converting blackhole **B5** / velodrome **H2** bug.

## 2. Why it matches the converting profile
- Single, light-dependency distributor contract with a **claim / claim_many sibling pair** (target shape #1).
- Direct payout path (`safeTransfer` / `deposit_for`), epoch reward accounting (`time_cursor_of`,
  `tokens_per_week`), veNFT recipient derivation (`ownerOf`) — exactly the area where B5's
  managed-owner-correction omission lived.
- Vendored Solidly fork (147 files) → the vulnerable contract can be isolated with small mocks if it passes.

## 3. Alternatives considered & rejected
| Alternative | Reject reason (refs) |
|---|---|
| ramses-2024-10-fresh | **0 vendored `.sol`** — cannot source-evaluate or harness |
| hybra `Bribes.getReward` | `require(msg.sender == gaugeManager)` :271 (G1 fail) + pays `ownerOf` :270/:277 (G2 fail) |
| hybra `GaugeV2.getReward` | pays the caller's **own** earned rewards (G2 fail — own funds) |
| hybra `VoterV3` claim/vote | `require(isApprovedOrOwner(msg.sender,_tokenId))` :123/:163/:182 (G1 fail) |
| hybra `RewardHYBR.redeemFor(amount,type,recipient)` :113 | caller-chosen recipient but burns caller's **own** rHYBR :116-117 (G2 fail) + `redeem`/`redeemFor` share `_redeem` (G4 no divergence) |

## 4. 4-gate pre-screen (real source refs — RewardsDistributor.sol)
| Gate | Verdict | Evidence |
|---|---|---|
| 1 · permissionless entrypoint | **PASS** | `claim` :195 and `claim_many` :214 are `external`, no auth modifier |
| 2 · attacker-is-recipient | **FAIL** | payout is `safeTransfer(ownerOf(_tokenId), amount)` :204/:228 or `deposit_for(_tokenId, amount)` :207/:231 — value goes to the **veNFT owner** (fixed party), never to an arbitrary caller |
| 3 · non-time/non-keeper | **FAIL** | direct-transfer branch gated on `_locked.end < block.timestamp` :203/:227; rewards accrue per-WEEK epoch in the `_claim` loop :145-152 → time-primary |
| 4 · logic-omission/parity/comparand | **FAIL** | `claim` and `claim_many` are functionally identical; the sole accounting checkpoint `time_cursor_of[_tokenId]` is in the **shared** `_claim` :153 (neither sibling omits it); recipient logic byte-identical; **no managed-NFT / original-owner correction layer** exists (vs blackhole B5's AVM `getOriginalOwner`) — VotingEscrow has only `idToOwner` + delegation, no `deposit_managed`/managed-owner indirection → no comparand to diverge from |

## 5. Decision
**`SOURCE_REFUTED_NO_HARNESS`** — gates 2, 3, 4 fail. The converting mechanism is architecturally absent.

## 7. Reason no harness was built
The bug that makes claim/claim_many a finding (one sibling applies a recipient correction the other omits)
**cannot exist here**: there is no correction/indirection layer, and the shared `_claim` guarantees the
checkpoint is applied by both paths. Building a harness would only re-confirm the absence — identical
conclusion to velodrome **H2** (RUNTIME_REFUTED). Per the H6/P160 discipline, no harness is built.

## 8. Trainer lesson (sharpened)
The converting predictor for the claim/claim_many family is **not** "a batch sibling exists" — it is
**"a recipient-correction / indirection layer exists that one sibling applies and the economically-equivalent
sibling omits"** (managed NFT / original owner / escrow owner / delegate owner). Evidence across the campaign:

| Arch | claim/claim_many present? | correction layer present? | outcome |
|---|---|---|---|
| velodrome (H2) | yes | **no** | RUNTIME_REFUTED |
| **hybra (H9)** | yes | **no** | SOURCE_REFUTED (gate) |
| blackhole (B5) | yes | **yes** (AVM `getOriginalOwner`) | RUNTIME_CONFIRMED |

→ The hunt should screen for the **correction layer** first (grep `managed`/`original`/`getOriginalOwner`/
`deposit_managed`/escrow-owner indirection), then the sibling pair — not the reverse. P161 confirms that even
targeting the ideal arch yields a gate refutation when the indirection layer is absent, and it does so at zero
harness cost — the strict pre-screen continues to convert "harness then discover" into "named-gate source
rejection."

## Campaign funnel (H5 → H9)
5 candidates · 1 runtime_confirmed (H5) · 1 reportable_candidate (H5) · 4 static_false_positive
(H6 source-refuted, H7 source-refuted, H8 gate-refuted, H9 gate-refuted) · **0 submission_ready**.

**Boundaries:** no production/harness/prompt/detector/taxonomy/dashboard/routing/severity/submission/corpus/
SIDECAR/symlink change; runtime sidecar byte-identical (H9 not_run → no row); ledger append-only; all flags
research_only/routing_allowed/submission_ready = false.
