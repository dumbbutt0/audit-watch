#!/usr/bin/env python3
"""P283 — bounded cross-function value-flow tracer (RESEARCH-ONLY, ADVISORY, UN-WIRED).

V2 repair: the value-flow VIOLATION for accounting/math/oracle/reward candidates usually lives across a function
boundary (wrapper->internal, public->library). This tracer follows RESOLVABLE callee edges from a candidate's body up
to a bounded depth, runs the (comment-stripped) value-flow/anomaly detectors on each callee body, and reports a
trace_status + value_flow_path. It NEVER traces external/dynamic dispatch (fail-closed), and it does NOT conclude a bug
— it assembles cross-function evidence so the gate can decide. No award text, no target constants.

Importable: trace(candidate_item, manifest_index, audit_id) -> trace_evidence dict.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CFG = json.loads((ROOT / "config/research_cross_function_value_tracer.json").read_text())
sys.path.insert(0, str(Path(__file__).resolve().parent))
import source_span_guard_extractor as _ssx  # noqa: E402

MAX_DEPTH = int(CFG["max_depth"])
MAX_CALLEES = int(CFG["max_callees_per_function"])
MAX_SPANS = int(CFG["max_total_spans_per_candidate"])
SKIP = set(CFG["call_skip_names"])
_CALL = re.compile(r"([A-Za-z_]\w*)\s*\(")
# external/dynamic dispatch: `Something(addr).fn(` or `IFoo(x).bar(` — a member call on a casted/external object
_EXTERNAL_CALL = re.compile(r"\)\s*\.\s*[A-Za-z_]\w*\s*\(|\b[A-Z]\w*\([^)]*\)\s*\.")


def _callee_names(body: str) -> list[str]:
    body = _ssx.strip_comments(body)
    names = [n for n in dict.fromkeys(_CALL.findall(body)) if n not in SKIP]
    return names[:MAX_CALLEES]


def _has_external_dynamic(body: str) -> bool:
    return bool(_EXTERNAL_CALL.search(_ssx.strip_comments(body)))


def _resolve(name: str, contract: str, index: dict) -> dict | None:
    """Resolve a callee by name: prefer same-contract, else a UNIQUE match (library/inherited). Ambiguous -> None."""
    cands = index.get(name, [])
    same = [i for i in cands if contract and contract == (i.get("contract") or "")]
    if same:
        return same[0]
    if len(cands) == 1:
        return cands[0]
    return None  # ambiguous (multiple) or absent -> unresolved (fail-closed)


def _body(item: dict, audit_id):
    bd = _ssx.extract_body(item, audit_id)
    return bd.get("body") if bd.get("body_available") and not bd.get("is_declaration_only") else None


def trace(item: dict, index: dict, audit_id=None) -> dict:
    """Trace value-flow across bounded callee edges from `item`. Returns trace_evidence."""
    root_body = _body(item, audit_id)
    if root_body is None:
        return {"trace_status": "TRACE_UNRESOLVED", "reason": "root body unavailable", "trace_path": [],
                "value_flow_path": None, "value_flow_confidence": "LOW", "spans_visited": 0}
    contract = item.get("contract") or ""
    visited = 0
    path = []
    found_anomaly = None
    found_valueflow = None
    too_dynamic = False
    unresolved = []
    frontier = [(item, root_body, 0)]
    seen = {f"{contract}.{item.get('name')}"}
    while frontier and visited < MAX_SPANS:
        cur_item, cur_body, depth = frontier.pop(0)
        if depth >= MAX_DEPTH:
            continue
        cur_contract = cur_item.get("contract") or ""
        if _has_external_dynamic(cur_body):
            too_dynamic = True
        for name in _callee_names(cur_body):
            callee = _resolve(name, cur_contract, index)
            if not callee:
                unresolved.append(name)
                continue
            key = f"{callee.get('contract')}.{callee.get('name')}"
            if key in seen:
                continue
            seen.add(key)
            cbody = _body(callee, audit_id)
            if cbody is None:
                unresolved.append(name)
                continue
            visited += 1
            det = _ssx.detect(cbody)  # comment-stripped inside detect()
            edge = {"caller": f"{cur_contract}.{cur_item.get('name')}", "callee": key,
                    "edge": "same_contract" if callee.get("contract") == cur_contract else "library_or_inherited",
                    "source_span": det.get("source_span"),
                    "callee_state_write": det.get("state_write"), "callee_asset_move": det.get("asset_move"),
                    "callee_value_anomaly_div_before_mul": det.get("value_anomaly_div_before_mul")}
            path.append(edge)
            if det.get("value_anomaly_div_before_mul") and not found_anomaly:
                found_anomaly = edge
            if (det.get("state_write") or det.get("asset_move")) and det.get("value_flow_detected") and not found_valueflow:
                found_valueflow = edge
            frontier.append((callee, cbody, depth + 1))
            if visited >= MAX_SPANS:
                break

    if found_anomaly:
        status, conf = "TRACE_FOUND", "MEDIUM"
        vfp = {"attacker_input": "candidate entry (external/internal)",
               "callee_value_anomaly": found_anomaly["callee"],
               "affected": "value computation in callee", "anomaly": "division-before-multiplication (cross-function)",
               "invariant": "value conservation / correct rounding", "poc_assertion":
               f"assert the cross-function value path through {found_anomaly['callee']} mis-rounds/strands value"}
    elif found_valueflow:
        status, conf = "TRACE_FOUND", "LOW"   # value-flow reached cross-function, but NO concrete anomaly -> not liftable
        vfp = {"attacker_input": "candidate entry", "callee_value_movement": found_valueflow["callee"],
               "affected": "state write / asset move in callee", "anomaly": None,
               "invariant": "generic (needs corrected-reference)", "poc_assertion": None}
    elif too_dynamic:
        status, conf, vfp = "TRACE_TOO_DYNAMIC", "LOW", None
    elif path:
        status, conf, vfp = "TRACE_PARTIAL", "LOW", None
    else:
        status, conf, vfp = "TRACE_UNRESOLVED", "LOW", None

    return {"trace_status": status, "trace_path": path, "value_flow_path": vfp, "value_flow_confidence": conf,
            "spans_visited": visited, "unresolved_callees": sorted(set(unresolved))[:8],
            "too_dynamic_seen": too_dynamic,
            "source_basis": f"bounded trace depth<={MAX_DEPTH} from {contract}.{item.get('name')}",
            "unresolved_assumptions": ([] if found_anomaly else
                                       ["cross-function value-flow reached but no source-detectable anomaly; the "
                                        "violation needs corrected-reference/data-flow reasoning (CORE)"])}


def build_index(manifest: dict) -> dict:
    idx = {}
    for i in manifest.get("items", []):
        if i.get("kind") == "function":
            idx.setdefault(i.get("name"), []).append(i)
    return idx


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--contract-function", required=True)
    ap.add_argument("--audit-id")
    a = ap.parse_args()
    man = json.loads(Path(a.manifest).read_text())
    idx = build_index(man)
    c, _, fn = a.contract_function.partition(".")
    item = next((i for i in man.get("items", []) if i.get("kind") == "function" and i.get("name") == fn
                 and c in (i.get("contract") or "")), None)
    print(json.dumps(trace(item or {}, idx, a.audit_id), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
