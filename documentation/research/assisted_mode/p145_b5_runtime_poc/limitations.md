# P145 — Limitations

1. **Mechanism proven, not severity/magnitude.** The PoC proves the wrong-recipient misdirection in the real
   `claim_many`. It does not quantify net protocol/user loss, which depends on how many AVM-managed tokenIds with
   expired non-permanent locks accrue rewards and the amounts involved — a human/program-context question.
2. **AVM-manager redistribution unknown.** Funds land at `ownerOf` (the AVM manager). Whether that manager later
   forwards them to original owners (making the loss recoverable) or retains/loses them is out of scope here.
3. **Mock VE/AVM/token.** VE point/balance/supply, AVM mapping, and the ERC20 are mocked to drive a deterministic
   nonzero claim and an AVM-managed expired-lock state; real Algebra/ve(3,3) state would change magnitudes, not
   the recipient-resolution divergence.
4. **`_claim` amount is synthetic.** Driven via funding + `checkpoint_token` + a 1-WEEK warp with `S<SUP`; the
   exact per-claim figure (1e18) is illustrative — the bug is independent of the amount (any nonzero amount on an
   AVM-managed expired-lock tokenId misdirects).
5. **Corrected reference is the sibling `claim`**, not a patched `claim_many`; the proof is the divergence between
   the two real sibling functions.
6. **Duplicate.** B5 is the known blackhole **M-04** — method validation, not a novel submission.
7. **Build deps fetched from network** (forge-std) — re-runnable via the documented clone.
