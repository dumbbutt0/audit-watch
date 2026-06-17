#!/usr/bin/env bash
# run_pipeline.sh — Audit Watch pipeline runner (single-user)
#
# Full audit flow:
#   1. ./run_pipeline.sh analyze <contract>   — Steps 0.5→1 + deep-analysis prepare
#      (API-FREE) pauses here → run /deep-analysis skill → ./run_pipeline.sh analyze-resume <contract>
#   2. /ite-audit                             — Step 2 specialist agents (in Claude Code)
#   3. ./run_pipeline.sh full                 — Steps 2.5→4 (synthesis → gates → triage → PAUSE at review_gate.md)
#      (API-FREE) triage pauses → run /triage skill → python scripts/triage_write.py → ./run_pipeline.sh review-gate
#      [Review review_gate.md, pick PoC finding IDs]
#   4. ./run_pipeline.sh poc <finding-id>     — PoC for selected findings (L1/L2/L3)
#   5. ./run_pipeline.sh submit               — Steps 5→9 (specialist review → QC → pack)
#
#   analyze-resume <contract>                 — finish Steps 0→1.5 after the /deep-analysis skill (API-FREE)
#
# Coverage system (deterministic denominator + hard review gate; see documentation/coverage_system.md):
#   coverage-manifest [contract]              — build coverage_manifest.json + init dispositions
#   coverage-sweep                            — prepare long-tail bundles → run /coverage-sweep skill → coverage_sweep_write.py
#   coverage-gate                             — run the coverage completeness + min-confirm gates (nonzero = block)
#   coverage-drive [--no-rebuild]             — DRIVE coverage to 100%: manifest+link+gate, auto-stage the sweep on a
#                                               gap, print the resumable /coverage-sweep loop (the review gate now does
#                                               this by default on a block; fail-closed)
#   coverage-status                           — print coverage metrics (coverage% vs detection)
#   deep-pass-queue                           — cluster the needs_deep_pass backlog into specialist packets (soft, not a gate)
#   NOTE: `full` and `review-gate` now run Step 3.9 (coverage_review_gate) and BLOCK the review gate
#         until every in-scope manifest item has an evidence-anchored disposition.
#
# Precision / reachability-truth confirm (MANUAL; NOT wired into eval/full — see documentation/pipeline_modes.md):
#   confirm-advisory                          — eval-mode reachability confirm: ADVISORY only, never blocks (exit 0)
#   submission-confirm [--strict]             — real-report precision gate: min-confirm + reachability confirm;
#                                               BLOCKS (exit 1) duplicate/unreachable/privileged/insufficient High claims
#
# Other commands:
#   ./run_pipeline.sh status                  — print compact status
#   ./run_pipeline.sh test [finding-id]       — run forge/cargo tests
#   ./run_pipeline.sh triage                  — quick triage (compound + triage_findings only)
#   ./run_pipeline.sh fuzz                     — P141: normalize + cause-confirm harness-fuzz signals into the
#                                                confirmed evidence set the fuzz_attacker_synthesis specialist reads
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

# Step 3.9 — hard coverage + min-confirmation gate. Blocks the review gate unless every in-scope
# manifest item has a valid (evidence-anchored) disposition and every submission candidate carries
# its confirmation skeleton. Additive to the existing gates. Override envs documented in the die msg.
coverage_review_gate() {
  log "Step 3.9: Coverage completeness + min-confirmation gate..."
  run_step "link_findings_to_manifest" "${PYTHON}" "${ROOT}/scripts/link_findings_to_manifest.py" --quiet
  "${PYTHON}" "${ROOT}/scripts/coverage_metrics.py" --quiet 2>/dev/null || true

  # Canonical per-finding record: join merged_findings + gates + confirmation + triage + poc into ONE record per
  # finding (output/candidates/<id>.json) with a single derived `state`. This is where READY is defined and where
  # unconfirmed High/Critical are routed to human_pending. The dashboard/report should read this, not re-join.
  # ADVISORY-ONLY pre-READY submission-risk flags (reachability/novelty/design). Runs BEFORE the canonical
  # record so it can overlay readiness_advisories; never changes finding state, never gates.
  "${PYTHON}" "${ROOT}/scripts/submission_risk_audit.py" --quiet 2>/dev/null || true

  run_step "build_candidate_records" "${PYTHON}" "${ROOT}/scripts/build_candidate_records.py"

  # MEASUREMENT-ONLY: attribute advisory-lens hits to the findings they became (canonical state), so lens
  # LIVE value is measurable instead of guessed (review J5). Never routes/gates/sets severity; pure read-only.
  "${PYTHON}" "${ROOT}/scripts/advisory_lens_attribution.py" --quiet 2>/dev/null || true

  # Step 3.85 — MANDATORY full-coverage drive (reach every necessary file). Specialists deep-dive the hot
  # clusters; this guarantees EVERY remaining in-scope manifest item is examined with evidence before the
  # review gate. Proactively (re)stage the long-tail sweep over ALL in-scope items so the drive loop is always
  # runnable — staging is idempotent and changes no dispositions. The hard coverage_completeness_gate below
  # fail-closes until coverage is 100%; this phase just makes the sweep an explicit, always-staged step.
  log "Step 3.85: Mandatory full-coverage drive (examine all necessary in-scope files)..."
  run_step "coverage_sweep_prepare" "${PYTHON}" "${ROOT}/scripts/coverage_sweep_prepare.py" 2>/dev/null || true
  if [[ "${AUDITWATCH_COVERAGE_OVERRIDE:-0}" == "1" ]]; then
    log "============================================================"
    log "WARNING: AUDITWATCH_COVERAGE_OVERRIDE=1 is set."
    log "WARNING: the necessary-file coverage gate is being OVERRIDDEN —"
    log "WARNING: this audit may complete BELOW 100% necessary-file coverage."
    log "WARNING: bugs can be missed because a file was never examined. Not recommended."
    log "============================================================"
  fi
  # Advisory recall lenses (never block): surface cross-artifact lifecycle, recipient/custody, cross-function
  # boundary invariants, asset-source/amount-origin mismatch, and checkpoint/queue liveness risks. Run BEFORE
  # the completeness gate so the advisory-escalation step can re-open the gate on high-risk thin clears.
  "${PYTHON}" "${ROOT}/scripts/cross_artifact_lifecycle_audit.py" 2>/dev/null || true
  "${PYTHON}" "${ROOT}/scripts/recipient_custody_audit.py" 2>/dev/null || true
  "${PYTHON}" "${ROOT}/scripts/cross_function_invariant_audit.py" 2>/dev/null || true
  "${PYTHON}" "${ROOT}/scripts/asset_source_consistency_audit.py" 2>/dev/null || true
  "${PYTHON}" "${ROOT}/scripts/checkpoint_liveness_audit.py" 2>/dev/null || true
  "${PYTHON}" "${ROOT}/scripts/abi_getter_mismatch_audit.py" 2>/dev/null || true
  "${PYTHON}" "${ROOT}/scripts/arithmetic_conservation_audit.py" 2>/dev/null || true
  "${PYTHON}" "${ROOT}/scripts/connector_position_accounting_audit.py" 2>/dev/null || true
  "${PYTHON}" "${ROOT}/scripts/liquidation_health_accounting_audit.py" 2>/dev/null || true
  # P136: units/decimals advisory input for the review-gate advisory surfacing (report-only, never blocks/routes).
  "${PYTHON}" "${ROOT}/scripts/units_invariant_audit.py" 2>/dev/null || true
  # P311: promoted recall lenses (ADVISORY-ONLY — surfaced in advisory_escalation_gate, never auto-route/gate).
  "${PYTHON}" "${ROOT}/scripts/nonstandard_permit_audit.py" 2>/dev/null || true
  "${PYTHON}" "${ROOT}/scripts/erc4626_limit_fidelity_audit.py" 2>/dev/null || true
  "${PYTHON}" "${ROOT}/scripts/eip712_domain_separator_staleness_audit.py" 2>/dev/null || true
  "${PYTHON}" "${ROOT}/scripts/beneficiary_guard_parity_audit.py" 2>/dev/null || true
  "${PYTHON}" "${ROOT}/scripts/admin_capability_parity_audit.py" 2>/dev/null || true
  "${PYTHON}" "${ROOT}/scripts/crosschain_min_gas_unchecked_audit.py" 2>/dev/null || true
  "${PYTHON}" "${ROOT}/scripts/crosschain_refund_recipient_audit.py" 2>/dev/null || true
  "${PYTHON}" "${ROOT}/scripts/fee_wrapper_bypass_audit.py" 2>/dev/null || true
  # Route high-risk advisory hits on currently-cleared high-risk surfaces → needs_deep_pass (strict full-audit
  # only; override AUDITWATCH_ADVISORY_ESCALATION_OVERRIDE=1). Prefer a deep pass over a thin clear.
  "${PYTHON}" "${ROOT}/scripts/advisory_escalation_gate.py" || true
  # Refresh the prioritized deep-pass queue (tiers 1-6) + budget ledger, and check mandatory specialist
  # coverage by target profile. Advisory here (warn only); the freeze-check command enforces both.
  "${PYTHON}" "${ROOT}/scripts/deep_pass_queue.py" >/dev/null 2>&1 || true
  "${PYTHON}" "${ROOT}/scripts/deep_pass_ledger.py" --quiet || true
  "${PYTHON}" "${ROOT}/scripts/specialist_coverage_gate.py" || true
  if ! "${PYTHON}" "${ROOT}/scripts/coverage_completeness_gate.py"; then
    # Coverage-drive default (P310): on a block, auto-stage the long-tail sweep so the drive loop is immediately
    # runnable, then fail closed with the resumable instructions. Staging is idempotent and changes no dispositions.
    run_step "coverage_sweep_prepare" "${PYTHON}" "${ROOT}/scripts/coverage_sweep_prepare.py"
    die "Coverage gate failed — NOT every necessary (in-scope) file has been examined (or a high-risk thin clear was routed to needs_deep_pass by the advisory-escalation step). The full workflow will not produce a clean review gate below 100% necessary-file coverage. DRIVE coverage to 100% (mandatory-sweep bundles staged in output/coverage_sweep/): (1) run the /coverage-sweep skill, (2) python scripts/coverage_sweep_write.py, (3) re-run ./run_pipeline.sh review-gate — loops until 0 unexamined. Deep-assign high-surface items instead of cheap-clearing; clears require evidence. See output/coverage_gate.json + output/advisory_escalation_gate.json. Override (not recommended, logged): AUDITWATCH_COVERAGE_OVERRIDE=1"
  fi
  if ! "${PYTHON}" "${ROOT}/scripts/min_confirm_gate.py"; then
    die "Min-confirmation gate failed — submission candidates missing confirmation fields (entrypoint/manifest_refs/preconditions/impact/guards/PoC/severity/confidence). See output/min_confirm_gate.json. Override: AUDITWATCH_MINCONFIRM_OVERRIDE=1"
  fi
  # No-silent-drop guard for bridge-relevant deep-analysis threads (blocks only in strict/full-audit).
  if ! "${PYTHON}" "${ROOT}/scripts/bridge_thread_escalation_gate.py"; then
    die "Bridge thread escalation gate failed — a bridge-relevant deep-analysis thread was dropped without escalation or a concrete invalidation (exact sink + attacker entrypoint + unreachable/bounded/subsumed reason). See output/bridge_thread_escalation_gate.json; record invalidations via scripts/bridge_thread_disposition_write.py. Override: AUDITWATCH_BRIDGE_THREAD_OVERRIDE=1"
  fi
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

    if "${PYTHON}" "${ROOT}/scripts/llm_runtime.py" --have-key; then HAS_KEY=1; else HAS_KEY=0; fi

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

    # Static runs before deep analysis so the deep-analysis stage has static.json flags.
    log "Step 1: Static analysis + test coverage..."
    run_step "static_analysis"       "${PYTHON}" "${ROOT}/tools/static_analysis.py" "${CONTRACT}"
    run_step "analyze_test_coverage" "${PYTHON}" "${ROOT}/scripts/analyze_test_coverage.py" \
      --contract "${CONTRACT}" --tests test/
    "${PYTHON}" "${ROOT}/scripts/update_session.py" --step "1" 2>/dev/null || true
    status_snapshot

    log "Step 0: Deep invariant analysis (stages 0a–0f)..."
    if [[ "${HAS_KEY}" == "1" ]]; then
      run_step "run_deep_analysis" "${PYTHON}" "${ROOT}/scripts/run_deep_analysis.py" \
        --contract "${CONTRACT}" --mode deep
      "${PYTHON}" "${ROOT}/scripts/update_session.py" --step "0" 2>/dev/null || true
      status_snapshot
    else
      log "API-FREE MODE — preparing the /deep-analysis bundle (no API)..."
      run_step "deep_analysis_prepare" "${PYTHON}" "${ROOT}/scripts/deep_analysis_prepare.py" \
        --contract "${CONTRACT}" --mode deep
      "${PYTHON}" "${ROOT}/scripts/update_session.py" --step "0-deep-prepare" 2>/dev/null || true
      log "============================================================"
      log "API-FREE PAUSE — deep-analysis bundle ready (data/invariants/_bundles/)."
      log "Finish Step 0 WITHOUT spending API credits:"
      log "  1. In Claude Code, run the /deep-analysis skill (reasons over the bundle in-session)."
      log "  2. ./run_pipeline.sh analyze-resume ${CONTRACT}   # validates Step 0 + finishes Steps 0.25→1.5"
      log "============================================================"
      exit 0
    fi

    # Steps 0.25 → 1.5 (api-free path runs these in 'analyze-resume' after the /deep-analysis skill).
    log "Step 0.25: Attacker mindset brief..."
    run_step "generate_step0_brief" "${PYTHON}" "${ROOT}/scripts/generate_step0_brief.py"
    "${PYTHON}" "${ROOT}/scripts/update_session.py" --step "0.25" 2>/dev/null || true

    log "Step 1.5: Defense mapper + context pack..."
    run_step "defense_mapper"        "${PYTHON}" "${ROOT}/scripts/defense_mapper.py" --contract "${CONTRACT}"
    run_step "generate_context_pack" "${PYTHON}" "${ROOT}/scripts/generate_context_pack.py" --contract "${CONTRACT}"
    "${PYTHON}" "${ROOT}/scripts/update_session.py" --step "1.5" 2>/dev/null || true
    status_snapshot

    log "Step 1.6: Coverage manifest + dispositions (full review denominator)..."
    run_step "build_coverage_manifest"   "${PYTHON}" "${ROOT}/scripts/build_coverage_manifest.py" --contract "${CONTRACT}"
    run_step "init_coverage_dispositions" "${PYTHON}" "${ROOT}/scripts/init_coverage_dispositions.py"

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

  analyze-resume)
    # API-free resume: validate the artifacts the /deep-analysis skill wrote, then finish Steps 0.25→1.5.
    require_audit
    CONTRACT="${ARG}"
    if [[ -z "${CONTRACT}" ]]; then
      CONTRACT="$("${PYTHON}" -c "
import json,sys
from pathlib import Path
m = Path('${ROOT}/audits/${AUDIT_ID}/meta.json')
print(json.loads(m.read_text()).get('contract_path','') if m.exists() else '')
")"
    fi
    [[ -z "${CONTRACT}" ]] && die "Could not resolve contract path. Run: ./run_pipeline.sh analyze-resume <contract_path>"

    log "=== Resuming analyze after /deep-analysis (validate Step 0 → finish Steps 0.25→1.5) ==="

    log "Step 0: Validate deep-analysis artifacts..."
    if ! "${PYTHON}" "${ROOT}/scripts/deep_analysis_write.py"; then
      die "Deep-analysis artifacts incomplete. Run the /deep-analysis skill, then retry analyze-resume."
    fi
    "${PYTHON}" "${ROOT}/scripts/update_session.py" --step "0" 2>/dev/null || true
    status_snapshot

    log "Step 0.25: Attacker mindset brief..."
    run_step "generate_step0_brief" "${PYTHON}" "${ROOT}/scripts/generate_step0_brief.py"
    "${PYTHON}" "${ROOT}/scripts/update_session.py" --step "0.25" 2>/dev/null || true

    log "Step 1.5: Defense mapper + context pack..."
    run_step "defense_mapper"        "${PYTHON}" "${ROOT}/scripts/defense_mapper.py" --contract "${CONTRACT}"
    run_step "generate_context_pack" "${PYTHON}" "${ROOT}/scripts/generate_context_pack.py" --contract "${CONTRACT}"
    "${PYTHON}" "${ROOT}/scripts/update_session.py" --step "1.5" 2>/dev/null || true
    status_snapshot

    log "Step 1.6: Coverage manifest + dispositions (full review denominator)..."
    run_step "build_coverage_manifest"   "${PYTHON}" "${ROOT}/scripts/build_coverage_manifest.py" --contract "${CONTRACT}"
    run_step "init_coverage_dispositions" "${PYTHON}" "${ROOT}/scripts/init_coverage_dispositions.py"

    log "Step 1.7: Fuzz-lane evidence gate (normalize + cause-confirm any harness signals)..."
    run_step "fuzz_evidence_gate" "${PYTHON}" "${ROOT}/scripts/fuzz_evidence_gate.py" --summary

    log ""
    log "=== Pre-analysis complete (api-free). Next steps: ==="
    log "  1. Review: cat audits/${AUDIT_ID}/output/step0_brief.md"
    log "  2. (optional) Deep harness fuzzing: run harnesses (run_move_fuzz.py / run_differential_fuzz.py /"
    log "     generate_fuzzing_harness.py) then: ./run_pipeline.sh fuzz   # re-derives confirmed evidence"
    log "  3. In Claude Code, run: /ite-audit   (Step 2 specialists + fuzz_attacker_synthesis) + /supply-chain"
    log "  4. When specialists finish: ./run_pipeline.sh full"
    log ""
    ;;

  fuzz)
    # P141 fuzz lane: (re)derive the confirmed harness-fuzz evidence set the fuzz_attacker_synthesis specialist
    # consumes. Run the harness runners FIRST (run_move_fuzz.py / run_differential_fuzz.py / generate_fuzzing_
    # harness.py --run-echidna) to populate data/fuzz_results/raw/, then this normalizes + cause-confirms them.
    require_audit
    run_step "fuzz_evidence_gate" "${PYTHON}" "${ROOT}/scripts/fuzz_evidence_gate.py"
    log ""
    log "Confirmed signals (if any) are now in data/fuzz_results/divergences.jsonl (status=confirmed)."
    log "They are consumed by the fuzz_attacker_synthesis specialist during /ite-audit, then ride the normal"
    log "FP gauntlet (ICE -> multi-pass -> fp_pattern_check -> 8 gates -> dupe -> confirm -> triage) UNCHANGED."
    ;;

  confirm-prepare)
    # Stage multi-pass confirmation bundles for the credit-free /confirm skill (api-free Step 3.5).
    require_audit
    run_step "confirm_prepare" "${PYTHON}" "${ROOT}/scripts/confirm_prepare.py" "${@:2}"
    ;;

  confirm-write)
    # Persist the /confirm skill's decisions into output/findings_confirmed.json (same schema as multi_pass).
    require_audit
    run_step "confirm_write" "${PYTHON}" "${ROOT}/scripts/confirm_write.py" "${@:2}"
    run_step "build_candidate_records" "${PYTHON}" "${ROOT}/scripts/build_candidate_records.py"
    ;;

  candidates)
    # (Re)build the canonical per-finding records (output/candidates/<id>.json + candidates_index.json).
    require_audit
    run_step "build_candidate_records" "${PYTHON}" "${ROOT}/scripts/build_candidate_records.py"
    ;;

  submission-risk)
    # ADVISORY-ONLY: flag findings likely to bounce at bounty triage on reachability/novelty/design axes
    # (output/submission_risk.json). Never changes state, never gates. checklist_required -> submission_risk_review.
    require_audit
    "${PYTHON}" "${ROOT}/scripts/submission_risk_audit.py"
    ;;

  calibration-worklist)
    # READ-ONLY: enumerate real-world accepted findings with no recorded outcome + emit record_outcome.py
    # stubs (documentation/metrics/outcome_worklist.md). Closing them moves FP/recall off 'unmeasured'.
    "${PYTHON}" "${ROOT}/scripts/calibration_worklist.py"
    ;;

  advisory-lens-value)
    # MEASUREMENT-ONLY: per-audit attribution (default) or --rollup the cross-audit lens-value table
    # (evals/advisory_lens_value.md) — the artifact a future review reads to decide keep-vs-shelve (J5).
    if [[ "${2:-}" == "--rollup" ]]; then
      "${PYTHON}" "${ROOT}/scripts/advisory_lens_attribution.py" --rollup
    else
      require_audit
      "${PYTHON}" "${ROOT}/scripts/advisory_lens_attribution.py"
    fi
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
    log "--- LLM pre-flight (which steps need a key / have a skill fallback) ---"
    "${PYTHON}" "${ROOT}/scripts/llm_runtime.py" cross_agent_connector synthesize_compound multi_pass_confirm triage >&2 || true
    if "${PYTHON}" "${ROOT}/scripts/llm_runtime.py" --have-key; then HAS_KEY=1; else HAS_KEY=0; fi
    if [[ "${HAS_KEY}" == "0" ]]; then
      log "API-FREE MODE (config/runtime_policy.json api_free, or no ANTHROPIC_API_KEY):"
      log "  optional enhancers (2.5 cross-agent, 3 compound, 3.5 multi-pass) SKIP cleanly;"
      log "  Step 4 triage runs via the /triage skill in-session."
      log "  Nothing will silently fail or spend credits."
    fi
    log "----------------------------------------------------------------------"
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
    if [[ "${HAS_KEY}" == "1" ]]; then
      run_step "multi_pass_confirm" "${PYTHON}" "${ROOT}/scripts/multi_pass_confirm.py"
    else
      # api-free: the python confirmer would SKIP and leave High/Critical unconfirmed. Stage bundles for the
      # /confirm skill instead (confirm_prepare prints the next steps if any High/Critical were staged). Until
      # confirmation exists, build_candidate_records routes High/Critical to human_pending (NOT ready) — so
      # nothing unconfirmed can look submission-ready.
      run_step "confirm_prepare" "${PYTHON}" "${ROOT}/scripts/confirm_prepare.py"
    fi
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

    if [[ "${HAS_KEY}" == "1" ]]; then
      log "Step 4: Triage (API)..."
      run_step "triage_findings" "${PYTHON}" "${ROOT}/scripts/triage_findings.py"
    else
      log "Step 4: Triage (zero-API) — preparing per-finding bundles for the /triage skill..."
      run_step "triage_prepare" "${PYTHON}" "${ROOT}/scripts/triage_prepare.py"
      log ""
      log "============================================================"
      log "ZERO-API PAUSE — triage bundles ready in data/triage/_bundles/."
      log "Finish triage WITHOUT spending API credits:"
      log "  1. In Claude Code, run the /triage skill (reasons over the bundles in-session)."
      log "  2. python scripts/triage_write.py     # writes the canonical triage buckets"
      log "  3. ./run_pipeline.sh review-gate      # builds PoC queue + review_gate.md, then pauses"
      log "============================================================"
      exit 0
    fi
    run_step "validate_triage_output" "${PYTHON}" "${ROOT}/scripts/validate_triage_output.py" --fix
    run_step "build_poc_queue"        "${PYTHON}" "${ROOT}/scripts/build_poc_queue.py"
    run_step "register_pc_findings"   "${PYTHON}" "${ROOT}/scripts/register_pc_findings.py" --apply
    "${PYTHON}" "${ROOT}/scripts/update_session.py" --step "4" 2>/dev/null || true

    log "Step 4.5: Human review classification..."
    run_step "human_review_classifier" "${PYTHON}" "${ROOT}/scripts/human_review_classifier.py"
    "${PYTHON}" "${ROOT}/scripts/update_session.py" --step "4.5" 2>/dev/null || true
    status_snapshot

    coverage_review_gate

    log "Step 4 gate: Writing review_gate.md and pausing pipeline..."
    # generate_review_gate.py exits 0 after printing the pause message — this is intentional.
    # Steps 5–9 (PoC → submit) do NOT run automatically. Resume with:
    #   ./run_pipeline.sh poc <finding-id>    (one finding)
    #   ./run_pipeline.sh poc-all             (all poc_required)
    # P136: surface existing mechanism-detector hits as ADVISORY review_context (never blocks, never
    # submission-ready; master switch config/agent_policy.json mechanism_advisory.surface_mechanism_advisories).
    "${PYTHON}" "${ROOT}/scripts/surface_mechanism_advisories.py" 2>/dev/null || true
    # P139: auto-route H-03-class value-provenance deep-pass jobs (advisory-only, scaffold; never blocks).
    "${PYTHON}" "${ROOT}/scripts/run_value_provenance_advisories.py" 2>/dev/null || true
    # P140: fold any on-disk manual deep-pass completion artifacts back in (deterministic, advisory-only; never blocks).
    "${PYTHON}" "${ROOT}/scripts/run_value_provenance_advisories.py" --ingest-results 2>/dev/null || true
    "${PYTHON}" "${ROOT}/scripts/generate_review_gate.py"
    exit 0
    ;;

  review-gate)
    # Zero-API resume: run after the /triage skill + triage_write.py have written the buckets.
    # Completes Step 4 post-triage work (PoC queue, human review) and writes review_gate.md.
    require_audit
    log "=== Finishing Step 4 → review gate (post-/triage resume, no API) ==="
    run_step "validate_triage_output"  "${PYTHON}" "${ROOT}/scripts/validate_triage_output.py" --fix
    run_step "build_poc_queue"         "${PYTHON}" "${ROOT}/scripts/build_poc_queue.py"
    run_step "register_pc_findings"    "${PYTHON}" "${ROOT}/scripts/register_pc_findings.py" --apply
    "${PYTHON}" "${ROOT}/scripts/update_session.py" --step "4" 2>/dev/null || true
    log "Step 4.5: Human review classification..."
    run_step "human_review_classifier" "${PYTHON}" "${ROOT}/scripts/human_review_classifier.py"
    "${PYTHON}" "${ROOT}/scripts/update_session.py" --step "4.5" 2>/dev/null || true
    status_snapshot

    coverage_review_gate

    log "Step 4 gate: Writing review_gate.md and pausing pipeline..."
    # P136: surface mechanism-detector hits as ADVISORY review_context (non-blocking, advisory-only).
    "${PYTHON}" "${ROOT}/scripts/surface_mechanism_advisories.py" 2>/dev/null || true
    # P139: auto-route H-03-class value-provenance deep-pass jobs (advisory-only, scaffold; never blocks).
    "${PYTHON}" "${ROOT}/scripts/run_value_provenance_advisories.py" 2>/dev/null || true
    # P140: fold any on-disk manual deep-pass completion artifacts back in (deterministic, advisory-only; never blocks).
    "${PYTHON}" "${ROOT}/scripts/run_value_provenance_advisories.py" --ingest-results 2>/dev/null || true
    "${PYTHON}" "${ROOT}/scripts/generate_review_gate.py"
    exit 0
    ;;

  coverage-manifest)
    # Build the full review denominator + initialize dispositions (deterministic, no API).
    require_audit
    CONTRACT="${ARG}"
    if [[ -z "${CONTRACT}" ]]; then
      CONTRACT="$("${PYTHON}" -c "
import json
from pathlib import Path
m = Path('${ROOT}/audits/${AUDIT_ID}/meta.json')
print(json.loads(m.read_text()).get('contract_path','') if m.exists() else '')
")"
    fi
    run_step "build_coverage_manifest"   "${PYTHON}" "${ROOT}/scripts/build_coverage_manifest.py" ${CONTRACT:+--contract "${CONTRACT}"}
    run_step "init_coverage_dispositions" "${PYTHON}" "${ROOT}/scripts/init_coverage_dispositions.py"
    ;;

  coverage-gate)
    # Run the coverage completeness + min-confirmation gates standalone (exit nonzero on block).
    require_audit
    "${PYTHON}" "${ROOT}/scripts/link_findings_to_manifest.py" --quiet 2>/dev/null || true
    # advisory recall lenses + high-risk escalation (route thin clears on high-risk surfaces → needs_deep_pass)
    "${PYTHON}" "${ROOT}/scripts/cross_function_invariant_audit.py" 2>/dev/null || true
    "${PYTHON}" "${ROOT}/scripts/asset_source_consistency_audit.py" 2>/dev/null || true
    "${PYTHON}" "${ROOT}/scripts/checkpoint_liveness_audit.py" 2>/dev/null || true
    "${PYTHON}" "${ROOT}/scripts/abi_getter_mismatch_audit.py" 2>/dev/null || true
  "${PYTHON}" "${ROOT}/scripts/arithmetic_conservation_audit.py" 2>/dev/null || true
  "${PYTHON}" "${ROOT}/scripts/connector_position_accounting_audit.py" 2>/dev/null || true
  "${PYTHON}" "${ROOT}/scripts/liquidation_health_accounting_audit.py" 2>/dev/null || true
    # P311: promoted recall lenses (ADVISORY-ONLY — surfaced, never auto-route/gate)
    "${PYTHON}" "${ROOT}/scripts/nonstandard_permit_audit.py" 2>/dev/null || true
    "${PYTHON}" "${ROOT}/scripts/erc4626_limit_fidelity_audit.py" 2>/dev/null || true
    "${PYTHON}" "${ROOT}/scripts/eip712_domain_separator_staleness_audit.py" 2>/dev/null || true
    "${PYTHON}" "${ROOT}/scripts/beneficiary_guard_parity_audit.py" 2>/dev/null || true
    "${PYTHON}" "${ROOT}/scripts/admin_capability_parity_audit.py" 2>/dev/null || true
    "${PYTHON}" "${ROOT}/scripts/crosschain_min_gas_unchecked_audit.py" 2>/dev/null || true
    "${PYTHON}" "${ROOT}/scripts/crosschain_refund_recipient_audit.py" 2>/dev/null || true
    "${PYTHON}" "${ROOT}/scripts/fee_wrapper_bypass_audit.py" 2>/dev/null || true
    "${PYTHON}" "${ROOT}/scripts/advisory_escalation_gate.py" || true
    "${PYTHON}" "${ROOT}/scripts/coverage_completeness_gate.py"; cov=$?
    "${PYTHON}" "${ROOT}/scripts/min_confirm_gate.py"; mc=$?
    "${PYTHON}" "${ROOT}/scripts/bridge_thread_escalation_gate.py"; bt=$?
    [[ ${cov} -eq 0 && ${mc} -eq 0 && ${bt} -eq 0 ]] || exit 1
    ;;

  coverage-status)
    require_audit
    "${PYTHON}" "${ROOT}/scripts/coverage_metrics.py"
    ;;

  coverage-drive)
    # P310: drive coverage toward 100% (production scripts only — mirrors scripts/research/coverage_drive.py).
    # Refresh the denominator from SOURCE, link findings, report the gate, and (if any in-scope item is unexamined)
    # stage the /coverage-sweep loop + print the resumable next step. Report/drive helper: always exits 0 — the
    # review gate (full/review-gate) is the hard fail-closed block. Pass --no-rebuild to skip the manifest rebuild.
    require_audit
    if [[ "${ARG}" != "--no-rebuild" ]]; then
      CONTRACT="$("${PYTHON}" -c "
import json
from pathlib import Path
m = Path('${ROOT}/audits/${AUDIT_ID}/meta.json')
print(json.loads(m.read_text()).get('contract_path','') if m.exists() else '')
")"
      run_step "build_coverage_manifest" "${PYTHON}" "${ROOT}/scripts/build_coverage_manifest.py" ${CONTRACT:+--contract "${CONTRACT}"}
    fi
    run_step "init_coverage_dispositions" "${PYTHON}" "${ROOT}/scripts/init_coverage_dispositions.py"
    run_step "link_findings_to_manifest"  "${PYTHON}" "${ROOT}/scripts/link_findings_to_manifest.py" --quiet
    "${PYTHON}" "${ROOT}/scripts/coverage_completeness_gate.py" || true
    UNEXAMINED="$("${PYTHON}" -c "
import json
from pathlib import Path
p = Path('${ROOT}/audits/${AUDIT_ID}/output/coverage_gate.json')
s = json.loads(p.read_text()).get('summary', {}) if p.exists() else {}
print(s.get('unassigned', 0) + s.get('assigned_only', 0) + s.get('examined', 0))
" 2>/dev/null || echo 0)"
    if [[ "${UNEXAMINED}" -gt 0 ]]; then
      run_step "coverage_sweep_prepare" "${PYTHON}" "${ROOT}/scripts/coverage_sweep_prepare.py"
      log "coverage-drive: ${UNEXAMINED} in-scope items UNEXAMINED — NOT done. DRIVE to 100% (resumable):"
      log "  1. run the /coverage-sweep skill (bundles staged in output/coverage_sweep/)"
      log "  2. python scripts/coverage_sweep_write.py"
      log "  3. ./run_pipeline.sh coverage-drive --no-rebuild   (loops until UNEXAMINED == 0)"
    else
      log "coverage-drive: COMPLETE — every in-scope item examined/cleared/finding/deferred. No silent gaps."
    fi
    ;;

  math-proof-clears)
    # Advisory math/estimator-proof check: flag math-estimator/guard/formula clears that lack an
    # independent formula re-derivation (NatSpec/code agreement is not proof — QuantAMM H-11). Manual,
    # not a hard gate. Writes output/math_estimator_clear_validation.{json,md}. Pass --mode strict to fail.
    require_audit
    "${PYTHON}" "${ROOT}/scripts/math_estimator_audit.py" || true
    "${PYTHON}" "${ROOT}/scripts/validate_math_estimator_clears.py" --mode "${ARG:-advisory}"
    ;;

  confirm-advisory)
    # Reachability-truth confirm in EVAL mode: advisory only, NEVER blocks (exit 0). Writes
    # output/confirm/{confirm_inventory,reachability_analysis,confirm_gate}.json. Manual; not wired
    # into eval/full so eval recall is never blocked. See documentation/pipeline_modes.md.
    require_audit
    "${PYTHON}" "${ROOT}/scripts/confirm_inventory.py"
    "${PYTHON}" "${ROOT}/scripts/confirm_reachability.py"
    "${PYTHON}" "${ROOT}/scripts/confirm_gate.py" --mode eval
    ;;

  submission-confirm)
    # Real-report PRECISION gate (manual): field-presence (min_confirm) + reachability-truth (confirm_gate
    # --mode submission). BLOCKS (exit 1) on submission risk: duplicate/unreachable/privileged_only/
    # insufficient_evidence High-Critical confirmed claims (lifecycle_only + uncertain only with --strict).
    # NOT wired into eval/full/coverage_review_gate. Override: AUDITWATCH_CONFIRM_OVERRIDE=1.
    require_audit
    "${PYTHON}" "${ROOT}/scripts/confirm_inventory.py"
    "${PYTHON}" "${ROOT}/scripts/confirm_reachability.py"
    "${PYTHON}" "${ROOT}/scripts/min_confirm_gate.py"; mc=$?
    if [[ "${2:-}" == "--strict" ]]; then
      "${PYTHON}" "${ROOT}/scripts/confirm_gate.py" --mode submission --strict; cf=$?
    else
      "${PYTHON}" "${ROOT}/scripts/confirm_gate.py" --mode submission; cf=$?
    fi
    [[ ${mc} -eq 0 && ${cf} -eq 0 ]] || die "submission-confirm BLOCKED — see output/min_confirm_gate.json + output/confirm/confirm_gate.json. Override: AUDITWATCH_CONFIRM_OVERRIDE=1"
    log "submission-confirm: PASS (field-presence + reachability-truth)"
    ;;

  eval-seal)
    # T4 blind wall: move audits/<id>/_sealed_answer_key OUT of the repo so the cold pass is physically blind.
    [[ -z "${2:-}" ]] && die "Usage: ./run_pipeline.sh eval-seal <audit-id>"
    "${PYTHON}" "${ROOT}/scripts/assert_blind.py" seal "${2}"
    ;;

  eval-reveal)
    # T4 blind wall: restore the sealed answer key for adjudication (the blind marker is kept).
    [[ -z "${2:-}" ]] && die "Usage: ./run_pipeline.sh eval-reveal <audit-id>"
    "${PYTHON}" "${ROOT}/scripts/assert_blind.py" reveal "${2}"
    ;;

  eval-adjudicate)
    # Recall Lab: (re)build adjudication.json for one eval project or --all scoreable (evals/corpus.json).
    # T4: if the key was vaulted for a blind pass, restore it first, then run the contamination backstop.
    if [[ -n "${2:-}" && "${2}" != --* ]]; then
      "${PYTHON}" "${ROOT}/scripts/assert_blind.py" reveal "${2}" 2>/dev/null || true
      "${PYTHON}" "${ROOT}/scripts/assert_blind.py" leakage "${2}" || \
        log "WARNING: possible answer-key leakage — verify the cold pass was blind before trusting recall."
    fi
    "${PYTHON}" "${ROOT}/scripts/adjudicate.py" "${@:2}"
    ;;

  eval-detect-misses)
    # Recall Lab: heuristic miss-detection for ALREADY-EVALUATED contests (or any with a cold pass + an
    # answer key in ANY format: report.md / answer_key_normalization.json / ground_truth.jsonl).
    # Auto labels are advisory (confidence-tagged); human/seed labels always win; not protected by the gate.
    #   eval-detect-misses <audit-id>   |   eval-detect-misses --all-evaluated
    if [[ "${2:-}" == "--all-evaluated" ]]; then
      for d in "${ROOT}"/audits/*/; do
        id="$(basename "$d")"; [[ "${id}" == _* ]] && continue
        merged="${d}output/merged_findings.json"
        key1="${d}_sealed_answer_key/report.md"; key2="${d}output/eval_ready/answer_key_normalization.json"; key3="${d}data/evaluation/ground_truth.jsonl"
        if [[ -f "${merged}" && ( -f "${key1}" || -f "${key2}" || -f "${key3}" ) ]]; then
          "${PYTHON}" "${ROOT}/scripts/adjudicate.py" "${id}" --auto
        fi
      done
    else
      "${PYTHON}" "${ROOT}/scripts/adjudicate.py" "${@:2}" --auto --print
    fi
    ;;

  eval-scoreboard)
    # Recall Lab: aggregate adjudication into the honest recall scoreboard (training/holdout + per-mechanism-class).
    # Eval-only; never touches the real-world dashboard.
    "${PYTHON}" "${ROOT}/scripts/eval_scoreboard.py"
    ;;

  eval-regression)
    # Recall Lab regression guard: fail (exit 1) if any protected TRAINING catch regressed to MISSED.
    # Run --snapshot to (re)capture the baseline after locking in new catches.
    if [[ "${2:-}" == "--snapshot" ]]; then
      "${PYTHON}" "${ROOT}/scripts/recall_regression_gate.py" --snapshot
    else
      "${PYTHON}" "${ROOT}/scripts/recall_regression_gate.py" || die "eval-regression BLOCKED — a previously-caught training finding is now MISSED. See evals/recall_baseline.json."
    fi
    ;;

  eval-iterate)
    # Recall Lab: print one iteration's checklist (freeze -> cold -> reveal -> adjudicate -> reincorporate).
    # The semantic steps (cold pass, adjudication, prompt authoring) run in-session via the /recall-lab skill.
    cat "${ROOT}/documentation/recall_lab.md" 2>/dev/null || log "see documentation/recall_lab.md"
    ;;

  eval-loop)
    # Recall Lab looping protocol over ALL past contests (resumable; one contest per /loop fire).
    #   eval-loop build | status | next | done <id> [--sections ..] [--classes ..] | enqueue-ingest
    # `next` mines the next contest + emits the iteration packet (does NOT advance); author the prompt §s
    # in-session, keep eval-regression green, then `done <id>` to bank + advance. State: evals/loop_state.json.
    "${PYTHON}" "${ROOT}/scripts/recall_lab_loop.py" "${@:2}"
    ;;

  deep-pass-queue|coverage-deep-queue)
    # Cluster the needs_deep_pass backlog into prioritized (tier 1-6) specialist packets (queue-mgmt).
    require_audit
    "${PYTHON}" "${ROOT}/scripts/deep_pass_queue.py"
    ;;

  deep-pass-status)
    # Account for executed vs skipped deep passes (deep_pass_ledger). Blocks (strict full-audit) if a
    # tier-1/2 deep pass was skipped without a waiver. Writes executed/skipped/budget summaries.
    require_audit
    "${PYTHON}" "${ROOT}/scripts/deep_pass_queue.py" >/dev/null 2>&1 || true
    "${PYTHON}" "${ROOT}/scripts/deep_pass_ledger.py"
    ;;

  freeze-check)
    # Eval freeze precondition: required specialists ran + no high-priority deep pass skipped (or waived).
    # Run BEFORE the manual sha256 freeze. Exit 1 (strict full-audit) blocks the freeze.
    require_audit
    if ! "${PYTHON}" "${ROOT}/scripts/freeze_preconditions.py"; then
      die "Freeze blocked — a mandatory specialist or a tier-1/2 deep pass was skipped. Resolve them, or record waivers in output/specialist_waiver.json / output/deep_pass_waiver.json."
    fi
    ;;

  coverage-sweep)
    # Prepare bundles for the /coverage-sweep skill (then run the skill + coverage_sweep_write.py).
    require_audit
    run_step "coverage_sweep_prepare" "${PYTHON}" "${ROOT}/scripts/coverage_sweep_prepare.py"
    log ""
    log "============================================================"
    log "COVERAGE-SWEEP PAUSE — bundles ready in output/coverage_sweep/_bundles/."
    log "  1. In Claude Code, run the /coverage-sweep skill (evidence-anchored clears, no API)."
    log "  2. python scripts/coverage_sweep_write.py   # validates + applies dispositions"
    log "  3. ./run_pipeline.sh coverage-gate          # confirm the gate now passes"
    log "============================================================"
    ;;

  poc-inventory)
    # Build the PoC-required worklist (deterministic; creates no tests).
    require_audit
    log "Building PoC validation inventory..."
    run_step "poc_inventory" "${PYTHON}" "${ROOT}/scripts/poc_inventory.py"
    status_snapshot
    ;;

  poc-validation-prepare)
    # Package PoC context bundles for the /poc-validation skill (deterministic; runs no tests).
    require_audit
    run_step "poc_validation_prepare" "${PYTHON}" "${ROOT}/scripts/poc_validation_prepare.py" "${@:2}"
    status_snapshot
    ;;

  poc-validation-write)
    # Normalize /poc-validation skill outputs into reviewer notes, then let the validator decide.
    require_audit
    run_step "poc_validation_write" "${PYTHON}" "${ROOT}/scripts/poc_validation_write.py" "${@:2}"
    run_step "validate_poc"         "${PYTHON}" "${ROOT}/scripts/validate_poc.py"
    status_snapshot
    ;;

  poc-validation)
    # Prepare bundles, then PAUSE for the /poc-validation skill (API-free, in-session).
    require_audit
    run_step "poc_validation_prepare" "${PYTHON}" "${ROOT}/scripts/poc_validation_prepare.py"
    log ""
    log "============================================================"
    log "POC-VALIDATION PAUSE — bundles ready in output/poc_validation/bundles/."
    log "  1. In Claude Code, run the /poc-validation skill (writes reviewer notes, no API)."
    log "  2. ./run_pipeline.sh poc-validation-write    # normalize notes + run the validator"
    log "  3. ./run_pipeline.sh poc-gate-engagement     # (or poc-gate-submission) check the gate"
    log "============================================================"
    ;;

  poc-validation-full)
    # End-to-end: inventory -> prepare -> PAUSE for /poc-validation -> (resume with poc-validation-write).
    require_audit
    run_step "poc_inventory"          "${PYTHON}" "${ROOT}/scripts/poc_inventory.py"
    run_step "poc_validation_prepare" "${PYTHON}" "${ROOT}/scripts/poc_validation_prepare.py"
    log ""
    log "============================================================"
    log "POC-VALIDATION-FULL PAUSE — bundles ready in output/poc_validation/bundles/."
    log "  1. In Claude Code, run the /poc-validation skill (reviewer notes, no API)."
    log "  2. ./run_pipeline.sh poc-validation-write    # write notes + validate_poc.py"
    log "  3. ./run_pipeline.sh poc-gate-engagement     # engagement-mode gate"
    log "============================================================"
    ;;

  poc-collect)
    # Run a PoC test command and record its execution. Pass-through args:
    #   ./run_pipeline.sh poc-collect --finding-id X --test-file F --test-name N --command "..."
    require_audit
    log "Collecting PoC execution result..."
    run_step "collect_poc_results" "${PYTHON}" "${ROOT}/scripts/collect_poc_results.py" "${@:2}"
    status_snapshot
    ;;

  poc-validate)
    # Validate whether collected PoCs prove the finding claim (uses optional reviewer notes).
    require_audit
    log "Validating PoCs..."
    if [[ -n "${ARG}" ]]; then
      run_step "validate_poc" "${PYTHON}" "${ROOT}/scripts/validate_poc.py" --finding-id "${ARG}"
    else
      run_step "validate_poc" "${PYTHON}" "${ROOT}/scripts/validate_poc.py"
    fi
    status_snapshot
    ;;

  poc-gate-eval)
    # Eval mode never blocks (recall is not gated by PoCs); warns on invalid/overclaimed claims.
    require_audit
    run_step "poc_validation_gate_eval" "${PYTHON}" "${ROOT}/scripts/poc_validation_gate.py" --mode eval
    status_snapshot
    ;;

  poc-gate-engagement)
    # Engagement mode: High/Critical need proven PoC (or waiver); Medium need >= partially_proven.
    require_audit
    run_step "poc_validation_gate_engagement" "${PYTHON}" "${ROOT}/scripts/poc_validation_gate.py" --mode engagement
    status_snapshot
    ;;

  poc-gate-submission)
    # Submission mode: High/Critical require proven; severity overclaim / invalid / inconclusive block.
    # Recommended order: coverage-gate -> confirm gate -> min-confirm -> THIS gate -> pre_submission_gate.py -> report.
    require_audit
    run_step "poc_validation_gate_submission" "${PYTHON}" "${ROOT}/scripts/poc_validation_gate.py" --mode submission
    status_snapshot
    ;;

  poc-engagement-report)
    # Operator readiness view: what can I submit now, what is blocked, what must I fix.
    # Optional args forwarded, e.g.:  ./run_pipeline.sh poc-engagement-report --mode submission
    require_audit
    run_step "poc_engagement_report" "${PYTHON}" "${ROOT}/scripts/poc_engagement_report.py" "${@:2}"
    log "     Fix-list: output/poc_validation/fix_list.md · dashboard: python scripts/dashboard.py"
    status_snapshot
    ;;

  poc-submission-report)
    # Stricter view: bucket every finding against the submission gate (writes the same artifacts).
    require_audit
    run_step "poc_submission_report" "${PYTHON}" "${ROOT}/scripts/poc_engagement_report.py" --mode submission
    log "     Fix-list: output/poc_validation/fix_list.md · dashboard: python scripts/dashboard.py"
    status_snapshot
    ;;

  poc-fix)
    # Stage the next concrete action for ONE finding from the fix-list. Forwards finding-id + flags, e.g.:
    #   ./run_pipeline.sh poc-fix DPF-036
    #   ./run_pipeline.sh poc-fix DPF-036 --mode submission
    #   ./run_pipeline.sh poc-fix DPF-036 --collect-command "forge test --match-test test_x -vvv"
    require_audit
    [[ -z "${ARG}" ]] && die "Usage: ./run_pipeline.sh poc-fix <finding-id> [--mode …] [--collect-command …]"
    run_step "poc_fix" "${PYTHON}" "${ROOT}/scripts/poc_fix.py" "${@:2}"
    status_snapshot
    ;;

  poc-fix-all)
    # Batch: stage the whole engagement's PoC-fix queue + consolidated operator worklist. Stages safely —
    # never executes test commands by default. Examples:
    #   ./run_pipeline.sh poc-fix-all
    #   ./run_pipeline.sh poc-fix-all --mode submission
    #   ./run_pipeline.sh poc-fix-all --limit 10
    #   ./run_pipeline.sh poc-fix-all --actions add_impact_assertion,add_negative_control
    require_audit
    run_step "poc_fix_all" "${PYTHON}" "${ROOT}/scripts/poc_fix_all.py" "${@:2}"
    log "     Worklist: output/poc_validation/operator_worklist.md · then run /poc-validation on staged bundles."
    status_snapshot
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

Recall Lab (eval against scored projects — eval-only, never affects the real-world dashboard):
  eval-adjudicate <id>|--all   Build/refresh adjudication.json (awarded vs cold-pass) for eval project(s)
  eval-detect-misses <id>|--all-evaluated   Heuristic miss-detection for already-evaluated contests (any answer-key format)
  eval-scoreboard              Honest recall scoreboard: training/holdout + per-mechanism-class (evals/scoreboard.md)
  eval-regression [--snapshot] Regression guard: fail if a previously-caught training finding is now MISSED
  eval-iterate                 Print one Recall Lab iteration checklist (see documentation/recall_lab.md)
  eval-loop <build|status|next|done <id>|enqueue-ingest|cold-coverage <id>|pattern-checklist <id>>   Resumable loop over ALL past contests (one per fire)
                               pattern-checklist: CHECKLIST PASS — scans source for reincorporated-pattern anchors -> candidate sites (auto-run on cold-coverage full pass)
                               cold-coverage gates an INGESTED contest: blocks reveal until the blind cold pass examined every in-scope substantive file

Reference: docs/pipeline_reference.md — full step details, gate rules, PoC levels
          documentation/recall_lab.md — the Recall Lab loop (freeze→cold→reveal→adjudicate→reincorporate)
USAGE
    exit 1
    ;;

esac
