# Agentic Workflows for Audit-Watch — Research & Roadmap

Repo-grounded research on optimizing Audit-Watch's **agentic workflows** — the LLM specialist agents
(`agents/*.md`) + in-session skills (`/ite-audit`, `/deep-analysis`, `/triage`, `/coverage-sweep`, …) that
run credit-free via the `api_free` skill route. Prompted by the **Phase-13 finding**: the deterministic
recall lenses are sub-shape-overfit (Holdout Recall 0%), and `corpus_gap_analysis.md` concluded the
remaining recall (broad wrong-value, semantic invariants) needs a **value-provenance / deep-pass reasoning
step, not more enumerated structural shapes**. That is exactly an agentic-workflow problem.

## The one principle carried forward (non-negotiable)

Phase 12/13 proved that anything that *looks* validated on its design corpus must be re-measured on an
**uninspected holdout**, with **Holdout Recall as the primary metric** and a **0-anchor-FP gate**. Agentic
steps are *more* prone to this trap (prompt-overfitting, contamination, hallucinated findings), so **every
agentic experiment here reuses the Phase-12 benchmark + `score_generalization.py` train/holdout harness** —
no agentic workflow is "accepted" on a demo.

## Documents

| Doc | Contents |
|-----|----------|
| `literature_synthesis.md` | Agentic-AI-workflow literature (from training knowledge ≤ Jan 2026 — **not live citations**), mapped to Audit-Watch. |
| `ai_setup_connector_inventory.md` | The current Claude/skill/MCP setup + connector compatibility. |
| `architecture_analysis.md` | Agentic architectures + optimization strategies, analyzed against the existing agents/skills/deep-pass. |
| `experiment_design.md` | Reproducible bug-hunting + generalization experiments (reuse benchmark + train/holdout). |
| `implementation_roadmap.md` | Prioritized roadmap with metrics (Generalization/Holdout Recall, FP, cost/latency, api_free constraint). |

## Answer to "is this enough research?"

For the **deterministic detector track: yes** — Phase 13 gave a sufficient, honest verdict. The *new*
subject worth researching is **agentic reasoning over the detectors' output** (the deep-pass), because the
repo's gap analysis already points there and the infrastructure (`deep_pass_queue.py` / `deep_pass_ledger.py`
/ `prompts/deep_pass_packet.md`, plus the SKILL_MAP `deep_pass` slot) is **built but not yet wired to an
agentic step**. These docs scope that — design + roadmap only, no code or routing changes this round.
