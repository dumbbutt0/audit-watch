# Research — `sibling_function_parity`

**Status:** research-only (un-wired). Phase 0 of the detector lifecycle
(`documentation/architecture/research_methodology.md`). This document establishes *why* the full
20-subject eval selected this family, the grounded bug corpus, and the expected signal / FP sources —
**before** any detector code is written.

## 1. Why the eval selected this family

From `documentation/evals/full_20_subject_detector_family_eval/`:
- `miss_analysis.md` → **Theme 1**, sub-cluster "Validation / sibling-parity completeness" is the
  single most-repeated *fixable, currently-untargeted* miss class (4 instances + 1 in-lens ADJACENT).
- `decision_matrix.md` → `sibling_function_parity` scores **31** (top buildable candidate): highest
  repeated-miss count, broadest category span, fast fixtures, low ambiguity, complements (does not
  duplicate) `cross_function_invariant` and `semantic_guard`.
- `easiest_next_family_recommendation.md` → named the pick, with the two-signal gate sketch.

The invariant: **when two or more near-identical functions reach the same state transition, they must
enforce the same guards, checks, value conversions, and state updates. If one omits what its sibling
has, that omission is the bug.**

## 2. Grounded bug corpus (parity-attributable answer-key bugs)

Transcribed from `raw_results/answer_keys.json` + verified against source.

| Subject | Bug | Sibling pair | Missing component in the weak sibling | Parity category |
|---------|-----|--------------|----------------------------------------|-----------------|
| blackhole-2025-05 | **M-04** (anchor) | `RewardsDistributor.claim` ↔ `claim_many` | `claim` resolves `avm.getOriginalOwner(_tokenId)` inside an AVM guard; `claim_many` omits the whole AVM block → AVM-managed lock rewards sent to wrong recipient | **Recipient / Validation** |
| size-credit-2024-06 | **M-02** | `SellCreditMarket.validateSellCreditMarket` vs sibling buy/execute path | min-credit threshold checked against cash, not resulting credit (validation present on one path, wrong/absent on the parity path) | **Validation** |
| size-credit-2024-06 | **M-06** | `SellCreditMarket.executeSellCreditMarket` ↔ `Compensate.executeCompensate` | `forSale` flag checked before selling on one path, not the other | **Validation / Access** |
| size-credit-2024-06 | **M-12** | `BuyCreditMarket.executeBuyCreditMarket` vs sibling | returns incorrect cash amount (over-estimates pool check vs sibling) | **State-transition** |
| (cross-eval echoes) | — | Beanstalk convert variants; Hybra `claimRewards` variants | sibling reward/convert paths diverge on a guard | Validation/State |

**Anchor detail (blackhole M-04), verified in source** (`RewardsDistributor.sol` L197/L219):
`claim` contains `if (address(avm) != address(0) && avm.tokenIdToAVMId(_tokenId) != 0) { _nftOwner =
avm.getOriginalOwner(_tokenId); }` before `IERC20(token).transfer(_nftOwner, amount)`. `claim_many`
runs the same `_claim` / `ownerOf` / `deposit_for` / `transfer` calls in a loop but **never** calls
`getOriginalOwner` / `tokenIdToAVMId` / references `avm`. The pair shares ≥4 internal calls and the
`claim` name-stem → unambiguous sibling; the missing owner-resolution call on a shared
transfer-recipient path is the bug.

## 3. Category distribution (from the corpus + the 7-category taxonomy)

| Parity category | Corpus instances | Cross-category reach |
|-----------------|:---:|----------------------|
| Validation (require / internal-validator parity) | 3 (size M-02/M-06 + blackhole M-04 sub) | Lending, Trading |
| Recipient (beneficiary/owner resolution parity) | 1 (blackhole M-04) | Trading, Yield |
| State-transition (accounting update parity) | 1 (size M-12) | Lending |
| Access-control (modifier parity) | latent (semantic_guard overlap) | all |
| Cap-enforcement / Registry / Pause | latent (expected from corpus mining Phase 2) | Lending, Yield, Infra |

Conclusion: parity bugs are **not** Lending-specific — the anchor is a Trading (ve(3,3)) reward bug.
This satisfies the cross-category success criterion.

## 4. Expected root causes

1. **Batch/variant drift** — a `*_many`/`batch*`/`*For`/`*To` sibling is added later and forgets a
   check the singular has (blackhole M-04 is exactly this).
2. **Validate-vs-execute drift** — `validate*` and `execute*` siblings encode the guard inconsistently
   (Size pattern).
3. **Copy-paste divergence** — two entrypoints into the same effect with one stale.

## 5. Expected signal sources

- **Sibling discovery:** name-stem match (`claim`/`claim_many`, `validate*`/`execute*`, `*For`/`*To`)
  **OR** ≥2 shared internal-call identifiers / shared state-write targets (Jaccard over call sets).
- **Asymmetry signal:** a *meaningful* component present in one body, absent in the sibling on a shared
  mutating path — drawn from a controlled vocabulary: `require`/internal-validator calls,
  owner/recipient-resolution calls (`getOriginalOwner`, `ownerOf`-resolution), cap checks, modifiers
  (from manifest `modifiers`), registry add/remove steps, pause guards, accounting state-writes.

## 6. Expected false-positive sources (to suppress in Phase 7)

- **Legitimate structural difference** — a `*_many` loop's scaffolding (`for`, `i`, `length`, `break`,
  running totals) differs but is not a security asymmetry. → diff only the *controlled vocabulary*,
  never arbitrary identifiers.
- **View/pure siblings** — getters with no state transition. → suppress.
- **Admin-only maintenance pairs** — both privileged; asymmetry is intended. → suppress when both carry
  admin modifiers.
- **Thin wrappers / overloads** — one sibling just forwards to the other (`f()` → `f(default)`). →
  suppress when one body is a single call to the other.
- **Interface / abstract declarations** — no body. → suppress.
- **Observability-only diffs** — a missing `emit` with no correlated state inconsistency. → never emit
  event-only findings.

These map 1:1 to the FP-controls block in the config and the suppression tests.
