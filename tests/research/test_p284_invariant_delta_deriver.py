"""P284 — corrected-reference / invariant-delta deriver. Behavior + guard tests (research-only, advisory)."""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DERIVER = ROOT / "scripts/research/completion_evidence_deriver.py"
GATE = ROOT / "scripts/research/poc_readiness_evidence_gate.py"
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts/research"))
import invariant_delta_deriver as idd  # noqa: E402

DOCS = ROOT / "documentation/research/assisted_mode/p284_invariant_delta_derivation"
OUTS = DOCS / "outputs"
FROZEN = {
    "scripts/research/locus_shape_prioritizer.py": "d6b494bc3c0cc746",
    "scripts/research/recall_first_shape_sweep.py": "a48336275cb65a4f",
    "scripts/research/recall_first_harness.py": "be428a1202c45b1a",
    "scripts/research/mechanism_pairwise_selector.py": "b0623b8c88752059",
    "scripts/research/impact_first_poc_triage.py": "63c88d02d2c7eefa",
    "scripts/research/award_class_coverage_router.py": "6debb753b45f1833",
    "config/research_award_class_coverage_router.json": "91f9deac7867af62",
    "documentation/research/assisted_mode/p271_lending_runtime_scaffold/"
    "LENDING_COMPLETION_CHECKLIST.md": "2929a2154a88104e",
}
# the reused detector platform — imported READ-ONLY; must stay byte-identical (P284 never edits/routes them)
REUSED = {
    "scripts/sibling_function_parity_taxonomy.py": "e504383db8f33844",
    "scripts/registry_position_lifecycle_taxonomy.py": "da83a7acc217c706",
    "scripts/omitted_term_dataflow_gate.py": "8172de380c51cf3a",
    "scripts/bound_semantics_gate.py": "d6fcbc46e7971ff9",
    "config/sibling_function_parity_patterns.json": "a8a10807f842c299",
    "config/registry_position_lifecycle_patterns.json": "841bb089cc717e53",
}
FORBIDDEN = {
    "scripts/dashboard_sync.py": "c1af70e1", "prompts/deep_trace.md": "c095c426",
    "scripts/min_confirm_gate.py": "2a15169a", "scripts/confirm_gate.py": "afc481c9",
    "scripts/validate_p208_l3_readiness.py": "ae55eb80",
}
DOC_FILES = ("SETUP.md", "INVARIANT_DELTA_DESIGN.md", "IMPLEMENTATION_NOTES.md", "INVARIANT_DELTA_REMAP_RESULTS.md",
             "INVARIANT_DELTA_EVIDENCE_AUDIT.md", "INVARIANT_DELTA_REPAIR_BACKLOG.md", "LIMITATIONS.md", "VERDICT.md",
             "ROLLBACK_PLAN.md")
VERDICTS = ("A — INVARIANT_DELTA_READY_FOR_POC_SWEEP", "B — INVARIANT_DELTA_PROMISING_NEEDS_REFINEMENT",
            "C — INVARIANT_DELTA_TOO_NOISY", "D — ABORTED_CONSTRAINT_VIOLATION")
VALUE = "ACCOUNTING_LIQUIDATION_BAD_DEBT"


def _sha16(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def _build(tmp, funcs):
    """funcs: list of (contract, name, body). One .sol file; manifest items with line spans + award_class slot."""
    lines, items = [], []
    for contract, name, body in funcs:
        start = len(lines) + 1
        lines.extend(body.splitlines())
        items.append({"kind": "function", "contract": contract, "name": name, "visibility": "external",
                      "mutability": "nonpayable", "modifiers": [], "file": None,
                      "source_span": {"start_line": start, "end_line": len(lines)}})
    src = Path(tmp) / "S.sol"
    src.write_text("\n".join(lines))
    for it in items:
        it["file"] = str(src)
    return {"items": items}


def _derive(tmp, funcs, target, award_class=VALUE, gate_evidence=None):
    man = _build(tmp, funcs)
    it = next(i for i in man["items"] if i["name"] == target)
    it["award_class"] = award_class
    return idd.derive(it, man, None, gate_evidence or {}, None)


# ---- derivation-type detection ----
def test_d43_detects_sibling_reference():
    with tempfile.TemporaryDirectory() as t:
        r = _derive(t, [("C", "claim", "function claim() external {\n getOriginalOwner(x);\n token.transfer(o,a);\n}"),
                        ("C", "claim_many", "function claim_many() external {\n for(uint i;i<n;i++){ token.transfer(o,a); }\n}")],
                    "claim_many", "REWARDS_CLAIMS")
        assert r["invariant_delta_status"] == "SIBLING_REFERENCE_FOUND"
        assert r["affected_variables"] == ["getOriginalOwner"] and r["confidence"] in ("HIGH", "MEDIUM")


def test_d42_detects_symmetric_ledger():
    with tempfile.TemporaryDirectory() as t:
        r = _derive(t, [("C", "openBorrowPosition", "function openBorrowPosition() external {\n proxy.openPosition(id);\n registry.updateHoldingPosition(id);\n}"),
                        ("C", "transferBetweenAccounts", "function transferBetweenAccounts() external {\n proxy.transferPosition(id);\n}")],
                    "transferBetweenAccounts")
        assert r["invariant_delta_status"] == "CONSERVATION_FOUND"


def test_d44_detects_corrected_reference_rounding():
    with tempfile.TemporaryDirectory() as t:
        r = _derive(t, [("C", "f", "function f() external {\n uint a = x.mulDiv(y, z, Math.Rounding.Floor);\n out = a / b * c;\n}")],
                    "f", "SHARE_ROUNDING_PRECISION")
        assert r["invariant_delta_status"] == "REFERENCE_FOUND" and r["derivation_type"] == "D4.4_rounding_direction"


def test_d46_detects_oracle_normalization():
    with tempfile.TemporaryDirectory() as t:
        r = _derive(t, [("C", "valueOf", "function valueOf() external {\n uint price = oracle.latestRoundData();\n value = price * amount;\n}")],
                    "valueOf", "ORACLE_PRICING")
        assert r["invariant_delta_status"] == "REFERENCE_FOUND" and r["derivation_type"] == "D4.6_oracle_normalization"


def test_d47_detects_state_machine_value_invariant():
    with tempfile.TemporaryDirectory() as t:
        ge = {"state_machine_detected": True, "or_state_gate": True, "state_markers": ["succeeded", "defeated"],
              "source_span": [1, 5]}
        r = _derive(t, [("C", "execute", "function execute() external {\n state();\n proposals[id].executed = true;\n}")],
                    "execute", "STATE_MACHINE_LIFECYCLE", gate_evidence=ge)
        assert r["invariant_delta_status"] == "STATE_MACHINE_DELTA_FOUND"


def test_d15_before_after_equation_extracted():
    # before/after / conservation equation IS extracted (assertion scaffold) even without a deviation
    eq = idd._d15_equation({}, "function f() external { uint b0=token.balanceOf(a); x(); uint b1=token.balanceOf(a); }")
    assert eq is not None and "balanceAfter" in eq[0]
    eq2 = idd._d15_equation({}, "function f() external { totalAssets += minted; }")
    assert eq2 is not None and "totalAssets" in eq2[0]


def test_d41_conservation_equation_no_lift_without_deviation():
    with tempfile.TemporaryDirectory() as t:
        r = _derive(t, [("C", "f", "function f() external {\n uint b0 = token.balanceOf(a);\n send(a);\n uint b1 = token.balanceOf(a);\n}")],
                    "f")
        # equation present (poc_assertion) but no deviation reference -> NO_REFERENCE (does not lift)
        assert r["invariant_delta_status"] == "NO_REFERENCE"
        assert r["poc_assertion"] and "balanceAfter" in r["poc_assertion"]


# ---- fail-closed ----
def test_generic_transfer_no_deviation():
    with tempfile.TemporaryDirectory() as t:
        r = _derive(t, [("C", "f", "function f() external {\n token.transfer(to, amt);\n}")], "f")
        assert r["invariant_delta_status"] in ("NO_REFERENCE", "INSUFFICIENT_SOURCE")


def test_naming_only_sibling_no_deviation():
    with tempfile.TemporaryDirectory() as t:
        r = _derive(t, [("C", "getRate", "function getRate() external {\n return rate;\n}"),
                        ("C", "getRates", "function getRates() external {\n return rates;\n}")], "getRates")
        assert r["invariant_delta_status"] in ("NO_REFERENCE", "INSUFFICIENT_SOURCE")


def test_ambiguous_reference_fails_closed():
    with tempfile.TemporaryDirectory() as t:
        r = _derive(t, [("C", "claim", "function claim() external {\n getOriginalOwner(x);\n token.transfer(o,a);\n}"),
                        ("C", "claimAll", "function claimAll() external {\n register(x);\n token.transfer(o,a);\n}"),
                        ("C", "claim_many", "function claim_many() external {\n for(uint i;i<n;i++){ token.transfer(o,a); }\n}")],
                    "claim_many", "REWARDS_CLAIMS")
        assert r["invariant_delta_status"] == "AMBIGUOUS_REFERENCE"


def test_invented_corrected_expr_fails_closed():
    # "looks like it rounds" but no rounding evidence / no sibling -> never invents a corrected expression
    with tempfile.TemporaryDirectory() as t:
        r = _derive(t, [("C", "f", "function f() external {\n out = a / b * c;\n}")], "f", "SHARE_ROUNDING_PRECISION")
        assert r["invariant_delta_status"] in ("NO_REFERENCE", "INSUFFICIENT_SOURCE")


def test_declaration_only_insufficient_source():
    with tempfile.TemporaryDirectory() as t:
        man = _build(t, [("I", "f", "function f() external returns (uint);")])
        it = man["items"][0]
        it["award_class"] = VALUE
        r = idd.derive(it, man, None, {}, None)
        assert r["invariant_delta_status"] == "INSUFFICIENT_SOURCE"


# ---- gate integration ----
def _gate(tmp, funcs, target, award_class=VALUE):
    man = _build(tmp, funcs)
    for it in man["items"]:
        if it["name"] == target:
            it_target = it
    pkg = {"candidate_id": "c1", "award_class": award_class, "contract_function": f"C.{target}",
           "mechanism_hypothesis": "m", "root_cause": "rc", "runner_up_mechanism": "ru"}
    mp = Path(tmp) / "m.json"; mp.write_text(json.dumps(man))
    pp = Path(tmp) / "p.json"; pp.write_text(json.dumps({"packages": [pkg]}))
    dp = Path(tmp) / "d.json"
    subprocess.run([sys.executable, str(DERIVER), "--manifest", str(mp), "--packages", str(pp), "--out", str(dp),
                    "--quiet"], capture_output=True, text=True)
    gp = Path(tmp) / "g.json"
    subprocess.run([sys.executable, str(GATE), "--packages", str(dp), "--out", str(gp), "--quiet"],
                   capture_output=True, text=True)
    return json.loads(gp.read_text())["decisions"][0]


def test_generic_transfer_cannot_create_ready():
    with tempfile.TemporaryDirectory() as t:
        d = _gate(t, [("C", "f", "function f() external {\n token.transfer(to, amt);\n}")], "f")
        assert d["status"] == "NEEDS_VALUE_FLOW_EVIDENCE"


def test_naming_only_similarity_cannot_create_ready():
    with tempfile.TemporaryDirectory() as t:
        d = _gate(t, [("C", "fooRate", "function fooRate() external {\n x = rate;\n}"),
                      ("C", "fooRates", "function fooRates() external {\n y = rates;\n}")], "fooRates")
        assert d["status"] != "READY_FOR_POC_INTENT"


def test_inline_guard_still_blocks_ready():
    with tempfile.TemporaryDirectory() as t:
        d = _gate(t, [("C", "claim", "function claim() external {\n getOriginalOwner(x);\n token.transfer(o,a);\n}"),
                      ("C", "claim_many", "function claim_many() external {\n require(msg.sender == owner);\n for(uint i;i<n;i++){ token.transfer(o,a); }\n}")],
                  "claim_many", "REWARDS_CLAIMS")
        assert d["status"] == "INLINE_GUARD_REFUTED"


# ---- corpus regressions ----
def test_l2governor_remains_ready():
    found = False
    for r in OUTS.glob("*/readiness.json"):
        for d in json.loads(r.read_text())["decisions"]:
            if d["candidate_id"] == "coverage_manifest:L2Governor:execute:20":
                found = True
                assert d["status"] == "READY_FOR_POC_INTENT"
    assert found


def test_transform_and_cancelpodlisting_not_ready():
    seen = {}
    for r in OUTS.glob("*/readiness.json"):
        for d in json.loads(r.read_text())["decisions"]:
            seen[d["candidate_id"]] = d["status"]
    assert seen.get("coverage_manifest:V3Vault:transform:9") == "INLINE_GUARD_REFUTED"
    assert seen.get("coverage_manifest:IBeanstalk:cancelPodListing:0") == "NEEDS_SOURCE_SPAN"


def test_no_severity_reportable_leakage():
    for r in OUTS.glob("*/readiness.json"):
        for d in json.loads(r.read_text())["decisions"]:
            assert d["severity"] is None
            for f in ("reportable", "submission_ready", "concluded", "emits_finding", "production_routing"):
                assert d[f] is False


def test_remap_severe_fp_zero_and_no_false_lift():
    m = json.loads((OUTS / "remap_metrics.json").read_text())
    assert m["severe_concluded_or_reportable_fp"] == 0
    assert m["newly_lifted_to_ready"] == []
    assert m["after_P284"]["READY_FOR_POC_INTENT"] == 1


def test_evidence_records_advisory_only():
    ev = json.loads((OUTS / "invariant_delta_evidence.json").read_text())
    for r in ev["records"]:
        assert r["invariant_delta_status"] in idd.ALL_STATUSES


# ---- byte-identical guards ----
def test_frozen_reused_and_forbidden_byte_identical():
    for rel, h in {**FROZEN, **REUSED}.items():
        assert _sha16(ROOT / rel) == h, f"changed: {rel}"
    for rel, h in FORBIDDEN.items():
        assert _sha16(ROOT / rel).startswith(h), f"forbidden changed: {rel}"


def test_docs_and_verdict():
    for d in DOC_FILES:
        assert (DOCS / d).exists(), f"missing {d}"
    assert any(v in (DOCS / "VERDICT.md").read_text() for v in VERDICTS)


