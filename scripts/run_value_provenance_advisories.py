#!/usr/bin/env python3
"""
run_value_provenance_advisories.py — P139 auto-run/route scaffold for H-03-class value-provenance deep passes.

Reads the H-03-class recommendations the P135/P136 surfacing layer already emits
(`output/mechanism_advisory_context.json` -> `deep_pass_recommendations[]`, recommended_prompt ==
deep_pass_value_provenance), applies a conservative trigger, builds a NEUTRAL answer-key-free source packet, and
queues a deep-pass job. Output is ADVISORY-ONLY review context — every entry is `advisory_only=true`,
`submission_ready=false`, `requires_human_review=true`.

SCAFFOLD (not a faked auto-run): the api-free pipeline (config/runtime_policy.json api_free=true) has NO safe
non-interactive LLM runner — `llm_runtime.llm_available()` is False — so the prompt is NOT executed here. Each job
is marked `auto_run_status="pending_manual_execution"` (prompt_decision "pending"); EXECUTION stays the in-session
`/deep-pass` skill (recorded later via `deep_pass_write.py --eval`). NEVER fabricates a prompt decision, NEVER
marks anything confirmed/submission-ready, NEVER assigns severity. Config-gated, capped, fail-open (never blocks).

Usage: python scripts/run_value_provenance_advisories.py [--eval] [--quiet]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path, get_audit_meta  # noqa: E402

ALLOWED_NEXT = ["inspect_source", "run_deep_pass_value_provenance", "map_defenses",
                "build_poc_if_confirmed", "reject_if_design_intended"]
FORBIDDEN_NEXT = ["submit_directly", "assign_severity_without_impact",
                  "mark_confirmed_without_poc_or_human_review"]

# P140 completion-ingestion vocabularies (manual /deep-pass result artifacts).
ALLOWED_DECISIONS = {"finding", "likely_exploitable", "needs_human", "strong_clear", "error"}
ALLOWED_CONFIDENCE = {"low", "medium", "high"}
RECOMMENDED_NEXT = {"human_review", "build_poc", "map_defenses", "reject", "keep_advisory"}

DEFAULT_CFG = {
    "auto_run_value_provenance_advisories": True,
    "auto_run_value_provenance_mode": "review_only",          # off | eval_only | review_only
    "auto_run_value_provenance_max_total": 5,
    "auto_run_value_provenance_max_per_audit": 5,
    "auto_run_value_provenance_timeout_seconds": 120,         # reserved for a future real runner
    "auto_run_value_provenance_allowed_prompts": ["deep_pass_value_provenance"],
    "auto_run_value_provenance_attach_to_human_queue": False,
    "auto_run_value_provenance_render_in_review_gate": True,
    "auto_run_value_provenance_surface_research_only": False,
    # P140 — completion loop
    "auto_run_value_provenance_manual_results_dir": "output/value_provenance_manual_results",
    "auto_run_value_provenance_hide_strong_clear": False,
    "auto_run_value_provenance_ingest_on_review_gate": True,
}

_LOOP_RE = re.compile(r"\b(for|while)\b\s*\(")
# A value-CONVERSION call (the value-provenance signal) — NOT any call. Config-setter loops (mapping
# assignment with no conversion call) do NOT match, so they don't falsely trigger.
_VALUE_CALL_RE = re.compile(r"\b(_?getValue|convert\w*|getPrice|getReserves|getAmountOut|toAssets\w*)\s*\(")
_MOCK_SEGMENTS = ("/mock", "/mocks/", "/test/", "/tests/", "/fixture")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_cfg(eval_mode: bool = False) -> dict:
    cfg = dict(DEFAULT_CFG)
    try:
        pol = json.loads((Path(__file__).resolve().parent.parent / "config" / "agent_policy.json").read_text())
        cfg.update(pol.get("value_provenance_auto_run", {}))
    except (OSError, ValueError):
        pass
    cfg["_eval_mode"] = eval_mode
    return cfg


def _is_mock(rec: dict) -> bool:
    f = (rec.get("file_path") or "").lower()
    base = f.rsplit("/", 1)[-1]
    c = (rec.get("contract") or "").lower()
    return ("mock" in base or "mock" in c or any(seg in f for seg in _MOCK_SEGMENTS))


def _span_index(out_dir: Path) -> dict:
    """Map (contract, function, start_line) -> end_line from the coverage manifest, so we read the EXACT
    function body and never overshoot into a neighboring function."""
    try:
        items = json.loads((out_dir / "coverage_manifest.json").read_text()).get("items", [])
    except (OSError, ValueError):
        return {}
    idx = {}
    for it in items:
        sp = it.get("source_span", {})
        if it.get("kind") == "function" and sp.get("start_line"):
            idx[(it.get("contract"), it.get("name"), sp["start_line"])] = sp.get("end_line", sp["start_line"])
    return idx


def _read_body(file_rel: str, start, end=None) -> str:
    if not file_rel or not start:
        return ""
    p = Path(file_rel)
    if not p.is_absolute():
        p = Path(__file__).resolve().parent.parent / file_rel
    try:
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        stop = end if end else min(start - 1 + 12, len(lines))   # exact span if known; else a small window
        return "\n".join(lines[start - 1: stop])
    except OSError:
        return ""


def _has_vp_signal(body: str) -> bool:
    """Conservative re-verify: a loop plus a VALUE-CONVERSION call inside the loop region (value-provenance
    loop). A loop that only assigns mappings / does no conversion does NOT qualify."""
    m = _LOOP_RE.search(body or "")
    if not m:
        return False
    return bool(_VALUE_CALL_RE.search(body[m.start():]))


def _trivial(body: str) -> bool:
    if "{" not in body or "}" not in body:
        return False
    inner = body[body.find("{") + 1: body.rfind("}")]
    inner = re.sub(r"/\*.*?\*/", "", inner, flags=re.S)
    inner = re.sub(r"//[^\n]*", "", inner)
    stmts = [s.strip() for s in inner.split(";") if s.strip()]
    return len(stmts) == 0


def build(cfg: dict, out_dir: Path, audit_id: str, ctx: dict | None) -> dict:
    """Pure-ish: given config + the mechanism_advisory_context dict, produce the results report (no queue I/O)."""
    mode = cfg.get("auto_run_value_provenance_mode", "review_only")
    if not cfg.get("auto_run_value_provenance_advisories", True) or mode == "off":
        return {"ran": False, "reason": "auto_run_value_provenance_advisories disabled or mode=off", "results": []}
    if mode == "eval_only" and not cfg.get("_eval_mode"):
        return {"ran": False, "reason": "mode=eval_only and not --eval", "results": []}
    if not isinstance(ctx, dict):
        return {"ran": True, "reason": "no/invalid mechanism_advisory_context", "results": [], "summary": {"total": 0}}

    allowed = set(cfg.get("auto_run_value_provenance_allowed_prompts", []))
    recs = ctx.get("deep_pass_recommendations", []) or []
    spans = _span_index(out_dir)
    jobs_dir = out_dir / "value_provenance_jobs"
    from llm_runtime import llm_available  # local import; cheap key/api_free check
    can_run = False
    try:
        can_run = bool(llm_available())
    except Exception:
        can_run = False

    results, skipped = [], 0
    per_audit = int(cfg.get("auto_run_value_provenance_max_per_audit", 5))
    total_cap = int(cfg.get("auto_run_value_provenance_max_total", 5))
    for rec in recs:
        if not isinstance(rec, dict):
            continue
        if rec.get("recommended_prompt") not in allowed:
            continue
        if rec.get("detector_status") == "research_only" and not cfg.get("auto_run_value_provenance_surface_research_only"):
            skipped += 1
            continue
        if rec.get("confirmed") or rec.get("submission_ready"):
            skipped += 1
            continue
        if _is_mock(rec):
            skipped += 1
            continue
        end = spans.get((rec.get("contract"), rec.get("function"), rec.get("line")))
        body = _read_body(rec.get("file_path", ""), rec.get("line"), end)
        if _trivial(body) or not _has_vp_signal(body):
            skipped += 1
            continue
        if len(results) >= total_cap or len(results) >= per_audit:
            skipped += 1
            continue

        contract = rec.get("contract", "?")
        function = rec.get("function", "?")
        advisory_id = f"VP-{contract}.{function}"
        # Build the neutral queued job packet (no answer key, no bug hint).
        jobs_dir.mkdir(parents=True, exist_ok=True)
        job_path = jobs_dir / f"{advisory_id}.md"
        job_path.write_text(
            f"# Value-Provenance deep-pass job — {advisory_id}\n\n"
            f"Run `prompts/deep_pass_value_provenance.md` on the bundle below (in-session /deep-pass skill).\n"
            f"ADVISORY-ONLY: result is review evidence, NOT confirmed/submission-ready; human + PoC required.\n\n"
            f"Contract.function: `{contract}.{function}`  ·  file: {rec.get('file_path')}:{rec.get('line')}\n\n"
            f"```solidity\n{body}\n```\n")
        # SCAFFOLD: no non-interactive runner in api-free mode -> pending; never fabricate a decision.
        status = "pending_manual_execution"  # (real "completed" path would require llm_available() AND a runner)
        results.append({
            "advisory_id": advisory_id, "audit_id": audit_id,
            "contract": contract, "function": function, "file_path": rec.get("file_path"),
            "source_detector_or_recommendation": rec.get("source_detector", "deep_pass_router"),
            "recommended_prompt": rec.get("recommended_prompt"),
            "auto_run_status": status,
            "advisory_only": True, "submission_ready": False, "requires_human_review": True,
            "prompt_decision": "pending", "prompt_confidence": None,
            "mechanism_summary": rec.get("prompt_reason", ""),
            "source_evidence_summary": f"value-provenance loop signal at {rec.get('file_path')}:{rec.get('line')}",
            "rejected_alternatives": None,
            "safety_notes": "prompt-derived review evidence, NOT proof; human + PoC required before any severity/submission",
            "allowed_next_steps": list(ALLOWED_NEXT), "forbidden_next_steps": list(FORBIDDEN_NEXT),
            "output_path": str(job_path), "error": None,
        })

    return {
        "ran": True, "generated_at": _now(), "llm_available": can_run, "config": cfg,
        "summary": {"total": len(results), "skipped": skipped,
                    "by_status": {"pending_manual_execution": sum(1 for r in results if r["auto_run_status"] == "pending_manual_execution")}},
        "results": results,
    }


# ---------------------------------------------------------------------------
# P140 — completion loop: ingest manual /deep-pass result artifacts.
# Deterministic, local, fail-open, idempotent. NEVER confirms, NEVER assigns
# severity, NEVER makes anything submission-ready; the advisory triplet is
# FORCED on every merged entry (ingestion can only flip it the safe way).
# ---------------------------------------------------------------------------

def _validate_completion(art: dict) -> tuple[bool, str]:
    """Return (ok, reason). Quarantines anything unsafe or malformed."""
    if not isinstance(art, dict):
        return False, "not an object"
    jid = art.get("job_id")
    if not jid or not isinstance(jid, str):
        return False, "missing/invalid job_id"
    # Unsafe / forbidden fields -> quarantine (never ingested).
    if art.get("submission_ready") is True:
        return False, "submission_ready=true (unsafe)"
    if art.get("advisory_only") is False:
        return False, "advisory_only=false (unsafe)"
    if art.get("requires_human_review") is False:
        return False, "requires_human_review=false (unsafe)"
    if art.get("confirmed") is True:
        return False, "forbidden field confirmed=true"
    fs = art.get("final_severity")
    if fs not in (None, "") and not art.get("final_severity_non_binding"):
        return False, "final_severity without explicit non-binding/hypothesis label"
    dec = art.get("prompt_decision")
    if dec not in ALLOWED_DECISIONS:
        return False, f"invalid prompt_decision '{dec}'"
    conf = art.get("confidence")
    if conf is not None and conf not in ALLOWED_CONFIDENCE:
        return False, f"invalid confidence '{conf}'"
    nxt = art.get("recommended_next_step")
    if nxt is not None and nxt not in RECOMMENDED_NEXT:
        return False, f"invalid recommended_next_step '{nxt}'"
    return True, "ok"


def _load_manual_results(results_dir: Path) -> list:
    """Read every *.json in the manual-results dir. Missing dir -> []. Per-file
    malformed/non-object -> a quarantine marker (never raises)."""
    out: list = []
    if not results_dir.exists() or not results_dir.is_dir():
        return out
    for fp in sorted(results_dir.glob("*.json")):
        try:
            payload = json.loads(fp.read_text())
        except (OSError, ValueError):
            out.append({"_file": fp.name, "_malformed": True})
            continue
        if isinstance(payload, dict):
            payload["_file"] = fp.name
            out.append(payload)
        else:
            out.append({"_file": fp.name, "_malformed": True})
    return out


def ingest_results(report: dict | None, manual_results: list, cfg: dict) -> tuple[dict, dict]:
    """Pure: merge manual completion artifacts into the advisory report.

    Returns (updated_report, ingestion_report). Idempotent (deterministic field copy keyed on the
    artifact). Unmatched artifacts and pending jobs without an artifact are left untouched.
    """
    if not isinstance(report, dict):
        report = {"ran": False, "results": []}
    results = [r for r in (report.get("results") or []) if isinstance(r, dict)]
    by_id = {r.get("advisory_id"): r for r in results}
    accepted: list = []
    rejected: list = []
    unmatched: list = []
    by_decision: dict = {}

    for art in manual_results or []:
        fname = art.get("_file", "?") if isinstance(art, dict) else "?"
        if isinstance(art, dict) and art.get("_malformed"):
            rejected.append({"file": fname, "job_id": None, "reason": "malformed JSON / not an object"})
            continue
        ok, reason = _validate_completion(art)
        if not ok:
            rejected.append({"file": fname, "job_id": (art.get("job_id") if isinstance(art, dict) else None),
                             "reason": reason})
            continue
        jid = art["job_id"]
        job = by_id.get(jid)
        if job is None:
            unmatched.append(jid)
            continue
        decision = art.get("prompt_decision")
        job["auto_run_status"] = "failed" if decision == "error" else "completed"
        job["prompt_decision"] = decision
        job["prompt_confidence"] = art.get("confidence")
        job["execution_mode"] = art.get("execution_mode", "manual_in_session")
        job["reviewer_or_runner"] = art.get("reviewer_or_runner")
        job["completed_at"] = art.get("completed_at")          # from artifact -> idempotent
        if art.get("mechanism_summary") is not None:
            job["mechanism_summary"] = art.get("mechanism_summary")
        if art.get("source_evidence_summary") is not None:
            job["source_evidence_summary"] = art.get("source_evidence_summary")
        job["rejected_alternatives"] = art.get("rejected_alternatives")
        job["impact_summary"] = art.get("impact_summary")
        job["limitations"] = art.get("limitations")
        job["recommended_next_step"] = art.get("recommended_next_step")
        job["source_result_path"] = art.get("source_result_path")
        job["raw_output_path"] = art.get("raw_output_path")
        # Defense-in-depth: ingestion can NEVER flip the advisory triplet.
        job["advisory_only"] = True
        job["submission_ready"] = False
        job["requires_human_review"] = True
        accepted.append(jid)
        by_decision[decision] = by_decision.get(decision, 0) + 1

    report["results"] = results
    completed = sum(1 for r in results if r.get("auto_run_status") in ("completed", "failed"))
    pending_remaining = sum(1 for r in results if r.get("auto_run_status") == "pending_manual_execution")
    ing = {
        "ran": True, "generated_at": _now(),
        "summary": {"accepted": len(accepted), "rejected": len(rejected), "unmatched": len(unmatched),
                    "completed": completed, "pending_remaining": pending_remaining, "by_decision": by_decision},
        "accepted": accepted, "rejected": rejected, "unmatched": unmatched,
    }
    return report, ing


def _run_ingest(out_dir: Path, mr_dir: Path, cfg: dict, quiet: bool) -> dict:
    """I/O wrapper: read results + manual artifacts, ingest, write back + ingestion report."""
    res_path = out_dir / "value_provenance_advisory_results.json"
    report: dict = {}
    if res_path.exists():
        try:
            report = json.loads(res_path.read_text())
        except (OSError, ValueError):
            report = {}
    manual = _load_manual_results(mr_dir)
    updated, ing = ingest_results(report, manual, cfg)
    res_path.write_text(json.dumps(updated, indent=2))
    (out_dir / "value_provenance_ingestion_report.json").write_text(json.dumps(ing, indent=2))
    if not quiet:
        s = ing["summary"]
        print(f"[run_value_provenance_advisories --ingest-results] accepted {s['accepted']}, "
              f"rejected {s['rejected']}, unmatched {s['unmatched']} · completed {s['completed']}, "
              f"pending {s['pending_remaining']} · advisory_only (never confirmed/submission-ready)")
    return ing


def main() -> int:
    ap = argparse.ArgumentParser(description="Auto-route value-provenance deep-pass advisories (scaffold).")
    ap.add_argument("--eval", action="store_true")
    ap.add_argument("--ingest-results", dest="ingest_results", action="store_true",
                    help="P140: ingest manual /deep-pass completion artifacts into the advisory report")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    out_dir = audit_path("output")
    out = out_dir / "value_provenance_advisory_results.json"

    if args.ingest_results:
        try:
            cfg = load_cfg(eval_mode=args.eval)
            mr_rel = cfg.get("auto_run_value_provenance_manual_results_dir",
                             "output/value_provenance_manual_results")
            mr_dir = audit_path(*Path(mr_rel).parts)
            _run_ingest(out_dir, mr_dir, cfg, args.quiet)
        except Exception as e:  # fail-open: ingestion never blocks
            try:
                (out_dir / "value_provenance_ingestion_report.json").write_text(
                    json.dumps({"ran": False, "error": str(e)}, indent=2))
            except OSError:
                pass
            if not args.quiet:
                print(f"[run_value_provenance_advisories --ingest-results] non-fatal error: {e} — continuing")
        return 0

    try:
        cfg = load_cfg(eval_mode=args.eval)
        audit_id = get_audit_meta().get("audit_id", "unknown")
        ctx = None
        ctx_path = out_dir / "mechanism_advisory_context.json"
        if ctx_path.exists():
            try:
                ctx = json.loads(ctx_path.read_text())
            except (OSError, ValueError):
                ctx = None
        report = build(cfg, out_dir, audit_id, ctx)
        out.write_text(json.dumps(report, indent=2))

        queued = 0
        if report.get("ran") and cfg.get("auto_run_value_provenance_attach_to_human_queue") and report.get("results"):
            qpath = audit_path("data") / "triage" / "human_review_queue.jsonl"
            qpath.parent.mkdir(parents=True, exist_ok=True)
            with qpath.open("a") as fh:
                for r in report["results"]:
                    fh.write(json.dumps({
                        "advisory_id": r["advisory_id"], "review_context": True, "advisory_only": True,
                        "submission_ready": False, "requires_human_review": True, "finding_id": None,
                        "recommended_severity": None, "source_detector": "value_provenance_auto_run",
                        "auto_run_status": r["auto_run_status"], "contract": r["contract"],
                        "function": r["function"], "file": r["file_path"], "queued_at": _now(),
                    }) + "\n")
                    queued += 1
            report["summary"]["queued"] = queued
            out.write_text(json.dumps(report, indent=2))

        if not args.quiet:
            if not report.get("ran"):
                print(f"[run_value_provenance_advisories] DISABLED ({report.get('reason')})")
            else:
                s = report.get("summary", {})
                print(f"[run_value_provenance_advisories] advisory_only · {s.get('total', 0)} jobs "
                      f"({s.get('by_status', {})}), skipped {s.get('skipped', 0)}, queued {queued} · wrote {out}")
    except Exception as e:  # fail-open: never block the pipeline
        try:
            out.write_text(json.dumps({"ran": False, "error": str(e), "results": []}, indent=2))
        except OSError:
            pass
        if not args.quiet:
            print(f"[run_value_provenance_advisories] non-fatal error: {e} — continuing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
