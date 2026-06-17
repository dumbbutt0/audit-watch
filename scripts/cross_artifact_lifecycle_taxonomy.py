#!/usr/bin/env python3
"""
cross_artifact_lifecycle_taxonomy.py — classify an in-scope item as a CROSS-ARTIFACT controller: it
deploys / initializes / owns / upgrades / configures / holds custody over another artifact (often an
out-of-scope token/collection/escrow/vault/proxy). The controlled artifact's lifecycle invariants stay
audit-relevant THROUGH the controller. Mirrors griefing_dos_taxonomy. Used by cross_artifact_lifecycle_audit.py.

classify() -> {cross_artifact_sensitive, role, deployed_kind, lifecycle_signals, missing_lifecycle,
               matched_on, severity_ceiling_hint}. The final disposition STATUS (cross_artifact_lifecycle_risk /
cross_artifact_scope_linked / lifecycle_under_escalated / lifecycle_cleared_with_local_proof) is computed by
the audit runner using coverage + scope-link, since it needs the manifest/dispositions.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "cross_artifact_lifecycle_patterns.json"


@lru_cache(maxsize=1)
def load_taxonomy(path: str | None = None) -> dict:
    p = Path(path) if path else CONFIG
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return {"deploy_signals": [], "init_signals": [], "disable_init_signals": [], "ownership_signals": [],
                "upgrade_signals": [], "custody_signals": [], "artifact_kinds": {}, "role_signals": {},
                "high_risk_roles": []}


def _strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.DOTALL)
    return re.sub(r"//[^\n]*", " ", text)


def _regex_any(text: str, patterns: list[str]) -> bool:
    for p in patterns:
        try:
            if re.search(p, text, re.IGNORECASE):
                return True
        except re.error:
            if p.lower() in text.lower():
                return True
    return False


def _regex_any_cs(text: str, patterns: list[str]) -> bool:
    """Case-SENSITIVE — so `new\\s+[A-Z]\\w*\\(` matches a contract deploy (`new ERC721Bridgeable(`)
    but NOT a Solidity memory allocation (`new string(`, `new bytes(`, `new uint256[](`)."""
    for p in patterns:
        try:
            if re.search(p, text):
                return True
        except re.error:
            if p in text:
                return True
    return False


def _deployed_kind(body_l: str, name_l: str, tax: dict) -> str | None:
    for kind, terms in tax.get("artifact_kinds", {}).items():
        if any(t in body_l or t in name_l for t in terms):
            return kind
    return None


def _roles(body: str, name_l: str, tax: dict) -> list[str]:
    out = []
    for role, sigs in tax.get("role_signals", {}).items():
        if _regex_any(name_l, sigs) or _regex_any(body, sigs):
            out.append(role)
    return out


def classify(name: str, signature: str = "", file: str = "", contract: str = "",
             snippet: str = "", tags=None, taxonomy: dict | None = None) -> dict:
    tax = taxonomy or load_taxonomy()
    name_l = (name or "").lower()
    body = _strip_comments(" ".join([signature or "", snippet or ""]))
    body_l = body.lower()

    # deploy detection is case-SENSITIVE so `new string(` / `new bytes(` memory allocations are NOT
    # mistaken for contract deploys (`new ERC721Bridgeable(`).
    has_deploy = _regex_any_cs(body, tax.get("deploy_signals", []))
    has_init = _regex_any(body, tax.get("init_signals", []))
    has_disable_init = _regex_any(body, tax.get("disable_init_signals", []))
    has_ownership = _regex_any(body, tax.get("ownership_signals", []))
    has_upgrade = _regex_any(body, tax.get("upgrade_signals", []))
    has_custody = _regex_any(body, tax.get("custody_signals", [])) or _regex_any(name_l, tax.get("custody_signals", []))

    roles = _roles(body, name_l, tax)
    # PRIMITIVE GATE (FP backbone): only sensitive if the item actually DEPLOYS or holds custody over an
    # artifact, or is an explicit ownership/upgrade controller of one. A lone "initialize" or "owner=" on the
    # contract's OWN state is not cross-artifact — we require a deploy/custody/controller primitive.
    is_controller = has_deploy or ("custodian" in roles and has_custody) or \
        ("upgrader" in roles and has_upgrade and has_deploy) or ("factory" in roles and has_deploy)
    if not is_controller:
        return {"cross_artifact_sensitive": False, "role": None, "deployed_kind": None,
                "lifecycle_signals": [], "missing_lifecycle": [], "matched_on": None, "severity_ceiling_hint": None}

    deployed_kind = _deployed_kind(body_l, name_l, tax)

    lifecycle_signals = []
    if has_deploy: lifecycle_signals.append("deploy")
    if has_init: lifecycle_signals.append("initialize")
    if has_disable_init: lifecycle_signals.append("disable_initializers")
    if has_ownership: lifecycle_signals.append("ownership_transfer")
    if has_upgrade: lifecycle_signals.append("upgrade_authority")
    if has_custody: lifecycle_signals.append("custody")

    # missing lifecycle = the steps a deployer/factory SHOULD do but didn't (in this item's body).
    missing = []
    if has_deploy:
        if not has_disable_init:
            missing.append("disable_initializers")
        if not has_ownership:
            missing.append("ownership_transfer_to_controller")
        if not has_upgrade:
            missing.append("upgrade_authority_retained")

    primary_role = next((r for r in ("deployer", "factory", "custodian", "upgrader", "owner_setter", "initializer", "configurer") if r in roles), roles[0] if roles else "controller")
    sev = "High" if (primary_role in tax.get("high_risk_roles", []) and missing) else "Medium"
    return {"cross_artifact_sensitive": True, "role": primary_role, "deployed_kind": deployed_kind,
            "lifecycle_signals": lifecycle_signals, "missing_lifecycle": missing,
            "matched_on": "deploy" if has_deploy else ("custody" if has_custody else "controller"),
            "severity_ceiling_hint": sev}


def is_high_risk(classification: dict, taxonomy: dict | None = None) -> bool:
    """High-risk = a controller with at least one MISSING lifecycle step (the under-handled case)."""
    if not classification.get("cross_artifact_sensitive"):
        return False
    return bool(classification.get("missing_lifecycle"))
