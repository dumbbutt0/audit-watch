"""Finding model, severity scale, and overall-risk aggregation.

Severity is per-finding. The overall repo risk is the max finding severity,
with a few *documented combination escalations* — the combinations that matter
most for a pre-audit quarantine decision (e.g. a secret present together with a
network-capable lifecycle script is treated as CRITICAL "possible exfiltration"
even if neither alone is critical).
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import IntEnum


class Severity(IntEnum):
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3

    @property
    def label(self) -> str:
        return self.name

    @classmethod
    def from_str(cls, s: str) -> "Severity":
        return cls[s.strip().upper()]


@dataclass
class Finding:
    """One pre-audit risk signal located at a file:line."""

    detector: str          # "prompt_injection" | "lifecycle_scripts" | "secrets"
    category: str          # finer-grained type, e.g. "instruction_injection", "install_hook", "private_key"
    severity: Severity
    file: str              # path relative to the scanned root
    line: int              # 1-based; 0 if not line-anchored
    message: str           # calibrated, human-readable ("potential ...", "review before execution")
    snippet: str = ""      # short evidence excerpt (redacted for secrets)
    recommendation: str = ""

    def to_dict(self) -> dict:
        d = asdict(self)
        d["severity"] = self.severity.label
        return d


# Generic, detector-level remediation advice surfaced when a category fires.
RECOMMENDATIONS: dict[str, str] = {
    "prompt_injection": (
        "Treat README/comments/docs as untrusted DATA. Do not let embedded text alter an "
        "agent's instructions, methodology, or severity decisions; strip/quarantine before LLM review."
    ),
    "lifecycle_scripts": (
        "Do NOT run install/build scripts blindly. Install with script execution disabled "
        "(e.g. `npm ci --ignore-scripts`), and read every setup/Makefile/shell script first."
    ),
    "secrets": (
        "Rotate and remove any committed key/secret immediately; never reuse it. "
        "Scrub it from git history before sharing the repository."
    ),
    "_network_in_setup": (
        "A setup/test path reaches the network. Review and run in a network-disabled sandbox first."
    ),
    "network_behavior": (
        "Build/test/CI code makes network calls. Review the endpoints and run with networking "
        "disabled until you trust them — network during setup is a common exfiltration/payload vector."
    ),
    "destructive_fs": (
        "Scripts perform destructive or catastrophic filesystem operations. Read them before running, "
        "and never execute on your host — use a disposable sandbox/container."
    ),
    "dynamic_exec": (
        "Code dynamically executes strings/serialized data (eval/exec/system/pickle/unsafe yaml). "
        "Trace the inputs before running; these are classic remote-code-execution vectors."
    ),
    "ci_actions": (
        "CI workflows carry supply-chain/secret-exposure risk. Avoid running untrusted workflows; "
        "review pull_request_target triggers, run-step injection, and pin third-party actions to a full SHA."
    ),
}


@dataclass
class ScanResult:
    root: str
    files_scanned: int
    findings: list[Finding] = field(default_factory=list)

    @property
    def overall(self) -> Severity:
        return aggregate_risk(self.findings)

    def counts(self) -> dict[str, int]:
        out = {s.label: 0 for s in Severity}
        for f in self.findings:
            out[f.severity.label] += 1
        return out

    def to_dict(self) -> dict:
        return {
            "tool": "preaudit-guard",
            "root": self.root,
            "files_scanned": self.files_scanned,
            "overall_risk": self.overall.label,
            "counts": self.counts(),
            "findings": [f.to_dict() for f in self.findings],
        }


def aggregate_risk(findings: list[Finding]) -> Severity:
    """Overall risk = max finding severity, with documented combination escalations.

    Escalations (only ever raise, never lower):
      * secret  +  network-capable lifecycle script  -> CRITICAL (possible exfiltration)
      * prompt-injection  +  executable setup path    -> at least HIGH (weaponizable injection)
    """
    if not findings:
        return Severity.LOW

    base = max(f.severity for f in findings)

    detectors = {f.detector for f in findings}
    has_secret = "secrets" in detectors
    has_injection = "prompt_injection" in detectors
    has_exec = ("lifecycle_scripts" in detectors) or ("dynamic_exec" in detectors)
    has_network = ("network_behavior" in detectors) or any(
        f.category == "network_in_setup" for f in findings
    )

    # secret present together with a way to reach the network or execute code -> exfiltration risk
    if has_secret and (has_network or has_exec):
        return Severity.CRITICAL
    # weaponizable injection: instructions to an agent plus an executable setup/code path
    if has_injection and has_exec:
        return max(base, Severity.HIGH)

    return base
