"""
Tests for scripts/validate_accounting_clears.py — the conservation-note rule for high-risk accounting clears.

A high-risk DeFi accounting function may be `cleared` only if the disposition carries a COMPLETE
accounting_conservation_note. Advisory mode reports but exits 0; strict mode exits nonzero on any
missing/incomplete note. Deterministic, no LLM/network. The high-risk set is supplied via a synthetic
output/defi_accounting_audit.json so no real source files are needed.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_context  # noqa: E402
val = importlib.import_module("validate_accounting_clears")

REQUIRED = [
    "accounting_domains", "value_in", "value_out", "ledger_side_updated", "matching_ledger_side",
    "conservation_property", "why_conserved", "stale_state_risk", "oracle_or_price_dependency",
    "signed_unsigned_or_precision_risk", "global_vs_local_consistency", "evidence_span",
    "duplicate_or_existing_finding_check",
]


def _complete_note():
    return {f: (["debt", "vault"] if f == "accounting_domains" else f"value for {f}") for f in REQUIRED}


def _setup(tmp_path, monkeypatch, dispositions, high_risk_ids):
    out = tmp_path / "output"
    out.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    items = [
        {"id": "function:CD:settleVaultsDebt#a", "kind": "function", "name": "settleVaultsDebt",
         "contract": "CreditDelegationBranch", "file": "src/CD.sol",
         "source_span": {"start_line": 1, "end_line": 1}, "in_scope": True},
        {"id": "function:VR:getName#b", "kind": "function", "name": "getName",
         "contract": "VaultRouterBranch", "file": "src/VR.sol",
         "source_span": {"start_line": 1, "end_line": 1}, "in_scope": True},
    ]
    (out / "coverage_manifest.json").write_text(json.dumps({"items": items}))
    (out / "coverage_dispositions.json").write_text(json.dumps({"dispositions": dispositions}))
    # supply the high-risk accounting set deterministically
    (out / "defi_accounting_audit.json").write_text(json.dumps({
        "detected": [{"manifest_id": mid, "high_risk": True, "category": "realized_debt",
                      "accounting_domains": ["debt", "vault"]} for mid in high_risk_ids]}))
    return out


def _run(mode):
    old = sys.argv
    sys.argv = ["validate_accounting_clears", "--mode", mode, "--quiet"]
    try:
        rc = val.main()
    finally:
        sys.argv = old
    return rc


def _report(out):
    return json.loads((out / "accounting_clear_validation.json").read_text())


def _row(rep, mid):
    return next(r for r in rep["results"] if r["manifest_id"] == mid)


# 1. high-risk accounting clear WITH complete note → pass
def test_complete_note_passes(tmp_path, monkeypatch):
    out = _setup(tmp_path, monkeypatch,
                 [{"manifest_id": "function:CD:settleVaultsDebt#a", "status": "cleared",
                   "clear_reason": "x", "evidence": ["src/CD.sol:1"],
                   "accounting_conservation_note": _complete_note()}],
                 ["function:CD:settleVaultsDebt#a"])
    rc = _run("strict")
    rep = _report(out)
    assert _row(rep, "function:CD:settleVaultsDebt#a")["status"] == "pass"
    assert rc == 0


# 2. high-risk accounting clear WITHOUT note → missing; strict exits nonzero
def test_missing_note_fails_strict(tmp_path, monkeypatch):
    out = _setup(tmp_path, monkeypatch,
                 [{"manifest_id": "function:CD:settleVaultsDebt#a", "status": "cleared",
                   "clear_reason": "looks safe", "evidence": ["src/CD.sol:1"]}],
                 ["function:CD:settleVaultsDebt#a"])
    rc = _run("strict")
    rep = _report(out)
    assert _row(rep, "function:CD:settleVaultsDebt#a")["status"] == "missing_conservation_note"
    assert rc != 0


# 2b. incomplete note → incomplete_conservation_note with missing fields listed
def test_incomplete_note(tmp_path, monkeypatch):
    note = _complete_note()
    del note["conservation_property"]
    note["why_conserved"] = ""  # empty counts as missing
    out = _setup(tmp_path, monkeypatch,
                 [{"manifest_id": "function:CD:settleVaultsDebt#a", "status": "cleared",
                   "clear_reason": "x", "evidence": ["src/CD.sol:1"],
                   "accounting_conservation_note": note}],
                 ["function:CD:settleVaultsDebt#a"])
    _run("advisory")
    row = _row(_report(out), "function:CD:settleVaultsDebt#a")
    assert row["status"] == "incomplete_conservation_note"
    assert "conservation_property" in row["missing_fields"] and "why_conserved" in row["missing_fields"]


# 3. low-risk / non-accounting clear → not_accounting_sensitive (no note required)
def test_low_risk_not_required(tmp_path, monkeypatch):
    out = _setup(tmp_path, monkeypatch,
                 [{"manifest_id": "function:VR:getName#b", "status": "cleared",
                   "clear_reason": "pure getter", "evidence": ["src/VR.sol:1"]}],
                 ["function:CD:settleVaultsDebt#a"])  # getName NOT high-risk
    rc = _run("strict")
    rep = _report(out)
    assert _row(rep, "function:VR:getName#b")["status"] == "not_accounting_sensitive"
    # getName must not be an offender; (settleVaultsDebt has no disposition → needs_review, not a strict fail)
    assert all(o["manifest_id"] != "function:VR:getName#b" for o in rep["offenders"])


# 4. finding-linked accounting item → covered_by_finding (no clear note needed)
def test_finding_linked_not_required(tmp_path, monkeypatch):
    out = _setup(tmp_path, monkeypatch,
                 [{"manifest_id": "function:CD:settleVaultsDebt#a", "status": "finding",
                   "finding_refs": ["DT-001"]}],
                 ["function:CD:settleVaultsDebt#a"])
    rc = _run("strict")
    rep = _report(out)
    assert _row(rep, "function:CD:settleVaultsDebt#a")["status"] == "covered_by_finding"
    assert rc == 0


# 5. duplicate_or_known → no note required
def test_duplicate_or_known_not_required(tmp_path, monkeypatch):
    note = {"duplicate_or_existing_finding_check": "duplicate of DT-001 (known)"}
    out = _setup(tmp_path, monkeypatch,
                 [{"manifest_id": "function:CD:settleVaultsDebt#a", "status": "cleared",
                   "clear_reason": "dup", "evidence": ["src/CD.sol:1"],
                   "accounting_conservation_note": note}],
                 ["function:CD:settleVaultsDebt#a"])
    rc = _run("strict")
    rep = _report(out)
    assert _row(rep, "function:CD:settleVaultsDebt#a")["status"] == "duplicate_or_known"
    assert rc == 0


# 6. advisory mode reports a missing note but exits 0
def test_advisory_exits_zero(tmp_path, monkeypatch):
    out = _setup(tmp_path, monkeypatch,
                 [{"manifest_id": "function:CD:settleVaultsDebt#a", "status": "cleared",
                   "clear_reason": "looks safe", "evidence": ["src/CD.sol:1"]}],
                 ["function:CD:settleVaultsDebt#a"])
    rc = _run("advisory")
    rep = _report(out)
    assert rep["failing_count"] == 1
    assert rc == 0


# 7. strict mode with a missing note exits nonzero
def test_strict_exits_nonzero(tmp_path, monkeypatch):
    out = _setup(tmp_path, monkeypatch,
                 [{"manifest_id": "function:CD:settleVaultsDebt#a", "status": "cleared",
                   "clear_reason": "looks safe", "evidence": ["src/CD.sol:1"]}],
                 ["function:CD:settleVaultsDebt#a"])
    rc = _run("strict")
    assert rc != 0
