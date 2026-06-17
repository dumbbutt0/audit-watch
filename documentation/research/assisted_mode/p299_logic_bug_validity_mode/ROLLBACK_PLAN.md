# P299 — ROLLBACK_PLAN

1. Revert `scripts/research/executed_poc_verifier.py` to sha256[:16] `a1280b2a01fbe207` (remove the additive
   logic_differential branch + the validity_confirmed/logic_verified/validity_mode fields).
2. Revert the verifier-hash pin bump (1a005811→a1280b2a) in test_p294/295/296/297/298.
3. Delete `pocs/p299/`, `tests/research/test_p299_logic_bug_validity_mode.py`, and this docs dir.
The exploit track, P298 outputs, answer keys, contest source, and forbidden 5 are untouched. The change is purely
additive (field-gated), so rollback restores the exact pre-P299 behavior.
