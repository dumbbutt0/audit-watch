# P235 — FREEZE MARKER (anti-hindsight gate)

**FROZEN_AT:** 2026-06-08, before any answer-key fetch (Phase 3 had not run).
**Subject:** reNFT 2024-01 (Code4rena), blind shadow workspace `audits/renft-2024-01-shadow`.

All artifacts below were committed before the official Code4rena report was fetched. Their sha256 are recorded
here; the reveal/scoring phase adds NEW files only (ANSWER_KEY_revealed.md, CONTEST_SCORECARD.md) and never edits
these frozen ones.

## Frozen content hashes
| Artifact | sha256 |
|---|---|
| candidates_renft.md (raw deep-trace) | `5d6ba1d380150e89fa14c0da05cdad2cd69b850033962d3b4a1f4f3d050b1779` |
| FROZEN_CANDIDATES.md | `1bc3845e56b17de6687470bd632b27334cb556862fc49812b1dc9b773d664b17` |
| FROZEN_RANKINGS.json | `06e969ace1087ebafd798cddfdca5e69ab5b81d0636d1cc94248cf21f63bcb5d` |
| FROZEN_SUBMISSIONS.md | `c35fab2e118720aa82603a75f0f91e43246f5f67c7e49cca4207c3e5c5f01796` |
| output_research/l3_readiness/RENFT-01.json | `dfea5e841fec03694fa154307e630bfd59ebbb646e75f8464b45118dd3de9566` |
| pocs/p235/renft/RENFT01_DisableModuleBypass.t.sol | `094481e4c751a794cd000ecfbae5b841d63a219706f76e7ffc7957a178ccbe1a` |

## Sealed blind-state witnesses (re-verified at freeze = never opened during the hunt)
| Sealed artifact | sha256 (== SETUP_WITNESS) |
|---|---|
| `_src/4naly3er-report.md` | `00e57abffb8cb0d5d3fc2cb8e3879b516c590595b47c9fabc300de6658784154` ✓ |
| `_src/bot-report.md` | `110aed3d10f42ed9b6a18d8adcc1e13b12c6d157cc3831f1b3d365359c821aeb` ✓ |
| `_src/bot-report.json` | `254ac9f9d362ba2f8e2ac38b768b8356925891018def9c47a73eb1601b3cd242` ✓ |
| `_src/slither.txt` | `fa8b7dc9dfbbce4edcf8ea3188f2cef34a9f9a4e9b5198416a1abe50c7be52d3` ✓ |

## Frozen hunt metrics
| Metric | Value |
|---|---|
| Candidate count | 10 |
| High-signal count | 1 (RENFT-01) [+4 medium-signal] |
| Harness count | 1 |
| Confirmed-L3 count | 1 (RENFT-01, 2/2 forge PASS) |
| False-Highs (decide()) | 0 |
| Pipeline depth executed | Steps 0.5→1.6 via real scripts; deep_trace/specialists in-session (manual deep-read across lenses) |
| Time allocation | setup ~20% · candidate-gen ~50% · flagship harness ~25% · submissions/freeze ~5%; ~0 on dead-end harnesses |

The hunt and submission drafts are now FROZEN. Proceed to Phase 3 (reveal + score).
