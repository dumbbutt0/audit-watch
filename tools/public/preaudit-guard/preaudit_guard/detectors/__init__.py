"""Detector registry.

Each detector exposes `detect(path, text, rules=None) -> list[Finding]` and a
module-level `DETECTOR` name. The scanner runs every registered detector against
every text file.
"""

from . import (
    prompt_injection,
    lifecycle_scripts,
    secrets,
    network_behavior,
    destructive_fs,
    dynamic_exec,
    ci_actions,
)

DETECTORS = [
    prompt_injection,
    lifecycle_scripts,
    secrets,
    network_behavior,
    destructive_fs,
    dynamic_exec,
    ci_actions,
]

__all__ = [
    "DETECTORS",
    "prompt_injection",
    "lifecycle_scripts",
    "secrets",
    "network_behavior",
    "destructive_fs",
    "dynamic_exec",
    "ci_actions",
]
