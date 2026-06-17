# Phase 81c — Lead precision (tighten bridge_receive) + promotion severity/impact gate

> **CORRECTION (added during P81d).** P81c cited Decent recall as 9/9; that was measured on the decent-bridge HEAD
> (post-fix) source. On the audited 2024-01 commit, recall is **8/9 DIRECT** (H-01 `setRouter` is unguarded and the
> lens misses it — `admin_config_setter` `requires_auth_modifier`). The `bridge_receive` tightening + severity gate
> results below are unaffected (no decent-bridge dependency). See P81d.

**Result: PASS.** The two known P81b problems are fixed without losing recall: the noisy `bridge_receive` class no
longer fires on view/accounting-math functions, and a new severity/impact gate demotes source-true-but-dust promotions
below POC_REQUIRED (closing the P81a D2 gap). Decent awarded-surface recall stays **9/9 DIRECT**; NOYA held-out
surface-relevant recall stays **8/8 DIRECT**. Narrow by design — no new surface classes. Research-only, un-wired,
promotes nothing.

## Why this phase
P81b's surface-first lens landed on awarded surfaces, but two issues would have corrupted the P81d end-to-end test:
1. `bridge_receive` over-tagged view/math functions (it fired on `abi.decode` / a bare `bytes` param) → would flood
   P77/P78 with junk (token waste, false mechanism pressure, wrong framing, severity over-promotion).
2. No promotion severity/impact gate — P81a's D2 (`swapNoPath`) was *source-true but dust-impact* yet became
   POC_REQUIRED. Source-true ≠ H/M-worthy.

## Job 1 — tighten `bridge_receive` (config + generic lens logic)
`bridge_receive` now requires **not view/pure** AND (a real bridge-callback **name**
[`receive`,`sgreceive`,`lzreceive`,`oncredit`,`credit`,`compose`,`onoftreceived`,`lzcompose`,`onflashloan`] **OR** a
**cross-chain shape** = a `bytes` payload param AND a cross-chain body token [`srcchain`,`srcaddress`,`srcpoolid`,
`origin`,`remote`,`_nonce`,`lzendpoint`]). `abi.decode` / bare bytes / generic `payload`/`callback` no longer trigger
it. Implemented via **generic config keys** (`require_any`, `crosschain_body_substr`, `crosschain_shape_needs_bytes_param`,
`exclude_view_pure`) in `classify_surface` — no class-name hardcoding; other classes unchanged.

**Effect (functions keep their lead status via the *correct* class; only the wrong label is removed):**
| | Decent | NOYA |
|---|---|---|
| total leads | 66 → **66** (no loss) | 231 → **198** (−33 pure view-math) |
| `bridge_receive` tags | 26 → **11** (all genuine: `receive`/`receiveFromBridge`/`onOFTReceived`/`sgReceive`) | 69 → **6** |
| `_getPositionTVL` tagged `bridge_receive` | 0 | **0** (was 6 — spurious) |

The 6 NOYA view-math `_getPositionTVL` findings (H-06/13/15/19/20/22) drop from *spurious DIRECT* to honest **ADJ**
(their connector contract still has real value/auth leads, but the pure-math view fn is no longer falsely tagged). This
is the **correct removal of noise** — those were never genuine surface recall.

## Job 2 — promotion severity/impact gate (new research-only layer)
`scripts/investigation/severity_impact_gate.py` (+ `config/severity_impact_gate.json`) — advisory post-layer shaped
like `hygiene_validate`: `gate(decision, impact_assessment) -> (kept, recommended_status, reason, impact_class)`.
Among PROMOTION-status decisions it **demotes** to `NEEDS_CONTEXT` when impact is `dust`/`low`/`qa`/`informational`
(or proven magnitude is transient/none), **keeps** material `critical`/`high`/`medium`, and **fail-closes** to
`NEEDS_CONTEXT` when impact is unproven. It never re-promotes a non-promotion decision, never edits
deep_pass/hygiene/transitions, never sets production severity.

**Demo (`_p81c/severity_gate_demo.json`):**
| candidate | input | → | result |
|---|---|---|---|
| P81a **D2** `swapNoPath` (source-true, transient/dust) | POC_REQUIRED | → | **NEEDS_CONTEXT** (gap closed) |
| H-03 `DecentBridgeExecutor.execute` (funds to random addr, material) | POC_REQUIRED | → | POC_REQUIRED (kept) |
| unproven-impact example | POC_REQUIRED | → | NEEDS_CONTEXT (fail-closed) |

## Pass / fail (user's P81c condition)
- Decent awarded-surface recall **9/9** (≥8/9 required) ✅
- NOYA surface-relevant recall **8/8** ✅
- spurious `bridge_receive` on view/math removed (6 `_getPositionTVL` → 0; tags 69→6 / 26→11) ✅
- D2-style source-true/dust demoted below POC_REQUIRED ✅
- no Decent/NOYA hardcoding (no-subject-names test passes); no production wiring; no finality language ✅
- **STRETCH met:** lead precision improved while preserving **100%** awarded-surface recall on Decent AND
  NOYA-surface-relevant.

## Honest notes / residuals
- A few remaining `bridge_receive` tags are name-substring matches on non-callback setters (e.g. NOYA
  `setFeeReceivers` — "receiver" contains "receive"). These are **not** view/math noise and remain correct leads via
  `admin_config_setter`; the extra label is cosmetic. Not worth a word-boundary rule that could risk
  `receiveFromBridge`.
- Mechanism naming is still the coarser layer (surface classes are a proxy) — unchanged from P81b; precise mechanism
  naming remains the deep-pass's job, to be tested in P81d.
- The severity gate consumes an `impact_assessment` it does not itself compute; in P81d that assessment comes from the
  live deep-pass / adversarial review. This phase proves the *gate logic*, not live impact estimation.

## Integrity
`config/surface_recall_lens.json` (`bridge_receive` only) + `scripts/investigation/surface_recall_lens.py`
(`classify_surface`, hash `29a7b915`) + new `scripts/investigation/severity_impact_gate.py` (`418738da`) +
`config/severity_impact_gate.json` + `_p81c/{severity_gate_demo.json,_freeze/phase81c_freeze.json}` + refreshed
`_p81b/{decent,noya}` leads/scores + `tests/investigation/test_severity_impact_gate.py` (8) + extended
`test_surface_recall_lens.py` (10). Protected modules **byte-identical** (deep_pass `57c29fff` · hygiene `b9e18f29` ·
transitions `2c00069c` · lead_schema `3c57f04e` · abc_eval `5e0d855d` · surface_recall_score `fd3c7543`; parked
detectors + value_flow unchanged). **147 tests pass.** No-wiring CLEAN. **Promotes nothing to production.**

## Recommended next — P81d (the genuine end-to-end test)
Keyed live A/B/C re-run on Decent: improved (clean) lead set → P77/P78 deep-pass → isolated adversarial review →
**severity_impact_gate** → keyed scoring. Question: now that leads land on awarded surfaces *and* the lens is
de-noised *and* the severity gate is in place, can the agentic loop recover real mechanisms (CLEAN_HIT/STRONG_PARTIAL)
**without adding severity FPs**? That is the real threshold before PoC handoff. Order: 1 leads ✅ → 2 investigate
safely ✅ → 3 severity gate ✅ (this phase) → **P81d end-to-end conversion test** → 4 PoC → 5 submission.
