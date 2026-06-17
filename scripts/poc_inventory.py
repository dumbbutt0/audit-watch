#!/usr/bin/env python3
"""
poc_inventory.py — Build the PoC-required worklist (deterministic, no LLM).

Enumerates every candidate that needs a real-world PoC and records what each PoC must prove, plus the
current PoC/validation status. It does NOT create tests — it only builds the worklist consumed by
collect_poc_results.py / validate_poc.py / poc_validation_gate.py.

Sources (each optional; missing files are skipped gracefully):
    output/merged_findings.json              (real findings: id/severity/location/manifest_refs/impact)
    output/triage/confirmed_findings.json    (triage-confirmed bucket, if present)
    output/poc_queue.json                    (legacy queue, if present)
    output/eval_ready/eval_findings.json     (eval candidates -> not_required_eval_only)
    data/poc_queue/results.jsonl             (existing forge/cargo PoC results, to mark poc_exists_*)
    data/runtime_poc/results.jsonl           (existing L3 runtime PoC results)
    output/poc_validation/poc_validation_results.json (this layer's own validation, to mark validated)
    output/coverage_manifest.json / coverage_dispositions.json (manifest cross-ref)

Writes: output/poc_validation/poc_inventory.json

Severity policy: High/Critical always require a PoC; Medium requires a PoC when its impact looks like
fund-loss / freeze / overmint / DoS / accounting-drift / authz-bypass; Low/Info and eval-layer
candidates are not_required (eval recall is never gated by PoCs).

Usage:
    python scripts/poc_inventory.py [--quiet]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path, load_jsonl  # noqa: E402

PROOF_IMPACT_RE = re.compile(
    r"\b(loss|lose|drain|steal|theft|overmint|over-mint|inflat|insolven|freeze|frozen|lock|"
    r"stuck|dos|denial|griefing|accounting|underflow|overflow|bypass|unauthor|authoriz|escalat)\w*",
    re.IGNORECASE,
)


def _load_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def _fid(rec: dict) -> str | None:
    return rec.get("id") or rec.get("finding_id") or rec.get("eval_id") or rec.get("lead_id")


def _severity(rec: dict) -> str:
    sev = rec.get("severity") or rec.get("severity_ceiling") or (rec.get("ice", {}) or {}).get("severity_ceiling")
    return (sev or "Unknown").title() if isinstance(sev, str) else "Unknown"


def _affected_functions(rec: dict) -> list[str]:
    fns = list(rec.get("affected_functions") or [])
    loc = rec.get("location") or {}
    if loc.get("function"):
        fns.append(loc["function"])
    return sorted(set(f for f in fns if f))


def _affected_files(rec: dict) -> list[str]:
    files = list(rec.get("affected_files") or rec.get("affected_contracts") or [])
    loc = rec.get("location") or {}
    if loc.get("file"):
        files.append(loc["file"])
    return sorted(set(f for f in files if f))


def _impact_text(rec: dict) -> str:
    parts = [rec.get("impact", ""), rec.get("title", ""), rec.get("vuln_type", "")]
    ice = rec.get("ice_chain") or {}
    parts.append(ice.get("impact", ""))
    return " ".join(p for p in parts if isinstance(p, str))


def _required_proof_type(rec: dict) -> str:
    """Heuristic: oracle/price/liquidity/fork-dependent -> fork; invariant/conservation -> invariant;
    pure-source severity-obvious low -> static_proof; otherwise unit."""
    blob = _impact_text(rec).lower() + " " + " ".join(_affected_files(rec)).lower()
    if any(k in blob for k in ("oracle", "price", "twap", "chainlink", "liquidity", "fork", "mainnet", "deployed")):
        return "fork"
    if any(k in blob for k in ("invariant", "conservation", "accounting", "sum of", "totals match")):
        return "invariant"
    return "unit"


def _poc_required(rec: dict, source: str) -> bool:
    if source == "eval":
        return False
    sev = _severity(rec)
    if sev in ("Critical", "High"):
        return True
    if sev == "Medium":
        return bool(PROOF_IMPACT_RE.search(_impact_text(rec)))
    return False


def _attacker_entrypoint(rec: dict) -> str:
    ite = rec.get("ite") or {}
    ice = rec.get("ice_chain") or {}
    return (ice.get("exploit_path") or ite.get("technique")
            or (rec.get("location") or {}).get("function") or "unprivileged external call to the affected function")


def _impact_assertion(rec: dict) -> str:
    impact = (rec.get("impact") or (rec.get("ice_chain") or {}).get("impact") or "").strip()
    return impact or "assert the claimed loss/freeze/overmint/DoS/authz-bypass on named state, before vs after"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    out = audit_path("output")
    # --- existing PoC capture (to mark status) ---
    poc_done: dict[str, dict] = {}
    for rel in ("data/poc_queue/results.jsonl", "data/runtime_poc/results.jsonl"):
        for r in load_jsonl(audit_path(*rel.split("/"))):
            fid = r.get("finding_id")
            if fid:
                poc_done[fid] = r
    validated: dict[str, dict] = {}
    vres = _load_json(out / "poc_validation" / "poc_validation_results.json")
    if isinstance(vres, dict):
        for r in vres.get("results", []):
            if r.get("finding_id"):
                validated[r["finding_id"]] = r

    # --- collect candidates from each source (first source wins on dup id) ---
    seen: dict[str, dict] = {}
    sources: list[tuple[str, list[dict]]] = []
    mf = _load_json(out / "merged_findings.json")
    if isinstance(mf, dict):
        sources.append(("merged_findings", mf.get("findings", [])))
    cf = _load_json(out / "triage" / "confirmed_findings.json")
    if isinstance(cf, dict):
        sources.append(("confirmed_findings", cf.get("findings", cf.get("confirmed", []))))
    elif isinstance(cf, list):
        sources.append(("confirmed_findings", cf))
    pq = _load_json(out / "poc_queue.json")
    if isinstance(pq, dict):
        sources.append(("poc_queue", pq.get("findings", pq.get("queue", []))))
    elif isinstance(pq, list):
        sources.append(("poc_queue", pq))
    ef = _load_json(out / "eval_ready" / "eval_findings.json")
    if isinstance(ef, dict):
        sources.append(("eval", ef.get("eval_findings", [])))

    inventory = []
    for source, recs in sources:
        for rec in recs or []:
            fid = _fid(rec)
            if not fid or fid in seen:
                continue
            required = _poc_required(rec, source)
            vs = (validated.get(fid) or {}).get("validation_status")
            if source == "eval" or not required:
                status = "not_required_eval_only"
            elif vs == "proven":
                status = "validated"
            elif vs in ("invalid_poc", "setup_only", "failed"):
                status = "invalid"
            elif vs in ("partially_proven", "duplicate_proof") or fid in poc_done:
                # a real PoC artifact exists but is not yet a clean proof
                status = "poc_exists_unvalidated"
            else:
                # inconclusive validation means no usable PoC artifact yet
                status = "missing_poc"
            entry = {
                "finding_id": fid,
                "title": rec.get("title", ""),
                "severity_ceiling": _severity(rec),
                "source": source,
                "manifest_refs": rec.get("manifest_refs", []),
                "affected_functions": _affected_functions(rec),
                "affected_files": _affected_files(rec),
                "poc_required": required,
                "required_proof_type": _required_proof_type(rec) if required else "static_proof",
                "minimum_proof_goal": (
                    "Prove root cause + unprivileged reachability + state transition + claimed impact at "
                    f"{_severity(rec)} ceiling" if required else "Eval recall only — no PoC required"),
                "suggested_test_strategy": (
                    "fork mainnet at a disclosed block, call the real public entrypoint as an unprivileged EOA, "
                    "assert before/after state" if _required_proof_type(rec) == "fork"
                    else "unit test calling the real function via a public entrypoint with before/after assertions"),
                "required_attacker_entrypoint": _attacker_entrypoint(rec),
                "required_impact_assertion": _impact_assertion(rec),
                "duplicate_candidates": [d for d in [rec.get("duplicate_of")] if d],
                "status": status,
            }
            seen[fid] = entry
            inventory.append(entry)

    required_n = sum(1 for e in inventory if e["poc_required"])
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total": len(inventory),
        "poc_required": required_n,
        "by_status": {s: sum(1 for e in inventory if e["status"] == s)
                      for s in ("missing_poc", "poc_exists_unvalidated", "validated", "invalid", "not_required_eval_only")},
        "candidates": inventory,
    }
    dest = out / "poc_validation" / "poc_inventory.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, indent=2))

    if not args.quiet:
        print(f"PoC inventory: {len(inventory)} candidates · {required_n} require a PoC")
        for s, n in report["by_status"].items():
            if n:
                print(f"  {s}: {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
