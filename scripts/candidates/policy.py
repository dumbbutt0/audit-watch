"""Loads config/candidate_validation_policy.json (Stage-1 policy). Read-only."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / "config/candidate_validation_policy.json"

_DEFAULT: Dict[str, Any] = {
    "stage1_gate_order": ["source_resolve", "reachability", "context_map"],
    "stop_state": "CONTEXT_MAPPED",
    "next_required_gate": "defense_map_gate",
    "poc_allowed": False,
    "report_allowed": False,
    "detector_requirements": {},
    "privileged_modifier_terms": ["onlyOwner", "onlyRole", "onlyGovernance", "onlyAdmin"],
}


def load_policy() -> Dict[str, Any]:
    try:
        return json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return dict(_DEFAULT)


def detector_requirements(detector: str) -> Dict[str, Any]:
    return load_policy().get("detector_requirements", {}).get(detector, {})
