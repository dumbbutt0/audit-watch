"""T9 — demote the un-wired research-detector platform behind one switch.

The research detector platform (CLAUDE.md "Research Detector Platform — UN-WIRED") is `routes_in_production:false`
and not in production routing, yet its tests are ~1/3 of the suite. This auto-marks those tests `research` so the
PRODUCTION suite can be run fast with `pytest -m "not research"`. Default `pytest tests/` is UNCHANGED (no marker
filter) — nothing is lost by default; this only adds an opt-out. Toggle intent is mirrored in
config/agent_policy.json → research_platform.enabled (false = opt-in)."""
from pathlib import Path

import pytest

# Research-detector-platform test dirs (un-wired families per CLAUDE.md + their composition layers).
RESEARCH_DIRS = {
    "research", "multicall_invariant", "permit_asset_binding", "sibling_function_parity",
    "cross_contract_sibling_parity", "value_flow_parity", "registry_position_lifecycle",
    "evidence_bundle_gate",
}


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "research: un-wired research-detector-platform tests (routes_in_production:false). "
        "Deselect the production suite with -m 'not research'.")


def pytest_collection_modifyitems(config, items):
    for item in items:
        if set(Path(str(item.fspath)).parts) & RESEARCH_DIRS:
            item.add_marker(pytest.mark.research)
