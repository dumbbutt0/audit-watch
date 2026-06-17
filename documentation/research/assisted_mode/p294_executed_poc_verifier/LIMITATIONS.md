# P294 — LIMITATIONS

- **Tier-C faithfulness, not full-contest compile.** The PoCs reproduce the bug-locus control-flow verbatim with
  minimal mocks (forge-std only), the validated pattern from p286/p287/p290. They are not compiled against the full
  contest import closure; faithfulness is argued in EVIDENCE_AUDIT, not guaranteed by linking the real contracts.
  A future hook could compile against contest source / fork where tractable.
- **PoC generation is still the agent step.** This phase built the PoCs in-session (the `/poc` agent role). The
  verifier orchestrates locate→execute→parse→verdict; it does not yet auto-generate PoCs for arbitrary candidates.
  The "verification agent loop" (auto-build for every surfaced candidate) is the next phase.
- **Polarity is author-declared.** Exploit vs refutation comes from `poc_manifest.json`. A mislabeled manifest
  (calling a refutation an exploit) would mis-route — but the L1+L2+L3 + real-PASS requirement still blocks a safety
  test from confirming a non-bug (a refutation test does not assert an attacker gain).
- **Fork/RPC offline.** Default substrate is no-fork (forge-std mocks); fork PoCs need a live RPC in
  `config/rpc_endpoints.json`, which may be unavailable offline.
- **recall_open not yet wired.** The open-recall flow is demonstrated by the proof driver over a candidate list; it
  is NOT yet integrated into the eval/classify path (deferred to keep this phase zero-cascade).
- **Three proof cases.** Strong (2 awarded confirmed incl. a net-new full-loop build + 1 refused) but not the whole
  corpus; corpus-wide open-recall measurement toward ~100% is the explicit next phase.
