"""
P178 — structured dependency evidence capture (no LLM, no network).

extract_dependency_metadata implements RESOLVE-OR-NOTHING: a candidate becomes structured metadata only if it
is an identifier-shaped, non-generic token that resolves to a manifest artifact. Generic prose stays advisory.
The writer auto-captures resolved facts so the UNCHANGED P177 router adjudicates on artifacts. classify_clear
routing semantics are not changed by this phase.
"""
import importlib
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

import audit_context  # noqa: E402
dmeta = importlib.import_module("dependency_metadata")
dcu = importlib.import_module("dependency_clear_utils")
sweep_write = importlib.import_module("coverage_sweep_write")

# a tiny manifest: the cleared item (pack) + an in-scope unreviewed guard + an in-scope reviewed guard
GUARD_ID = "function:Guard:_guardQuantAMMWeights#bbbb"
NAVOPS_ID = "function:Vault:ensureNoNavOps#cccc"
PACK_ID = "function:Pool:pack#aaaa"
MANIFEST = [
    {"id": PACK_ID, "kind": "function", "contract": "Pool", "file": "Pool.sol", "name": "pack",
     "in_scope": True, "attack_surface_score": 2, "source_span": {"start_line": 5, "end_line": 9}},
    {"id": GUARD_ID, "kind": "function", "contract": "Guard", "file": "Guard.sol", "name": "_guardQuantAMMWeights",
     "in_scope": True, "attack_surface_score": 2, "source_span": {"start_line": 19, "end_line": 30}},
    {"id": NAVOPS_ID, "kind": "function", "contract": "Vault", "file": "Vault.sol", "name": "ensureNoNavOps",
     "in_scope": True, "attack_surface_score": 2, "source_span": {"start_line": 40, "end_line": 44}},
]
MAN_IDX = {i["id"]: i for i in MANIFEST}
NAME_IDX = dcu.build_manifest_name_index(MANIFEST)


def _extract(clear_reason, disp_index=None):
    disp = {"manifest_id": PACK_ID, "status": "cleared", "evidence": ["Pool.sol:5"], "clear_reason": clear_reason}
    return dmeta.extract_dependency_metadata(disp, manifest_index=MAN_IDX, name_index=NAME_IDX,
                                             disposition_index=disp_index or {})


# ---------- resolve-or-nothing (the core guardrail) ----------

def test_generic_prose_resolves_nothing_advisory():
    for reason in ["safe because guarded downstream before use",
                   "protected by invariant",
                   "the oracle prevents this",
                   "bounded by downstream guard"]:
        meta = _extract(reason)
        assert meta["dependency_name"] is None, reason
        assert "clear_depends_on" not in meta            # no bridge → advisory under P177
        assert dmeta.validate_dependency_metadata(meta) == "dependency_name_unresolved"


def test_resolved_underscore_camel_artifact_is_structured():
    di = {GUARD_ID: {"manifest_id": GUARD_ID, "status": "assigned"}}  # in-scope, unreviewed
    meta = _extract("clamped by _guardQuantAMMWeights", disp_index=di)
    assert meta["dependency_name"] == "_guardquantammweights"
    assert meta["dependency_scope"] == "cross_contract"
    assert meta["dependency_status"] == "unreviewed_dependency"
    assert meta["clear_depends_on"] == [GUARD_ID]                     # bridged to legacy fields
    assert dmeta.validate_dependency_metadata(meta) == "metadata_complete"


def test_resolved_camelcase_artifact_is_structured():
    di = {NAVOPS_ID: {"manifest_id": NAVOPS_ID, "status": "cleared", "evidence": ["Vault.sol:40"],
                      "clear_reason": "reviewed"}}  # reviewed dependency → proven
    meta = _extract("validated by ensureNoNavOps", disp_index=di)
    assert meta["dependency_name"] == "ensurenonavops"
    assert meta["dependency_status"] == "proven"
    assert dmeta.validate_dependency_metadata(meta) == "metadata_complete"


def test_unresolvable_identifier_stays_advisory():
    # identifier-shaped but NOT in the manifest → resolve-or-nothing → advisory
    meta = _extract("guarded by someNonexistentHelper before use")
    assert meta["dependency_name"] is None
    assert dmeta.validate_dependency_metadata(meta) == "dependency_name_unresolved"


def test_extractor_is_fail_open_on_garbage():
    assert dmeta.extract_dependency_metadata({}, None, None, None)["dependency_name"] is None
    assert dmeta.extract_dependency_metadata({"clear_reason": None})["dependency_name"] is None


# ---------- P180: boilerplate / survey / plumbing suppression ----------

def test_p180_boilerplate_out_of_scope_clear_stays_advisory():
    # the exact zaros artifact shape: out-of-scope boilerplate whose guard_or_invariant enumerates loadLive
    disp = {"manifest_id": PACK_ID, "status": "cleared", "evidence": ["Pool.sol:5"],
            "clear_reason": "Out of contest README scope (not in 43-file allowlist). Light pass; not answer-key eligible.",
            "guard_or_invariant": "Relevant guards/invariants identified (loadLive/loadExisting existence checks, access modifiers)"}
    meta = dmeta.extract_dependency_metadata(disp, MAN_IDX, NAME_IDX, {GUARD_ID: {"manifest_id": GUARD_ID, "status": "assigned"}})
    assert meta["dependency_name"] is None                     # suppressed → advisory
    assert dmeta.validate_dependency_metadata(meta) == "dependency_name_unresolved"


def test_p180_guard_survey_stays_advisory():
    disp = {"manifest_id": PACK_ID, "status": "cleared", "evidence": ["Pool.sol:5"],
            "guard_or_invariant": "guards/invariants identified: _guardQuantAMMWeights, ensureNoNavOps, access modifiers"}
    meta = dmeta.extract_dependency_metadata(disp, MAN_IDX, NAME_IDX, {})
    assert meta["dependency_name"] is None                     # survey enumeration → advisory


def test_p180_plumbing_helper_stays_advisory():
    # loadLive resolves in the manifest but is plumbing, not a guard → stoplisted
    man = MANIFEST + [{"id": "function:Vault:loadLive#dddd", "kind": "function", "contract": "Vault",
                       "file": "Vault.sol", "name": "loadLive", "in_scope": True, "attack_surface_score": 1,
                       "source_span": {"start_line": 1, "end_line": 3}}]
    mi = {i["id"]: i for i in man}
    ni = dcu.build_manifest_name_index(man)
    disp = {"manifest_id": PACK_ID, "status": "cleared", "evidence": ["Pool.sol:5"],
            "clear_reason": "bounded by loadLive before use"}
    meta = dmeta.extract_dependency_metadata(disp, mi, ni, {})
    assert meta["dependency_name"] is None


# ---------- P180 regression: real explicit deps still resolve ----------

def test_p180_real_guard_still_resolves():
    di = {GUARD_ID: {"manifest_id": GUARD_ID, "status": "assigned"}}
    meta = _extract("clamped by _guardQuantAMMWeights", disp_index=di)
    assert meta["dependency_name"] == "_guardquantammweights"
    assert dmeta.validate_dependency_metadata(meta) == "metadata_complete"


def test_p180_ensurenonavops_still_resolves():
    di = {NAVOPS_ID: {"manifest_id": NAVOPS_ID, "status": "cleared", "evidence": ["Vault.sol:40"],
                      "clear_reason": "reviewed"}}
    meta = _extract("validated by ensureNoNavOps", disp_index=di)
    assert meta["dependency_name"] == "ensurenonavops"


def test_p180_explicit_clear_depends_on_bypasses_boilerplate_skip():
    # genuine structured input must be honored even if the prose looks boilerplate
    di = {GUARD_ID: {"manifest_id": GUARD_ID, "status": "assigned"}}
    disp = {"manifest_id": PACK_ID, "status": "cleared", "evidence": ["Pool.sol:5"],
            "clear_reason": "Out of contest scope; light pass",  # boilerplate prose
            "clear_depends_on": [GUARD_ID]}                       # but EXPLICIT structured claim
    meta = dmeta.extract_dependency_metadata(disp, MAN_IDX, NAME_IDX, di)
    assert meta["dependency_name"] == "_guardquantammweights"     # honored, not suppressed


# ---------- bridged metadata drives the UNCHANGED P177 router ----------

def test_resolved_unreviewed_bridges_to_block_under_p177():
    di = {GUARD_ID: {"manifest_id": GUARD_ID, "status": "assigned"}}
    disp = {"manifest_id": PACK_ID, "status": "cleared", "evidence": ["Pool.sol:5"],
            "clear_reason": "clamped by _guardQuantAMMWeights"}
    meta = dmeta.extract_dependency_metadata(disp, MAN_IDX, NAME_IDX, di)
    disp.update({k: v for k, v in meta.items() if v is not None})
    cls = dcu.classify_clear(disp, di, NAME_IDX, manifest_index=MAN_IDX)
    assert cls["status"] == "unreviewed_dependency"
    assert dcu.dependency_route_decision(cls, disp) == "block"        # P177 rule, unchanged


def test_generic_prose_bridges_nothing_stays_advisory_under_p177():
    disp = {"manifest_id": PACK_ID, "status": "cleared", "evidence": ["Pool.sol:5"],
            "clear_reason": "safe because guarded downstream"}
    meta = dmeta.extract_dependency_metadata(disp, MAN_IDX, NAME_IDX, {})
    disp.update({k: v for k, v in meta.items() if v is not None})
    cls = dcu.classify_clear(disp, {}, NAME_IDX, manifest_index=MAN_IDX)
    assert dcu.dependency_route_decision(cls, disp) == "advisory"     # no prose hard-route


# ---------- writer integration: auto-capture then route per P177 ----------

@pytest.fixture()
def ws(tmp_path, monkeypatch):
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    return tmp_path


def _write(ws, rel, obj):
    p = ws / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2))


def _run(mod, argv=None):
    old = sys.argv
    sys.argv = [mod.__name__] + (argv or [])
    try:
        return mod.main()
    finally:
        sys.argv = old


def test_writer_auto_captures_resolved_dep_and_routes(ws, monkeypatch):
    # full-audit strict: a prose clear naming a REAL in-scope unreviewed guard is auto-captured → routes.
    monkeypatch.setenv("AUDITWATCH_FULL_AUDIT", "1")
    _write(ws, "output/coverage_manifest.json", {"schema_version": 1, "source": {}, "items": MANIFEST})
    _write(ws, "output/coverage_dispositions.json", {"dispositions": [
        {"manifest_id": PACK_ID, "status": "unassigned", "evidence": [], "finding_refs": [], "clear_reason": None},
        {"manifest_id": GUARD_ID, "status": "assigned", "assigned_pass": "deep", "evidence": [], "finding_refs": []},
    ]})
    _write(ws, "data/coverage_sweep/_decisions.json", {"decisions": [
        {"manifest_id": PACK_ID, "disposition": "cleared", "evidence_span": "Pool.sol:5",
         "reason": "clamped by _guardQuantAMMWeights"},
    ]})
    assert _run(sweep_write) == 0
    item = {d["manifest_id"]: d for d in
            json.loads((ws / "output" / "coverage_dispositions.json").read_text())["dispositions"]}[PACK_ID]
    assert item["status"] == "assigned"                              # routed (now precise, fact-based)
    assert item.get("dependency_name") == "_guardquantammweights"    # structured fact captured
    assert item.get("dependency_status") == "unreviewed_dependency"


def test_writer_prose_only_stays_cleared_advisory(ws, monkeypatch):
    # full-audit: generic prose (no resolvable artifact) is NOT auto-captured → stays cleared+advisory.
    monkeypatch.setenv("AUDITWATCH_FULL_AUDIT", "1")
    _write(ws, "output/coverage_manifest.json", {"schema_version": 1, "source": {}, "items": MANIFEST})
    _write(ws, "output/coverage_dispositions.json", {"dispositions": [
        {"manifest_id": PACK_ID, "status": "unassigned", "evidence": [], "finding_refs": [], "clear_reason": None},
    ]})
    _write(ws, "data/coverage_sweep/_decisions.json", {"decisions": [
        {"manifest_id": PACK_ID, "disposition": "cleared", "evidence_span": "Pool.sol:5",
         "reason": "safe because guarded downstream before use"},
    ]})
    assert _run(sweep_write) == 0
    item = {d["manifest_id"]: d for d in
            json.loads((ws / "output" / "coverage_dispositions.json").read_text())["dispositions"]}[PACK_ID]
    assert item["status"] == "cleared"                              # NOT routed
    assert item.get("dependency_name") is None
