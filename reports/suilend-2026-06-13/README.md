# Suilend (Sui Move lending) — audit deliverables (2026-06-13)

Real hunt (solendprotocol/suilend @d5ba83a, branch devel = deployed v20), local-only, **nothing submitted**,
honest negative. Bounty: docs.suilend.fi/security/bug-bounty (Critical up to $250k, PoC required, no KYC, devnet only).

- `FINDINGS.md` — full per-surface review (decimal/liquidation/health/interest+cToken/oracle/ObligationOwnerCap/
  rate_limiter), toolchain notes, verdict, OOS.
- `poc/zzz_reserve_conservation.move` — runnable `sui move test` conservation harness (3/3 PASS): cToken round-trip
  can't profit; interest only grows the exchange rate; internal available_amount == real held balance.

## Reproduce
```
git clone --depth 1 https://github.com/solendprotocol/suilend /tmp/suilend-hunt
cd /tmp/suilend-hunt/contracts/suilend
sui client switch --env mainnet     # IMPORTANT: testnet framework pin (563c1582) is a dead git rev; mainnet (868c226) resolves
cp <this>/poc/zzz_reserve_conservation.move tests/
sui move test                       # repo suite: 88/88 PASS
sui move test zzz_reserve_conservation   # added harness: 3/3 PASS
```
