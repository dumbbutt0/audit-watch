"""validate_dynamic_weight_lifecycle_clears — proof gate for clearing a dynamic-weight-lifecycle surface.

A clear of a lifecycle-sensitive surface (setWeights/update/onSwap/computeBalance) requires a
lifecycle-completeness proof: each of {normalized_sum, per_weight_bounds, epsilon_guard, update_interval,
staleness} is either enforced (with a concrete code location) or shown not-applicable, AND the permissionless
update paths were considered. Absent that, the clear is routed to needs_deep_pass (re-surface only — this module
never confirms a finding or sets severity). Mirrors validate_math_estimator_clears.py.
"""

from __future__ import annotations

from typing import Optional

REQUIRED_PROOF_FIELDS = [
    "normalized_sum_proof", "per_weight_bounds_proof", "epsilon_guard_proof",
    "update_interval_proof", "staleness_proof", "permissionless_paths_considered",
]
# boilerplate that asserts a check exists without locating it → confirmatory, not a real proof
_CONFIRMATORY_PHRASES = ["enforced", "checked", "validated", "guarded", "handled", "is correct",
                         "looks fine", "appears", "as expected", "n/a", "not applicable"]
# a real per-check proof should cite something concrete (a function/modifier/line/require)
_CONCRETE_TOKENS = ["require(", "revert", "function ", "modifier ", "line ", ":", "_guard", "_clamp",
                    "<=", ">=", "==", "interval", "timestamp", "sum", "minweight", "maxweight"]


def _nonempty(v) -> bool:
    if isinstance(v, bool):
        return True
    if isinstance(v, (list, dict)):
        return len(v) > 0
    return bool(str(v or "").strip())


def _text(v) -> str:
    if isinstance(v, (list, tuple)):
        return " ".join(str(x) for x in v).lower()
    return str(v or "").lower()


def validate_proof(proof: dict, adversarial: bool = True) -> tuple[str, list[str], list[str]]:
    """Return (status, missing_fields, reasons).
    status in {lifecycle_proof_valid, missing_lifecycle_proof, incomplete_lifecycle_proof,
               confirmatory_lifecycle_proof}. adversarial=False skips the boilerplate content check."""
    if not isinstance(proof, dict):
        return "missing_lifecycle_proof", list(REQUIRED_PROOF_FIELDS), []
    missing = [f for f in REQUIRED_PROOF_FIELDS if not _nonempty(proof.get(f))]
    if missing:
        return "incomplete_lifecycle_proof", missing, []
    if adversarial:
        reasons: list[str] = []
        for f in REQUIRED_PROOF_FIELDS[:5]:  # the 5 per-check proofs (not the paths-considered field)
            t = _text(proof.get(f))
            # a per-check proof that only asserts ("enforced"/"checked"/"n/a") without any concrete anchor
            if any(p in t for p in _CONFIRMATORY_PHRASES) and not any(c in t for c in _CONCRETE_TOKENS):
                reasons.append(f"{f} asserts the check exists ('{t[:40]}…') without a concrete code anchor "
                               f"(require/modifier/line/bound)")
        if reasons:
            return "confirmatory_lifecycle_proof", [], reasons
    return "lifecycle_proof_valid", [], []


def classify_clear(disp: dict, item: dict, tax: Optional[dict] = None, adversarial: bool = True) -> dict:
    import dynamic_weight_lifecycle_taxonomy as dwl
    cls = dwl.classify_manifest_item(item, taxonomy=tax) if item else dwl._neg()
    if not cls.get("lifecycle_sensitive"):
        return {"status": "not_lifecycle_sensitive", "lifecycle_domain": "none", "missing": [], "reasons": []}
    status, missing, reasons = validate_proof(disp.get("dynamic_weight_lifecycle_proof"), adversarial=adversarial)
    return {"status": status, "lifecycle_domain": cls["lifecycle_domain"], "missing": missing, "reasons": reasons,
            "missing_lifecycle_checks": cls.get("missing_lifecycle_checks", [])}
