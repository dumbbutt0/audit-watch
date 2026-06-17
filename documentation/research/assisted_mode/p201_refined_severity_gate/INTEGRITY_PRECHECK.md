# P201 — integrity precheck

## START hashes (md5sum first-8) — before any P201 action
| artifact | START | expected | match |
|---|---|---|---|
| `prompts/deep_trace.md` | `ef93a6c2` | `ef93a6c2` | ✓ |
| `scripts/validate_deep_pass_mechanisms.py` | `5d2a97f9` | `5d2a97f9` | ✓ |
| `scripts/eval_locus_resolver.py` | `3b0b2c02` | `3b0b2c02` | ✓ |
| `output_research/option_a_campaign/ledger.jsonl` | `e23c5bc9` | `e23c5bc9` | ✓ |
| `scripts/validate_p200.py` (reused template) | `d1c41876` | — (record) | n/a |

All four production artifacts byte-identical to the P200 END state → no drift since P200.

## Seal status (zetachain-2023-10-holdout)
`audits/zetachain-2023-10-holdout/_sealed_answer_key/` present and **unopened** at precheck: `report.md`, `data/`,
`README.md`. Opened only as documented: count-only viability (Step 4), full read at scoring (Step 7) — after both
freezes.

## Symlink
`output -> audits/quantamm-2024-12-eval/output` — intact.

## Corpus (source, NOT sealed)
zetachain-2023-10 omnichain bridge, **18 core `.sol` / 2444 LOC**: evm/ (ERC20Custody, Zeta tokens, ZetaConnector
eth/non-eth/base, ZetaInteractor, ZetaTokenConsumer×4, ImmutableCreate2Factory), zevm/ (SystemContract, ZRC20,
WZETA, ZetaConnectorZEVM, Uniswap, UniswapPeriphery). Classes A (theft/value-flow) · D (DoS) · E (auth) well-
represented; C (precision) light (ZRC20 gas-fee / consumer swap math); **B (oracle) absent — carved out**.

## END re-check
Recorded in `integrity_checks.md` at phase close — START==END required for the four production artifacts.
