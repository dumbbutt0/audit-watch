"""Recall Lab regression — reasoning-gap sections reincorporated from the Panoptic Next-Core eval
(panoptic-2025-12-strict-eval, loop iteration). Locks that each authored §, its anchor, and its
mechanism_class entry are present so a future edit can't silently drop the knowledge.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _md(name):
    return (ROOT / "agents" / name).read_text()


def test_init_once_guard_section_present():
    t = _md("access_control.md")
    assert "panoptic-next-core H-01" in t
    assert "init-once guard" in t
    assert "minimal-proxy" in t and "constructors do NOT run" in t


def test_default_sentinel_reward_routing_section_present():
    t = _md("economic_attack.md")
    assert "panoptic-next-core M-15" in t
    assert "default code == 0" in t or "default/sentinel code" in t.lower()
    assert "JIT-capture" in t


def test_critical_path_math_revert_dos_section_present():
    t = _md("dos.md")
    assert "panoptic-next-core M-05/M-08" in t
    assert "getSqrtRatioAtTick" in t
    assert "division by zero" in t or "division-by-zero" in t


def test_partial_to_strong_underflow_dos_in_dos_section():
    # M-01 (liquidation subtraction underflow) folded into the critical-path math DoS section + the
    # partial->strong discipline (don't down-grade to dust when an underflow-DoS sits in the same fn).
    t = _md("dos.md")
    assert "panoptic-next-core M-05/M-08/M-01" in t
    assert "thresholdCross - balanceCross" in t
    assert "PARTIAL->STRONG DISCIPLINE" in t


def test_partial_to_strong_unreachable_guard_in_logic():
    t = _md("logic.md")
    assert "panoptic-next-core M-17" in t
    assert "UNREACHABLE" in t and "TRACE REACHABILITY" in t
    assert "SIGNAL TO FINISH THE TRACE" in t  # the anti-hedge discipline


def test_partial_to_strong_bad_debt_par_exit_in_economic():
    t = _md("economic_attack.md")
    assert "panoptic-next-core M-19" in t
    assert "unrealized" in t.lower() and "socialize" in t.lower()


def test_mechanism_classes_registered():
    classes = json.loads((ROOT / "config" / "mechanism_classes.json").read_text())["classes"]
    for slug, agent in [("init-once-guard-missing", "access_control"),
                        ("default-sentinel-reward-routing-jit", "economic_attack"),
                        ("critical-path-math-revert-dos", "dos"),
                        ("unreachable-guard-branch-ordering", "logic"),
                        ("bad-debt-socialization-par-exit", "economic_attack")]:
        assert slug in classes, slug
        assert classes[slug]["agent"] == agent
        assert classes[slug]["status"] == "reincorporated"
        assert any("panoptic" in e for e in classes[slug]["awarded_examples"])
    # M-01 partial now linked into the dos class.
    assert "panoptic-2025-12-strict-eval:M-01" in classes["critical-path-math-revert-dos"]["awarded_examples"]
