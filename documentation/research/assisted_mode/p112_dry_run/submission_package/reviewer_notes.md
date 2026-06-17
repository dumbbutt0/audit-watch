# Reviewer notes (INTERNAL)

_Assisted-mode caveat: this candidate was prepared by an assisted research workflow; a human must own scope, duplicate, program severity tier, and the submit decision. Nothing here is submitted._

- Why real: the exploit reproduces on a Fraxtal fork (intended feeBps 100 → adopted 1); the minimal guard makes the migration revert on the attacker pair while a clean migration still succeeds.
- Why Medium: bounded to lost swap-fee revenue + attacker-controlled migration price; no direct theft of user principal.
- What to run: the documented `forge test` command on the pinned commit; then the patch regression; restore source and verify the hash.
