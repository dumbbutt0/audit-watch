from preaudit_guard.detectors import destructive_fs as df
from preaudit_guard.findings import Severity


def cats(f):
    return {x.category for x in f}


def test_fork_bomb_critical():
    f = df.detect("run.sh", ":(){ :|:& };:\n")
    assert any(x.category == "fork_bomb" and x.severity == Severity.CRITICAL for x in f)


def test_rm_rf_home_is_high():
    f = df.detect("scripts/run.sh", "rm -rf ~/.config/app\n")
    assert any(x.category == "destructive_rm" and x.severity == Severity.HIGH for x in f)


def test_generic_build_rm_not_flagged_here():
    # generic build cleanup is left to lifecycle_scripts (MEDIUM), not destructive_fs.
    f = df.detect("build.sh", "rm -rf ./build ./dist\n")
    assert f == []


def test_shutil_rmtree_high():
    f = df.detect("clean.py", "import shutil\nshutil.rmtree(target)\n")
    assert "recursive_delete" in cats(f)


def test_dd_to_device_critical():
    f = df.detect("wipe.sh", "dd if=/dev/zero of=/dev/sda bs=1M\n")
    assert any(x.severity == Severity.CRITICAL for x in f)
