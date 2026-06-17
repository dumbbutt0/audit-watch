"""
P310 — coverage-drive wired into the production pipeline as the default. No network.

Verifies: (a) run_pipeline.sh's coverage gate block-path auto-stages the sweep + emits the resumable DRIVE loop, and
a first-class `coverage-drive` command exists + is documented; (b) `./run_pipeline.sh coverage-drive --no-rebuild`
runs on the active audit, reports the gate, stages the sweep on a gap, and exits 0; (c) the reused production coverage
scripts + forbidden-5 + verifier are byte-identical (only run_pipeline.sh changed).
"""
import hashlib
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RP = (ROOT / "run_pipeline.sh").read_text()


# ---- (a) wiring is present ----
def test_block_path_drives_coverage():
    # the gate's block branch stages the sweep before failing closed, with the resumable drive message
    assert 'run_step "coverage_sweep_prepare"' in RP
    assert "DRIVE coverage to 100%" in RP and "loops until 0 unexamined" in RP
    # fail-closed preserved: the coverage gate block still calls die()
    assert RP.count("Coverage gate failed") >= 1


def test_coverage_drive_command_exists_and_documented():
    assert "\n  coverage-drive)\n" in RP
    assert "coverage-drive [--no-rebuild]" in RP                 # usage/help line
    assert "--no-rebuild" in RP and "coverage_completeness_gate.py" in RP


# ---- (b) coverage-drive runs on the active audit ----
def test_coverage_drive_runs_and_exits_zero(tmp_path):
    r = subprocess.run(["bash", "run_pipeline.sh", "coverage-drive", "--no-rebuild"],
                       cwd=str(ROOT), capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stderr[-800:]
    out = r.stdout + r.stderr
    assert "coverage-drive:" in out                              # the drive summary line
    # active audit's gate report was produced
    link = ROOT / "output"
    assert (link / "coverage_gate.json").exists()
    # on a gap, the sweep is staged + the resumable loop is printed (else COMPLETE)
    assert ("UNEXAMINED" in out and "coverage_sweep" in out) or "COMPLETE — every in-scope item" in out


# ---- (c) reused production scripts byte-identical (only run_pipeline.sh changed) ----
def test_reused_scripts_byte_identical():
    pins = {
        "scripts/coverage_completeness_gate.py": "c0ffcacf5ead",
        "scripts/link_findings_to_manifest.py": "abe906cafa04",
        "scripts/coverage_sweep_prepare.py": "a24e4cd26cc1",
        "scripts/min_confirm_gate.py": "2a15169a53c2",
        "scripts/research/executed_poc_verifier.py": "1a005811fbb9",
        "scripts/research/coverage_drive.py": "c1230491fc78",
    }
    for rel, h in pins.items():
        got = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()[:12]
        assert got == h, f"{rel} changed: {got} != {h}"


def test_bash_syntax_ok():
    r = subprocess.run(["bash", "-n", "run_pipeline.sh"], cwd=str(ROOT), capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
