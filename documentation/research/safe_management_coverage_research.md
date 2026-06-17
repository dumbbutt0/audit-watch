# Research detector: `safe_management_coverage` (RESEARCH-ONLY, un-wired)

> is_gate:false · research_only:true · routes_in_production:false · routed_manifest_ids:[]. Built P237 to close the
> P236-identified highest-leverage recall gap (Safe governance/management — incomplete/incorrectly-decoded guard
> selector coverage). Scope: Safe-management selector coverage + calldata decode ONLY. Does NOT detect
> hostile-token, reentrancy, Seaport, or economic issues.

## 1. Research
Gap (P236, verdict B): the dominant family of P235 reNFT recall misses is guard/policy contracts that filter Gnosis
Safe transactions by **function selector** but (a) decode a multi-argument Safe self-management call at the **wrong
calldata offset** (validating the wrong argument), or (b) cover some Safe self-management selectors while **missing**
others. This is architectural (any Safe-guard / module-guarded custody / account-abstraction system), not
reNFT-specific. Core question: *for a contract that claims to restrict Safe self-management, is every high-impact
self-management selector covered and correctly decoded?* Precision tension: many contracts mention these selector
names as callers (modules/factories) without being guards — must not flag mere usage.

## 2. Taxonomy
Two finding shapes:
- **decode_offset_mismatch** — a covered multi-arg Safe selector whose protected argument is read at the wrong
  calldata offset. Canonical: `disableModule(address prevModule, address module)` — protected arg `module` is at
  offset `0x44`; checking `0x24` validates `prevModule`. (reNFT H-04.)
- **incomplete_selector_coverage** — guard covers ≥1 Safe self-management selector but misses high-impact ones:
  `setFallbackHandler`/`setGuard` (HIGH — install malicious fallback/guard), `enable/disableModule` (HIGH — module
  install/removal), and a grouped MED tier (module-execution `execTransactionFromModule[ReturnData]`, batched
  `multiSend`, owner-management, and approval-equivalent `permit`/`increaseAllowance` when `approve`/
  `setApprovalForAll` are already blocked). (reNFT H-02; H-05 fallback/permit basis.)

IN scope: contracts implementing a Safe transaction-check guard (selector dispatch over a calldata-loaded selector,
or Gnosis `checkTransaction`/`BaseGuard`). OUT of scope: the Safe primitives themselves; modules/factories/policies
that merely *call* Safe functions; non-Safe selector contexts.

## 3. Ground-truth corpus
- **In-repo anchor (runnable):** reNFT 2024-01 `Guard.sol` + `RentalConstants.sol`
  (`audits/renft-2024-01-shadow/...`). H-04 = `gnosis_safe_disable_module_offset = 0x24` (reads prevModule).
  H-02 = `setFallbackHandler` not in the guard's selector set.
- **Web-confirmed:** reNFT C4 report H-04 (#38/#625), H-02, H-05 (#614 area / fallback-handler removal + permit).
- **Negatives/controls:** modules/policies that call Safe fns (`Stop`, `Factory`); test/mock guards; a
  fully-covering guard; a plain ERC20/approval guard with no Safe-specific selectors.

## 4. Prototype (this detector)
- `scripts/safe_management_coverage_taxonomy.py` — pure classifier (`classify`, `is_safe_guard`, offset resolver).
- `scripts/safe_management_coverage_audit.py` — manifest-driven runner (in-scope, non-test contracts only;
  resolves selector/offset `constant`s from all non-test source; emits the 4 research flags; `--out` for capture).
- `config/safe_management_coverage_patterns.json` — selector knowledge base (canonical bytes4 + name-tokens +
  protected offsets + impact tiers), guard-context gate, suppressions, fp_controls.
- `tests/safe_management_coverage/` — 8 synthetic cases + reNFT replay recovery (10 tests, all pass).

Two-signal FP gate: **Signal-1** = implements a Safe-guard transaction check (`checkTransaction`/`BaseGuard`, or a
calldata-selector load + `selector ==` dispatch) **and** covers ≥1 Safe-specific self-mgmt selector; **Signal-2** =
a concrete defect (offset mismatch OR missing high-impact selector). Admin-only paths downgrade to low.

## 5–7. Validation / scope / stability
reNFT full-workspace replay (22,345 manifest items, 160 in-scope): **4 candidates, all on the real `Guard`, 0 false
positives** (Stop/Factory/test guards correctly suppressed by the tightened guard-entrypoint gate + in-scope/non-test
filter). Recovers H-04 (decode_offset_mismatch, HIGH) and H-02 (setFallbackHandler missing, HIGH) directly; H-05
permit basis as a MED approval-equivalent candidate. Recovery is mechanism-based (offset value 0x24≠0x44;
selector-set difference) — no answer-key string matching.

- **Scope classification:** NARROW SCOPE CONFIRMED — Safe-management selector coverage + multi-arg decode offset.
- **Stability classification:** **PROMISING-BUT-NEEDS-REFINEMENT** (validated on the single reNFT anchor with 0 FP;
  needs a 15–20 target validation campaign before RESEARCH-STABLE). Un-wired; promotion is a separate human decision.
