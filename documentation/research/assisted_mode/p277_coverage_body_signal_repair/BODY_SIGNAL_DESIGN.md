# P277 — BODY_SIGNAL_DESIGN

## Why (P276 finding)
advisory_surfaced **68.1%** → class_routed **39.6%**: the system sees the locus but the router doesn't recognize the
award class. Root cause: class signals came from locus/function/contract/template **name tokens** only. Many awards'
class lives in the **mechanism body** (oracle issue inside a generic `update`; external-integration inside `settle`;
front-run inside `fill`/`callback`).

## What is now scanned
The router reads class signals from two tiers:
1. **Locus tier** (unchanged): locus/function/contract names + explicit `signals` + `templates`.
2. **Body tier** (new): an **allow-listed** set of generated-mechanism fields — `mechanism_summary`, `attacker_action`,
   `expected_value_delta`, `victim_gainer_hypothesis`, `affected_state_assets_permissions`, `invariant`,
   `falsification_question`/`falsifier`, `completion_note`, `evidence`, `mechanism_body`, `protocol_comparand_hint`,
   `source_backed_trigger` — scanned at top level AND inside each `mechanisms[]`/`generated_mechanisms[]` dict.

## How body affects the score (add weight, NEVER blindly override)
- Locus class = argmax of locus keyword hits (the primary classifier, exactly as pre-P277).
- **If locus has a class** (locus_hits>0): KEEP it. Body only **reinforces strength** when it agrees with that same
  class (so a body-confirmed class scores higher for the recall/`min_signal` gate). Body never flips a confident
  locus class.
- **If locus is blank** (UNKNOWN_OTHER, locus_hits==0): body MAY **assign** the class — the recall lift, a class
  hiding in the body that the name missed. This is the only case body changes the class (`body_changed_decision`).
- Body per-class contribution is **capped** (`body_signal_cap_per_class`) so verbose natural-language body text cannot
  swamp/reshuffle classification.

## Award-text hard-coding prevented
Body fields are an **allowlist**; an explicit **denylist** (`award_title`, `title`, `award_body`, `reveal`, `scoring`,
`ak_title`, `ak_id`, `issue_id`, `answer_key`, `public_finding`, …) is never read even if present. No contest names, no
award titles, no scoring labels enter the signal path. (Tested.)

## FP risk + anti-drama
Plausibility is unchanged: a body-elevated class still needs `impact_supported != false`, not REFUTE_FIRST, no
infeasible blocker, and recall_delta-or-strength≥min_signal. Anti-monoculture round-robin + guard unchanged. The strict
late gate is untouched, so severe concluded/reportable FP stays 0.
