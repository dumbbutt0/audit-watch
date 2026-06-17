#!/usr/bin/env python3
"""
dependency_metadata.py — P178 structured dependency evidence capture (deterministic, no LLM, fail-open).

Converts a coverage clear's prose + the manifest into RESOLVED structured dependency facts so the P177
guarded-downstream router can operate on artifacts instead of prose heuristics. Produces the canonical four
fields {dependency_name, dependency_scope, dependency_status, proof_status} and — only when a real in-scope
artifact resolves — the legacy fields P177's dependency_clear_utils.classify_clear already consumes
(clear_depends_on / dependency_clearance_status / dependency_reason / dependency_evidence), so a resolved
in-scope unreviewed dependency becomes block-eligible under the UNCHANGED P177 rule.

RESOLVE-OR-NOTHING is the core guardrail: a candidate becomes structured metadata only if it (1) looks like a
Solidity identifier (camelCase / underscore / explicit `name(` call), (2) is not a generic category word, and
(3) resolves to a manifest artifact. Generic prose ("guarded downstream", "protected by invariant", "oracle")
resolves to nothing → stays advisory under P177. This module NEVER changes routing semantics and NEVER blocks.
"""
from __future__ import annotations

import re

import dependency_clear_utils as dcu
import math_estimator_taxonomy as _me
import dynamic_weight_lifecycle_taxonomy as _dwl

# Category / connective words that are NOT specific code artifacts (kept advisory even if they slip the
# identifier heuristic). Extends the dcu name-hygiene stoplist with the guarded-downstream vocabulary.
NAME_STOPLIST = set(dcu.GENERIC_DEP_NAME_TOKENS) | {
    "oracle", "invariant", "scope", "guarded", "clamped", "protected", "validated", "downstream", "upstream",
    "estimator", "lifecycle", "sibling", "caller", "callee", "function", "modifier", "before", "after",
    "handled", "mitigated", "bounded", "normalized", "normalised", "checked", "ensured", "enforced",
    "reverts", "owner", "admin", "guardrail", "epsilon", "staleness", "interpolation",
}
# P180: near-generic storage-load / existence-check accessors (plumbing, NOT guards). P179 showed boilerplate
# guard surveys enumerate these (loadLive/loadExisting) and the extractor wrongly resolved them as dependencies.
PLUMBING_HELPERS = {"loadlive", "loadexisting", "getlive", "getexisting"}
NAME_STOPLIST |= PLUMBING_HELPERS

# P180: a clear is boilerplate / out-of-scope / a guard SURVEY when its prose matches these markers — prose
# mined from such a clear is unreliable and must stay advisory (it is not a specific protective-dependency claim).
_BOILERPLATE_PHRASES = ("out of contest", "out-of-contest", "answer-key eligible", "answer key eligible",
                        "not answer-key", "allowlist", "light pass")
_SURVEY_PHRASES = ("guards/invariants identified", "guards identified", "invariants identified",
                   "relevant guards", "existence checks", "access modifiers")

DEPENDENCY_SCOPES = {"same_function", "same_contract", "cross_contract", "out_of_scope", "unknown"}
DEPENDENCY_STATUSES = {"proven", "unreviewed_dependency", "missing"}
PROOF_STATUSES = {"valid", "missing", "not_applicable"}

_PROSE_FIELDS = ("clear_reason", "guard_or_invariant", "no_impact_reason", "dependency_reason")
_IDENT = re.compile(r"_?[A-Za-z][A-Za-z0-9_]{2,}")


def _neg() -> dict:
    return {"dependency_name": None, "dependency_scope": "unknown",
            "dependency_status": "missing", "proof_status": "not_applicable"}


def _prose(disp: dict) -> str:
    return "  ".join(str(disp.get(k) or "") for k in _PROSE_FIELDS)


def _looks_like_identifier(tok: str, text_nospace: str) -> bool:
    """A Solidity-identifier-shaped token: internal uppercase (camelCase), an underscore, or an explicit call."""
    return bool(re.search(r"[A-Z]", tok)) or "_" in tok or (tok + "(") in text_nospace


def _is_generic(name: str) -> bool:
    return dcu._bare(name).lower() in NAME_STOPLIST or name.strip().lower() in NAME_STOPLIST


def _is_boilerplate_or_survey(disp: dict, manifest_index: dict) -> bool:
    """P180: True when the clear is a boilerplate / out-of-scope disposition or an enumerated guard SURVEY —
    prose mined from such a clear is not a specific protective-dependency claim and must stay advisory.
    (Gated by the caller to prose-mining only: an explicit clear_depends_on is still honored.)"""
    blob = _prose(disp).lower()
    if any(p in blob for p in _BOILERPLATE_PHRASES) or any(p in blob for p in _SURVEY_PHRASES):
        return True
    item = (manifest_index or {}).get(disp.get("manifest_id")) or {}
    nm = (item.get("name") or "").strip().lower()
    if nm == "constructor" or nm.startswith("_authorizeupgrade") or item.get("kind") == "constant":
        return True
    return False


def mine_candidate_names(disp: dict) -> list[str]:
    """Identifier-shaped, non-generic tokens from the clear prose (or the explicit clear_depends_on list)."""
    explicit = disp.get("clear_depends_on")
    if explicit:
        return [str(x) for x in explicit]
    text = _prose(disp)
    text_nospace = re.sub(r"\s+", "", text)
    out, seen = [], set()
    for m in _IDENT.finditer(text):
        tok = m.group(0)
        if _is_generic(tok) or not _looks_like_identifier(tok, text_nospace):
            continue
        if tok not in seen:
            seen.add(tok); out.append(tok)
    return out


def _resolve_ids(name: str, manifest_index: dict, name_index: dict) -> list[str]:
    if name in manifest_index:
        return [name]
    return list(name_index.get(dcu._bare(name), []))


def _scope(disp: dict, dep_id: str, manifest_index: dict) -> str:
    dep = manifest_index.get(dep_id)
    if not dep:
        return "unknown"
    if dep.get("in_scope") is False:
        return "out_of_scope"
    own = manifest_index.get(disp.get("manifest_id"))
    if not own:
        return "cross_contract"
    if own.get("contract") == dep.get("contract"):
        return "same_function" if dcu._bare(own.get("name") or "") == dcu._bare(dep.get("name") or "") \
            else "same_contract"
    return "cross_contract"


_STATUS_MAP = {
    "all_cleared": "proven", "finding_linked": "proven", "out_of_scope_dependency": "proven",
    "unreviewed_dependency": "unreviewed_dependency", "partially_cleared": "unreviewed_dependency",
    "unknown_dependency": "missing",
}


def _proof(disp: dict, dep_id: str, manifest_index: dict) -> str:
    # a valid recorded proof on the cleared item closes it
    mep = disp.get("math_estimator_proof")
    lcp = disp.get("dynamic_weight_lifecycle_proof")
    try:
        import validate_math_estimator_clears as _vme
        import validate_dynamic_weight_lifecycle_clears as _vdwl
        if mep and _vme.validate_proof(mep)[0] == "math_proof_valid":
            return "valid"
        if lcp and _vdwl.validate_proof(lcp)[0] == "lifecycle_proof_valid":
            return "valid"
    except Exception:  # noqa: BLE001 — fail-open
        pass
    dep = manifest_index.get(dep_id) or {}
    try:
        needs = (_me.classify_manifest_item(dep).get("math_estimator_sensitive")
                 or _dwl.classify_manifest_item(dep).get("lifecycle_sensitive"))
    except Exception:  # noqa: BLE001
        needs = False
    return "missing" if needs else "not_applicable"


def _dep_evidence(dep_id: str, manifest_index: dict) -> list[str]:
    dep = manifest_index.get(dep_id) or {}
    span = dep.get("source_span") or {}
    f = dep.get("file")
    if f and span.get("start_line"):
        return [f"{f}:{span.get('start_line')}-{span.get('end_line', span.get('start_line'))}"]
    return []


def extract_dependency_metadata(disp: dict, manifest_index: dict | None = None,
                                name_index: dict | None = None,
                                disposition_index: dict | None = None) -> dict:
    """Resolve structured dependency facts for a clear. Returns the canonical four fields always, plus the
    bridged legacy fields when (and only when) a real in-scope artifact resolves. Fail-open: any error or
    non-resolution yields the canonical 'nothing resolved' result (→ advisory under P177)."""
    manifest_index = manifest_index or {}
    name_index = name_index or {}
    disposition_index = disposition_index or {}
    try:
        # P180: prose mined from a boilerplate / out-of-scope clear or an enumerated guard SURVEY is not a
        # specific dependency claim → stay advisory. An EXPLICIT clear_depends_on (genuine structured input)
        # bypasses this and is still honored.
        if not disp.get("clear_depends_on") and _is_boilerplate_or_survey(disp, manifest_index):
            return _neg()
        cands = [c for c in mine_candidate_names(disp) if not _is_generic(c)]
        resolved = [(c, ids[0]) for c in cands for ids in [_resolve_ids(c, manifest_index, name_index)] if ids]
        if not resolved:
            return _neg()                                   # RESOLVE-OR-NOTHING → advisory
        name, dep_id = resolved[0]
        all_names = [c for c, _ in resolved]
        clr = dcu.resolve_dependency_status(all_names, disposition_index, name_index)
        meta = {
            "dependency_name": dcu._bare(name),
            "dependency_scope": _scope(disp, dep_id, manifest_index),
            "dependency_status": _STATUS_MAP.get(clr, "missing"),
            "proof_status": _proof(disp, dep_id, manifest_index),
        }
        if clr != "unknown_dependency":
            # bridge to the legacy fields P177's classify_clear consumes (no routing-rule change)
            meta["clear_depends_on"] = [dep_id]
            meta["dependency_clearance_status"] = clr
            meta["dependency_reason"] = (disp.get("clear_reason")
                                         or f"auto-extracted: leans on {meta['dependency_name']}")[:300]
            ev = _dep_evidence(dep_id, manifest_index)
            if ev:
                meta["dependency_evidence"] = ev
        return meta
    except Exception:  # noqa: BLE001 — fail-open, never raise, never block
        return _neg()


def validate_dependency_metadata(meta: dict) -> str:
    """Report the capture quality of one metadata dict (read-only verdict)."""
    name = meta.get("dependency_name")
    if not name:
        return "dependency_name_unresolved"
    if _is_generic(name):
        return "generic_dependency_name"
    if meta.get("dependency_scope") in (None, "unknown") or meta.get("dependency_status") in (None, "missing"):
        return "metadata_incomplete"
    return "metadata_complete"
