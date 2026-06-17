#!/usr/bin/env python3
"""
asset_source_consistency_taxonomy.py — classify asset-source / amount-origin consistency risk in one
function: which asset-source FAMILIES (collateral / supply / native / token) it references, what it
transfers from, and whether the transfer source differs from the amount's origin family. Two-signal,
FP-tight. Mirrors recipient_custody_taxonomy. Derived from Recall H-05 and DT-002.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "config" / "asset_source_consistency_patterns.json"


@lru_cache(maxsize=1)
def load_taxonomy(path: str | None = None) -> dict:
    p = Path(path) if path else CONFIG
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return {"source_families": {}, "transfer_call_signals": [], "accounting_signals": [], "categories": {}}


def _strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.DOTALL)
    return re.sub(r"//[^\n]*", " ", text)


def _hit(text: str, patterns: list[str]) -> bool:
    for p in patterns or []:
        try:
            if re.search(p, text):
                return True
        except re.error:
            if p.lower() in text.lower():
                return True
    return False


def families_referenced(body: str, tax: dict) -> set[str]:
    fams = set()
    for fam, pats in (tax.get("source_families") or {}).items():
        if _hit(body, pats):
            fams.add(fam)
    return fams


def transfer_sources(body: str, tax: dict) -> set[str]:
    """The object names that funds are transferred/locked FROM (e.g. {collateralSource})."""
    srcs = set()
    for p in tax.get("transfer_call_signals", []):
        for m in re.finditer(p, body):
            if m.groups():
                srcs.add(m.group(1))
    return srcs


def _family_of(obj_name: str, tax: dict) -> str | None:
    for fam, pats in (tax.get("source_families") or {}).items():
        for p in pats:
            try:
                if re.search(p, obj_name):
                    return fam
            except re.error:
                if p.lower() in obj_name.lower():
                    return fam
    return None


def classify(name: str, signature: str = "", file: str = "", contract: str = "",
             snippet: str = "", tags=None, taxonomy: dict | None = None) -> dict:
    tax = taxonomy or load_taxonomy()
    body = _strip_comments(" ".join([signature or "", snippet or ""]))
    fams = families_referenced(body, tax)
    tsrcs = transfer_sources(body, tax)
    transfer_fams = {_family_of(s, tax) for s in tsrcs} - {None}
    has_accounting = _hit(body, tax.get("accounting_signals", []))
    # mismatch candidate: the function references >=2 source families AND transfers/locks (so two asset
    # domains are mixed in one function with a movement). The deep pass must confirm the amount's origin
    # family equals the transfer source family.
    sensitive = len(fams) >= 2 and (bool(tsrcs) or has_accounting)
    return {
        "asset_source_sensitive": sensitive,
        "families": sorted(fams),
        "transfer_sources": sorted(tsrcs),
        "transfer_families": sorted(transfer_fams),
        "has_accounting": has_accounting,
        "category": "source_family_mismatch" if sensitive else None,
        "severity_ceiling_hint": (tax.get("categories", {}).get("source_family_mismatch", {})
                                  .get("severity_ceiling_hint", "High") if sensitive else None),
    }


def is_high_risk(classification: dict, taxonomy: dict | None = None) -> bool:
    """High-risk = >=2 distinct asset-source families mixed in a function that moves funds, AND the transfer
    source family is not the only family present (so a cross-family payout is possible — the H-05 shape)."""
    if not classification.get("asset_source_sensitive"):
        return False
    fams = set(classification.get("families") or [])
    tfams = set(classification.get("transfer_families") or [])
    # transfer happens from one family while >=1 other family (the likely amount origin) is also present
    return len(fams) >= 2 and (not tfams or bool(fams - tfams) or len(tfams) >= 1)
