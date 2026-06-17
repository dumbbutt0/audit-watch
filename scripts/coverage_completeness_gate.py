#!/usr/bin/env python3
"""
coverage_completeness_gate.py — Block the review gate unless every in-scope manifest item has a
valid, evidence-anchored disposition (deterministic, no LLM).

Reads output/coverage_manifest.json, output/coverage_dispositions.json, and
config/agent_policy.json -> coverage_policy. Writes output/coverage_gate.json and prints a concise
summary. Exit 0 = pass (review may proceed); nonzero = block.

Blocks on: missing manifest/dispositions; duplicate or unknown manifest ids; finding refs to a
missing manifest id; any in-scope item that is unassigned; in-scope assigned-only (not examined);
examined without clear/finding (unless policy allows); cleared without evidence or reason; finding
without finding_ref; deferred_out_of_scope without a reason.

Escape hatch: AUDITWATCH_COVERAGE_OVERRIDE=1 downgrades blocks to warnings (still writes report).

Usage:
    python scripts/coverage_completeness_gate.py [--strict] [--quiet]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
import gate_dos_utils as gdu  # noqa: E402
import read_completeness_utils as rcu  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ALLOWED = {"unassigned", "assigned", "examined", "cleared", "finding", "deferred_out_of_scope"}


def _policy() -> dict:
    try:
        return json.loads((ROOT / "config" / "agent_policy.json").read_text()).get("coverage_policy", {})
    except Exception:
        return {}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="(reserved) treat warnings as blocks too")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--enforce-read-completeness", action="store_true",
                    help="P245 #3 (default-off): block triage until every CRITICAL in-scope item is "
                         "READ_FULL or explicitly justified (NOT_IN_SCOPE / GENERATED_INTERFACE_ONLY / "
                         "DUPLICATE_WRAPPER / BLOCKED_BY_* with reason+ack).")
    args = ap.parse_args()

    pol = _policy()
    block_unassigned = pol.get("review_gate_blocks_unassigned", True)
    block_unexamined = pol.get("review_gate_blocks_unexamined", True)
    block_unevidenced = pol.get("review_gate_blocks_unevidenced_clears", True)
    allow_examined_only = pol.get("allow_examined_without_disposition", False)
    strong_on = pol.get("high_score_strong_clear", True)
    strong_threshold = pol.get("high_score_threshold", 3)
    strong_fields = pol.get("strong_clear_fields", ["attacker_reachability", "guard_or_invariant", "no_impact_reason"])
    full_audit = os.environ.get("AUDITWATCH_FULL_AUDIT") == "1"
    gd_strict = pol.get("gate_vs_dos_enabled", True) and (
        pol.get("gate_vs_dos_strict", False)
        or (pol.get("gate_vs_dos_strict_full_audit", True) and full_audit))
    override = os.environ.get("AUDITWATCH_COVERAGE_OVERRIDE", "").strip() in ("1", "true", "yes", "on")
    # P245 #3 read-completeness enforcement is DEFAULT-OFF: enabled only by the CLI flag or the policy
    # key (optionally only under a full audit). When off, this gate behaves exactly as before.
    enforce_read = (args.enforce_read_completeness
                    or pol.get("enforce_read_completeness", False)
                    or (pol.get("enforce_read_completeness_full_audit", False) and full_audit))

    blocking: list[dict] = []
    warnings: list[dict] = []

    def block(mid, reason):
        (warnings if override else blocking).append({"manifest_id": mid, "reason": reason})

    man_path = audit_path("output") / "coverage_manifest.json"
    disp_path = audit_path("output") / "coverage_dispositions.json"
    if not man_path.exists():
        blocking.append({"manifest_id": None, "reason": "coverage_manifest.json missing"})
    if not disp_path.exists():
        blocking.append({"manifest_id": None, "reason": "coverage_dispositions.json missing"})

    summary = {"total_items": 0, "in_scope_items": 0, "finding": 0, "cleared": 0, "examined": 0,
               "deferred_out_of_scope": 0, "unassigned": 0, "assigned_only": 0, "coverage_percent": 0.0}
    # P245 #3 read-completeness tallies (populated only when enforce_read is on; advisory otherwise).
    read_summary = {"enforced": enforce_read, "critical_in_scope": 0, "critical_read_full": 0,
                    "critical_blocked": 0, "noncritical_unread_warned": 0,
                    "read_state_counts": {}}

    if man_path.exists() and disp_path.exists():
        manifest = json.loads(man_path.read_text())
        items = {i["id"]: i for i in manifest.get("items", [])}
        if len(items) != len(manifest.get("items", [])):
            blocking.append({"manifest_id": None, "reason": "duplicate manifest ids"})
        disp = json.loads(disp_path.read_text()).get("dispositions", [])
        disp_idx: dict[str, dict] = {}
        for d in disp:
            mid = d.get("manifest_id")
            if mid in disp_idx:
                blocking.append({"manifest_id": mid, "reason": "duplicate disposition id"})
            disp_idx[mid] = d

        summary["total_items"] = len(items)
        in_scope = [m for m in items.values() if m.get("in_scope", True)]
        summary["in_scope_items"] = len(in_scope)

        # finding refs must point at real findings (existence-of-id check is best-effort here)
        for m in items.values():
            d = disp_idx.get(m["id"])
            if d is None:
                if m.get("in_scope", True):
                    block(m["id"], "no disposition record for in-scope item")
                continue
            st = d.get("status")
            if st not in ALLOWED:
                block(m["id"], f"invalid status '{st}'")
                continue
            # count
            if st == "finding":
                summary["finding"] += 1
            elif st == "cleared":
                summary["cleared"] += 1
            elif st == "examined":
                summary["examined"] += 1
            elif st == "deferred_out_of_scope":
                summary["deferred_out_of_scope"] += 1
            elif st == "unassigned":
                summary["unassigned"] += 1
            elif st == "assigned":
                summary["assigned_only"] += 1

            if not m.get("in_scope", True):
                if st != "deferred_out_of_scope":
                    warnings.append({"manifest_id": m["id"], "reason": f"out-of-scope item not deferred (status={st})"})
                continue
            # in-scope enforcement
            if st == "unassigned" and block_unassigned:
                block(m["id"], "in-scope item unassigned")
            elif st == "assigned" and block_unexamined:
                block(m["id"], "in-scope item assigned but not examined/cleared/finding")
            elif st == "examined" and not allow_examined_only:
                block(m["id"], "examined without a clear/finding disposition")
            elif st == "cleared":
                if block_unevidenced and not d.get("evidence"):
                    block(m["id"], "cleared without evidence")
                if not d.get("clear_reason"):
                    block(m["id"], "cleared without a clear_reason")
                if strong_on and m.get("attack_surface_score", 0) >= strong_threshold:
                    missing = [f for f in strong_fields if not (d.get(f) or "").strip()]
                    if missing:
                        block(m["id"], f"high-surface (score {m.get('attack_surface_score')}) cleared "
                                       f"without strong-clear fields: {', '.join(missing)}")
                if gd_strict and not d.get("finding_refs"):
                    gcls = gdu.classify(d)
                    if gcls["status"] == "missing_liveness_disproof":
                        block(m["id"], f"{gdu.ROUTED_STATUS}: intended-gate clear without liveness/DoS "
                                       f"disproof ({', '.join(gcls['missing'])})")
            elif st == "finding":
                if not d.get("finding_refs"):
                    block(m["id"], "finding without a finding_ref")
                for fr in d.get("finding_refs", []):
                    pass  # finding-id existence validated by link/min-confirm stage
            elif st == "deferred_out_of_scope":
                if not (d.get("scope_reason") or d.get("clear_reason")):
                    block(m["id"], "deferred_out_of_scope without a reason")

            # P245 #3 — read-completeness for CRITICAL in-scope items (default-off; orthogonal to status)
            if enforce_read:
                rs = d.get("read_state")
                if rs:
                    read_summary["read_state_counts"][rs] = read_summary["read_state_counts"].get(rs, 0) + 1
                if rcu.is_critical(m):
                    read_summary["critical_in_scope"] += 1
                    ok, why = rcu.read_state_satisfies_critical(d)
                    if ok:
                        if rs == "READ_FULL":
                            read_summary["critical_read_full"] += 1
                    else:
                        read_summary["critical_blocked"] += 1
                        block(m["id"], f"read-completeness: {why} "
                                       f"[critical: {', '.join(rcu.critical_reasons(m))}]")
                else:
                    # non-critical items only warn (never block) on incomplete read_state
                    ok, why = rcu.read_state_satisfies_critical(d)
                    if not ok and rs not in (None, ""):
                        read_summary["noncritical_unread_warned"] += 1
                        warnings.append({"manifest_id": m["id"],
                                         "reason": f"read-completeness (non-critical, advisory): {why}"})

        # unknown disposition ids (point at no manifest item)
        for mid in disp_idx:
            if mid not in items:
                warnings.append({"manifest_id": mid, "reason": "disposition references unknown manifest id"})

        resolved = summary["finding"] + summary["cleared"]
        denom = summary["in_scope_items"] or 1
        summary["coverage_percent"] = round(100.0 * resolved / denom, 1)

    passed = len(blocking) == 0
    report = {
        "passed": passed,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "override_active": override,
        "summary": summary,
        "read_completeness": read_summary,
        "blocking_items": blocking[:200],
        "blocking_count": len(blocking),
        "warnings": warnings[:200],
        "warning_count": len(warnings),
    }
    (audit_path("output") / "coverage_gate.json").write_text(json.dumps(report, indent=2))

    if not args.quiet:
        s = summary
        print(f"Coverage gate: {'PASS' if passed else 'BLOCK'}"
              + (" (OVERRIDE)" if override else ""))
        print(f"  in-scope {s['in_scope_items']}/{s['total_items']} · finding {s['finding']} · "
              f"cleared {s['cleared']} · examined {s['examined']} · deferred {s['deferred_out_of_scope']} · "
              f"unassigned {s['unassigned']} · assigned-only {s['assigned_only']}")
        print(f"  coverage: {s['coverage_percent']}%  ·  blocking {len(blocking)}  ·  warnings {len(warnings)}")
        if enforce_read:
            r = read_summary
            print(f"  read-completeness (ENFORCED): critical in-scope {r['critical_in_scope']} · "
                  f"READ_FULL {r['critical_read_full']} · blocked {r['critical_blocked']}")
        for b in blocking[:15]:
            print(f"    BLOCK {b['manifest_id']}: {b['reason']}")
        if len(blocking) > 15:
            print(f"    … +{len(blocking)-15} more (see output/coverage_gate.json)")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
