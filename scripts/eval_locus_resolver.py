#!/usr/bin/env python3
"""eval_locus_resolver.py — canonical answer-key -> manifest function locus resolver (EVAL-HARNESS, P194).

Replaces the naive backtick regex in build_answer_key.py (which dropped function names present in
title/alt_titles/match_terms and captured var/lang noise). This module resolves an answer-key finding to a
coverage-manifest function deterministically, AUTO-RESOLVING ONLY SAFE tiers and REVIEW-GATING anything ambiguous.

Scope: eval-harness / measurement infrastructure ONLY. It is NOT wired into the production pipeline, does NOT
mutate answer keys, sets no severity/routing, and mints no findings. A resolved locus means "the awarded function
is locatable in the manifest" — it is a MEASUREMENT correction, not a recall/bug claim.

Public API:
    build_manifest_index(items) -> {"by_contract": {contract_lower: {name: item}}, "names": set, "ids": {(c,n):id}}
    resolve_locus(finding, manifest_index, match_terms=None) -> dict(status, function, manifest_id, tier,
                                                                     field_cited, evidence, candidates)
      status ∈ {RESOLVED, AMBIGUOUS, REVIEW_GATED, UNRESOLVED}
"""
from __future__ import annotations
import re

# Generic / Solidity-global / math noise that must never be treated as a resolved function locus.
GENERIC_TOKENS = {
    "get","set","the","is","of","to","for","and","if","msg","require","address","uint","uint256","int","int256",
    "bool","bytes","bytes32","memory","storage","public","external","internal","private","view","pure","payable",
    "return","returns","function","mapping","struct","event","emit","call","send","transfer","value","amount",
    "data","params","owner","sender","this","abi","keccak256","solidity","javascript","console","json","true",
    "false","null","min","max","sum","abs","diff","add","sub","mul","div","mod","balance","balanceof",
    "totalsupply","constructor","fallback","receive","initialize","array","length","index","token","tokens",
    "user","users","pool","vault","market","design","note","contract","contracts","code","example","javascripts",
}
_PREFIXES = ("get","set","update","is","_")
_SCALE = re.compile(r"(x18|x96|x32|x128|usdx?18?|wad|e18|usd)$")


def _norm(name: str) -> str:
    t = re.sub(r"[^a-z0-9]", "", str(name).lower())
    return _SCALE.sub("", t)


def _strip_prefix(low: str) -> str:
    for p in _PREFIXES:
        if p != "_" and low.startswith(p) and len(low) > len(p) + 2:
            return low[len(p):]
    return low.lstrip("_")


def _is_generic(name: str) -> bool:
    low = str(name).lower()
    return low in GENERIC_TOKENS or len(re.sub(r"[^a-z0-9]", "", low)) < 4


def build_manifest_index(items):
    by_contract, ids, orig = {}, {}, {}
    names = set()
    for it in items:
        if it.get("kind") != "function":
            continue
        c = str(it.get("contract") or "")
        cl = c.lower()
        n = it.get("name")
        if not n:
            continue
        by_contract.setdefault(cl, {}).setdefault(n, it)
        ids[(cl, n)] = it.get("id")
        orig[cl] = c
        names.add(n)
    return {"by_contract": by_contract, "names": names, "ids": ids, "orig": orig}


def _contracts(finding):
    s = set()
    for x in (finding.get("affected_contracts") or []):
        s.add(re.sub(r"\.sol$", "", str(x)).lower())
    for fld in ("affected", "location"):
        v = finding.get(fld)
        if isinstance(v, str):
            for m in re.findall(r"\b([A-Z][A-Za-z0-9_]{2,})\b", v):     # CamelCase contract refs
                s.add(m.lower())
            head = re.sub(r"\.sol$", "", v.strip().split(".")[0].split("(")[0].split("/")[0].strip())
            if head and re.fullmatch(r"[A-Za-z_]\w*", head):            # bare 'affected' token
                s.add(head.lower())
    return {c for c in s if c}


def _field_text(finding, field):
    v = finding.get(field)
    if isinstance(v, list):
        return " ".join(str(x) for x in v)
    return str(v or "")


def _verbatim_hits(text, contract_fns):
    """manifest function names that appear as whole-word tokens in text (guardrail-filtered)."""
    hits = set()
    for n in contract_fns:
        if _is_generic(n):
            continue
        if re.search(rf"(?<![A-Za-z0-9_]){re.escape(n)}(?![A-Za-z0-9_])", text):
            hits.add(n)
    return hits


def resolve_locus(finding, manifest_index, match_terms=None):
    by_contract = manifest_index["by_contract"]
    ids = manifest_index["ids"]
    cts = [c for c in _contracts(finding) if c in by_contract]
    if not cts:
        return {"status": "UNRESOLVED", "function": None, "manifest_id": None, "tier": None,
                "field_cited": None, "evidence": "no affected contract present in manifest", "candidates": []}

    orig = manifest_index.get("orig", {})

    def result(status, contract, name, tier, field, ev, cands=None):
        disp_c = orig.get(contract, contract)
        return {"status": status, "function": (f"{disp_c}.{name}" if name else None),
                "manifest_id": ids.get((contract, name)) if name else None, "tier": tier,
                "field_cited": field, "evidence": ev, "candidates": sorted(cands or [])}

    # SAFE verbatim tiers, in field priority order. Auto-resolve only if EXACTLY ONE in-contract fn matches.
    SAFE_FIELDS = [("DIRECT_NAME_MISSED", "title"),
                   ("DIRECT_NAME_MISSED", "affected_functions"),
                   ("DIRECT_NAME_MISSED", "functions"),
                   ("DIRECT_NAME_MISSED", "root_cause"),
                   ("ALT_TITLE_MISSED", "alt_titles")]
    for ct in cts:
        contract_fns = set(by_contract[ct])
        for tier, field in SAFE_FIELDS:
            hits = _verbatim_hits(_field_text(finding, field), contract_fns)
            if len(hits) == 1:
                n = next(iter(hits))
                return result("RESOLVED", ct, n, tier, f"answer_key.{field}",
                              f"verbatim manifest fn '{n}' in {field} (contract-constrained, unique)")
            if len(hits) > 1:
                return result("AMBIGUOUS", ct, None, tier, f"answer_key.{field}",
                              "multiple in-contract manifest fns named verbatim; not auto-selected", hits)
        # MATCH_TERM verbatim (only if provided)
        if match_terms:
            mt_text = " ".join(str(t) for t in match_terms)
            hits = _verbatim_hits(mt_text, contract_fns)
            if len(hits) == 1:
                n = next(iter(hits))
                return result("RESOLVED", ct, n, "MATCH_TERM_MISSED", "eval_findings.match_terms",
                              f"verbatim manifest fn '{n}' in match_terms (contract-constrained, unique)")
            if len(hits) > 1:
                return result("AMBIGUOUS", ct, None, "MATCH_TERM_MISSED", "eval_findings.match_terms",
                              "multiple in-contract manifest fns in match_terms; not auto-selected", hits)

    # NORMALIZATION tier: normalized answer-key token == normalized manifest fn (unique, in-contract).
    ak_tokens = set()
    for fld in ("affected_functions", "functions"):
        v = finding.get(fld)
        if isinstance(v, list): ak_tokens |= set(v)
        elif isinstance(v, str): ak_tokens |= set(re.split(r"[\/,\s]+", v))
    ak_tokens |= set(re.findall(r"`([A-Za-z_]\w{2,})", _field_text(finding, "title")))
    ak_tokens = {t for t in ak_tokens if t and not _is_generic(t)}
    for ct in cts:
        nmap = {}
        for n in by_contract[ct]:
            if not _is_generic(n): nmap.setdefault(_norm(n), set()).add(n)
        for t in ak_tokens:
            cand = nmap.get(_norm(t))
            if cand and len(cand) == 1:
                n = next(iter(cand))
                if n != t:  # exact handled above
                    return result("RESOLVED", ct, n, "NORMALIZATION_FAILURE", "normalized(answer_key)",
                                  f"normalized('{t}')==manifest fn '{n}' (contract-constrained, unique)")

    # REVIEW_GATED: get/set/update prefix drift — detected but NEVER auto-resolved.
    for ct in cts:
        stripped = {}
        for n in by_contract[ct]:
            if not _is_generic(n): stripped.setdefault(_strip_prefix(n.lower()), set()).add(n)
        for t in ak_tokens:
            cand = stripped.get(_strip_prefix(t.lower()))
            if cand and not any(_norm(t) == _norm(n) for n in cand):
                return result("REVIEW_GATED", ct, None, "GET_SET_DRIFT", "answer_key.token",
                              f"get/set/update prefix drift: '{t}' ~ {sorted(cand)} (needs human confirm)", cand)

    return {"status": "UNRESOLVED", "function": None, "manifest_id": None, "tier": None,
            "field_cited": None, "evidence": "no safe verbatim/normalized match in resolved contract(s)",
            "candidates": []}


# eval-harness flag (mirrors research-platform discipline): not production, no routing/severity/findings.
EVAL_HARNESS_ONLY = True
ROUTES_IN_PRODUCTION = False
