"""dynamic_weight_lifecycle_taxonomy — classify dynamic-weight / Balancer-V3 weight-lifecycle surfaces.

The single source of truth shared by the lens (dynamic_weight_lifecycle_audit.py), the validator
(validate_dynamic_weight_lifecycle_clears.py), and the coverage_sweep_write enforcement, so all three agree on
what is lifecycle-sensitive. Two-signal FP backbone (DOMAIN term + STRUCTURAL signal, or an UNAMBIGUOUS token);
pure getters and admin-only-gated setters are excluded. RE-SURFACE ONLY — classification never sets severity,
mints findings, or routes; it only marks a surface as needing the weight-set lifecycle deep-trace.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_CFG = ROOT / "config" / "dynamic_weight_lifecycle_patterns.json"


def load_taxonomy(path: str | None = None) -> dict:
    try:
        return json.loads(Path(path or _DEFAULT_CFG).read_text())
    except Exception:  # noqa: BLE001  — fail-open: no taxonomy → nothing is sensitive
        return {}


def _strip_comments(text: str) -> str:
    text = re.sub(r"//[^\n]*", " ", text)
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return text


def _neg() -> dict:
    return {"lifecycle_sensitive": False, "lifecycle_domain": "none",
            "missing_lifecycle_checks": [], "present_lifecycle_checks": []}


def classify(name: str, signature: str = "", file: str = "", contract: str = "",
             snippet: str = "", tags: Optional[list] = None, taxonomy: dict | None = None) -> dict:
    tax = taxonomy if taxonomy is not None else load_taxonomy()
    if not tax:
        return _neg()
    name_l = (name or "").lower()
    sig_l = (signature or "").lower()
    body_l = _strip_comments((snippet or "")).lower()
    ident = name_l + "  " + body_l

    unambiguous = any(tok in name_l for tok in tax.get("unambiguous_tokens", []))

    # FP control 1: pure getters have no state transition to analyse — EXCEPT the unambiguous lifecycle
    # entrypoints (onSwap/computeBalance are `view` in Balancer-V3 yet are the core pricing/lifecycle surfaces,
    # e.g. M-08 maxTradeSizeRatio bypass, M-12 computeBalance boundary revert). The getter cut only applies to
    # the ambiguous two-signal path.
    if not unambiguous and any(g in sig_l for g in tax.get("getter_tokens", [])):
        return _neg()

    # FP control 2: an admin-ONLY-gated setter (no permissionless update path) is not the target — UNLESS it
    # is an unambiguous lifecycle entrypoint (those are the awarded surfaces and may be permissionlessly
    # reachable via performUpdate/onSwap).
    role_gated = any(r in sig_l for r in tax.get("role_gate_tokens", []))
    if role_gated and not unambiguous:
        return _neg()

    if not unambiguous:
        has_domain = any(t in ident for t in tax.get("domain_terms", []))
        has_struct = any(re.search(p, snippet or "", re.I) for p in tax.get("structural_signals", []))
        if not (has_domain and has_struct):
            return _neg()

    # lifecycle-check completeness over the function body
    sig_map = tax.get("lifecycle_check_signals", {})
    present, missing = [], []
    for chk in tax.get("lifecycle_checks", []):
        toks = sig_map.get(chk, [chk])
        (present if any(t in body_l for t in toks) else missing).append(chk)
    return {"lifecycle_sensitive": True, "lifecycle_domain": "dynamic_weight_lifecycle",
            "missing_lifecycle_checks": missing, "present_lifecycle_checks": present}


def _snippet(file_rel: str, start, end) -> str:
    try:
        from audit_context import audit_path
        base = audit_path("contracts")
        p = (base / file_rel) if file_rel and not Path(file_rel).is_absolute() else Path(file_rel)
        if not p.exists():
            p = ROOT / file_rel
        if not p.exists() or start is None or end is None:
            return ""
        lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
        return "\n".join(lines[max(0, int(start) - 1):int(end)])
    except Exception:  # noqa: BLE001
        return ""


def classify_manifest_item(item: dict, taxonomy: dict | None = None) -> dict:
    """Classify a coverage-manifest item, reading its source span for the snippet (mirrors
    math_estimator_taxonomy.classify_manifest_item so lens/validator/writer agree)."""
    span = item.get("source_span", {}) or {}
    snip = _snippet(item.get("file", ""), span.get("start_line"), span.get("end_line"))
    return classify(item.get("name", ""), item.get("signature", ""), item.get("file", ""),
                    item.get("contract", ""), snippet=snip, tags=item.get("tags"), taxonomy=taxonomy)


def is_high_risk(classification: dict) -> bool:
    return bool(classification.get("lifecycle_sensitive")) and bool(classification.get("missing_lifecycle_checks"))
