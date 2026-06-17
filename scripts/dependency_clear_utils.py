#!/usr/bin/env python3
"""
dependency_clear_utils.py — shared logic for the dependency-aware clear policy (deterministic, no LLM).

A coverage "clear" must not rely on an *unreviewed* downstream dependency (guard / estimator / oracle /
math rule / invariant / lifecycle check). A dependency is a proof only if it is itself finding-linked,
deeply reviewed with evidence, strongly cleared with its own evidence, or out of scope. This module is
the single source of truth used by both validate_dependency_clears.py and the writer enforcement in
coverage_sweep_write.py / deep_pass_write.py, so detection/resolution never drifts between them.

Motivation: the QuantAMM 2024-12 fresh blind eval over-cleared rule-math/guard/estimator functions with
reasoning like "outputs pass through _guardQuantAMMWeights … before setWeights" — but those guards were
themselves in-scope and unproven, and held missed bugs. See documentation/dependency_clear_policy.md.
"""
from __future__ import annotations

import re

# Phrases/tokens that indicate a clear is leaning on another component to absorb the threat.
# Lower-cased substring match against the clear text. Kept conservative but broad (advisory by default).
DEP_PHRASES = [
    "guarded downstream", "checked later", "validated later", "validated by", "validated at registration",
    "bounded by", "protected by", "prevented by", "enforced by", "handled by", "handled downstream",
    "downstream guard", "downstream", "before setweights", "passes through", "pass through",
    "clamped by", "normalized by", "normalised by", "absorbed by", "caught by", "mitigated by",
]
# Single tokens (whole-word match) that name a typical dependency component.
DEP_TOKENS = [
    "_guardquantammweights", "mathguard", "estimator", "oracle", "guard", "invariant", "lifecycle",
    "interpolation", "covariance", "variance", "gradient", "guardrail", "guard rail", "guard-rail",
    "weight guard", "epsilon", "staleness", "clamp",
]

# Map a named token to its likely downstream_guard_type (best-effort, for reporting only).
_TYPE_HINTS = [
    (("oracle", "staleness", "chainlink", "latestrounddata"), "oracle"),
    (("estimator", "covariance", "variance", "gradient", "moving average", "ewma"), "estimator"),
    (("mathguard", "_guardquantammweights", "guard", "guardrail", "guard rail", "clamp", "epsilon"), "guard"),
    (("invariant",), "invariant"),
    (("lifecycle", "interpolation", "staleness", "updateinterval"), "lifecycle_check"),
    (("bound", "int32", "int128", "overflow", "underflow"), "bounds_check"),
    (("onlyowner", "onlyadmin", "onlymanager", "msg.sender", "access"), "access_control"),
]

# Dependency-clearance status values (metadata, NOT a disposition status).
DEP_CLEARANCE_OK = {"all_cleared", "finding_linked", "out_of_scope_dependency"}
DEP_CLEARANCE_BAD = {"unreviewed_dependency", "unknown_dependency"}
DEP_CLEARANCE_PARTIAL = {"partially_cleared"}

# P177 clear-time evidence shortcuts: a clear whose dependency carries a VALID proof is closed (non-blocking),
# and an auditor-declared OUT-OF-SCOPE dependency does not meet the "in-scope unproven guard" bar to block.
PROOF_OK = {"valid", "proven", "math_proof_valid", "lifecycle_proof_valid"}
DEP_SCOPE_OOS = {"out_of_scope", "oos", "deferred_out_of_scope", "out-of-scope"}

# Disposition statuses that count as "this dependency has actually been reviewed".
_REVIEWED_STATUSES = {"cleared", "finding", "deferred_out_of_scope"}

_REQUIRED_DEP_FIELDS = ["clear_depends_on", "dependency_clearance_status", "dependency_reason", "dependency_evidence"]

# --- Finding-linked escape ----------------------------------------------------------------------
# A dependency-based clear is non-blocking when it is explicitly anchored to an EXISTING finding: the
# dependency (the bug) has already been reviewed and filed, so leaning on it is not circular. This is
# evidence-anchored — either a structured finding-ref field or a concrete finding id in the prose.
FINDING_REF_FIELDS = ["finding_refs", "finding_ref", "duplicate_of", "related_finding"]
# Concrete Audit-Watch finding/report id, e.g. DT-003, DPF-036, EVAL-001, GOR-001, CHAIN-001, H-01.
_FINDING_ID_RE = re.compile(r"\b[A-Z]{1,5}-\d{2,4}\b")
# Prefixes that match the id shape but name a standard/token (NOT a finding) — guards against ERC-20,
# EIP-1153, CWE-841, etc. being misread as finding links.
_FINDING_ID_EXCLUDE = {"ERC", "EIP", "BIP", "SIP", "CWE", "CVE", "RFC", "ISO", "SHA", "UTF", "AES", "RSA"}

# Generic words that must NEVER be emitted as a dependency *name* (report hygiene). They still trigger
# dependency-based phrase/token detection in is_dependency_based_clear — only name extraction is filtered.
GENERIC_DEP_NAME_TOKENS = {
    "require", "assert", "revert", "zero", "path", "check", "validate", "validation",
    "guard", "math", "condition", "bounds", "later", "downstream",
}

# function-name-ish token: optional leading underscore + identifier, used either as name( or bare name.
_FN_RE = re.compile(r"(_?[A-Za-z][A-Za-z0-9_]{2,})")


def _clear_text(disp: dict) -> str:
    """Concatenate the human-readable fields where dependency language would appear."""
    parts = [disp.get("clear_reason") or "", disp.get("guard_or_invariant") or "",
             disp.get("no_impact_reason") or "", disp.get("dependency_reason") or ""]
    return "  ".join(str(p) for p in parts).lower()


def required_dependency_fields() -> list[str]:
    return list(_REQUIRED_DEP_FIELDS)


def is_finding_linked_clear(disp: dict) -> bool:
    """True if the clear is explicitly anchored to an existing finding — via a structured finding-ref
    field, or a concrete finding id (e.g. DT-003 / DPF-036) in clear_reason / dependency_reason /
    evidence. A finding IS a completed review, so such a dependency is non-blocking. Standard/token ids
    (ERC-20, EIP-1153, CWE-841, …) are excluded so they don't masquerade as finding links."""
    for f in FINDING_REF_FIELDS:
        if disp.get(f):  # non-empty list or string
            return True
    parts = [str(disp.get("clear_reason") or ""), str(disp.get("dependency_reason") or "")]
    ev = disp.get("evidence")
    if ev:
        parts += [str(x) for x in (ev if isinstance(ev, (list, tuple)) else [ev])]
    text = "  ".join(parts)
    for m in _FINDING_ID_RE.finditer(text):
        if m.group(0).split("-", 1)[0] not in _FINDING_ID_EXCLUDE:
            return True
    return False


def is_dependency_based_clear(disp: dict) -> bool:
    """True if this clear relies on another component (by explicit flag or by language)."""
    if disp.get("downstream_guard_claim") is True:
        return True
    if disp.get("clear_depends_on"):
        return True
    text = _clear_text(disp)
    if not text.strip():
        return False
    for ph in DEP_PHRASES:
        if ph in text:
            return True
    # whole-word token match (avoid matching "guard" inside unrelated words handled by \b)
    for tok in DEP_TOKENS:
        if " " in tok or "-" in tok or tok.startswith("_"):
            if tok in text:
                return True
        elif re.search(r"\b" + re.escape(tok) + r"\b", text):
            return True
    return False


def guess_guard_type(disp: dict) -> str:
    text = _clear_text(disp)
    for toks, typ in _TYPE_HINTS:
        if any(t in text for t in toks):
            return typ
    return "other"


def extract_dependency_names(disp: dict) -> list[str]:
    """Names of the dependencies a clear leans on. Prefer the explicit clear_depends_on list; else mine
    the clear text for function-name-ish tokens that look like dependencies (calls, or known guard names)."""
    explicit = disp.get("clear_depends_on")
    if explicit:
        return [str(x) for x in explicit]
    text = " ".join(str(disp.get(k) or "") for k in ("clear_reason", "guard_or_invariant", "no_impact_reason"))
    names: list[str] = []
    # 1) explicit calls  foo(   /  _bar(
    for m in re.finditer(r"(_?[A-Za-z][A-Za-z0-9_]{2,})\s*\(", text):
        names.append(m.group(1))
    # 2) known guard/estimator tokens mentioned by name
    low = text.lower()
    for known in ("_guardQuantAMMWeights", "validParameters", "setWeights", "MathGuard"):
        if known.lower() in low and known not in names:
            names.append(known)
    # dedupe, preserve order; drop generic words that are not real dependency names (report hygiene)
    seen, out = set(), []
    for n in names:
        if n.lower() in GENERIC_DEP_NAME_TOKENS:
            continue
        if n not in seen:
            seen.add(n); out.append(n)
    return out


def _bare(name: str) -> str:
    """Reduce a manifest_id or qualified name to a bare function name for matching."""
    n = name
    if ":" in n and "#" in n:  # manifest_id: kind:contract:name#hash
        try:
            n = n.split(":", 2)[2].split("#", 1)[0]
        except IndexError:
            pass
    if "." in n:
        n = n.rsplit(".", 1)[-1]
    return n.strip().lower()


def build_manifest_name_index(manifest_items: list[dict]) -> dict[str, list[str]]:
    """bare-name (lowercased) -> list of manifest_ids that define a function/var with that name."""
    idx: dict[str, list[str]] = {}
    for it in manifest_items:
        nm = (it.get("name") or "").strip().lower()
        if nm:
            idx.setdefault(nm, []).append(it["id"])
    return idx


def _dependency_is_reviewed(dep_disp: dict | None) -> bool:
    """A dependency counts as reviewed only if it has a real disposition AND, when 'cleared', its own
    clear is evidence-backed and is NOT itself a tainted dependency-clear (one level of transitive guard —
    blocks A→B→A laundering)."""
    if not dep_disp:
        return False
    st = dep_disp.get("status")
    if st not in _REVIEWED_STATUSES:
        return False
    if st == "cleared":
        if not dep_disp.get("evidence"):
            return False
        # Laundering guard (A→B→A): if the dependency's OWN clear EXPLICITLY declares it leans on a
        # further dependency, only trust it when that further dependency was resolved OK. We use the
        # explicit signals (downstream_guard_claim / clear_depends_on) rather than loose prose tokens,
        # so a genuinely terminal reviewed guard whose text merely mentions "clamp"/"guard" still counts.
        explicit_dep = bool(dep_disp.get("downstream_guard_claim")) or bool(dep_disp.get("clear_depends_on"))
        if explicit_dep:
            return dep_disp.get("dependency_clearance_status") in DEP_CLEARANCE_OK
    return True


def resolve_dependency_status(names: list[str], disposition_index: dict[str, dict],
                              manifest_name_index: dict[str, list[str]]) -> str:
    """Fold the named dependencies into one dependency_clearance_status.

    disposition_index: manifest_id -> disposition dict.
    manifest_name_index: bare-name -> [manifest_id, ...] (from build_manifest_name_index).
    """
    if not names:
        return "unknown_dependency"
    resolved_reviewed = 0
    resolved_total = 0
    any_finding = False
    any_oos = False
    any_unresolved = False
    any_unreviewed = False
    for raw in names:
        # direct manifest_id hit?
        ids: list[str] = []
        if raw in disposition_index:
            ids = [raw]
        else:
            ids = manifest_name_index.get(_bare(raw), [])
        if not ids:
            any_unresolved = True
            continue
        resolved_total += 1
        # if ANY definition of that name is reviewed, treat the dependency as reviewed.
        dep_dispositions = [disposition_index.get(i) for i in ids]
        if any(d and d.get("status") == "finding" for d in dep_dispositions):
            any_finding = True; resolved_reviewed += 1; continue
        if any(d and d.get("status") == "deferred_out_of_scope" for d in dep_dispositions):
            any_oos = True; resolved_reviewed += 1; continue
        if any(_dependency_is_reviewed(d) for d in dep_dispositions):
            resolved_reviewed += 1
        else:
            any_unreviewed = True
    if any_unresolved and resolved_total == 0:
        return "unknown_dependency"
    if any_unresolved:
        # some names couldn't be resolved at all → treat as unknown (conservative)
        return "unknown_dependency"
    if any_unreviewed:
        return "unreviewed_dependency"
    if resolved_reviewed == resolved_total and resolved_total > 0:
        if any_finding and resolved_reviewed == 1 and resolved_total == 1:
            return "finding_linked"
        return "all_cleared" if not any_oos or resolved_total > 1 else "out_of_scope_dependency"
    if resolved_reviewed > 0:
        return "partially_cleared"
    return "unreviewed_dependency"


def check_dependency_metadata(disp: dict) -> list[str]:
    """Return the list of required dependency-metadata fields that are missing/empty."""
    missing = []
    for f in _REQUIRED_DEP_FIELDS:
        v = disp.get(f)
        if v is None or (isinstance(v, (list, str)) and len(v) == 0):
            missing.append(f)
    return missing


# --- locality / path-dominance ------------------------------------------------------------------
# A dependency clear that leans on a guard in a DIFFERENT function/contract is only valid if that
# guard DOMINATES every attacker-reachable path to the sensitive operation. A guard "somewhere" is
# not a guard "on every path" (Swan/Dria H-02: Swan.purchase's missing local round check was cleared
# by leaning on BuyerAgent's phase guard in another contract, but purchase is directly callable).
_DOMINATING_LOCALITY = {"same_contract_dominates", "cross_contract_dominates"}
_LOCALITY_FIELDS = ["guard_locality", "path_dominance_evidence", "alternative_paths_considered"]


def _resolve_guard_items(names: list[str], manifest_name_index: dict[str, list[str]],
                         manifest_index: dict[str, dict]) -> list[dict]:
    """Manifest items for the named dependencies (best-effort)."""
    items, seen = [], set()
    for raw in names:
        ids = [raw] if raw in manifest_index else manifest_name_index.get(_bare(raw), [])
        for i in ids:
            it = manifest_index.get(i)
            if it and i not in seen:
                seen.add(i); items.append(it)
    return items


def _call_adjacency(call_graph: dict) -> dict[str, set]:
    """bare-callee-name set keyed by bare-caller-name, from call_graph['call_graph'][]."""
    adj: dict[str, set] = {}
    for e in (call_graph or {}).get("call_graph", []):
        caller = _bare(e.get("caller_function") or "")
        callee = _bare(e.get("callee_function") or "")
        if caller and callee:
            adj.setdefault(caller, set()).add(callee)
    return adj


def _reaches(adj: dict[str, set], src: str, dst: str, blocked: set) -> bool:
    """True if dst is reachable from src following edges, never traversing a blocked node.
    src==dst returns True (the entry IS the sink — directly callable)."""
    if src in blocked:
        return False
    if src == dst:
        return True
    stack, seen = [src], {src}
    while stack:
        n = stack.pop()
        for m in adj.get(n, ()):  # noqa: E1133
            if m in blocked or m in seen:
                continue
            if m == dst:
                return True
            seen.add(m); stack.append(m)
    return False


def find_nondominated_entry(call_graph: dict, sink_fn: str, guard_fns: set,
                            public_entries: set) -> str | None:
    """Return an attacker-reachable entry that reaches sink_fn WITHOUT passing through any guard
    (dominance disproven), else None. Sound for blocking, NOT complete — tuned for near-zero false
    positives, because the call graph does not encode intra-function ordering:
      - if the sink itself calls a guard (edge sink→guard) the sink body is locally protected → None;
      - an entry that ALSO calls a guard directly is given the benefit of the doubt (it may call the
        guard before the sink in the same body) and is NOT treated as a bypass.
    This still catches the Swan/Dria H-02 shape (a public sink directly callable without the guard) and
    proxy/router/alternative entries that reach the sink on a guard-free path."""
    sink = _bare(sink_fn)
    guards = {_bare(g) for g in guard_fns if g}
    if not sink or not guards:
        return None
    adj = _call_adjacency(call_graph)
    if adj.get(sink, set()) & guards:  # sink calls a guard itself → locally protected
        return None
    # attacker entries = public/external functions (a public SINK is among them and is its own entry —
    # the H-02 shape). If visibility is unknown, fall back to graph roots (callers never called).
    entries = {_bare(e) for e in public_entries}
    if not entries:
        callees = set().union(*adj.values()) if adj else set()
        entries = set(adj) - callees
    for entry in entries:
        if entry in guards or (adj.get(entry, set()) & guards):
            continue  # the entry is/uses a guard → ordering unknown, do not disprove
        if _reaches(adj, entry, sink, guards):
            return entry
    return None


def _public_entries(manifest_index: dict[str, dict]) -> set:
    """Bare names of public/external functions (attacker entry points)."""
    out = set()
    for it in (manifest_index or {}).values():
        if it.get("kind") == "function" and str(it.get("visibility", "")).lower() in ("public", "external"):
            out.add(_bare(it.get("name") or ""))
    out.discard("")
    return out


def check_locality(disp: dict, names: list[str], manifest_index: dict[str, dict],
                   manifest_name_index: dict[str, list[str]], call_graph: dict | None) -> str | None:
    """Return a reason string if an otherwise-valid dependency clear FAILS path-dominance, else None.
    Only enforced when manifest_index is provided AND the guard resolves to a different function/
    contract than the cleared item (conservative: never over-blocks a same-function/local guard)."""
    if not manifest_index:
        return None
    sink_item = manifest_index.get(disp.get("manifest_id"))
    if not sink_item:
        return None
    sink_fn, sink_contract = _bare(sink_item.get("name") or ""), sink_item.get("contract")
    guard_items = _resolve_guard_items(names, manifest_name_index, manifest_index)
    non_local = any((g.get("contract") != sink_contract) or (_bare(g.get("name") or "") != sink_fn)
                    for g in guard_items)
    if not non_local:
        return None  # guard is local (same function) or unresolved → don't enforce dominance
    locality = disp.get("guard_locality")
    if locality == "non_local":
        return "guard explicitly declared non_local — a non-local guard cannot clear a missing local check"
    if locality not in _DOMINATING_LOCALITY:
        return ("non-local guard requires guard_locality in {same_contract_dominates, "
                "cross_contract_dominates} with path_dominance_evidence")
    if not disp.get("path_dominance_evidence"):
        return "non-local guard requires path_dominance_evidence (proof every attacker-reachable path passes the guard)"
    if not disp.get("alternative_paths_considered"):
        return ("non-local guard requires alternative_paths_considered (proxy/router/callback/batch/"
                "delegatecall paths + parameter immutability between guard and sink)")
    # call-graph disproof: if an attacker entry reaches the sink without the guard, dominance is false.
    if call_graph:
        guard_fns = {g.get("name") for g in guard_items if g.get("name")}
        bypass = find_nondominated_entry(call_graph, sink_fn, guard_fns, _public_entries(manifest_index))
        if bypass:
            return (f"call graph disproves dominance: '{bypass}' reaches {sink_fn} without passing through "
                    f"the guard ({sorted(guard_fns)[:3]})")
    return None


def classify_clear(disp: dict, disposition_index: dict[str, dict],
                   manifest_name_index: dict[str, list[str]],
                   manifest_index: dict[str, dict] | None = None,
                   call_graph: dict | None = None) -> dict:
    """Classify one cleared disposition. Returns {status, dependency_based, names, clearance_status,
    missing_metadata, guard_type, locality_reason}.

    status ∈ not_dependency_based | dependency_valid | finding_linked_dependency |
             missing_dependency_metadata | unreviewed_dependency | unknown_dependency |
             dependency_evidence_missing | guard_not_path_dominant

    Locality (guard_not_path_dominant) is only evaluated when manifest_index is supplied AND the guard
    resolves to a different function/contract; otherwise the prior behavior is byte-identical.
    """
    if not is_dependency_based_clear(disp):
        return {"status": "not_dependency_based", "dependency_based": False, "names": [],
                "clearance_status": None, "missing_metadata": [], "guard_type": None, "locality_reason": None}
    names = extract_dependency_names(disp)
    guard_type = disp.get("downstream_guard_type") or guess_guard_type(disp)
    # finding-linked escape: a clear anchored to an existing finding is non-blocking (the dependency —
    # the bug — has already been reviewed and filed). Takes priority over missing-metadata.
    if is_finding_linked_clear(disp):
        return {"status": "finding_linked_dependency", "dependency_based": True, "names": names,
                "clearance_status": "finding_linked", "computed_clearance": "finding_linked",
                "missing_metadata": [], "guard_type": guard_type, "locality_reason": None}
    # P177 clear-time evidence shortcuts (additive — absent fields leave prior behavior byte-identical):
    # an auditor-declared OUT-OF-SCOPE dependency does not meet the "in-scope unproven guard" bar (non-blocking);
    # a dependency carrying a VALID proof is closed (non-blocking).
    if str(disp.get("dependency_scope") or "").lower() in DEP_SCOPE_OOS:
        return {"status": "out_of_scope_dependency", "dependency_based": True, "names": names,
                "clearance_status": "out_of_scope_dependency", "computed_clearance": "out_of_scope_dependency",
                "missing_metadata": [], "guard_type": guard_type, "locality_reason": None}
    if str(disp.get("proof_status") or "").lower() in PROOF_OK:
        return {"status": "dependency_valid", "dependency_based": True, "names": names,
                "clearance_status": "proven", "computed_clearance": "proven",
                "missing_metadata": [], "guard_type": guard_type, "locality_reason": None}
    missing = check_dependency_metadata(disp)
    # evidence for the dependency specifically
    dep_evidence_missing = not disp.get("dependency_evidence")
    # resolved clearance status: prefer the recorded one, else compute it
    clearance = disp.get("dependency_clearance_status")
    computed = resolve_dependency_status(names, disposition_index, manifest_name_index)
    if not clearance:
        clearance = computed
    locality_reason = None
    if missing:
        st = "missing_dependency_metadata"
    elif clearance in DEP_CLEARANCE_BAD:
        st = "unreviewed_dependency" if clearance == "unreviewed_dependency" else "unknown_dependency"
    elif dep_evidence_missing:
        st = "dependency_evidence_missing"
    else:
        # the dependency is reviewed AND evidenced — now require it to DOMINATE the sink's paths.
        locality_reason = check_locality(disp, names, manifest_index, manifest_name_index, call_graph)
        st = "guard_not_path_dominant" if locality_reason else "dependency_valid"
    return {"status": st, "dependency_based": True, "names": names,
            "clearance_status": clearance, "computed_clearance": computed,
            "missing_metadata": missing, "guard_type": guard_type, "locality_reason": locality_reason}


# LEGACY blocking set (flag-off path): every dependency-based status that historically hard-routed, including
# the prose-only/incomplete `missing_dependency_metadata` and unresolvable `unknown_dependency`.
BLOCKING_CLASSIFICATIONS = {
    "missing_dependency_metadata", "unreviewed_dependency", "unknown_dependency",
    "dependency_evidence_missing",
}
# locality blocking is gated by a separate config flag (dependency_locality_strict[_full_audit]) so it
# can be tuned independently; writers/validator union it in when the locality flag is effective.
LOCALITY_BLOCKING = {"guard_not_path_dominant"}

# --- P177: precision-tightened routing ----------------------------------------------------------
# Hard-route ONLY when complete structured metadata resolves a genuine in-scope, unproven downstream guard.
# These two statuses are reachable only when all required dependency fields are present (see classify_clear).
STRUCTURED_BLOCKING = {"unreviewed_dependency", "dependency_evidence_missing"}
# Dependency-based but NOT adjudicable to an in-scope unproven guard → advisory, never a hard route:
#   missing_dependency_metadata  (prose-only OR structured-but-incomplete claim)
#   unknown_dependency           (named dependency does not resolve to an in-scope manifest item)
ADVISORY_CLASSIFICATIONS = {"missing_dependency_metadata", "unknown_dependency"}
# Non-blocking outcomes (clear stands).
ALLOW_CLASSIFICATIONS = {"not_dependency_based", "dependency_valid", "finding_linked_dependency",
                         "out_of_scope_dependency"}


def dependency_signal_source(disp: dict) -> str:
    """How the dependency was detected: 'structured' (explicit downstream_guard_claim / clear_depends_on),
    'prose' (only clear-text phrases/tokens), or 'none'. Used to keep prose-only mentions out of hard-routing."""
    if disp.get("downstream_guard_claim") is True or disp.get("clear_depends_on"):
        return "structured"
    if is_dependency_based_clear(disp):
        return "prose"
    return "none"


def dependency_route_decision(cls: dict, disp: dict | None = None, locality_on: bool = False,
                              require_structured: bool = True) -> str:
    """Single source of truth for what a dependency-based clear should do: 'block' | 'advisory' | 'allow'.

    require_structured (P177 default, config `guarded_downstream_require_structured`): hard-route ONLY on
    STRUCTURED_BLOCKING (+ locality) — i.e. complete structured metadata resolving an in-scope unproven guard.
    Prose-only / incomplete / unresolvable detections (`missing_dependency_metadata`, `unknown_dependency`) are
    advisory, never a hard route. require_structured=False restores the LEGACY blocking set.
    """
    st = cls.get("status")
    if st in ALLOW_CLASSIFICATIONS:
        return "allow"
    block_set = (STRUCTURED_BLOCKING if require_structured else BLOCKING_CLASSIFICATIONS)
    block_set = block_set | (LOCALITY_BLOCKING if locality_on else set())
    if st in block_set:
        return "block"
    return "advisory"
