# P117 — Minimal runtime question

The unbounded-loop DoS hypothesis, reduced to one executable question:

> **Does `CuratorRewardsDistributor.distribute(credId)` gas grow with the curator count N and exceed a practical
> block-gas budget (~30,000,000) — i.e. revert / become un-includable before completing reward distribution — at an
> N reachable via permissionless curator growth (`Cred.buyShareCred`)?**

- Independent variable: N = curator count (size of `getCuratorAddresses(credId, 0, 0)`).
- Measured: gas consumed by `distribute(credId)`; and whether `distribute` completes within a 30M gas cap.
- Threshold: mainnet block gas limit ≈ 30,000,000. If `distribute` needs more, it can never be included → the
  accumulated `balanceOf[credId]` rewards are permanently undistributable (no paginated alternative).
- Reachability (source-established, not the runtime question): curator growth is permissionless and `(0,0)` returns
  ALL curators — so N is attacker-controllable and also grows organically for popular creds.

The harness answers ONLY this gas-practicality question. Runtime decides; source frames.
