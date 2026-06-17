#!/usr/bin/env python3
"""
value_provenance_eval_harness.py — P142 standing eval_only_manual_queue harness (RESEARCH-ONLY, UN-WIRED).

Invariant (research-platform Layer pattern, see documentation/architecture/platform_invariants.md):
    **"Aggregate, don't adjudicate."**
It seeds eval-only value-provenance queues from a corpus, ingests ALREADY-RECORDED real blind/manual deep-pass
outcomes through the UNCHANGED P140 safety merge (`ingest_results`), and tallies cross-architecture conversion
over time. It REFUSES to do the next layer's job: it never routes, never confirms, never sets severity /
exploitability / submission, never touches an audit's production output/ or review_gate.md, and is NOT wired into
run_pipeline.sh / agent_policy.json.

Every output carries the four research flags (`is_gate:false`, `research_only:true`, `routes_in_production:false`,
`routed_manifest_ids:[]`) plus `routing_allowed:false`. Routed inputs are refused. No fabrication: completion
artifacts are built only from corpus rows that carry provenance (`blind_output_ref`); provenance-less rows are
refused. The harness writes ONLY under the research workspace (default output_research/value_provenance_eval/).

Subcommands:
    seed      [--arch X | --all] [--workdir D]   build pending eval_only_manual_queue queues from the corpus
    ingest    [--arch X | --all] [--workdir D]   replay recorded outcomes through ingest_results() (safety merge)
    scorecard [--append] [--workdir D]           aggregate cross-arch conversion (+ time-series)
    all       [--workdir D]                       seed -> ingest -> scorecard --append

Usage: python scripts/research/value_provenance_eval_harness.py all
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
# Library reuse ONLY (no production wiring): the P140 safety-merge + validator.
from run_value_provenance_advisories import ingest_results, DEFAULT_CFG as RV_CFG  # noqa: E402

# The four research flags + routing_allowed — stamped on every harness output.
RESEARCH_FLAGS = {
    "is_gate": False, "research_only": True, "routes_in_production": False,
    "routed_manifest_ids": [], "routing_allowed": False,
}

DEFAULT_CFG = {
    "enabled": True,
    "corpus_path": "data/research/value_provenance_eval/corpus.jsonl",
    "workdir": "output_research/value_provenance_eval",
    "runtime_status_path": "output_research/value_provenance_eval/runtime_status.jsonl",
    **RESEARCH_FLAGS,
}

_DECISIONS = {"finding", "likely_exploitable", "needs_human", "strong_clear", "error"}
_NEXT_STEP = {"finding": "build_poc", "likely_exploitable": "build_poc",
              "needs_human": "human_review", "strong_clear": "keep_advisory", "error": "human_review"}

# P146 runtime-evidence-panel vocab (supplemental; NEVER feeds the prompt-derived scorecard metrics).
RUNTIME_STATUS = {"not_run", "partial", "runtime_confirmed", "runtime_refuted", "inconclusive"}
RUNTIME_CONFIDENCE = {"none", "low", "medium", "high"}
# The panel fields surfaced per corpus item (req 3).
_PANEL_FIELDS = ("bug_id", "architecture", "bug_class", "harness_path", "real_contract_deployed",
                 "production_source_modified", "corrected_reference_type", "control_case",
                 "vulnerable_output", "corrected_output", "divergence_summary", "limitations",
                 "duplicate_status", "runtime_status", "runtime_confidence", "routing_allowed",
                 "submission_ready")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_cfg() -> dict:
    cfg = dict(DEFAULT_CFG)
    try:
        p = ROOT / "config" / "research" / "value_provenance_eval_harness.json"
        cfg.update(json.loads(p.read_text()))
    except (OSError, ValueError):
        pass
    # Research flags are non-negotiable regardless of config edits.
    cfg.update(RESEARCH_FLAGS)
    return cfg


def _refuse_if_routed(obj: dict, what: str) -> None:
    """Defensive guard (mirrors evidence_bundle_gate): refuse routed / non-research input."""
    if not isinstance(obj, dict):
        return
    if obj.get("routing_allowed", False) is not False:
        raise SystemExit(f"[value_provenance_eval_harness] REFUSED: {what} has routing_allowed != false")
    if obj.get("routes_in_production") or obj.get("routed_manifest_ids"):
        raise SystemExit(f"[value_provenance_eval_harness] REFUSED: {what} is production-routed")


def _load_corpus(cfg: dict) -> list:
    """Read corpus.jsonl; skip malformed lines (fail-open)."""
    rows = []
    p = Path(cfg.get("corpus_path", DEFAULT_CFG["corpus_path"]))
    if not p.is_absolute():
        p = ROOT / p
    if not p.exists():
        return rows
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if isinstance(row, dict) and row.get("contract") and row.get("function"):
            rows.append(row)
    return rows


def _advisory_id(row: dict) -> str:
    return f"VP-{row.get('contract')}.{row.get('function')}"


def _arches(rows: list, arch: str | None) -> dict:
    out: dict = {}
    for r in rows:
        a = r.get("arch", "unknown")
        if arch and a != arch:
            continue
        out.setdefault(a, []).append(r)
    return out


def _workdir(cfg: dict, override: str | None) -> Path:
    wd = override or cfg.get("workdir", DEFAULT_CFG["workdir"])
    p = Path(wd)
    if not p.is_absolute():
        p = ROOT / p
    return p


# --------------------------------------------------------------------------- seed
def seed(cfg: dict, workdir: Path, arch: str | None) -> dict:
    rows = _load_corpus(cfg)
    groups = _arches(rows, arch)
    summary = {}
    for a, items in groups.items():
        results = []
        for r in items:
            aid = _advisory_id(r)
            results.append({
                "advisory_id": aid, "audit_id": r.get("audit_id"), "arch": a,
                "contract": r.get("contract"), "function": r.get("function"),
                "file_path": r.get("file_path"), "item_id": r.get("item_id"), "label": r.get("label"),
                "queue_origin": "eval_only_manual_queue",
                "auto_run_status": "pending_manual_execution", "prompt_decision": "pending",
                "advisory_only": True, "submission_ready": False, "requires_human_review": True,
                "prompt_confidence": None, "mechanism_summary": "",
                "output_path": f"{a}/value_provenance_jobs/{aid}.md", "error": None,
                **RESEARCH_FLAGS,
            })
        queue = {"ran": True, "generated_at": _now(), "queue_origin": "eval_only_manual_queue",
                 "arch": a, "summary": {"total": len(results)}, "results": results, **RESEARCH_FLAGS}
        d = workdir / a
        d.mkdir(parents=True, exist_ok=True)
        (d / "value_provenance_advisory_results.json").write_text(json.dumps(queue, indent=2))
        summary[a] = len(results)
    return {"ran": True, "seeded": summary, **RESEARCH_FLAGS}


# --------------------------------------------------------------------------- ingest
def _artifact_from_row(r: dict) -> dict | None:
    """Build a completion artifact from a corpus row's RECORDED real outcome. None if no provenance."""
    prov = r.get("blind_output_ref")
    dec = r.get("recorded_decision")
    if not prov or dec not in _DECISIONS:
        return None
    return {
        "job_id": _advisory_id(r), "audit_id": r.get("audit_id"),
        "contract": r.get("contract"), "function": r.get("function"), "file_path": r.get("file_path"),
        "prompt_name": "deep_pass_value_provenance", "execution_mode": "replayed_recorded_blind",
        "completed_at": f"replayed:{r.get('source_phase', '?')}",   # deterministic -> idempotent
        "reviewer_or_runner": prov,
        "prompt_decision": dec, "confidence": r.get("confidence"),
        "mechanism_summary": r.get("expected_shape", ""),
        "source_evidence_summary": f"recorded blind outcome ({r.get('source_phase', '?')})",
        "rejected_alternatives": None, "impact_summary": None, "limitations": None,
        "recommended_next_step": _NEXT_STEP.get(dec, "human_review"),
        "advisory_only": True, "submission_ready": False, "requires_human_review": True,
        "source_result_path": prov,
    }


def ingest(cfg: dict, workdir: Path, arch: str | None) -> dict:
    rows = _load_corpus(cfg)
    groups = _arches(rows, arch)
    summary, refused_provenance = {}, []
    for a, items in groups.items():
        qpath = workdir / a / "value_provenance_advisory_results.json"
        if not qpath.exists():
            # seed-on-demand so ingest is usable standalone
            seed(cfg, workdir, a)
        try:
            queue = json.loads(qpath.read_text())
        except (OSError, ValueError):
            continue
        _refuse_if_routed(queue, f"{a} queue")
        artifacts = []
        for r in items:
            art = _artifact_from_row(r)
            if art is None:
                refused_provenance.append(_advisory_id(r))
                continue
            artifacts.append(art)
        updated, ing = ingest_results(queue, artifacts, dict(RV_CFG))
        updated.update(RESEARCH_FLAGS)            # keep flags after merge
        updated["queue_origin"] = "eval_only_manual_queue"
        ing.update(RESEARCH_FLAGS)
        ing["refused_no_provenance"] = [x for x in refused_provenance]
        (workdir / a / "value_provenance_advisory_results.json").write_text(json.dumps(updated, indent=2))
        (workdir / a / "value_provenance_ingestion_report.json").write_text(json.dumps(ing, indent=2))
        summary[a] = ing["summary"]
    return {"ran": True, "ingested": summary, "refused_no_provenance": refused_provenance, **RESEARCH_FLAGS}


# --------------------------------------------------------------------------- scorecard
def _blank_counts() -> dict:
    return {"queued": 0, "completed": 0, "finding": 0, "likely_exploitable": 0, "needs_human": 0,
            "strong_clear": 0, "error": 0, "clean_strong_clear": 0, "clean_false_finding": 0,
            "buggy": 0, "clean": 0, "buggy_useful": 0, "buggy_strict": 0, "rejected": 0}


def _tally(entry: dict, c: dict) -> None:
    c["queued"] += 1
    dec = entry.get("prompt_decision")
    status = entry.get("auto_run_status")
    label = entry.get("label")
    if status in ("completed", "failed"):
        c["completed"] += 1
    if dec in ("finding", "likely_exploitable", "needs_human", "strong_clear", "error"):
        c[dec] += 1
    if label == "buggy":
        c["buggy"] += 1
        if dec in ("finding", "likely_exploitable", "needs_human"):
            c["buggy_useful"] += 1
        if dec in ("finding", "likely_exploitable"):
            c["buggy_strict"] += 1
    elif label == "clean":
        c["clean"] += 1
        if dec == "strong_clear":
            c["clean_strong_clear"] += 1
        if dec in ("finding", "likely_exploitable"):
            c["clean_false_finding"] += 1


def _rates(c: dict) -> dict:
    return {
        "useful_recall": round(c["buggy_useful"] / c["buggy"], 4) if c["buggy"] else None,
        "strict_recall": round(c["buggy_strict"] / c["buggy"], 4) if c["buggy"] else None,
        "clean_false_finding_rate": round(c["clean_false_finding"] / c["clean"], 4) if c["clean"] else None,
    }


# --------------------------------------------------------------------------- P146 runtime evidence panel
def _load_runtime_sidecar(cfg: dict) -> dict:
    """Read the research-only runtime_status.jsonl → {bug_id: row}. Fail-open (missing/malformed → {})."""
    rel = cfg.get("runtime_status_path", DEFAULT_CFG["runtime_status_path"])
    p = Path(rel)
    if not p.is_absolute():
        p = ROOT / p
    out: dict = {}
    if not p.exists():
        return out
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except ValueError:
            continue
        bid = row.get("item_id") or row.get("bug_id")
        if isinstance(row, dict) and bid:
            out[bid] = row
    return out


def _panel_row(bid: str, s: dict, corpus_item: dict | None, runtime_only: bool) -> dict:
    """Normalize one panel row from a sidecar row `s` (may be {}) + an optional corpus item.
    Forces routing_allowed/submission_ready False (research invariant) and validates the vocab."""
    c = corpus_item or {}
    status = s.get("runtime_status", "not_run")
    if status not in RUNTIME_STATUS:
        status = "inconclusive"
    conf = s.get("runtime_confidence", "none")
    if conf not in RUNTIME_CONFIDENCE:
        conf = "none"
    return {
        "bug_id": bid,
        "architecture": s.get("architecture") or c.get("arch"),
        "bug_class": s.get("bug_class") or c.get("expected_shape"),
        "harness_path": s.get("harness_path") or s.get("test_path"),
        "real_contract_deployed": s.get("real_contract_deployed",
                                        s.get("runtime_harness_type") == "real_contract" if s else None),
        "production_source_modified": bool(s.get("production_source_modified", False)),
        "corrected_reference_type": s.get("corrected_reference_type"),
        "control_case": s.get("control_case"),
        "vulnerable_output": s.get("vulnerable_output") or s.get("vulnerable_output_wad") or s.get("wrong_recipient"),
        "corrected_output": s.get("corrected_output") or s.get("corrected_output_wad") or s.get("correct_recipient"),
        "divergence_summary": s.get("divergence_summary") or s.get("runtime_result_summary"),
        "limitations": s.get("limitations"),
        "duplicate_status": s.get("duplicate_status") or s.get("duplicate_known"),
        "runtime_status": status,
        "runtime_confidence": conf,
        "runtime_only": runtime_only,    # True => sidecar item NOT in the prompt corpus (does not affect metrics)
        # Research invariant — forced regardless of sidecar contents.
        "routing_allowed": False,
        "submission_ready": False,
    }


def build_runtime_panel(cfg: dict) -> dict:
    """Supplemental, research-only runtime panel: one row per corpus item (default not_run/none, overlaid with the
    sidecar) PLUS one row per sidecar item whose bug_id is NOT in the corpus (runtime_only=True). The corpus is
    never modified, so the prompt-derived scorecard metrics (per_arch/totals/runs) are untouched. Every row is
    forced routing_allowed=False / submission_ready=False (research invariant)."""
    corpus = _load_corpus(cfg)
    side = _load_runtime_sidecar(cfg)
    corpus_ids = {c.get("item_id") for c in corpus}
    rows = [_panel_row(c.get("item_id"), side.get(c.get("item_id"), {}), c, runtime_only=False) for c in corpus]
    # runtime-only rows: sidecar entries that are not prompt-corpus items (e.g. P147 holdout findings).
    extra = sorted(b for b in side if b not in corpus_ids)
    for b in extra:
        rows.append(_panel_row(b, side[b], None, runtime_only=True))
    by_status = {}
    for r in rows:
        by_status[r["runtime_status"]] = by_status.get(r["runtime_status"], 0) + 1
    integrity = {
        "supplemental_only": True,
        "production_source_modified": any(r["production_source_modified"] for r in rows),
        "routing_allowed_all_false": all(r["routing_allowed"] is False for r in rows),
        "submission_ready_all_false": all(r["submission_ready"] is False for r in rows),
        "prompt_metrics_keys": ["per_arch", "totals", "runs"],
        "prompt_metrics_mutated_by_panel": False,
        "prompt_corpus_unchanged": True,
        "runtime_only_rows": extra,
        "backfilled": sorted(b for b in side if b in corpus_ids),
    }
    return {"generated_at": _now(), "summary": {"rows": len(rows), "runtime_only": len(extra), "by_status": by_status},
            "integrity": integrity, "rows": rows, **RESEARCH_FLAGS}


def runtime_panel(cfg: dict, workdir: Path) -> dict:
    """Build + write the standalone runtime panel (research-only). Never perturbs the prompt scorecard."""
    panel = build_runtime_panel(cfg)
    workdir.mkdir(parents=True, exist_ok=True)
    (workdir / "runtime_panel.json").write_text(json.dumps(panel, indent=2))
    (workdir / "runtime_panel.md").write_text(_runtime_panel_md(panel))
    return panel


def _runtime_panel_md(panel: dict) -> str:
    cols = ["bug_id", "architecture", "bug_class", "runtime_status", "runtime_confidence",
            "duplicate_status", "routing_allowed", "submission_ready"]
    lines = ["# Runtime Evidence Panel (research-only, SUPPLEMENTAL)", "",
             "> Runtime evidence is recorded SEPARATELY from the prompt-derived scorecard metrics "
             "(`per_arch`/`totals`/`runs`); it never feeds them, never routes, never submits. "
             "`research_only:true`, `routing_allowed:false`.", "",
             "| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in panel.get("rows", []):
        lines.append("| " + " | ".join(str(r.get(k)) for k in cols) + " |")
    s = panel.get("summary", {})
    lines += ["", f"Rows: {s.get('rows', 0)} · by_status: {s.get('by_status', {})}", ""]
    return "\n".join(lines)


def scorecard(cfg: dict, workdir: Path, append: bool) -> dict:
    per_arch, totals = {}, _blank_counts()
    if workdir.exists():
        for d in sorted(p for p in workdir.iterdir() if p.is_dir()):
            qpath = d / "value_provenance_advisory_results.json"
            if not qpath.exists():
                continue
            try:
                queue = json.loads(qpath.read_text())
            except (OSError, ValueError):
                continue
            _refuse_if_routed(queue, f"{d.name} queue")
            c = _blank_counts()
            for e in queue.get("results", []):
                if isinstance(e, dict):
                    _tally(e, c)
            try:
                ing = json.loads((d / "value_provenance_ingestion_report.json").read_text())
                c["rejected"] = int(ing.get("summary", {}).get("rejected", 0))
            except (OSError, ValueError):
                pass
            c.update(_rates(c))
            per_arch[d.name] = c
            for k in _blank_counts():
                totals[k] += c[k]
    totals.update(_rates(totals))
    snapshot = {"at": _now(), "totals": dict(totals)}

    sc_path = workdir / "scorecard.json"
    runs = []
    if append and sc_path.exists():
        try:
            runs = json.loads(sc_path.read_text()).get("runs", [])
        except (OSError, ValueError):
            runs = []
    runs.append(snapshot)

    out = {"generated_at": _now(), "corpus_path": cfg.get("corpus_path"),
           "per_arch": per_arch, "totals": totals, "runs": runs, **RESEARCH_FLAGS}
    # P146: SUPPLEMENTAL runtime evidence panel — additive key; per_arch/totals/runs above are computed
    # solely from the queues and are NOT touched by the panel (panel derives from corpus + sidecar only).
    panel = runtime_panel(cfg, workdir)
    out["runtime_panel"] = panel
    workdir.mkdir(parents=True, exist_ok=True)
    sc_path.write_text(json.dumps(out, indent=2))
    (workdir / "scorecard.md").write_text(_scorecard_md(out) + "\n" + _runtime_panel_md(panel))
    return out


def _scorecard_md(out: dict) -> str:
    cols = ["queued", "completed", "finding", "likely_exploitable", "needs_human", "strong_clear", "error",
            "clean_strong_clear", "clean_false_finding", "rejected"]
    lines = ["# Value-Provenance Eval Harness — Scorecard (research-only)", "",
             "> Aggregate, don't adjudicate. Every figure is prompt-derived advisory evidence — NOT confirmed, "
             "NOT submission-ready. `research_only:true`, `routing_allowed:false`.", "",
             "| arch | " + " | ".join(cols) + " | useful_recall | clean_FP |",
             "|" + "---|" * (len(cols) + 3)]
    for a, c in sorted(out["per_arch"].items()):
        row = " | ".join(str(c.get(k, 0)) for k in cols)
        lines.append(f"| {a} | {row} | {c.get('useful_recall')} | {c.get('clean_false_finding_rate')} |")
    t = out["totals"]
    lines.append(f"| **TOTAL** | " + " | ".join(str(t.get(k, 0)) for k in cols) +
                 f" | {t.get('useful_recall')} | {t.get('clean_false_finding_rate')} |")
    lines += ["", f"Runs recorded (time-series): {len(out.get('runs', []))}", ""]
    return "\n".join(lines)


# --------------------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(description="P142 value-provenance eval harness (research-only, un-wired).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("seed", "ingest"):
        sp = sub.add_parser(name)
        sp.add_argument("--arch")
        sp.add_argument("--all", action="store_true")
        sp.add_argument("--workdir")
    sc = sub.add_parser("scorecard")
    sc.add_argument("--append", action="store_true")
    sc.add_argument("--workdir")
    rp = sub.add_parser("runtime-panel")
    rp.add_argument("--workdir")
    al = sub.add_parser("all")
    al.add_argument("--workdir")
    args = ap.parse_args()

    cfg = load_cfg()
    if not cfg.get("enabled", True):
        print("[value_provenance_eval_harness] disabled via config (enabled=false)")
        return 0
    _refuse_if_routed(cfg, "config")
    workdir = _workdir(cfg, getattr(args, "workdir", None))

    try:
        if args.cmd == "seed":
            rep = seed(cfg, workdir, None if getattr(args, "all", False) else args.arch)
            print(f"[seed] {rep['seeded']} -> {workdir}")
        elif args.cmd == "ingest":
            rep = ingest(cfg, workdir, None if getattr(args, "all", False) else args.arch)
            print(f"[ingest] {rep['ingested']} · refused_no_provenance={rep['refused_no_provenance']}")
        elif args.cmd == "scorecard":
            out = scorecard(cfg, workdir, args.append)
            print(f"[scorecard] totals={out['totals']} · runs={len(out['runs'])} -> {workdir}/scorecard.json")
        elif args.cmd == "runtime-panel":
            panel = runtime_panel(cfg, workdir)
            print(f"[runtime-panel] {panel['summary']} · integrity={panel['integrity']} -> {workdir}/runtime_panel.json")
        elif args.cmd == "all":
            seed(cfg, workdir, None)
            ingest(cfg, workdir, None)
            out = scorecard(cfg, workdir, True)
            print(f"[all] totals={out['totals']} · clean_FP_rate={out['totals'].get('clean_false_finding_rate')}")
    except SystemExit:
        raise
    except Exception as e:  # fail-open: a research instrument must never wedge a workflow
        print(f"[value_provenance_eval_harness] non-fatal error: {e} — continuing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
