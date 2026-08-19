from preaudit_guard.detectors import secrets
from preaudit_guard.findings import Severity


def cats(findings):
    return {f.category for f in findings}


FAKE_PEM = (
    "-----BEGIN RSA PRIVATE KEY-----\n"
    "MIIBOgIBAAJBAKj34GkxFhD90vcNLYLInFEX6Ppy1tPf9Cnzj4p4WGeKLs1Pt8Qu\n"
    "-----END RSA PRIVATE KEY-----\n"
)


def test_pem_private_key_block_critical():
    f = secrets.detect("key.pem", FAKE_PEM)
    blk = [x for x in f if x.category == "private_key_block"]
    assert blk and blk[0].severity == Severity.CRITICAL


def test_named_key_with_real_value():
    text = "DEPLOYER_PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80\n"
    f = secrets.detect(".env.deploy", text)
    assert "named_secret" in cats(f)


def test_named_key_placeholder_skipped():
    text = "PRIVATE_KEY=${PRIVATE_KEY}\nMNEMONIC=your-key-here\n"
    f = secrets.detect("config.sh", text)
    assert "named_secret" not in cats(f)


def test_solana_keypair_file_critical():
    arr = "[" + ",".join(str(i % 256) for i in range(64)) + "]"
    f = secrets.detect("id.json", arr)
    assert any(x.category == "solana_keypair" and x.severity == Severity.CRITICAL for x in f)


def test_hex_privkey_requires_context():
    bare = "bytes32 constant SALT = 0x" + "ab" * 32 + ";\n"      # no key/secret keyword
    assert "hex_privkey_like" not in cats(secrets.detect("Foo.sol", bare))
    withctx = "uint256 privateKey = 0x" + "ab" * 32 + ";\n"      # 'key' on the line
    assert "hex_privkey_like" in cats(secrets.detect("Foo.sol", withctx))


def test_secret_value_is_redacted():
    secret = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
    f = secrets.detect(".env", f"PRIVATE_KEY={secret}\n")
    for finding in f:
        assert secret not in finding.snippet  # full secret must never be echoed
