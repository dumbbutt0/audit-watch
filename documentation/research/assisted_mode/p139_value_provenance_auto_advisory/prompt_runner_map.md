# P139 — Prompt Runner Map

- `prompts/deep_pass_value_provenance.md` — the value-provenance specialist prompt (one function-scoped bundle;
  emits finding/likely_exploitable/strong_clear/needs_human). Executed via the in-session `/deep-pass` skill.
- `scripts/deep_pass_prepare.py` — deterministic bundle builder (reuses `sibling_function_parity_audit._function_body`).
- `scripts/deep_pass_write.py --eval` — RESEARCH-ONLY: validates skill output -> deep_pass_audit.json; never touches dispositions.
- `scripts/llm_runtime.py` — `llm_available()` returns **False** whenever `config/runtime_policy.json api_free=true`
  (the default), regardless of key. **There is NO safe non-interactive LLM runner.**

Conclusion: a `run_pipeline.sh`-invoked Python script cannot execute the prompt non-interactively → the auto path
is a SCAFFOLD: it auto-prepares + auto-routes a queued job (`pending_manual_execution`) and the LLM EXECUTION
stays the in-session `/deep-pass` skill (results recorded later via `deep_pass_write.py --eval`). No runner is
invented; no decision is faked.
