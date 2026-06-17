# Deep-Pass Depth-Trace v2 (Phase-18, RESEARCH-ONLY, experimental/off)

Repaired depth checklist composed ON TOP OF the baseline value-provenance pass. v2 exists because
**depth_trace_v1 did not generalize** (1 win on BakerFi, +2 hallucinations on Kelp). v2's bias is
**reject-unless-proven-exploitable**, not "flag if the math looks odd."

**NOT a detector.** Generic reasoning questions only; no protocol-specific or known-bug rules. Must be able to
conclude **no_finding**.

## Run per candidate (after baseline). A finding requires passing BOTH gates §1 and §2.

### §1 — Exploitable-as-deployed gate (ALL must be true, with evidence, or → `no_finding`)
1. **Attacker-controlled entrypoint** exists (a permissionless or attacker-reachable function reaches this code).
2. **Required state is reachable** on the **live, in-scope** deployment (not a hypothetical future config).
3. **No trusted-role dependency** — the exploit does not require a governor/owner/keeper to misbehave.
4. **No impossible/not-yet-supported state** — it does not rely on an asset/config the protocol does not (and
   per scope, will not) support (e.g. a non-standard-decimal token that isn't onboarded).
5. **Impact follows from the path** — a concrete value or protocol-invariant impact results.
If any is unproven → **mark `latent`/`no_finding`** with `reason_rejected`. (This kills the Kelp scale halluc.)

### §2 — Mechanism-match gate
State the **exact mechanism** from: `missing_term · wrong_conversion · scale_mismatch · order_of_operations ·
first_actor · missing_check · lifecycle_flow · oracle_mismatch · interface_mismatch · other`. The evidence and
the divergence point **must support that mechanism**. If the evidence actually supports a *different*
mechanism, **reject the claimed one** (don't flag the right function with the wrong mechanism — the Kelp error).

### §3 — Order-of-operations trace (mandatory for every candidate)
Write: **pre-state → attacker action → state-mutation order → checks-before-mutation → checks-after-mutation →
any stale/premature state use → final state.** Flag `order_of_operations` only if a value is **read after a
mutation that should have happened later** (or a check guards the wrong side of a mutation). (Kelp H-62: the
deposit is added to `totalEthLocked` *before* the mint price is computed → under-mint.)

### §4 — First-actor / empty-state analysis (mandatory)
Check the attacker-reachable empty/first state: `totalSupply==0 · first deposit · first stake · first mint ·
first redemption · empty pool · uninitialized accumulator · bootstrap price · first reward index · initial
share/exchange-rate`. Flag `first_actor` only if the first actor can set a **manipulable** rate/price/index
that harms later users, AND no guard (min-deposit / dead-shares / seeded supply) prevents it. (Kelp H-42.)

### §5 — Scale-mismatch skepticism
Flag `scale_mismatch` **only if ALL**: (a) units are **proven** inconsistent (write the unit ledger), (b) the
attacker can **influence the path**, (c) the mismatch **changes value or permissions**, (d) the exploit impact
is **demonstrated on a supported input**. Otherwise → **`latent`/`no_finding`** (record it as a note, not a
finding). This is the explicit anti-Kelp-hallucination rule.

### §6 — Two-sided evidence (mandatory for any suspected issue)
List `evidence_wrong` (with `file:line`) AND `evidence_safe_or_intended` (with `file:line`). Decide by which
side is **stronger** under §1+§2. If safe/intended is plausible and exploitability is unproven → `no_finding`.

### §7 — Mandatory no-finding path
Allowed conclusion: **"No vulnerability found; suspicious pattern is not exploitable as deployed."** Use it
freely — **"more findings" is a liability**; an unexploitable suspicious note is noise, not recall.

### §8 — Output schema (per candidate, appended to output/deep_pass/_decisions.json)
```json
{
  "manifest_id": "...", "contract": "...", "function": "...",
  "decision": "finding | no_finding",            // (finding ⇒ emit as finding/likely_exploitable to the writer)
  "mechanism": "<one of §2>",
  "confidence": "high | medium | low",
  "attacker_entrypoint": "...",
  "reachable_state": "...",                        // why §1.2 holds
  "exploit_steps": ["..."],
  "affected_identity_or_invariant": "...",
  "evidence_wrong": "file:line — ...",
  "evidence_safe_or_intended": "file:line — ...",
  "reason_rejected_if_no_finding": "...",          // required when decision=no_finding
  "hallucination_risk": "low | medium | high",     // self-assessed; high ⇒ prefer no_finding
  "depth_class": "<missing_term|wrong_conversion|scale_mismatch|order_of_operations|first_actor|callee_identity|none>",
  "via_callee": true/false,
  "family": "value_flow_parity", "shape": "<mechanism>", "evidence_span": "file:line", "repro_hint": {…}
}
```
For the deterministic writer: map `decision:finding` → `finding`/`likely_exploitable` (high/medium); map
`decision:no_finding` → `needs_human`/`strong_clear`. Carry `repro_hint` for findings.

## Discipline
- A finding must pass §1 (exploitable-as-deployed) AND §2 (mechanism-match). No exceptions.
- Internal-callee flags require a **concrete divergence in the callee** (§6), not "I read a callee."
- Conversion flags require a **demonstrated who-benefits exploit**, not the mere presence of a conversion.
- Research-only: sets family/shape/confidence + a hypothesis; no severity/submission/routing.
