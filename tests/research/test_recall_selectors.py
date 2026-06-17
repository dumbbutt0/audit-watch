"""Isolated tests for the research-only F1/F2 recall selectors + guarded-downstream rule (P172)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "research"))
import recall_selectors as rs  # noqa: E402

_FLAGS_OK = lambda d: d.get("research_only") is True and d.get("routes_in_production") is False  # noqa: E731


def _write(tmp_path, rel, body):
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(body)
    return p


def test_f1_flags_setweights_missing_lifecycle_guard(tmp_path):
    _write(tmp_path, "src/Pool.sol",
           "contract Pool { function setWeights(uint[] w) external { weights = w; } }")
    hits = rs.f1_dynamic_weight_lifecycle(str(tmp_path))
    assert any(h["function"] == "setWeights" for h in hits)
    assert all(_FLAGS_OK(h) for h in hits)


def test_f1_skips_onlyowner_only_setter(tmp_path):
    _write(tmp_path, "src/Pool.sol",
           "contract Pool { function setWeights(uint[] w) external onlyOwner { weights = w; } }")
    hits = rs.f1_dynamic_weight_lifecycle(str(tmp_path))
    assert not any(h["function"] == "setWeights" for h in hits)  # role-gated-only → reject-first filter


def test_f1_excludes_vendored_lib(tmp_path):
    _write(tmp_path, "lib/oz/Pool.sol",
           "contract Pool { function setWeights(uint[] w) external { weights = w; } }")
    assert rs.f1_dynamic_weight_lifecycle(str(tmp_path)) == []  # hygiene: protocol_src only


def test_f2_flags_div_before_mul_math(tmp_path):
    _write(tmp_path, "src/MathGuard.sol",
           "contract MathGuard { function _normalizeWeightUpdates(int x) internal returns(int){ return (x / total) * scale; } }")
    hits = rs.f2_estimator_math(str(tmp_path))
    assert any(h["function"] == "_normalizeWeightUpdates" and "division_before_multiplication" in h["edges"] for h in hits)


def test_f2_ignores_math_without_edge(tmp_path):
    _write(tmp_path, "src/MathGuard.sol",
           "contract MathGuard { function _calculateQuantAMMGradient() internal returns(uint){ return a + b; } }")
    assert rs.f2_estimator_math(str(tmp_path)) == []  # no arithmetic edge


def test_guarded_downstream_rule():
    a = rs.guarded_downstream_flag({"clear_rationale": "guarded downstream by _guardQuantAMMWeights",
                                    "guard_in_scope": True, "guard_proven": False})
    assert a["do_not_clear"] is True and a["action"] == "needs_deep_pass"
    b = rs.guarded_downstream_flag({"clear_rationale": "guarded downstream", "guard_in_scope": True,
                                    "guard_proven": True})
    assert b["do_not_clear"] is False
    c = rs.guarded_downstream_flag({"clear_rationale": "no value path"})
    assert c["do_not_clear"] is False


def test_module_is_unwired():
    import subprocess
    r = subprocess.run(["grep", "-rq", "recall_selectors", "run_pipeline.sh", "config/agent_policy.json"],
                       cwd=str(ROOT))
    assert r.returncode != 0  # not referenced by pipeline/policy
