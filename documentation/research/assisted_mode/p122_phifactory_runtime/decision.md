# P122 — Decision: PhiFactory.claim (NOVEL candidate)

## Terminal state: **KILLED_RUNTIME** (high-impact) + a runtime-confirmed low-impact fee-binding observation

Runtime decided. The harness refuted the high-impact attacker hypotheses with executed assertions, and separately
confirmed a bounded/conditional fee-binding behavior — both executed, not source-only.

| KILLED condition (spec) — high-impact | Evidence (runtime) |
|---|---|
| entitlement cannot be forged | Case A: a `claim` with an invalid signer signature reverts (`AddressNotSigned`) — `minter_` cannot be claimed-for without a valid `phiSignerAddress` signature (PASS). |
| no over-claim past the guards | Case E: minting up to `maxSupply` then one more reverts (`OverMaxAllowedToMint`); the time-window / `quantity>0` guards apply too (PASS). |
| normal flow is clean | Case B: exact-fee claim splits `protocolFee` → destination and the remainder → the art contract; no excess stuck (PASS). |

**High-impact verdict:** a permissionless caller cannot spoof the minter, mint without a valid signer entitlement,
or over-claim past the per-art caps → **KILLED_RUNTIME**. The trusted `phiSignerAddress` (phi's backend) gates who
may mint; the cap/window guards bound how much.

## Runtime-confirmed observation (recorded, NOT promoted)
The `claim` wrapper forwards a *computed* `mintFee` (not the caller's `msg.value`) via an external self-call, so:
- **Case C** — overpayment to `claim` leaves the excess **stuck** in the factory (no refund on the wrapper path),
  inconsistent with the DIRECT `signatureClaim`/`merkleClaim` path which refunds `etherValue_ - mintFee`.
- **Case D** — underpayment (`msg.value = 0`) reverts on an empty factory but **succeeds drawing the `mintFee` from
  the factory's standing balance** when funds are present (themselves from a prior overpayer).

This is real and runtime-confirmed, but **bounded and conditional**: it requires standing funds (a prior overpayer's
stuck excess) AND a valid signer entitlement, and the `mintFee` still flows to the protocol/art. It is **not** an
unconditional fund-theft and **not** an unauthorized mint. Per the hard stops, **no severity is assigned** (human-owned);
it is recorded as an observation and not promoted — analogous to P120's balanceOf misattribution and P121's
by-design geometric drain.

## Scope / honesty notes
- The trusted `phiSignerAddress` is taken as honest (phi's backend signer); "holding a valid signature" = being an
  authorized minter, not an attacker capability.
- HARNESS_COMPLEX but BUILT (UUPS proxy + signature-gated `createArt` + LibClone of a mock PhiNFT1155 + LibZip claim).
- **No severity assigned**, no report, no submission package, no READY state, no production wiring (hard stops).

## Hard-stop self-check
- KILLED_RUNTIME (and the fee-binding observation) claimed only with passing runtime tests (Cases A–E all PASS, executed). ✓
- No source-only reasoning used as runtime proof — guards/fees/balances are executed assertions. ✓
- No severity / report / submission / READY token; no production wiring. ✓
- phi `src/` **unmutated** — `PhiFactory.sol` (sha d703528e) imported via remapping; the harness lives only in the
  standalone `/tmp/p122-phifactory-harness/` project. ✓
