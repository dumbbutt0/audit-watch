# P216 — FINISHED BUG PARITY (ZETA-04 vs Abracadabra H5)

Model: the finished **Abracadabra H5** runtime finding (`output_research/value_provenance_eval/runtime_status.jsonl`),
which renders the full read-only verifier card. Compared one generated P215 record (**ZETA-04**, the H-13 mechanism HIT)
against it. Both cards are produced by the **same** `finding_detail.build_verifier_evidence()` builder, so the
structure is identical by construction; content differs (H5 is a runtime-confirmed finding with executed evidence;
ZETA-04 is a source-confirmed mechanism still NEEDS_HARNESS).

| Card section | Abracadabra H5 | ZETA-04 (generated) | structural parity |
|--------------|----------------|---------------------|-------------------|
| report_summary (bug/contracts/functions/attacker/impact/severity/novelty/boundary) | populated | populated (severity=Medium recorded) | ✅ |
| mechanism (one_sentence/root_cause/refutation) | populated | one_sentence populated; root_cause from mechanism_correctness | ✅ |
| function_map | populated | derived from contract.function | ✅ |
| attacker_model | populated | attacker/controls (some unknown) | ✅ |
| exploit_steps | from harness doc | MISSING_EVIDENCE (no harness) — explicit | ✅ (explicit unknown) |
| defense_map | populated | unknown/empty — explicit | ✅ |
| poc_verification | executed (real contract, control) | NEEDS_HARNESS; command/result unknown | ✅ |
| impact_severity | populated | impact + severity_recommendation=Medium | ✅ |
| intent_scope_operator | p155/p156 gates | unknown where not recorded | ✅ |
| novelty_duplicate | populated | unknown/HUMAN_PENDING | ✅ |
| conversion | RUNTIME_CONFIRMED/booleans | CLEAN_HIT + readiness booleans | ✅ |
| main_blocker | none (confirmed) | L3 readiness blocker | ✅ |
| final_triage | recorded | from triage status | ✅ |
| red_flags | p155-gate-derived | computed | ✅ |
| evidence_backup | artifacts | source_refs / artifact_links | ✅ |

## Safety-semantics parity (must match exactly)
| Flag | H5 | ZETA-04 |
|------|----|---------|
| `research_only` | true | true |
| `routing_allowed` | false | false |
| `submission_ready` | false | false |
| browser computes severity | no | no (`_sev_or_status` → recorded/HUMAN_PENDING) |
| submit/promote controls | none | none |
| `read_only_synced` | true | true |

**Verdict:** same structural completeness (15/15 sections) and identical safety semantics; content differs as expected.
Parity achieved.
