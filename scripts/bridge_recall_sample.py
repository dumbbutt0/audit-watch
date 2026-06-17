#!/usr/bin/env python3
"""bridge_recall_sample.py — Phase-21 RESEARCH-ONLY sampler-recall overlay (un-wired, no gate, no routing).

Closes the Phase-20 Decent gap: score-5 cross-chain callback entrypoints (UTB.receiveFromBridge,
StargateBridgeAdapter.sgReceive) were never queued because no production semantic_surface_patterns.json
name_regex carried bridge-callback vocabulary. This script does NOT modify or import the FROZEN
deep_pass_prepare.py / semantic_surface_patterns.json. It reads the coverage manifest + the FROZEN base
candidate_queue.json (the OLD arm) + config/semantic_surface_patterns_bridge_recall.json, and emits a
BRIDGE_RECALL queue = base UNION bridge-callback candidates, each carrying source-grounded reason codes.

TWO-SIGNAL gate (single-signal matches are REFUSED — see --self-test):
  name_signal     : strong callback name | generic verb (needs strong context) | structural (receiver/adapter
                    + payload/src-chain param, name unknown)
  context_signal  : external/public visibility (required) + >=1 of {payload/message/src-chain param,
                    protocol/bridge context term, receiver/adapter interface name}
Generic verbs (handle/execute/dispatch/finalize/redeem/process/bridge/send/...) qualify ONLY with STRONG
context (param signal AND a protocol/interface signal). The category generalizes by STRUCTURE, not names.

  is_gate:false  research_only:true  routes_in_production:false  routed_manifest_ids:[]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
from sibling_function_parity_audit import _function_body  # noqa: E402
from bridge_terms import PRIMARY_BRIDGE_TERMS  # noqa: E402  (FP-tuned cross-chain context vocab, reused)

ROOT = Path(__file__).resolve().parent.parent
CFG = ROOT / "config" / "semantic_surface_patterns_bridge_recall.json"
FLAGS = {"is_gate": False, "research_only": True, "routes_in_production": False, "routed_manifest_ids": []}
_AUTH_RE = re.compile(r"require\s*\(\s*msg\.sender|if\s*\(\s*msg\.sender|onlyOwner|onlyRole|onlyExecutor|onlyUtb", re.I)


def _load(p: Path):
    try:
        return json.loads(Path(p).read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _cfg():
    c = _load(CFG)
    return {
        "strong": re.compile(c.get("callback_names_strong", "$^"), re.I),
        "generic": re.compile(r"\b(" + c.get("callback_names_generic", "$^") + r")\b", re.I),
        "param": re.compile(c.get("param_context_regex", "$^"), re.I),
        "iface": re.compile(c.get("interface_name_regex", "$^"), re.I),
        "proto": [t.lower() for t in c.get("protocol_terms", [])],
        "vis": set(c.get("entrypoint_visibility", ["external", "public"])),
        "must": bool(c.get("must_include_for_scheduler", True)),
    }


def _evaluate(it, cfg, body):
    """Return (included, record) where record holds the two signals separately + evidence + reason codes."""
    name = (it.get("name") or "")
    nlow = name.lower()
    sig = (it.get("signature") or "")
    contract = (it.get("contract") or "")
    vis = it.get("visibility")
    blob = f"{contract} {sig} {body or ''}".lower()

    # ---- name signal (callback/name) ----
    name_kind, name_ev = None, None
    if cfg["strong"].search(nlow):
        name_kind, name_ev = "strong", f"name '{name}' matches a known cross-chain callback"
    elif cfg["generic"].search(nlow):
        name_kind, name_ev = "generic", f"name '{name}' is a generic bridge verb (needs strong context)"

    # ---- context signal (trust boundary) ----
    ctx_param = bool(cfg["param"].search(sig)) or bool(cfg["param"].search(body or ""))
    ctx_proto = next((t for t in cfg["proto"] if t in blob), None)
    ctx_prim = next((t for t in PRIMARY_BRIDGE_TERMS if t in blob), None)
    ctx_iface = bool(cfg["iface"].search(contract.lower()))
    vis_ok = vis in cfg["vis"]
    ctx_sub = []
    if ctx_param: ctx_sub.append("payload/src-chain param")
    if ctx_proto: ctx_sub.append(f"protocol term '{ctx_proto}'")
    if ctx_prim and not ctx_proto: ctx_sub.append(f"bridge term '{ctx_prim}'")
    if ctx_iface: ctx_sub.append(f"receiver/adapter contract '{contract}'")
    strong_ctx = ctx_param and (ctx_proto or ctx_iface or ("override" in sig.lower()))

    # ---- structural generalization (unknown name) ----
    structural = (name_kind is None) and vis_ok and ctx_param and (ctx_iface or ctx_proto or "override" in sig.lower())
    if structural:
        name_kind, name_ev = "structural", f"unknown name '{name}' but receiver/adapter structure + payload param"

    # A real callback EXECUTES — view/pure getters (e.g. getBridgeToken) are not trust-boundary entrypoints.
    # Strong explicit callback names are exempt; generic/structural matches must be state-changing/payable.
    mut = (it.get("mutability") or "").lower()
    if name_kind in ("generic", "structural") and mut in ("view", "pure"):
        return False, {"manifest_id": it.get("id"), "contract": contract, "function": name,
                       "name_signal": {"kind": None, "evidence": f"{name_kind} match dropped: {mut} getter, not an entrypoint"},
                       "context_signal": {"visibility_ok": vis_ok, "sub_signals": [], "strong": False}}

    # ---- two-signal inclusion ----
    has_name = name_kind in ("strong", "structural") or (name_kind == "generic")
    has_ctx = vis_ok and bool(ctx_sub)
    if name_kind == "generic":
        include = vis_ok and strong_ctx        # generic verbs require STRONG context
    else:
        include = bool(name_kind) and vis_ok and bool(ctx_sub)
    include = include and (name_kind is not None) and has_ctx

    etype = ("bridge_receive_callback" if name_kind == "strong" and re.search(r"receive|lzreceive|sgreceive|ccipreceive|xreceive|wormhole", nlow)
             else "bridge_message_handler" if re.search(r"handle|process|execute|message|deliver|relay", nlow)
             else "bridge_finalize" if re.search(r"finalize|complete", nlow)
             else "bridge_dispatch" if re.search(r"bridge|send|dispatch", nlow)
             else "bridge_structural")
    auth = it.get("modifiers") or []
    auth_in_body = bool(_AUTH_RE.search(body or ""))

    rec = {
        "manifest_id": it.get("id"), "contract": contract, "function": name,
        "score": it.get("attack_surface_score", 0),
        "name_signal": {"kind": name_kind, "evidence": name_ev},
        "context_signal": {"visibility_ok": vis_ok, "sub_signals": ctx_sub, "strong": strong_ctx},
        "surface_reason": "external_bridge_callback",
        "trust_boundary": "cross_chain_message_sender",
        "entrypoint_type": etype,
        "must_include_for_scheduler": cfg["must"],
        "evidence": {"signature": sig.strip(), "visibility": vis, "modifiers": auth,
                     "nearby_authorization": (auth or (["msg.sender check"] if auth_in_body else []))},
        "selected_by": [f"bridge_recall:{etype}"],
    }
    return include, rec


def run(audit_out: Path, subject_dir: Path, quiet=False):
    cfg = _cfg()
    items = _load(audit_out / "coverage_manifest.json").get("items", [])
    base = _load(audit_out / "deep_pass" / "candidate_queue.json")
    base_q = base.get("queue", [])
    base_ids = {c.get("manifest_id") for c in base_q}
    use_source = True

    added, rejected_single = [], 0
    seen = set()
    # Skip interface DECLARATIONS (no implementation): the `IFoo` convention AND Centrifuge's `FooLike` /
    # `FooInterface` convention. Bridge bugs live in concrete implementations, not interface decls.
    _iface_re = re.compile(r"(^I[A-Z][a-zA-Z])|(Like$)|(Interface$)")
    for it in items:
        if it.get("kind") not in ("function", "initializer") or not it.get("in_scope", True):
            continue
        if _iface_re.search(it.get("contract") or ""):
            continue
        mid = it.get("id")
        if mid in seen:
            continue
        sp = it.get("source_span", {})
        body = _function_body(it.get("file", ""), sp.get("start_line"), use_source)
        inc, rec = _evaluate(it, cfg, body)
        # track single-signal near-misses for the noise/precision report
        ns = rec["name_signal"]["kind"] is not None
        cs = bool(rec["context_signal"]["sub_signals"]) and rec["context_signal"]["visibility_ok"]
        if (ns ^ cs) and (ns or cs):
            rejected_single += 1
        if inc and mid not in base_ids:
            seen.add(mid)
            added.append(rec)

    # must-include bridge candidates FIRST (score desc) so a budgeted scheduler reaches them, then base
    added.sort(key=lambda r: -r.get("score", 0))
    bridge_q = [dict(manifest_id=r["manifest_id"], contract=r["contract"], function=r["function"],
                     score=r["score"], selected_by=r["selected_by"], bridge_recall=r) for r in added]
    merged = bridge_q + base_q

    out = audit_out / "deep_pass" / "candidate_queue_bridge_recall.json"
    out.write_text(json.dumps({"mode": "bridge_recall", **FLAGS,
                               "base_queue_size": len(base_q), "added_bridge_candidates": len(added),
                               "queue_size": len(merged), "queue": merged}, indent=2))
    subject_dir.mkdir(parents=True, exist_ok=True)
    (subject_dir / "bridge_recall_added.json").write_text(json.dumps(
        {**FLAGS, "added": added, "single_signal_rejected": rejected_single}, indent=2))

    if not quiet:
        print(f"[bridge_recall] base {len(base_q)} + {len(added)} bridge = {len(merged)}  "
              f"(single-signal refused: {rejected_single})")
        for i, r in enumerate(added, 1):
            ns, cs = r["name_signal"], r["context_signal"]
            print(f"  #{i} {r['contract']}.{r['function']}  [{r['entrypoint_type']}]")
            print(f"      name_signal   : {ns['kind']} — {ns['evidence']}")
            print(f"      context_signal: vis_ok={cs['visibility_ok']} strong={cs['strong']} :: {', '.join(cs['sub_signals'])}")
    return {"base": len(base_q), "added": len(added), "merged": len(merged), "rejected_single": rejected_single}


def _self_test():
    """Assert the two-signal gate REFUSES single-signal matches (guardrail 5)."""
    cfg = _cfg()
    cases = [
        # (item, body, expect_included, label)
        ({"name": "sgReceive", "contract": "StargateBridgeAdapter", "visibility": "external",
          "signature": "function sgReceive(uint16,bytes,uint256,address,uint256,bytes memory payload) external", "modifiers": ["onlyExecutor"]},
         "", True, "strong name + payload param + adapter contract"),
        ({"name": "receiveFromBridge", "contract": "UTB", "visibility": "public",
          "signature": "function receiveFromBridge(SwapInstructions memory postBridge,address target,address paymentOperator,bytes memory payload,address payable refund) public", "modifiers": []},
         "", True, "strong name + payload param"),
        ({"name": "totalSupply", "contract": "TwabERC20", "visibility": "public",
          "signature": "function totalSupply() public view returns(uint256)", "modifiers": []},
         "return x;", False, "no name, no context — must refuse"),
        ({"name": "handle", "contract": "Vault", "visibility": "external",
          "signature": "function handle(uint256 amount) external", "modifiers": []},
         "x=amount;", False, "generic name only, NO bridge context — must refuse"),
        ({"name": "collectFees", "contract": "UTBFeeCollector", "visibility": "public",
          "signature": "function collectFees(FeeStructure calldata fees,bytes memory packedInfo,bytes memory signature) public", "modifiers": ["onlyUtb"]},
         "", False, "context-ish (bytes) but NO callback name — single-signal, must refuse"),
        ({"name": "process", "contract": "AxelarGateway", "visibility": "external",
          "signature": "function process(bytes calldata payload, string calldata sourceChain) external", "modifiers": []},
         "", True, "generic name + STRONG context (payload param + gateway/axelar) — admit by structure"),
    ]
    ok = True
    for it, body, expect, label in cases:
        inc, _ = _evaluate(it, cfg, body)
        status = "PASS" if inc == expect else "FAIL"
        if inc != expect:
            ok = False
        print(f"  [{status}] include={inc} expect={expect} :: {label}")
    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit-out", help="audits/<id>/output (default: active audit)")
    ap.add_argument("--subject-dir", help="documentation/evals/sampler_recall/<subject>")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    ao = Path(args.audit_out) if args.audit_out else audit_path("output")
    sd = Path(args.subject_dir) if args.subject_dir else (ROOT / "documentation/evals/sampler_recall/_adhoc")
    run(ao, sd, quiet=args.quiet)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
