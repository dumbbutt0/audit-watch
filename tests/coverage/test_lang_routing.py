"""Cross-language routing spine — audit_context.audit_language() + build_coverage_manifest language dispatch.
Locks: solidity is the default (Solidity path byte-behavior-unchanged when language unset/unknown); rust is
detected from meta or inferred from a .rs-only tree.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
import audit_context as ac  # noqa: E402
import build_coverage_manifest as bcm  # noqa: E402


def test_audit_language_normalization(monkeypatch):
    monkeypatch.setattr(ac, "get_audit_meta", lambda: {"language": "RUST"})
    assert ac.audit_language() == "rust"
    monkeypatch.setattr(ac, "get_audit_meta", lambda: {"language": "Solidity"})
    assert ac.audit_language() == "solidity"
    monkeypatch.setattr(ac, "get_audit_meta", lambda: {"language": "go"})  # unknown -> default
    assert ac.audit_language() == "solidity"
    monkeypatch.setattr(ac, "get_audit_meta", lambda: {})  # missing -> default
    assert ac.audit_language() == "solidity"


def test_infer_language_and_source_dispatch(tmp_path):
    (tmp_path / "a.rs").write_text("pub fn f() {}")
    assert bcm._infer_language(tmp_path) == "rust"
    assert bcm._source_files(tmp_path, "rust") and all(p.suffix == ".rs" for p in bcm._source_files(tmp_path, "rust"))
    (tmp_path / "b.sol").write_text("contract C {}")
    # mixed tree: inference is conservative -> solidity (only pure-rust trees infer rust)
    assert bcm._infer_language(tmp_path) == "solidity"
    assert all(p.suffix == ".sol" for p in bcm._source_files(tmp_path, "solidity"))


def test_rust_files_skips_tests_and_target(tmp_path):
    (tmp_path / "lib.rs").write_text("pub fn f() {}")
    (tmp_path / "tests").mkdir(); (tmp_path / "tests" / "t.rs").write_text("fn t() {}")
    (tmp_path / "target").mkdir(); (tmp_path / "target" / "g.rs").write_text("fn g() {}")
    (tmp_path / "x_test.rs").write_text("fn x() {}")
    names = {p.name for p in bcm._rust_files(tmp_path)}
    assert names == {"lib.rs"}
