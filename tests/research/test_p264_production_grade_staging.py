"""P264 — production-grade staging (default-off shadow harness). Safety + contract + isolation tests."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HARNESS = ROOT / "scripts/research/recall_first_harness.py"
HCFG = ROOT / "config/research_recall_first_harness.json"
SCHEMA = ROOT / "schemas/recall_first_advisory.schema.json"
DOCS = ROOT / "documentation/research/assisted_mode/p264_production_grade_staging"
OUTS = DOCS / "outputs"
P263 = ROOT / "documentation/research/assisted_mode/p263_fresh_scored_recall_proof/outputs"
DOC_FILES = ("SETUP.md", "DEPLOYMENT_SPEC.md", "SHADOW_MODE_CONTRACT.md", "GUARDRAILS.md", "OUTPUT_SCHEMA.md",
             "OPERATOR_RUNBOOK.md", "ROLLBACK_PLAN.md", "TEST_RESULTS.md", "LIMITATIONS.md", "VERDICT.md")
VERDICTS = ("A — SHADOW_DEPLOYMENT_READY", "B — SHADOW_DEPLOYMENT_NEEDS_REFINEMENT",
            "C — DEPLOYMENT_ABORTED_SAFETY_RISK", "D — DEPLOYMENT_ABORTED_CONSTRAINT_VIOLATION")
# Frozen reused modules must stay byte-identical (harness imports, never modifies).
FROZEN = {"scripts/research/locus_shape_prioritizer.py": "d6b494bc3c0cc746",
          "config/research_locus_shape_prioritizer.json": "c61da091ad3ed21e",
          "scripts/research/recall_first_shape_sweep.py": "a48336275cb65a4f",
          "config/research_recall_first_shape_sweep.json": "62e860199e7c51cd"}
FORBIDDEN = {"scripts/dashboard_sync.py": "c1af70e1", "prompts/deep_trace.md": "c095c426",
             "scripts/min_confirm_gate.py": "2a15169a", "scripts/confirm_gate.py": "afc481c9",
             "scripts/validate_p208_l3_readiness.py": "ae55eb80"}
ARGS = ["--manifest", str(P263 / "benddao_coverage_manifest.json"),
        "--accounting", str(P263 / "benddao_accounting_checkpoint.json"),
        "--state-transition", str(P263 / "benddao_state_transition_checkpoint.json")]


def _sha(p, n=16):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()[:n]


def _run(args, **kw):
    return subprocess.run([sys.executable, str(HARNESS), *args], capture_output=True, text=True, **kw)


def test_files_and_docs_exist():
    assert HARNESS.exists() and HCFG.exists() and SCHEMA.exists()
    for d in DOC_FILES:
        assert (DOCS / d).exists(), f"missing {d}"
    assert any(v in (DOCS / "VERDICT.md").read_text() for v in VERDICTS)
    cfg = json.loads(HCFG.read_text())
    assert cfg["default_mode"] == "disabled" and cfg["is_gate"] is False and cfg["routes_in_production"] is False


def test_default_mode_does_nothing(tmp_path):
    r = _run(["--out-dir", str(tmp_path / "d")])  # no --mode → disabled
    assert r.returncode == 0
    assert not (tmp_path / "d" / "recall_advisory_candidates.json").exists()


def test_shadow_emits_four_files(tmp_path):
    out = tmp_path / "s"
    r = _run(["--mode", "shadow", "--out-dir", str(out), *ARGS])
    assert r.returncode == 0, r.stderr
    for f in ("recall_advisory_candidates.json", "recall_advisory_candidates.md",
              "recall_metrics.json", "recall_guard_report.json"):
        assert (out / f).exists(), f"missing {f}"


def test_no_promoted_flags_can_be_true(tmp_path):
    out = tmp_path / "s"
    _run(["--mode", "shadow", "--out-dir", str(out), *ARGS])
    d = json.loads((out / "recall_advisory_candidates.json").read_text())
    assert d["emits_findings"] is False and d["concludes_vulnerability"] is False and d["guard_violations"] == 0
    for c in d["advisory_candidates"]:
        assert c["severity"] is None
        for f in ("reportable", "submission_ready", "concluded", "emits_finding", "production_routing"):
            assert c[f] is False, f"{f} true"
        assert c["status"] == "ADVISORY_RECALL_CANDIDATE"
        assert c["promotion_label"] in ("NEEDS_RANKING", "NEEDS_COMPLETION", "NEEDS_REFUTATION",
                                        "READY_FOR_HUMAN_REVIEW_SHADOW")


def test_output_validates_against_schema(tmp_path):
    out = tmp_path / "s"
    _run(["--mode", "shadow", "--out-dir", str(out), *ARGS])
    doc = json.loads((out / "recall_advisory_candidates.json").read_text())
    sch = json.loads(SCHEMA.read_text())
    try:
        import jsonschema
        jsonschema.validate(doc, sch)
    except ImportError:
        # structural fallback
        assert doc["module"] == "recall_first_harness" and isinstance(doc["advisory_candidates"], list)


def test_caps_enforced(tmp_path):
    out = tmp_path / "s"
    _run(["--mode", "shadow", "--out-dir", str(out), *ARGS])
    d = json.loads((out / "recall_advisory_candidates.json").read_text())
    cfg = json.loads(HCFG.read_text())["caps"]
    assert len(d["advisory_candidates"]) <= cfg["max_swept_loci_json"]
    for c in d["advisory_candidates"]:
        assert len(c["generated_mechanisms"]) <= cfg["max_mechs_per_locus"]


def test_malformed_config_fails_closed(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"default_mode": "shadow", "supported_modes": ["shadow"],
                               "caps": {"max_swept_loci_json": -5}, "cap_hard_upper_bounds": {}}))
    out = tmp_path / "bo"
    r = _run(["--mode", "shadow", "--config", str(bad), "--out-dir", str(out), *ARGS])
    assert r.returncode != 0
    assert not (out / "recall_advisory_candidates.json").exists()


def test_missing_input_fails_closed(tmp_path):
    out = tmp_path / "mo"
    r = _run(["--mode", "shadow", "--out-dir", str(out),
              "--manifest", "/nope.json", "--accounting", "/nope.json", "--state-transition", "/nope.json"])
    assert r.returncode != 0
    assert not (out / "recall_advisory_candidates.json").exists()


def test_metrics_record_module_hashes(tmp_path):
    out = tmp_path / "s"
    _run(["--mode", "shadow", "--out-dir", str(out), *ARGS])
    m = json.loads((out / "recall_metrics.json").read_text())
    vh = m["version_hashes"]
    assert vh["p260_module"] == "d6b494bc3c0cc746" and vh["p262_module"] == "a48336275cb65a4f"
    assert m["reproducibility"]["git"].startswith("n/a")
    assert "input_hashes" in m["reproducibility"]


def test_reused_modules_byte_identical():
    for path, h in FROZEN.items():
        assert _sha(path) == h, f"{path} changed (harness must import, not modify)"


def test_forbidden_files_byte_identical():
    for path, h in FORBIDDEN.items():
        assert _sha(path, 8) == h, f"forbidden file {path} changed"


def test_no_production_authority_files_touched():
    """Harness must not reference production submission/routing/severity/dashboard/confirm wiring."""
    src = HARNESS.read_text()
    for tok in ("run_pipeline", "dashboard_sync", "confirm_gate", "min_confirm_gate", "record_outcome",
                "agent_policy", "severity_"):
        assert tok not in src, f"harness references production wiring: {tok}"


