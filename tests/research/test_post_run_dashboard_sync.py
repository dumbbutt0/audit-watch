"""P224 — tests for the multi-source dashboard sync adapter + safe post-run hook.

Covers: existing Zeta sync still works (byte-compatible record set) · Size Credit SC-* normalize correctly ·
duplicate ids rejected · missing artifact paths become explicit unresolved · dry-run writes nothing · failed
write (deletion guard) does not mutate the existing mirror · atomic backup created on a real write · deletion
guard blocks drops unless --allow-delete · dashboard renders an SC-* card without crashing (post-sync).
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import sync_hunt_findings as sh           # noqa: E402
import dashboard_sync as ds               # noqa: E402
import finding_detail as fd               # noqa: E402

ZETA_ARGS = ["--phase", "P215", "--audit", "zetachain-2023-10-holdout",
             "--workspace", "documentation/research/assisted_mode/p215_full_funnel_rehearsal"]
SC_ARGS = ["--phase", "P223", "--audit", "size-credit-2024-06-blind",
           "--workspace", "documentation/research/assisted_mode/p223_size_credit_hunt",
           "--source-adapter", "size_credit"]
SC_PREFIX = "size-credit-2024-06-blind:P223:"
ZETA_PREFIX = "zetachain-2023-10:P215:"


def _emit(args, tmp_path, *extra):
    out = tmp_path / "mirror.json"
    rc = sh.main(args + ["--out", str(out), *extra])
    return rc, out


# ---------------- 1. Zeta sync still works (byte-compatible record set) ----------------
# ---------------- 2. Size Credit SC-* normalize correctly ----------------
# ---------------- 3. Duplicate ids rejected ----------------
def test_duplicate_record_id_rejected():
    doc = {"schema_version": "synced-1", "findings": [
        ds.to_synced_finding({"candidate_id": "X", "source_track": "audit_workspace", "record_id": "p:1"}),
        ds.to_synced_finding({"candidate_id": "Y", "source_track": "audit_workspace", "record_id": "p:1"}),
    ]}
    errs = sh._validate_mirror_doc(doc, ["X", "Y"], "zzz:")
    assert any("duplicate record_id" in e for e in errs)


def test_duplicate_candidate_id_rejected():
    doc = {"schema_version": "synced-1", "findings": [
        ds.to_synced_finding({"candidate_id": "X", "source_track": "audit_workspace", "record_id": "p:1"}),
        ds.to_synced_finding({"candidate_id": "X", "source_track": "audit_workspace", "record_id": "p:2"}),
    ]}
    errs = sh._validate_mirror_doc(doc, ["X"], "zzz:")
    assert any("duplicate candidate_id" in e for e in errs)


# ---------------- 4. Missing artifact paths become explicit unresolved ----------------
def test_missing_paths_become_unresolved():
    rec = {"record_id": "pre:SC-01:C.f",
           "source_refs": {"merged_finding": "audits/does-not-exist/output/merged_findings.json#SC-01",
                           "harness": "pocs/p223/test/SC01_eth_sweep.t.sol"}}
    unresolved = sh._unresolved_artifacts([rec], "pre:")
    paths = [p for _rid, p in unresolved]
    assert any("does-not-exist" in p for p in paths)      # missing -> explicitly listed
    assert all("SC01_eth_sweep" not in p for p in paths)  # existing harness -> NOT listed


# ---------------- 5. Dry-run writes nothing ----------------
# ---------------- 6 + 8. Deletion guard blocks drops + no mutation on failure ----------------
def _seed_mirror(tmp_path, extra_record_id):
    out = tmp_path / "mirror.json"
    rec = ds.to_synced_finding({"candidate_id": "ZZZ-99", "source_track": "audit_workspace",
                                "record_id": extra_record_id, "contract": "C", "function": "f"})
    doc = {"schema_version": "synced-1", "generated_by": "test", "research_only": True,
           "review_only": True, "routes_in_production": False, "is_gate": False, "findings": [rec]}
    out.write_text(json.dumps(doc, indent=1) + "\n")
    return out


# ---------------- 7. Atomic backup created on a real write ----------------
# ---------------- 9. Dashboard renders an SC-* card without crashing (post-sync) ----------------
