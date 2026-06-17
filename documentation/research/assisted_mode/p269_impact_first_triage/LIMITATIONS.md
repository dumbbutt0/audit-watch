# P269 — LIMITATIONS

1. **Routing, not recovery.** "SELECT" means *routed into the PoC path*; it does not prove exact recovery follows.
   Whether the heavy/partial harness then confirms the awarded mechanism is the job of a fresh full-path run (P270).
   P269 fixes the *de-scope* (the P268 failure), not the downstream PoC outcome.

2. **Garbage-in.** The dimension signals (impact_class, impact_supported, feasibility_blockers, recall_delta) are
   operator-assigned. A mis-scored input — a true slashing bug mislabeled `griefing_minor`, or unsupported drama
   marked `impact_supported=true` — misleads the policy. It formalizes and enforces "impact over ease"; it does not
   independently verify the impact behind each signal.

3. **partial_runtime_plausible is operator-asserted.** The PARTIAL vs MANUAL split depends on the operator's
   `partial_runtime_plausible` flag; the policy does not itself judge whether a partial runtime is actually
   constructible.

4. **Infeasibility boundary is policy, not proof.** Harness-weight blockers (beacon/slashing/snapshot/fork) are
   treated as feasible-but-heavy by config; a genuinely intractable harness mislabeled as harness-weight would be
   routed and then fail at PoC time. The four `infeasible_blockers` are a coarse gate.

5. **Backtest necessary-not-sufficient.** Fixtures are hand-encoded from already-scored frozen artifacts, so the
   policy is scored on impact structures I summarized. The decisive proof is P270 (fresh run, dimensions assigned
   blind pre-reveal).

6. **Budget heuristic.** `poc_budget=4` + subsystem-clustering is a reasonable default, not tuned against a large
   labeled set. With many high-impact subsystems, budget choice matters; it is config-exposed for later calibration
   (which must stay answer-key-free).

7. **No severity / no authority.** Outputs are advisory (`ADVISORY_TRIAGE_DECISION`, all promotion flags false),
   enforced by the guard. That is a containment guarantee, not a claim the impact rankings are correct.
