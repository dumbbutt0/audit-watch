#!/usr/bin/env python3
"""
validate_deep_pass_mechanisms.py — P183 ADVISORY checker (read-only) for deep-trace mechanism-enumeration.

A deep-trace output on a hot/routed surface should enumerate multiple plausible mechanisms before choosing one
(prompts/deep_trace.md STEP 0/5/6). This checker reports — per deep-trace finding — whether it carries the
mechanism-enumeration fields, so missing fields are VISIBLE. It is ADVISORY: it never blocks, never changes
severity/routing/submission, never mutates dispositions. Mirrors validate_dependency_clears.py.

Usage: python scripts/validate_deep_pass_mechanisms.py [--quiet]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402

REQUIRED = ["mechanism_inventory", "rejection_table", "chosen_mechanism", "impact_direction", "stop_condition"]
_IMPACT_KEYS = ("attacker_receives", "attacker_preserves", "victim_loses", "invariant_violated")
# P185: a who-loses/who-gains value that means "no real impact" (so it is a legitimate rejection, not a demotion).
_EMPTY_IMPACT = {"", "none", "n/a", "na", "nobody", "no one", "n.a."}

# ---------------------------------------------------------------------------------------------------------------
# P188 adjudication-support detectors (ADVISORY). Native port of the P187 research rubric
# (scripts/research/adjudication_rubric.py stays UN-WIRED — it is NOT imported here). Both detectors only make a
# mis-targeted rejection VISIBLE: they never block, never set severity/routing/submission, never mint findings.
# They run only on `rejected_mechanisms` rows, so a selected/unresolved (carried) mechanism is never flagged.
# ---------------------------------------------------------------------------------------------------------------
import re  # noqa: E402

# Part B — a rejection that rebuts only a fund-loss/High bar.
_HIGH_BAR_TOKENS = ("not fund-loss", "not fund loss", "no fund loss", "no funds", "not theft", "not stolen",
                    "dos not fund", "liveness/dos not", "not high", "not a fund", "no fund-loss")
# Part B — a genuine Medium-class impact (DoS / griefing / unavailability / permanent block).
_MEDIUM_IMPACT_TOKENS = ("dos", "denial", "liveness", "lockout", "lock ", "locked", "unavailable", "brick",
                         "permanently", "blocked", "no timely", "frozen", "stuck", "grief", "cannot ",
                         "revert")
# Part B — a NON-impact reason (legitimate Low/no-impact rejection) — keeps reject-first discipline intact.
_NON_IMPACT_TOKENS = ("dust", "self-fund", "self fund", "self-funded", "no victim", "nobody")
# Identifier shape for a "distinctive locus" — camelCase, snake/underscore, or dotted member, length>=6.
_IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*")
# Plain English words that are identifier-shaped but not loci (avoid false "distinctive identifier").
_IDENT_STOPWORDS = {"mechanism", "external", "function", "internal", "reentrancy", "accounting", "snapshot",
                    "precision", "invariant", "underflow", "overflow", "rejection", "attacker", "withdrawal",
                    "lifecycle", "ordering", "callback", "modifier", "constructor", "control", "direction",
                    "propagates", "propagate", "documented", "dimensionally", "consistent"}


def _words(s) -> set:
    return {w for w in re.split(r"[^a-z0-9]+", str(s or "").lower()) if w}


def _distinctive_identifiers(text: str) -> list:
    """Identifier-shaped tokens that denote a source locus (camelCase / snake_case / dotted member), excluding
    plain prose words. e.g. lpTokenDepositValueChange, _getOracleData, quantAMMFeeTake, block.number."""
    out = []
    for tok in _IDENT_RE.findall(str(text or "")):
        low = tok.lower()
        if low in _IDENT_STOPWORDS or len(tok) < 6:
            continue
        is_camel = any(c.isupper() for c in tok[1:]) and any(c.islower() for c in tok)
        is_snake = "_" in tok
        is_dotted = "." in tok
        if is_camel or is_snake or is_dotted:
            out.append(tok)
    # de-dup preserving order
    seen, uniq = set(), []
    for t in out:
        if t.lower() not in seen:
            seen.add(t.lower()); uniq.append(t)
    return uniq


def _best_inventory_match(mech_text: str, inventory) -> str:
    """Return the inventory entry that best matches a rejection's mechanism text, only if the match is STRONG
    (word-set Jaccard >= 0.6 OR one is a substring of the other). Else ''."""
    mw = _words(mech_text)
    if not mw or not isinstance(inventory, list):
        return ""
    best, best_score = "", 0.0
    ml = str(mech_text or "").lower()
    for entry in inventory:
        ew = _words(entry)
        if not ew:
            continue
        jacc = len(mw & ew) / len(mw | ew)
        el = str(entry or "").lower()
        substring = ml and (ml in el or el in ml)
        score = max(jacc, 0.95 if substring else 0.0)
        if score > best_score:
            best, best_score = entry, score
    return best if best_score >= 0.6 else ""


def detect_non_responsive_rejection(row: dict, inventory) -> dict | None:
    """Part A. A rejection is non-responsive when the alleged mechanism's distinctive locus is absent from the
    entire rejection row. The alleged locus comes from an explicit `claimed_locus` field if present, else from
    the best-matching inventory entry's distinctive identifiers. Advisory; returns a flag dict or None."""
    if not isinstance(row, dict):
        return None
    addressed = " ".join(str(row.get(k) or "") for k in ("mechanism", "rejecting_source_fact",
                                                          "why_unexploitable", "claimed_locus")).lower()
    claimed = row.get("claimed_locus")
    if claimed:
        loci = _distinctive_identifiers(claimed) or [str(claimed)]
        source = "claimed_locus"
    else:
        inv_entry = _best_inventory_match(row.get("mechanism", ""), inventory)
        loci = _distinctive_identifiers(inv_entry)
        source = "inventory"
    if not loci:
        return None
    unaddressed = [t for t in loci if t.lower() not in addressed]
    if not unaddressed:
        return None
    rejection_loci = _distinctive_identifiers(
        " ".join(str(row.get(k) or "") for k in ("rejecting_source_fact", "why_unexploitable")))
    return {"flag": "non_responsive_rejection", "mechanism": row.get("mechanism"),
            "claimed_locus": unaddressed[0], "rejection_locus": ", ".join(rejection_loci) or None,
            "locus_source": source,
            "reason": "rejection does not address alleged source location"}


def detect_severity_floor_misrejection(row: dict) -> dict | None:
    """Part B. A rejection that correctly identifies a Medium-class impact (DoS/griefing/unavailability) but
    rejects it solely for not being fund-loss/High. Advisory; returns a flag dict or None."""
    if not isinstance(row, dict):
        return None
    blob = " ".join(str(row.get(k) or "") for k in ("rejecting_source_fact", "why_unexploitable",
                                                    "who_loses", "mechanism")).lower()
    high_bar = any(t in blob for t in _HIGH_BAR_TOKENS)
    if not high_bar:
        return None
    if any(t in blob for t in _NON_IMPACT_TOKENS) and not _has_impact(row.get("who_loses")):
        return None  # genuine no-impact rejection (dust/self-funded) — reject-first preserved
    impacts = [t for t in _MEDIUM_IMPACT_TOKENS if t in blob]
    if not impacts:
        return None
    return {"flag": "severity_floor_misrejection",
            "reason": "rejection rebuts only a fund-loss/High bar; mechanism still clears Medium",
            "impact_type": impacts[0].strip(), "severity_floor": "Medium"}


def _has_impact(v) -> bool:
    return bool(v) and str(v).strip().lower() not in _EMPTY_IMPACT


def _entries(v):
    """Normalize chosen/selected to a list of dict entries (accept dict OR list-of-dicts)."""
    if isinstance(v, dict):
        return [v]
    if isinstance(v, list):
        return [e for e in v if isinstance(e, dict)]
    return []


def _impact_ok(imp) -> bool:
    """P185: accept impact_direction as a dict (legacy keys) OR structured prose that states who-gains,
    who-loses, the impacted state/value, and the self-funded/admin-only/dust/timing exclusion."""
    if isinstance(imp, dict):
        return any(k in imp for k in _IMPACT_KEYS)
    s = str(imp or "").lower()
    if not s.strip():
        return False
    # a beneficiary (who gains) — broad synonym set
    has_gain = any(t in s for t in ("gain", "receive", "profit", "extract", "steal", "preserve", "keep",
                                    "withdraw", "mint", "benefit", "griefer", "attacker"))
    # a loser (who loses / is harmed) — broad synonym set
    has_loss = any(t in s for t in ("los", "erase", "destroy", "burn", "lock", "frozen", "drain", "stuck",
                                    "harm", "damage", "victim", "under-charg", "over-charg", "mispric"))
    has_state = any(t in s for t in ("state", "value", "variable", "invariant", "fee", "balance", "position",
                                     "price", "accounting", "nft"))
    has_excl = any(t in s for t in ("self-fund", "self fund", "dust", "admin-only", "admin only", "timing"))
    return has_gain and has_loss and has_state and has_excl


def check_output(d: dict) -> dict:
    """Classify one deep-trace finding/output. Returns {status, missing:[...], flags:[...], flag_details:[...]}.
    Never raises."""
    missing, flags = [], []
    flag_details = []                                    # P188: structured advisory flag records
    inv = d.get("mechanism_inventory")
    if not isinstance(inv, list) or len([x for x in inv if str(x).strip()]) < 3:
        missing.append("mechanism_inventory")            # <3 plausible mechanisms (when source supports)
    # rejection table (legacy alias: rejection_table; new: rejected_mechanisms)
    rt = d.get("rejected_mechanisms")
    if not isinstance(rt, list):
        rt = d.get("rejection_table")
    if not isinstance(rt, list) or not rt:
        missing.append("rejection_table")
    else:
        if not all(isinstance(r, dict) and (r.get("who_loses") or r.get("who_gains")) for r in rt):
            missing.append("who_loses_gains")
        # P185 demotion detector: a rejected row with REAL impact whose rejection is unproven (leans on an
        # unproven guard, or has no concrete rejecting source fact) should have been CARRIED, not rejected.
        for r in rt:
            if not isinstance(r, dict):
                continue
            real_impact = _has_impact(r.get("who_loses")) or _has_impact(r.get("who_gains"))
            unproven = bool(r.get("leans_on_unproven_guard")) or not str(r.get("rejecting_source_fact") or "").strip()
            if real_impact and unproven:
                flags.append("demoted_unresolved_mechanism")
                break
        # P188 advisory detectors (Part A + Part B) — run per rejection row; never block.
        for r in rt:
            nr = detect_non_responsive_rejection(r, inv)
            if nr:
                flags.append("non_responsive_rejection"); flag_details.append(nr)
            sf = detect_severity_floor_misrejection(r)
            if sf:
                flags.append("severity_floor_misrejection"); flag_details.append(sf)
    # selected/chosen (P185: accept selected_mechanisms OR chosen_mechanism as dict OR list)
    sel = _entries(d.get("selected_mechanisms")) or _entries(d.get("chosen_mechanism"))
    if not any(_has_impact(e.get("who_loses")) or _has_impact(e.get("who_gains")) for e in sel):
        if "who_loses_gains" not in missing:
            missing.append("who_loses_gains")
    if not _impact_ok(d.get("impact_direction")):
        missing.append("impact_direction")
    if not str(d.get("stop_condition") or "").strip():
        missing.append("stop_condition")
    # P188: recognize NEEDS_HARNESS escalations (advisory count; carried mechanisms are never flagged).
    unres = d.get("unresolved_mechanisms")
    needs_harness = 0
    if isinstance(unres, list):
        needs_harness = sum(1 for u in unres if isinstance(u, dict)
                            and str(u.get("status") or "").strip().upper() == "NEEDS_HARNESS")
    return {"status": "mechanism_complete" if not missing else "mechanism_incomplete",
            "missing": missing, "flags": sorted(set(flags)), "flag_details": flag_details,
            "selected_count": len(sel), "needs_harness_count": needs_harness}


def _iter_findings(obj):
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        for k in ("findings", "threads", "decisions"):
            if isinstance(obj.get(k), list):
                return obj[k]
    return []


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    rows, counts = [], Counter()
    out_dir = audit_path("output")
    for name in ("findings_deep_trace.json", "deep_pass/_decisions.json"):
        p = out_dir / name
        if not p.exists():
            continue
        try:
            data = json.loads(p.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        for f in _iter_findings(data):
            if not isinstance(f, dict):
                continue
            res = check_output(f)
            counts[res["status"]] += 1
            for fl in res.get("flags", []):
                counts[fl] += 1
            loc = f.get("location") or {}
            rows.append({"source": name, "id": f.get("id") or f.get("manifest_id"),
                         "function": (loc.get("function") if isinstance(loc, dict) else None),
                         "status": res["status"], "missing": res["missing"],
                         "flags": res.get("flags", []), "flag_details": res.get("flag_details", []),
                         "selected_count": res.get("selected_count", 0),
                         "needs_harness_count": res.get("needs_harness_count", 0)})

    report = {"phase": "P188", "advisory": True, "counts": dict(counts),
              "demoted_unresolved_mechanism": counts.get("demoted_unresolved_mechanism", 0),
              "non_responsive_rejection": counts.get("non_responsive_rejection", 0),
              "severity_floor_misrejection": counts.get("severity_floor_misrejection", 0),
              "needs_harness_total": sum(r.get("needs_harness_count", 0) for r in rows), "rows": rows}
    (out_dir / "deep_pass_mechanism_validation.json").write_text(json.dumps(report, indent=2))
    md = [f"# Deep-pass mechanism-enumeration + adjudication check (P183/P188) — ADVISORY (non-blocking)",
          f"- complete: {counts.get('mechanism_complete', 0)}  incomplete: {counts.get('mechanism_incomplete', 0)}",
          f"- non_responsive_rejection: {counts.get('non_responsive_rejection', 0)}  "
          f"severity_floor_misrejection: {counts.get('severity_floor_misrejection', 0)}"]
    for r in rows:
        if r["status"] == "mechanism_incomplete":
            md.append(f"- INCOMPLETE {r.get('function') or r.get('id')}: missing {r['missing']}")
        for fd in r.get("flag_details", []):
            md.append(f"- {fd.get('flag')} @ {r.get('function') or r.get('id')}: {fd.get('reason')}")
    (out_dir / "deep_pass_mechanism_validation.md").write_text("\n".join(md) + "\n")
    if not args.quiet:
        print("\n".join(md))
    return 0  # advisory: never non-zero


if __name__ == "__main__":
    raise SystemExit(main())
