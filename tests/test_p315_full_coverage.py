"""
P315 — full workflow reaches every necessary (in-scope) file. No network.

Verifies: (a) run_pipeline.sh has the mandatory Step 3.85 coverage drive + loud override warning + always-staged
sweep; (b) the ite-audit skill + specialist prompts + context pack no longer drop low-signal in-scope files;
(c) generate_review_gate.py surfaces necessary-file coverage; (d) coverage_sweep_prepare bundles EVERY in-scope
unassigned item (the mandatory sweep covers all necessary files); (e) the security-critical gate + evidence
enforcement + verifier + forbidden-5 are byte-identical (no weakening).
"""
import hashlib
import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

RP = (ROOT / "run_pipeline.sh").read_text()
SKILL = (ROOT / ".claude" / "skills" / "ite-audit" / "SKILL.md").read_text()
CP = (ROOT / "scripts" / "generate_context_pack.py").read_text()
RG = (ROOT / "scripts" / "generate_review_gate.py").read_text()


# ---- (a) run_pipeline mandatory coverage drive ----
def test_run_pipeline_mandatory_drive():
    assert "Step 3.85" in RP and "Mandatory full-coverage drive" in RP
    # the sweep is staged proactively inside coverage_review_gate (always), not only on gate-fail
    assert RP.count("coverage_sweep_prepare.py") >= 2
    # loud override warning
    assert "AUDITWATCH_COVERAGE_OVERRIDE" in RP and "OVERRIDDEN" in RP
    # fail-closed gate still present + unchanged invocation
    assert "coverage_completeness_gate.py" in RP


# ---- (b) no silent file dropping ----
def test_skill_no_skip_language():
    assert "do not re-derive the whole surface area" not in SKILL
    assert "lower priority unless your specialty" not in SKILL
    # The skill must mandate opening every in-scope file in remit (no silent skip of specialty-relevant files).
    # Reworded 2026-06 from "no in-scope file is skipped" to the stronger, more specific phrasing below — assert
    # the current canonical guarantee, not the stale exact string.
    assert "OPEN EVERY IN-SCOPE FILE" in SKILL
    assert "do NOT defer a file your specialty touches" in SKILL
    # ...backed by the fail-closed coverage gate / open-all-files enforcement
    assert "fail-closed coverage gate" in SKILL.lower() or "open all in-scope files in remit" in SKILL.lower()


def test_agent_prompts_non_skip_note():
    for a in ["reentrancy.md", "access_control.md"]:
        t = " ".join((ROOT / "agents" / a).read_text().lower().split())  # collapse wrapping whitespace
        assert "mandatory coverage sweep" in t and "not skipped" in t, f"{a} missing non-skip note"


def test_context_pack_surfaces_all_clusters():
    assert "Remaining in-scope — mandatory sweep" in CP
    # the old "drop to a one-line footnote" wording is gone
    assert "Lower priority — no High/Med/sink signal:" not in CP


# ---- (c) review gate surfaces necessary-file coverage ----
def test_review_gate_coverage_section():
    assert "_coverage_section" in RG and "Necessary-file coverage" in RG
    assert "lines += _coverage_section()" in RG


# ---- (d) the mandatory sweep covers EVERY in-scope unassigned item ----
def test_sweep_prepare_covers_all_in_scope(tmp_path, monkeypatch):
    import audit_context
    prep = importlib.import_module("coverage_sweep_prepare")
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    items = [
        {"id": "function:C:a#1", "kind": "function", "contract": "C", "name": "a", "file": "C.sol",
         "signature": "", "source_span": {"start_line": 1, "end_line": 2}, "in_scope": True, "attack_surface_score": 5},
        {"id": "function:C:b#2", "kind": "function", "contract": "C", "name": "b", "file": "C.sol",
         "signature": "", "source_span": {"start_line": 3, "end_line": 4}, "in_scope": True, "attack_surface_score": 0},
        {"id": "function:D:c#3", "kind": "function", "contract": "D", "name": "c", "file": "D.sol",
         "signature": "", "source_span": {"start_line": 1, "end_line": 2}, "in_scope": True, "attack_surface_score": 1},
        {"id": "function:M:m#4", "kind": "function", "contract": "M", "name": "m", "file": "Mock.sol",
         "signature": "", "source_span": {"start_line": 1, "end_line": 2}, "in_scope": False, "attack_surface_score": 0},
    ]
    (tmp_path / "output" / "coverage_manifest.json").write_text(json.dumps({"schema_version": 1, "items": items}))
    disp = [{"manifest_id": it["id"], "status": ("deferred_out_of_scope" if not it["in_scope"] else "unassigned")}
            for it in items]
    (tmp_path / "output" / "coverage_dispositions.json").write_text(json.dumps({"dispositions": disp}))
    monkeypatch.setattr(audit_context, "get_audit_root", lambda: tmp_path)
    old = sys.argv
    sys.argv = ["coverage_sweep_prepare"]
    try:
        assert prep.main() == 0
    finally:
        sys.argv = old
    idx = json.loads((tmp_path / "output" / "coverage_sweep" / "_bundles" / "index.json").read_text())
    # all 3 in-scope unassigned items (incl. the low-score-0 tail) are bundled; the out-of-scope mock is not
    assert idx["total_pending_items"] == 3


# ---- (e) integrity: gate + evidence enforcement + verifier + forbidden-5 byte-identical (no weakening) ----
def test_integrity_pins_unchanged():
    pins = {
        "scripts/coverage_completeness_gate.py": "c0ffcacf5ead",
        "scripts/research/executed_poc_verifier.py": "1a005811fbb9",
        "scripts/min_confirm_gate.py": "2a15169a53c2",
        "scripts/confirm_gate.py": "afc481c99ea9",
        "data/fp_autopsies/rejection_rules.jsonl": "693c019027ce",  # refreshed: legit human promote_learning 2026-06-11 (+2 FP rules: EVK rate<1 rounding-favorable, revert-lend oracle-decimals)
        "audits/beanstalk-2024-05/data/evaluation/ground_truth.jsonl": "35f44065901c",
    }
    for rel, h in pins.items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()[:12] == h, f"{rel} changed"


# ---- config flag ----
def test_config_mandatory_full_sweep():
    pol = json.loads((ROOT / "config" / "agent_policy.json").read_text())
    assert pol["coverage_policy"]["mandatory_full_sweep"] is True
    # the underlying fail-closed defaults remain on
    assert pol["coverage_policy"]["review_gate_blocks_unassigned"] is True
    assert pol["coverage_policy"]["review_gate_blocks_unexamined"] is True
