"""P113: fresh top-ranked assisted discovery run — RESEARCH-ONLY, un-wired.

Proves selection is mechanical/deterministic (excludes confirmed controls, records a skip log, picks the global
recommended #1), and that the workflow reaches a TRUTHFUL terminal in the allowed set without unsafe promotion:
no source-backed evidence -> NEEDS_CONTEXT; VALIDATED-without-a-runner -> HARNESS_UNAVAILABLE (no package); a
submission package / READY state appears ONLY on execution-backed CONFIRMED_RUNTIME; never auto-submit / never
severity.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "assisted"))
sys.path.insert(0, str(ROOT / "scripts" / "investigation"))
import assisted_fresh_run as F  # noqa: E402
import validate_candidate_invariant as V  # noqa: E402

CORPUS_PATH = ROOT / "documentation" / "research" / "assisted_mode" / "p105" / "benchmark_corpus.json"
_needs = pytest.mark.skipif(not CORPUS_PATH.is_file(), reason="P105 corpus not present")


def _corpus():
    return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))

_GT = {"localized_mechanism": "x", "controlled_inputs": "x", "pre_state": "x", "operation_trace": "x",
       "boundary_cases": "x", "post_state": "x", "concrete_outcome": "PASS"}
_GO = {"relied_upon_invariant": "x", "mechanism_class": "accounting", "counterexample_found": True,
       "counterexample_trace": "x"}
_GI = {"impact_class": "medium", "proven_magnitude": "significant", "source_true": True, "source_backed": True,
       "material_consequence": ["fund_loss"]}
_EVID = {"depth_trace": _GT, "adversarial_ordering": _GO, "impact_assessment": _GI}


def test_flags_unwired():
    assert F.FLAGS["is_gate"] is False
    assert F.FLAGS["routes_in_production"] is False
    assert F.FLAGS["routed_manifest_ids"] == []


def test_terminals_and_controls_defined():
    assert {"CONFIRMED_RUNTIME", "KILLED_RUNTIME", "HARNESS_UNAVAILABLE", "NEEDS_CONTEXT"} <= F.TERMINALS
    assert ("iq-ai-2025-01", "LiquidityManager", "moveLiquidity") in F.CONFIRMED_CONTROLS
    assert ("secondswap-2024-12", "SecondSwap_Marketplace", "spotPurchase") in F.CONFIRMED_CONTROLS


@_needs
def test_selection_deterministic():
    a, b = F.select_candidate(_corpus()), F.select_candidate(_corpus())
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


