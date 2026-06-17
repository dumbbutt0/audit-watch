# P230 — Architecture Recall Generalization Evaluation

> **Type:** read-only measurement. No detectors/prompts/routing/severity/harnesses/dashboard/taxonomy modified.
> Answer keys **sealed end-to-end** (user decision) → this measures recall *quality* (senior-auditor
> plausibility), not hit-rate vs ground truth. Every scored candidate traces to a captured artifact
> (`candidates_{quantamm,decent,traitforge}.md`); nothing was invented during scoring.

## Objective & method
Test the P228/P229 hypothesis that **architecture-coverage recall is the dominant remaining blocker**. Ran the
api-free recall workflow (surface → defense → invariant → candidate generation → exploitability reasoning),
**stopping before harness**, on three fresh blind subjects outside the validated lending corpus, one per
architecture:

| Category | Subject | Core scope | Recall instruments driven |
|---|---|---|---|
| Oracle-heavy | QuantAMM 2024-12 | ~2,227 LOC | deep_trace + oracle/arithmetic/economic/logic/access/behavioral specialists + units/defi-accounting lenses |
| Cross-chain | Decent 2024-01 (UTB) | ~1,377 LOC | deep_trace + cross_chain/access/logic/economic/dos/reentrancy + cross_chain_constants/migration lenses |
| NFT/Gaming | TraitForge 2024-07 | ~880 nSLOC | deep_trace + token_integration/access/logic/economic/arithmetic/reentrancy/dos + token_standard/griefing lenses |

---

## Part A — Recall Measurement

| Subject | Raw Recall (plausible candidates) | Useful Recall (HIGH+MED, worth investigating) | HIGH | NOISE | Architecture Coverage |
|---|---|---|---|---|---|
| QuantAMM (Oracle) | 25 | 17 | 8 | 1 | **Diverse** — oracle, accounting, invariant, arithmetic, access-control, state-transition |
| Decent (Cross-chain) | 17 | 16 | 8 | 0 | **Diverse** — access-control, routing, accounting, economic, dos, invariant |
| TraitForge (NFT) | 26 | 18 | 6 | 2 | **Diverse** — entropy/oracle, access-control, reentrancy, accounting, dos, economic |
| **Total** | **68** | **51 (75%)** | **22** | **3 (4.4%)** | broad in all three |

Every subject produced double-digit candidates with strong HIGH-signal counts and <5% noise. Decisively, the
candidates are **architecture-specific**, not generic lending shapes recycled:
- **Oracle:** staleness-revert-unreachable (QAMM-03), missing `answeredInRound` (QAMM-23), multi-hop zero/negative
  price (QAMM-07), 1e18 price double-scaling into fee accounting (QAMM-09), uplift-fee integer-truncation
  (QAMM-10), weight-sum guard-rail invariants (QAMM-16/06).
- **Cross-chain:** unguarded destination execution (DEC-01), `chainId`-less fee-signature replay (DEC-03),
  trusted-remote/src-field discarding (DEC-02), bridged-vs-execution amount mismatch (DEC-13) — the canonical
  bridge bug taxonomy.
- **NFT/Gaming:** entropy predictability/seeding/cycling (TF-01/02/24), honeypot fund-vs-balance divergence
  (TF-05), generation-bricking owner mismatch (TF-17), CEI on ETH payouts (TF-06/07), merkle whitelist replay
  (TF-23).

---

## Part B — Mechanism Diversity (8 classes × 3 subjects)

| Bug class | QuantAMM | Decent | TraitForge |
|---|---|---|---|
| accounting | ✓ (09,10,01) | ✓ (04,05,15) | ✓ (05,12,16) |
| state-transition | ✓ (01,11,17) | ~ (via routing) | ✓ (03,11,25) |
| access-control | ✓ (02,14,18,19) | ✓ (01,06,09) | ✓ (02,17,23) |
| economic | ✓ (10) | ✓ (05,07) | ✓ (09,19) |
| invariant-violation | ✓ (05,06,12,16) | ✓ (03) | ✓ (05,08,24) |
| oracle | ✓ (03,07,23) | — (no oracle in scope) | ✓ (01,19,24 entropy-as-oracle) |
| routing | — | ✓ (02,12,13) | ✓ (04,16) |
| timing | ~ (interp boundary/cadence) | ~ (fee volatility) | ~ (holding-period TF-08) |

**Recall is BROAD, not concentrated.** Each subject covers 6–7 of 8 classes, and the concentrations track the
architecture correctly (oracle-heavy in QuantAMM, routing in Decent, entropy/access in TraitForge). The recall
stack is not pattern-locked to one mechanism family.

---

## Part C — Senior-Auditor Simulation

Triage judgment on the HIGH_SIGNAL candidates (the auditor's first pass); MED/LOW rolled up below.

| Candidate | Investigate? | Why | Priority | Effort | Conversion likelihood |
|---|---|---|---|---|---|
| DEC-01 unguarded receiveFromBridge | **YES** | public fn executing arbitrary payload at contract's expense | P0 | low | high |
| DEC-03 chainId-less fee replay | **YES** | textbook cross-chain replay; single-tx path | P0 | low | high |
| DEC-13/02 sgReceive ignores token/amount/src | **YES** | systematic bridged-vs-exec mismatch; canonical | P1 | med | med-high |
| DEC-04 stale approval on failed call | **YES** | drainable allowance | P1 | med | med |
| DEC-06 onlyUtb bypass on swapNoPath | **YES** | residual-balance drain | P1 | med | med |
| DEC-09/10 ecrecover-zero / locked refund | **YES** | known patterns, real funds | P2 | low | med |
| QAMM-09 price double-scale into fee | **YES** | 1e18-inflated value into exit-fee math | P0 | med | high |
| QAMM-10 uplift-fee truncation | **YES** | fee never charged <100% growth | P0 | med | high |
| QAMM-01 shared fee storage slot | **YES** | two fees overwrite each other | P1 | low | high |
| QAMM-03 staleness unreachable (1 oracle) | **YES** | stale price silently used | P1 | med | med |
| QAMM-16/05 weight invariant/underflow | **YES** | sum-to-one break / interp DoS (CYFRIN H02 echo) | P1 | high | med |
| QAMM-08/14 uint loop / pool pre-register | **YES** | DoS surfaces | P2 | med | med |
| TF-17 generation-bricking owner mismatch | **YES** | minting halts after gen 1 | P0 | low | high |
| TF-02/01/24 entropy seed/predict/cycle | **YES** | trait randomness fully gameable | P0 | med | high |
| TF-05 honeypot fund/balance divergence | **YES** | core economic invariant | P1 | med | med |
| TF-14 transfer-bricking forging cancel | **YES** | protocol-wide transfer DoS | P1 | low | med |

**Roll-up:** of 68 candidates, an experienced auditor would investigate **all 22 HIGH and most of the 29 MED**
(≈45–50 of 68). The LOW/NOISE (14) are correctly self-deprioritized, several explicitly self-marked "analyzed —
not a bug" (e.g., QAMM-21, TF-13/18/25) — evidence the stack also self-suppresses rather than over-claiming.

---

## Part D — Architecture Weakness Analysis

| | Oracle (QuantAMM) | Cross-chain (Decent) | NFT/Gaming (TraitForge) |
|---|---|---|---|
| **Missing Recall** | multi-block oracle-manipulation *sequences* (found single-read flaws, not "manipulate-then-act" timelines) | LayerZero/Stargate-specific config-trust depth; gas/airdrop griefing economics | long-run economic-equilibrium / honeypot-solvency over many txns; game-progression exploits |
| **Missing Vocabulary** | TFMM weight-interpolation semantics (handled, but interpolation-timeline reasoning was the shakiest) | adapter trust topology (which actor is `bridgeExecutor` in practice) | breeding/forge eligibility economics; nuke-factor game theory |
| **Missing Invariants** | cross-oracle *consistency*; weight-sum after pack round-trip under all clamp combos | conservation across swap→bridge→postBridge as one timeline | fund-share conservation across interleaved nuke/mint/airdrop; entropy-uniqueness |
| **Missing Taxonomy** | none critical (oracle lens fired well) | message-binding/replay is caught by reasoning but is not a *validated* family | **no entropy/randomness-predictability detector family** (caught by reasoning only) |

The common thread across all three is **temporal / multi-transaction reasoning** — single-call flaws are caught
strongly; cross-tx economic-equilibrium and manipulation-sequence invariants are where candidates drop to
Speculative. This is the *same* gap P229 named for harnesses (temporal bugs), now visible on the recall side too.

---

## Part E — Counterfactual: if harnessing were perfect tomorrow, would these be reportable?

- **Oracle (QuantAMM):** **Yes, strongly.** QAMM-09 (price double-scale → fee inflation), QAMM-10 (uplift-fee
  truncation), QAMM-01 (shared fee slot), QAMM-03 (stale price) are concrete, code-evidenced, single-mechanism —
  exactly the shape that converts to an L3 proof. High-yield.
- **Cross-chain (Decent):** **Yes, strongly.** DEC-01/03/13/04/06 are concrete access-control / replay /
  accounting bugs with clear attacker entry. The cleanest set (0 noise). High-yield, though some require a
  multi-contract/bridge harness (the integration tier P229 flagged).
- **NFT/Gaming (TraitForge):** **Yes, moderately.** TF-17 (generation brick), TF-02/01/24 (entropy), TF-05
  (fund divergence), TF-14 (transfer DoS) would convert. Slightly lower yield: more Speculative entries and the
  highest-value game-economic exploits need multi-tx harnesses.

Conversion is gated by **harness capability, not candidate quality** — which isolates the result: recall is not
the limiting factor for any of the three.

---

## Final Verdict

# A — RECALL_GENERALIZES

Recall is architecture-agnostic in the measured sense: on three architectures outside the validated lending
corpus, the stack produced 68 plausible, broadly-distributed, **architecture-specific** candidates (75% worth
investigating, 4.4% noise), including the canonical bug classes for each (oracle staleness/scaling/accounting;
bridge replay/trusted-remote/amount-mismatch; NFT entropy/honeypot/CEI). It did not collapse to generic lending
patterns. **The P228/P229 framing — that architecture-coverage recall is the dominant blocker — is not supported
by the measurement; it was overestimated.**

Caveats (why confidence is MEDIUM, not HIGH): keys sealed → quality measured, not key-verified hit-rate; one
subject per architecture; my own scoring is the instrument. The soft spots are NFT signal-density (lowest HIGH
ratio) and, across all three, temporal/multi-tx economic-invariant recall.

---

## Deliverables

| Field | Value |
|---|---|
| **Recall Score** | **80 / 100** (raw volume strong; 75% useful; 4.4% noise; broad mechanism coverage; architecture-specific) |
| **Confidence** | **MEDIUM** (quality not hit-rate; n=1 subject/arch; single scorer) |
| **Strongest Architecture** | **Cross-chain (Decent)** — 16/17 useful, 0 noise, full canonical bridge taxonomy |
| **Weakest Architecture** | **NFT/Gaming (TraitForge)** — lowest HIGH density (6/26), most noise (2), more Speculative game-economic entries |
| **Biggest Missing Invariant Family** | **Multi-transaction / cross-epoch economic-equilibrium invariants** (honeypot solvency, oracle manipulate-then-act, conservation across swap→bridge timelines) — where candidates consistently fell to Speculative |
| **Biggest Missing Taxonomy Family** | **Entropy / on-chain-randomness predictability** (NFT/gaming) — found by reasoning, but no validated detector family |
| **Estimated Readiness If Harnesses Were Perfect** | **~85/100, verdict approaches A (BUG_BOUNTY_READY).** With recall shown to generalize AND conversion solved, both P228 unknowns close; residual is precision verification + the temporal-invariant soft spot |
| **Top-3 ROI "recall expansions"** | These are **refinements, not blockers** (no recall gap was found): (1) temporal/multi-tx economic-invariant recall; (2) entropy/randomness-predictability family for gaming; (3) cross-oracle-consistency / manipulation-sequence recall |

### Recommendation: **Harness scaffold** (then live hunting) — NOT architecture validation

Defended by the measurement, not optimism:
1. **No recall gap was measured**, so the three "validation" implementation phases (Oracle / Cross-chain / NFT)
   are **not** warranted — the phase explicitly forbids recommending implementation absent a genuine recall gap.
2. Recall generalizing **revives harness generation as the binding constraint**. P229 had de-ranked harness only
   *because it assumed recall was the gap*; P230 falsifies that assumption. With strong candidates now
   demonstrated across 3 architectures and conversion still gated by a **lending-only** harness capability
   (P229), the highest-ROI move is to build the **multi-architecture harness/conversion capability**.
3. **Live hunting is premature** until conversion exists — strong unverified candidates would hit the harness
   wall immediately.

Net correction to the arc: **P228/P229 overestimated the recall/coverage blocker. The dominant blocker is
conversion (harness generation, generalized beyond lending) plus the shared temporal-invariant soft spot — not
architecture recall.**
