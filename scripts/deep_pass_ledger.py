#!/usr/bin/env python3
"""
deep_pass_ledger.py — account for which deep passes were EXECUTED vs SKIPPED, and block freeze if a
HIGH-PRIORITY (tier 1-2) deep pass was skipped without a budget waiver.

The Panoptic eval correctly scheduled 156 needs_deep_pass items but executed none in-session; 9 awarded
Mediums sat in that backlog. Recall was preserved but not realized. This ledger makes the backlog state
explicit and enforceable: it diffs the deep_pass_queue (the scheduled work) against the current
dispositions (the resolved work).

  executed = a queued item now resolved (cleared / finding / deferred_out_of_scope)
  skipped  = a queued item still pending (assigned+deep, or fell back to unassigned)

Writes output/executed_deep_passes.json, output/skipped_deep_passes_with_reason.json,
output/deep_pass_budget_summary.json. Strict full-audit + skipped tier-1/2 work → exit 1 unless
output/deep_pass_waiver.json records a budget waiver. Advisory → warn, exit 0.
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
import waiver_utils as wu  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HIGH_PRIORITY_TIERS = {1, 2}
RESOLVED = {"cleared", "finding", "deferred_out_of_scope"}


def _policy() -> dict:
    try:
        return json.loads((ROOT / "config" / "agent_policy.json").read_text()).get("coverage_policy", {})
    except Exception:
        return {}


def _load(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _load_waivers() -> tuple[dict[str, str], list[dict]]:
    """Split deep_pass_waiver.json into cluster-level waivers ({cluster_id: reason}) and per-sink waivers
    (a list of dicts identifying a manifest_id and/or contract+function with the per-sink fields)."""
    w = _load(audit_path("output") / "deep_pass_waiver.json")
    clusters, per_sink = {}, []
    for item in (w.get("waivers") or []):
        if not isinstance(item, dict):
            continue
        if item.get("manifest_id") or item.get("function"):
            per_sink.append(item)
        elif item.get("cluster_id") and item.get("reason"):
            clusters[item["cluster_id"]] = item["reason"]
    return clusters, per_sink


def _match_per_sink(item: dict, mid: str, per_sink: list[dict]) -> dict | None:
    """Find a per-sink waiver for a manifest item (by manifest_id, else contract+function name)."""
    name = (item or {}).get("name", "")
    contract = (item or {}).get("contract", "")
    for w in per_sink:
        if w.get("manifest_id") == mid:
            return w
        if w.get("function") and w.get("function") == name and (not w.get("contract") or w.get("contract") == contract):
            return w
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    pol = _policy()
    full_audit = os.environ.get("AUDITWATCH_FULL_AUDIT") == "1"
    enabled = pol.get("deep_pass_priority_enabled", True)
    strict = enabled and (pol.get("deep_pass_high_priority_block_strict", False)
                          or (pol.get("deep_pass_high_priority_block_strict_full_audit", True) and full_audit))
    # waiver discipline: high-risk items may NOT be cluster-waived; they need a per-sink waiver. The number
    # of honored high-risk per-sink waivers (recall-risk) is capped.
    wd_strict = pol.get("waiver_discipline_enabled", True) and (
        pol.get("waiver_discipline_strict", False)
        or (pol.get("waiver_discipline_strict_full_audit", True) and full_audit))
    high_risk_waiver_max = pol.get("high_risk_waiver_max", 0)

    queue = _load(audit_path("output") / "deep_pass_queue.json")
    disp = {d["manifest_id"]: d for d in _load(audit_path("output") / "coverage_dispositions.json").get("dispositions", [])}
    man = {i["id"]: i for i in _load(audit_path("output") / "coverage_manifest.json").get("items", [])}
    cluster_waivers, per_sink_waivers = _load_waivers()

    executed, skipped = [], []
    cluster_rows = []
    high_risk_blocked, waiver_incomplete, recall_risk = [], [], []
    for c in queue.get("clusters", []):
        tier = c.get("priority_tier", 6)
        cl_waived = c["cluster_id"] in cluster_waivers
        ex_ids, sk_ids, unhonored = [], [], []
        for mid in c.get("item_ids", []):
            st = disp.get(mid, {}).get("status")
            if st in RESOLVED:
                ex_ids.append(mid)
                executed.append({"manifest_id": mid, "cluster_id": c["cluster_id"], "tier": tier,
                                 "status": st, "specialist": c.get("suggested_specialist")})
                continue
            sk_ids.append(mid)
            item = man.get(mid, {})
            rc = wu.risk_class(item)
            ps = _match_per_sink(item, mid, per_sink_waivers)
            row = {"manifest_id": mid, "cluster_id": c["cluster_id"], "tier": tier,
                   "specialist": c.get("suggested_specialist"), "risk_class": rc,
                   "reason": f"tier-{tier} {c.get('tier_reason', '')} deep pass not executed"}
            if rc != "none":
                # high-risk: requires a valid PER-SINK waiver; a cluster waiver is not enough
                if ps is not None:
                    ok, missing = wu.validate_per_sink_waiver(ps)
                    if ok:
                        row["waiver_status"] = wu.RECALL_RISK_STATUS
                        recall_risk.append(row)
                    else:
                        row["waiver_status"] = wu.INCOMPLETE_STATUS
                        row["missing_fields"] = missing
                        waiver_incomplete.append(row); unhonored.append(mid)
                elif cl_waived:
                    row["waiver_status"] = wu.BLOCKED_STATUS
                    high_risk_blocked.append(row); unhonored.append(mid)
                else:
                    row["waiver_status"] = None
                    unhonored.append(mid)
            else:
                # low-risk: a cluster waiver (or a per-sink waiver) honors it; else it is an open skip
                if not (cl_waived or ps is not None):
                    unhonored.append(mid)
            skipped.append(row)
        # a cluster counts as "covered" if every skipped item is honored (executed items aside)
        cluster_rows.append({"cluster_id": c["cluster_id"], "tier": tier, "executed": len(ex_ids),
                             "skipped": len(sk_ids), "unhonored": len(unhonored),
                             "cluster_waived": cl_waived})

    # blocking conditions (strict): any tier-1/2 cluster with an unhonored skipped item, any high-risk item
    # cluster-waived or with an incomplete per-sink waiver, or recall-risk waivers over the cap.
    hp_unhonored = [r for r in cluster_rows if r["tier"] in HIGH_PRIORITY_TIERS and r["unhonored"] > 0]
    over_cap = len(recall_risk) > high_risk_waiver_max
    waiver_block = wd_strict and (bool(high_risk_blocked) or bool(waiver_incomplete) or over_cap)

    total_q = sum(len(c.get("item_ids", [])) for c in queue.get("clusters", []))
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "strict": strict, "full_audit": full_audit,
        "queued_items": total_q, "executed": len(executed), "skipped": len(skipped),
        "execution_rate": round(len(executed) / total_q, 3) if total_q else 1.0,
        "clusters": cluster_rows,
        "high_priority_skipped_clusters": [r["cluster_id"] for r in hp_unhonored],
        "cluster_waivers": sorted(cluster_waivers.keys()),
        "high_risk_waiver_max": high_risk_waiver_max,
        "high_risk_waiver_blocked": high_risk_blocked,
        "waiver_requires_per_sink_justification": waiver_incomplete,
        "recall_risk_waivers": recall_risk,
    }
    out = audit_path("output")
    (out / "executed_deep_passes.json").write_text(json.dumps({"executed": executed}, indent=2))
    (out / "skipped_deep_passes_with_reason.json").write_text(json.dumps({"skipped": skipped}, indent=2))
    (out / "deep_pass_budget_summary.json").write_text(json.dumps(summary, indent=2))
    _append_history(queue, executed, skipped, recall_risk)

    blocked = (bool(hp_unhonored) and strict) or waiver_block
    if not args.quiet:
        print(f"Deep-pass ledger: {'STRICT' if (strict or wd_strict) else 'advisory'}  ·  "
              f"queued {total_q} · executed {len(executed)} · skipped {len(skipped)} "
              f"({summary['execution_rate']*100:.0f}% executed) · recall-risk waivers {len(recall_risk)}")
        for r in hp_unhonored:
            print(f"   ✗ HIGH-PRIORITY (tier {r['tier']}) cluster has {r['unhonored']} unhonored item(s): {r['cluster_id']}")
        for r in high_risk_blocked:
            print(f"   ✗ {wu.BLOCKED_STATUS}: {r['manifest_id']} ({r['risk_class']}) cluster-waived — needs a per-sink waiver")
        for r in waiver_incomplete:
            print(f"   ✗ {wu.INCOMPLETE_STATUS}: {r['manifest_id']} missing {', '.join(r.get('missing_fields', []))}")
        if over_cap:
            print(f"   ✗ recall-risk waivers {len(recall_risk)} exceed cap {high_risk_waiver_max}")
        if blocked:
            print("  → BLOCK: execute the work, or record per-sink waivers (function/sink/risk_class/reason/"
                  "no_impact_justification/answer_independent_reviewer/follow_up) for high-risk items.")
    return 1 if blocked else 0


def _append_history(queue: dict, executed: list, skipped: list, recall_risk: list) -> None:
    """Append a cumulative per-item history record (T5). Best-effort; never raises into the gate."""
    try:
        import hashlib
        ts = datetime.now(timezone.utc).isoformat()
        run_id = hashlib.sha256((json.dumps(queue.get("clusters", []), sort_keys=True) + ts).encode()).hexdigest()[:12]
        recall_ids = {r["manifest_id"] for r in recall_risk}
        lines = []
        for c in queue.get("clusters", []):
            for mid in c.get("item_ids", []):
                lines.append({"ts": ts, "run_id": run_id, "type": "queued", "manifest_id": mid,
                              "cluster_id": c["cluster_id"], "tier": c.get("priority_tier", 6),
                              "specialist": c.get("suggested_specialist")})
        for e in executed:
            lines.append({"ts": ts, "run_id": run_id, "type": "executed", "manifest_id": e["manifest_id"],
                          "cluster_id": e["cluster_id"], "tier": e["tier"], "specialist": e.get("specialist"),
                          "disposition": e.get("status")})
        for s in skipped:
            t = "waived" if s["manifest_id"] in recall_ids else "skipped"
            lines.append({"ts": ts, "run_id": run_id, "type": t, "manifest_id": s["manifest_id"],
                          "cluster_id": s["cluster_id"], "tier": s["tier"], "specialist": s.get("specialist"),
                          "reason": s.get("reason")})
        hp = audit_path("output") / "deep_pass_ledger_history.jsonl"
        with hp.open("a") as f:
            for ln in lines:
                f.write(json.dumps(ln) + "\n")
        _write_cumulative(run_id)
    except Exception:
        pass


def _write_cumulative(latest_run: str) -> None:
    """Fold the full history into output/deep_pass_cumulative.json. The latest TYPE per item is reconciled
    against the CURRENT dispositions (the source of truth) so an item executed after it left the queue still
    reads 'executed' — fixing Revert Lend's misleading current-queue 'executed 0'."""
    hp = audit_path("output") / "deep_pass_ledger_history.jsonl"
    if not hp.exists():
        return
    disp = {d["manifest_id"]: d for d in _load(audit_path("output") / "coverage_dispositions.json").get("dispositions", [])}
    recall_ids = {r["manifest_id"] for r in _load(audit_path("output") / "deep_pass_budget_summary.json").get("recall_risk_waivers", [])}
    items: dict[str, dict] = {}
    runs = set()
    for ln in hp.read_text().splitlines():
        if not ln.strip():
            continue
        try:
            r = json.loads(ln)
        except Exception:
            continue
        runs.add(r.get("run_id"))
        mid = r.get("manifest_id")
        if not mid:
            continue
        cur = items.setdefault(mid, {"manifest_id": mid, "first_queued": r["ts"]})
        cur.update({"latest_ts": r["ts"], "cluster_id": r.get("cluster_id"),
                    "tier": r.get("tier"), "specialist": r.get("specialist"),
                    "answer_key_matched": cur.get("answer_key_matched")})
    # reconcile latest_type with current disposition (authoritative)
    for mid, cur in items.items():
        st = disp.get(mid, {}).get("status")
        if st in RESOLVED:
            cur["latest_type"] = "executed"
            cur["disposition"] = st
        elif mid in recall_ids:
            cur["latest_type"] = "waived"
        elif st is not None:
            cur["latest_type"] = "skipped"
        else:
            cur.setdefault("latest_type", "skipped")
    rows = list(items.values())
    hp12 = [r for r in rows if r.get("tier") in HIGH_PRIORITY_TIERS]
    done = [r for r in hp12 if r["latest_type"] in ("executed", "waived")]
    cum = {"runs": sorted(r for r in runs if r), "latest_run": latest_run,
           "items_total": len(rows), "items": rows,
           "cumulative_tier12_completion_rate": round(len(done) / len(hp12), 3) if hp12 else 1.0}
    (audit_path("output") / "deep_pass_cumulative.json").write_text(json.dumps(cum, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
