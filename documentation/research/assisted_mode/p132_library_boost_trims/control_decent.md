# P132 — Control: decent (no libraries)

decent is the non-library control. The trims should not cost it any recall or break paths.

| Metric | Before trim (P130/P131) | After trim (P132) | Δ |
|---|---|---|---|
| awarded-FUNCTION deep-pass coverage | 3/9 (33%) | 3/9 (33%) | **0** |
| deep-pass volume (functions ≥3) | 52 | 52 | **0** |
| boosted functions (distinct) | 5 | 5 | 0 (composition shifted, see note) |

## Notes
- **No recall loss, no path breakage.** decent's awarded contracts (`DcntEth`, `DecentEthRouter`,
  `DecentBridgeExecutor`) live in `lib/decent-bridge/src` (outside the `--contract src` root used here), so they
  are `(absent)` regardless of trims — unaffected.
- One trivial getter (`UniSwapper.getId`) dropped out of the boosted set; because of the per-contract cap, a
  previously cap-excluded eligible function in the same contract took its slot, so the **boosted count and
  volume are unchanged** (cap-neutral reshuffle, expected). No awarded function involved.
- decent has no `library`/mock contracts in scope, so the mock trim does not fire; the trivial trim removes only
  obviously trivial getters. Confirms the trims are **architecture-proportional and non-destructive**.
