# P219 — ZETA vs H5 EVIDENCE DIFF (after extraction improvements)

Per-section parity vs the H5 checklist. "present" = artifact-backed value; "explicit-unknown" = slot rendered as
unknown/NEEDS_HARNESS (acceptable parity); "weak" = generic only.

## Focus candidates
### ZETA-04 (=H-13, NEEDS_HARNESS)
| section | before P219 | after P219 | source | rerun can populate? |
|---|---|---|---|---|
| mechanism | present | present | merged.description | n/a |
| function_map | present | present | register | n/a |
| attacker_model + reachability | weak (no verdict) | **+reachability "uncertain (confirm gate)"** | confirm | partly (a harness would confirm) |
| exploit_steps | present | present | merged.ice_chain | n/a |
| defense_map | present | present | triage follow_up_packet | n/a |
| PoC actual/expected/control | missing | **explicit-unknown** (no executed PoC) | L3 (empty) | yes — build harness |
| impact who_loses/asset | missing | asset present; who_loses explicit-unknown | L3 | yes — harness/severity memo |
| red_flags | 3 | **5, each citing evidence** | derived | n/a |
| novelty | unknown | unknown | none | human only |

### ZETA-07 (executed, L3 PASS) — full depth
PoC actual/expected/control/value-delta, who_loses, asset, reachability all **present** (L3 executed record). 8/8 depth.

### ZETA-11 (≈H-10, NEEDS_HARNESS)
reachability + expected/control (L3 planned control) + asset present; actual/value-delta explicit-unknown (no harness).

## All 12 — depth fields populated (of 8 H5-parity depth dims)
ZETA-01 5/8 · 02 2/8 · 03 5/8 · 04 3/8 · 05 3/8 · 06 3/8 · **07 8/8** · 08 5/8 · 09 2/8 · 10 5/8 · 11 5/8 · 12 2/8.
Lower scores = NEEDS_HARNESS / no-L3-record candidates (ZETA-02/09/12) — explicit, not invented.
