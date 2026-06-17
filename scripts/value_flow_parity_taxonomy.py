#!/usr/bin/env python3
"""
value_flow_parity_taxonomy.py — pure (no-I/O) classifier for the VALUE-FLOW PARITY research lens.
Detects WRONG-VALUE parity: the check/accounting component is present but fed a different semantic
value/identity than its sibling/correct counterpart. Anchored on Size M-02 (validateSellCreditMarket
guards `params.amount < minimumCreditBorrowAToken` — a cash amount checked against a CREDIT-named
threshold; the derived creditAmount is what should be checked).

DISTINCT from asset_source_consistency (asset-source FAMILY transfer-source mismatch): this lens compares
curated IDENTIFIER ALIAS-PAIRS for check-vs-use / threshold-name mismatch.

Reuses cross_contract_sibling_parity_taxonomy (guard predicate regexes) and sibling_function_parity_taxonomy
(extract_features / strip_comments / _core / _is_wrapper).

RESEARCH-ONLY: read-only, is_gate:false, routes_in_production:false — never mints or routes.
High precision over recall (wrong-value is FP-prone; deliberately narrow).
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

import sibling_function_parity_taxonomy as sfp
import cross_contract_sibling_parity_taxonomy as ccs  # _REQUIRE_PRED/_IF_REVERT_PRED/_DOTTED/_IDENT

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "value_flow_parity_patterns.json"

_RETURN = re.compile(r"\breturn\s+([^;]+);")
_NETGROSS = re.compile(r"([A-Za-z_]\w*)\s*-\s*([A-Za-z_]\w*)")

# ---- v2 generalization shapes (Phase 13) ----
_FOR_IDX = re.compile(r"\bfor\s*\(\s*(?:u?int\d*\s+)?([A-Za-z_]\w*)\s*=")
# bare top-level array only (NOT a `.field[...]` access — avoids the 2D / shadowed-name FP)
_ARR_IDX = re.compile(r"(?<![.\w])([A-Za-z_]\w*)\s*\[\s*([A-Za-z_]\w*)\s*\]")
_MUTATING_VERBS = ("remove", "transfer", "burn", "mint", "deposit", "withdraw", "move", "send", "redeem")
_AUTH_HINTS = ("approved", "owner", "auth", "check", "require", "valid", "isowner")
_OWNER_RESOLVE = re.compile(
    r"\b(?:address\s+)?([A-Za-z_]\w*)\s*=\s*(?:[A-Za-z_][\w.]*\.)?(ownerOf|getOriginalOwner)\s*\(\s*([A-Za-z_]\w*)")
_MSGSENDER_CALL = re.compile(r"\b([A-Za-z_]\w*)\s*\(\s*msg\.sender\s*,\s*([A-Za-z_]\w*)")
_MAP_ADDR_KEY = re.compile(r"\b([A-Za-z_]\w*)\s*\[\s*address\s*\(\s*([A-Za-z_]\w*)\s*\)\s*\]")
_IDX_MINUS1 = re.compile(r"\[\s*([A-Za-z_]\w*)\s*-\s*1\s*\]")
_IDX_FIELD = re.compile(r"\[\s*([A-Za-z_]\w*)\s*\]\s*\.\s*[A-Za-z_]\w*")


def classify_v2_shapes(name: str, signature: str = "", snippet: str = "") -> list:
    """Phase-13 deterministic wrong-value sub-shapes (each independently 0-FP-gated on the anchor corpus).
    All emit at MEDIUM under a tight gate. None touches the v1 shapes (Size M-02 preserved)."""
    if not _t("enable_v2_shapes", True):
        return []
    body = sfp.strip_comments(snippet or "")
    cands = []

    def add(shape, fn_value, expect, evidence, sig, conf="medium"):
        cands.append({"shape": shape, "parity_type": "value_flow", "confidence": conf,
                      "guard_value": fn_value, "effect_value": expect, "evidence": evidence, "signals": sig})

    # 1) loop_index_anomaly: array indexed by an OUTER loop var inside an inner loop where the inner var dominates
    loopvars = _FOR_IDX.findall(body)
    if len(set(loopvars)) >= 2:
        lv = list(dict.fromkeys(loopvars))  # ordered, unique (outer..inner)
        idx_by_arr = {}
        for arr, idx in _ARR_IDX.findall(body):
            if idx in lv:
                idx_by_arr.setdefault(arr, []).append(idx)
        for arr, idxs in idx_by_arr.items():
            counts = {v: idxs.count(v) for v in set(idxs)}
            if len(counts) >= 2:
                dominant = max(counts, key=counts.get)
                for v, n in counts.items():
                    # an outer-loop var used exactly once where the inner var dominates ≥2x
                    if v != dominant and n == 1 and counts[dominant] >= 2 and lv.index(v) < lv.index(dominant):
                        add("loop_index_anomaly", f"{arr}[{v}]", f"{arr}[{dominant}]",
                            f"{name}: `{arr}[{v}]` uses the outer-loop index `{v}` inside the `{dominant}` "
                            f"loop where `{arr}[{dominant}]` is otherwise used — likely wrong index",
                            {"array": arr, "wrong_index": v, "expected": dominant})

    # 2) identity_resolution_then_misuse: canonical owner resolved into a local, but a STATE-MUTATING
    #    call passes msg.sender (NOT the resolved local). The callee must be a mutating op, not an auth
    #    guard like _isApprovedOrOwner(msg.sender, id) — that is a legitimate msg.sender use.
    for local, resolver, rid in _OWNER_RESOLVE.findall(body):
        for callee, cid in _MSGSENDER_CALL.findall(body):
            cl = callee.lower()
            is_mutating = any(v in cl for v in _MUTATING_VERBS) and not any(a in cl for a in _AUTH_HINTS)
            if cid == rid and is_mutating and local.lower() not in ("msg",):
                # the resolved owner local exists for this id but the call uses msg.sender instead
                add("identity_resolution_then_misuse", f"{callee}(msg.sender, {cid})",
                    f"{callee}({local}, {cid})",
                    f"{name}: resolves `{local} = {resolver}({rid})` but calls `{callee}(msg.sender, {cid})` "
                    f"— should pass the resolved `{local}`, not msg.sender",
                    {"resolved_local": local, "resolver": resolver, "callee": callee})

    # 3) mapping_key_inconsistency: same mapping keyed by both address(this) and address(<param>)
    params = set(re.findall(r"\b([A-Za-z_]\w*)\b(?=\s*[,)])", (signature or "").split("(", 1)[-1])) if signature else set()
    key_by_map = {}
    for mp, key in _MAP_ADDR_KEY.findall(body):
        key_by_map.setdefault(mp, set()).add(key)
    for mp, keys in key_by_map.items():
        if "this" in keys and (keys - {"this"}):
            other = sorted(keys - {"this"})[0]
            if (not params) or other in params or True:  # other is typically a param/local
                add("mapping_key_inconsistency", f"{mp}[address({other})]", f"{mp}[address(this)]",
                    f"{name}: mapping `{mp}` is keyed by both `address(this)` and `address({other})` — "
                    f"inconsistent key (one of them is wrong)",
                    {"mapping": mp, "keys": sorted(keys)})

    # 4) off_by_one_index: index used as [k-1] >=2x AND bare [k].field in the same body
    minus1 = [v for v in _IDX_MINUS1.findall(body)]
    fields = set(_IDX_FIELD.findall(body))
    for k in set(minus1):
        if minus1.count(k) >= 2 and k in fields:
            # LOW only: off-by-one is FP-prone (benign on beanstalk/quantamm anchor patterns) — not routable.
            add("off_by_one_index", f"[{k}].field", f"[{k}-1].field",
                f"{name}: index `{k}` is used as `[{k}-1]` elsewhere but read bare as `[{k}].field` — "
                f"possible off-by-one (low confidence — high FP shape)",
                {"index": k, "minus1_uses": minus1.count(k)}, conf="low")

    return cands


@lru_cache(maxsize=1)
def _cfg() -> dict:
    try:
        return json.loads(CONFIG.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def _t(key, default):
    return _cfg().get(key, default)


def _pred_tokens(pred: str) -> set:
    toks = set(t.lower() for t in ccs._DOTTED.findall(pred))
    toks |= set(t.lower() for t in ccs._IDENT.findall(pred))
    return toks - set(_t("exclude_idents", []))


def guard_predicates(snippet: str) -> list:
    body = sfp.strip_comments(snippet or "")
    return ccs._REQUIRE_PRED.findall(body) + ccs._IF_REVERT_PRED.findall(body)


def guard_idents(snippet: str) -> set:
    out = set()
    for p in guard_predicates(snippet):
        out |= _pred_tokens(p)
    return out


def effect_operands(snippet: str) -> set:
    """Identifiers used in value-moving effects: transfer-like calls + return statements."""
    body = sfp.strip_comments(snippet or "")
    out = set()
    tr = re.compile(_t("transfer_call_re", r"\.transfer\s*\(([^;]*?)\)"))
    for m in tr.finditer(body):
        out |= {t.lower() for t in ccs._DOTTED.findall(m.group(1))}
        out |= {t.lower() for t in ccs._IDENT.findall(m.group(1))}
    for m in _RETURN.finditer(body):
        out |= {t.lower() for t in ccs._DOTTED.findall(m.group(1))}
        out |= {t.lower() for t in ccs._IDENT.findall(m.group(1))}
    return out - set(_t("exclude_idents", []))


def _is_validator(name: str, snippet: str) -> bool:
    nl = (name or "").lower()
    if any(nl.startswith(v) for v in _t("validator_context_verbs", [])):
        return True
    # a function that only reverts (no transfer / no state write) is validator-like
    return bool(guard_predicates(snippet)) and not re.search(r"\.transfer|=\s*[^=]", sfp.strip_comments(snippet or ""))


def classify_intra(name: str, signature: str = "", snippet: str = "") -> list:
    """Shapes 1 (identity check-vs-use), 2 (threshold-name value mismatch), 3 (net/gross, low)."""
    cands = []
    gids = guard_idents(snippet)
    eops = effect_operands(snippet)
    body = sfp.strip_comments(snippet or "").lower()

    # ---- Shape 1: identity check-vs-use divergence (LOW only / experimental) ----
    # NOTE: deliberately LOW, never routable. Corpus eval showed the premise is weak — checking
    # msg.sender/owner while sending to recipient/receiver is the NORMAL transfer pattern (ERC20/4626),
    # not a bug, so this fires on benign transfers. Kept as research context behind a stronger signal.
    for pair in _t("identity_alias_pairs", []):
        A, B = [a.lower() for a in pair["a"]], [b.lower() for b in pair["b"]]
        a_g = any(a in gids for a in A); b_g = any(b in gids for b in B)
        a_e = any(a in eops for a in A); b_e = any(b in eops for b in B)
        if a_g and b_e and not b_g and not a_e:
            cands.append({"shape": "identity_check_vs_use", "parity_type": "recipient_parity",
                          "confidence": "low", "guard_value": next(a for a in A if a in gids),
                          "effect_value": next(b for b in B if b in eops),
                          "evidence": f"{name} guards/validates `{next(a for a in A if a in gids)}` but the "
                                      f"effect uses `{next(b for b in B if b in eops)}` (identity alias mismatch)",
                          "signals": {"guard_idents": sorted(gids)[:6], "effect_operands": sorted(eops)[:6]}})
        if b_g and a_e and not a_g and not b_e:
            cands.append({"shape": "identity_check_vs_use", "parity_type": "recipient_parity",
                          "confidence": "low", "guard_value": next(b for b in B if b in gids),
                          "effect_value": next(a for a in A if a in eops),
                          "evidence": f"{name} guards/validates `{next(b for b in B if b in gids)}` but the "
                                      f"effect uses `{next(a for a in A if a in eops)}` (identity alias mismatch)",
                          "signals": {"guard_idents": sorted(gids)[:6], "effect_operands": sorted(eops)[:6]}})

    # ---- Shape 2: threshold-name value mismatch (the M-02 anchor) ----
    if _is_validator(name, snippet):
        ops = _t("comparison_ops", [])
        thr = _t("threshold_idents", [])
        for pred in guard_predicates(snippet):
            if not any(o in pred for o in ops):
                continue
            toks = _pred_tokens(pred)
            for vp in _t("value_alias_pairs", []):
                raw, derived = [r.lower() for r in vp["raw"]], [d.lower() for d in vp["derived"]]
                dkw = [k.lower() for k in vp["derived_kw"]]
                has_raw = any(r in toks for r in raw)
                has_derived_member = any(d in toks for d in derived)
                named_derived = any(any(k in tok for k in dkw) for tok in toks)
                if has_raw and named_derived and not has_derived_member:
                    is_thr = any(th in pred.lower() for th in thr)
                    cands.append({"shape": "threshold_value_mismatch",
                                  "parity_type": "validation_parity",
                                  "confidence": "medium" if is_thr else "low",
                                  "guard_value": next(r for r in raw if r in toks),
                                  "effect_value": f"<{dkw[0]}-named bound>",
                                  "evidence": f"{name} compares raw value `{next(r for r in raw if r in toks)}` "
                                              f"against a `{dkw[0]}`-named bound — the derived "
                                              f"{dkw[0]} quantity is what should be checked",
                                  "signals": {"predicate": pred.strip()[:120]}})

    # ---- Shape 3: net/gross self-mismatch (LOW, experimental) ----
    fee_terms = _t("fee_terms", [])
    rets = {t.lower() for m in _RETURN.finditer(sfp.strip_comments(snippet or "")) for t in ccs._IDENT.findall(m.group(1))}
    for m in _NETGROSS.finditer(body):
        lhs, rhs = m.group(1), m.group(2)
        if lhs in rets and any(f in rhs for f in fee_terms):
            cands.append({"shape": "net_gross_mismatch", "parity_type": "validation_parity",
                          "confidence": "low", "guard_value": lhs, "effect_value": f"{lhs}-{rhs}",
                          "evidence": f"{name} returns `{lhs}` but moves `{lhs} - {rhs}` (gross vs net) — "
                                      f"a returned/accounted value may disagree with the transferred value",
                          "signals": {"fee_term": rhs}})
            break
    # ---- v2 generalization shapes (Phase 13) ----
    cands.extend(classify_v2_shapes(name, signature, snippet))

    # de-dup, keeping the HIGHEST-confidence candidate per key
    rank = {"high": 3, "medium": 2, "low": 1}
    best = {}
    for c in cands:
        k = (c["shape"], c["parity_type"], c["guard_value"], c["effect_value"])
        if k not in best or rank[c["confidence"]] > rank[best[k]["confidence"]]:
            best[k] = c
    return list(best.values())


def classify_validate_execute_pair(fa: dict, fb: dict) -> list:
    """Shape 2b: across validate*/execute* siblings, validate guards a raw-alias value while the execute
    sibling's effect uses the paired derived-alias value. fa/fb carry name + snippet-derived sets."""
    # require validate/execute kinship: same _core, different verb (one validate, one execute)
    if sfp._core(fa["name"]) != sfp._core(fb["name"]):
        return []
    val, exe = None, None
    for f in (fa, fb):
        nl = f["name"].lower()
        if nl.startswith("validate"):
            val = f
        elif nl.startswith("execute"):
            exe = f
    if not val or not exe:
        return []
    cands = []
    vg = val["guard_idents"]
    ee = exe["effect_operands"] | exe["calls_lower"]
    for vp in _t("value_alias_pairs", []):
        raw, derived = [r.lower() for r in vp["raw"]], [d.lower() for d in vp["derived"]]
        raw_in_guard = any(r in vg for r in raw)
        derived_in_exec = any(d in ee for d in derived)
        derived_in_guard = any(d in vg for d in derived)
        if raw_in_guard and derived_in_exec and not derived_in_guard:
            cands.append({"shape": "validate_execute_value_mismatch", "parity_type": "validation_parity",
                          "confidence": "medium",
                          "guard_value": next(r for r in raw if r in vg),
                          "effect_value": next(d for d in derived if d in ee),
                          "strong": exe["name"], "weak": val["name"],
                          "evidence": f"{val['name']} validates raw `{next(r for r in raw if r in vg)}` while "
                                      f"sibling {exe['name']} computes/uses derived "
                                      f"`{next(d for d in derived if d in ee)}` — validator checked the wrong basis",
                          "signals": {"core": sfp._core(val['name'])}})
    return cands
