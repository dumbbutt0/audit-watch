#!/usr/bin/env python3
"""value_state_recall_sample.py — Phase-30 RESEARCH-ONLY value/state candidate-recall overlay (un-wired).

Closes the P28 Badger gap: the awarded post-op comparison bug (LeverageMacroBase._doCheckValueType, internal) was
never queued. Mirrors the P21 bridge-recall sampler but for vault/CDP/liquidation/accounting/post-op surfaces, with
TWO key differences: (a) NO external/public visibility gate — value/state bugs are frequently internal/library/view
math; (b) internal/private functions carry a caller_context hint. CANDIDATE-RECALL ONLY: it adds candidates to the
queue; it does NOT reason, run validity/impact, or claim recovery. Does not modify the frozen base queue.

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

ROOT = Path(__file__).resolve().parent.parent
CFG = ROOT / "config" / "value_state_surface_patterns.json"
FLAGS = {"is_gate": False, "research_only": True, "routes_in_production": False, "routed_manifest_ids": []}


def _load(p):
    try:
        return json.loads(Path(p).read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _cfg():
    c = _load(CFG)
    return {
        "strong": re.compile(c.get("names_strong", "$^"), re.I),
        "generic": re.compile(r"\b(" + c.get("names_generic", "$^") + r")\b", re.I),
        "ctx_terms": [t.lower() for t in c.get("context_terms", [])],
        "value_param": re.compile(c.get("value_param_regex", "$^"), re.I),
        "cdp_vault": re.compile(c.get("cdp_vault_contract_regex", "$^"), re.I),
        "iface": re.compile(c.get("interface_contract_regex", "$^")),
        "erc20": re.compile(c.get("erc20_wrapper_names", "$^"), re.I),
        "class_map": {k: re.compile(v, re.I) for k, v in c.get("class_map", {}).items()},
        "cap": int(c.get("per_class_cap", 14)),
        "budget_pct": float(c.get("global_budget_pct", 0.35)),
        "budget_abs": int(c.get("global_budget_abs", 40)),
        "class_share_cap": float(c.get("class_share_cap", 0.40)),
        "w": c.get("score_weights", {}),
        "must": bool(c.get("must_include_for_scheduler", True)),
    }


def _classify(nlow, blob, cfg):
    for cls, rx in cfg["class_map"].items():
        if rx.search(nlow) or rx.search(blob):
            return cls
    return "accounting_delta"


def _caller_hint(fn, def_file, src_files):
    """Find a reachable caller / call-chain hint for an internal/private fn (first usage outside its own file)."""
    pat = re.compile(r"[.\s(]" + re.escape(fn) + r"\s*\(")
    for f, text in src_files.items():
        for i, line in enumerate(text, 1):
            if pat.search(line) and not re.search(r"function\s+" + re.escape(fn) + r"\b", line):
                if f != def_file or True:  # any call site (same or other file) is a hint
                    return f"{Path(f).name}:{i}"
    return None


def _evaluate(it, cfg, body, src_files):
    name = it.get("name") or ""
    nlow = name.lower()
    sig = it.get("signature") or ""
    contract = it.get("contract") or ""
    vis = (it.get("visibility") or "").lower()
    mut = (it.get("mutability") or "").lower()
    blob = f"{contract} {sig} {body or ''}".lower()

    if cfg["iface"].search(contract):  # interface declaration -> refuse
        return False, {"reason": "interface declaration"}

    # context sub-signals
    ctx_param = bool(cfg["value_param"].search(sig)) or bool(cfg["value_param"].search(body or ""))
    ctx_term = next((t for t in cfg["ctx_terms"] if t in blob), None)
    ctx_contract = bool(cfg["cdp_vault"].search(contract))
    sub = []
    if ctx_param: sub.append("value/comparison param")
    if ctx_term: sub.append(f"context term '{ctx_term}'")
    if ctx_contract: sub.append(f"cdp/vault contract '{contract}'")
    n_ctx = len(sub)

    # name signal
    if cfg["strong"].search(nlow):
        name_kind = "strong"
    elif cfg["generic"].search(nlow):
        name_kind = "generic"
    elif ctx_contract and ctx_param:
        name_kind = "structural"
    else:
        name_kind = None

    # noise: plain ERC20 transfer/approve wrapper unless accounting/liquidation context
    if cfg["erc20"].search(nlow) and not (ctx_term or ctx_param):
        return False, {"reason": f"plain ERC20 wrapper '{name}' without accounting/liquidation context"}
    # noise: pure/view getter with no value-comparison evidence and no strong name -> refuse
    if mut in ("view", "pure") and not ctx_param and name_kind != "strong":
        return False, {"reason": f"{mut} getter without value/comparison evidence"}

    if name_kind is None:
        return False, {"reason": "no value/state name or structural signal"}
    # generic verbs need >=2 strong context sub-signals
    if name_kind == "generic" and n_ctx < 2:
        return False, {"reason": f"generic name '{name}' with <2 context signals ({sub})"}
    if n_ctx == 0:
        return False, {"reason": "no context signal"}

    vcls = _classify(nlow, blob, cfg)
    caller_context = None
    if vis in ("internal", "private"):
        caller_context = _caller_hint(name, it.get("file", ""), src_files) or "unknown (no static caller found)"

    rec = {
        "manifest_id": it.get("id"), "contract": contract, "function": name,
        "score": it.get("attack_surface_score", 0), "visibility": vis,
        "name_signal": {"kind": name_kind, "evidence": f"name '{name}' ({name_kind})"},
        "context_signal": {"sub_signals": sub, "count": n_ctx},
        "value_state_class": vcls,
        "surface_reason": "value_state_surface",
        "evidence_span": (sig.strip() or f"{contract}.{name}")[:200],
        "caller_context": caller_context,
        "must_include_for_scheduler": cfg["must"],
        "selected_by": [f"value_state_recall:{vcls}"],
    }
    return True, rec


def _caller_known(r):
    cc = r.get("caller_context")
    return bool(cc) and not str(cc).startswith("unknown")


def _post_op_term(rec):
    blob = (str(rec.get("evidence_span", "")) + " " + str(rec.get("function", ""))).lower()
    return any(t in blob for t in ("valuetocheck", "<=", ">=", "requirevalid", "post check",
                                   "collateral", "debt", "health", "icr"))


def value_state_score(rec, w):
    """Rank score (P30.1): boosts the post-op/comparison/valueToCheck shape + reachable internal helpers above
    generic high-attack-surface functions, so a low-attack-surface awarded check (e.g. _doCheckValueType, raw
    attack_surface=0) survives the global budget."""
    s = w.get("attack_surface_weight", 0.5) * rec.get("score", 0)
    cls = rec.get("value_state_class")
    sub = rec.get("context_signal", {}).get("sub_signals", [])
    has_param = any("param" in x for x in sub)
    if cls in ("comparison_check", "post_op_check") and has_param:
        s += w.get("post_op_comparison_with_param", 6)
    elif cls in ("comparison_check", "post_op_check"):
        s += w.get("post_op_or_comparison_class", 3)
    if cls == "liquidation":
        s += w.get("liquidation_class", 3)
    if _post_op_term(rec):
        s += w.get("post_op_term_bonus", 2)
    if (rec.get("visibility") or "") in ("internal", "private"):
        s += w.get("internal_with_caller", 2) if _caller_known(rec) else w.get("internal_isolated_penalty", -1)
    if rec.get("context_signal", {}).get("count", 0) >= 2:
        s += w.get("two_context_bonus", 1)
    if rec.get("name_signal", {}).get("kind") == "generic":
        s += w.get("generic_name_penalty", -2)
    return s


def run(audit_out: Path, subject_dir: Path, quiet=False):
    cfg = _cfg()
    items = _load(audit_out / "coverage_manifest.json").get("items", [])
    base = _load(audit_out / "deep_pass" / "candidate_queue.json").get("queue", [])
    base_ids = {c.get("manifest_id") for c in base}
    # source text cache for caller hints
    src_files = {}
    cdir = audit_out.parent / "contracts"
    for f in cdir.rglob("*.sol"):
        try:
            src_files[str(f)] = f.read_text(errors="replace").splitlines()
        except OSError:
            pass

    # ADMISSION: every fn passing the two-signal gate (NO per-class cap here — that is a SELECTION concern).
    admitted, refused = [], 0
    seen = set()
    for it in items:
        if it.get("kind") not in ("function", "initializer") or not it.get("in_scope", True):
            continue
        mid = it.get("id")
        if mid in seen or mid in base_ids:
            continue
        sp = it.get("source_span", {})
        body = _function_body(it.get("file", ""), sp.get("start_line"), True)
        inc, rec = _evaluate(it, cfg, body, src_files)
        if not inc:
            refused += 1
            continue
        rec["value_state_score"] = round(value_state_score(rec, cfg["w"]), 3)
        seen.add(mid)
        admitted.append(rec)

    # RANK (deterministic tie-breaker) -> rank_before
    admitted.sort(key=lambda r: (-r["value_state_score"], -r.get("context_signal", {}).get("count", 0),
                                 0 if _caller_known(r) else 1, str(r.get("manifest_id", ""))))
    for i, r in enumerate(admitted, 1):
        r["rank_before"] = i

    # SELECT under global budget + per-class share cap (the growth control)
    K = min(cfg["budget_abs"], round(cfg["budget_pct"] * len(base)))
    C = max(2, round(cfg["class_share_cap"] * K))
    selected, cut = [], []
    sel_by_class, cut_by_class = {}, {}
    for r in admitted:
        cls = r["value_state_class"]
        if len(selected) < K and sel_by_class.get(cls, 0) < C:
            sel_by_class[cls] = sel_by_class.get(cls, 0) + 1
            r["selected"] = True
            selected.append(r)
        else:
            cut_by_class[cls] = cut_by_class.get(cls, 0) + 1
            r["selected"] = False
            cut.append(r)
    for i, r in enumerate(selected, 1):
        r["rank_after"] = i

    vs_q = [dict(manifest_id=r["manifest_id"], contract=r["contract"], function=r["function"],
                 score=r["score"], value_state_score=r["value_state_score"], selected_by=r["selected_by"],
                 value_state_recall=r) for r in selected]
    merged = vs_q + base

    out = audit_out / "deep_pass" / "candidate_queue_value_state.json"
    out.write_text(json.dumps({"mode": "value_state_recall", **FLAGS, "base_queue_size": len(base),
                               "admitted_count": len(admitted), "selected_count": len(selected),
                               "cut_count": len(cut), "budget_K": K, "class_share_cap_C": C,
                               "added_value_state": len(selected), "queue_size": len(merged),
                               "selected_by_class": sel_by_class, "cut_by_class": cut_by_class,
                               "queue": merged}, indent=2))
    subject_dir.mkdir(parents=True, exist_ok=True)
    (subject_dir / "value_state_added.json").write_text(json.dumps(
        {**FLAGS, "admitted_count": len(admitted), "selected_count": len(selected), "cut_count": len(cut),
         "budget_K": K, "class_share_cap_C": C, "selected_by_class": sel_by_class, "cut_by_class": cut_by_class,
         "admitted": admitted, "selected": selected, "cut": cut, "added": selected, "refused": refused},
        indent=2))
    by_class = sel_by_class
    if not quiet:
        print(f"[value_state_recall] base {len(base)} · admitted {len(admitted)} · selected {len(selected)} "
              f"(budget K={K}, class_cap C={C}) · refused {refused} · selected_by_class {sel_by_class}")
        for r in selected[:20]:
            print(f"   {r['contract']}.{r['function']} [{r['value_state_class']}] vs_score={r['value_state_score']} "
                  f"vis={r['visibility']} ctx={r['context_signal']['count']}" + (f" caller={r['caller_context']}" if r['caller_context'] else ""))
    return {"base": len(base), "admitted": len(admitted), "selected": len(selected), "refused": refused, "by_class": by_class}


def _self_test():
    cfg = _cfg()
    sf = {}
    cases = [
        ("internal comparison-check admitted", {"name": "_doCheckValueType", "contract": "LeverageMacroBase",
            "visibility": "internal", "mutability": "nonpayable",
            "signature": "function _doCheckValueType(CheckValueAndType memory check, uint256 valueToCheck) internal"}, True),
        ("liquidation admitted", {"name": "liquidate", "contract": "LiquidationLogic", "visibility": "external",
            "signature": "function liquidate(uint256 vaultId, uint256 closeRatio) external", "mutability": "nonpayable"}, True),
        ("fee accrual admitted", {"name": "claimYieldFeeShares", "contract": "PrizeVault", "visibility": "external",
            "signature": "function claimYieldFeeShares(uint256 _shares) external", "mutability": "nonpayable"}, True),
        ("generic 'check' no context refused", {"name": "check", "contract": "Helper", "visibility": "public",
            "signature": "function check(uint256 x) public", "mutability": "pure"}, False),
        ("pure getter no value refused", {"name": "totalSupply", "contract": "TwabERC20", "visibility": "public",
            "signature": "function totalSupply() public view returns(uint256)", "mutability": "view"}, False),
        ("ERC20 transfer wrapper refused", {"name": "transfer", "contract": "Token", "visibility": "public",
            "signature": "function transfer(address to, uint256 amt) public", "mutability": "nonpayable"}, False),
        ("interface decl refused", {"name": "liquidate", "contract": "ILiquidationLogic", "visibility": "external",
            "signature": "function liquidate(uint256 id) external", "mutability": "nonpayable"}, False),
        ("conversion view WITH muldiv admitted", {"name": "convertToShares", "contract": "PrizeVault",
            "visibility": "public", "mutability": "view",
            "signature": "function convertToShares(uint256 a) public view returns(uint256)"}, True),
    ]
    ok = True
    for label, it, exp in cases:
        body = "valueToCheck >= check.value" if "Check" in it["name"] else ("mulDiv(a, totalDebt, x)" if "convert" in it["name"] else "")
        inc, rec = _evaluate(it, cfg, body, sf)
        good = inc == exp
        ok &= good
        print(f"  [{'PASS' if good else 'FAIL'}] {label}: include={inc}" + (f" class={rec.get('value_state_class')}" if inc else f" ({rec.get('reason')})"))
    # generic with >=2 ctx admitted
    inc, rec = _evaluate({"name": "update", "contract": "CdpManager", "visibility": "external",
                          "signature": "function update(uint256 debt, uint256 collateral) external", "mutability": "nonpayable"},
                         cfg, "debt collateral icr", sf)
    g = inc is True and rec.get("context_signal", {}).get("count", 0) >= 2
    print(f"  [{'PASS' if g else 'FAIL'}] generic 'update' with >=2 context admitted (ctx={rec.get('context_signal',{}).get('count') if inc else 'n/a'})")
    ok &= g
    # ranking: a low-attack-surface internal comparison_check (raw 0, valueToCheck, caller known) must score ABOVE
    # a generic high-attack-surface accounting fn (raw 5) — so the budget keeps the awarded check, not the generic.
    w = cfg["w"]
    chk_rec = {"score": 0, "visibility": "internal", "value_state_class": "comparison_check",
               "caller_context": "X.sol:10", "evidence_span": "function _doCheckValueType(... uint256 valueToCheck)",
               "function": "_doCheckValueType", "context_signal": {"sub_signals": ["value/comparison param", "context term 'valuetocheck'"], "count": 2},
               "name_signal": {"kind": "strong"}}
    gen_rec = {"score": 5, "visibility": "public", "value_state_class": "accounting_delta",
               "caller_context": None, "evidence_span": "function update(uint256 x)", "function": "update",
               "context_signal": {"sub_signals": ["context term 'shares'"], "count": 1}, "name_signal": {"kind": "generic"}}
    rk = value_state_score(chk_rec, w) > value_state_score(gen_rec, w)
    print(f"  [{'PASS' if rk else 'FAIL'}] ranking: low-surface comparison_check ({value_state_score(chk_rec,w)}) > generic high-surface ({value_state_score(gen_rec,w)})")
    ok &= rk
    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit-out")
    ap.add_argument("--subject-dir")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    ao = Path(args.audit_out) if args.audit_out else audit_path("output")
    sd = Path(args.subject_dir) if args.subject_dir else (ROOT / "documentation/evals/value_state_recall/_adhoc")
    run(ao, sd, quiet=args.quiet)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
