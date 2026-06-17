# P147 — Limitations

1. **Intent-dependent (the main caveat).** `UserEscrow.transferOut`'s `receiver != destination` path is documented
   as "additional protection" (NatSpec). The runtime PoC proves the **mechanism** (escrow redirectable to an
   unrelated max-allowance receiver; allowance never reduced) but **not** that it is a vulnerability vs intended
   flexibility — that is a human severity/validity decision.
2. **Mechanism proven, not severity/magnitude.** Real loss depends on whether destinations grant unrelated
   infinite allowances and whether auth can be abused (the NatSpec's stated threat model is "compromised auth").
3. **Mock ERC20.** A standard mock (max allowance non-decrementing, matching real ERC20s) — magnitudes are
   illustrative; the recipient-resolution divergence is the point.
4. **Corrected reference is a control**, not a patched production contract (`receiver == destination`).
5. **duplicate_unknown ≠ novel.** No local answer key; matches a recognized finding class; no novelty/award claim.
6. **Build deps fetched from network** (forge-std) — re-runnable via the documented clone.
7. **Not submission-ready.** `submission_ready=false`; human + PoC review mandatory.
