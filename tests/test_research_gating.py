"""T9 — the un-wired research platform is gated behind one switch + a deselectable pytest marker, with NO change
to production routing or default test coverage."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_research_platform_flag_present_and_off():
    pol = json.loads((ROOT / "config" / "agent_policy.json").read_text())
    rp = pol["research_platform"]
    assert rp["enabled"] is False  # opt-in by default


def test_research_marker_registered_in_conftest():
    cf = (ROOT / "tests" / "conftest.py").read_text()
    assert "research:" in cf and "RESEARCH_DIRS" in cf and "add_marker" in cf


def test_research_dir_is_marked_and_deselectable():
    # `-m "not research"` must deselect tests under tests/research (collection-only, fast)
    r = subprocess.run([sys.executable, "-m", "pytest", "tests/research", "-m", "not research",
                        "--collect-only", "-q"], cwd=str(ROOT), capture_output=True, text=True, timeout=180)
    out = r.stdout + r.stderr
    assert "deselected" in out and "no tests collected" in out  # the whole research dir is marked + deselected
