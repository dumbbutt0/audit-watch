# P280 — VERDICT

## Verdict: **D — READY_LABEL_TOO_NOISY**

### Why D
All 3 auto-derived READY candidates are **READY_OVERCLAIMED**: their PoCs (runnable, Tier C) show the auto mechanism is
refuted or mis-framed —
- `V3Vault.transform` — PASS_REFUTED (inline owner/approval guard the manifest `modifiers=[]` missed).
- `IBeanstalk.cancelPodListing` — PASS_REFUTED (inline ownership `require` in `LibMarket._cancelPodListing`).
- `L2Governor.execute` — BENIGN_BY_DESIGN (permissionless execute is intended) + SAME_AREA_WRONG_MECHANISM (the real
  bug is a state-machine anomaly: Defeated/Expired proposals executable — which the ACCESS framing missed).
**0 PASS_SUPPORTED.** The READY label currently overclaims because the deriver's auth signal (manifest `modifiers`) is
blind to inline guards and state-machine semantics. → D.

### The honest positives (the sweep PROCESS worked)
- The PoCs are **runnable** and the auto evidence packets were **sufficient to BUILD** all 3 (attacker_path + assertion
  pointed straight at what to test) → 2 clean PASS_REFUTED + 1 benign/same-area, **0 hallucinated core evidence, 0
  placeholder leaks, 0 severe FP**. So this is not noise-from-nothing; it is a precise, fixable miscalibration.

### Not A / B / C / E
- Not **A** (POC_SWEEP_PASS): declaring a pass when every READY mechanism was refuted/mis-framed would mislead — the
  READY label was not trustworthy as a bug-claim.
- Not **B** (≥1 useful PoC, readiness "needs refinement"): understates that **all 3** overclaimed via one systemic
  blind spot — "too noisy" is the accurate signal.
- Not **C** (can't convert): they converted fine — the evidence was sufficient to build; the *claims* were wrong.
- Not **E**: research-only; P279 deriver/gate + all frozen modules + forbidden 5 byte-identical; active audit unchanged.

### Next (specific, pre-identified)
**Inline-guard detection (D1)** + **value-flow evidence derivation (D3)** as the next deriver repair — the manifest
`modifiers` field is not a sufficient auth signal; until D1 lands, auto-READY should not feed a PoC sweep. Then re-map,
then a fresh blind target. Production authority WITHHELD.
