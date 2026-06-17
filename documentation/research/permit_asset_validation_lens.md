# Permit / Permit2 Asset-Validation Lens — Research Program

**Type:** research only. No detector, code, routing, gate, submission, or production integration was created.
This study assesses whether permit/Permit2 *asset-validation / authorization-drift / signature-reuse-via-execution-
indirection* bugs form a detector-worthy family (as `multicall_invariant` was assessed), and whether they can be
detected without excessive noise. It does **not** optimize for historical HITs or answer keys; every proposed
signal carries an explicit benefit **and** precision cost.

**Separation:** this is a brand-new lens. `multicall_invariant` is frozen/research-only and is **not** touched or
extended; no permit logic is added to it.

---

## 1. Executive Summary

Permit/Permit2 authorization bugs are a **real, recurring, high-value family** at the top end (a missing
"permitted token == protocol asset" check is a direct fund-loss path), but the family is **heterogeneous** and its
**most detectable** members are also its **lowest-severity** ones. From a grounded dataset of 15 public findings
(KB corpus + web-verified Code4rena/Sherlock issues + the in-repo Revert Lend anchor), three sub-shapes emerge:

1. **Asset/token mismatch** (high severity, fund loss) — rare in the corpus; the clean exemplar is Revert Lend
   `V3Vault` (permit token never checked == USDC). The bug is an **absent equality check**, often **cross-call**.
2. **Permit front-running / unused-allowance DoS** (mostly Medium) — high frequency, but a **generic, well-known
   pattern** (a `permit()` in the mempool can be replayed/consumed) that overlaps existing `signature-replay`
   coverage and is largely a UX/griefing class, not fund loss.
3. **Authorization drift / signature reuse via indirection** (Medium–High) — reuse after revocation, missing
   contract/domain binding, params not bound into the signed digest, recipient/`to` not signed (Permit2
   `SignatureTransfer`).

**Detection tension:** the highest-value sub-shape (asset mismatch) is **absence-based and contextual** — the
classic precision trap — while the easiest-to-detect sub-shape (front-running) is low-severity and already
partially covered. A *broad* "permit detector" would be noisy (permit usage is ubiquitous and usually safe). A
**narrow, data-flow, two-signal** detector targeting **Permit2 `permitTransferFrom`/`permitWitnessTransferFrom`
whose permitted-token / recipient / amount is not bound to a protocol-known value** is the only precision-viable
entry point.

**Verdict: MODERATE POTENTIAL DETECTOR FAMILY** — worth a narrowly-scoped, Permit2-asset-binding research
prototype with a frozen evaluation set; **not** a broad permit lens, and lower-priority than families with denser,
presence-based (not absence-based) signals.

---

## 2. Dataset

**Method (no fabrication):** grounded first in the repo's KB (`kb-search` MCP over the Solodit/Code4rena/Sherlock
corpus + `kb/patterns/signature-replay.json`), anchored on the in-repo Revert Lend finding, and supplemented with
read-only web search to confirm real report URLs + finding IDs for permit/Permit2-specific cases. Every row carries
a **verification** tag; nothing is invented.

**Verification legend:** `in-repo` (present in this repo + its eval report) · `web` (confirmed report URL/ID via
web search) · `kb` (returned by the repo's grounded KB with a source URL). Severities are as labeled by the source.

**Scope note:** rows tagged ⚠ are **boundary/adjacent** (meta-tx or bridge signatures) and are listed for
completeness but excluded from the in-scope frequency counts per the explicit out-of-scope rules (governance/
validator/bridge attestations, ECDSA bugs, AA, ERC2771, msg.value, multicall executor detection).

---

## 3. Finding Inventory (n = 15; 13 in-scope + 2 boundary)

| # | Protocol | Source | ID | Sev | Affected contract → fn | Permit type | Root cause | Exploit mechanism | Auth object | Asset | Attacker capability | Verif |
|--:|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Revert Lend (C4 2024-03) | code-423n4/2024-03-revert-lend-findings #368 | H-01 | High | `V3Vault` → `permit2.permitTransferFrom` (×3), `createWithPermit` | Permit2 SignatureTransfer | permitted token never asserted == vault asset (USDC) | sign a Permit2 for a worthless ERC-20; vault credits it as USDC → drain | Permit2 signed token/amount | USDC vs arbitrary ERC-20 | permissionless EOA | web/in-repo |
| 2 | Aave v3.3 (Sherlock 2025-01) | sherlock-audit/2025-01-aave-v3-3-judging #138 | M | Med | `Pool` → `supplyWithPermit` | ERC-2612 | permit signature validation can be bypassed in supplyWithPermit path | supply credited without a valid binding permit consumption | permit (owner→pool) | supplied asset | conditional | web |
| 3 | Oku (Sherlock 2024-11) | sherlock-audit/2024-11-oku-judging #54 | M | Med | permit-consuming entrypoint | ERC-2612 | external `permit()` not wrapped/try-caught | front-run the `permit()` → victim tx reverts (nonce used) → DoS | permit nonce | router asset | permissionless | web |
| 4 | Union Finance (Sherlock 2024-06) | sherlock-audit/2024-06-union-finance-update-2-judging #67 | M | Med | `stakeWithERC20Permit`, `repayBorrowWithERC20Permit` | ERC-2612 | permit + action not atomic against front-run | grief: replay signature on token, victim action reverts | permit nonce | stake/repay token | permissionless | web |
| 5 | Uniswap Permit2 (design) | github.com/Uniswap/permit2 #250 | design | n/a | `SignatureTransfer.permitTransferFrom` | Permit2 SignatureTransfer | recipient `to` is **not** in the signed data (only token/amount/nonce/deadline) | a leaked/mempool permit can be transferred to an attacker-chosen `to`; integrators must use witness | signed transfer | any token | front-runner | web |
| 6 | P2P.org (MixBytes) | mixbytes audits_public/P2P.org Lending Proxy | #4 | Med | `P2pLendingProxy.isValidSignature` | EIP-1271/custom | signature not bound to the contract instance | reuse the same signature across the user's other proxy instances | signed op | proxy assets | conditional | kb |
| 7 | Ondo Finance (C4 2023-01) | code4rena.com/reports/2023-01-ondo | M-04 | Med | `KYCRegistry.addKYCAddressViaSignature` | EIP-712 custom | signature stays valid after the authorization is revoked | replay the original sig to re-grant a revoked KYC status | KYC grant | n/a (authority) | conditional | kb |
| 8 | Harmonix Tokensale (Shieldify) | shieldify HarmonixFinance-TokenSale review | M-01 | Med | `_validatePermit` | EIP-712 custom | `permitSigner == address(0)` disables signature checks | forge arbitrary permits → bypass allocation access control | purchase permit | sale allocation | permissionless | kb |
| 9 | Ethena Labs (C4 2023-10) | code4rena.com/reports/2023-10-ethena | M-01 | Med | `StakedUSDe` → approvals path | ERC-20 approval | restriction not enforced on the approval/owner path | a restricted staker reuses an approval to move funds | allowance | sUSDe | conditional | kb |
| 10 | Beanstalk: The Finale (Codehawks 2024-05) | Cyfrin/2024-05-beanstalk-the-finale | H | High | `redeemDepositsAndInternalBalances` | EIP-712 custom | signed params not bound / not consumed | replay the same signed deposit set → inflate stalk/roots | signed redeem | deposits | conditional | kb |
| 11 | Rigor Protocol (C4 2022-08) | code4rena.com/reports/2022-08-rigor | H-01 | High | multiple (untyped signing) | custom | untyped data signing → no domain/function binding | reuse a signature across functions/projects/chains | signed op | project funds | conditional | kb |
| 12 | reNFT (C4 2024-01) | code4rena.com/reports/2024-01-renft | M-13 | Med | `RentPayload` flow | EIP-712 | payload uniqueness not enforced | replay a rental signature for multiple fulfillments | rental order | rent earnings | conditional | kb |
| 13 | SeaDrop (Spearbit) | spearbit Seadrop review | — | Med | `SeaDrop.mintSigned`/`mintAllowList` | EIP-712 + Merkle | minted units not tracked against the signature | replay sig/proof to mint beyond the wallet cap | mint auth | NFT supply | conditional | kb |
| 14 ⚠ | Rolla (C4 2022-03) | code4rena.com/reports/2022-03-rolla | H-04 | High | `EIP712MetaTransaction.executeMetaTransaction` | meta-tx | nonce not bumped on failed tx | replay a failed meta-tx | meta-tx | USDC | conditional | kb (boundary: meta-tx) |
| 15 ⚠ | Connext (Spearbit) | spearbit Connext review | — | Med | router exec on destination | bridge sig | router signed message reusable per transferId | replay router sig → over-provision liquidity | router auth | liquidity | conditional | kb (boundary: bridge) |

**Supporting class references (not counted as findings, used for taxonomy + safe patterns):** Trust Security
"Permission denied" (the canonical ERC-2612 permit-DoS class), Oxorio "What's wrong with ERC20Permit", and the
ChainSecurity Permit2 audit (safe-integration guidance).

---

## 4. Root Cause Taxonomy

Counts over the **13 in-scope** findings. (A finding may touch two categories; primary category used for the count.)

| Category | Freq | Severity dist | Exploitability | Common code pattern |
|---|--:|---|---|---|
| **token / asset mismatch** | 1 (#1) | High | permissionless, direct fund loss | `permit2.permitTransferFrom(permit, …)` then treat `permit.permitted.token` as the protocol asset with **no `== asset` assert** |
| **recipient / spender mismatch** | 1 (#5) | design (→ High when integrated wrong) | front-runner | Permit2 `permitTransferFrom` with `to` taken from calldata, not from signed data; no witness |
| **permit-validation bypass** | 2 (#2, #8) | Med | conditional / permissionless | `*WithPermit` that proceeds even when the permit is not validly bound (zero signer, swallowed failure) |
| **signature replay (front-run / DoS)** | 2 (#3, #4) | Med | permissionless | external `IERC20Permit.permit(...)` **not** wrapped in try/catch and **not** atomic with the action |
| **authorization widening / approval reuse** | 2 (#7, #9) | Med | conditional | signed authority (KYC/allowance) usable after revocation / on an unguarded path |
| **scope / params not bound (replay via indirection)** | 4 (#6, #10, #11, #13) | Med–High | conditional | signed digest omits contract address / chainId / consumed-marker / unique nonce |
| **delegated-execution drift** | 0 in corpus | — | — | (theoretical; the executor-side overlaps `multicall_invariant`, out of scope here) |
| **permit scope mismatch / approval reuse (pure)** | folded into above | — | — | — |
| **unknown** | 0 | — | — | — |

**Distribution headline:** only **1/13** is the namesake **asset mismatch** (but it's the only *High direct-drain*
case); **8/13** are replay/front-run/widening shapes that **overlap the existing `signature-replay` KB pattern** and
are **mostly Medium**. The detector's *unique* value therefore concentrates in the small, high-severity
asset/recipient-binding corner — not in the large, already-covered replay corner.

---

## 5. Authorization Model Analysis

Every permit/Permit2 flow signs an **authorization object** and later **consumes** it during execution. A bug is a
**divergence between what was signed and what is consumed** along five axes:

| Axis | Signed says | Execution consumes | Failure when unchecked |
|---|---|---|---|
| **who (owner/signer)** | owner = S | recovered signer | zero-signer / 1271 spoof (#8, #6) |
| **what (token/asset)** | token = T | protocol treats it as asset A | **asset mismatch (#1)** |
| **how much (amount)** | amount = X | pulls ≤ X | partial-fill / leftover-allowance reuse |
| **where (spender/recipient)** | spender = this; (to often **unsigned** in Permit2) | `to` from calldata | recipient hijack / front-run (#5) |
| **when/uniqueness (nonce/deadline/domain)** | nonce N, chain C, contract K | replay marker | replay across tx/chain/contract/fn (#6,#7,#10,#11,#13) |

The high-value bug class (#1) is an **identity check on the "what" axis that is simply absent**. The Permit2 design
note (#5) is a **"where" axis** gap that integrators must close with `permitWitnessTransferFrom`. These two axes —
**what** and **where** — are where a dedicated lens adds value beyond generic replay detection.

---

## 6. Common Validation Failures
- **Missing `permit.permitted.token == asset` assertion** before treating a Permit2 transfer as the protocol asset (#1).
- **Using `permitTransferFrom` with a caller-supplied `to`** instead of `permitWitnessTransferFrom` binding the recipient (#5).
- **Calling external `permit()` non-atomically / without try/catch**, so a front-run consumes the nonce and DoSes the action (#3, #4).
- **Accepting a permit when the signer config is degenerate** (zero address) or when validation can be skipped (#8, #2).
- **Signed digest omits a binding field** — contract address (#6), chainId (#11), a consumed-marker/unique nonce (#7, #10, #13).

## 7. Common Safe Patterns (the negative space — basis for precision)
- **Explicit asset equality:** `if (permit.permitted.token != asset) revert InvalidToken();` (the exact Revert Lend mitigation).
- **`permitWitnessTransferFrom`** with the recipient/intent bound into the witness (Permit2 recommended integration).
- **try/catch around external `permit()`** + proceeding on already-set allowance (defuses front-run DoS).
- **Consumed-marker / unique nonce / full EIP-712 domain** (chainId + verifyingContract) in the signed struct.
- **Pull-then-verify:** measure `balanceOf` delta of the *expected asset* rather than trusting the permit's token.

These safe patterns are the **suppression signals** any detector must encode to stay precise (their *presence*
clears a candidate).

---

## 8. Potential Detection Signals

| Signal | Rationale | Expected coverage | Expected precision | FP risk |
|---|---|---|---|---|
| **S1 — Permit2 transfer without asset-equality assert** (a `permitTransferFrom`/`permitWitnessTransferFrom` call where `permit.permitted.token` is never compared to a protocol-known asset var on the path) | directly models #1, the High fund-loss shape | low (rare shape) but high-value | **high if** the protocol has a single known `asset`/`token` storage var to compare against; lower in multi-asset routers | moderate — routers legitimately accept arbitrary tokens (must suppress when no single "expected asset" exists) |
| **S2 — `permitTransferFrom` with caller-supplied `to`** (recipient not from signed data / no witness) | models #5 recipient axis | medium | medium | high — many integrations set `to = address(this)` safely; needs taint that `to` is attacker-influenced |
| **S3 — external `permit()` not in try/catch and not atomic** | models #3/#4 front-run DoS | high (common) | low–medium | **high** — extremely common, mostly Medium; broad → noisy. Overlaps generic replay. |
| **S4 — signed struct missing a binding field** (no chainId / verifyingContract / consumed-marker in the EIP-712 typehash) | models #6/#10/#11/#13 | medium | medium | medium — overlaps the existing `signature-replay` pattern; risk of double-reporting |
| **S5 — `*WithPermit` proceeds without enforcing permit validity** (zero-signer / swallowed failure) | models #2/#8 | low | medium | medium |

**Two-signal framing (precision discipline):** the only signal with a *presence-based, protocol-specific* anchor
is **S1** (executor consumes Permit2 transfer **AND** a protocol "expected asset" exists **AND** no equality
assert). S3/S4 are absence-of-protection signals over ubiquitous code → inherently broad; they should **not** be
built as standalone detectors (they would flood and overlap `signature-replay`).

---

## 9. Candidate Detector Shapes (DESCRIBE ONLY — no implementation)

**Shape A — Permit2 asset-binding (S1-centric).** Flag a function that consumes a Permit2 `permitTransferFrom`/
`permitWitnessTransferFrom` (or ERC-2612 `permit` then `transferFrom`) where (i) the protocol has a single known
asset (`asset`/`token`/`underlying` immutable/state var) and (ii) no `permit.permitted.token == <asset>` (or
equivalent) comparison exists on the path.
- *Strengths:* tightest, highest-severity, presence+absence two-signal, maps to a concrete safe pattern.
- *Weaknesses:* requires identifying "the expected asset" (data-flow); silent on multi-asset routers (by design).
- *Precision risk:* moderate — routers/aggregators that legitimately accept any token must be suppressed.
- *Coverage potential:* low count but the only High-fund-loss shape; the worthwhile core.

**Shape B — recipient-binding (S2).** Flag Permit2 `permitTransferFrom` where the `to` is caller-influenced and not
bound via witness.
- *Strengths:* models a real Permit2 footgun (#5). *Weaknesses:* `to = address(this)` is common and safe →
  needs taint. *Precision risk:* high without taint. *Coverage:* medium.

**Shape C — non-atomic external permit (S3).** Flag `IERC20Permit.permit(...)` not wrapped in try/catch.
- *Strengths:* high recall on the front-run DoS class. *Weaknesses:* broad, low severity, overlaps replay.
  *Precision risk:* high (floods). *Coverage:* high but low value. **Not recommended standalone.**

**Shape D — digest-binding completeness (S4).** Flag EIP-712 typehashes missing chainId/verifyingContract/nonce.
- *Strengths:* models replay-via-indirection. *Weaknesses:* **duplicates the existing `signature-replay` KB
  pattern** → consolidation, not a new lens. *Precision risk:* medium. *Coverage:* medium.

---

## 10. Failure Modes (how detector design goes wrong)
1. **Absence-of-check detection is intrinsically noisy** — "no `== asset` assert" fires on every safe multi-asset
   router; without a "single expected asset" anchor the lens floods.
2. **Asset identity is contextual** — "the protocol's asset" may be per-market, per-vault, or computed; a literal
   var match misses/false-fires.
3. **Permit ubiquity → volume** — `permit`/`permitTransferFrom` appear in most modern DeFi; a name-gate alone is
   meaningless (the `multicall_invariant` lesson: presence of the primitive ≠ a bug).
4. **Cross-function binding** — the permit call and the asset-use are often in different functions; single-function
   scoping under-covers, multi-function taint over-reaches.
5. **Overlap with `signature-replay`** — S3/S4 re-detect what the existing pattern already covers → double-counting
   and turf confusion; the new lens must claim only the **what/where binding** corner.

---

## 11. Evaluation Plan (for a future prototype — mirrors the `multicall_invariant` arc)
1. **Freeze this dataset** (the 13 in-scope rows) as the recall set; the in-repo **Revert Lend #368** is the
   known-positive anchor (re-runnable on `audits/revert-lend-2024-03-strict-eval`).
2. **Build research-only, un-wired** (`is_gate:false`/`research_only:true`/`routes_in_production:false`), Shape A
   first; measure recall on the frozen set and **FP volume on a benign corpus** (the 20 multicall targets +
   router-heavy protocols are a good noise stressor — many permits, few asset-mismatch bugs).
3. **Precision gate:** require the two-signal anchor (Permit2 consume + single expected-asset var + no equality
   assert); record FP autopsies; reject if high-confidence FP > 0 on the noise corpus.
4. **Boundary check:** confirm zero overlap-double-reporting with the `signature-replay` pattern (S4 cases must be
   deferred to that pattern, not re-emitted).
5. **Decision:** promote to advisory only if Shape A holds recall on #1-class cases with ~0 high-confidence noise —
   exactly the bar `multicall_invariant` met for its narrow shape.

---

## 12. Recommendation

# MODERATE POTENTIAL DETECTOR FAMILY

The family is real and includes a genuine High-severity, fund-loss shape (asset mismatch, #1). But it is **not**
HIGH potential, because: (a) the highest-value shape is **rare and absence-based** (precision-hard, needs cross-
function data-flow + a protocol-specific "expected asset" anchor); (b) the **high-frequency** members are mostly
Medium DoS/replay that **overlap existing `signature-replay` coverage**; and (c) permit primitives are ubiquitous,
so a broad detector would flood. It is clearly above LOW (the shape is concrete, has a clean safe-pattern, and a
verified anchor) and is not NOT-RECOMMENDED. Pursue a **narrow, Permit2 asset-binding research prototype (Shape A)**
with a frozen eval set; defer S3/S4 to the existing replay pattern.

---

## Final Output

### 1. Executive summary
Permit/Permit2 bugs are a real recurring family with a High fund-loss corner (asset mismatch) but a heterogeneous,
mostly-Medium body that overlaps existing signature-replay coverage. The one precision-viable entry point is a
narrow, data-flow Permit2 **asset-binding** detector (consume + expected-asset + no equality assert). **MODERATE
potential.**

### 2. Top 10 findings
Revert Lend #368 (asset mismatch, High) · Permit2 #250 (recipient not signed, design) · Aave v3.3 #138 (permit
bypass) · Beanstalk Finale (param-not-bound replay, High) · Rigor H-01 (untyped signing, High) · Oku #54 (permit
front-run DoS) · Union #67 (permit front-run grief) · Harmonix M-01 (zero permit-signer) · Ondo M-04 (auth after
revoke) · Ethena M-01 (approval-reuse bypass).

### 3. Root-cause distribution (13 in-scope)
scope/params-not-bound 4 · validation-bypass 2 · replay/front-run 2 · widening/approval-reuse 2 · **asset mismatch
1** · recipient mismatch 1 (design) · delegated-execution drift 0.

### 4. Most promising signals
**S1 (Permit2 transfer without asset-equality assert)** — the only presence+protocol-anchored, high-severity
signal. Secondary: S2 (recipient not witness-bound) with taint.

### 5. Biggest precision risks
Absence-of-check noise on multi-asset routers; permit ubiquity; cross-function binding; double-counting vs.
`signature-replay`; "expected asset" being contextual rather than a single var.

### 6. Recommended detector architecture
Narrow, research-only, **two-signal** Shape A: (consume Permit2/ERC-2612 transfer) **AND** (a single protocol
expected-asset var) **AND** (no `permitted.token == asset` assertion on path) → flag; suppress when no single
expected asset (router) or when the safe pattern is present. Data-flow / +1-level cross-function resolution. Defer
replay-binding (S4) to the existing pattern.

### 7. Recommended evaluation strategy
Freeze the 13-row recall set with Revert Lend #368 as the known-positive anchor; measure recall + FP volume on a
permit-dense benign corpus; require ~0 high-confidence FP; FP autopsies; promote to advisory only on a clean narrow
result — the same bar `multicall_invariant` met.

### 8. Final recommendation
**MODERATE POTENTIAL DETECTOR FAMILY** — build the narrow Permit2 asset-binding prototype (Shape A) research-only;
do not build a broad permit detector; route nothing until separately validated.
