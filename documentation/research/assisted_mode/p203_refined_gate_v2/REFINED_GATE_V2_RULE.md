# Refined severity gate v2 — independent magnitude/precondition rule

**Status: general rule, written BEFORE application (no per-case backfit).** Additive to the v1 mechanism-level
reject-first gate; it adds one **independent source-substantiation precondition** that must pass before any
mechanism may be `HIGH_CONFIRMED`. Design/offline only; not wired to production.

## v1's failure this fixes
v1 trusted the blind layer's *asserted* value-extraction magnitude. When a blind output asserted "theft" without the
source proving the funds are custodied/movable at the vulnerable point, v1 confirmed HIGH (P202: M-03 receiveFromBridge
over-confirmed ×3; decent-06/12 unawarded false-Highs). v2 requires the calibrator to *independently cite source
evidence* for the value path.

## The independent HIGH precondition (ALL must hold, each source-cited)
A mechanism may be `HIGH_CONFIRMED` **only if** the calibrator can cite source-backed evidence for **all**:
1. **public or attacker-controlled entry path** (the vulnerable function is reachable by an unprivileged/attacker actor);
2. **concrete affected asset or accounting balance** (a specific token balance, ETH balance, share/supply, or
   accounting variable is named);
3. **attacker-controlled action that changes that asset/balance** (the attacker's call demonstrably moves/alters it);
4. **victim or protocol loses value, control, solvency, or permanent access** (a real loser is identified);
5. **magnitude is material or scalable, not merely asserted** (source shows the amount is unbounded/large/repeatable,
   not dust/bounded/asserted-only);
6. **no trusted/admin/TSS prerequisite** (does not require compromising an owner/operator/relayer/executor key);
7. **no dependency on unseen code** unless that unseen code is already source-proven within the sampled corpus;
8. **no reliance on "the contract may hold funds"** unless the source shows the contract **holds or controls** the
   relevant funds **at the vulnerable point**.

## Downgrade rule (the core change)
If the blind output claims **theft/material-loss** but the source only proves **unauthorized call / fee bypass /
signature bypass / message spoofing / access-control bypass** — *without* source-proven custody or value movement —
then classify:
- `MEDIUM_OR_LOWER_CALIBRATED` if the proven impact is bounded / reversible / local;
- `NEEDS_HARNESS_FOR_SEVERITY` if value movement *might* be material but is **not source-proven** at the vulnerable point.

## Evidence fields recorded per mechanism (v2 regrade)
- `value_precondition_status`: SOURCE_PROVEN | NOT_SOURCE_PROVEN | PARTIAL | UNSEEN_DEPENDENCY
- `magnitude_status`: MATERIAL_PROVEN | BOUNDED | UNKNOWN | ASSERTED_ONLY
- `custody_value_flow_proof`: CONTRACT_CUSTODY_PROVEN | USER_BALANCE_PROVEN | ACCOUNTING_BALANCE_PROVEN | NOT_PROVEN
- `downgrade_reason` (if v2 < v1) / `retained_high_reason` (if HIGH retained)

## Labels (unchanged enum)
HIGH_CONFIRMED · MEDIUM_OR_LOWER_CALIBRATED · NEEDS_HARNESS_FOR_SEVERITY · SOURCE_REFUTED · INSUFFICIENT_EVIDENCE.

## Generality (anti-backfit)
The rule references **no specific finding, surface, or severity label** from any answer key. It is applied uniformly
to every mechanism by a key-blind calibrator that reads the protocol source to substantiate or refute the value path.
HIGH is retained only where custody/value-flow + material magnitude are source-proven; demoted otherwise — wherever
the chips fall.
