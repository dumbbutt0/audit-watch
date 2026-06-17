---
name: deep-pass
description: "Credit-free, skill-in-session agentic deep-pass over detector candidates (Phase-14 / Experiment E1, RESEARCH-ONLY). Reasons about value provenance — does a value validated against one subject get used on a different subject (wrong variable/key/index/identity/operand)? — to recover wrong-value bugs the deterministic value_flow_parity lens cannot generalize to. Reads bundles from deep_pass_prepare.py, applies prompts/deep_pass_value_provenance.md (ROUTE→PLAN→TRACE→CRITIC→DECIDE→REPRO_HINT), emits decisions, then deep_pass_write.py --eval validates + writes a scorer-compatible deep_pass_audit.json WITHOUT touching coverage_dispositions.json. Activate when user says: /deep-pass, deep pass, run the deep-pass over detector candidates, value-provenance pass, or run an E1 ladder rung."
---

# Deep-Pass (skill-in-session, RESEARCH-ONLY)

Agentic second stage over the deterministic lens output. The detectors route the right *functions* but miss
the generalizable *wrong-value* shapes; this pass reasons over each candidate's value provenance to recover
them. **No API calls. Research-only: it never mutates dispositions, never sets severity, never produces a
PoC.** It is measured on the Phase-12/13 train/holdout benchmark (Holdout Recall primary, 0 anchor FP).

## When to use

After the research detectors have run on a workspace (so `value_flow_parity_audit.json` etc. exist) and you
want to run an ablation-ladder rung (c1 = reasoning no-KB, c2 = reasoning + KB). Reasoning spec:
`prompts/deep_pass_value_provenance.md`. SKILL_MAP key: `deep_pass` (optional ⇒ never gate-blocks).

**Ladder note:** `c-1` (detector only) and `c0` (packaging control) are mechanical — do NOT run this skill
for them (c0 recall == c-1 by construction). Only `c1`/`c2` run the skill.

## Procedure

1. **Prepare bundles (deterministic):**
   ```
   python scripts/deep_pass_prepare.py --no-kb        # rung c1 (reasoning, no KB)
   python scripts/deep_pass_prepare.py                 # rung c2 (reasoning + KB)
   ```
   Writes `output/deep_pass/_bundles/dp_*.json` (one per candidate) + `_bundles/index.json`. Each bundle
   embeds the function body + 1–2 callee bodies (+ `kb_precedents` at c2) so you reason from the bundle.

2. **Reason over each bundle (you, in-session).** Read `index.json`, then each `dp_*.json`. Apply
   `prompts/deep_pass_value_provenance.md` literally per bundle:
   - **ROUTE** → **PLAN** → **TRACE** the semantic-mismatch schema (validated_subject vs mutated_subject,
     identity_source, quantity_source, state_delta, preconditions, **divergence_point**) → **CRITIC**
     (disprove first; carry a real `evidence_span`) → **DECIDE** → **REPRO_HINT**.
   - `finding` needs a real evidence line + a `repro_hint`. `likely_exploitable` additionally needs
     `attacker_entrypoint` + `divergence_point` + `claimed_effect` (mandatory evidence) + a `repro_hint`.
   - Uncertainty ⇒ `needs_human` (never a silent `strong_clear`). No evidence ⇒ no finding (it's rejected).
   - At **c1** there are no `kb_precedents` — reason from source alone. At **c2** use them as templates only.

3. **Emit decisions** to `output/deep_pass/_decisions.json`:
   `{"packet_id":"deep_pass_<rung>","decisions":[{manifest_id, decision, family, shape, contract, function,
   confidence, evidence_span, validated_subject, mutated_subject, divergence_point, attacker_entrypoint,
   claimed_effect, repro_hint{state_preconditions,required_actor,required_assets,critical_transaction,
   expected_violation}, reasoning_summary}, ...]}`.

4. **Validate + emit audit (deterministic, research-only):**
   ```
   python scripts/deep_pass_write.py --eval \
       --decisions output/deep_pass/_decisions.json --out output/deep_pass_audit.json
   ```
   Rejects findings without evidence, `likely_exploitable` without its mandatory fields, and findings without
   a complete `repro_hint`. Writes `output/deep_pass_audit.json` (scorer-compatible) and **leaves
   `coverage_dispositions.json` untouched**.

## Output

Report counts (finding / likely_exploitable / strong_clear / needs_human / rejected) and how many findings
carry a `repro_hint`. For the benchmark: copy `output/deep_pass_audit.json` into
`documentation/evals/promotion_benchmark/raw_results/<proto>/` and run `score_generalization.py`.
**Firewall:** design/freeze the prompt + skill on train + anchors before ever running the ECG holdout;
record prompt/skill hashes in `holdout_firewall_attestation.md`.
