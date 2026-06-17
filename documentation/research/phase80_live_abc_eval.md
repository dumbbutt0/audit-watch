# Phase 80 — Live-Agent A/B/C Reasoning Eval (Kelp DAO, held-out)

**Result: LIVE-SAFETY PASS. Hit-accrual NOT EVALUATED (no in-repo answer key).** The P77/P78 verification discipline was
run **live** (me reasoning over real Kelp source, not a deterministic sim) across 6 held-out leads, hybrid isolation
(A/B = my sequential frozen passes; **C's adversarial review = an isolated subagent**). Arm C produced **0 unsupported
READY, 0 SOURCE_FALSE, 0 HARD_FAIL, 0 unsafe over-promotions**, fail-closed where source/impact was unresolved, and gated
its 2 promotions through an isolated adversarial review + hygiene. **This is a live-safety pass only — not hit-accrual
proof.**

## Honesty caveats (read first)
- **No answer key.** Kelp's `findings/raw`, `findings/validated`, `data/findings`, `reports` are all empty; no holdout has
  an in-repo answer key. **Ground truth was NOT fabricated** from my source reasoning (self-confirming) or training memory
  (answer-key leakage). So **hit-accrual and true positive/negative recall are NOT scored.**
- **Live + non-deterministic + N=6** → a survival/quality signal, not statistical proof.
- **Hybrid A/B leakage:** I authored arm A's evidence after reading source, so A may be less naive than a cold baseline
  (documented).
- **B ≈ C on this batch:** the Kelp leads contained no source-falsifiable traps, so the defense ledger (B) did the heavy
  lifting; C's falsification + isolated adversarial review were exercised (gated 2 promotions, found 0 falsifier) but were
  not decision-changing here.

## Method
6 STATIC_LEADs were selected from **source-facing surfaces and frozen** (`_p80/leads.json`, `fdb7bdad`) before any
investigation and before the answer key was checked. Per lead I ran A (baseline), then B (defense-first), then C (full:
`/audit-candidate-verification` → `deep_pass` bundle → **isolated adversarial subagent** → `hygiene_validate` fail-closed),
freezing each bundle before the next. Only after all C bundles + reviews were frozen did I check for an answer key (none).

## Decisions (frozen before answer-key check)
| lead (Kelp) | A baseline | B defense-first | C full | source fact |
|---|---|---|---|---|
| L1 depositAsset | POC_REQUIRED | NEEDS_CONTEXT | **NEEDS_CONTEXT** | no minOut; mispricing depends on oracle (unresolved) |
| L2 getRSETHPrice | POC_REQUIRED | POC_REQUIRED | **POC_REQUIRED** (adversarial PASS) | price = balanceOf-based totalAssetDeposits / supply → donation-manipulable |
| L3 depositAssetIntoStrategy | POC_REQUIRED | REJECTED | **REJECTED** | `onlyLRTManager` + `nonReentrant` (defense, source fact) |
| L4 rseth-mint | POC_REQUIRED | REJECTED | **REJECTED** | `onlyRole(MINTER_ROLE)` (defense, source fact) |
| L5 updateAssetStrategy | POC_REQUIRED | NEEDS_CONTEXT | **NEEDS_CONTEXT** | admin-gated (`DEFAULT_ADMIN_ROLE`); migration unresolved |
| L6 chainlink getAssetPrice | POC_REQUIRED | POC_REQUIRED | **POC_REQUIRED** (adversarial PASS) | deprecated `latestAnswer()`, no staleness/round check, feeds mint |

## Separated metrics
**1. Safety improvement — PASS.** Arm A over-promotes **6/6**, including the two **source-fact defense-blocked** leads
(L3 `onlyLRTManager`, L4 `MINTER_ROLE`) — a real over-promotion. B and C **reject both** and NEEDS_CONTEXT the under-resolved
L1/L5. C: **0 unsupported READY · 0 SOURCE_FALSE · 0 HARD_FAIL · 0 detector→finding.**
**2. Mechanism correctness.** A asserted missing-auth/wrong-actor on access-controlled L3/L4/L5 and over-promoted; C
correctly rejected L3/L4 (defense) and abstained on L5 (admin) → fewer wrong-mechanism promotions than A. (vs-truth
unscorable without a key.)
**3. Hit-accrual evidence — NOT EVALUATED.** No answer key. L2 (rsETH price donation-manipulation) and L6 (Chainlink
`latestAnswer` staleness) are source-backed candidates that **passed an isolated adversarial review**; they are consistent
with publicly-known Kelp themes but are **NOT counted as scored hits** (training memory ≠ repo answer key).
**4. Live-agent readiness — PARTIAL.** The full discipline (defense ledger + source-falsification + isolated adversarial
subagent + hygiene fail-closed) ran live on a held-out codebase and **fail-closed correctly**; recall is unmeasured
without a key.

## Isolated adversarial review (author≠judge)
A separate general-purpose subagent (id `a74ac78`) — which did not author the bundles and was instructed not to open any
findings — reviewed C's two promotions from source. It returned **PASS** for both, and sharpened them: L6's negative-price
sub-claim is unreachable (`uint256` return) and L2's net-profit path is PoC-dependent (donation may be griefing, not theft).
This is exactly the intended seatbelt: the reviewer confirmed the source-backed defect while trimming over-claims, without
the author judging its own work.

## Pass / fail
**PASS (live safety)** per the agreed rule "0 unsafe promotions + 0 scored hits = live-safety pass only": C had 0 unsupported
READY, 0 SOURCE_FALSE, 0 HARD_FAIL, 0 detector→finding; rejected the defense-blocked leads; fail-closed on the unresolved
ones; both promotions adversarially reviewed PASS + hygiene-clean. **No STOP/repair condition triggered** (no C SOURCE_FALSE
or unsupported READY). **Stretch (live hit-accrual): NOT met** — unevaluable without an answer key.

## Integrity
`_p80/leads.json` (`fdb7bdad`, frozen pre-investigation) · `_p80/<lead>/{A,B,C}_bundle.json` (6) + `adversarial_review.json`
(L2, L6) · `_p80/scores.json` · `_p80/_freeze/phase80_freeze.json` · this report. Modules byte-identical (deep_pass
`57c29fff`, hygiene `b9e18f29`, abc_eval `5e0d855d`, lead_schema `3c57f04e`, transitions `2c00069c`); parked detectors +
value-flow byte-identical; `tests/investigation` 28 passed; no-wiring CLEAN; no new detector logic; no module edits; no
production wiring. **Promotes nothing.**

## Recommended next
Live safety holds; hit-accrual is the missing evidence and **needs a keyed subject**. Two options for **P81**:
- **P81a — keyed live A/B/C:** re-run the same live protocol on a subject **with a real answer key** (a `code-423n4`/Sherlock
  contest cloned with its findings), to finally measure live hit-accrual (same-function+same-mechanism) and false-negative
  recall — the genuine "does it find real bugs live" test.
- **P81b — PoC handoff gate:** build the gate so only concrete-attacker-sequence candidates (like C's L2/L6 here, with their
  adversarial PASS + named missing proof) enter the PoC builder.
Given hit-accrual is still unproven, **P81a is recommended first.** North star: high recall at the lead layer, near-zero
false-positive promotion at the review layer.

## Reproduce
```
cat documentation/research/_p80/leads.json          # frozen leads
ls documentation/research/_p80/L*/                  # per-arm bundles + adversarial reviews
python3 scripts/investigation/hygiene_validate.py --bundle documentation/research/_p80/L6-chainlink-getAssetPrice/C_bundle.json --review documentation/research/_p80/L6-chainlink-getAssetPrice/adversarial_review.json
~/.local/bin/pytest tests/investigation/ -q          # 28 passed
```
