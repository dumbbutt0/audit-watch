"""Scan orchestration: walk a path, run every detector, collect a ScanResult.

Pure and offline — never executes target code.
"""

from __future__ import annotations

from pathlib import Path

from .detectors import DETECTORS
from .findings import Finding, ScanResult, Severity
from .walker import iter_text_files


def run_scan(root: str | Path, max_bytes: int | None = None) -> ScanResult:
    root_path = Path(root)
    findings: list[Finding] = []
    n = 0
    kwargs = {"max_bytes": max_bytes} if max_bytes else {}
    for relpath, text in iter_text_files(root_path, **kwargs):
        n += 1
        for det in DETECTORS:
            try:
                findings.extend(det.detect(relpath, text))
            except Exception:
                # A detector must never crash the scan; skip its output for this file.
                continue
    findings.sort(key=lambda f: (-int(f.severity), f.file, f.line))
    return ScanResult(root=str(root_path), files_scanned=n, findings=findings)


def severity_at_least(result: ScanResult, threshold: Severity) -> bool:
    return result.overall >= threshold
