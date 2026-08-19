import json

from preaudit_guard.cli import main
from preaudit_guard.findings import Severity
from preaudit_guard.report import render
from preaudit_guard.scanner import run_scan


def test_malicious_repo_is_high_or_critical(malicious_repo):
    result = run_scan(malicious_repo)
    assert result.overall >= Severity.HIGH
    detectors = {f.detector for f in result.findings}
    # all seven detector families should fire on the toy repo
    assert {
        "prompt_injection", "lifecycle_scripts", "secrets",
        "network_behavior", "destructive_fs", "dynamic_exec", "ci_actions",
    } <= detectors


def test_clean_repo_is_low(clean_repo):
    result = run_scan(clean_repo)
    assert result.overall == Severity.LOW, [f.to_dict() for f in result.findings]


def test_json_format_parses(malicious_repo):
    out = render(run_scan(malicious_repo), "json")
    data = json.loads(out)
    assert data["tool"] == "preaudit-guard"
    assert data["overall_risk"] in ("HIGH", "CRITICAL")
    assert data["findings"]


def test_markdown_renders(malicious_repo):
    out = render(run_scan(malicious_repo), "markdown")
    assert out.startswith("# PreAudit Guard")
    assert "Overall risk" in out


def test_cli_exit_codes(malicious_repo, clean_repo, capsys):
    # malicious -> non-zero (block); --exit-zero forces 0; clean -> 0
    assert main(["scan", str(malicious_repo)]) == 2
    capsys.readouterr()
    assert main(["scan", str(malicious_repo), "--exit-zero"]) == 0
    capsys.readouterr()
    assert main(["scan", str(clean_repo)]) == 0
    capsys.readouterr()


def test_cli_missing_path():
    assert main(["scan", "/no/such/path/xyz"]) == 1
