"""End-to-end orchestrator tests — RAW -> CONTEXT_MAPPED, writes only to a tmp candidates root, no PoC/report."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "candidates"))
import artifacts as A  # noqa: E402
import validate_candidate as vc  # noqa: E402

DETECTOR_JSON = ROOT / "audits/size-credit-2024-06/output/multicall_invariant_audit.json"
TARGET = "audits/size-credit-2024-06/contracts/2024-06-size"
CID = "multicall_invariant:Multicall:multicall:delegatecall_self_context:5d1136da"


@pytest.fixture
def tmp_candidates(tmp_path, monkeypatch):
    monkeypatch.setattr(A, "CANDIDATES_ROOT", tmp_path)
    return tmp_path


def test_end_to_end_context_mapped(tmp_candidates):
    res = vc.validate(CID, "size-credit-2024-06", DETECTOR_JSON, TARGET, mode="strict")
    assert res["final_state"] == "CONTEXT_MAPPED"
    folder = tmp_candidates / "size-credit-2024-06" / "5d1136da"
    written = {p.name for p in folder.glob("*")}
    # 8 stage-1 artifacts
    assert {"candidate_manifest.json", "source_resolution.json", "reachability_map.json", "callable_surface.json",
            "state_mutation_map.json", "validation_scorecard.json", "promotion_decision.json", "verdict.md"} <= written
    # MUST NOT emit poc/report locks or any poc/report file
    assert "poc_ready.lock.json" not in written and "report_ready.lock.json" not in written


def test_scorecard_separates_four_confidences(tmp_candidates):
    vc.validate(CID, "size-credit-2024-06", DETECTOR_JSON, TARGET)
    sc = json.loads((tmp_candidates / "size-credit-2024-06" / "5d1136da" / "validation_scorecard.json").read_text())
    c = sc["confidences"]
    assert set(c) == {"detector_confidence", "validation_confidence", "exploit_confidence", "impact_confidence"}
    assert c["detector_confidence"] == "high"        # carried verbatim from detector
    assert c["exploit_confidence"] is None and c["impact_confidence"] is None  # not yet established
    assert c["validation_confidence"] == "medium"


def test_promotion_stops_at_context_mapped(tmp_candidates):
    vc.validate(CID, "size-credit-2024-06", DETECTOR_JSON, TARGET)
    pd = json.loads((tmp_candidates / "size-credit-2024-06" / "5d1136da" / "promotion_decision.json").read_text())
    assert pd["current_state"] == "CONTEXT_MAPPED"
    assert pd["next_required_gate"] == "defense_map_gate"
    assert pd["poc_allowed"] is False and pd["report_allowed"] is False


def test_common_header_present(tmp_candidates):
    vc.validate(CID, "size-credit-2024-06", DETECTOR_JSON, TARGET)
    m = json.loads((tmp_candidates / "size-credit-2024-06" / "5d1136da" / "candidate_manifest.json").read_text())
    for k in ("candidate_id", "audit_id", "candidate_hash", "generated_at", "tool", "source_root",
              "status", "reasons", "unresolved_assumptions", "routing_allowed", "research_only"):
        assert k in m
    assert m["routing_allowed"] is False and m["research_only"] is True


def test_max_stage_invariant_end_to_end(tmp_candidates):
    res = vc.validate(CID, "size-credit-2024-06", DETECTOR_JSON, TARGET, mode="strict", max_stage="invariant")
    assert res["final_state"] == "INVARIANT_ANALYZED"
    folder = tmp_candidates / "size-credit-2024-06" / "5d1136da"
    written = {p.name for p in folder.glob("*")}
    assert "defense_map.json" in written and "invariant_analysis.json" in written
    # Stage-2 must NOT create later-stage artifacts
    for forbidden in ("sequence_candidates.json", "negative_tests.json", "poc_ready.lock.json", "report_ready.lock.json"):
        assert forbidden not in written
    promo = json.loads((folder / "promotion_decision.json").read_text())
    assert promo["current_state"] == "INVARIANT_ANALYZED"
    assert promo["next_required_gate"] == "sequence_gate"
    assert promo["poc_allowed"] is False and promo["report_allowed"] is False
    sc = json.loads((folder / "validation_scorecard.json").read_text())
    assert sc["required"]["defense_mapped"] is True and sc["required"]["invariant_defined"] is True
    assert sc["confidences"]["exploit_confidence"] is None and sc["confidences"]["impact_confidence"] is None


def test_default_max_stage_still_context(tmp_candidates):
    res = vc.validate(CID, "size-credit-2024-06", DETECTOR_JSON, TARGET)  # default context
    assert res["final_state"] == "CONTEXT_MAPPED"
    folder = tmp_candidates / "size-credit-2024-06" / "5d1136da"
    written = {p.name for p in folder.glob("*")}
    assert "defense_map.json" not in written and "invariant_analysis.json" not in written


def test_stage2_reconstructs_candidate_from_folder(tmp_candidates):
    # run stage 1 first (writes manifest+source_resolution), then stage 2 with empty candidate-json
    vc.validate(CID, "size-credit-2024-06", DETECTOR_JSON, TARGET)
    res = vc.validate(CID, "size-credit-2024-06", None, TARGET, max_stage="invariant")
    assert res["final_state"] == "INVARIANT_ANALYZED"


def test_refuses_to_overwrite_illustrative(tmp_candidates):
    folder = tmp_candidates / "size-credit-2024-06" / "5d1136da"
    folder.mkdir(parents=True)
    (folder / "candidate_manifest.json").write_text(json.dumps({"_illustrative": True, "candidate_id": CID}))
    with pytest.raises(SystemExit):
        vc.validate(CID, "size-credit-2024-06", DETECTOR_JSON, TARGET)
    # with --force it proceeds
    res = vc.validate(CID, "size-credit-2024-06", DETECTOR_JSON, TARGET, force=True)
    assert res["final_state"] == "CONTEXT_MAPPED"
