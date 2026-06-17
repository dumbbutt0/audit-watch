"""Phase-13 value_flow_v2 generalization shapes (deterministic, 0-FP-gated on anchors)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import value_flow_parity_taxonomy as vfp  # noqa: E402


def _shapes(name, snippet, sig=""):
    return {c["shape"]: c["confidence"] for c in vfp.classify_v2_shapes(name, sig, snippet)}


# ---- loop_index_anomaly (Renzo H-08) ----
def test_loop_index_anomaly_medium():
    body = ("for (uint i=0;i<a;){ for (uint j=0;j<b;){ x = arr[j]; y = arr[j];"
            " z = lookup(arr[i], arr[j].bal); } }")
    assert _shapes("calculateTVLs", body).get("loop_index_anomaly") == "medium"


def test_loop_index_2d_field_not_flagged():
    """scores[v_i] (local) vs .scores[g_i] (field) is legitimate 2D access, not an anomaly."""
    body = "for(uint g_i=0;g_i<n;){ for(uint v_i=0;v_i<m;){ scores[v_i] = validations[v_i].scores[g_i]; } }"
    assert "loop_index_anomaly" not in _shapes("finalize", body)


# ---- identity_resolution_then_misuse (Velodrome H-02) ----
def test_identity_misuse_medium():
    body = ("require(_isApprovedOrOwner(msg.sender, _tokenId));"
            " address owner = ownerOf(_tokenId);"
            " _removeTokenFrom(msg.sender, _tokenId);")
    assert _shapes("_burn", body).get("identity_resolution_then_misuse") == "medium"


def test_identity_fixed_version_not_flagged():
    """The FIXED version uses the resolved owner; only the auth guard uses msg.sender -> no flag."""
    body = ("require(_isApprovedOrOwner(msg.sender, _tokenId));"
            " address owner = ownerOf(_tokenId);"
            " _removeTokenFrom(owner, _tokenId);")
    assert "identity_resolution_then_misuse" not in _shapes("_burn", body)


def test_identity_auth_guard_alone_not_flagged():
    """owner resolved + only an auth predicate uses msg.sender -> not a misuse."""
    body = "address owner = ownerOf(id); require(_isApprovedOrOwner(msg.sender, id)); _move(owner, id);"
    assert "identity_resolution_then_misuse" not in _shapes("f", body)


# ---- mapping_key_inconsistency (Renzo H-02) ----
def test_mapping_key_inconsistency_medium():
    body = "return queuedShares[address(this)] == 0 ? a : b + view(queuedShares[address(token)]);"
    assert _shapes("getTokenBalanceFromStrategy", body, "function f(IERC20 token)").get(
        "mapping_key_inconsistency") == "medium"


def test_mapping_consistent_keys_not_flagged():
    body = "x = m[address(this)] + m[address(this)];"
    assert "mapping_key_inconsistency" not in _shapes("f", body)


# ---- off_by_one_index demoted to LOW (FP-prone) ----
def test_off_by_one_is_low_only():
    body = "a = c[k-1].t; b = c[k-1].t; d = c[k].voted;"
    s = _shapes("_writeCheckpoint", body)
    assert s.get("off_by_one_index") == "low"  # never routable


# ---- the v1 anchor shape is untouched ----
def test_v1_threshold_shape_preserved():
    body = "if (params.amount < state.riskConfig.minimumCreditBorrowAToken) revert MinCredit();"
    cands = vfp.classify_intra("validateSellCreditMarket", "", body)
    assert any(c["shape"] == "threshold_value_mismatch" and c["confidence"] == "medium" for c in cands)
