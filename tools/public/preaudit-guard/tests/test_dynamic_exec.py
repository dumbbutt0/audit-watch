from preaudit_guard.detectors import dynamic_exec as de
from preaudit_guard.findings import Severity


def cats(f):
    return {x.category for x in f}


def test_os_system_high():
    f = de.detect("tool.py", "import os\nos.system('rm x')\n")
    assert any(x.category == "os_system" and x.severity == Severity.HIGH for x in f)


def test_pickle_loads_high():
    f = de.detect("tool.py", "import pickle\npickle.loads(blob)\n")
    assert "insecure_deserialize" in cats(f)


def test_yaml_safe_loader_not_flagged():
    unsafe = de.detect("c.py", "yaml.load(s)\n")
    safe = de.detect("c.py", "yaml.load(s, Loader=yaml.SafeLoader)\n")
    assert "insecure_deserialize" in cats(unsafe)
    assert "insecure_deserialize" not in cats(safe)


def test_eval_in_js():
    f = de.detect("app.js", "const r = eval(userInput);\n")
    assert "eval" in cats(f)


def test_not_scanned_in_docs():
    f = de.detect("notes.md", "we call eval(x) and os.system(y)\n")
    assert f == []
