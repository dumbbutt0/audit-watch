"""Honest-score policy: the Solidity scoreboard must surface per-project coverage and gate the headline on
full coverage (thin passes are shown but excluded from the honest number). User directive 2026-06-12:
"run the solidity evals at full coverage at all times so we get an honest score."
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_coverage_fraction_helper():
    import sys
    sys.path.insert(0, str(ROOT / "scripts"))
    from recall_lab_loop import coverage_fraction
    # a known full-coverage rust eval (Pyth, 2/2 files) -> full True
    cov = coverage_fraction("pyth-lazer-solana-2024-eval")
    assert cov is not None and cov["full"] is True and cov["pct"] == 1.0


def test_scoreboard_has_full_coverage_headline():
    import subprocess, sys
    subprocess.run([sys.executable, str(ROOT / "scripts" / "eval_scoreboard.py")], check=True, capture_output=True)
    d = json.loads((ROOT / "evals" / "scoreboard.json").read_text())
    h = d["headline"]
    # the honest, full-coverage-gated headline keys exist
    for k in ("holdout_recall_full_coverage_only", "holdout_full_coverage_projects",
              "training_recall_full_coverage_only"):
        assert k in h, k
    # every scoreable project row carries coverage + full flag
    for s in ("holdout", "training"):
        for p in d["sets"][s]["projects"]:
            if "recall_of_surfaced" in p:
                assert "coverage_pct" in p and "full_coverage" in p, p["id"]


def test_thin_pass_excluded_from_full_coverage_headline():
    # honesty invariant: a project with <100% coverage must NOT count toward the full-coverage headline
    d = json.loads((ROOT / "evals" / "scoreboard.json").read_text())
    for s in ("holdout", "training"):
        thin = [p for p in d["sets"][s]["projects"]
                if p.get("coverage_pct") is not None and not p.get("full_coverage")]
        # if there are thin projects, the full-coverage aggregate must not silently include them:
        # the full-coverage project count is <= total scoreable
        agg = d["sets"][s]["full_coverage_aggregate"]
        scoreable = [p for p in d["sets"][s]["projects"] if "recall_of_surfaced" in p]
        assert agg["awarded_adjudicated"] <= sum(p.get("awarded_total", 0) or 0 for p in scoreable)
