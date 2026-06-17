# idOS — IDOSNodeStaking audit deliverables (2026-06-13)

Real bug-bounty hunt (HackenProof, idOS Network — Smart Contracts). Local/fork-only, nothing submitted.
Saved here so it survives `/tmp` cleanup.

- `F-B_report.md` — standalone, fork-validated finding: reward payouts are drawn from staker principal
  (no reward/principal segregation). High, conditional on funding posture. **The submission-ready write-up.**
- `FINDINGS.md` — full audit notes for all 3 in-scope files (IDOSToken / IDOSVesting honest negatives;
  IDOSNodeStaking F-A/F-B/F-C; F-A and F-C are prior-audit known per NM-0731).
- `poc/` — the proof-of-concept sources:
  - `poc/test/zzz_IDOSNodeStakingPoC.t.sol` — local PoCs (no-time-weighting, conservation, principal-eating).
  - `poc/test/zzz_IDOSNodeStaking_ForkPoC.t.sol` — **fork validation** against live Arbitrum One bytecode+token.
  - `poc/src/IDOSNodeStaking.sol` — the audited contract source (copied for reference / to run the PoCs).

## Target
- Repo: `idos-network/contracts` @ `ebbae56b3bf3598dc9794032dd3df37c772cfe8d` (master)
- Chain: Arbitrum One (42161) — `IDOSNodeStaking 0x6132F2EE66deC6bdf416BDA9588D663EaCeec337`,
  `IDOSToken 0x68731d6F14B827bBCfFbEBb62b19Daa18de1d79c`

## Reproducing the PoCs
The PoCs were run inside a Foundry checkout of the repo (`/tmp/idos-hunt/contracts`). To re-run, drop the
two test files into that repo's `test/` and run with solc 0.8.35 (svm can't fetch 0.8.27):

```
# local PoC
forge test --use ~/.solc-select/artifacts/solc-0.8.35/solc-0.8.35 \
  --match-test test_rewardClaimEatsPrincipal -vv

# fork PoC (live Arbitrum One; read-only fork + local simulation, no live tx)
forge test --use ~/.solc-select/artifacts/solc-0.8.35/solc-0.8.35 \
  --match-contract IDOSNodeStaking_ForkPoC -vv
# optional: ARBITRUM_ONE_RPC_URL=<your endpoint> (default https://arb1.arbitrum.io/rpc)
```

Env notes: OZ 5.5.0 via `forge soldeer install` (remap `@openzeppelin/contracts/=dependencies/
@openzeppelin-contracts-5.5.0/`); copy `forge-std` into `lib/`; stash out-of-scope CCA contracts + `script/`.

Last run (this session): all PoCs PASS. Fork test reports live posture @ epoch 144 — balance 26,938,533.96
IDOS vs principal 26,411,601.41 → ~527K buffer (~2% of principal) — and reproduces bob's unrecoverable 100M
principal after an unfunded reward claim.
