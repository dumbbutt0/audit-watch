#!/usr/bin/env python3
"""
safe_management_coverage_taxonomy.py — pure (no-I/O) classifier for the SAFE-MANAGEMENT COVERAGE research
prototype. Detects guard/policy/blocklist contracts that protect a Gnosis Safe but either:

  - decode_offset_mismatch: decode a multi-arg Safe self-management selector at the WRONG calldata offset
    (read the wrong argument). Anchor: reNFT 2024-01 H-04 — disableModule(address prevModule, address module)
    protected arg is `module` @0x44, but the guard checks @0x24 (prevModule).
  - incomplete_selector_coverage: cover >=1 Safe self-management selector (proving intent to restrict Safe
    self-management) yet MISS a high-impact selector (setFallbackHandler/setGuard/enable-disableModule/
    module-exec/multiSend/owner-mgmt/permit). Anchors: reNFT H-02 (setFallbackHandler), H-05 (fallback/permit).

Two-signal gate: Signal-1 = Safe-guard selector-filter context AND >=1 Safe-specific self-mgmt selector covered;
Signal-2 = a concrete defect (offset mismatch OR a missing high-impact selector). Mechanism-based (offset values,
selector-set difference) — NEVER answer-key string matching.

RESEARCH-ONLY: the audit that uses this is read-only, is_gate:false, routes_in_production:false — never mints or
routes. High precision over recall. Scope = Safe-management selector coverage + calldata decode ONLY.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "safe_management_coverage_patterns.json"
_COMMENT_RE = re.compile(r"//[^\n]*|/\*.*?\*/", re.DOTALL)
_SAFE_SPECIFIC_FAMILIES = ("module_mgmt", "fallback_guard", "owner_mgmt", "module_exec", "batched_exec")


@lru_cache(maxsize=1)
def _cfg() -> dict:
    try:
        return json.loads(CONFIG.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def strip_comments(code: str) -> str:
    return _COMMENT_RE.sub(" ", code or "")


def _norm(text: str) -> str:
    return strip_comments(text or "").lower()


def _selector_covered(body: str, sel: dict) -> bool:
    """A selector is covered if its canonical hex literal OR a specific name-token appears in the guard body."""
    hx = (sel.get("selector_hex") or "").lower()
    if hx and hx in body:
        return True
    return any(tok in body for tok in sel.get("name_tokens", []))


def _parse_int(tok: str):
    tok = (tok or "").strip()
    try:
        return int(tok, 16) if tok.lower().startswith("0x") else int(tok)
    except ValueError:
        return None


def _branch_offset(body: str, sel: dict, constants: dict | None):
    """Resolve the calldata offset actually used when decoding this selector's argument.

    Strategy: (1) locate the selector's branch window (from a comparison against its hex/name-token to the next
    `else if`/branch boundary) and read the offset passed to a calldata load there; (2) fall back to a sibling
    `<...family...>_offset` constant. Returns an int offset or None. Pure: `constants` maps lowercased
    constant-name -> value string (resolved by the runner; tests may pass inline-hex bodies and omit it).
    """
    constants = constants or {}
    # candidate anchor tokens that mark this selector's branch
    anchors = [t for t in ([(sel.get("selector_hex") or "").lower()] + list(sel.get("name_tokens", []))) if t]
    load_re = re.compile(
        r"(?:_loadvaluefromcalldata|mload)\s*\(\s*(?:add\s*\(\s*)?[A-Za-z_]\w*\s*,\s*([A-Za-z0-9_]+)\s*\)"
    )
    for a in anchors:
        idx = body.find("== " + a)
        if idx < 0:
            idx = body.find(a)
        if idx < 0:
            continue
        # window: from the anchor to the next branch boundary
        rest = body[idx:]
        nxt = rest.find("else if", 4)
        window = rest[: nxt if nxt > 0 else 600]
        m = load_re.search(window)
        if m:
            tok = m.group(1)
            val = _parse_int(tok)
            if val is None:  # named offset constant -> resolve
                val = _parse_int(constants.get(tok.lower(), ""))
            if val is not None:
                return val
    # fallback: sibling offset constant whose name shares the selector's family token
    for tok in sel.get("name_tokens", []):
        base = tok.replace("_selector", "").strip("_")
        if not base:
            continue
        for cname, cval in constants.items():
            if "offset" in cname and base in cname:
                v = _parse_int(cval)
                if v is not None:
                    return v
    return None


def is_safe_guard(body: str, *, force: bool | None = None) -> bool:
    """Signal-1a: does this contract IMPLEMENT a Safe-guard transaction-check (a selector dispatch over a
    calldata-loaded selector), not merely CALL Safe functions? Tight, to avoid flagging modules/policies/factories
    that use enableModule/execTransactionFromModule as callers."""
    if force is not None:
        return force
    b = _norm(body)
    # Gnosis guard entrypoint / base contract is conclusive
    if "checktransaction" in b or "baseguard" in b:
        return True
    # otherwise require BOTH: a selector loaded from the tx calldata AND a selector-dispatch comparison
    has_calldata_selector = ("mload(add(data" in b) or ("_loadvaluefromcalldata" in b)
    has_dispatch = bool(re.search(r"selector\s*==", b)) or ("== gnosis_safe" in b) or ("unauthorizedselector" in b)
    return has_calldata_selector and has_dispatch


def classify(contract: str, guard_body: str, *, constants: dict | None = None,
             context: dict | None = None) -> list:
    """Return 0..N Safe-management coverage candidates for one guard contract. Pure."""
    cfg = _cfg()
    context = context or {}
    body = _norm(guard_body)
    clow = (contract or "").lower()

    # ---- suppression: the Safe primitive itself, not an integrator guard ----
    for lib in cfg.get("suppress_library_contracts", []):
        if clow == lib:
            return []

    # ---- Signal-1a: guard-filter context ----
    if not is_safe_guard(guard_body, force=context.get("is_safe_guard")):
        return []

    selectors = cfg.get("safe_selectors", [])
    covered = {s["name"]: s for s in selectors if _selector_covered(body, s)}
    covered_safe_specific = [n for n, s in covered.items() if s.get("family") in _SAFE_SPECIFIC_FAMILIES]

    # ---- Signal-1b: must restrict at least one Safe-specific self-mgmt selector ----
    if not covered_safe_specific:
        return []

    # admin-only / trusted path -> downgrade severity
    admin_only = bool(context.get("admin_only")) or any(
        t in body for t in cfg.get("suppress_admin_only_terms", [])
    )

    def _tier(t: str) -> str:
        if admin_only:
            return "low"
        return t

    candidates = []

    # ---- Signal-2a: decode offset mismatch on a covered multi-arg selector ----
    for name, sel in covered.items():
        po = _parse_int(sel.get("protected_offset") or "")
        if not sel.get("multi_arg") or po is None:
            continue
        used = _branch_offset(body, sel, constants)
        if used is not None and used != po:
            candidates.append({
                "finding_shape": "decode_offset_mismatch",
                "confidence": _tier("high"),
                "selector": name,
                "signature": sel.get("signature"),
                "used_offset": hex(used),
                "expected_offset": sel.get("protected_offset"),
                "explanation": (
                    f"{contract} guards {sel.get('signature')} but decodes the argument at offset {hex(used)} "
                    f"(the wrong argument) instead of {sel.get('protected_offset')} (the protected `module`). "
                    f"The whitelist/allow check therefore validates the wrong address, so a renter can {sel.get('role')} "
                    f"by routing the disable through an allowed predecessor (reNFT H-04 class)."),
                "signals": {"covered_safe_selectors": covered_safe_specific[:8],
                            "decode_used_offset": hex(used), "decode_expected_offset": sel.get("protected_offset")},
            })

    # ---- Signal-2b: incomplete coverage of high-impact self-mgmt selectors ----
    by_name = {s["name"]: s for s in selectors}
    missing_high = [n for n in cfg.get("flag_if_missing_high", []) if n in by_name and n not in covered]
    for n in missing_high:
        sel = by_name[n]
        candidates.append({
            "finding_shape": "incomplete_selector_coverage",
            "confidence": _tier("high"),
            "selector": n,
            "signature": sel.get("signature"),
            "explanation": (
                f"{contract} restricts Safe self-management (covers {', '.join(covered_safe_specific[:4])}) but does "
                f"NOT cover {sel.get('signature')}, so a renter can {sel.get('role')} — bypassing the guard "
                f"(reNFT H-02/H-05 class)."),
            "signals": {"covered_safe_selectors": covered_safe_specific[:8], "missing_selector": n,
                        "family": sel.get("family")},
        })

    # grouped medium (module-exec / owner-mgmt / multiSend) + approval-equiv, to keep volume low
    for group_key, shape_conf, label in (
        ("flag_if_missing_medium_grouped", "medium", "privileged Safe selectors"),
        ("flag_if_missing_approval_grouped", "medium", "approval-equivalent selectors"),
    ):
        grp = [n for n in cfg.get(group_key, []) if n in by_name and n not in covered]
        # approval group only meaningful if the guard already blocks approve/setApprovalForAll
        if group_key == "flag_if_missing_approval_grouped" and not (
            "setApprovalForAll" in covered or "approve" in covered
        ):
            continue
        if grp:
            candidates.append({
                "finding_shape": "incomplete_selector_coverage",
                "confidence": _tier(shape_conf),
                "selector": ",".join(grp),
                "signature": label,
                "explanation": (
                    f"{contract} restricts Safe self-management but leaves {label} uncovered: "
                    f"{', '.join(grp)}. Each is a residual escape path (module execution / owner-threshold change / "
                    f"batched delegate execution / gasless approval) the guard does not block."),
                "signals": {"covered_safe_selectors": covered_safe_specific[:8], "missing_selectors": grp,
                            "group": label},
            })

    return candidates


if __name__ == "__main__":  # tiny manual smoke
    import sys
    print(json.dumps(classify("Guard", sys.stdin.read()), indent=2))
