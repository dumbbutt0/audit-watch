"""T4 — mechanical blind wall. seal moves the answer key out of the working tree; check fails when it's reachable
and passes when vaulted; reveal restores it; leakage flags verbatim answer-key title overlap in merged_findings."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import assert_blind as ab  # noqa: E402


@pytest.fixture
def env(tmp_path, monkeypatch):
    audits = tmp_path / "audits"
    (audits / "X" / "_sealed_answer_key").mkdir(parents=True)
    (audits / "X" / "output").mkdir(parents=True)
    (audits / "X" / "_sealed_answer_key" / "report.md").write_text(
        "# Issue H-1: reentrancy in withdraw drains vault balance\n")
    monkeypatch.setattr(ab, "ROOT", tmp_path)
    monkeypatch.setattr(ab, "AUDITS", audits)
    monkeypatch.setattr(ab, "VAULT", tmp_path / "vault")
    return tmp_path, audits


def test_check_fails_before_seal(env):
    assert ab.check("X") == 1                      # key reachable -> NOT blind


def test_seal_moves_key_then_check_passes(env):
    tmp, audits = env
    assert ab.seal("X") == 0
    assert not (audits / "X" / "_sealed_answer_key").exists()   # gone from working tree
    assert (tmp / "vault" / "X" / "_sealed_answer_key" / "report.md").exists()
    assert (audits / "X" / "output" / "_blind_pass.json").exists()
    assert ab.check("X") == 0                      # vaulted -> BLIND OK


def test_reveal_restores(env):
    tmp, audits = env
    ab.seal("X")
    assert ab.reveal("X") == 0
    assert (audits / "X" / "_sealed_answer_key" / "report.md").exists()


def test_leakage_flags_verbatim_title_overlap(env):
    tmp, audits = env
    # a cold finding whose title clearly echoes the awarded title -> leakage (contamination signal)
    (audits / "X" / "output" / "merged_findings.json").write_text(json.dumps({"findings": [
        {"id": "RE-1", "title": "reentrancy in withdraw drains vault balance via callback"}]}))
    assert ab.leakage("X") == 1


def test_leakage_clean_when_titles_differ(env):
    tmp, audits = env
    (audits / "X" / "output" / "merged_findings.json").write_text(json.dumps({"findings": [
        {"id": "AR-1", "title": "integer truncation in fee math underpays protocol"}]}))
    assert ab.leakage("X") == 0
