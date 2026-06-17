# Zero-Trust Triage Policy

Triage re-derives every claim from raw source. A prior stage's score is a suggestion, never a
seal of approval. Two stages disagree → the conservative (more vulnerable) reading wins and both
are logged.

## ICE re-derivation (from scratch)

For each finding, re-score from the source — do not inherit the specialist's numbers:

- **I — Impact:** worst-case outcome for the protocol (Critical/High/Medium/Low/Info).
- **C — Confidence:** is the code path reachable and the flaw real? (Confirmed/High/Medium/Speculative).
- **E — Exploitability:** permissionless / privileged / conditional.

A finding advances past triage only if **I ≥ Medium AND C ≥ High AND the exploit path is traced
end-to-end**.

## The no-silent-clear rule (the core change)

An agent or triage step may **not** output "cleared / sound / safe / works as designed / not
exploitable" on **safety-net code** without a written **attacker-path disproof**.

**Safety-net code** = code whose whole job is to protect the protocol:
- solvency/invariant modifiers (e.g. `Invariable`, `fundsSafu`, `noNetFlow`)
- custom sorts / normalization / distribution math (e.g. `quickSort`)
- peg/oracle aggregators and price selection
- bridge-address / cross-domain sender checks
- season/epoch/time gates
- one-shot init / migration completeness

**A valid disproof names the concrete thing an attacker would need and why it is impossible**,
e.g. _"to violate this an attacker must make `s.sys.rain.roots` exceed total roots, but it is set
to `s.sys.silo.roots` in the same transaction before any user action, so no intermediate state is
reachable."_ Hand-waving ("looks correct", "standard pattern") is not a disproof.

**Absent a disproof, the step must emit an `unresolved_invariant` finding** routed to the human
queue — never a silent clear. This converts the worst Beanstalk failure mode (5 confident false
clearances by `protocol_context`) into a surfaced, reviewable artifact.

### Enforcement

- Agent templates `protocol_context.md`, `semantic_guard.md` and the global
  `prompts/human_auditor_methodology.md` state the rule.
- `scripts/validate_agent_output.py` rejects a finding/verdict tagged `cleared` on safety-net
  code that lacks a `disproof` field, and accepts `unresolved_invariant` as a valid routing
  outcome. (Verified with a synthetic reject/accept fixture, Guardrail 3.)

## Follow-up packet (required for every submit-bound finding)

Triage produces a tight packet a human can check in under a minute:

1. **Reachable:** the exact external/public entrypoint; not behind privileged auth.
2. **No privileged keys:** the attacker is an ordinary EOA (or state the exact privilege needed).
3. **State before → after:** named storage slots/balances, asserted both sides.
4. **Why guards fail:** the specific modifier/check that *should* stop it and why it doesn't.
5. **Scope match:** the claimed impact is in the program's scope and severity band.

## Severity calibration notes (carried from the Beanstalk eval)

- One-shot init/migration routines that can revert or run out of gas **block the launch** → at
  least **High**, not "admin robustness" (Beanstalk #140 was under-called).
- Critical/High require PoC evidence matching the claimed impact before severity is finalized.
- `attacker_mindset` hypotheses are **not findings** — they inform `attack_surface.json` only and
  must not enter the findings corpus.
- `supply_chain_check` output goes to `reports/build_security_annex.md`, separate from the
  contract-vuln findings, so it doesn't dilute precision.
