#!/usr/bin/env python3
"""
migration_flow_taxonomy.py — Classifier for L1->L2 migration / reseed state-flow surfaces. Used by
migration_flow_audit.py. Mirrors the prior lens taxonomies but is the FIRST cross-function model: the
audit script additionally resolves the `cross_function_invariants` against the manifest.

FP backbone (the spec's controls):
  * MIGRATION-CONTEXT REQUIRED: an item is migration_flow_sensitive only when it has a migration-context
    signal — its file is in a reseed/migration/L1/L2 path, OR its name/snippet hits a migration_context_term.
    An ordinary SiloFacet.deposit/withdraw/claim or a generic initializeOwner with NO migration context is
    NOT tagged (this is what keeps the lens from re-flagging the whole Silo).
  * HIGH-RISK requires migration-context AND a state-domain signal (a state_domain_term hit).
  * Comments are stripped before matching; a lone bridge constant (handled by the cross-chain lens) is not
    tagged unless it sits inside a migration state-flow function.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "migration_flow_patterns.json"

# generic init names that, with no migrated-state signal, are just ownership/admin setup
_GENERIC_INIT = ("initializeowner", "initowner", "transferownership", "__ownable_init", "initerc")


@lru_cache(maxsize=1)
def load_taxonomy(path: str | None = None) -> dict:
    p = Path(path) if path else CONFIG
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return {"categories": {}, "high_risk_categories": [], "migration_context_terms": [],
                "migration_file_patterns": [], "state_domain_terms": [], "cross_function_invariants": []}


def _strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.DOTALL)
    text = re.sub(r"//[^\n]*", " ", text)
    return text


def _name_len(name_l: str, patterns: list[str]) -> int:
    best = 0
    for p in patterns:
        pl = p.lower()
        if pl and pl in name_l:
            best = max(best, len(pl))
    return best


def _any(text: str, patterns: list[str]) -> bool:
    return any(p.lower() in text for p in patterns)


def has_migration_context(name: str, file: str, snippet: str = "", signature: str = "",
                          taxonomy: dict | None = None) -> bool:
    tax = taxonomy or load_taxonomy()
    file_l = (file or "").lower()
    if _any(file_l, tax.get("migration_file_patterns", [])):
        return True
    blob = _strip_comments(" ".join([(name or ""), signature or "", snippet or ""])).lower()
    return _any(blob, tax.get("migration_context_terms", []))


def classify(name: str, signature: str = "", file: str = "", contract: str = "",
             snippet: str = "", tags=None, taxonomy: dict | None = None) -> dict:
    tax = taxonomy or load_taxonomy()
    cats = tax.get("categories", {})
    name_l = (name or "").lower()
    body = _strip_comments(" ".join([signature or "", snippet or ""]))
    body_l = body.lower()
    file_l = (file or "").lower()
    hay = " ".join([name_l, body_l, file_l, (contract or "").lower(), " ".join(tags or []).lower()])

    # FP backbone #1: no migration context -> not a migration-flow item at all.
    if not has_migration_context(name, file, snippet, signature, tax):
        return _neg()
    # FP backbone #2: generic ownership-init with no migrated-state signal -> not tagged.
    state_terms = tax.get("state_domain_terms", [])
    has_state = _any(hay, state_terms)
    if any(g in name_l for g in _GENERIC_INIT) and not has_state:
        return _neg()

    hr = set(tax.get("high_risk_categories", []))
    best = None  # (sort_key, cat, meta, matched_on)
    for cat, meta in cats.items():
        nlen = _name_len(name_l, meta.get("name_patterns", []))
        name_hit = nlen > 0
        file_hit = _any(file_l, meta.get("file_patterns", []))
        sv_hit = _any(body_l, [s.lower() for s in meta.get("state_var_patterns", [])])
        call_hit = _any(body_l, [c.lower() for c in meta.get("call_patterns", [])])
        event_hit = any(re.search(r"\b" + re.escape(e) + r"\b", body) for e in meta.get("event_patterns", []))
        signal = name_hit or sv_hit or call_hit or event_hit
        # file_hit alone is weak (a whole reseed file) — needs a name/state/call signal to pick a category
        if not signal:
            continue
        body_sig = sv_hit or call_hit or event_hit
        # Precedence: (1) name specificity (a function literally named setStalk/addMigratedDeposits beats a
        # category that only matched an incidental 'account' state-var); (2) body signal; (3) file context
        # (reseed file -> reseed_initializer over migration_initializer); (4) high-risk.
        key = (nlen, 1 if body_sig else 0, 1 if file_hit else 0, 1 if cat in hr else 0)
        matched_on = ("name" if name_hit else "state_var" if sv_hit else "call" if call_hit
                      else "event" if event_hit else "file")
        if best is None or key > best[0]:
            best = (key, cat, meta, matched_on)

    if best is None:
        return _neg()
    _, cat, meta, matched_on = best
    return {
        "migration_flow_sensitive": True, "category": cat, "risk_tags": list(meta.get("risk_tags", [])),
        "state_domains": list(meta.get("state_domains", [])), "review_hint": meta.get("review_hint", ""),
        "severity_ceiling_hint": meta.get("severity_ceiling_hint"), "matched_on": matched_on,
        "has_state_domain": has_state,
    }


def _neg() -> dict:
    return {"migration_flow_sensitive": False, "category": None, "risk_tags": [], "state_domains": [],
            "review_hint": "", "severity_ceiling_hint": None, "matched_on": None, "has_state_domain": False}


def is_high_risk(classification: dict, taxonomy: dict | None = None) -> bool:
    """High-risk = high-risk category AND a state-domain signal present (the spec's 2-signal rule for
    high-risk: migration context [already required for sensitivity] + a state domain)."""
    tax = taxonomy or load_taxonomy()
    if not classification.get("migration_flow_sensitive"):
        return False
    if not classification.get("has_state_domain"):
        return False
    return classification.get("category") in tax.get("high_risk_categories", [])
