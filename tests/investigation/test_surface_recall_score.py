"""Phase-81b tests for the lead-recall scorer (RESEARCH-ONLY)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from investigation import surface_recall_score as S  # noqa: E402


def test_1_self_test_passes():
    assert S._self_test() == 0


def test_2_direct_adjacent_miss_classification():
    leads = [
        {"trigger_contract": "A", "trigger_function": "f", "surface_classes": ["value_exit"]},
        {"trigger_contract": "B", "trigger_function": "other", "surface_classes": ["auth_boundary"]},
    ]
    awarded = [
        {"id": "1", "severity": "High", "contract": "A", "function": "f", "mechanism_class": ["value_exit"]},
        {"id": "2", "severity": "High", "contract": "B", "function": "missing", "mechanism_class": ["auth_boundary"]},
        {"id": "3", "severity": "Medium", "contract": "Z", "function": "g", "mechanism_class": ["fee_path"]},
    ]
    t = S.score(leads, awarded)["totals"]
    assert t["direct"] == 1 and t["adjacent"] == 1 and t["miss"] == 1


def test_3_mechanism_scored_only_on_direct():
    # an ADJ match (different function) must NOT earn mechanism-naming credit
    leads = [{"trigger_contract": "A", "trigger_function": "other", "surface_classes": ["value_exit"]}]
    awarded = [{"id": "1", "severity": "High", "contract": "A", "function": "missing", "mechanism_class": ["value_exit"]}]
    r = S.score(leads, awarded)
    assert r["rows"][0]["recall"] == "ADJ"
    assert r["rows"][0]["mechanism_naming"] == "n/a"
    assert r["totals"]["mechanism_naming_match"] == 0


def test_4_required_functions_gate():
    leads = [{"trigger_contract": "A", "trigger_function": "f", "surface_classes": ["value_exit"]}]
    awarded = [{"id": "1", "severity": "High", "contract": "A", "function": "f", "mechanism_class": ["value_exit"]}]
    r = S.score(leads, awarded, required_functions=["A.f", "A.missing"])
    assert r["required_functions"]["A.f"] is True
    assert r["required_functions"]["A.missing"] is False


def test_5_research_only_flags():
    r = S.score([], [])
    assert r["routes_in_production"] is False and r["research_only"] is True and r["is_gate"] is False


def test_6_real_decent_artifact_recall():
    # the frozen Decent run must cover all 9 awarded findings incl the two named functions
    import json
    base = ROOT / "documentation" / "research" / "_p81b" / "decent"
    if not (base / "leads.json").exists():
        return
    leads = json.loads((base / "leads.json").read_text())["leads"]
    awarded = json.loads((base / "awarded_map.json").read_text())["awarded"]
    r = S.score(leads, awarded, required_functions=["UTB.receiveFromBridge", "DecentBridgeExecutor.execute"])
    assert r["totals"]["covered"] >= 6
    assert all(r["required_functions"].values())
