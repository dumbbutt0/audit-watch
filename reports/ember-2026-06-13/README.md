# Ember Vaults (Sui Move) — audit deliverables (2026-06-13)

Real HackenProof hunt (ember-protocol/Ember-Vaults @28a2d8e), local-only, **nothing submitted**, honest negative.
First real-world use of Audit-Watch's new Move (Sui) support.

- `FINDINGS.md` — full per-module review (math/queue/vault/gateway/admin), verdict, OOS notes.
- `poc/zzz_withdrawal_accounting_invariant.move` — runnable `sui move test` invariant harness over the
  multi-account cancel/skip/process share accounting (the highest-risk area). 3 adversarial scenarios, all PASS:
  asserts `pending_shares_to_burn == Σ account pending shares == Σ per-account request.shares` after every step.

## Reproduce
```
git clone --depth 1 https://github.com/ember-protocol/Ember-Vaults /tmp/ember-hunt
# Sui CLI: prebuilt binary (sui-mainnet-vX-ubuntu-x86_64.tgz -> ~/.local/bin/sui)
cp poc/zzz_withdrawal_accounting_invariant.move /tmp/ember-hunt/tests/
cd /tmp/ember-hunt && sui move test zzz_withdrawal_accounting_invariant
```
Result this session: 3/3 PASS (full repo suite also green). No permissionless High/Critical found.
