# INS-002 — topUp() (documented governance treasury-seeding path) is unreachable dead code; the fund can only be seeded by the liquidation-fee skim

- **Severity (recommended):** Low
- **Category (HackenProof VRT):** Business Logic Errors
- **Confidence:** Confirmed
- **ICE:** Impact=Low · Confidence=Confirmed · Exploitability=Privileged
- **Location(s):** `contracts/insurance/InsuranceFundUtils.sol:139-167`
- **Vulnerable files (bundled in `sources/`):** `InsuranceFundUtils.sol`, `InsuranceFundUtilsTest.sol`

## Description

InsuranceFundUtils.topUp (InsuranceFundUtils.sol:139-167) is declared `internal` and is documented as the 'Governance-initiated reserve top-up from treasury'. A repo-wide search finds no production caller; the only reference is the external test wrapper InsuranceFundUtilsTest.topUp (test/InsuranceFundUtilsTest.sol:43-53) and the event helper. No handler, router, or Config function exposes it, and being `internal` it cannot be reached cross-contract anyway. Therefore the documented manual/treasury seeding capability does not exist on-chain: the InsuranceVault can only ever be funded by the per-close LIQUIDATION_FEE_INSURANCE_FACTOR slice deposited from MarketToken (deposit(), InsuranceFundUtils.sol:98-131, called from _distributeLiquidationShares). Secondary latent concern if topUp is ever wired: it records the received amount via vault.recordTransferIn(token) (which snaps tokenBalances to current balanceOf) and increments the bucket by `amount`; because deposit() also relies on recordTransferIn against the same cached tokenBalances, interleaving an out-of-band ERC20 transfer + topUp with the normal deposit flow could mis-attribute deltas if both are not strictly serialized, though the global reentrancy guard on the calling handlers currently serializes them.

## Impact

The protocol's intended treasury/governance seeding of the insurance fund is non-functional; reserves grow only slowly from fee skims, so the fund is likely undersized relative to the drawdowns it is meant to cover (compounding INS-001). Dead-code / spec-vs-implementation divergence.

## Attack path (Intent / Technique / Evasion)

- **Intent:** No direct attacker gain; this is a missing-capability / dead-code defect that leaves the fund chronically under-capitalized.
- **Technique:** n/a — the function is simply unreachable in production; the documented capability cannot be invoked.
- **Evasion:** Developer documented and unit-tested a governance top-up, but never exposed it through any controller-roled handler or Config entrypoint and left it `internal`, so the audited behavior is not the deployed behavior.

## Reachability / follow-up

Privileged
