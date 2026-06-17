"""Tests for the Silo stalk/stem conservation taxonomy/classifier.

This lens models conservation of deposit amount, BDV, stem, stalk, grown-stalk, roots and reward scaling —
NOT a 'find stalk words' scan. Positives assert real Silo accounting flows are caught; FP-controls assert
generic transfers, comments, plain getters, unrelated math, and non-Silo deposits are NOT tagged.
"""
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

silo = importlib.import_module("silo_stalk_taxonomy")

SILO_FILE = "contracts/2024-05-beanstalk-the-finale/protocol/contracts/libraries/Silo/LibSilo.sol"
TS_FILE = "contracts/2024-05-beanstalk-the-finale/protocol/contracts/beanstalk/silo/SiloFacet/TokenSilo.sol"


def clf(name, snippet, file=SILO_FILE, contract="LibSilo", **kw):
    return silo.classify(name, snippet=snippet, file=file, contract=contract, **kw)


# --------------------------------------------------------------------------- positives
def test_transfer_stalk_with_rounding():
    c = clf("transferStalk",
            snippet="roots = s.sys.silo.roots.sub(1).mul(stalk).div(s.sys.silo.stalk).add(1);")
    assert c["silo_stalk_sensitive"] is True
    assert c["category"] in ("stalk_transfer", "rounding_direction", "roots_stalk_ratio")
    assert silo.is_high_risk(c)


def test_transfer_deposit_with_stem():
    c = clf("_transferDeposit", contract="TokenSilo", file=TS_FILE,
            snippet="LibSilo._removeDepositFromAccount(sender, token, stem, amount);"
                    " LibTokenSilo.addDepositToAccount(recipient, token, stem, amount, bdv);")
    assert c["silo_stalk_sensitive"] is True
    assert c["category"] in ("deposit_transfer", "deposit_stem_mismatch", "partial_deposit_transfer")
    assert silo.is_high_risk(c)


def test_transfer_deposits_batch():
    c = clf("_transferDeposits", contract="TokenSilo", file=TS_FILE,
            snippet="for (uint i; i < stems.length; i++) { bdvs[i] = _transferDeposit(sender, recipient, token, stems[i], amounts[i]); }")
    assert c["silo_stalk_sensitive"] is True
    assert c["category"] in ("deposit_batch_transfer", "deposit_transfer", "partial_deposit_transfer")


def test_grown_stalk_recompute():
    c = clf("_mow",
            snippet="uint256 grownStalk = _balanceOfGrownStalk(lastStem, stemTipForToken(token), bdv);"
                    " s.accts[account].stalk = s.accts[account].stalk.add(grownStalk);")
    assert c["silo_stalk_sensitive"] is True
    assert c["category"] in ("grown_stalk_recompute", "grown_stalk", "user_vs_global_stalk", "stem_accounting")


def test_earned_beans_reward_scaling():
    c = clf("stalkReward", mutability="pure",
            snippet="return uint128(uint96(endStem.sub(startStem))).mul(bdv).div(PRECISION);")
    assert c["silo_stalk_sensitive"] is True
    assert c["category"] in ("reward_scaling", "stem_scale", "grown_stalk")
    assert silo.is_high_risk(c)


def test_bdv_to_stalk_conversion():
    c = clf("calculateStalkFromStemAndBdv", contract="LibTokenSilo",
            snippet="stalk = bdv.mul(stalkIssuedPerBdv(token)).add(stalkReward(stem, stemTip, bdv));")
    assert c["silo_stalk_sensitive"] is True
    assert c["category"] in ("bdv_to_stalk", "reward_scaling", "grown_stalk", "stem_accounting")


def test_roots_stalk_ratio_update():
    c = clf("mintActiveStalk",
            snippet="uint256 roots = s.sys.silo.roots.mul(stalk).div(s.sys.silo.stalk);"
                    " s.sys.silo.stalk = s.sys.silo.stalk.add(stalk);")
    assert c["silo_stalk_sensitive"] is True
    assert c["category"] in ("roots_stalk_ratio", "user_vs_global_stalk", "stalk_transfer", "rounding_direction")


def test_user_global_stalk_update():
    c = clf("burnActiveStalk",
            snippet="s.accts[account].stalk = s.accts[account].stalk.sub(stalk);"
                    " s.sys.silo.stalk = s.sys.silo.stalk.sub(stalk);")
    assert c["silo_stalk_sensitive"] is True
    assert c["category"] in ("user_vs_global_stalk", "stalk_transfer", "roots_stalk_ratio")


def test_partial_deposit_transfer():
    c = clf("_transferDeposit", contract="TokenSilo", file=TS_FILE,
            snippet="uint256 partBdv = bdv.mul(amount).div(totalAmount);"
                    " LibTokenSilo.addDepositToAccount(recipient, token, stem, amount, partBdv);")
    assert c["silo_stalk_sensitive"] is True
    assert c["category"] in ("partial_deposit_transfer", "deposit_transfer", "deposit_stem_mismatch")


def test_zero_amount_deposit_edge():
    c = clf("_deposit", contract="TokenSilo", file=TS_FILE,
            snippet="require(amount > 0, 'Silo: amount'); LibTokenSilo.addDepositToAccount(account, token, stem, amount, bdv);")
    assert c["silo_stalk_sensitive"] is True
    assert c["category"] in ("zero_amount_deposit", "deposit_transfer", "deposit_stem_mismatch", "user_vs_global_deposit")


# --------------------------------------------------------------------------- FP controls
def test_fp_generic_erc20_transfer():
    c = silo.classify("transfer", snippet="_balances[to] = _balances[to].add(amount); return true;",
                      file="contracts/tokens/ERC20.sol", contract="ERC20")
    assert c["silo_stalk_sensitive"] is False


def test_fp_comment_only_stalk_words():
    c = clf("doThing", snippet="// updates stalk, stem, grown stalk and roots accounting\n x = y + 1;")
    assert c["silo_stalk_sensitive"] is False


def test_fp_simple_getter_returns_stored_stalk():
    c = clf("balanceOfStalk", mutability="view", snippet="return s.accts[account].stalk;")
    assert c["silo_stalk_sensitive"] is False


def test_fp_unrelated_amount_math():
    c = silo.classify("computeFee", snippet="return amount.mul(feeBps).div(10000);",
                      file="contracts/market/Fees.sol", contract="Fees")
    assert c["silo_stalk_sensitive"] is False


def test_fp_generic_deposit_non_silo():
    c = silo.classify("deposit", snippet="totalAssets = totalAssets.add(amount); shares = amount;",
                      file="contracts/vault/Vault4626.sol", contract="Vault4626")
    assert c["silo_stalk_sensitive"] is False
