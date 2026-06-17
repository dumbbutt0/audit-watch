# Next Specialist Chains — Phase Plan (Access-Control + Signature-Replay)

Research-only planning. Both chains follow the **same disciplined arc** that produced the value-flow chain (P33–P60):
no-code taxonomy → anchors + negative controls → research-only detector → contaminated diagnostics → fresh blind batch →
stop on OVERFIT → repair only the proven failure class → keep a regression pool → no promotion until repeated fresh-blind
success. **REVIEW_ONLY outputs; no production wiring; no promotion claimed.**

## Shared methodology (per chain)
1. **No-code taxonomy** — define families + strong-evidence + rejection (drafted in the chain configs).
2. **Anchors + negative controls** — 2–3 source-verified positive anchors from the already-contaminated corpus + ≥2
   negative controls (by-design-public / correctly-nonce'd) so the detector must abstain on benign code.
3. **Research-only detector** — narrow, FP-tight, `is_gate:false research_only:true routes_in_production:false`; self-test
   + pytest; emits the REVIEW_ONLY schema.
4. **Contaminated diagnostics** — validate on anchors + negatives + the existing regression pool (must not create noise).
5. **Fresh blind batch** — freeze-before-findings on fresh, uncontaminated, architecture-distinct subjects.
6. **Stop on OVERFIT** — any confident false positive halts the batch; no mid-batch tuning.
7. **Repair only the proven failure class** — a demotion-only gate for the exact false-positive shape (P45/P47/P49/P52 pattern).
8. **Keep a regression pool** — every anchor + repaired class pinned; re-run each phase.
9. **No promotion** until the promotion criteria below are met on repeated fresh-blind success.

## Scoring categories
CLEAN · PARTIAL · ADJACENT · ABSTAIN_CORRECT · OVERFIT · HARD_FAIL.

## Promotion criteria (per chain → promotion-review candidate only)
≥2 fresh-blind CLEAN/strong-PARTIAL · 0 unrepaired OVERFIT · 0 HARD_FAIL · regression pool green · exact source evidence
emitted · impact path available or clearly bounded · outputs REVIEW_ONLY until human approval.

## Stop conditions (both chains)
Any OVERFIT/HARD_FAIL/noisy advance · pre-freeze key exposure · frozen-file drift · production wiring · tuning to anchor
function names · live-bounty-looking candidate · regression red.

---

## Chain 1 — Access Control / Authorization / Caller Surface
**Config:** `config/research_modules/access_control_chain_draft.json`.
**Phase sequence (proposed, mirrors value-flow):**
- **A0** no-code taxonomy + anchors. Anchors (already-contaminated): Phi `H-05` exposed `_removeCredIdPerAddress` /
  `_addCredIdPerAddress` (missing access control), Phi `H-04`/`H-07` unrestricted `updateArtSettings`. Negatives:
  intentionally-permissionless actions (e.g. open `deposit`/`claim` by design), benign public views.
- **A1** research-only detector (caller-surface + missing/wrong-auth + protected-sibling comparand).
- **A2** contaminated diagnostics (anchors + negatives + value-flow regression pool must stay green).
- **A3** fresh blind batch (architecture-distinct, freeze-before-findings).
- **A4+** stop-on-OVERFIT → repair-proven-class → re-batch.
**Strong evidence / reject:** see config (privileged mutation + reachable + missing/wrong check + protected sibling +
no by-design reason + downstream authority/value effect; reject views/permissionless-by-design/naming-only).
**Eval subjects:** anchors from Phi (contaminated); fresh subjects TBD at the fresh-batch phase (stop-and-approve, never
a future-blind value-flow benchmark). **Likely FP families:** by-design-public actions, owner-trusted setters, init-only.

## Chain 2 — Signature Replay / Permit / Domain Separation / Nonce Integrity
**Config:** `config/research_modules/signature_replay_chain_draft.json`.
**Phase sequence (proposed):**
- **S0** no-code taxonomy + anchors. Anchors (already-contaminated): Phi `H-01` `signatureClaim` replay, Phi `H-02`
  `createArt` replay. Negatives: a correctly-built EIP-712 permit (nonce consumed + deadline + domain with chainId +
  verifyingContract), e.g. a Permit2-style path (reuse `project_permit_asset_binding_prototype` learnings).
- **S1** research-only detector (recovered-signer + signed-field inventory + nonce-consume + domain-completeness +
  reachable-replay + state-effect).
- **S2** contaminated diagnostics (anchors + negatives + regression pool green).
- **S3** fresh blind batch.
- **S4+** stop-on-OVERFIT → repair-proven-class → re-batch.
**Strong evidence / reject:** see config (signer recovered + missing nonce/domain/deadline/critical-field OR nonce not
consumed + reachable replay + value/authority/claim/approval state change + signed-field proof + no harmless reason;
reject correct-nonce/correct-domain/deadline-enforced/event-only/login-only/test-mock).
**Eval subjects:** anchors from Phi; fresh TBD at fresh-batch. **Likely FP families:** off-chain-attestation signatures,
correctly-implemented EIP-712/Permit2, event-only sig usage.

## Regression strategy (both chains)
Each chain keeps its own anchor+repaired-class regression pool AND must not regress the **value-flow** regression suite
(the chains share the corpus). A combined research-regression run (value-flow `run_p52.py` + each chain's pool) gates any
phase's trust. Stop conditions above apply.

## Fresh-blind strategy
Same as the value-flow arc: source-only clone → verify scope/local Solidity → freeze source+engine → run → freeze
candidates → THEN open findings → score → adjudicate every advance from source first (genuine vs OVERFIT). Subjects must
be uncontaminated, architecture-distinct, not in the fresh pool, not future-blind value-flow benchmarks; **stop-and-approve
before cloning** (human sign-off), as in P44/P48/P51/P53.

## Sequencing recommendation
Build **Access-Control first** (highest out-of-charter frequency, simplest source-local signal), then **Signature-Replay**
(reuses permit/Permit2 prior work). Each is a multi-phase arc; do not start the second until the first reaches its
fresh-blind phase or is explicitly parked. No promotion for either until the promotion criteria are met.
