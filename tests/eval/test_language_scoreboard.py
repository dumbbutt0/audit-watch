"""Per-language recall scoreboards (move/rust). Locks: build_language writes a real board keyed on each
adjudication's `language` field; the Solidity board routes move/rust OUT (they never inflate Solidity recall);
the honest non-Solidity number is the full-coverage aggregate. Regenerates eval artifacts (not pinned)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import eval_scoreboard as ES  # noqa: E402


def test_move_board_built_and_classes_present():
    d = ES.build_language("move")
    assert d is not None and d["language"] == "move"
    ids = {p["id"] for p in d["projects"]}
    assert "sui-amm-swap-2022-11-eval" in ids
    # the move classes the recall lab authored show up with per-class recall
    assert "move-constant-product-invariant-recheck" in d["by_mechanism_class"]
    assert "move-public-helper-visibility" in d["by_mechanism_class"]
    assert (ROOT / "evals" / "move_scoreboard.md").exists()
    # honest number = full-coverage aggregate
    assert d["full_coverage_aggregate"]["recall_of_surfaced"] is not None


def test_rust_board_built_when_adjudications_exist():
    d = ES.build_language("rust")
    if d is None:
        return  # no rust adjudications in this checkout — nothing to assert
    assert d["language"] == "rust"
    # thin passes are reported but excluded from the full-coverage (honest) headline
    assert (ROOT / "evals" / "rust_scoreboard.md").exists()
    # non-blind reincorporations (no cold-pass fixture) are surfaced as provenance, NOT banked as blind recall
    sb = (ROOT / "evals" / "rust_scoreboard.md").read_text()
    if d.get("non_blind_reincorporations"):
        assert "NON-BLIND" in sb and "not banked" in sb.lower()


def test_solidity_board_excludes_move_and_rust():
    sol = ES.build()
    for set_name in ("training", "holdout"):
        for p in sol["sets"][set_name]["projects"]:
            if p["id"] == "sui-amm-swap-2022-11-eval":
                # routed out: present as a pointer, NEVER scored into Solidity recall
                assert "recall_of_surfaced" not in p
