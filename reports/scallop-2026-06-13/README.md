# Scallop Protocol (Sui Move lending) — audit deliverables (2026-06-13)

Real HackenProof hunt (scallop-io/sui-lending-protocol @334e93a), local-only, **nothing submitted**, honest negative.
Max $300k, KYC + PoC. 4th Sui-Move target (after turbos CLMM, Ember vault, Suilend lending).
**Confirm the program's reputation requirement is ≤80 on the HackenProof dashboard before submitting.**

- `FINDINGS.md` — full per-surface review; verdict; the post-audit-delta method.

## Method / reproduce
```
git clone https://github.com/scallop-io/sui-lending-protocol /tmp/scallop-hunt && cd /tmp/scallop-hunt
git fetch --tags
# Highest-EV: diff main vs the LATEST audit to find unaudited code (was the new liquidation mechanism):
git diff --stat asymptotic-audit-2025 HEAD -- 'contracts/**/sources/**/*.move'
cd contracts/protocol
sui client switch --env mainnet     # testnet framework pin can be a dead rev; mainnet resolves
sui move test                        # repo suite: 53/53 PASS (runnable conservation evidence)
```
Result this session: 53/53 PASS; post-audit liquidation delta deep-traced and sound; no permissionless H/C.
