//! Solana PoC template — Level 3 standard (see CLAUDE.md "Level 3 PoC Standard").
//!
//! A PoC only passes if it proves ALL THREE layers, each as a test that ACTUALLY PASSES:
//!   L1 — Entry:      attacker tx built from a fresh keypair (EOA), NO privileged setup/signers.
//!   L2 — State Flip: name the exact account / token balance / lamports and assert before vs after
//!                    (litesvm `svm.get_account()` / SPL `Account::unpack`), not inferred.
//!   L3 — Outcome:    the final economic/security consequence proven in test output
//!                    (attacker balance up by the stolen amount; victim/vault down by it).
//!
//! An HONEST PARTIAL PoC (one layer proven, others `#[ignore]` with a written reason) is more
//! useful than a fabricated passing test. Never assert success you did not observe.
//!
//! ──────────────────────────────────────────────────────────────────────────────────────────
//! WORKED SHAPE (illustration — Orderly H-2, withdrawal-recipient not bound to message receiver):
//!   L1: attacker keypair pays for `lz_receive` and passes ITS OWN `user`/`user_deposit_wallet`
//!       for a withdraw message addressed to the victim `receiver`.
//!   L2: load `attacker_ata` and `vault_ata` token balances before/after; assert attacker_ata
//!       += amount, vault_ata -= amount.
//!   L3: assert the victim never received funds AND attacker net gain == withdraw amount.
//! ──────────────────────────────────────────────────────────────────────────────────────────

#![cfg(test)]

use litesvm::LiteSVM;
use solana_sdk::{
    account::Account,
    instruction::{AccountMeta, Instruction},
    pubkey::Pubkey,
    signature::{Keypair, Signer},
    transaction::Transaction,
};

/// Program id of the in-scope program (replace with the real `declare_id!`).
fn program_id() -> Pubkey {
    // Pubkey::from_str("AdA9VFXwkKPj51SZxSQwJ4bqPJiAJqidCwPhb8zSJndx").unwrap()
    Pubkey::new_unique()
}

/// Boot a LiteSVM, deploy the in-scope program .so, and seed the protocol state the bug needs.
/// Keep setup to the MINIMUM legitimate state — anything an honest deployer would create — so the
/// exploit's permissionlessness is credible (L1).
fn setup() -> (LiteSVM, Keypair) {
    let mut svm = LiteSVM::new();
    let attacker = Keypair::new();
    svm.airdrop(&attacker.pubkey(), 10_000_000_000).unwrap();
    // svm.add_program_from_file(program_id(), "path/to/target_program.so").unwrap();
    // ... create vault PDAs, fund the vault ATA, configure allowed token/broker, etc.
    (svm, attacker)
}

/// Read an SPL token account's `amount` (the L2 primitive: a NAMED balance, asserted).
fn token_amount(svm: &LiteSVM, ata: &Pubkey) -> u64 {
    let acct: Account = svm.get_account(ata).expect("ata exists");
    spl_token::state::Account::unpack(&acct.data).expect("valid token account").amount
}

// ── L1 — Entry: the attacker tx is constructed and lands from an unprivileged EOA ───────────
#[test]
fn l1_entry_unprivileged() {
    let (mut svm, attacker) = setup();
    let ix = Instruction {
        program_id: program_id(),
        accounts: vec![
            AccountMeta::new(attacker.pubkey(), true),
            // ... attacker-chosen accounts that SHOULD have been constrained
        ],
        data: vec![/* instruction discriminator + params */],
    };
    let tx = Transaction::new_signed_with_payer(
        &[ix],
        Some(&attacker.pubkey()),
        &[&attacker],
        svm.latest_blockhash(),
    );
    let res = svm.send_transaction(tx);
    // For a reachability PoC we only require the runtime ACCEPTS the attacker tx (no priv signer).
    assert!(res.is_ok(), "L1: attacker tx must execute from an EOA with no privileged setup: {res:?}");
}

// ── L2 — State Flip: name the slots/balances and assert before≠after ────────────────────────
#[test]
fn l2_state_flip() {
    let (mut svm, _attacker) = setup();
    let vault_ata = Pubkey::new_unique();   // replace with the real derived ATA
    let attacker_ata = Pubkey::new_unique();

    let _vault_before = token_amount(&svm, &vault_ata);
    let _attacker_before = token_amount(&svm, &attacker_ata);

    // ... send the exploit tx (as in l1) ...

    // let vault_after = token_amount(&svm, &vault_ata);
    // let attacker_after = token_amount(&svm, &attacker_ata);
    // assert!(attacker_after > _attacker_before, "L2: attacker balance must increase");
    // assert!(vault_after < _vault_before, "L2: vault balance must decrease by the same amount");
    panic!("L2 not yet implemented — fill in the exploit tx + balance assertions, or #[ignore] with a reason");
}

// ── L3 — Outcome: the economic/security consequence, proven not inferred ─────────────────────
#[test]
fn l3_outcome() {
    let (mut svm, _attacker) = setup();
    // Prove the net consequence: e.g. attacker_gain == stolen_amount AND the legitimate
    // receiver got nothing; or an invariant (sum of credited == sum of deposited) is broken.
    // assert_eq!(attacker_gain, stolen_amount, "L3: attacker net-extracts the full amount");
    let _ = &mut svm;
    panic!("L3 not yet implemented — assert the final economic outcome from observed state");
}
