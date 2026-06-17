# P219 — ABRACADABRA H5 GOLD STANDARD (field model)

Source: `output_research/value_provenance_eval/runtime_status.jsonl` (item H5-abracadabra-lockingrewards-boost),
rendered by `finding_detail.build_verifier_evidence`. The gold standard is **structural + evidence-source parity**, NOT
content/severity. "Good enough for human analysis" = the field is populated from a named artifact OR explicitly marked
unknown/blocked.

| H5 card field | populated? | source artifact (H5) | "good enough" bar for Zeta |
|---|---|---|---|
| report_summary (bug/contracts/functions/attacker/impact/severity/novelty/boundary) | yes | runtime row + p155/p156 review | summary+contracts+functions present or explicit |
| one-sentence mechanism | yes | suspected_mechanism / divergence | merged.description |
| function_map (role/permission/why/location) | yes | source map (surface_function+target) | register surface + impact_class role |
| attacker_model + reachability_verdict | yes | runtime reachability + p155 gate2 | register attacker_model + confirm reachability_status |
| exploit_steps | yes | harness_design "Scenario" | merged.ice_chain.exploit_path |
| defense_map | yes | defense_map.md table | triage follow_up_packet / L3 control (recommended fix) |
| PoC verification: actual / expected / control / value-delta | yes | runtime harness (vulnerable_output/corrected_output/control_case/runtime_delta) | L3 record actual_delta/expected_delta_or_control/magnitude_basis — present iff executed/recorded |
| impact: who_loses / who_gains / asset / loss_type / bounds | yes | runtime + severity memo | L3 victim_or_protocol_loss / affected_asset_or_state / impact_class; who_gains unknown unless stated |
| intent/scope/operator | yes | p155 gate1/gate3 | register privileged⇒operator-dep / triage decision_reason |
| novelty/duplicate | yes | p156 external search | **unknown / HUMAN_PENDING** (no Zeta novelty artifact) |
| conversion_classification | yes | conversion_outcome | scorecard PRIMARY verdict (post-score) |
| main_blocker | yes | primary_blocker_if_not_reportable | L3 decide() blocker |
| final_triager_decision | yes | review report | triage status + decision_reason |
| red_flags | yes | p155 gates + facts | derived from recorded facts (attacker/L3/reachability), each citing evidence |
| evidence_backup | yes | docs + harness + runtime result + review | source_refs: register/merged/confirm/L3/harness/report-package/dry-run-queue |

Key: H5 is runtime-CONFIRMED so every PoC field is real. Zeta candidates are mostly NEEDS_HARNESS, so executed-PoC
fields are legitimately absent — parity means the SLOT is present and explicitly unknown, not fabricated.
