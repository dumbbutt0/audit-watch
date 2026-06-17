"""
Handoff bundle generator (P84) — generalizes the one-off P82 (PoC) + P83 (submission package) handoff into a
repeatable, finding-type-aware generator.

Given a *promoted finding descriptor*, it emits a complete handoff bundle:
  - PoC scaffold + run plan   (the P82 half — a NON-PASSING stub to be implemented from source behavior)
  - submission_draft.md, evidence_bundle.md, pre_submission_gate.md, reviewer_notes.md   (the P83 half)
  - funnel_record.json        (a stub that slots into the Blind-to-Reproducible Funnel)

Finding-type-specific NARRATIVE fragments come from `config/handoff_finding_types.json`; the L3 PoC
requirements / negative control / severity rationale come from the existing
`templates/proof_requirements/<bug_class>.json` taxonomy. The **reject-first gate is identical across all
types** — it is the same gate logic as `scripts/funnel.py` (reused here), and a freshly generated bundle is
verified to be UN-promotable (it can never look reproduced or submission-ready until a human fills evidence).

INVARIANTS (consistent with the platform's hard rules):
  - research_only / routes_in_production:false / is_gate:false; UN-WIRED (no run_pipeline / llm_runtime /
    agent_policy / runtime_policy reference).
  - "scaffold, don't prove": the generator NEVER emits a PASS for a finding-specific gate item, NEVER emits
    REPRODUCED or READY_FOR_HUMAN_REVIEW, and the PoC scaffold carries a guard that cannot report a false pass.
  - Refuses to write into any frozen phase directory; refuses to overwrite without `force=True`.
  - No answer-key dependence; templates are generic.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import funnel  # reuse the funnel enums + the SAME reject-first promotion gates

ROOT = Path(__file__).resolve().parent.parent
TYPES_CONFIG = ROOT / "config/handoff_finding_types.json"
PROOF_REQ_DIR = ROOT / "templates/proof_requirements"
TEMPLATE_DIR = ROOT / "templates/handoff"

BUNDLE_FILES = {
    "submission_draft.md": "submission_draft.md.tmpl",
    "evidence_bundle.md": "evidence_bundle.md.tmpl",
    "pre_submission_gate.md": "pre_submission_gate.md.tmpl",
    "reviewer_notes.md": "reviewer_notes.md.tmpl",
    "run_plan.md": "run_plan.md.tmpl",
}
POC_TEMPLATE = "poc_scaffold.t.sol.tmpl"

# directories whose contents are frozen and must never be written into.
_FROZEN_MARKERS = ("_p81e", "_p82_h01_claim_poc", "_p83_h01_submission", "_freeze")

DEFAULT_SOLC_PRAGMA = "^0.8.0"


class HandoffGeneratorError(ValueError):
    pass


# ----------------------------------------------------------------------- io
def _read_json(path: Path) -> Optional[Any]:
    try:
        with Path(path).open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def _read_text(path: Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def load_finding_types() -> Dict[str, Any]:
    data = _read_json(TYPES_CONFIG)
    if not isinstance(data, dict) or "finding_types" not in data:
        raise HandoffGeneratorError(f"missing/invalid finding-type registry: {TYPES_CONFIG}")
    return data["finding_types"]


def load_proof_requirements(bug_class: str) -> Dict[str, Any]:
    data = _read_json(PROOF_REQ_DIR / f"{bug_class}.json")
    if not isinstance(data, dict):
        raise HandoffGeneratorError(f"missing proof_requirements for bug_class={bug_class}")
    return data


# --------------------------------------------------------------- rendering
def _camel(s: str) -> str:
    parts = re.split(r"[^A-Za-z0-9]+", str(s))
    return "".join(p[:1].upper() + p[1:] for p in parts if p)


def _sanitize_ident(s: str) -> str:
    s = re.sub(r"[^A-Za-z0-9_]", "_", str(s))
    return s or "X"


def _bullets(items: List[str], prefix: str = "- ") -> str:
    return "\n".join(f"{prefix}{it}" for it in items) if items else "- TODO"


def _numbered(items: List[str]) -> str:
    return "\n".join(f"{i+1}. {it}" for i, it in enumerate(items)) if items else "1. TODO"


def _l3_checklist(proof_req: Dict[str, Any]) -> str:
    reqs = proof_req.get("required_for_high") or proof_req.get("required_for_medium") or []
    return _bullets([f"[ ] {r}" for r in reqs]) if reqs else "- TODO"


def _fill(template: str, fields: Dict[str, str]) -> str:
    out = template
    for k, v in fields.items():
        out = out.replace("{{" + k + "}}", v)
    leftover = re.findall(r"\{\{([A-Z0-9_]+)\}\}", out)
    if leftover:
        raise HandoffGeneratorError(f"unfilled template placeholders: {sorted(set(leftover))}")
    return out


# ------------------------------------------------------------- descriptor
def _require(descriptor: Dict[str, Any], key: str) -> str:
    v = descriptor.get(key)
    if v is None or str(v).strip() == "":
        raise HandoffGeneratorError(f"descriptor missing required field: {key}")
    return str(v)


def build_fields(descriptor: Dict[str, Any]) -> Dict[str, str]:
    """Assemble the placeholder map for a descriptor + its finding type. Read-only; no writes."""
    types = load_finding_types()
    ftype = _require(descriptor, "finding_type")
    if ftype not in types:
        raise HandoffGeneratorError(f"unknown finding_type {ftype!r}; known: {sorted(types)}")
    t = types[ftype]
    proof_req = load_proof_requirements(t["proof_requirements_ref"])

    contract = _require(descriptor, "contract")
    function = _require(descriptor, "function")
    finding_id = descriptor.get("finding_id") or "TBD"
    subject = descriptor.get("subject") or "TODO — subject"
    commit = descriptor.get("commit")
    title = descriptor.get("title") or f"{t['label']} issue in {contract}.{function}"
    summary = descriptor.get("summary") or "TODO — one-paragraph summary of the mechanism and consequence."

    test_contract = f"{_camel(contract)}{_camel(function)}PoC"
    test_name = f"test_{_sanitize_ident(finding_id)}_invariant"
    test_command = f"forge test --match-test {test_name} -vv"

    root_cause = str(t["root_cause_skeleton"]).replace("{{FUNCTION}}", function)

    # item 1 (source pinned) is a FACT, not a finding-claim: PASS only if a real commit hash is provided.
    commit_is_pinned = bool(commit) and bool(re.fullmatch(r"[0-9a-fA-F]{7,40}", str(commit)))
    gate_1_status = "✅ PASS" if commit_is_pinned else "❌ TODO — pin commit"
    commit_str = str(commit) if commit else "TODO — pin the audited commit + submodules"

    return {
        "FINDING_ID": finding_id,
        "SUBJECT": subject,
        "CONTRACT": contract,
        "FUNCTION": function,
        "TITLE": title,
        "TYPE_LABEL": str(t["label"]),
        "BUG_CLASS": str(proof_req.get("bug_class", t["proof_requirements_ref"])),
        "COMMIT": commit_str,
        "GATE_1_STATUS": gate_1_status,
        "SUMMARY": summary,
        "ROOT_CAUSE": root_cause,
        "SEVERITY_ARGUMENT": str(t["severity_argument"]),
        "NON_DUST_ARGUMENT": str(t["non_dust_argument"]),
        "POC_INVARIANT": str(t["poc_invariant_pattern"]),
        "POC_SETUP_HINT": str(t["poc_setup_hint"]),
        "MITIGATION_OPTIONS": _numbered(list(t.get("mitigation_options", []))),
        "EVIDENCE_PROMPTS": _bullets([f"TODO — {p}" for p in t.get("evidence_prompts", [])]),
        "L3_REQUIREMENTS": _l3_checklist(proof_req),
        "NEGATIVE_CONTROL": str(proof_req.get("negative_control_template", "TODO")),
        "HIGH_SEVERITY_RATIONALE": str(proof_req.get("high_severity_rationale", "TODO")),
        "TEST_CONTRACT": test_contract,
        "TEST_NAME": test_name,
        "TEST_COMMAND": test_command,
        "SOLC_PRAGMA": str(descriptor.get("solc_pragma") or DEFAULT_SOLC_PRAGMA),
        "GENERATED_AT": datetime.now(timezone.utc).isoformat(),
    }


def build_funnel_record_stub(descriptor: Dict[str, Any], fields: Dict[str, str]) -> Dict[str, Any]:
    """A funnel record for the scaffolded bundle. PoC + submission start at NOT_STARTED so the SAME funnel
    gates (funnel.py) cannot promote it to reproduced/submission-ready until a human fills evidence."""
    rec = {
        "record_id": f"{fields['SUBJECT']}:{fields['FINDING_ID']}:{fields['CONTRACT']}.{fields['FUNCTION']}",
        "subject": fields["SUBJECT"],
        "phase_discovered": descriptor.get("phase_discovered"),
        "finding_id": fields["FINDING_ID"],
        "contract": fields["CONTRACT"],
        "function": fields["FUNCTION"],
        "finding_type": descriptor["finding_type"],
        # conversion/safety carried from the descriptor if present; otherwise neutral (un-promotable).
        "conversion": descriptor.get("conversion", "NONE"),
        "severity_gate": descriptor.get("severity_gate", "n/a"),
        "adversarial_result": descriptor.get("adversarial_result", "n/a"),
        "severity_fp": bool(descriptor.get("severity_fp", False)),
        "safety": descriptor.get("safety") or {"source_false": False, "unsupported_ready": False, "hard_fail": False},
        "poc": {"poc_status": "NOT_STARTED"},
        "submission": {"submission_status": "NOT_STARTED"},
        "research_only": True,
        "routes_in_production": False,
    }
    return funnel.normalize_record(rec)


# ------------------------------------------------------------- generation
def _assert_writable(out_dir: Path, force: bool) -> None:
    parts = set(out_dir.resolve().parts)
    if parts & set(_FROZEN_MARKERS):
        raise HandoffGeneratorError(f"refusing to write into a frozen phase directory: {out_dir}")
    if out_dir.exists() and any(out_dir.iterdir()) and not force:
        raise HandoffGeneratorError(f"output dir not empty (pass force=True to overwrite): {out_dir}")


def render_bundle(descriptor: Dict[str, Any]) -> Dict[str, str]:
    """Render all bundle files in memory (no writes). Returns {filename: content}."""
    fields = build_fields(descriptor)
    out: Dict[str, str] = {}
    for fname, tmpl in BUNDLE_FILES.items():
        out[fname] = _fill(_read_text(TEMPLATE_DIR / tmpl), fields)
    poc_name = f"{fields['TEST_CONTRACT']}.t.sol"
    out[poc_name] = _fill(_read_text(TEMPLATE_DIR / POC_TEMPLATE), fields)
    out["funnel_record.json"] = json.dumps(
        build_funnel_record_stub(descriptor, fields), indent=2, ensure_ascii=False
    ) + "\n"
    return out


def generate_bundle(
    descriptor: Dict[str, Any],
    out_dir: Union[str, Path],
    force: bool = False,
) -> Dict[str, Any]:
    """Render + write a full handoff bundle. Reject-first: verifies the written bundle is un-promotable
    before returning. Returns a manifest."""
    out_dir = Path(out_dir)
    _assert_writable(out_dir, force)
    rendered = render_bundle(descriptor)

    out_dir.mkdir(parents=True, exist_ok=True)
    written: List[str] = []
    for fname, content in rendered.items():
        (out_dir / fname).write_text(content, encoding="utf-8")
        written.append(fname)

    report = validate_bundle(out_dir)
    if not report["ok"]:
        raise HandoffGeneratorError(f"generated bundle failed reject-first validation: {report['violations']}")

    return {
        "out_dir": str(out_dir),
        "finding_type": descriptor["finding_type"],
        "files": sorted(written),
        "reject_first_ok": report["ok"],
        "research_only": True,
        "routes_in_production": False,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


# ------------------------------------------------------------- validation
def validate_bundle(out_dir: Union[str, Path]) -> Dict[str, Any]:
    """Reject-first validation of a generated bundle. A freshly generated bundle must be UN-promotable and
    must not present any finding-specific item as proven."""
    out_dir = Path(out_dir)
    violations: List[str] = []

    # 1. all required files present
    expected = set(BUNDLE_FILES) | {"funnel_record.json"}
    present = {p.name for p in out_dir.glob("*")}
    poc_files = [p for p in present if p.endswith(".t.sol")]
    missing = expected - present
    if missing:
        violations.append(f"missing files: {sorted(missing)}")
    if not poc_files:
        violations.append("missing PoC scaffold (*.t.sol)")

    # 2. PoC scaffold must carry the non-passing guard
    for pf in poc_files:
        if "assertTrue(false" not in _read_text(out_dir / pf):
            violations.append(f"PoC scaffold {pf} lacks the non-passing reject-first guard")

    # 3. gate must be DO_NOT_SUBMIT and must NOT claim readiness; finding-specific items 4-9 not PASS
    gate_path = out_dir / "pre_submission_gate.md"
    if gate_path.is_file():
        gate = _read_text(gate_path)
        token = re.search(r"VERDICT_TOKEN:\s*([A-Z_]+)", gate)
        verdict = token.group(1) if token else None
        if verdict != "DO_NOT_SUBMIT":
            violations.append(f"gate verdict token is {verdict!r}, expected DO_NOT_SUBMIT for a fresh bundle")
        # items 4-9 should be TODO, not PASS
        for n in range(4, 10):
            row = re.search(rf"\|\s*{n}\s*\|[^\n]*", gate)
            if row and "✅ PASS" in row.group(0):
                violations.append(f"gate item {n} is PASS in a freshly generated bundle (must be TODO)")

    # 4. the SAME funnel gates must not promote this record
    rec = _read_json(out_dir / "funnel_record.json")
    if isinstance(rec, dict):
        repro_ok, _ = funnel.can_promote_to_poc_reproduced(rec)
        subm_ok, _ = funnel.can_promote_to_submission_ready(rec)
        status = funnel.compute_pipeline_status(rec)
        if repro_ok:
            violations.append("funnel record is already POC_REPRODUCED-eligible (must not be at generation)")
        if subm_ok:
            violations.append("funnel record is already submission-ready (must not be at generation)")
        if status in {"POC_REPRODUCED", "PARTIAL_REPRO", "SUBMISSION_READY_HUMAN_REVIEW"}:
            violations.append(f"funnel record pipeline_status={status} is too advanced for a scaffold")
    else:
        violations.append("missing/invalid funnel_record.json")

    return {"ok": not violations, "violations": violations, "out_dir": str(out_dir)}
