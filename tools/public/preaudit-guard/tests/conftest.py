"""Pytest config: make the package importable without an install, expose example paths."""

import sys
from pathlib import Path

import pytest

PKG_ROOT = Path(__file__).resolve().parent.parent  # the preaudit-guard/ dir
# append (not insert) so this never shadows an earlier path entry if these tests are
# ever swept into a parent repo's bare `pytest` run.
if str(PKG_ROOT) not in sys.path:
    sys.path.append(str(PKG_ROOT))

EXAMPLES = PKG_ROOT / "examples"


@pytest.fixture
def malicious_repo() -> Path:
    return EXAMPLES / "malicious-toy-repo"


@pytest.fixture
def clean_repo() -> Path:
    return EXAMPLES / "clean-toy-repo"
