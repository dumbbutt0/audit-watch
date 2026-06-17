#!/usr/bin/env python3
"""
deep_pass_queue.py — Cluster the needs_deep_pass backlog into specialist packets (deterministic, no LLM).

The cheap sweep escalates non-trivial items to `needs_deep_pass` (disposition status `assigned` with
assigned_pass=`deep`). Left as a flat list of ids that queue is unmanageable. This groups them into
prioritized, specialist-routed packets so a deep pass can be run cluster-by-cluster.

Reads output/coverage_manifest.json, output/coverage_dispositions.json, config/agent_policy.json.
Writes output/deep_pass_queue.json. Pure queue-management artifact — NOT a gate.

Usage:
    python scripts/deep_pass_queue.py
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
import special_focus_terms as sft  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

# Execution-priority tiers (Panoptic conversion-engine): which deep passes to spend budget on FIRST.
# 1 advisory-escalation hits · 2 special-focus w/ external call or asset movement · 3 liquidation/
# solvency/oracle/collateral/accounting · 4 reentrancy/access-control/init · 5 invariant near-misses ·
# 6 remaining backlog. Tiers 1-2 are "high priority" (the freeze ledger blocks if they're skipped).
HIGH_PRIORITY_TIERS = {1, 2}
ASSET_MOVE_RE = re.compile(r"transfer|withdraw|deposit|settle|mint|burn|refund|delegate|redeem|\bpay", re.I)
TIER3_RE = re.compile(r"liquidat|solven|oracle|collateral|account|\bmargin\b|\bdebt\b|twap|\bema\b|premium|bonus", re.I)
TIER4_RE = re.compile(r"reentr|permission|\binit\b|owner|admin|guardian|\brole\b|access", re.I)


def _tier_of(it: dict, d: dict) -> tuple[int, str]:
    rr = d.get("routed_reason") or ""
    text = ((it.get("name") or "") + " " + (it.get("signature") or "") + " "
            + " ".join(it.get("tags") or [])).lower()
    if rr.startswith("advisory_escalation") or d.get("advisory_escalation"):
        return 1, "advisory-escalation hit"
    if sft.is_special_focus(it) and (it.get("external_calls") or ASSET_MOVE_RE.search(text)):
        return 2, "special-focus with external call / asset movement"
    if TIER3_RE.search(text):
        return 3, "liquidation/solvency/oracle/collateral/accounting surface"
    if it.get("external_calls") or TIER4_RE.search(text) or it.get("kind") in ("initializer", "constructor"):
        return 4, "reentrancy/access-control/init surface"
    agent = (d.get("assigned_agent") or "").lower()
    if "invariant" in rr or "intended_gate" in rr or "cross_function" in agent or "checkpoint" in agent:
        return 5, "invariant / liveness near-miss"
    return 6, "remaining backlog"

# Ordered classifier: first matching rule assigns the cluster label. (label, priority, specialist).
# Priority 1 = highest. Mirrors the rollout priority rules.
LABELS = {
    "oracle_accounting":                    (1, "oracle"),
    "token_mint_burn_transfer":             (1, "token_integration"),
    "migration_reseed_init":                (2, "logic"),
    "cross_chain_bridge_message_validation":(2, "cross_chain"),
    "external_calls_arbitrary_call":        (3, "reentrancy"),
    "constants_decimals_config":            (4, "arithmetic"),
    "loops_dos_gas_growth":                 (5, "dos"),
    "permissions_admin":                    (6, "access_control"),
    "misc_high_risk":                       (7, "logic"),
}

REVIEW_HINT = {
    "oracle_accounting": "ITE-decompose each oracle/accounting path: source of price/value, manipulation surface, decimals/precision, and the consumer that acts on it. Produce a finding or a STRONG clear (attacker_reachability+guard_or_invariant+no_impact_reason).",
    "token_mint_burn_transfer": "Check mint/burn/transfer authorization, balance accounting vs actual received (fee-on-transfer/rebasing), and supply invariants.",
    "migration_reseed_init": "Re-derive the per-field reseed/init accounting invariant: is every global/per-account total set exactly once and consistently? Look for = vs +=, uninitialized globals, ordering, replay.",
    "cross_chain_bridge_message_validation": "Verify message/proof/signature validation, spent-markers/nonces, L1<->L2 address pairing, and hardcoded cross-domain constants.",
    "external_calls_arbitrary_call": "Trace arbitrary-call / Pipeline execution: reentrancy guard coverage, who the call executes as, and mid-batch invariant exposure.",
    "constants_decimals_config": "Confirm each constant/immutable/address: its use, whether a wrong/stale/cross-domain value is exploitable, and whether it is admin-set vs hardcoded.",
    "loops_dos_gas_growth": "Check loop bounds, unbounded growth, external-call-in-loop, and division-by-zero/revert DoS on core flows (sunrise/silo/field/migration).",
    "permissions_admin": "Confirm the access boundary (modifier/role), two-step ownership, and that no privileged action is reachable by an attacker.",
    "misc_high_risk": "General ITE pass: attacker entrypoint, corrupted state, consumer, and impact.",
}


def _label_of(it: dict) -> str:
    tags = set(it.get("tags", []))
    file_l = (it.get("file") or "").lower()
    kind = it.get("kind")
    cross = any(k in file_l for k in ("reciever", "receiver", "bridge", "/migration/", "l2migration", "l1token", "migratel"))
    if cross:
        return "cross_chain_bridge_message_validation"
    if "oracle" in tags or "accounting" in tags:
        return "oracle_accounting"
    if "token" in tags:
        return "token_mint_burn_transfer"
    if "migration" in tags or kind in ("initializer", "constructor"):
        return "migration_reseed_init"
    if "external_call" in tags or it.get("external_calls"):
        return "external_calls_arbitrary_call"
    if kind in ("constant", "immutable", "address") or "decimals" in tags or "config" in tags:
        return "constants_decimals_config"
    if "loop" in tags or "dos" in tags:
        return "loops_dos_gas_growth"
    if "permissions" in tags:
        return "permissions_admin"
    return "misc_high_risk"


def main() -> int:
    man_path = audit_path("output") / "coverage_manifest.json"
    disp_path = audit_path("output") / "coverage_dispositions.json"
    if not man_path.exists() or not disp_path.exists():
        raise SystemExit("[deep_pass_queue] manifest or dispositions missing — build/init first.")
    items = {i["id"]: i for i in json.loads(man_path.read_text()).get("items", [])}
    disp = {d["manifest_id"]: d for d in json.loads(disp_path.read_text()).get("dispositions", [])}

    # needs_deep_pass = in-scope, status 'assigned' with assigned_pass 'deep'
    queue = [items[mid] for mid in items
             if items[mid].get("in_scope", True)
             and disp.get(mid, {}).get("status") == "assigned"
             and disp.get(mid, {}).get("assigned_pass") == "deep"]

    # Sub-cluster by (label, contract) so packets stay reviewable — a single 200-item "packet"
    # is not a useful specialist task. cap_per_cluster bounds packet size; oversized (label,contract)
    # groups are split into numbered chunks.
    CAP = 40
    by_group: dict[tuple, list[dict]] = defaultdict(list)
    for it in queue:
        by_group[(_label_of(it), it.get("contract") or "?")].append(it)

    clusters = []
    for (label, contract), gitems in by_group.items():
        prio, specialist = LABELS[label]
        # split oversized groups into chunks
        chunks = [gitems[i:i + CAP] for i in range(0, len(gitems), CAP)] or [gitems]
        for ci, its in enumerate(chunks):
            suffix = f"-{ci+1}" if len(chunks) > 1 else ""
            clusters.append(_make_cluster(label, prio, specialist, contract, its, disp, suffix))
    _print_and_write(clusters, queue)
    return 0


def _make_cluster(label, prio, specialist, contract, its, disp, suffix):
    # prefer the suggested_agent the sweep proposed, if consistent
    sugg = [disp[i["id"]].get("assigned_agent") for i in its if disp[i["id"]].get("assigned_agent")]
    suggested = max(set(sugg), key=sugg.count) if sugg else specialist
    files = sorted({i["file"] for i in its})
    tags = sorted({t for i in its for t in i.get("tags", [])})
    hi = sum(1 for i in its if i.get("attack_surface_score", 0) >= 3)
    # execution priority tier = the most urgent tier any item in the cluster triggers (lowest number).
    tiers = [_tier_of(i, disp.get(i["id"], {})) for i in its]
    tier_n, tier_reason = min(tiers, key=lambda t: t[0]) if tiers else (6, "remaining backlog")
    return {
        "cluster_id": f"DPQ-{label}-{contract}{suffix}",
        "label": label,
        "priority": prio,
        "priority_tier": tier_n,
        "tier_reason": tier_reason,
        "contract": contract,
        "reason": f"{len(its)} needs_deep_pass items ({hi} score>=3) in {contract} across {len(files)} files",
        "contracts": [contract],
        "files": files,
        "tags": tags,
        "item_ids": sorted(i["id"] for i in its),
        "high_score_items": hi,
        "suggested_specialist": suggested,
        "review_prompt": (f"Run the {suggested} specialist over these {len(its)} {label} items in "
                          f"{contract} ({', '.join(f.split('/')[-1] for f in files[:5])}"
                          f"{' …' if len(files) > 5 else ''}). " + REVIEW_HINT[label]),
    }


def _print_and_write(clusters, queue):
    # Sort by execution tier first (the conversion-engine priority), then label-priority, then size.
    clusters.sort(key=lambda c: (c["priority_tier"], c["priority"], -len(c["item_ids"])))
    schedule: dict[str, list[str]] = defaultdict(list)
    for pos, c in enumerate(clusters, 1):
        c["execution_position"] = pos
        schedule[f"tier_{c['priority_tier']}"].append(c["cluster_id"])
    high_priority = [c for c in clusters if c["priority_tier"] in HIGH_PRIORITY_TIERS]
    out = {
        "schema_version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "needs_deep_pass_total": len(queue),
            "clusters": len(clusters),
            "high_score_items": sum(1 for i in queue if i.get("attack_surface_score", 0) >= 3),
            "high_priority_clusters": len(high_priority),
            "items_by_tier": {str(t): sum(len(c["item_ids"]) for c in clusters if c["priority_tier"] == t)
                              for t in sorted({c["priority_tier"] for c in clusters})},
        },
        "execution_schedule": dict(schedule),
        "clusters": clusters,
    }
    (audit_path("output") / "deep_pass_queue.json").write_text(json.dumps(out, indent=2))
    print("[ok] deep-pass queue → output/deep_pass_queue.json")
    print(f"     needs_deep_pass: {len(queue)} · clusters: {len(clusters)} · "
          f"high-priority(tier1-2): {len(high_priority)} · high-score: {out['summary']['high_score_items']}")
    print("     execution order (by tier):")
    for c in clusters[:10]:
        print(f"       #{c['execution_position']:>2} T{c['priority_tier']} {c['cluster_id']:<46} "
              f"{len(c['item_ids']):>3} items ({c['high_score_items']} hi) → {c['suggested_specialist']}")
    largest = sorted(clusters, key=lambda c: -len(c["item_ids"]))[:3]
    print("     largest: " + ", ".join(f"{c['cluster_id']}({len(c['item_ids'])})" for c in largest))


if __name__ == "__main__":
    raise SystemExit(main())
