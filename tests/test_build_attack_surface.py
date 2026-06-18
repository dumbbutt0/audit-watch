"""build_attack_surface.py derives output/attack_surface.json from the coverage manifest in the
api-free path (analyze-resume), so /ite-audit + cross_agent_connector always have the artifact they
read. Pins: correct projection + score-desc ordering + _derived_from marker; idempotent refresh of its
own output; and the no-clobber guard that preserves an LLM/agent-authored attack_surface.json."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_attack_surface as bas  # noqa: E402


def _write_manifest(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "coverage_manifest.json").write_text(json.dumps({"items": [
        {"kind": "function", "name": "lowFn", "contract": "C", "file": "C.sol",
         "visibility": "external", "attack_surface_score": 2, "tags": []},
        {"kind": "function", "name": "hotFn", "contract": "C", "file": "C.sol",
         "visibility": "public", "attack_surface_score": 5, "tags": ["oracle"],
         "external_calls": True, "in_tainted_sink": True},
        {"kind": "constructor", "name": "constructor", "contract": "C", "file": "C.sol",
         "visibility": "public", "attack_surface_score": 3, "tags": []},
        {"kind": "constant", "name": "FEE", "contract": "C", "file": "C.sol",
         "attack_surface_score": 1, "tags": ["accounting"]},  # non-function -> excluded
    ]}))


@pytest.fixture
def patched(tmp_path, monkeypatch):
    out = tmp_path / "output"
    _write_manifest(out)
    monkeypatch.setattr(bas, "audit_path", lambda *p: tmp_path.joinpath(*p))
    return out


def test_derives_sorted_functions_with_marker(patched):
    assert bas.main([]) == 0
    d = json.loads((patched / "attack_surface.json").read_text())
    assert d["_derived_from"] == "coverage_manifest.json"
    names = [f["name"] for f in d["functions"]]
    assert names == ["hotFn", "constructor", "lowFn"]          # score-desc, constant excluded
    assert d["function_count"] == 3 and d["high_surface_count"] == 2
    assert d["functions"][0]["external_calls"] is True and d["functions"][0]["in_tainted_sink"] is True


def test_idempotent_refresh_of_own_output(patched):
    assert bas.main([]) == 0
    # re-run without --force: it owns the file (has _derived_from) -> refreshes, stays valid
    assert bas.main([]) == 0
    d = json.loads((patched / "attack_surface.json").read_text())
    assert d["_derived_from"] == "coverage_manifest.json" and d["function_count"] == 3


def test_no_clobber_of_agent_authored(patched):
    # an LLM/agent file has no _derived_from marker -> must be preserved
    (patched / "attack_surface.json").write_text(json.dumps(
        {"functions": [{"name": "AGENT", "attack_surface_score": 9}]}))
    assert bas.main([]) == 0
    d = json.loads((patched / "attack_surface.json").read_text())
    assert d["functions"][0]["name"] == "AGENT"               # untouched
    # --force overrides
    assert bas.main(["--force"]) == 0
    d2 = json.loads((patched / "attack_surface.json").read_text())
    assert d2.get("_derived_from") == "coverage_manifest.json"
