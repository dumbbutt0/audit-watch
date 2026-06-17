# Eval Plan — QuantAMM 2024-12 CodeHawks Blind Eval

## Identity
- **Eval name:** QuantAMM 2024-12 CodeHawks blind eval
- **Workspace:** `audits/quantamm-2024-12-eval/`
- **Audit id:** `quantamm-2024-12-eval`
- **Platform:** CodeHawks
- **Contest slug:** `2024-12-quantamm`

## Answer key
- **Answer-key URL (locked source):**
  `https://codehawks.cyfrin.io/c/2024-12-quantamm/submissions?filterSelectedForReport=%7B%22value%22%3A%22selectedForReport%22%2C%22label%22%3A%22Selected+for+Report%22%2C%22disabled%22%3Afalse%7D&filterValidated=%7B%22value%22%3A%22validated%22%2C%22label%22%3A%22Validated%22%2C%22disabled%22%3Afalse%7D&search=`
- **Answer-key status:** 🔒 **LOCKED until post-freeze.** Will only be opened in Phase 6, after the
  blind scoring set is frozen + hashed (Phases 4–5).
- **Rule:** NO answer-key access before freeze. The URL must not be opened, scraped, summarized,
  or used to infer scope, findings, or severity until the pre-answer-key snapshot MANIFEST exists.

## Provenance / version
- **Start timestamp (UTC):** 2026-05-31T03:01:46Z
- **Auditor repo git commit:** N/A — the auditor working dir is **not a git repository**.
  Version pinned by key-script sha256 + mtime instead:
  - `run_pipeline.sh` — `5704b1fe…1c2a3e` (mtime 2026-05-31T02:50:43Z)
  - `scripts/build_coverage_manifest.py` — `7e199a16…6136c4` (2026-05-30T04:56:51Z)
  - `scripts/coverage_completeness_gate.py` — `2e2c91ed…b4694` (2026-05-29T22:06:32Z)
  - `scripts/confirm_gate.py` — `afc481c9…815d1d` (2026-05-30T06:18:55Z)
  - `scripts/build_final_scoring_set.py` — `c8b7740a…597856` (2026-05-30T04:19:20Z)
  - `tools/static_analysis.py` — `064e67bc…6cdd83` (2026-05-28T23:15:15Z)
- **Python:** 3.12.3 · **pytest:** present at `~/.local/bin/pytest`

## Runtime policy
- **`config/runtime_policy.json` → `api_free: true`** (preserved for the whole eval).
- **API-free status:** ENFORCED. No Anthropic API calls. Every LLM stage (deep-analysis,
  ite-audit specialists, coverage-sweep, triage) runs in-session via skills.
- **Budget mode:** `config/agent_policy.json → active_mode = deep` (full specialist pass +
  conditional lenses + long-tail coverage sweep).
- **PoCs:** NOT generated — eval mode does not require PoCs (CLAUDE.md: PoCs not required for eval
  classification). High/Critical recall findings remain eval-only, NOT submission-ready.

## Blindness / contamination controls
1. Scope (Phase 1) reconstructed only from the contest landing page, source repo, README, and
   docs — never the filtered submissions answer-key page.
2. STOP-and-report if repo/commit can't be confidently reconstructed without the answer key.
3. All blind artifacts frozen + sha256-hashed (Phase 4) and the final scoring set frozen
   (Phase 5) **before** the answer-key URL is opened (Phase 6).
4. After answer-key access: no scoring artifact is mutated; integrity re-verified by re-hash.
5. No answer-key knowledge is converted into findings.

## Pipeline (API-free, deep)
`analyze` → `/deep-analysis` → `analyze-resume` → `/ite-audit` (+`/supply-chain`) → semantic
lenses → `/coverage-sweep` → `full` (pauses at triage) → `/triage` → `triage_write.py` →
`review-gate` → `write_eval_ready` → `confirm-advisory` (advisory only, never blocks) → gates →
status. Eval scoring layer uses workspace-local harness in `logs/` (Zaros pattern), leaving
shared `scripts/` untouched.

## Status log
- 2026-05-31T03:01:46Z — Phase 0 complete: workspace created + switched + eval_plan written.
