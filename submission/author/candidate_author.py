#!/usr/bin/env python3
"""
candidate_author.py — turn raw finding artifacts into a submission_candidate.json.

This is a TRANSLATOR, not a decision-maker:
  - It reads ONLY the files passed explicitly on the command line.
  - It builds a schema-shaped candidate, filling unknown fields with cautious
    safe defaults and recording every gap — it never fabricates evidence.
  - It always sets human_approval_required=true.
  - It never emits a readiness verdict (recommended_status is a fixed cautious
    placeholder); only submission_gate.py can decide readiness.
  - It NEVER submits anything and has no auto-submit code path.

Optionally (--run-gate) it runs the existing submission gate in-process purely to
show the operator the cautious verdict; a DO_NOT_SUBMIT result is NOT an authoring
failure.

Usage:
  python -m submission.author.candidate_author \
    --report report.md \
    --triage triage_notes.md \
    --poc-output poc.log \
    --scope scope.md \
    --program program.json \
    --duplicate-search duplicate_search.md \
    --defense-notes defense_notes.md \
    --out submission_candidate.json \
    --run-gate \
    --readiness-out readiness_report.md

Exit codes:
  0  authoring succeeded (regardless of the gate verdict, including DO_NOT_SUBMIT)
  1  authoring failed: missing required input, unreadable file, or the produced
     JSON does not satisfy the schema
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Package-relative imports (this module runs as submission.author.candidate_author).
from . import evidence_extractors as ex
from . import normalize as nz

# Location of the existing gate (sibling package). Used only for optional, local
# validation via --run-gate. NOTE: this is the submission gate, not the pipeline.
_GATES_DIR = Path(__file__).resolve().parent.parent / "gates"


class AuthoringError(Exception):
    """Raised when a candidate cannot be authored (IO / schema-generation)."""


# --------------------------------------------------------------------------- #
# Input loading                                                               #
# --------------------------------------------------------------------------- #

# maps CLI arg name -> the only files we are allowed to read
INPUT_KEYS = [
    "report", "triage", "poc_output", "scope", "program",
    "duplicate_search", "defense_notes",
]


def load_inputs(args) -> dict:
    """Read only the explicitly-provided files. Returns {key: text or None}.

    A None value means "this artifact was not provided" and must be reflected as
    missing evidence downstream — distinct from "" (provided but empty)."""
    inputs: dict = {"_source_files": []}
    for key in INPUT_KEYS:
        path = getattr(args, key)
        if not path:
            inputs[key] = None
            continue
        p = Path(path)
        try:
            inputs[key] = ex.read_text(p)
        except OSError as e:
            raise AuthoringError(f"could not read --{key.replace('_', '-')} file {path!r}: {e}")
        inputs["_source_files"].append(str(p))
    return inputs


# --------------------------------------------------------------------------- #
# Candidate construction                                                       #
# --------------------------------------------------------------------------- #

def build_candidate(inputs: dict, *, include_timestamp: bool = True) -> dict:
    """Assemble a schema-shaped candidate dict from extracted evidence.

    Every field is one of: extracted, conservatively derived, safely defaulted,
    or marked missing. Unknown is represented as missing — never invented.
    """
    report = inputs.get("report") or ""
    triage = inputs.get("triage")
    poc_log = inputs.get("poc_output")
    scope = inputs.get("scope")
    program_text = inputs.get("program")
    dup = inputs.get("duplicate_search")
    defense = inputs.get("defense_notes")

    program = ex.extract_program(program_text)
    gaps: list[str] = []

    # --- identity -----------------------------------------------------------
    title = ex.extract_section(report, ["title"]).splitlines()[0].strip() if \
        ex.extract_section(report, ["title"]) else ""
    if not title:
        title = _first_heading(report) or "Untitled finding"
    explicit_id = ex.extract_section(report, ["id", "finding id"]).strip()
    finding_id = explicit_id or ("AUTH-" + nz.slugify(title))

    # --- core narrative -----------------------------------------------------
    root_cause = ex.extract_section(report, ["root cause", "vulnerability details",
                                             "vulnerability detail"]).strip()
    if not root_cause:
        gaps.append("root_cause (no 'Root Cause' / 'Vulnerability Details' section)")

    affected_contracts = ex.extract_list_section(report, ["affected contracts", "affected contract",
                                                          "contracts", "target"])
    code_refs = nz.extract_file_line_refs(report)
    if not affected_contracts and code_refs:
        # derive contract names from code references (file part only)
        affected_contracts = _unique([r.split(":")[0] for r in code_refs])
    if not affected_contracts:
        gaps.append("affected_contracts (no contracts named)")

    affected_functions = ex.extract_list_section(report, ["affected functions", "affected function",
                                                          "functions"])
    if not affected_functions:
        gaps.append("affected_functions (no functions named)")

    attacker_entrypoint = _flatten(ex.extract_section(report, ["entry point", "entrypoint",
                                                               "attacker entrypoint"]))
    if not attacker_entrypoint:
        gaps.append("attacker_entrypoint (no external entrypoint stated)")

    attacker_capabilities = ex.extract_list_section(report, ["attacker capabilities",
                                                             "preconditions", "prerequisites"])

    # --- privilege ----------------------------------------------------------
    privilege_text = " ".join([attacker_entrypoint, root_cause,
                               " ".join(attacker_capabilities)])
    privilege_required = nz.normalize_privilege(privilege_text)

    # --- impact / severity --------------------------------------------------
    impact_text = ex.extract_section(report, ["impact", "impact details"])
    impact_category = nz.normalize_impact_category(impact_text + " " + title + " " + root_cause)
    if impact_category == "info":
        gaps.append("impact_category (no concrete impact identified -> 'info')")

    severity_claim = nz.normalize_severity(ex.extract_severity(report))
    # preserve the claim verbatim — never reconcile it with impact here.

    severity_justification = {
        "worst_case": _flatten(ex.extract_section(report, ["worst case", "worst-case"])),
        "realistic_case": _flatten(ex.extract_section(report, ["realistic case", "realistic-case"])),
        "program_table_mapping": _flatten(
            ex.extract_section(report, ["program table mapping", "impact table",
                                        "severity justification"])
        ) or (program.get("scope_reference", "") if program else ""),
    }

    asset_delta = _flatten(ex.extract_section(report, ["asset delta", "quantified loss",
                                                       "loss amount"]))

    # --- scope --------------------------------------------------------------
    in_scope_asset = ex.match_in_scope_asset(affected_contracts, scope, program)
    if scope is None and not program:
        scope_status = nz.SAFE_DEFAULTS["scope_status"]  # uncertain
        gaps.append("scope_status (no scope.md / program.json provided -> 'uncertain')")
    elif in_scope_asset:
        scope_status = "in_scope"
    else:
        scope_status = "uncertain"
        gaps.append("scope_status (affected asset not confirmed in scope -> 'uncertain')")

    out_of_scope_risks = ex.extract_list_section(report, ["out of scope", "out-of-scope risks",
                                                          "excluded assumptions"])

    bounty_program_mapping = _build_program_mapping(program, impact_category)

    # --- proof / poc --------------------------------------------------------
    poc = ex.extract_poc(poc_log)
    poc_status = poc["status"]
    proof_type = "runnable_poc" if (poc["is_run"] and poc_status in ("passing", "compiling")) \
        else nz.SAFE_DEFAULTS["proof_type"]
    poc_path = _flatten(ex.extract_section(report, ["poc path", "poc file", "test file"]))
    if not poc_path and inputs.get("poc_output") is not None and poc["is_run"]:
        # the provided log is a real artifact we may reference (not fabricated)
        poc_path = _provided_path(inputs, "poc_output")
    reproduction_steps = ex.extract_list_section(report, ["reproduction", "reproduction steps",
                                                          "steps to reproduce", "steps"])
    if poc_log is None:
        gaps.append("poc (no PoC log provided -> proof_type 'reasoning_only', poc_status 'none')")
    elif poc_status == "none":
        gaps.append("poc_status (PoC log has no pass/compile/trace evidence -> 'none')")

    # --- call trace / state -------------------------------------------------
    call_trace = ex.extract_list_section(report, ["attack path", "call trace", "call path",
                                                  "exploit path"])
    if not call_trace:
        gaps.append("call_trace (no 'Attack Path' / 'Call Trace' section)")
    state_transition = _build_state_transition(report)

    # --- duplicate / known issue -------------------------------------------
    duplicate_check_status = ex.extract_duplicate_status(dup)
    # known-issue status: from same note unless a dedicated section exists
    known_issue_text = ex.extract_section(dup or "", ["known issues", "known issue"]) or dup
    known_issue_check_status = ex.extract_duplicate_status(known_issue_text)
    if dup is None:
        gaps.append("duplicate_check / known_issue_check (no duplicate-search provided "
                    "-> 'not_searched')")
    prior_audit_overlap = ex.extract_prior_reports(dup)

    # --- defenses -----------------------------------------------------------
    defense_analysis = ex.extract_defenses(defense)
    if not defense_analysis:
        gaps.append("defense_analysis (no defense notes provided -> empty -> gate NEEDS_PROOF)")

    # --- residual narrative -------------------------------------------------
    false_positive_risks = ex.extract_list_section(report, ["false positive", "false positives",
                                                            "false positive risks"])
    invalidating_conditions = ex.extract_list_section(report, ["invalidating conditions",
                                                              "invalidating", "limitations"])
    assumptions = ex.extract_list_section(report, ["assumptions", "assumption"])

    evidence_links = _unique(code_refs)
    if poc_log is not None and poc["has_trace"]:
        p = _provided_path(inputs, "poc_output")
        if p:
            evidence_links.append(p)
    if not evidence_links:
        gaps.append("evidence_links (no file:line code references or PoC artifact)")

    triager_summary = _flatten(
        ex.extract_section(triage or "", ["summary", "triager summary", "triage summary"])
        or ex.extract_section(report, ["summary"])
    )

    # --- assemble -----------------------------------------------------------
    candidate = {
        "finding_id": finding_id,
        "title": title,
        "root_cause": root_cause,
        "affected_contracts": affected_contracts,
        "affected_functions": affected_functions,
        "attacker_entrypoint": attacker_entrypoint,
        "attacker_capabilities": attacker_capabilities,
        "privilege_required": privilege_required,
        "scope_status": scope_status,
        "in_scope_asset": in_scope_asset,
        "out_of_scope_risks": out_of_scope_risks,
        "impact_category": impact_category,
        "severity_claim": severity_claim,
        "severity_justification": severity_justification,
        "bounty_program_mapping": bounty_program_mapping,
        "call_trace": call_trace,
        "state_transition": state_transition,
        "asset_delta": asset_delta,
        "proof_type": proof_type,
        "poc_path": poc_path,
        "poc_status": poc_status,
        "reproduction_steps": reproduction_steps,
        "duplicate_check_status": duplicate_check_status,
        "known_issue_check_status": known_issue_check_status,
        "prior_audit_overlap": prior_audit_overlap,
        "false_positive_risks": false_positive_risks,
        "invalidating_conditions": invalidating_conditions,
        "defense_analysis": defense_analysis,
        "assumptions": assumptions,
        "evidence_links": evidence_links,
        "triager_summary": triager_summary,
        # The author NEVER claims readiness; the gate decides. Fixed cautious
        # placeholder (never READY_TO_SUBMIT_AFTER_APPROVAL).
        "recommended_status": nz.SAFE_DEFAULTS["recommended_status"],
        # Invariant: human approval is always mandatory.
        "human_approval_required": True,
        # Provenance / honesty metadata (allowed by schema additionalProperties).
        "authoring_metadata": _authoring_metadata(inputs, gaps, include_timestamp),
    }
    return candidate


# --------------------------------------------------------------------------- #
# small builders / helpers                                                     #
# --------------------------------------------------------------------------- #

def _build_program_mapping(program: dict, impact_category: str) -> dict:
    """Build bounty_program_mapping. Unknown booleans are OMITTED so the scope
    gate stays cautious (it only treats explicit False / non-True as signals)."""
    mapping: dict = {}
    if not program:
        return mapping
    if program.get("program"):
        mapping["program"] = program["program"]
    if program.get("platform"):
        mapping["platform"] = nz.normalize_platform(program["platform"])
    if program.get("scope_reference"):
        mapping["scope_reference"] = program["scope_reference"]
    in_scope_impacts = program.get("in_scope_impacts")
    if isinstance(in_scope_impacts, list):
        # only assert the bool when we actually know the program's accepted impacts
        mapping["impact_in_scope"] = impact_category in in_scope_impacts
    if "privileged_in_scope" in program and isinstance(program["privileged_in_scope"], bool):
        mapping["privileged_roles_in_scope"] = program["privileged_in_scope"]
    return mapping


def _build_state_transition(report: str) -> dict:
    before = _flatten(ex.extract_section(report, ["state before", "before"]))
    after = _flatten(ex.extract_section(report, ["state after", "after"]))
    slots = ex.extract_list_section(report, ["slots", "storage slots", "affected slots"])
    st: dict = {}
    if before:
        st["before"] = before
    if after:
        st["after"] = after
    if slots:
        st["slots_or_balances"] = slots
    return st


def _authoring_metadata(inputs: dict, gaps: list[str], include_timestamp: bool) -> dict:
    meta = {
        "authored_by": "submission.author.candidate_author",
        "source_files": list(inputs.get("_source_files", [])),
        # confidence is never "high": the author is a translator, not a judge.
        "author_confidence": "low" if gaps else "medium",
        "evidence_gaps": gaps,
        "notes": "Authored from explicit artifacts only. No evidence was inferred "
                 "beyond the provided text. The submission gate is authoritative; "
                 "human approval is mandatory. This tool performs no submission.",
    }
    if include_timestamp:
        meta["authoring_timestamp"] = datetime.now(timezone.utc).isoformat()
    return meta


def _first_heading(md: str) -> str:
    for line in (md or "").splitlines():
        m = ex._HEADING_RE.match(line)
        if m:
            return m.group(2).strip()
    return ""


def _flatten(text: str) -> str:
    return " ".join((text or "").split()).strip()


def _unique(items: list[str]) -> list[str]:
    out: list[str] = []
    for it in items:
        if it and it not in out:
            out.append(it)
    return out


def _provided_path(inputs: dict, key: str) -> str:
    """Return the source path recorded for a given input key, if any."""
    # source_files preserves insertion order matching INPUT_KEYS iteration
    provided = [k for k in INPUT_KEYS if inputs.get(k) is not None]
    files = inputs.get("_source_files", [])
    if key in provided:
        idx = provided.index(key)
        if idx < len(files):
            return files[idx]
    return ""


# --------------------------------------------------------------------------- #
# Optional gate run (local validation only — never submits)                    #
# --------------------------------------------------------------------------- #

def run_gate(candidate: dict) -> dict:
    """Run the existing submission gate in-process and return its report.

    This imports the gate as flat sibling modules (its established pattern). It
    is a local validation call only; it performs no submission and reads no
    pipeline state."""
    if str(_GATES_DIR) not in sys.path:
        sys.path.insert(0, str(_GATES_DIR))
    import submission_gate  # noqa: E402  (the submission gate, not the pipeline)
    return submission_gate.evaluate_candidate(candidate)


def render_report(gate_report: dict) -> str:
    if str(_GATES_DIR) not in sys.path:
        sys.path.insert(0, str(_GATES_DIR))
    import render  # noqa: E402
    return render.render_readiness_report(gate_report)


def schema_errors(candidate: dict) -> list[str]:
    if str(_GATES_DIR) not in sys.path:
        sys.path.insert(0, str(_GATES_DIR))
    import _common  # noqa: E402
    return _common.validate_schema(candidate)


def emit_platform_draft(candidate: dict, gate_report: dict, platform: str):
    """Render a gated platform draft via the renderers package.

    Returns (ok, text_or_reason). ok=False means the gate status is blocking and
    no draft was produced. This never submits anything."""
    from submission.renderers import platform_renderer
    return platform_renderer.emit_draft(candidate, gate_report, platform)


# --------------------------------------------------------------------------- #
# CLI                                                                          #
# --------------------------------------------------------------------------- #

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Author a submission_candidate.json from raw finding artifacts. "
                    "This tool never submits anything and never decides readiness.",
    )
    ap.add_argument("--report", required=True, help="finding report markdown (required)")
    ap.add_argument("--out", required=True, help="output submission_candidate.json path (required)")
    ap.add_argument("--triage", help="triage notes markdown")
    ap.add_argument("--poc-output", dest="poc_output", help="PoC run log")
    ap.add_argument("--scope", help="scope markdown")
    ap.add_argument("--program", help="program.json (program / scope rules)")
    ap.add_argument("--duplicate-search", dest="duplicate_search", help="duplicate-search notes")
    ap.add_argument("--defense-notes", dest="defense_notes", help="defense analysis notes")
    ap.add_argument("--run-gate", action="store_true",
                    help="also run the submission gate locally (does NOT submit)")
    ap.add_argument("--readiness-out", dest="readiness_out",
                    help="write the gate's readiness report markdown here (implies gate run)")
    ap.add_argument("--emit-platform", dest="emit_platform",
                    choices=["immunefi", "code4rena"],
                    help="render a platform DRAFT after authoring (implies gate run). The draft is "
                         "emitted only for non-blocking gate statuses and never submits.")
    ap.add_argument("--platform-out", dest="platform_out",
                    help="write the platform draft markdown here")
    ap.add_argument("--no-timestamp", action="store_true",
                    help="omit authoring_timestamp (deterministic output)")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    try:
        inputs = load_inputs(args)
        candidate = build_candidate(inputs, include_timestamp=not args.no_timestamp)

        # The produced JSON must satisfy the schema; if not, that is an authoring
        # failure (the author's job is to emit schema-valid candidates).
        errs = schema_errors(candidate)
        if errs:
            for e in errs:
                print(f"[author] schema error: {e}", file=sys.stderr)
            raise AuthoringError("produced candidate failed schema validation")

        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(candidate, indent=2) + "\n")
    except AuthoringError as e:
        print(f"[author] FAILED: {e}", file=sys.stderr)
        return 1

    if not args.quiet:
        gaps = candidate["authoring_metadata"]["evidence_gaps"]
        print(f"[author] wrote {args.out}")
        print(f"[author] finding_id: {candidate['finding_id']}")
        print(f"[author] severity_claim (preserved): {candidate['severity_claim']}")
        print(f"[author] evidence gaps: {len(gaps)}")
        for g in gaps:
            print(f"    - missing: {g}")

    # Optional local gate run — purely informational. DO_NOT_SUBMIT is NOT a
    # failure of authoring. A platform draft also requires the gate result.
    if args.run_gate or args.readiness_out or args.emit_platform:
        gate_report = run_gate(candidate)
        status = gate_report.get("recommended_status")
        if not args.quiet:
            print(f"[gate]   verdict: {status} (the gate is authoritative)")
            for b in gate_report.get("blockers", []):
                print(f"    BLOCK : {b}")
            for n in gate_report.get("needs_proof", []):
                print(f"    PROOF : {n}")
            for w in gate_report.get("warnings", []):
                print(f"    WARN  : {w}")
        if args.readiness_out:
            rp = Path(args.readiness_out)
            rp.parent.mkdir(parents=True, exist_ok=True)
            rp.write_text(render_report(gate_report))
            if not args.quiet:
                print(f"[gate]   readiness report: {args.readiness_out}")

        # Platform draft (gated). Blocking status -> refuse, write no file, but
        # this is NOT an authoring failure (exit stays 0).
        if args.emit_platform:
            ok, payload = emit_platform_draft(candidate, gate_report, args.emit_platform)
            if not ok:
                print(f"[draft]  platform draft NOT emitted: {payload}")
            else:
                if args.platform_out:
                    pp = Path(args.platform_out)
                    pp.parent.mkdir(parents=True, exist_ok=True)
                    pp.write_text(payload)
                    if not args.quiet:
                        print(f"[draft]  {args.emit_platform} DRAFT written to {args.platform_out}")
                elif not args.quiet:
                    print(f"[draft]  {args.emit_platform} DRAFT rendered "
                          "(no --platform-out given; not written)")

        if not args.quiet:
            print("[author] No submission was performed. Human approval is required "
                  "before any submission.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
