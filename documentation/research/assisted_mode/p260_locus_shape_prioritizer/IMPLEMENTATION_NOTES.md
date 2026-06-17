# P260 — IMPLEMENTATION_NOTES
- Deterministic; no LLM-in-loop; no answer keys. Scores from manifest fields + checkpoint family hits + function-
  name/signature keyword buckets. Optional --with-source brace-matched body scan (reuses the _function_body
  approach from scripts/state_transition_checkpoint_audit.py) only to confirm markers; default off.
- Mechanism hypotheses are interrogative scaffolds (questions + matched-signal context), mirroring the checkpoint
  "signal, don't submit" boundary. Deep mechanism reasoning stays downstream (operator/LLM + B/C ranking + 5 ops).
- Self-tripwire: runtime assert every emitted hypothesis has severity None and concluded False.
- Bounded output (top-N) prevents noise flooding; low-signal loci (no checkpoint hit AND attack_surface<3) dropped;
  loci with no routed template dropped.
- UN-WIRED: no import from run_pipeline / agent_policy / routing / dashboard; nothing imports this module.
