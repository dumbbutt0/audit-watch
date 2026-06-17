"""Phase-77 universal STATIC_LEAD schema + normalizer (RESEARCH-ONLY, un-wired).

Converts mixed detector/lens outputs into ONE comparable STATIC_LEAD shape WITHOUT rewriting detectors: missing fields are
filled null/"unknown". Carries the source's confidence/claim verbatim (never invents confidence). Refuses to normalize a
routed source (routes_in_production:true OR routed_manifest_ids != []) — the deep-pass never launders a routed source.

A STATIC_LEAD is a QUESTION, not a verdict.
"""
from __future__ import annotations
from typing import Any, Dict, Optional

LEAD_FIELDS = (
    "candidate_id", "detector_family", "trigger_contract", "trigger_function", "trigger_lines",
    "suspicious_pattern", "detector_claim", "source_snippets", "required_followup_questions",
    "known_false_positive_shapes", "minimum_evidence_to_advance",
)

FLAGS = {"is_gate": False, "research_only": True, "review_only": True, "routes_in_production": False, "routed_manifest_ids": []}


class RoutedSourceRefused(Exception):
    """Raised when a lead is built from a production-routed source — never laundered into the deep-pass."""


def _is_routed(raw: Dict[str, Any]) -> bool:
    return bool(raw.get("routes_in_production")) or bool(raw.get("routed_manifest_ids"))


def normalize_lead(raw: Dict[str, Any], *, detector_family: Optional[str] = None,
                   candidate_id: Optional[str] = None) -> Dict[str, Any]:
    """Normalize one raw detector/lens record into a STATIC_LEAD. Unknown fields -> null/'unknown'. Refuses routed sources."""
    if not isinstance(raw, dict):
        raise TypeError("raw lead must be a dict")
    if _is_routed(raw):
        raise RoutedSourceRefused(f"refusing routed source: routes_in_production={raw.get('routes_in_production')} "
                                  f"routed_manifest_ids={raw.get('routed_manifest_ids')}")
    tgt = raw.get("target", {}) if isinstance(raw.get("target"), dict) else {}
    lead = {
        "candidate_id": candidate_id or raw.get("candidate_id") or f"{tgt.get('contract') or raw.get('contract')}.{tgt.get('function') or raw.get('function')}",
        "detector_family": detector_family or raw.get("detector_family") or raw.get("detector") or "unknown",
        "trigger_contract": tgt.get("contract") or raw.get("contract") or raw.get("trigger_contract"),
        "trigger_function": tgt.get("function") or raw.get("function") or raw.get("trigger_function"),
        "trigger_lines": tgt.get("lines") or raw.get("lines") or raw.get("trigger_lines"),
        "suspicious_pattern": raw.get("suspicious_pattern") or raw.get("defect", {}).get("kind") if isinstance(raw.get("defect"), dict) else raw.get("suspicious_pattern"),
        "detector_claim": raw.get("detector_claim") or raw.get("decision") or raw.get("detector"),
        "source_snippets": raw.get("source_snippets") or raw.get("snippet") or None,
        "required_followup_questions": raw.get("required_followup_questions") or [],
        "known_false_positive_shapes": raw.get("known_false_positive_shapes") or [],
        "minimum_evidence_to_advance": raw.get("minimum_evidence_to_advance") or [],
    }
    for f in LEAD_FIELDS:
        lead.setdefault(f, None)
    lead.update(FLAGS)
    lead["state"] = "STATIC_LEAD"
    return lead


def is_valid_lead(lead: Dict[str, Any]) -> bool:
    return isinstance(lead, dict) and lead.get("state") == "STATIC_LEAD" and bool(lead.get("candidate_id")) \
        and bool(lead.get("detector_family")) and lead.get("routes_in_production") is False
