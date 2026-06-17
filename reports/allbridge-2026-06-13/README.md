# Allbridge Core (EVM) — audit deliverables (2026-06-13)

Real HackenProof hunt, local/fork-only, **nothing submitted**, no finding (honest negative).

- `FINDINGS.md` — per-area dispositions (Pool / Bridge+Messenger / CCTP-OFT adapters), deployed-version pin,
  conservation-fuzz results, consensus/replay trace, audit cross-check.
- `poc/Pool6DecConservation.t.sol` — added Foundry invariant harness: 6-decimal (USDC/USDT) Pool conservation,
  balance-guard OFF + zero fee (the Apr-2023 LP+swapper flash-loan hack shape). 3 invariants × 200k calls, 0 fails.
  Drop into `test/foundry/` of `allbridge-io/allbridge-core-evm-contracts` and run with the skip flags below.

## Reproduce
```
git clone --depth 1 https://github.com/allbridge-io/allbridge-core-evm-contracts /tmp/allbridge-hunt
cd /tmp/allbridge-hunt
npm install --ignore-scripts --no-audit --no-fund --legacy-peer-deps --no-save @openzeppelin/contracts@4.9.6
# forge-std already vendored in lib/
cp <this>/poc/Pool6DecConservation.t.sol test/foundry/
forge test --match-contract Pool6DecConservationTest \
  --skip OftBridge --skip CctpBridge --skip CctpV2Bridge --skip XReserveBridge --skip PayerWithAbr \
  --skip MockOftBridge --skip MockOFT --skip MockCctpBridge \
  --skip AutoDepositWallet --skip AutoDepositFactory --skip AutoDepositParent
# also: forge test --match-contract BasicInvariantTest <same skips>   (repo's own 18-dec suite)
```
Result this session: both suites PASS (3 invariants × 200,000 calls each, 0 failures).
