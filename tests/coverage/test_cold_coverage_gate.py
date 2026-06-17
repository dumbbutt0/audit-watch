"""Recall Lab — full-coverage gate for ingested cold passes (scripts/recall_lab_loop.py cold_coverage).

Locks the rule the Cap experiment proved: a thin cold pass must BLOCK before reveal (it manufactures phantom
coverage-gap misses). Gate is green only when every in-scope SUBSTANTIVE file appears in merged_findings._coverage[];
interfaces/ and storage *StorageUtils.sol are boilerplate (reported, non-blocking).
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import recall_lab_loop as rll  # noqa: E402


@pytest.fixture
def aud(tmp_path, monkeypatch):
    monkeypatch.setattr(rll, "AUDITS", tmp_path)
    adir = tmp_path / "X"
    (adir / "output").mkdir(parents=True)
    return adir


def _scope(adir, files):
    (adir / "scope.json").write_text(json.dumps({"in_scope_files": [{"file": f} for f in files]}))


def _coverage(adir, files):
    (adir / "output" / "merged_findings.json").write_text(
        json.dumps({"_coverage": [{"file": f, "depth": "deep"} for f in files]}))


def _adjfile(adir):
    (adir / "output" / "eval_ready").mkdir(parents=True, exist_ok=True)
    p = adir / "output" / "eval_ready" / "adjudication.json"
    p.write_text(json.dumps({"summary": {}}))
    return p


# --- require_full_coverage: the AUTO-ENFORCED gate (always-on, mirrors production override) -------------------

def test_require_not_gated_without_scope_json(aud):
    # archived/heuristic contest (no scope.json) -> never gated, even with empty coverage
    _coverage(aud, [])
    assert rll.require_full_coverage("X") == 0


def test_require_blocks_thin_scoped(aud):
    _scope(aud, ["oracle/PriceOracle.sol", "vault/Vault.sol", "lendingPool/Lender.sol", "interfaces/IVault.sol"])
    _coverage(aud, ["oracle/PriceOracle.sol"])  # 1 of 3 substantive
    assert rll.require_full_coverage("X") == 1


def test_require_passes_full_scoped(aud):
    _scope(aud, ["oracle/PriceOracle.sol", "vault/Vault.sol", "interfaces/IVault.sol"])
    _coverage(aud, ["oracle/PriceOracle.sol", "vault/Vault.sol"])
    assert rll.require_full_coverage("X") == 0


def test_require_override_passes_and_stamps(aud, monkeypatch):
    _scope(aud, ["oracle/PriceOracle.sol", "vault/Vault.sol"])
    _coverage(aud, ["oracle/PriceOracle.sol"])  # thin
    adj = _adjfile(aud)
    monkeypatch.setenv("AUDITWATCH_COVERAGE_OVERRIDE", "1")
    assert rll.require_full_coverage("X") == 0
    s = json.loads(adj.read_text())["summary"]
    assert s.get("coverage_override") is True and s.get("coverage_unexamined") == 1


def test_boilerplate_classifier():
    assert rll._is_boilerplate("interfaces/IVault.sol")
    assert rll._is_boilerplate("storage/VaultStorageUtils.sol")
    assert not rll._is_boilerplate("vault/Vault.sol")
    assert not rll._is_boilerplate("oracle/PriceOracle.sol")


def test_thin_pass_blocks(aud, capsys):
    _scope(aud, ["oracle/PriceOracle.sol", "vault/Vault.sol", "lendingPool/Lender.sol", "interfaces/IVault.sol"])
    _coverage(aud, ["oracle/PriceOracle.sol"])  # only 1 of 3 substantive
    assert rll.cold_coverage("X", block=True) == 1
    out = capsys.readouterr().out
    assert "vault/Vault.sol" in out and "lendingPool/Lender.sol" in out


def test_full_substantive_coverage_passes(aud):
    # interfaces boilerplate unread -> still passes (only substantive blocks)
    _scope(aud, ["oracle/PriceOracle.sol", "vault/Vault.sol", "interfaces/IVault.sol", "storage/VaultStorageUtils.sol"])
    _coverage(aud, ["oracle/PriceOracle.sol", "vault/Vault.sol"])
    assert rll.cold_coverage("X", block=True) == 0


def test_no_block_reports_but_returns_zero(aud):
    _scope(aud, ["oracle/PriceOracle.sol", "vault/Vault.sol"])
    _coverage(aud, ["oracle/PriceOracle.sol"])
    assert rll.cold_coverage("X", block=False) == 0  # report-only


def test_basename_match_tolerates_path_prefix(aud):
    # _coverage may log a slightly different prefix; basename match still counts it covered.
    _scope(aud, ["vault/libraries/VaultLogic.sol"])
    _coverage(aud, ["VaultLogic.sol"])
    assert rll.cold_coverage("X", block=True) == 0
