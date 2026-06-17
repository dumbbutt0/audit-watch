#!/usr/bin/env python3
"""
cross_artifact_lifecycle_audit.py — recall lens: surface in-scope contracts that control an artifact's
lifecycle (deploy/init/own/upgrade/configure/custody) so the artifact stays audit-relevant THROUGH the
controller even when the artifact file is OUT of strict scope (ArkProject AK-H4 miss).

Statuses (per the spec): cross_artifact_lifecycle_risk | cross_artifact_scope_linked |
lifecycle_under_escalated | lifecycle_cleared_with_local_proof. NOT a gate; never mutates dispositions.
Writes output/cross_artifact_lifecycle_audit.{json,md}.

Usage: python scripts/cross_artifact_lifecycle_audit.py [--manifest <path>] [--no-source]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
import cross_artifact_lifecycle_taxonomy as cal  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
_FILE_CACHE: dict[str, list[str]] = {}
_NEW_RE = re.compile(r"new\s+([A-Z]\w*)\s*\(")
_DEPLOYFN_RE = re.compile(r"deploy([A-Z]\w*)\s*\(")


def _snippet(file_rel, start, end, use_source):
    if not use_source or not file_rel or not start:
        return ""
    if file_rel not in _FILE_CACHE:
        try:
            _FILE_CACHE[file_rel] = (ROOT / file_rel).read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            _FILE_CACHE[file_rel] = []
    lines = _FILE_CACHE[file_rel]
    return "\n".join(lines[max(0, (start or 1) - 1):min(len(lines), end or start or 1)])[:4000] if lines else ""


def _load(path: Path, key: str):
    if not path.exists():
        return [] if key else {}
    try:
        d = json.loads(path.read_text())
        return d.get(key, []) if key else d
    except (OSError, json.JSONDecodeError):
        return [] if key else {}


def _controlled_artifact_names(snippet: str) -> list[str]:
    names = set(_NEW_RE.findall(snippet or "")) | set(_DEPLOYFN_RE.findall(snippet or ""))
    # drop obvious infra types so the scope-link stays meaningful
    return sorted(n for n in names if n not in {"Request", "Bytes", "Array", "String"})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest")
    ap.add_argument("--no-source", action="store_true")
    args = ap.parse_args()

    man_path = Path(args.manifest) if args.manifest else audit_path("output") / "coverage_manifest.json"
    items = _load(man_path, "items")
    if not items:
        raise SystemExit(f"[cross_artifact_lifecycle_audit] no manifest items at {man_path}")
    tax = cal.load_taxonomy()
    disp = {d["manifest_id"]: d for d in _load(audit_path("output") / "coverage_dispositions.json", "dispositions")}
    use_source = not args.no_source

    # index manifest contracts (incl. deferred_out_of_scope) for scope-linking the controlled artifact
    contracts_by_name: dict[str, list[str]] = {}
    deferred_contracts = set()
    for it in items:
        c = (it.get("contract") or "")
        if c:
            contracts_by_name.setdefault(c, []).append(it["id"])
        d = disp.get(it["id"], {})
        if d.get("status") == "deferred_out_of_scope" and c:
            deferred_contracts.add(c)

    def _cov(mid):
        st = disp.get(mid, {}).get("status")
        return ("covered_by_finding" if st == "finding" else "examined_but_cleared" if st == "cleared"
                else "deferred" if st == "deferred_out_of_scope" else "uncovered")

    detected, under_escalated, scope_linked = [], [], []
    for it in items:
        if it.get("kind") not in ("function", "constructor", "initializer"):
            continue
        if not it.get("in_scope", True):
            continue
        span = it.get("source_span", {})
        snip = _snippet(it.get("file", ""), span.get("start_line"), span.get("end_line"), use_source)
        cls = cal.classify(it.get("name", ""), it.get("signature", ""), it.get("file", ""),
                           it.get("contract", ""), snippet=snip, tags=it.get("tags"))
        if not cls.get("cross_artifact_sensitive"):
            continue
        cov = _cov(it["id"])
        missing = cls["missing_lifecycle"]
        artifacts = _controlled_artifact_names(snip + " " + (it.get("signature") or ""))
        # scope-link: does a controlled artifact resolve to a manifest contract (esp. deferred_out_of_scope)?
        links = []
        for a in artifacts:
            if a in contracts_by_name:
                links.append({"artifact": a, "manifest_ids": contracts_by_name[a],
                              "out_of_scope": a in deferred_contracts})
        # primary status
        if not missing:
            status = "lifecycle_cleared_with_local_proof"
        elif cov == "covered_by_finding":
            status = "cross_artifact_lifecycle_risk"
        else:
            status = "lifecycle_under_escalated"
        row = {
            "manifest_id": it["id"], "name": it.get("name"), "contract": it.get("contract"),
            "file": it.get("file"), "line": span.get("start_line"),
            "role": cls["role"], "deployed_kind": cls["deployed_kind"],
            "lifecycle_signals": cls["lifecycle_signals"], "missing_lifecycle": missing,
            "controlled_artifacts": artifacts, "scope_links": links,
            "status": status, "high_risk": cal.is_high_risk(cls, tax),
            "severity_ceiling_hint": cls["severity_ceiling_hint"], "coverage": cov,
            "clear_reason": (disp.get(it["id"], {}).get("clear_reason") or "")[:160]
            if cov == "examined_but_cleared" else "",
        }
        detected.append(row)
        if status == "lifecycle_under_escalated":
            under_escalated.append(row)
        if links:
            scope_linked.append(row)

    by_status = Counter(x["status"] for x in detected)
    by_role = Counter(x["role"] for x in detected)
    packets = []
    for x in under_escalated:
        packets.append({"packet_id": f"XAL-{x['contract']}-{x['name']}", "label": "cross_artifact_lifecycle",
                        "suggested_specialist": "upgrade_storage", "manifest_id": x["manifest_id"],
                        "severity_ceiling_hint": x["severity_ceiling_hint"],
                        "review_prompt": (f"{x['contract']}.{x['name']} controls an artifact's lifecycle "
                                          f"(role={x['role']}, deploys/holds {x['deployed_kind']}) but is MISSING "
                                          f"{x['missing_lifecycle']} and is not filed as a finding. The controlled "
                                          f"artifact's lifecycle is in-scope through this controller. " + tax.get("review_hint", ""))})

    ts = datetime.now(timezone.utc).isoformat()
    report = {
        "lens": "cross_artifact_lifecycle", "generated_at": ts, "manifest": str(man_path), "is_gate": False,
        "source_snippets": use_source,
        "total_cross_artifact_sensitive": len(detected),
        "by_status": dict(by_status), "by_role": dict(by_role),
        "lifecycle_under_escalated": [x["manifest_id"] for x in under_escalated],
        "cross_artifact_scope_linked": [{"manifest_id": x["manifest_id"], "links": x["scope_links"]} for x in scope_linked],
        "recommended_review_packets": packets,
        "detected": detected,
    }
    out = audit_path("output") / "cross_artifact_lifecycle_audit.json"
    out.write_text(json.dumps(report, indent=2))

    md = [f"# Cross-artifact lifecycle audit\n", f"_Generated {ts} · manifest `{man_path}` · NOT a gate_\n",
          f"**{len(detected)}** cross-artifact controllers · **{len(under_escalated)}** lifecycle_under_escalated · "
          f"**{len(scope_linked)}** scope-linked to a manifest artifact\n",
          "## By status", "| status | n |", "|---|---|"] + [f"| {s} | {n} |" for s, n in by_status.most_common()]
    md += ["\n## ⚠ lifecycle_under_escalated (controller has a missing lifecycle step, NOT filed)\n",
           "| contract.name | role | deployed_kind | missing | controlled_artifacts |", "|---|---|---|---|---|"]
    for x in under_escalated:
        md.append(f"| {x['contract']}.{x['name']} | {x['role']} | {x['deployed_kind']} | "
                  f"{', '.join(x['missing_lifecycle'])} | {', '.join(x['controlled_artifacts']) or '—'} |")
    md += ["\n## Scope-linked (out-of-scope artifact controlled by in-scope code)\n"]
    for x in scope_linked:
        for l in x["scope_links"]:
            md.append(f"- {x['contract']}.{x['name']} → `{l['artifact']}` (out_of_scope={l['out_of_scope']})")
    (audit_path("output") / "cross_artifact_lifecycle_audit.md").write_text("\n".join(md) + "\n")

    print(f"[ok] cross_artifact_lifecycle_audit → {out}")
    print(f"     detected {len(detected)} · under_escalated {len(under_escalated)} · scope_linked {len(scope_linked)}")
    print(f"     by_status {dict(by_status)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
