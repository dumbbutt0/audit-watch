# Scope boundary: ZK-circuit soundness & BitVM / Bitcoin-script (FLAG, never adjudicate)

This document is the authoritative statement of what the cross-language auditor **does not**
audit, and how it behaves at that boundary. It exists because real targets sit right on it
(e.g. the Code4rena `2025-08-solana-foundation` contest — Token-2022 confidential transfers +
the ZK ElGamal proof program), and the honest move is to declare the limit, not to manufacture
a recall number against code the architecture cannot credibly reason about.

## What is OUT of adjudication scope

The auditor delivers **application / program logic** auditing (Solidity contracts; Solana/Anchor
programs — account model, CPI, PDA, accounting, access control, DoS). The following are OUT:

1. **ZK-circuit soundness & cryptographic-proof systems** — ElGamal encryption, Pedersen
   commitments, sigma proofs, range proofs / Bulletproofs, proof generation & verification,
   confidential-transfer ciphertext arithmetic, R1CS/PLONK/Groth16 circuits. Verifying these
   requires cryptographic-protocol expertise (completeness/soundness/zero-knowledge, malleability,
   transcript/Fiat-Shamir binding) that this architecture's specialists do not encode.
2. **BitVM / Bitcoin-script & Bitcoin consensus-level constructions** — covenant emulation,
   script-based fraud proofs, BitVM circuit commitments. Specialized; flagged, never adjudicated.

These are distinct from things we DO cover that merely *touch* crypto: signature checks
(ECDSA/ed25519 `recover`/`verify` usage), nonce/replay logic, hash-commitment *usage* (we audit
whether a commitment is checked, not whether the hash is collision-resistant).

## Behavior at the boundary (FLAG, don't adjudicate)

- The Rust static adapter (`tools/static_analysis_rust.py`) sets **`zk_out_of_scope: true`** in
  `output/static.json` when it detects ZK/proof markers (`ElGamal`, `Pedersen`, `RangeProof`,
  `sigma_proof`, `zk-elgamal`, `ciphertext`, `confidential_transfer`, `proof_generation|extraction`),
  and writes a `zk_boundary_note` pointing here.
- A flagged finding is surfaced as **advisory / needs-specialist**: route to a human ZK
  cryptographer; the pipeline must NOT assign a soundness severity or claim a proof break.
- The recall lab must NOT ingest a ZK/circuit-soundness contest as an in-architecture eval target
  (it would produce a meaningless ~0 recall and contaminate the honest scoreboard). Such targets
  are recorded as *out-of-architecture* (see `project_crosslang_rust` memory, Verdict B note).

## Honest framing

This boundary is a feature, not a gap to paper over. Stating "we audit Solana program logic; we
do not adjudicate ZK-circuit soundness" is more useful — and more honest — than a fabricated pass
over proof code. When a contest is mixed (app logic + ZK), audit the app-logic surface fully and
hand the ZK surface to a specialist with the `zk_out_of_scope` flag as the handoff marker.
