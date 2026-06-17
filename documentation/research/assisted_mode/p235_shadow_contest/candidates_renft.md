# P235 — reNFT blind candidate set (deep-trace output, pre-reveal)

> Generated BLIND from source only (12 in-scope files + supporting libraries). Answer key / bot reports NOT
> opened. ICE scored independently. This is the raw recall artifact; the frozen + selected set lives in
> FROZEN_CANDIDATES.md.

Architecture: collateral-free NFT rentals. Lender's NFT is escrowed into a **Gnosis Safe** the renter co-owns; a
**Guard** (selector blocklist) prevents the renter from transferring/approving the rented NFT out; the **Stop**
policy (an enabled Safe *module*) reclaims the NFT to the lender at expiry; **Create** is a Seaport **zone** that
validates rental orders; **PaymentEscrow** holds rental payments. Default "Kernel/modules/policies" framework.

Core invariants: (I1) a rented NFT cannot leave the renter's safe until the rental is stopped; (I2) the lender can
always reclaim the NFT at/after expiry; (I3) payments settle pro-rata/in-full correctly and only protocol fees are
skimmable.

| ID | Title | I | C | E | Class |
|---|---|---|---|---|---|
| RENFT-01 | Guard `disableModule` checks wrong calldata arg → renter removes Stop module → reclaim bricked | High | High | Permissionless¹ | **HIGH_SIGNAL** |
| RENFT-02 | Guard skips ALL transfer/module protections when a hook is active for the target | High | Medium | Conditional(admin hook) | MEDIUM_SIGNAL |
| RENFT-03 | Guard delegatecall bypass via any whitelisted delegate (full guard escape) | High | High | Conditional(admin delegate) | MEDIUM_SIGNAL |
| RENFT-04 | Guard selector-blocklist lets renter call non-transfer fns on rented NFT (burn/claim/consume) | Medium | High | Permissionless² | MEDIUM_SIGNAL |
| RENFT-05 | CREATE_SIGNER payload has no nonce & not bound to seaport orderHash → protocol-sig replay | Medium | Medium | Permissionless | MEDIUM_SIGNAL |
| RENFT-06 | EIP-712 domain separator immutable; cached chainId unused → cross-fork sig replay | Low | High | Conditional(fork) | LOW_SIGNAL |
| RENFT-07 | `rentalOrderTypeHash` uses abi.encode not encodePacked → non-standard EIP-712 (self-consistent) | Low | High | n/a | LOW_SIGNAL |
| RENFT-08 | Factory safe-deploy salt from global counter → safe address not pre-computable / front-run shift | Low | Medium | Permissionless | LOW_SIGNAL |
| RENFT-09 | Accumulator hand-rolled memory: fragile "no alloc between insert/convert" invariant | Info | Medium | n/a | LOW_SIGNAL |
| RENFT-10 | Stop reclaim/settle/hooks run BEFORE order-hash existence check (validation-last / CEI) | Info | High | n/a | LOW_SIGNAL |

¹ renter is a normal safe owner (no privilege); precondition = ≥1 whitelisted extension exists (the feature's purpose).
² token-dependent (rented token must expose a damaging non-transfer function).

---

## RENFT-01 — Guard `disableModule` validates `prevModule`, not the module being disabled  (FLAGSHIP)
**Files:** `policies/Guard.sol:255-266` (`_checkTransaction` disableModule branch), `libraries/RentalConstants.sol:57-62`.
**Mechanism.** `disableModule(address prevModule, address module)` ABI-encodes `prevModule` at calldata offset
`0x24` and `module` at `0x44`. The guard uses `gnosis_safe_disable_module_offset = 0x24`, so
`_revertNonWhitelistedExtension(extension)` inspects **prevModule**, never the module actually being removed.
(Verified: for `bytes memory data`, `mload(add(data,0x24))` = content bytes [4:36] = arg1 = prevModule; module is at
`mload(add(data,0x44))`.) Contrast `enableModule(address module)` whose single arg legitimately sits at `0x24`.
**Exploit path (permissionless, renter = safe owner, threshold 1).**
1. Renter `enableModule(E)` where `E` is any admin-whitelisted extension → guard reads module=E (offset correct),
   `whitelistedExtensions[E]==true` → allowed. Safe linked-list becomes `SENTINEL → E → Stop → SENTINEL`.
2. Renter `disableModule(E, Stop)`. Gnosis requires `modules[E]==Stop` ✓. Guard reads prevModule=E,
   `whitelistedExtensions[E]==true` → **allowed**. Safe removes the **Stop** module.
3. `Stop.stopRent(order)` → `_reclaimRentedItems` → `safe.execTransactionFromModule(...)` reverts (Stop no longer an
   enabled module, GS104) → stopRent reverts permanently.
**Impact.** Invariant I2 broken: lender can NEVER reclaim the NFT, and the escrowed payment is stuck (settlePayment
never runs). The rented NFT is permanently locked in the renter's safe; lender suffers total loss of the lent asset
and of the rental payment. (Renter cannot extract either — guard still blocks transfers — so it is a permanent
asset-lock/griefing rather than direct theft, but the lender's loss is total and irreversible.) **High.**
**ICE:** I=High · C=High (offset math verified statically) · E=Permissionless (precondition ≥1 whitelisted ext).
**PoC plan:** real Guard + Safe + Stop module; enable a whitelisted ext, disable Stop through it, assert Stop no
longer a module and a subsequent module-tx reverts. (Harness in pocs/p235.)

## RENFT-02 — Hook path bypasses the selector blocklist entirely
**File:** `Guard.sol:333-344`. When `STORE.contractToHook(to)!=0 && hookOnTransaction(hook)`, only
`_forwardToHook` runs; `_checkTransaction` (which blocks transfer/approve/setApprovalForAll/setGuard/enable-disable
module) is skipped. Any target with an active hook loses all built-in protections — the hook must re-implement them.
A permissive or narrowly-scoped hook registered for a rented token contract would let the rented asset be moved or
re-approved out. Admin-config dependent (hooks are admin-gated), so Medium confidence / design fragility.

## RENFT-03 — Whitelisted delegatecall = full guard escape
**File:** `Guard.sol:322-326`; Factory NatSpec `Factory.sol:113-118` explicitly flags this assumption. DelegateCall
is permitted to any `whitelistedDelegates[to]`; inside it the safe executes arbitrary code in its own context
(including `setGuard(0)` and transferring the rented NFT), and the guard only inspects the outer delegatecall
selector. If any delegate that can move assets/alter the guard is whitelisted, I1 fully breaks. Conditional on admin
whitelist (acknowledged design assumption) → Medium.

## RENFT-04 — Renter can call damaging non-transfer functions on the rented NFT
**File:** `Guard.sol:195-293`. The blocklist only covers transfer/approval/module selectors. A renter (safe owns the
NFT) can call `burn`, reward `claim`, governance `vote`, or game "consume/level" functions on the rented token —
destroying or degrading the lender's asset or siphoning token-bound value. Token-dependent → Medium.

## RENFT-05 — Protocol-signer payload replay (no nonce, not bound to seaport order)
**File:** `packages/Signer.sol:248-262`, `policies/Create.sol:733-775`. `RentPayload` = {fulfillment.recipient,
metadata, expiration, intendedFulfiller}; no nonce, and `_RENT_PAYLOAD_TYPEHASH` omits the seaport orderHash. The
CREATE_SIGNER signature therefore authorizes *any* seaport order with matching zoneHash+fulfiller until expiry →
reuse across orders. Weakens the authorization gate. Medium.

## RENFT-06 / 07 / 08 / 09 / 10 — see table. Low/Info: cross-fork domain-separator replay; non-standard
typehash encoding (self-consistent, not exploitable); non-pre-computable safe address from global salt counter;
fragile hand-rolled accumulator memory invariant; validation-last ordering in Stop (currently atomic-safe).

---
### Specialist-lens coverage (recall instrument)
Manual deep-read of all 12 in-scope files reasoning across the production specialist lenses:
access_control (Kernel roles/policies, Admin, permissioned setters — clean), logic (order lifecycle, settlement),
reentrancy (settle/reclaim ordering — mitigated), dos/griefing (RENFT-01), arithmetic (pro-rata rounding — ok),
signature/replay (RENFT-05/06/07), token_integration (RENFT-04), upgrade/proxy (Proxiable/onlyByProxy — clean).
Out of scope: `examples/**` (demo hooks/upgrades), `lib/**`, `test/**`.
