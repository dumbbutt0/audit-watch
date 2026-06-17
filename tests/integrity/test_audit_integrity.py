"""Workspace-integrity preflight. Catches the k2 failure mode: a workspace whose meta.language disagrees with
its findings' file extensions (a different audit overwrote it), and stale findings with no source. READ-ONLY;
contaminated => exit 2 so the eval/scoring preflight can block."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import check_audit_integrity as cai  # noqa: E402


@pytest.fixture
def audits(tmp_path, monkeypatch):
    d = tmp_path / "audits"
    d.mkdir()
    monkeypatch.setattr(cai, "_AUDITS_DIR", d)
    return d


def _mk(audits, aid, *, language, findings, with_source_ext=None):
    a = audits / aid
    (a / "output").mkdir(parents=True)
    (a / "meta.json").write_text(json.dumps({"audit_id": aid, "language": language}))
    (a / "output" / "merged_findings.json").write_text(json.dumps({"findings": findings}))
    if with_source_ext:
        src = a / "contracts" / "_sources"
        src.mkdir(parents=True)
        (src / f"x{with_source_ext}").write_text("// src")
    return a


def test_contaminated_lang_mismatch(audits):
    # k2 shape: meta rust, findings .sol -> contaminated.
    _mk(audits, "k2", language="rust",
        findings=[{"id": "F-1", "location": "contracts/origin/AerodromeAMOStrategy.sol:806"}],
        with_source_ext=".sol")
    r = cai.check_audit("k2")
    assert r["status"] == "contaminated"
    assert any("lang_mismatch" in i for i in r["issues"])


def test_multilang_label_is_not_a_mismatch(audits):
    # meta 'solidity+rust', findings .sol -> .sol's lang (solidity) is in the set -> OK (no FP).
    _mk(audits, "recall", language="solidity+rust",
        findings=[{"id": "F-1", "location": "src/Vault.sol:10"}], with_source_ext=".sol")
    assert cai.check_audit("recall")["status"] == "ok"


def test_empty_sources_with_findings_warns(audits):
    _mk(audits, "stale", language="solidity",
        findings=[{"id": "F-1", "location": "src/Vault.sol:10"}])  # no _sources written
    r = cai.check_audit("stale")
    assert r["status"] == "warn"
    assert any("empty_sources" in i for i in r["issues"])


def test_clean_workspace_ok(audits):
    _mk(audits, "good", language="move",
        findings=[{"id": "F-1", "location": "sources/amm.move:42"}], with_source_ext=".move")
    assert cai.check_audit("good")["status"] == "ok"


def test_main_exit_code_blocks_on_contaminated(audits, monkeypatch, capsys):
    _mk(audits, "k2", language="rust",
        findings=[{"id": "F-1", "location": "x.sol"}], with_source_ext=".sol")
    monkeypatch.setattr(sys, "argv", ["x", "k2"])
    assert cai.main() == 2                                   # contaminated -> non-zero (preflight blocks)
    monkeypatch.setenv("AUDITWATCH_INTEGRITY_OVERRIDE", "1")
    assert cai.main() == 0                                   # override clears the block
