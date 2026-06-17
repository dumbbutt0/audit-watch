"""P106: rank-signal probe (evidence-free pre-ranking) — RESEARCH-ONLY, un-wired.

Proves the probe extracts per-function evidence-free features, ranks the awarded function within its surface (not
just present/absent), reports selectivity via lift (so blunt binary features can't masquerade as discriminators),
is deterministic, and promotes/scores nothing. The live corpus is exercised only when /tmp sources are present.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "assisted"))
import rank_signal_probe as P  # noqa: E402

CORPUS = ROOT / "documentation" / "research" / "assisted_mode" / "p105" / "benchmark_corpus.json"

_SRC = (
    "// SPDX-License-Identifier: MIT\npragma solidity ^0.8.0;\n"
    "contract Fix {\n"
    "  mapping(address=>uint256) public balance; uint256 public total; address owner;\n"
    "  function drain(uint256 amount) external {\n"
    "     balance[msg.sender] += amount; total += amount;\n"
    "     IERC20(token).transfer(msg.sender, amount); pool.staticcall(data);\n"
    "  }\n"
    "  function setOwner(address o) external { require(msg.sender == owner); owner = o; }\n"
    "  function ping() external view returns (uint256) { return total; }\n"
    "}\n"
)


def _corpus(tmp_path):
    (tmp_path / "Fix.sol").write_text(_SRC, encoding="utf-8")
    return {
        "exclude_substrings": [],
        "subjects": [{
            "id": "fx", "phase": "test", "source_roots": [str(tmp_path)],
            "awarded_findings": [
                {"finding_id": "HIGH", "contract": "Fix", "function": "drain",
                 "invariant_category": "per_user_accounting", "severity": "High",
                 "surfaceable": True, "grounding": "high"},
                {"finding_id": "LOW", "contract": "Fix", "function": "setOwner",
                 "invariant_category": "role_access", "severity": "Low",
                 "surfaceable": True, "grounding": "high"},
            ],
        }],
    }


def test_flags_unwired():
    assert P.FLAGS["is_gate"] is False
    assert P.FLAGS["research_only"] is True
    assert P.FLAGS["routes_in_production"] is False
    assert P.FLAGS["routed_manifest_ids"] == []


def test_self_test_passes():
    assert P._self_test() == 0


def test_body_extraction_and_features():
    bodies = P._function_bodies(_SRC)
    assert ("Fix", "drain") in bodies and "transfer" in bodies[("Fix", "drain")].lower()
    fdrain = P._features_for(bodies[("Fix", "drain")], "drain", "external")
    fset = P._features_for(bodies[("Fix", "setOwner")], "setOwner", "external")
    assert fdrain["actor_clarity"] == 1.0 and fset["actor_clarity"] == 0.0
    assert fdrain["consequence_value_movement"] == 1.0 and fset["consequence_value_movement"] == 0.0
    assert fdrain["exploitability_external_call"] == 1.0


def test_p115_signature_modifier_detected():
    """P115: a function whose ONLY access guard is a SIGNATURE modifier (onlyOwner) must be non-permissionless.
    Without the signature it is missed (the original bug); with it, actor_clarity drops to 0."""
    src = ("pragma solidity ^0.8.0;\ncontract C {\n"
           "  uint256 total;\n"
           "  function adminPoke(uint256 v) external onlyOwner { total = v; }\n}\n")
    bodies = P._function_bodies(src)
    sigs = P._function_signatures(src)
    body = bodies[("C", "adminPoke")]
    sig = sigs[("C", "adminPoke")]
    assert "onlyowner" in sig.lower(), "signature captures the modifier"
    assert P._features_for(body, "adminPoke", "external", signature=sig)["actor_clarity"] == 0.0
    # body-only (the pre-P115 behavior) would have missed it
    assert P._features_for(body, "adminPoke", "external")["actor_clarity"] == 1.0


def test_p119_caller_equality_role_gate_detected():
    """P119: caller-equality admin-role gates the body regex previously missed (operand-reversed / OR-clause /
    cast) must demote permissionless->privileged — incl. the secondswap unlistVesting form. Resource-ownership
    (`ownerOf(id) == msg.sender`) must NOT demote (preserves attacker-reachable funcs like forgeWithListed)."""
    # the P118 unlistVesting form: seller==msg.sender (reversed) || msg.sender==s2Admin() (cast, after ||)
    unlist = "{ require(listing.seller == msg.sender || msg.sender == IMarketplaceSetting(s).s2Admin()); st = 1; }"
    assert P._features_for(unlist, "unlistVesting", "external")["actor_clarity"] == 0.0
    # reversed-only role gate
    assert P._features_for("{ require(owner == msg.sender); x = 1; }", "f", "external")["actor_clarity"] == 0.0
    # RESOURCE-OWNERSHIP must stay permissionless (the forgeWithListed M-18 preservation)
    res = "{ require(nftContract.ownerOf(id) == msg.sender); x = 1; }"
    assert P._features_for(res, "forgeWithListed", "external")["actor_clarity"] == 1.0
    # no guard -> permissionless
    assert P._features_for("{ x = 1; }", "f", "external")["actor_clarity"] == 1.0


def test_p115_function_signatures_does_not_change_bodies_contract():
    """_function_bodies must still return {(c,f): body_str} (self_kill_validation depends on it)."""
    bodies = P._function_bodies(_SRC)
    assert isinstance(bodies, dict)
    assert isinstance(bodies[("Fix", "drain")], str)


def test_percentile_and_rank_math():
    assert P._percentile([0, 1, 2, 3], 3) == 1.0
    assert P._percentile([0, 1, 2, 3], 0) == 0.25
    assert P._percentile([], 1) == 0.0
    assert P._rank(sorted([0, 1, 2, 3], reverse=True), 3) == 1
    assert P._rank(sorted([5, 5, 1], reverse=True), 5) == 1  # ties share best rank


def test_awarded_function_ranked_within_surface(tmp_path):
    res = P.run_corpus(_corpus(tmp_path))
    rows = {r["finding_id"]: r for r in res["subjects"][0]["scored_findings"]}
    assert rows["HIGH"]["found_in_surface"] and rows["HIGH"]["has_body"]
    hi = rows["HIGH"]["per_feature"]["consequence_value_movement"]["percentile"]
    lo = rows["LOW"]["per_feature"]["consequence_value_movement"]["percentile"]
    assert hi >= lo


def test_discrimination_reports_lift_and_base_rate(tmp_path):
    res = P.run_corpus(_corpus(tmp_path))
    disc = res["discrimination"]
    for feat in P.FEATURES:
        assert feat in disc
        assert "lift" in disc[feat] and "surface_base_rate" in disc[feat]
        assert "mean_awarded_percentile" in disc[feat]


def test_probe_promotes_nothing(tmp_path):
    """No combined score / ordering / severity in the output — it ranks per-feature, it does not adjudicate."""
    res = P.run_corpus(_corpus(tmp_path))
    blob = json.dumps(res)
    assert "SUBMITTED" not in blob
    for s in res["subjects"]:
        for r in s["scored_findings"]:
            assert "combined_score" not in r and "final_rank" not in r and "severity_assigned" not in r


def test_deterministic(tmp_path):
    corpus = _corpus(tmp_path)
    a, b = P.run_corpus(corpus), P.run_corpus(corpus)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def _sources_present():
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    return all(Path(r).exists() for s in corpus["subjects"] for r in s["source_roots"])


@pytest.mark.skipif(not _sources_present(), reason="burned /tmp subject sources not present")
def test_live_every_awarded_function_is_measurable():
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))
    res = P.run_corpus(corpus)
    for s in res["subjects"]:
        for r in s["scored_findings"]:
            assert r["found_in_surface"] is True, f"{r['finding_id']} not in surface — corpus drifted"
            assert r["has_body"] is True, f"{r['finding_id']} body not extracted"
    # lift must be computed for every feature (selectivity honesty)
    assert all(res["discrimination"][f]["lift"] is not None for f in P.FEATURES)
