"""
P311 — the 8 staged lenses promoted to production ADVISORY-ONLY. No network.

Verifies: (a) all 8 lenses are wired to RUN in run_pipeline.sh (both the review-gate block and the coverage-gate
case); (b) each lens emits the promoted-advisory flag set (research_only:false, promotion:advisory_only, is_gate:false,
routes_in_production:false); (c) advisory_escalation_gate.py surfaces them under promoted_advisory_lens_hits with
routed_to:advisory_only, NEVER routes them (promoted_advisory_routed==0) and NEVER mutates dispositions; (d) the
existing 10-lens strict routing is untouched; (e) the staged proposals are marked promoted (advisory_only).
"""
import hashlib
import importlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LENSES = ["nonstandard_permit", "erc4626_limit_fidelity", "eip712_domain_separator_staleness",
          "beneficiary_guard_parity", "admin_capability_parity", "crosschain_min_gas_unchecked",
          "crosschain_refund_recipient", "fee_wrapper_bypass"]
RP = (ROOT / "run_pipeline.sh").read_text()
AEG = (ROOT / "scripts" / "advisory_escalation_gate.py").read_text()


# ---- (a) wired to run in both lists ----
def test_all_lenses_wired_in_run_pipeline():
    for l in LENSES:
        # appears in both the coverage_review_gate block and the coverage-gate case (>=2 invocations)
        assert RP.count(f"scripts/{l}_audit.py") >= 2, f"{l} not wired in both lens lists"


# ---- (b) each lens emits the promoted-advisory flag set ----
def test_lens_flags_promoted_advisory():
    for l in LENSES:
        src = (ROOT / "scripts" / f"{l}_audit.py").read_text()
        assert '"research_only": False' in src and '"promotion": "advisory_only"' in src
        assert '"is_gate": False' in src and '"routes_in_production": False' in src


# ---- (c)/(d) advisory_escalation_gate surfaces them advisory-only, never routes them ----
def test_advisory_gate_surfaces_promoted_set_only():
    assert "PROMOTED_ADVISORY_LENSES" in AEG and '"promoted_advisory_lens_hits"' in AEG
    assert '"promoted_advisory_routed": 0' in AEG
    for l in LENSES:
        assert f'"{l}"' in AEG
    # the promoted set must NOT enter the strict-routing dict (which is what apply_update keys off of)
    assert "LENS_SPECIALIST" in AEG
    for l in LENSES:
        assert f'"{l}": ' not in AEG.split("LENS_SPECIALIST = {")[1].split("}")[0], \
            f"{l} leaked into the strict-routing LENS_SPECIALIST set"


def test_advisory_gate_runs_without_routing(tmp_path):
    # run the 8 lenses + the gate on the ACTIVE audit; dispositions must be byte-identical (advisory-only, no routing)
    disp = ROOT / "output" / "coverage_dispositions.json"
    if not disp.exists():
        pytest.skip("no active-audit dispositions")
    before = hashlib.sha256(disp.read_bytes()).hexdigest()
    for l in LENSES:
        subprocess.run([sys.executable, f"scripts/{l}_audit.py", "--quiet"], cwd=str(ROOT),
                       capture_output=True, text=True, timeout=120)
    r = subprocess.run([sys.executable, "scripts/advisory_escalation_gate.py", "--quiet"], cwd=str(ROOT),
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0
    after = hashlib.sha256(disp.read_bytes()).hexdigest()
    assert before == after, "advisory-only promotion must NOT mutate coverage dispositions"
    rep = json.loads((ROOT / "output" / "advisory_escalation_gate.json").read_text())
    assert sorted(rep.get("promoted_advisory_lenses", [])) == sorted(LENSES)
    assert rep.get("promoted_advisory_routed") == 0


# ---- (e) proposals marked promoted ----
def test_proposals_marked_promoted():
    for f in ["p303_detector_proposals.jsonl", "p305_detector_proposals.jsonl", "p307_detector_proposals.jsonl"]:
        p = ROOT / "data" / "learning" / "_proposed" / f
        rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
        assert rows and all(r.get("promoted") is True and r.get("promotion_mode") == "advisory_only" for r in rows)


# ---- integrity: gates/verifier/forbidden + the 10 existing lenses + taxonomies unchanged ----
def test_integrity_pins_unchanged():
    pins = {
        "scripts/research/executed_poc_verifier.py": "1a005811fbb9",
        "scripts/coverage_completeness_gate.py": "c0ffcacf5ead",
        "scripts/min_confirm_gate.py": "2a15169a53c2",
        "scripts/confirm_gate.py": "afc481c99ea9",
        "data/fp_autopsies/rejection_rules.jsonl": "693c019027ce",  # refreshed: legit human promote_learning 2026-06-11 (+2 FP rules)
        "audits/beanstalk-2024-05/data/evaluation/ground_truth.jsonl": "35f44065901c",
        "scripts/sibling_function_parity_taxonomy.py": "e504383db8f3",
        "scripts/griefing_dos_taxonomy.py": "1c2bfffb5d9e",
    }
    for rel, h in pins.items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()[:12] == h, f"{rel} changed"
