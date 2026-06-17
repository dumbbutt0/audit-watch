#!/usr/bin/env python3
"""
surface_recall_lens.py — Phase-81b RESEARCH-ONLY surface-first lead-recall lens (un-wired).

Bottleneck P81a exposed: the platform's safety stack is good, but lead generation is PATTERN-biased — it picks likely
bug SHAPES and misses the security-relevant SURFACES where awarded bugs actually live (e.g. it led on a narrow swap
helper instead of the missing-access-control entrypoint, and never led on the bridge-receive / executor surfaces). This lens
inverts the order: it picks SECURITY-RELEVANT SURFACES first and emits a STATIC_LEAD per surface even when the
mechanism is uncertain, then lets the UNCHANGED P77/P78 deep-pass + hygiene reason over them.

It is NOT a bug detector. It classifies every in-scope public/external function (+ receive/fallback) into generic
surface classes (config/surface_recall_lens.json — generic vocab, NO subject names) and is RECALL-biased: precision is
the downstream investigation's job, never this lens's. Output is a list of STATIC_LEADs (lead_schema.normalize_lead).

Reuse: sibling_function_parity_taxonomy.{strip_comments,extract_features} for pure-text body features;
investigation.lead_schema.normalize_lead for the canonical STATIC_LEAD shape (refuses routed sources).

is_gate:false research_only:true review_only:true routes_in_production:false routed_manifest_ids:[].
Usage: surface_recall_lens.py --src <dir-or-file> [--out <leads.json>] | --self-test
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent.parent
CFG = ROOT / "config" / "surface_recall_lens.json"
sys.path.insert(0, str(ROOT / "scripts"))
from sibling_function_parity_taxonomy import strip_comments, extract_features  # noqa: E402
from investigation.lead_schema import normalize_lead, is_valid_lead  # noqa: E402

FLAGS = {"is_gate": False, "research_only": True, "review_only": True,
         "routes_in_production": False, "routed_manifest_ids": []}

# function header up to the opening brace or a trailing ';' (interface decl).
_FUNC_RE = re.compile(r"\bfunction\s+([A-Za-z_]\w*)\s*\(", re.MULTILINE)
_SPECIAL_RE = re.compile(r"\b(receive|fallback)\s*\(\s*\)\s*([^;{]*)\{", re.MULTILINE)
_CONTRACT_RE = re.compile(r"\b(contract|library|interface|abstract\s+contract)\s+([A-Za-z_]\w*)")


@lru_cache(maxsize=1)
def _cfg() -> dict:
    return json.loads(CFG.read_text())


def _match_paren(text: str, open_idx: int) -> int:
    """Return index just after the matching ')' for the '(' at open_idx (or len(text) if unbalanced)."""
    depth = 0
    for k in range(open_idx, len(text)):
        c = text[k]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return k + 1
    return len(text)


def _brace_body(text: str, brace_idx: int) -> str:
    depth, started = 0, False
    for k in range(brace_idx, len(text)):
        c = text[k]
        if c == "{":
            depth += 1
            started = True
        elif c == "}":
            depth -= 1
            if started and depth == 0:
                return text[brace_idx:k + 1]
    return text[brace_idx:]


def _contract_at(clean: str, pos: int) -> str:
    name = ""
    for m in _CONTRACT_RE.finditer(clean):
        if m.start() > pos:
            break
        name = m.group(2)
    return name


def _is_interface_kind(clean: str, pos: int) -> bool:
    kind = ""
    for m in _CONTRACT_RE.finditer(clean):
        if m.start() > pos:
            break
        kind = m.group(1)
    return kind == "interface"


def enumerate_functions(source: str, file_rel: str = "") -> List[Dict[str, Any]]:
    """Enumerate functions from raw Solidity text. Returns dicts with name/contract/visibility/mutability/
    modifiers/signature/body/has_bytes_param/is_interface. Pure-text; safe on fixtures."""
    clean = strip_comments(source)
    out: List[Dict[str, Any]] = []

    def _emit(name: str, params: str, header: str, after_open: int, special: bool = False):
        # body
        brace = clean.find("{", after_open)
        semic = clean.find(";", after_open)
        no_body = brace == -1 or (semic != -1 and semic < brace)
        body = "" if no_body else _brace_body(clean, brace)
        toks = re.findall(r"[A-Za-z_]\w*", header)
        vis = next((t for t in toks if t in _cfg()["visibility_keywords"]), "")
        noise = set(_cfg()["header_noise_tokens"])
        mods = []
        # modifier tokens = identifiers in header that are not vis/mut/noise and not the return type list
        hdr_wo_returns = re.sub(r"returns\s*\([^)]*\)", " ", header)
        for t in re.findall(r"[A-Za-z_]\w*", hdr_wo_returns):
            if t in noise or t in _cfg()["visibility_keywords"]:
                continue
            mods.append(t)
        mut = next((t for t in toks if t in _cfg()["mutability_keywords"]), "")
        out.append({
            "name": name, "contract": _contract_at(clean, after_open), "file": file_rel,
            "visibility": (vis or ("external" if special else "")).lower(),
            "mutability": mut.lower(), "modifiers": mods,
            "signature": (("receive() " if special else f"function {name}(") + (params or "") + (")" if not special else "") + " " + header.strip())[:300],
            "body": body, "has_bytes_param": bool(re.search(r"\bbytes(\s|\[|\bcalldata|\bmemory|\s+\w)", params or "")),
            "is_interface": _is_interface_kind(clean, after_open), "no_body": no_body,
        })

    for m in _FUNC_RE.finditer(clean):
        name = m.group(1)
        popen = clean.find("(", m.start())
        pclose = _match_paren(clean, popen)
        params = clean[popen + 1:pclose - 1]
        hdr_end = min([i for i in (clean.find("{", pclose), clean.find(";", pclose)) if i != -1] or [pclose])
        header = clean[pclose:hdr_end]
        _emit(name, params, header, pclose)
    for m in _SPECIAL_RE.finditer(clean):
        kind = m.group(1)
        _emit(kind, "", m.group(2), m.end() - 1, special=True)
    return out


def _auth_modifier(fn: Dict[str, Any]) -> bool:
    rx = re.compile(_cfg()["auth_modifier_regex"])
    for mod in fn.get("modifiers", []):
        if rx.match(mod.lower()):
            return True
    return False


def classify_surface(fn: Dict[str, Any]) -> Dict[str, Any]:
    """Return {classes:[...], score:int, signals:{...}} for one function."""
    name = (fn.get("name") or "").lower()
    body = strip_comments(fn.get("body") or "").lower()
    feats = extract_features(fn.get("name", ""), fn.get("signature", ""), fn.get("modifiers"),
                             fn.get("body", ""), fn.get("visibility", ""))
    has_bytes = bool(fn.get("has_bytes_param"))
    auth = _auth_modifier(fn) or feats.get("msg_sender", False)
    is_view = (fn.get("mutability") or "") in ("view", "pure")
    classes: List[str] = []
    score = 0
    for cls, spec in _cfg()["surface_classes"].items():
        # individual generic signals (no class-name hardcoding)
        name_sig = (any(s in name for s in spec.get("name_substr", []))
                    or any(name.startswith(p) for p in spec.get("name_prefix", [])))
        body_sig = any(s in body for s in spec.get("body_substr", []))
        bytes_sig = bool(spec.get("shape_bytes_param")) and has_bytes
        both_sig = bool(spec.get("requires_both_shape_and_body")) and has_bytes and body_sig
        crosschain_sig = (any(t in body for t in spec.get("crosschain_body_substr", []))
                          and (has_bytes or not spec.get("crosschain_shape_needs_bytes_param")))
        _SIGNALS = {"name": name_sig, "body": body_sig, "bytes": bytes_sig,
                    "crosschain_shape": crosschain_sig}
        if "require_any" in spec:                       # P81c: explicit signal gate (tightened classes)
            hit = any(_SIGNALS.get(s, False) for s in spec["require_any"])
        elif spec.get("requires_both_shape_and_body"):
            hit = both_sig
        else:
            hit = name_sig or body_sig or bytes_sig
        if cls == "auth_boundary" and _auth_modifier(fn):
            hit = True
        if hit and spec.get("requires_auth_modifier") and not auth:
            hit = False
        if hit and spec.get("exclude_view_pure") and is_view:   # P81c: a receive that EXECUTES is state-changing
            hit = False
        if hit:
            classes.append(cls)
            score += int(spec.get("weight", 1))
    return {"classes": classes, "score": score,
            "signals": {"has_bytes_param": has_bytes, "auth_gated": auth,
                        "calls": sorted(feats.get("calls", []))[:8]}}


def _excluded(fn: Dict[str, Any], classes: List[str]) -> Optional[str]:
    ex = _cfg()["exclusions"]
    if fn.get("name") in ex.get("skip_names_exact", []):
        return "constructor/special"
    if ex.get("skip_interface_contracts") and fn.get("is_interface"):
        return "interface contract"
    if ex.get("skip_no_body") and fn.get("no_body"):
        return "no body (declaration)"
    if fn.get("visibility") in ex.get("skip_visibilities", []):
        return f"visibility={fn.get('visibility')}"
    if ex.get("skip_pure_view_getter_unless_class") and fn.get("mutability") in ("view", "pure") and not classes:
        return "pure/view getter, no surface class"
    return None


def lens_to_leads(functions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    leads: List[Dict[str, Any]] = []
    per_contract: Dict[str, int] = {}
    cap = _cfg()["exclusions"].get("max_leads_per_contract", 40)
    for fn in functions:
        cs = classify_surface(fn)
        if not cs["classes"]:
            continue
        if _excluded(fn, cs["classes"]):
            continue
        c = fn.get("contract") or "?"
        if per_contract.get(c, 0) >= cap:
            continue
        per_contract[c] = per_contract.get(c, 0) + 1
        raw = {
            "candidate_id": f"{c}.{fn.get('name')}",
            "detector_family": "surface_recall_lens",
            "contract": c, "function": fn.get("name"),
            "trigger_contract": c, "trigger_function": fn.get("name"),
            "trigger_lines": None,
            "suspicious_pattern": ",".join(cs["classes"]),
            "detector_claim": "security-relevant surface; mechanism uncertain",
            "source_snippets": (fn.get("signature") or "")[:200],
            "required_followup_questions": [f"is the {cls} surface adequately guarded?" for cls in cs["classes"]],
            "known_false_positive_shapes": [],
            "minimum_evidence_to_advance": ["defense ledger over this surface", "reachable from an EOA entrypoint"],
        }
        lead = normalize_lead(raw, detector_family="surface_recall_lens")
        lead["surface_classes"] = cs["classes"]
        lead["surface_score"] = cs["score"]
        lead["signals"] = cs["signals"]
        lead["file"] = fn.get("file")
        lead["visibility"] = fn.get("visibility")
        lead.update(FLAGS)
        leads.append(lead)
    leads.sort(key=lambda x: (-x.get("surface_score", 0), x["candidate_id"]))
    return leads


def run_src(src: Path) -> List[Dict[str, Any]]:
    files = [src] if src.is_file() else sorted(src.rglob("*.sol"))
    fns: List[Dict[str, Any]] = []
    for f in files:
        rel = str(f)
        try:
            rel = str(f.relative_to(ROOT))
        except ValueError:
            pass
        fns.extend(enumerate_functions(f.read_text(encoding="utf-8", errors="replace"), rel))
    return lens_to_leads(fns)


_SELFTEST_SRC = """
interface IThing { function poke(uint256 x) external; }
contract Vault {
    address owner;
    function setRouter(address r) public onlyOwner { router = r; }
    function execute(address target, bytes memory data) external returns (bool) {
        (bool success, ) = target.call(data); return success;
    }
    function sgReceive(uint16 c, bytes memory src, uint n, address t, uint amt, bytes memory payload) external onlyExecutor {
        IERC20(t).transfer(recipient, amt);
    }
    function collectFees(uint v, bytes memory info, bytes memory sig) public onlyUtb { feeBalance += v; }
    function totalAssets() public view returns (uint) { return x; }
}
"""


def _self_test() -> int:
    leads = lens_to_leads(enumerate_functions(_SELFTEST_SRC, "self.sol"))
    by = {l["candidate_id"]: l for l in leads}
    ok = True
    def chk(cond, msg):
        nonlocal ok; ok &= cond; print(f"  [{'PASS' if cond else 'FAIL'}] {msg}")
    chk(all(is_valid_lead(l) for l in leads), "all emitted leads are valid STATIC_LEADs")
    chk("Vault.setRouter" in by and "admin_config_setter" in by["Vault.setRouter"]["surface_classes"], "setRouter -> admin_config_setter")
    chk("Vault.execute" in by and "external_executor" in by["Vault.execute"]["surface_classes"], "execute -> external_executor")
    chk("Vault.sgReceive" in by and "bridge_receive" in by["Vault.sgReceive"]["surface_classes"], "sgReceive -> bridge_receive")
    chk("Vault.collectFees" in by and "fee_path" in by["Vault.collectFees"]["surface_classes"], "collectFees -> fee_path")
    chk("Vault.totalAssets" not in by, "pure/view getter excluded")
    chk("IThing.poke" not in by, "interface decl excluded")
    chk(all(l["routes_in_production"] is False and l["research_only"] for l in leads), "all leads research-only/un-wired")
    print("SELF-TEST:", "OK" if ok else "FAILED")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src")
    ap.add_argument("--out")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return _self_test()
    if not args.src:
        ap.error("--src required (or --self-test)")
    leads = run_src(Path(args.src))
    payload = {"research_only": True, "review_only": True, "phase": "P81b", "detector_family": "surface_recall_lens",
               "src": args.src, "lead_count": len(leads), "leads": leads, **FLAGS}
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(payload, indent=2))
    print(json.dumps({"src": args.src, "lead_count": len(leads),
                      "by_class": _class_hist(leads)}, indent=2))
    return 0


def _class_hist(leads: List[Dict[str, Any]]) -> Dict[str, int]:
    h: Dict[str, int] = {}
    for l in leads:
        for c in l.get("surface_classes", []):
            h[c] = h.get(c, 0) + 1
    return dict(sorted(h.items(), key=lambda kv: -kv[1]))


if __name__ == "__main__":
    raise SystemExit(main())
