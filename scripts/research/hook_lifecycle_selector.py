#!/usr/bin/env python3
"""
hook_lifecycle_selector.py — RESEARCH-ONLY F3 hook-lifecycle selector (P181). UN-WIRED.

Re-surfaces Balancer/AMM hook-lifecycle risks ONLY when all of: (1) a Balancer/AMM hook lifecycle surface is
present, (2) the hook mutates pool/accounting state, (3) the transition depends on lifecycle ordering, OR
(4) a matching lifecycle guard is missing/unproven — i.e. (1) AND (2) AND ((3) OR (4)). Avoid filters reject
view/pure hooks, no-state-impact hooks, admin-only config hooks, generic callback noise, and interface-only
signatures.

RESEARCH DETECTOR PLATFORM DISCIPLINE (CLAUDE.md): this file carries research_only=true / routes_in_production=
false / is_gate=false, is imported by NOTHING in production (no run_pipeline / agent_policy / coverage_sweep /
dependency_clear / *_audit reference), never mutates anything, never mints findings or sets severity. Promotion
to production is a separate later human decision.
"""
from __future__ import annotations

import re
from pathlib import Path

_FLAGS = {"research_only": True, "routes_in_production": False, "is_gate": False, "re_surface_only": True}
ROOT = Path(__file__).resolve().parent.parent.parent

# (1) DOMAIN — Balancer-V3 hook lifecycle entrypoints + LP-NFT lifecycle.
_HOOK_NAME_TOKENS = ("onafter", "onbefore", "onregister", "afterupdate",
                     "addliquidity", "removeliquidity", "oninitialize")
_NFT_LIFECYCLE_NAMES = ("_update", "mint", "burn")  # only counted in an NFT/LP-NFT contract context
# (2) STRUCTURAL — pool/accounting state mutation.
_STATE_SIGNALS = [r"\bpoolsFeeData\b", r"\.push\(", r"\b_mint\b", r"\b_burn\b", r"\bburn\(", r"\bmint\(",
                  r"\baccruedFees?\b", r"\bfeeAmount\b", r"\[[^\]]+\]\s*=", r"\+=", r"-=",
                  r"\btransfer(From)?\(", r"\bbalances?\b\s*=", r"\bweights?\b\s*=", r"storage\b"]
# (3) LIFECYCLE-ORDERING — recovery mode / deposit-array+cap / NFT mint-burn pairing / fee-accrual on liquidity /
#     before-after pairing / initialize-once.
_LIFECYCLE_SIGNALS = [r"recover", r"\.push\(", r"\.length\b", r"\b_mint\b", r"\b_burn\b", r"\bburn\(",
                      r"accrued", r"uplift", r"currentFee", r"feeAmount", r"minWithdrawalFee",
                      r"\binitiali[sz]e", r"before", r"after"]
# (4) GUARD-GAP — auth/bound guards appropriate to a lifecycle hook. ABSENCE of all of these = a gap.
_GUARD_SIGNALS = [r"onlySelfRouter", r"onlyRouter", r"_ensureSelfRouter", r"onlyVault", r"isApprovedOrOwner",
                  r"require\([^)]*length[^)]*<", r"require\([^)]*<\s*\d", r"recover", r"initiali[sz]ed"]
# avoid: admin-only config hooks
_ADMIN_MODIFIERS = ("onlyowner", "onlygovernor", "onlyadmin", "onlymanager", "onlyauthorized")
# avoid: generic callback noise
_CALLBACK_NOISE = ("onerc721received", "onerc1155received", "onerc1155batchreceived", "fallback", "receive")


def _re_any(text: str, pats) -> bool:
    return any(re.search(p, text, re.I) for p in pats)


def _neg(reason="") -> dict:
    return {"hook_lifecycle_sensitive": False, "signals": [], "missing_guard": False, "reason": reason,
            **_FLAGS}


def classify(name: str, signature: str = "", visibility: str = "", mutability: str = "",
             contract: str = "", file: str = "", snippet: str = "") -> dict:
    nm = (name or "").lower()
    sig = (signature or "").lower()
    body = snippet or ""
    vis = (visibility or "").lower()
    mut = (mutability or "").lower()

    # ----- avoid filters (FP control) -----
    if mut in ("view", "pure"):
        return _neg("view/pure hook — no state transition")
    if nm in _CALLBACK_NOISE:
        return _neg("generic callback noise")
    if any(m in sig for m in _ADMIN_MODIFIERS) and nm.startswith(("set", "configure", "update")) \
            and not nm.startswith("afterupdate"):
        return _neg("admin-only configuration hook")
    if (contract or "").startswith("I") and (contract or "")[1:2].isupper() and not body.strip():
        return _neg("interface-only hook signature")

    # ----- (1) DOMAIN: is this a hook-lifecycle surface? -----
    is_hook = any(t in nm for t in _HOOK_NAME_TOKENS)
    is_nft_life = nm in _NFT_LIFECYCLE_NAMES and ("nft" in (contract or "").lower())
    if not (is_hook or is_nft_life):
        return _neg("not a Balancer/AMM hook-lifecycle surface")

    # ----- (2) STRUCTURAL: does it mutate pool/accounting state? -----
    has_state = _re_any(body, _STATE_SIGNALS)
    if not has_state:
        return _neg("hook present but no pool/accounting state mutation")

    # ----- (3) lifecycle-ordering OR (4) missing guard -----
    has_lifecycle = _re_any(body, _LIFECYCLE_SIGNALS)
    has_guard = _re_any(body, _GUARD_SIGNALS) or any(m in sig for m in
                                                     ("onlyselfrouter", "onlyrouter", "onlyvault"))
    missing_guard = not has_guard
    if not (has_lifecycle or missing_guard):
        return _neg("hook mutates state but no lifecycle-ordering signal and a guard is present")

    signals = []
    if is_hook:
        signals.append("balancer_hook")
    if is_nft_life:
        signals.append("nft_lifecycle")
    if has_state:
        signals.append("state_mutation")
    if has_lifecycle:
        signals.append("lifecycle_ordering")
    if missing_guard:
        signals.append("missing_lifecycle_guard")
    return {"hook_lifecycle_sensitive": True, "signals": signals, "missing_guard": missing_guard,
            "reason": "+".join(signals), **_FLAGS}


def _snippet(file_rel: str, start, end, maxlines: int = 60) -> str:
    if not file_rel or not start:
        return ""
    p = Path(file_rel)
    if not p.exists():
        p = ROOT / file_rel
    if not p.exists():
        # manifests store repo-relative or audit-relative paths; try a couple bases
        for base in (ROOT, ROOT / "audits"):
            cand = base / file_rel
            if cand.exists():
                p = cand; break
    try:
        lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return ""
    a = max(0, int(start) - 1)
    b = min(len(lines), int(end or (a + maxlines)))
    return "\n".join(lines[a:max(b, a + 1)][:maxlines])


def classify_manifest_item(item: dict) -> dict:
    if item.get("kind") != "function":
        return _neg("not a function")
    span = item.get("source_span") or {}
    snip = _snippet(item.get("file", ""), span.get("start_line"), span.get("end_line"))
    return classify(item.get("name", ""), item.get("signature", ""), item.get("visibility", ""),
                    item.get("mutability", ""), item.get("contract", ""), item.get("file", ""), snippet=snip)


def is_high_risk(classification: dict) -> bool:
    return bool(classification.get("hook_lifecycle_sensitive")) and bool(classification.get("missing_guard"))
