# P298 — VERDICT

## A — BEANSTALK_EVAL_DELIVERED_ALL_THREE_AXES_AT_FP_ZERO

The eval delivered recall/precision vs the answer key + novelty per finding + executed-PoC validity, with ≥1 awarded
locus confirmed by a real PoC and confirmed-FP = 0.

### A-criteria — all met
- **Answer-key axis:** 81 public; recall_useful 0.42 (34/81), recall_any_touch 0.53; 12 platform_confirmed accepted;
  8 pipeline-only (read-only from eval2).
- **Novelty axis:** per-finding KB cosine sim; 0 novel / 44 known (all map to a known solodit class); immunefi MCP
  corroborates the confirmed loci's classes.
- **Validity axis:** 2 awarded loci **confirmed by executed PoC** (AC-001 replay, AC-003 unguarded sweep) at
  **confirmed-FP = 0**; 3 logic-bugs proven-by-test-but-setup_only (LG-001/PC-001/SN-001); 7 evidence-bundle
  needs_execution. The verifier (sole judge) overrode 3 builder "confirmed" claims — the judge-not-builder guard.
- Answer key + contest source unchanged (read-only); verifier + forbidden 5 byte-identical; symlink unchanged; both
  the kb-search and immunefi MCPs set up + verified live.

### Headline finding (actionable)
The stack recalls ~42% of the 81 public on this target and PROVES the attacker-exploit awarded bugs by execution at
FP=0. The binding limitation surfaced: the executed-PoC verifier is exploit-shaped and under-credits
logic/correctness/admin bugs — a **logic-bug validity mode** (passing differential test vs a corrected reference,
no attacker L1) is the next improvement and would convert LG-001/PC-001/SN-001 to clean confirmations.

### Next
Add the logic-bug validity mode; run the 7 needs_execution bundles as the next wave; extend the eval template to the
strict-eval corpus once answer keys are available. Submission stays human-gated.
