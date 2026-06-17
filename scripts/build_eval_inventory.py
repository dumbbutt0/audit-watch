#!/usr/bin/env python3
"""
build_eval_inventory.py — Consolidate triage buckets + finding-leads + PoC-queue into a
root-cause-deduplicated, honestly-classified EVAL candidate set (deterministic, no LLM).

This is the eval-prep layer. It does NOT re-derive analysis, build PoCs, or mutate any source
artifact — it reads the triage verdicts (which already carry root_cause/evidence/duplicate
reasoning), assigns each raw candidate a root_cause_id via a small curated cluster map, maps the
triage verdict onto an eval classification (never upgrading: uncertainty routes DOWN), and writes:

  output/eval_ready/eval_candidate_inventory.json   every raw candidate, tagged with root_cause_id
  output/eval_ready/eval_findings.json              deduped NEW root-cause clusters (the candidate layer)
  output/eval_ready/eval_findings.md                human-readable
  output/eval_ready/eval_duplicate_map.json         raw candidate -> root_cause_id (+ dup-of-existing)
  output/eval_ready/eval_exclusions.json            duplicate_of_existing / insufficient / FP, excluded

Classification set: confirmed_eval_finding | partial_eval_finding | duplicate_of_existing |
                    false_positive | insufficient_evidence | real_world_poc_later

Scope decision (confirmed with user): eval_findings.json = NEW candidate layer only (does not
re-list the 48 merged findings); the matcher unions it with merged_findings.json.

Usage: python scripts/build_eval_inventory.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402

# ── Cluster metadata: the one curated input (derived from existing triage fields) ──────────────
# classification ∈ confirmed_eval_finding | partial_eval_finding | real_world_poc_later
#                  | duplicate_of_existing | insufficient_evidence | false_positive
CLUSTERS = {
    "transferPlots-allowance-argswap": {
        "title": "MarketplaceFacet.transferPlots passes decrementAllowancePods args in swapped order (allowance bypass on field 0 / DoS on field>0)",
        "classification": "confirmed_eval_finding", "severity_ceiling": "High", "confidence": "Confirmed",
        "match_terms": ["transferPlots", "decrementAllowancePods", "pod allowance", "argument order", "allowance bypass"],
        "include": True,
    },
    "eip712-hardcoded-chainid": {
        "title": "EIP-712 domain separator hardcodes chainId=1 (C.getChainId pure) across LibTokenPermit/LibSiloPermit/LibTractor; reseed targets Arbitrum (42161)",
        "classification": "confirmed_eval_finding", "severity_ceiling": "High", "confidence": "Confirmed",
        "match_terms": ["chainId", "EIP-712", "domain separator", "permit", "Tractor blueprint", "getChainId"],
        "note": "Distinct from CC-005 (migration-specific L1 chainId domain) and AC-003 (wrong blueprint typehash).",
        "include": True,
    },
    "libgauge-sunrise-dos": {
        "title": "LibGauge stepGauge unguarded arithmetic bricks permissionless sunrise (div-by-zero on totalGaugePoints==0; uint32 SafeCast overflow)",
        "classification": "partial_eval_finding", "severity_ceiling": "High", "confidence": "High",
        "match_terms": ["LibGauge", "stepGauge", "sunrise DoS", "gauge points", "division by zero", "season advancement"],
        "note": "NEW arithmetic sites (updateGrownStalkEarnedPerSeason:272 div0; issueGrownStalkPerBdv:305 uint32). The .sub-underflow site (line 351) is the AR-001 duplicate, excluded separately.",
        "include": True,
    },
    "initinvariants-placeholder-baselines": {
        "title": "InitInvariants hardcodes placeholder invariant baselines (TODO) feeding fundsSafu entitlements on every guarded tx (brick if too-high / weakened safety if too-low)",
        "classification": "partial_eval_finding", "severity_ceiling": "High", "confidence": "High",
        "match_terms": ["InitInvariants", "fundsSafu", "placeholder", "internalTokenBalanceTotal", "fertilizedPaidIndex", "entitlements"],
        "include": True,
    },
    "l1tokenfacet-internal-transfer-freeze-bypass": {
        "title": "L1TokenFacet.transferInternalTokenFrom omits checkBeanAsset (present on sibling transferToken) — migration freeze bypass for internal Bean-asset balances",
        "classification": "partial_eval_finding", "severity_ceiling": "High", "confidence": "High",
        "match_terms": ["transferInternalTokenFrom", "checkBeanAsset", "migration freeze", "L1TokenFacet", "internal balance"],
        "include": True,
    },
    "hardcoded-mainnet-addresses-on-l2": {
        "title": "Hardcoded mainnet addresses (C.sol / LibWeth) on the Arbitrum L2 reseed target — wrong/no-code tokens, oracles, wells, fertilizer",
        "classification": "partial_eval_finding", "severity_ceiling": "High", "confidence": "High",
        "match_terms": ["hardcoded address", "mainnet address", "Arbitrum", "WETH", "wstETH", "Chainlink aggregator",
                        "USDC", "CREATE2", "BEAN address", "Fertilizer", "well address", "C.sol constants"],
        "note": ("Single root cause; consumer subclasses for the matcher: "
                 "(a) WETH wrap [DPF-002/003/028/029]; (b) wstETH redemption+oracle [DPF-004/005/008/009/010/011]; "
                 "(c) ETH/USD Chainlink [DPF-006/007]; (d) Well-address constant-vs-CREATE2 mismatch [DPF-012/013/014/015]; "
                 "(e) CREATE2 token mismatch BEAN/urBEAN/urLP [DPF-018..023]; (f) Fertilizer proxy [DPF-024/025]; "
                 "(g) USDC [DPF-026/027]; (h) PIPELINE [DPF-016/017] — FALSE-POSITIVE CANDIDATE: deterministic-deployer "
                 "singleton may reproduce its address cross-chain; needs a getCode check on L2."),
        "include": True,
    },
    # ── real_world_poc_later: source-backed but impact gated on unproven runtime/deploy state ──
    "reseedbean-well-zero-impl-deploy-dos": {
        "title": "ReseedBean hardcodes all three Well implementations (+AQUIFIER) to address(0) under a TODO; ERC1967Proxy(0) reverts → reseed init deploy-DoS",
        "classification": "real_world_poc_later", "severity_ceiling": "High", "confidence": "Medium",
        "match_terms": ["ReseedBean", "Well implementation", "address(0)", "ERC1967Proxy", "deploy DoS", "reseed init"],
        "note": "Static revert is certain; real-world impact conditional on the TODO surviving to the reseed broadcast (a deployment mistake). Hence poc_later, not partial.",
        "include": True,
    },
    "l1tokenfacet-wrapeth-residual-eth": {
        "title": "L1TokenFacet.wrapEth / LibWeth wrap-unwrap lack amount<=msg.value; deposit draws aggregate diamond ETH and unconditional refundEth sweeps residual",
        "classification": "real_world_poc_later", "severity_ceiling": "Medium", "confidence": "Medium",
        "match_terms": ["wrapEth", "LibWeth", "refundEth", "msg.value", "residual ETH", "WETH deposit"],
        "note": "Code logic confirmed; severity hinges on whether the L1 migration diamond holds residual ETH R>0 (unproven). Includes untriaged LibWeth wrap/unwrap/deposit/withdraw mechanics (DPF-030/031/032/033).",
        "include": True,
    },
    "libunripeconvert-wrong-denominator": {
        "title": "LibUnripeConvert.getBeanAmountOut uses wrong UNRIPE_BEAN-vs-LP supply denominator (view-only miscomputation)",
        "classification": "real_world_poc_later", "severity_ceiling": "Low", "confidence": "Medium",
        "match_terms": ["LibUnripeConvert", "getBeanAmountOut", "denominator", "unripe LP", "supply"],
        "note": "Deep-pass decision=finding (Low, view-only); not high-priority-triaged → conservative poc_later.",
        "include": True,
    },
    "libdeltab-lp-supply-ratio": {
        "title": "LibDeltaB deltaB * beforeLpTokenSupply / afterLpTokenSupply ratio (pure) — rounding/scaling concern",
        "classification": "real_world_poc_later", "severity_ceiling": "Low", "confidence": "Speculative",
        "match_terms": ["LibDeltaB", "deltaB", "LP token supply"], "include": True,
    },
    "libreceiving-unknown-recipient": {
        "title": "LibReceiving.receiveShipment/barnReceive silent no-op / mis-dispatch on unknown ShipmentRecipient (mint-accounting loss; governance-route gated)",
        "classification": "real_world_poc_later", "severity_ceiling": "Medium", "confidence": "Speculative",
        "match_terms": ["LibReceiving", "receiveShipment", "ShipmentRecipient", "barnReceive"], "include": True,
    },
    "libdibbler-morning-temp": {
        "title": "LibDibbler morning-temperature / sow accounting rounding (scaleTemperature rounds up vs documented down; sow scaling)",
        "classification": "real_world_poc_later", "severity_ceiling": "Low", "confidence": "Speculative",
        "match_terms": ["LibDibbler", "morning temperature", "scaleTemperature", "sow", "soil"], "include": True,
    },
    "listing-fill-dust": {
        "title": "Listing._fillListing pod/bean rounding dust",
        "classification": "real_world_poc_later", "severity_ceiling": "Low", "confidence": "Speculative",
        "match_terms": ["Listing", "_fillListing", "dust", "rounding"], "include": True,
    },
    # ── excluded clusters (duplicates / insufficient) ──
    "enroot-bdv-downcast": {
        "title": "EnrootFacet enrootDeposit/enrootDeposits uint128(bdv) downcast",
        "classification": "duplicate_of_existing", "duplicate_of": "AR-005", "severity_ceiling": "Info", "confidence": "High",
        "note": "FL-001 over-mint hypothesis refuted (enroot uses defended pump EMA / storage, not spot). Same downcast class as AR-005.",
        "include": False,
    },
    "libgauge-sub-underflow": {
        "title": "LibGauge.updateAverageStalkPerBdvPerSeason → getAverageGrownStalkPerBdv .sub(STALK_BDV_PRECISION) underflow",
        "classification": "duplicate_of_existing", "duplicate_of": "AR-001", "severity_ceiling": "Medium", "confidence": "High",
        "note": "Same revert site/path/precondition/impact as AR-001 (the caller, not a new bug).",
        "include": False,
    },
    "reseedbean-mintandsync": {
        "title": "ReseedBean.mintAndSync",
        "classification": "insufficient_evidence", "severity_ceiling": "Info", "confidence": "High",
        "note": "Dead code behind the address(0) constructor revert; hypothesized tokens()-decode revert never reached. No standalone defect.",
        "include": False,
    },
}

# explicit raw-id → root_cause_id (triaged items + untriaged leads)
ID_TO_CLUSTER = {
    "DPF-036": "transferPlots-allowance-argswap",
    "DPF-001": "eip712-hardcoded-chainid",
    "function:LibGauge:updateGrownStalkEarnedPerSeason#4bcba620": "libgauge-sunrise-dos",
    "function:LibGauge:issueGrownStalkPerBdv#1b02171c": "libgauge-sunrise-dos",
    "DPF-042": "initinvariants-placeholder-baselines",
    "DPF-043": "initinvariants-placeholder-baselines",
    "constant:ReseedBean:CP2_U_BEAN_ETH_WELL_IMPLMENTATION#9466ed7e": "reseedbean-well-zero-impl-deploy-dos",
    "initializer:ReseedBean:init#89ca74fb": "reseedbean-well-zero-impl-deploy-dos",
    "DPF-044": "l1tokenfacet-wrapeth-residual-eth",
    "DPF-045": "l1tokenfacet-internal-transfer-freeze-bypass",
    "function:LibGauge:updateAverageStalkPerBdvPerSeason#057e89a1": "libgauge-sub-underflow",
    "function:EnrootFacet:enrootDeposit#f669e65c": "enroot-bdv-downcast",
    "function:EnrootFacet:enrootDeposits#5f691bb7": "enroot-bdv-downcast",
    "function:ReseedBean:mintAndSync#448f1571": "reseedbean-mintandsync",
    # untriaged lower-priority leads
    "DPF-030": "l1tokenfacet-wrapeth-residual-eth", "DPF-031": "l1tokenfacet-wrapeth-residual-eth",
    "DPF-032": "l1tokenfacet-wrapeth-residual-eth", "DPF-033": "l1tokenfacet-wrapeth-residual-eth",
    "DPF-034": "libunripeconvert-wrong-denominator",
    "DPF-035": "libdeltab-lp-supply-ratio",
    "DPF-037": "libreceiving-unknown-recipient", "DPF-038": "libreceiving-unknown-recipient",
    "DPF-039": "libdibbler-morning-temp", "DPF-040": "libdibbler-morning-temp", "DPF-041": "libdibbler-morning-temp",
    "DPF-046": "listing-fill-dust",
}
# DPF-002 .. DPF-029 → hardcoded address bundle
for n in range(2, 30):
    ID_TO_CLUSTER[f"DPF-{n:03d}"] = "hardcoded-mainnet-addresses-on-l2"
# fix the ones already explicitly set above (030..046 set explicitly; 002-029 are the bundle)


def _items(path: Path, key: str):
    if not path.exists():
        return []
    d = json.loads(path.read_text())
    return d.get(key, d if isinstance(d, list) else [])


def _str_evidence(v):
    e = v.get("evidence_spans") or v.get("evidence") or []
    if isinstance(e, str):
        e = [e]
    return e


def main() -> int:
    tri = audit_path("output") / "triage"
    out = audit_path("output") / "eval_ready"
    out.mkdir(parents=True, exist_ok=True)

    merged_ids = {f.get("id") or f.get("finding_id")
                  for f in _items(audit_path("output") / "merged_findings.json", "findings")}

    inventory = []      # every raw candidate
    seen_keys = set()

    def add(raw_id, source, rec, cluster=None, dup_existing=None):
        if not raw_id:
            return
        key = (source, raw_id)
        if key in seen_keys:
            return
        seen_keys.add(key)
        inventory.append({
            "raw_id": raw_id, "source": source,
            "root_cause_id": cluster, "duplicate_of_existing": dup_existing,
            "title": rec.get("title") or rec.get("name") or "",
            "file": rec.get("file", ""), "contract": rec.get("contract", ""),
            "function": rec.get("function") or rec.get("name", ""),
            "manifest_refs": rec.get("manifest_refs") or ([rec.get("manifest_id")] if rec.get("manifest_id") else []),
            "severity_ceiling": rec.get("severity_ceiling", ""),
            "triage_verdict": rec.get("verdict", ""),
            "triaged": bool(rec.get("verdict")),
            "evidence_spans": _str_evidence(rec),
        })

    # 1) triage buckets (authoritative verdicts)
    for fn, key in [("confirmed_findings.json", "items"), ("poc_required.json", "items"),
                    ("duplicates.json", "items")]:
        for v in _items(tri / fn, key):
            rid = v.get("id")
            add(rid, f"triage:{fn}", v, cluster=ID_TO_CLUSTER.get(rid), dup_existing=v.get("duplicate_of"))
    # insufficient_evidence lives in high_priority_triage_results.out_of_scope_or_insufficient
    hp = audit_path("output") / "triage" / "high_priority_triage_results.json"
    if hp.exists():
        for v in json.loads(hp.read_text()).get("out_of_scope_or_insufficient", []):
            add(v.get("id"), "triage:insufficient", v, cluster=ID_TO_CLUSTER.get(v.get("id")))

    # 2) finding_leads (catches the untriaged lower-priority leads)
    for l in _items(audit_path("output") / "deep_pass_execution" / "finding_leads.json", "leads"):
        lid = l.get("lead_id")
        rec = {"title": l.get("title"), "name": l.get("name"), "file": l.get("file"),
               "severity_ceiling": l.get("severity_ceiling"), "verdict": l.get("triage_status", ""),
               "manifest_id": l.get("manifest_id")}
        add(lid, "finding_leads", rec, cluster=ID_TO_CLUSTER.get(lid))

    # 3) poc_queue — DPF-lead refs fold into the lead's cluster; existing-finding refs → dup_of_existing
    for q in _items(audit_path("output") / "poc_queue.json", "poc_queue"):
        refs = q.get("finding_refs") or []
        dpf = next((r for r in refs if str(r).startswith("DPF")), None)
        existing = next((r for r in refs if r in merged_ids), None)
        cluster = ID_TO_CLUSTER.get(dpf) if dpf else None
        rid = q.get("manifest_id") or (dpf or (refs[0] if refs else None))
        rec = {"title": q.get("name"), "name": q.get("name"), "file": q.get("file"),
               "severity_ceiling": q.get("severity_ceiling"), "manifest_id": q.get("manifest_id")}
        add(f"pocq:{rid}", "poc_queue", rec, cluster=cluster, dup_existing=existing)

    # ── assign untagged inventory rows ──
    for r in inventory:
        if r["root_cause_id"]:
            continue
        if r["duplicate_of_existing"]:
            r["root_cause_id"] = f"dup-existing::{r['duplicate_of_existing']}"
        else:
            r["root_cause_id"] = "unassigned-review"

    # ── build clusters ──
    clusters = {}
    for r in inventory:
        cid = r["root_cause_id"]
        c = clusters.setdefault(cid, {"root_cause_id": cid, "members": [], "files": set(),
                                      "functions": set(), "manifest_refs": set(), "evidence_spans": set(),
                                      "severities": set(), "triaged_any": False})
        c["members"].append(r["raw_id"])
        if r["file"]:
            c["files"].add(r["file"])
        if r["function"]:
            c["functions"].add(r["function"])
        for m in r["manifest_refs"]:
            if m:
                c["manifest_refs"].add(m)
        for e in r["evidence_spans"]:
            c["evidence_spans"].add(e)
        if r["severity_ceiling"]:
            c["severities"].add(r["severity_ceiling"])
        c["triaged_any"] = c["triaged_any"] or r["triaged"]

    eval_findings, exclusions, dup_map_clusters = [], [], []
    eid = 1
    for cid, c in clusters.items():
        meta = CLUSTERS.get(cid, {})
        is_dup_existing = cid.startswith("dup-existing::")
        dup_target = meta.get("duplicate_of") or (cid.split("::", 1)[1] if is_dup_existing else None)
        classification = meta.get("classification") or ("duplicate_of_existing" if is_dup_existing else "real_world_poc_later")
        title = meta.get("title") or (sorted(c["functions"])[:1] or ["(review)"])[0]
        entry = {
            "root_cause_id": cid, "title": title, "classification": classification,
            "severity_ceiling": meta.get("severity_ceiling") or ("/".join(sorted(c["severities"]))[:40]),
            "confidence": meta.get("confidence", "Medium" if c["triaged_any"] else "Speculative"),
            "duplicate_of": dup_target,
            "affected_contracts": sorted({f.split("/")[-1] for f in c["files"]}),
            "affected_functions": sorted(c["functions"]),
            "evidence_spans": sorted(c["evidence_spans"]),
            "source_leads": sorted(set(c["members"])),
            "manifest_refs": sorted(c["manifest_refs"]),
            "match_terms": meta.get("match_terms", []),
            "notes_for_matcher": meta.get("note", ""),
            "untriaged_default": (not c["triaged_any"]) and classification == "real_world_poc_later" and not is_dup_existing,
        }
        dup_map_clusters.append({"root_cause_id": cid, "classification": classification,
                                 "duplicate_of": dup_target, "members": sorted(set(c["members"]))})
        if meta.get("include") is True and not is_dup_existing:
            entry["eval_id"] = f"EVAL-{eid:03d}"; eid += 1
            eval_findings.append(entry)
        else:
            exclusions.append(entry)

    # order eval_findings: confirmed first, then partial, then poc_later
    order = {"confirmed_eval_finding": 0, "partial_eval_finding": 1, "real_world_poc_later": 2}
    eval_findings.sort(key=lambda e: (order.get(e["classification"], 9), e["eval_id"]))

    ts = datetime.now(timezone.utc).isoformat()
    (out / "eval_candidate_inventory.json").write_text(json.dumps(
        {"generated_at": ts, "candidates_in": len(inventory), "inventory": inventory}, indent=2))
    (out / "eval_findings.json").write_text(json.dumps(
        {"generated_at": ts, "scope": "new_candidate_layer_only", "count": len(eval_findings),
         "eval_findings": eval_findings}, indent=2))
    (out / "eval_duplicate_map.json").write_text(json.dumps(
        {"generated_at": ts, "candidate_to_root_cause": [
            {"raw_id": r["raw_id"], "source": r["source"], "root_cause_id": r["root_cause_id"],
             "duplicate_of_existing": r["duplicate_of_existing"]} for r in inventory],
         "clusters": dup_map_clusters}, indent=2))
    (out / "eval_exclusions.json").write_text(json.dumps(
        {"generated_at": ts, "count": len(exclusions), "excluded_clusters": exclusions}, indent=2))

    # markdown
    from collections import Counter
    counts = Counter(e["classification"] for e in eval_findings)
    excl_counts = Counter(e["classification"] for e in exclusions)
    lines = [f"# Eval-Ready Findings — Beanstalk eval2 (root-cause deduped)\n",
             f"_Generated {ts} · scope: NEW candidate layer only (unions with the 48 merged findings)_\n",
             f"Raw candidates: **{len(inventory)}** → root-cause clusters: **{len(clusters)}** "
             f"→ eval findings: **{len(eval_findings)}** · excluded: **{len(exclusions)}**\n",
             "## Classification counts",
             f"- confirmed_eval_finding: {counts.get('confirmed_eval_finding',0)}",
             f"- partial_eval_finding: {counts.get('partial_eval_finding',0)}",
             f"- real_world_poc_later: {counts.get('real_world_poc_later',0)}",
             f"- (excluded) duplicate_of_existing: {excl_counts.get('duplicate_of_existing',0)}",
             f"- (excluded) insufficient_evidence: {excl_counts.get('insufficient_evidence',0)}",
             f"- (excluded) false_positive: {excl_counts.get('false_positive',0)}\n",
             "## Eval findings (confirmed → partial → poc_later)\n",
             "| eval_id | class | sev | title |", "|---|---|---|---|"]
    for e in eval_findings:
        lines.append(f"| {e['eval_id']} | {e['classification'].replace('_eval_finding','').replace('real_world_','')} "
                     f"| {e['severity_ceiling']} | {e['title']} |")
    lines.append("\n## Per-cluster detail\n")
    for e in eval_findings:
        lines += [f"### {e['eval_id']} — {e['title']}",
                  f"- **classification:** {e['classification']} · **severity_ceiling:** {e['severity_ceiling']} · **confidence:** {e['confidence']}",
                  f"- **affected:** {', '.join(e['affected_contracts'])}",
                  f"- **source_leads:** {', '.join(e['source_leads'])}",
                  f"- **match_terms:** {', '.join(e['match_terms'])}",
                  (f"- **notes:** {e['notes_for_matcher']}" if e['notes_for_matcher'] else ""),
                  (f"- **untriaged_default** (no high-priority verdict; conservative)" if e['untriaged_default'] else ""), ""]
    lines.append("## Excluded (not counted as new eval findings)\n")
    for e in exclusions:
        tgt = f" → {e['duplicate_of']}" if e.get("duplicate_of") else ""
        lines.append(f"- **{e['root_cause_id']}** [{e['classification']}{tgt}] — {e['title']}")
    (out / "eval_findings.md").write_text("\n".join(l for l in lines if l is not None))

    print(f"[ok] build_eval_inventory: candidates={len(inventory)} clusters={len(clusters)} "
          f"eval_findings={len(eval_findings)} excluded={len(exclusions)}")
    print(f"     classes: {dict(counts)}  excluded: {dict(excl_counts)}")
    unassigned = [r["raw_id"] for r in inventory if r["root_cause_id"] == "unassigned-review"]
    if unassigned:
        print(f"     [warn] unassigned-review ({len(unassigned)}): {unassigned[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
