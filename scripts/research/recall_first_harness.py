#!/usr/bin/env python3
"""
recall_first_harness.py — P264 PRODUCTION-GRADE STAGING of the recall-first harness v1.

DEFAULT-OFF (mode=disabled), SHADOW/RESEARCH-ONLY, UN-WIRED. Composes the frozen P260 prioritizer + P262
recall-first sweep into a single staged entrypoint with a strict ADVISORY output contract, runtime guardrails,
bounded output, observability metrics, and reproducibility hashes.

SAFETY (the whole point): increase recall WITHOUT letting raw recall candidates become production findings. This
harness NEVER submits, sets severity/reportability, routes as canonical, or concludes. Advisory candidates are
promotion-gated: a candidate becomes a finding only via the SEPARATE downstream B/C ranking + five-op completion +
refutation stages (not in this module).

Modes: disabled (default; no-op exit 0) · shadow · research_eval. No mode ⇒ disabled.

Usage:
  python scripts/research/recall_first_harness.py --manifest <p> --accounting <p> --state-transition <p> \
      [--base-candidates <p>] [--suspicious-loci <p>] --out-dir <dir> --mode {disabled,shadow,research_eval} [--config <p>]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import locus_shape_prioritizer as lsp  # noqa: E402  (frozen P260; imported, never modified)
import recall_first_shape_sweep as rfs  # noqa: E402  (frozen P262; imported, never modified)
import source_span_guard_extractor as _ssx  # noqa: E402  (P285; imported READ-ONLY for body extraction)
import re  # noqa: E402

HARNESS_CFG = ROOT / "config" / "research_recall_first_harness.json"
_GUARD_FIELDS = ("reportable", "submission_ready", "concluded", "emits_finding", "production_routing")
_CALLEE_RE = re.compile(r"(?<![.\w])([A-Za-z_]\w*)\s*\(")
_STATE_WRITE_RE = re.compile(r"\b[\w.\[\]]+\s*(?:=|\+=|-=)\s*[^=]|\.push\(|delete\s+\w")


def _expand_internal_loci(manifest: dict, cands: list, contest: str, cfg: dict) -> list:
    """P291 Part B: surface class-relevant INTERNAL callees reached from surfaced public/external candidates as
    advisory internal_locus candidates. Bounded, fail-closed, advisory-only. No target/award constants."""
    icfg = cfg.get("internal_locus_recall") or {}
    if not icfg.get("enabled"):
        return []
    terms = [t.lower() for t in icfg.get("class_relevant_terms", [])]
    getters = [g.lower() for g in icfg.get("getter_prefixes", [])]
    skips = [s.lower() for s in icfg.get("skip_name_substrings", [])]
    per_entry = int(icfg.get("max_expansions_per_public_entry", 3))
    total_cap = int(icfg.get("max_internal_candidates_per_contest", 15))
    # index manifest functions by (contract, name) and by name
    fns = [i for i in manifest.get("items", []) if i.get("kind") == "function"]
    by_cn = {(f.get("contract"), f.get("name")): f for f in fns}
    by_name: dict = {}
    for f in fns:
        by_name.setdefault(f.get("name"), []).append(f)

    def _is_internal(f):
        return str(f.get("visibility", "")).lower() in ("internal", "private")

    def _class_relevant(name, body):
        nm = (name or "").lower()
        b = body.lower()
        score = sum(1 for t in terms if t in nm) * 2 + sum(1 for t in terms if t in b)
        return score

    surfaced = {(c.get("contract"), c.get("function")) for c in cands}
    out, seen = [], set()
    for c in cands:
        item = by_cn.get((c.get("contract"), c.get("function")))
        if not item:
            continue
        bd = _ssx.extract_body(item, None)
        if not bd.get("body_available") or bd.get("is_declaration_only"):
            continue
        body = _ssx.strip_comments(bd.get("body", ""))
        added = 0
        ranked = []
        for callee in dict.fromkeys(_CALLEE_RE.findall(body)):
            if added >= per_entry:
                break
            # resolve callee: prefer same-contract, else unique; fail-closed otherwise
            same = by_cn.get((c.get("contract"), callee))
            cand_fn = same or (by_name[callee][0] if len(by_name.get(callee, [])) == 1 else None)
            if not cand_fn or not _is_internal(cand_fn):
                continue
            key = (cand_fn.get("contract"), cand_fn.get("name"))
            if key in surfaced or key in seen:
                continue
            nm = (cand_fn.get("name") or "")
            if any(s in nm.lower() for s in skips):
                continue
            if any(nm.lower().startswith(g) for g in getters):  # trivial getter
                continue
            cbd = _ssx.extract_body(cand_fn, None)
            if not cbd.get("body_available") or cbd.get("is_declaration_only"):
                continue
            cbody = _ssx.strip_comments(cbd.get("body", ""))
            rel = _class_relevant(nm, cbody)
            if rel <= 0 or not _STATE_WRITE_RE.search(cbody):  # must be class-relevant AND mutate state
                continue
            ranked.append((rel + (1 if _STATE_WRITE_RE.search(cbody) else 0), cand_fn, callee))
        ranked.sort(key=lambda x: -x[0])
        for rel, cand_fn, callee in ranked[:per_entry]:
            key = (cand_fn.get("contract"), cand_fn.get("name"))
            if key in seen:
                continue
            seen.add(key)
            out.append({
                "candidate_id": f"{contest}:{cand_fn.get('contract')}:{cand_fn.get('name')}:int{len(out)}",
                "locus": f"{cand_fn.get('contract')}:{cand_fn.get('name')}",
                "contract": cand_fn.get("contract"), "function": cand_fn.get("name"),
                "source_span": cand_fn.get("source_span"),
                "internal_locus": True, "advisory_only": True,
                "reached_from_public_entry": f"{c.get('contract')}.{c.get('function')}",
                "call_path": [f"{c.get('contract')}.{c.get('function')}", f"{cand_fn.get('contract')}.{cand_fn.get('name')}"],
                "reason": f"internal accounting/reward/share/index callee (class-relevance score {rel}) reached from "
                          f"surfaced public {c.get('function')}",
                "class_hypothesis": "rewards_share_index_accounting",
                "prioritizer_score": c.get("prioritizer_score"),
                "sweep_inclusion_reason": ["p291_internal_locus_expansion"],
                "templates_applied": [], "generated_mechanisms": [],
                "bc_ranking_handoff": {"top_2_for_profile_B_C": [], "note": "internal-locus advisory; downstream gated"},
                "completion_status": None, "refutation_status": None,
                "evidence_pointers": [cand_fn.get("file", "")],
                "status": "ADVISORY_RECALL_CANDIDATE", "promotion_label": "NEEDS_RANKING",
                "severity": None, "reportable": False, "submission_ready": False,
                "concluded": False, "emits_finding": False, "production_routing": False,
            })
            if len(out) >= total_cap:
                return out
    return out


def _sha16(p: Path) -> str:
    try:
        return hashlib.sha256(p.read_bytes()).hexdigest()[:16]
    except OSError:
        return "missing"


def _load(p) -> dict | list | None:
    try:
        return json.loads(Path(p).read_text())
    except (OSError, json.JSONDecodeError):
        return None


class FailClosed(Exception):
    pass


def _validate_config(cfg: dict) -> dict:
    if not cfg:
        raise FailClosed("config missing or unparseable")
    caps, hub = cfg.get("caps", {}), cfg.get("cap_hard_upper_bounds", {})
    for k, v in caps.items():
        if not isinstance(v, int) or v <= 0:
            raise FailClosed(f"cap {k}={v} not a positive int")
        if k in hub and v > hub[k]:
            raise FailClosed(f"cap {k}={v} exceeds hard upper bound {hub[k]}")
    return cfg


def _promotion_label(cand: dict) -> str:
    # Recall candidates always start un-ranked/uncompleted/unrefuted in shadow mode.
    return "NEEDS_RANKING"


def _to_advisory(swept: dict, contest: str) -> list:
    out = []
    for i, s in enumerate(swept.get("swept_loci", [])):
        out.append({
            "candidate_id": f"{contest}:{s['contract']}:{s['function']}:{i}",
            "locus": s.get("locus_key", f"{s['contract']}:{s['function']}"),
            "contract": s["contract"], "function": s["function"],
            "source_span": s.get("source_span"),
            "prioritizer_score": None if s.get("p260_rank") is None else float(s.get("p260_rank")),
            "sweep_inclusion_reason": s.get("inclusion_reasons", []),
            "templates_applied": s.get("applied_shape_templates", []),
            "generated_mechanisms": s.get("candidate_mechanisms", []),
            "bc_ranking_handoff": {"top_2_for_profile_B_C": s.get("applied_shape_templates", [])[:2],
                                   "note": "feeds Profile B/C ranking + five-op completion (downstream, not here)"},
            "completion_status": None,         # not run in shadow harness
            "refutation_status": None,         # not run in shadow harness
            "evidence_pointers": [s.get("source_path", ""), f"checkpoint:{s.get('checkpoint_signal', [])}"],
            "status": "ADVISORY_RECALL_CANDIDATE",
            "promotion_label": _promotion_label(s),
            "severity": None, "reportable": False, "submission_ready": False,
            "concluded": False, "emits_finding": False, "production_routing": False,
        })
    return out


def _enforce_guards(cands: list) -> list:
    """Return list of guard violations (empty = clean). Never allow a promoted/concluded advisory candidate."""
    viol = []
    for c in cands:
        if c.get("severity") is not None:
            viol.append({"candidate_id": c["candidate_id"], "field": "severity", "value": c.get("severity")})
        for f in _GUARD_FIELDS:
            if c.get(f) not in (False, None):
                viol.append({"candidate_id": c["candidate_id"], "field": f, "value": c.get(f)})
        if c.get("status") != "ADVISORY_RECALL_CANDIDATE":
            viol.append({"candidate_id": c["candidate_id"], "field": "status", "value": c.get("status")})
    return viol


def _markdown(cands: list, cfg: dict, contest: str, metrics: dict) -> str:
    rows = []
    for c in cands[:cfg["caps"]["max_high_priority_md"]]:
        rows.append(f"| {c['prioritizer_score']} | {c['contract']}.{c['function']} | "
                    f"{','.join(t.split('_')[0] for t in c['templates_applied'])} | "
                    f"{';'.join(c['sweep_inclusion_reason'])} | {c['promotion_label']} |")
    return (f"# Recall-First Harness — SHADOW advisory ({contest})\n\n"
            f"**ADVISORY ONLY. No severity, no reportability, no submission, no routing.** "
            f"advisory_candidates={len(cands)} · guard_violations={metrics['guard_violations']} · "
            f"truncated={metrics['mechanisms_truncated']>0}\n\n"
            "| p260_rank | locus | templates | inclusion | promotion_label |\n|---|---|---|---|---|\n"
            + "\n".join(rows) +
            "\n\nEvery candidate is ADVISORY_RECALL_CANDIDATE → requires downstream B/C ranking + five-op completion "
            "+ refutation before any human-review escalation. None may be treated as a confirmed/reportable finding.\n")


def run(manifest_p, acct_p, st_p, base_p, susp_p, out_dir: Path, mode: str, cfg: dict, argv: str) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    manifest, acct, st = _load(manifest_p), _load(acct_p), _load(st_p)
    if manifest is None or acct is None or st is None:
        raise FailClosed("missing/unreadable required input (manifest/accounting/state-transition)")
    base = _load(base_p) if base_p else None
    p260_cfg = _load(lsp.CONFIG_PATH)
    rfs_cfg = _load(rfs.CFG_PATH)
    if not p260_cfg or not rfs_cfg:
        raise FailClosed("missing P260/P262 config")

    contest = Path(manifest_p).stem.replace("_coverage_manifest", "")
    swept = rfs.sweep(manifest, acct, st, base, p260_cfg, rfs_cfg, None)
    cands = _to_advisory(swept, contest)

    # P291 Part B: surface class-relevant internal accounting/reward/share/index callees of the surfaced candidates
    # (advisory-only, bounded). Append BEFORE harness caps so they share the deterministic cap window.
    try:
        cands = cands + _expand_internal_loci(manifest, cands, contest, cfg)
    except Exception:
        pass  # fail-closed: internal-locus expansion never blocks the base advisory output

    # bounded output (harness caps; P262 already bounds, this re-applies harness caps deterministically)
    caps = cfg["caps"]
    if len(cands) > caps["max_swept_loci_json"]:
        cands = cands[:caps["max_swept_loci_json"]]
    for c in cands:
        if len(c["generated_mechanisms"]) > caps["max_mechs_per_locus"]:
            c["generated_mechanisms"] = c["generated_mechanisms"][:caps["max_mechs_per_locus"]]

    violations = _enforce_guards(cands)

    from collections import Counter
    reason_counter: Counter = Counter()
    for c in cands:
        for r in c["sweep_inclusion_reason"]:
            reason_counter[r] += 1
    metrics = {
        "module": "recall_first_harness", "mode": mode, "contest": contest,
        "total_manifest_functions": len([i for i in manifest.get("items", [])
                                         if i.get("kind") in ("function", "initializer", "constructor")]),
        "checkpoint_hit_functions": len(rfs.lsp._checkpoint_hits(acct)) + len(rfs.lsp._checkpoint_hits(st)),
        "swept_loci": len(cands),
        "forced_loci_by_clause": dict(reason_counter),
        "templates_applied": sum(len(c["templates_applied"]) for c in cands),
        "mechanisms_generated": swept.get("total_mechs_to_ranking", 0),
        "mechanisms_truncated": 1 if swept.get("truncated") else 0,
        "bc_ranking_handoff_count": len(cands),
        "completion_attempted": 0, "refuted": 0,
        "advisory_candidate_count": len(cands),
        "guard_violations": len(violations),
        "runtime_seconds": round(time.time() - t0, 3),
        "version_hashes": {
            "p260_module": _sha16(ROOT / "scripts/research/locus_shape_prioritizer.py"),
            "p260_config": _sha16(lsp.CONFIG_PATH),
            "p262_module": _sha16(ROOT / "scripts/research/recall_first_shape_sweep.py"),
            "p262_config": _sha16(rfs.CFG_PATH),
            "harness_config": _sha16(HARNESS_CFG),
        },
        "reproducibility": {
            "git": "n/a (not a git repo)",
            "command": argv,
            "input_hashes": {"manifest": _sha16(Path(manifest_p)), "accounting": _sha16(Path(acct_p)),
                             "state_transition": _sha16(Path(st_p))},
        },
    }

    guard_report = {"module": "recall_first_harness", "mode": mode, "guard_violations": len(violations),
                    "violations": violations, "guard_fields_checked": ["severity", *_GUARD_FIELDS, "status"],
                    "result": "PASS" if not violations else "FAIL"}
    (out_dir / "recall_guard_report.json").write_text(json.dumps(guard_report, indent=2))

    if violations:
        # fail closed: do NOT emit promoted advisory outputs
        (out_dir / "recall_metrics.json").write_text(json.dumps(metrics, indent=2))
        raise FailClosed(f"GUARD FAILURE: {len(violations)} violation(s); no advisory outputs emitted")

    advisory = {
        "module": "recall_first_harness", "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": mode, "contest": contest,
        "is_gate": False, "research_only": True, "routes_in_production": False, "routed_manifest_ids": [],
        "emits_findings": False, "concludes_vulnerability": False,
        "output_type": "advisory_recall_candidates",
        "guard_violations": 0,
        "caps": caps, "truncated": bool(swept.get("truncated")),
        "advisory_candidates": cands,
    }
    (out_dir / "recall_advisory_candidates.json").write_text(json.dumps(advisory, indent=2))
    (out_dir / "recall_advisory_candidates.md").write_text(_markdown(cands, cfg, contest, metrics))
    (out_dir / "recall_metrics.json").write_text(json.dumps(metrics, indent=2))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest")
    ap.add_argument("--accounting")
    ap.add_argument("--state-transition")
    ap.add_argument("--base-candidates")
    ap.add_argument("--suspicious-loci")
    ap.add_argument("--out-dir")
    ap.add_argument("--mode")
    ap.add_argument("--config")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    cfg_raw = _load(args.config) if args.config else _load(HARNESS_CFG)
    mode = args.mode or (cfg_raw or {}).get("default_mode", "disabled")
    if mode not in ((cfg_raw or {}).get("supported_modes", ["disabled", "shadow", "research_eval"])):
        print(f"[recall_first_harness] unknown mode '{mode}' → treating as disabled (no-op)")
        return 0
    if mode == "disabled":
        if not args.quiet:
            print("[recall_first_harness] mode=disabled → no-op (default-off). Nothing emitted.")
        return 0

    try:
        cfg = _validate_config(cfg_raw)
        if not (args.manifest and args.accounting and args.state_transition and args.out_dir):
            raise FailClosed("shadow/research_eval requires --manifest --accounting --state-transition --out-dir")
        rc = run(args.manifest, args.accounting, args.state_transition, args.base_candidates,
                 args.suspicious_loci, Path(args.out_dir), mode, cfg, " ".join(sys.argv))
    except FailClosed as e:
        print(f"[recall_first_harness] FAIL-CLOSED: {e}", file=sys.stderr)
        return 2
    if not args.quiet:
        print(f"[recall_first_harness] mode={mode} · ADVISORY (no severity/reportability/routing) · wrote {args.out_dir}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
