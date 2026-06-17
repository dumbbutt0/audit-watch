"""Recall Lab regression — the 4 reasoning-gap sections from the Numa eval (numa-2024-12-eval), authored from
misses in files the cold pass DID read (M-1, M-10, M-13, M-14). The other 12 Numa misses were COVERAGE gaps in
the fork/small files the fast-forward skipped (recorded in adjudication.json, not prompt-addressable here).
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _md(n):
    return (ROOT / "agents" / n).read_text()


def test_bps_sqrt_precision_loss():
    t = _md("logic.md")
    assert "numa M-10" in t and "setMaxSpotOffsetBps" in t and "sqrt" in t.lower()


def test_round_boundary_decay_reset():
    t = _md("logic.md")
    assert "numa M-1" in t and "round-to-1" in t and "decay" in t.lower()


def test_controller_fed_pre_fee_amount():
    t = _md("economic_attack.md")
    assert "numa M-13" in t and "PID" in t and "pre-fee" in t.lower()


def test_pct_cap_below_abs_floor():
    t = _md("dos.md")
    assert "numa M-14" in t and "MAX < MIN" in t


def test_numa_classes_registered():
    c = json.loads((ROOT / "config" / "mechanism_classes.json").read_text())["classes"]
    for slug, agent in [("bps-sqrt-precision-loss", "logic"),
                        ("round-boundary-decay-reset", "logic"),
                        ("controller-fed-pre-fee-amount", "economic_attack"),
                        ("pct-cap-below-abs-floor", "dos")]:
        assert slug in c and c[slug]["agent"] == agent and c[slug]["status"] == "reincorporated"
        assert any("numa-2024-12-eval" in e for e in c[slug]["awarded_examples"])
