#!/usr/bin/env bash
# run_pipeline.sh — Audit Watch pipeline runner (single-user)
#
# Full audit flow:
#   1. ./run_pipeline.sh analyze <contract>   — Steps 0.5→1.5 (scope inventory, sandbox, deep analysis, static, context pack)
#   2. /ite-audit                             — Step 2 specialist agents (in Claude Code)
#   3. ./run_pipeline.sh full                 — Steps 2.5→4 (synthesis → gates → triage → PAUSE at review_gate.md)
#      [Review review_gate.md, pick PoC finding IDs]
#   4. ./run_pipeline.sh poc <finding-id>     — PoC for selected findings (L1/L2/L3)
#   5. ./run_pipeline.sh submit               — Steps 5→9 (specialist review → QC → pack)
#
# Other commands:
#   ./run_pipeline.sh status                  — print compact status
#   ./run_pipeline.sh test [finding-id]       — run forge/cargo tests
#   ./run_pipeline.sh triage                  — quick triage (compound + triage_findings only)
#   ./run_pipeline.sh specialist              — run specialist review (Step 5)
#   ./run_pipeline.sh poc <finding-id>        — generate + run PoC for one finding
#   ./run_pipeline.sh poc-all                 — PoC for all poc_required findings
#   ./run_pipeline.sh package [finding-id]    — build submission pack
#   ./run_pipeline.sh checklist               — quality checklist for all proved findings
#   ./run_pipeline.sh gate                    — PoC completeness gate

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${ROOT}/.venv/bin/python"
if [[ ! -x "${PYTHON}" ]]; then
  PYTHON="$(command -v python3 || command -v python)"
fi

CMD="${1:-status}"
ARG="${2:-}"

log()  { echo "[pipeline] $*" >&2; }
die()  { echo "[pipeline] ERROR: $*" >&2; exit 1; }
warn() { echo "[pipeline] WARNING: $*" >&2; }

# run_step <label> <cmd> [args...] — run a step, warn on failure, continue
run_step() {
  local name="$1"; shift
  log "  → ${name}"
  if ! "$@" ; then
    warn "${name} failed (exit $?) — continuing"
  fi
}

status_snapshot() {
  "${PYTHON}" "${ROOT}/scripts/generate_status.py" 2>/dev/null || true
}

active_audit_id() {
  "${PYTHON}" -c "
import sys, json
from pathlib import Path
f = Path('${ROOT}/config/active_audit.json')
if not f.exists(): sys.exit('No active audit')
d = json.loads(f.read_text())
print(d.get('audit_id', ''))
"
}

require_audit() {
  AUDIT_ID="$(active_audit_id)"
  if [[ -z "${AUDIT_ID}" ]]; then
    die "No active audit. Run: python scripts/audit_manager.py new <id>"
  fi
  log "Active audit: ${AUDIT_ID}"
}

# populate data/findings/<ID>.json from merged_findings.json (Step 3 post-merge)
populate_finding_metadata() {
  "${PYTHON}" - << 'PYEOF'
import json, sys
from pathlib import Path
sys.path.insert(0, 'scripts')
try:
    from audit_context import audit_path
    merged_path = audit_path('output') / 'merged_findings.json'
    if not merged_path.exists():
        print("  [skip] No merged_findings.json yet")
        sys.exit(0)
    merged = json.loads(merged_path.read_text())
    d = audit_path('data/findings')
    d.mkdir(parents=True, exist_ok=True)
    count = 0
    for f in merged.get('findings', []):
        fid = f.get('id')
        if fid:
            p = d / f'{fid}.json'
            if not p.exists():
                loc = f.get('location', {})
                p.write_text(json.dumps({
                    'finding_id': fid,
                    'title': f.get('title', ''),
                    'severity': f.get('severity', 'Medium'),
                    'vuln_type': f.get('vuln_type', ''),
                    'bug_class': f.get('vuln_type', 'logic_error'),
                    'claimed_severity': f.get('severity', 'Medium'),
                    'file': loc.get('file', ''),
                    'function': loc.get('function', ''),
                    'confidence': f.get('confidence', 'Medium'),
                    'duplicate_of': f.get('duplicate_of'),
                    'agent': f.get('agent', ''),
                }, indent=2))
                count += 1
    print(f"  [findings] Written {count} new finding definitions")
except Exception as e:
    print(f"  [findings] Skipped: {e}")
PYEOF
}

case "${CMD}" in

  analyze)
    [[ -z "${ARG}" ]] && die "Usage: ./run_pipeline.sh analyze <contract_path>"
    require_audit
    CONTRACT="${ARG}"

    log "=== Pre-analysis pipeline (Steps 0.5 → 1.5) ==="

    log "Step 0: Scope inventory..."
    run_step "generate_scope_inventory" "${PYTHON}" "${ROOT}/scripts/generate_scope_inventory.py" \
      --contract "${CONTRACT}"
    "${PYTHON}" "${ROOT}/scripts/update_session.py" --step "0-scope" 2>/dev/null || true

    log "Step 0.5: Sandbox check (FATAL on flags)..."
    if ! "${PYTHON}" "${ROOT}/scripts/sandbox_check.py" "${CONTRACT}"; then
      die "Sandbox check flagged the contract. Review flags above. Use --allow-flagged only with explicit justification."
    fi
    "${PYTHON}" "${ROOT}/scripts/update_session.py" --step "0.5" 2>/dev/null || true

    log "Step 0: Deep invariant analysis (stages 0a–0f)..."
    run_step "run_deep_analysis" "${PYTHON}" "${ROOT}/scripts/run_deep_analysis.py" \
      --contract "${CONTRACT}" --mode deep
    "${PYTHON}" "${ROOT}/scripts/update_session.py" --step "0" 2>/dev/null || true
    status_snapshot

    log "Step 0.25: Attacker mindset brief..."
    run_step "generate_step0_brief" "${PYTHON}" "${ROOT}/scripts/generate_step0_brief.py"
    "${PYTHON}" "${ROOT}/scripts/update_session.py" --step "0.25" 2>/dev/null || true

    log "Step 1: Static analysis + test coverage..."
    run_step "static_analysis"       "${PYTHON}" "${ROOT}/tools/static_analysis.py" "${CONTRACT}"
    run_step "analyze_test_coverage" "${PYTHON}" "${ROOT}/scripts/analyze_test_coverage.py" \
      --contract "${CONTRACT}" --tests test/
    "${PYTHON}" "${ROOT}/scripts/update_session.py" --step "1" 2>/dev/null || true
    status_snapshot

    log "Step 1.5: Defense mapper + context pack..."
    run_step "defense_mapper"        "${PYTHON}" "${ROOT}/scripts/defense_mapper.py" --contract "${CONTRACT}"
    run_step "generate_context_pack" "${PYTHON}" "${ROOT}/scripts/generate_context_pack.py" --contract "${CONTRACT}"
    "${PYTHON}" "${ROOT}/scripts/update_session.py" --step "1.5" 2>/dev/null || true
    status_snapshot

    log ""
    log "=== Pre-analysis complete. Next steps: ==="
    log ""
    log "  1. Review: cat audits/${AUDIT_ID}/output/step0_brief.md"
    log "  2. In Claude Code, run: /ite-audit"
    log "     → spawns Step 2 specialist agents (reentrancy, access_control, oracle, etc.)"
    log "     → also run /supply-chain for the Step 1 parallel supply chain check"
    log "  3. When specialists finish: ./run_pipeline.sh full"
    log ""
    ;;

  status)
    require_audit
    "${PYTHON}" "${ROOT}/scripts/generate_status.py"
    ;;

  test)
    require_audit
    if [[ -n "${ARG}" ]]; then
      log "Running Rust PoC tests for ${ARG}..."
      (cd "${ROOT}/pocs/k2" && cargo test "${ARG}" -- --nocapture 2>&1) \
        | tee "${ROOT}/audits/${AUDIT_ID}/output/test_${ARG}.log" \
        || warn "Tests failed — see output above"
    else
      log "Running all Rust PoC tests..."
      (cd "${ROOT}/pocs/k2" && cargo test -- --nocapture 2>&1) \
        | tee "${ROOT}/audits/${AUDIT_ID}/output/test_all.log" \
        || warn "Some tests failed — see output above"
    fi
    ;;

  triage)
    require_audit
    log "Quick triage (compound synthesis + triage_findings only)..."
    log "For the full gated sequence, use: ./run_pipeline.sh full"
    run_step "synthesize_compound_findings" "${PYTHON}" "${ROOT}/scripts/synthesize_compound_findings.py"
    run_step "triage_findings"              "${PYTHON}" "${ROOT}/scripts/triage_findings.py"
    run_step "build_poc_queue"              "${PYTHON}" "${ROOT}/scripts/build_poc_queue.py"
    run_step "register_pc_findings"        "${PYTHON}" "${ROOT}/scripts/register_pc_findings.py" --apply
    status_snapshot
    ;;

  specialist)
    require_audit
    log "Running specialist review (Step 5)..."
    run_step "run_specialist_review" "${PYTHON}" "${ROOT}/scripts/run_specialist_review.py"
    status_snapshot
    ;;

  poc)
    require_audit
    [[ -z "${ARG}" ]] && die "Usage: ./run_pipeline.sh poc <finding-id>"
    log "Generating PoC plan for ${ARG}..."
    run_step "generate_poc_plan" "${PYTHON}" "${ROOT}/scripts/generate_poc_plan.py" --finding-id "${ARG}"
    log "Writing PoC test for ${ARG}..."
    run_step "generate_poc_test" "${PYTHON}" "${ROOT}/scripts/generate_poc_test.py" \
      --finding-id "${ARG}" --max-repair-attempts 3
    log "Running PoC tests for ${ARG}..."
    run_step "run_poc_tests"     "${PYTHON}" "${ROOT}/scripts/run_poc_tests.py" --finding-id "${ARG}"
    status_snapshot
    ;;

  poc-all)
    require_audit
    log "Running integrated PoC for all poc_required findings..."
    run_step "run_integrated_poc"    "${PYTHON}" "${ROOT}/scripts/run_integrated_poc.py" --all
    run_step "summarize_poc_results" "${PYTHON}" "${ROOT}/scripts/summarize_poc_results.py" \
      --out "reports/poc_evidence.md"
    status_snapshot
    ;;

  package)
    require_audit
    log "Building submission pack..."
    run_step "final_submission_pack" "${PYTHON}" "${ROOT}/scripts/final_submission_pack.py"
    if [[ -n "${ARG}" ]]; then
      SUBFILE="${ROOT}/audits/${AUDIT_ID}/output/submissions/${ARG}_submission.md"
      [[ -f "${SUBFILE}" ]] && log "Submission: ${SUBFILE}" || log "No submission file for ${ARG}"
    fi
    log "See: audits/${AUDIT_ID}/output/submission_pack.md"
    ;;

  checklist)
    require_audit
    log "Running quality checklist for all proved findings..."
    run_step "run_quality_checklist" "${PYTHON}" "${ROOT}/scripts/run_quality_checklist.py" --all
    status_snapshot
    ;;

  gate)
    require_audit
    log "Running PoC completeness gate..."
    run_step "analyze_poc_completeness" "${PYTHON}" "${ROOT}/scripts/analyze_poc_completeness.py" --all
    status_snapshot
    ;;

  full)
    require_audit
    log "=== Full pipeline run (Steps 2.5 → 4, then PAUSE) ==="
    log "Assumes Step 2 specialist findings already exist in output/findings_*.json"
    log "If not, run: ./run_pipeline.sh analyze <contract> then /ite-audit in Claude Code"
    log "After this command pauses, reply with PoC finding IDs, then:"
    log "  ./run_pipeline.sh poc <finding-id>"
    log ""

    log "Step 2.5: Cross-agent connector (annotates threads, finds chains)..."
    run_step "cross_agent_connector" "${PYTHON}" "${ROOT}/scripts/cross_agent_connector.py"
    "${PYTHON}" "${ROOT}/scripts/update_session.py" --step "2.5" 2>/dev/null || true

    log "Step 3: Compound synthesis + report merge..."
    run_step "synthesize_compound_findings" "${PYTHON}" "${ROOT}/scripts/synthesize_compound_findings.py"
    run_step "report_generator"             "${PYTHON}" "${ROOT}/tools/report_generator.py"
    populate_finding_metadata
    "${PYTHON}" "${ROOT}/scripts/update_session.py" --step "3" 2>/dev/null || true
    status_snapshot

    log "Step 3.4: Impact chain escalation..."
    run_step "run_impact_chain_escalation" "${PYTHON}" "${ROOT}/scripts/run_impact_chain_escalation.py"
    "${PYTHON}" "${ROOT}/scripts/update_session.py" --step "3.4" 2>/dev/null || true

    log "Step 3.5: Multi-pass confirmation (High/Critical only)..."
    run_step "multi_pass_confirm" "${PYTHON}" "${ROOT}/scripts/multi_pass_confirm.py"
    "${PYTHON}" "${ROOT}/scripts/update_session.py" --step "3.5" 2>/dev/null || true

    log "Step 3.6: FP pattern check..."
    run_step "fp_pattern_check" "${PYTHON}" "${ROOT}/scripts/fp_pattern_check.py" --all
    "${PYTHON}" "${ROOT}/scripts/update_session.py" --step "3.6" 2>/dev/null || true

    log "Step 3.7: Pre-submission gate (8 hard-reject gates)..."
    run_step "pre_submission_gate" "${PYTHON}" "${ROOT}/scripts/pre_submission_gate.py" --all
    "${PYTHON}" "${ROOT}/scripts/update_session.py" --step "3.7" 2>/dev/null || true

    log "Step 3.8: Public-report duplicate screen..."
    run_step "pre_submission_dupe_screen" "${PYTHON}" "${ROOT}/scripts/pre_submission_dupe_screen.py" --all
    "${PYTHON}" "${ROOT}/scripts/update_session.py" --step "3.8" 2>/dev/null || true
    status_snapshot

    log "Step 4: Triage..."
    run_step "triage_findings"        "${PYTHON}" "${ROOT}/scripts/triage_findings.py"
    run_step "validate_triage_output" "${PYTHON}" "${ROOT}/scripts/validate_triage_output.py" --fix
    run_step "build_poc_queue"        "${PYTHON}" "${ROOT}/scripts/build_poc_queue.py"
    run_step "register_pc_findings"   "${PYTHON}" "${ROOT}/scripts/register_pc_findings.py" --apply
    "${PYTHON}" "${ROOT}/scripts/update_session.py" --step "4" 2>/dev/null || true

    log "Step 4.5: Human review classification..."
    run_step "human_review_classifier" "${PYTHON}" "${ROOT}/scripts/human_review_classifier.py"
    "${PYTHON}" "${ROOT}/scripts/update_session.py" --step "4.5" 2>/dev/null || true
    status_snapshot

    log "Step 4 gate: Writing review_gate.md and pausing pipeline..."
    # generate_review_gate.py exits 0 after printing the pause message — this is intentional.
    # Steps 5–9 (PoC → submit) do NOT run automatically. Resume with:
    #   ./run_pipeline.sh poc <finding-id>    (one finding)
    #   ./run_pipeline.sh poc-all             (all poc_required)
    "${PYTHON}" "${ROOT}/scripts/generate_review_gate.py"
    exit 0
    ;;

  submit)
    # Steps 5–9: run AFTER user reviews review_gate.md and confirms PoC finding IDs.
    require_audit
    log "=== Submit pipeline (Steps 5 → 9) ==="
    log "Run this only after reviewing output/review_gate.md."
    log ""

    log "Step 5: Specialist review..."
    run_step "run_specialist_review" "${PYTHON}" "${ROOT}/scripts/run_specialist_review.py"
    run_step "final_submission_pack" "${PYTHON}" "${ROOT}/scripts/final_submission_pack.py"
    status_snapshot

    log "Step 6: PoC (all eligible)..."
    run_step "run_integrated_poc"    "${PYTHON}" "${ROOT}/scripts/run_integrated_poc.py" --all
    run_step "summarize_poc_results" "${PYTHON}" "${ROOT}/scripts/summarize_poc_results.py" \
      --out "reports/poc_evidence.md"
    status_snapshot

    log "Step 7: Quality checklist..."
    run_step "run_quality_checklist" "${PYTHON}" "${ROOT}/scripts/run_quality_checklist.py" --all
    status_snapshot

    log "Step 8: PoC completeness gate..."
    run_step "analyze_poc_completeness" "${PYTHON}" "${ROOT}/scripts/analyze_poc_completeness.py" --all
    status_snapshot

    log "Step 9: Final submission pack..."
    run_step "final_submission_pack" "${PYTHON}" "${ROOT}/scripts/final_submission_pack.py"
    status_snapshot

    log ""
    log "=== Submit pipeline complete ==="
    log "Results:"
    log "  Submit-ready: audits/${AUDIT_ID}/data/triage/submit.jsonl"
    log "  Human review: audits/${AUDIT_ID}/data/triage/human_review_queue.jsonl"
    log "  Submission:   audits/${AUDIT_ID}/output/submission_pack.md"
    log "  Dashboard:    python scripts/dashboard.py  (http://localhost:8765)"
    ;;

  *)
    cat >&2 << 'USAGE'
Usage: ./run_pipeline.sh <command> [arg]

Full audit flow:
  1. analyze <contract>   Steps 0.5→1.5 (sandbox, scope inventory, deep analysis, static, defense, context pack)
  2. /ite-audit           Step 2 specialist agents (run inside Claude Code)
  3. full                 Steps 2.5→4 (cross-agent → gates → triage → PAUSE at review_gate.md)
  4. poc <finding-id>     PoC for selected findings (one at a time, after reviewing review_gate.md)
  5. submit               Steps 5→9 (specialist review → PoC all → QC → completeness gate → pack)

Other commands:
  status                  Print compact audit status
  test [finding-id]       Run Rust PoC tests
  triage                  Quick compound synthesis + triage (partial; full preferred)
  specialist              Run specialist review (Step 5 only)
  poc-all                 Integrated PoC for all eligible findings
  package [finding-id]    Build submission pack
  checklist               Quality checklist for all proved findings
  gate                    PoC completeness gate (Step 8)

Reference: docs/pipeline_reference.md — full step details, gate rules, PoC levels
USAGE
    exit 1
    ;;

esac
