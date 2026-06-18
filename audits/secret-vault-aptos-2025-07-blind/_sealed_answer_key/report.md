# Secret Vault on Aptos (CodeHawks 2025-07) — Awarded Findings (revealed at adjudication)

Source: https://codehawks.cyfrin.io/c/2025-07-secret-vault (2 High / 1 Medium, APTOS Move). Reconstructed at
REVEAL from CodeHawks public submission pages (titles not on the results summary). Titles only.

## High Risk Findings
- H-01 | Global Resource Exposure Leading to Confidential Data Leakage — secret stored in plaintext in Move global storage is publicly readable
- H-02 | Broken access control on secret retrieval/storage — owner check via a spoofable address param instead of a verified signer

## Medium Risk Findings
- M-01 | set_secret missing owner authorization / no update path (move_to aborts on second set)
