# Permit2 Asset-Binding Detector Prototype (Shape A)

**Type:** research prototype. Research-only, un-wired: `is_gate:false` / `research_only:true` /
`routes_in_production:false` / `routed_manifest_ids:[]`. No routing, submission, gate integration, severity
automation, answer-key modification, or promotion. The frozen `multicall_invariant` detector is untouched. Design
philosophy: **high precision over recall** — false negatives are acceptable; high-confidence false positives are
not.

**Files:** `scripts/permit_asset_binding_taxonomy.py` (pure classifier) · `scripts/permit_asset_binding_audit.py`
(manifest-driven runner) · `config/permit_asset_binding_patterns.json` · `tests/permit_asset_binding/` (11 tests).
Eval artifacts: `documentation/research/_permit_experiment/_runs/<target>/output/permit_asset_binding_audit.json`.

---

## 1. Executive Summary

A narrow, three-signal Permit2 asset-binding detector (Shape A) **detects the Revert Lend #368 anchor cleanly and
stays silent on every permit-heavy negative**. On a 7-target evaluation (1 positive + 6 negatives): the anchor
produced **3 high-confidence candidates** (the V3Vault permit cluster `_deposit` / `_repay` / `liquidate`), and
**all 6 negatives produced 0 candidates** — including two real multi-asset routers (UniV3 SwapRouter, UniV3
SelfPermit) and four in-scope permit-using protocols. **Zero high-confidence false positives; total candidate
volume on the positive = 3 of 201 manifest items.** This meets every success criterion. The shape is precise
because it requires a *protocol-bound single asset* (vaults/lending) AND the *absence* of a token==asset check AND
survives router/library/validation/param-token suppression — i.e. it fires on the narrow asset-mismatch corner and
nothing else. **Verdict: HIGH PRECISION PROTOTYPE VALIDATED** (research-only; recall is intentionally narrow).

---

## 2. Detector Scope
Detects **only Shape A**: a permit/Permit2-authorized transfer is consumed by protocol logic that has a single
expected asset, and the code never binds `permitted.token == expectedAsset`. It does **not** detect replay,
front-running, recipient/witness binding, signature/approval reuse, ERC2771, msg.value reuse, or multicall
execution (those are explicitly out of scope and, where relevant, covered by the existing `signature-replay`
pattern or the frozen `multicall_invariant` lens).

## 3. Shape Definition (three-signal AND, then suppressions)
- **S1 — permit consumption (own body):** a genuine consumption call — `permitTransferFrom` /
  `permitWitnessTransferFrom` / ERC-2612 `.permit(`. Gated on the function's **own** body so a non-consuming caller
  of a permit helper is not flagged.
- **S2 — single bound asset:** the (resolved) scope references a protocol-bound asset — `asset` / `asset()` /
  `IERC20(asset)` / `underlying` / `want` / an immutable/state token var. A caller-supplied token parameter does
  **not** count (that is router / asset-agnostic).
- **S3 — missing binding (absence):** no `permitted.token == asset` (or `!=`, `InvalidToken`, `TokenMismatch`)
  comparison on the resolved path. (S2/S3 use +1-level helper resolution so a binding located in a helper is seen
  and does **not** false-positive.)
- **Candidate iff** S1 ∧ S2 ∧ S3 ∧ not suppressed.

## 4. Positive Dataset

| Protocol | Source | Permit type | Expected-asset source | Validation mechanism | Detector result |
|---|---|---|---|---|---|
| Revert Lend `V3Vault` (anchor, H-01/#368) | code-423n4/2024-03-revert-lend-findings #368 (in-repo workspace) | Permit2 SignatureTransfer | `address public immutable asset` (USDC); `IERC20(asset)` in the non-permit branch | **none** (no `permitted.token == asset`) | **DETECTED — 3× high** (`_deposit`, `_repay`, `liquidate`) |

Corpus positives that are **accepted false negatives** (not runnable in-repo / out-of-shape, recorded for honesty):
Aave v3.3 #138 (permit *validation bypass*, not token mismatch) and Permit2 #250 (recipient axis, not asset axis) —
both outside Shape A by design.

## 5. Negative Dataset (permit-heavy but safe / out-of-shape)

| Protocol | Source | Permit usage | Why it should stay quiet | Detector result |
|---|---|---|---|---|
| UniV3 SwapRouter | fetched (v3-periphery) | `selfPermit` + `Multicall` | multi-asset router (router name + token-param) | **0** ✓ |
| UniV3 SelfPermit/Payments | fetched (v3-periphery) | `selfPermit*` | permit primitive / router base | **0** ✓ |
| Recall 2025-02 | in-repo | 3 in-scope permit/batch fns | not a single-asset permit-transfer consumer | **0** ✓ |
| Tokemak 2023-06 | in-repo | 1 permit ref | not Shape A | **0** ✓ |
| QuantAMM 2024-12 | in-repo | 1 permit ref | AMM, not single-asset permit consume | **0** ✓ |
| Blackhole 2025-05 | in-repo | 1 permit ref | router/AMM | **0** ✓ |

Additionally, the **full Revert Lend manifest (201 items)** acted as a volume control: only the 3 genuine permit
consumers fired; the other ~198 items (including `V3Vault.constructor`, which merely *references* `permit2`/`asset`)
produced nothing — the S1 consumption gate excludes the constructor.

## 6. Detection Signals (with benefit + precision cost)
| Signal | Benefit | Precision cost |
|---|---|---|
| S1 permit-consume (own body) | anchors on the genuine attack surface; excludes type-refs/assignments and non-consuming callers | may miss permit consumption hidden behind an opaque external call |
| S2 single bound asset | restricts to vaults/lending where "the asset" is well-defined (where mismatch = fund loss) | misses protocols whose asset is per-market/computed (accepted FN) |
| S3 missing binding | this *is* the bug; absence is the signal | absence-detection is intrinsically fragile — mitigated by helper-resolved binding check + validation suppression |

## 7. Suppression Rules (and why)
- **Multi-asset router / aggregator / bridge** — by contract/file name (`router`/`swap`/`aggregat`/`bridge`/
  `periphery`/`zap`) **or** an arbitrary token/path parameter (`tokenIn`, `path`, `tokens[]`, `token` param).
  Routers accept any token by design → not a mismatch bug. (Drove the two UniV3 negatives to 0.)
- **Permit primitive library** — `kind==library` or contract ∈ {Permit2, SignatureTransfer, AllowanceTransfer,
  SafeERC20, SelfPermit, ERC20Permit}. The primitive is not an integrator.
- **Explicit validation present** — any `permitted.token == asset` / `!=` / `InvalidToken` → S3 fails → no
  candidate (the exact Revert Lend mitigation clears the finding).
- **Asset-agnostic** — token sourced from a caller parameter with no bound asset.

## 8. Candidate Examples (required output format)
```
contract=V3Vault  function=_deposit  permit_source=permittransferfrom  expected_asset_source=IERC20(asset)
  confidence=high  suppression_status=none
  missing_binding_explanation: _deposit consumes a Permit2 transfer into a protocol with a single expected asset
    (IERC20(asset)) but never asserts the permit's token equals that asset — a Permit2 signature for a different
    ERC-20 could be credited as the protocol asset (Shape A, Revert Lend #368 class).
```
(`_repay`, `liquidate` identical shape/confidence; all `suppression_status=none`.)

## 9. False Positive Analysis
- **High-confidence FPs: 0** across all 7 targets.
- An early build false-fired on `V3Vault.constructor` (it references `permit2` and sets `asset`); fixed by gating
  **S1 on a genuine consumption call in the function's own body** (a type reference / assignment is not
  consumption). It also initially bled the permit signal to non-consuming public callers via helper resolution;
  the own-body S1 gate removed that, dropping the anchor from 7→3 candidates with no loss of the true positive.
- The router negatives confirm the asset-agnostic + router-name suppressions hold on real multi-asset code.

## 10. Precision Assessment
**High.** 0 high-confidence FPs; routers and permit primitives suppressed; permit-using non-vault protocols silent;
positive volume = 3/201. The three-signal AND gate plus the protocol-bound-asset requirement keep the detector off
the ubiquitous-but-safe permit surface. **Most common suppression reason: multi-asset router / asset-agnostic
param-token** (the designed-quiet case for routers).

## 11. Recall Assessment
**Intentionally narrow (acceptable for a research lens).** It recovers the in-repo asset-mismatch anchor (#368) in
full. It does **not** cover permit-validation-bypass (Aave #138), recipient-axis (Permit2 #250), or
per-market/computed-asset protocols — these are **accepted false negatives** consistent with "high precision over
recall" and the Shape-A-only mandate. Recall on the *asset-mismatch* sub-shape specifically: 1/1 runnable positive.

## 12. Known Limitations
- Absence-based S3 is fragile if a binding is expressed unusually or lives >1 helper level away (could FP); the
  helper-resolved binding check mitigates the common case.
- S2 keys on a literal `asset`/`asset()`/immutable token; protocols whose "expected asset" is per-market or derived
  are missed (FN) — by design (suppressed rather than guessed).
- Single runnable in-repo positive (Revert Lend); broader recall numbers await more in-repo permit-asset-mismatch
  source.
- Regex/body-scoped (like the other lenses); no full data-flow — it flags the *opportunity* (permit consumed, asset
  bound, no equality check), not a proven exploit.

## 13. Recommendation

# HIGH PRECISION PROTOTYPE VALIDATED

All four success criteria are met: (1) the Revert Lend anchor is detected (3× high incl. `_deposit`); (2)
permit-heavy safe protocols stay quiet (6/6 negatives = 0); (3) zero high-confidence false positives; (4) candidate
volume is tiny and reviewable. **Keep research-only / do not route / do not promote.** The narrow Shape-A asset-
binding family is precision-preserving and behaves like the validated `multicall_invariant` narrow lens. Next steps
(separate approval): grow the in-repo positive set for a recall number, and consider an advisory-only promotion only
after a frozen multi-target validation with sustained 0 high-confidence FP — the same bar `multicall_invariant` met.

---

## Final Output
1. **Executive summary:** narrow three-signal Permit2 asset-binding detector; detects Revert Lend #368 (3× high),
   silent on 6/6 permit-heavy negatives, 0 high-confidence FP — HIGH PRECISION PROTOTYPE VALIDATED, research-only.
2. **Dataset summary:** 1 positive (Revert Lend `V3Vault`, in-repo) + 6 negatives (2 UniV3 routers + Recall/Tokemak/
   QuantAMM/Blackhole) + full-manifest volume control.
3. **Detection rate:** anchor 3/3 V3Vault permit consumers (incl. `_deposit`); asset-mismatch sub-shape recall 1/1
   runnable positive.
4. **False positive rate:** 0 high-confidence FP across 7 targets; 0 candidates on all 6 negatives.
5. **Most common suppression reason:** multi-asset router / asset-agnostic param-token.
6. **Precision assessment:** high (3/201 on positive; 0 elsewhere; routers + primitives suppressed).
7. **Recall assessment:** intentionally narrow; recovers asset-mismatch anchor; validation-bypass / recipient-axis
   / computed-asset cases are accepted false negatives.
8. **Recommendation:** **HIGH PRECISION PROTOTYPE VALIDATED** — keep research-only, un-wired; promote only after a
   broader frozen validation.

### Integrity
Frozen `multicall_invariant` (taxonomy/audit/patterns) **0 drift**; eval-workspace canonical manifests **0 drift**;
new detector **un-wired** (no routing/gate/run_pipeline/agent_policy reference); flags preserved
(`is_gate:false`/`research_only:true`/`routes_in_production:false`/`routed_manifest_ids:[]`); **36 tests pass**
(11 new permit + 25 multicall). New files only; no canonical manifest, answer key, or frozen snapshot modified.
