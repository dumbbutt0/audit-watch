"""Recall Lab — heuristic miss-detector (detect misses even in already-evaluated contests).

Locks the CONSERVATIVE behavior: bias toward MISSED; recall credit requires real function/mechanism evidence;
file/contract overlap alone does NOT grant credit (only sets read_file). No protocol-specific strings.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import adjudicate as adj  # noqa: E402


def _aw(title, funcs=(), contracts=(), files=(), text=""):
    return {"id": "X-1", "severity": "High", "title": title, "functions": list(funcs),
            "contracts": list(contracts), "files": list(files), "text": text or title}


def _c(cid, title, file="", function="", contract="", description=""):
    return {"id": cid, "title": title, "file": file, "function": function,
            "contract": contract, "description": description}


def test_no_overlap_is_missed():
    aw = _aw("Reentrancy in withdraw drains vault", funcs=["withdraw"], contracts=["Vault"])
    cands = [_c("C1", "Oracle staleness in price feed", file="Oracle.sol", function="getPrice")]
    r = adj._auto_label(aw, cands)
    assert r["label"] == "MISSED" and r["confidence"] == "high" and r["matched_candidate_id"] is None


def test_empty_candidates_via_default():
    # No candidates -> the caller skips auto; _auto_label with [] yields MISSED (nothing to match).
    assert adj._auto_label(_aw("anything"), [])["label"] == "MISSED"


def test_function_match_is_same_area_at_least():
    aw = _aw("Bad accounting in settleLiquidation", funcs=["settleLiquidation"], contracts=["CollateralTracker"])
    cands = [_c("C1", "settleLiquidation rounding", function="settleLiquidation")]
    r = adj._auto_label(aw, cands)
    assert r["label"] in ("SAME_AREA", "STRONG") and r["matched_candidate_id"] == "C1"


def test_function_plus_strong_mechanism_is_strong():
    aw = _aw("Liquidation underflow blocks insolvent account settlement",
             funcs=["settleLiquidation"],
             text="liquidation underflow blocks insolvent account settlement collateral")
    cands = [_c("C1", "settleLiquidation underflow on insolvent collateral settlement",
                function="settleLiquidation",
                description="underflow blocks insolvent liquidation settlement of collateral account")]
    assert adj._auto_label(aw, cands)["label"] == "STRONG"


def test_file_overlap_alone_does_not_grant_credit_but_sets_read_file():
    # Same FILE, totally different mechanism + no function match -> MISSED, but read_file True (file examined).
    aw = _aw("init() re-initialization lets attacker overwrite admin", funcs=["init"],
             contracts=["BuilderWallet"], files=["RiskEngine.sol"],
             text="missing access control init once guard overwrite admin")
    cands = [_c("C1", "Guardian safe-mode monotonicity not verified", file="contracts/in_scope/RiskEngine.sol",
                description="guardian can only increase safe mode never relax isSafeMode oraclepack lockmode")]
    r = adj._auto_label(aw, cands)
    assert r["label"] == "MISSED"
    assert r["read_file"] is True  # file was examined -> reasoning-gap miss, not coverage-gap
