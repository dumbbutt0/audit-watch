# P167 — Candidate Generation Hygiene

**Why:** P166's H10 was a **candidate-generation false positive**, not a protocol false positive. The
selection grep matched `originalOwner` only in vendored `lib/openzeppelin-contracts/.../mocks/
ERC1271WalletMock.sol` (+ permit2's copy) — **0** hits in protocol `src/`. The reject-first protocol caught it
at gate G0 for zero harness cost, but the cheaper fix is to never let vendored/test/mock noise become a
candidate. P167 improves the *input* to the protocol.

**Boundaries:** research-only, un-wired; no change to the production `generate_scope_inventory.py`, detectors,
routing, severity, or submission policy. `fabrication_rate=0` stays the only other hard rule.

## Signal-provenance taxonomy (`candidate_signal_source`)
| Source | Meaning | Allowed as a candidate? |
|---|---|---|
| `protocol_src` | in-scope protocol source | **yes** (the only quality input) |
| `protocol_test` | `test/`, `tests/`, `*.t.sol`, `*.s.sol` | no |
| `vendored_lib` | `lib/`, `vendor/`, `node_modules/`, `deps/` | no |
| `mock` | `mock/`, `mocks/` | no |
| `generated` | `out/`, `cache/`, `build/`, `dist/`, `artifacts/`, `examples/`, `scripts/`, `broadcast/` | no |

`classify_signal_source(path)` assigns these by path part (priority vendored → mock → test → generated → src),
plus a filename check for `*.t.sol`/`*.s.sol`.

## The rule
1. **Exclude** candidate-generation signals originating from `lib/ vendor/ node_modules/ test/ tests/ mocks/
   mock/ examples/ scripts/` (+ build/out dirs). `scan_signals(corpus_root, pattern)` walks `*.sol` and returns
   **only `protocol_src`** hits by default (`include_nonprotocol=True` returns all, tagged with provenance).
2. **Record provenance** — every campaign row carries `candidate_signal_source`.
3. **Reject candidate creation** if `candidate_signal_source != protocol_src`, unless `research_override=true`
   (to record a documented-noise lesson like H10). `record()` raises `ValueError` on a non-protocol_src signal
   without the override. A `None`/unset value is legacy and does not trip the gate (backward-compatible).

## Worked example — how this would have caught H10
```
$ echo '{"corpus_root":"audits/revert-lend-2024-03-strict-eval/contracts","pattern":"originalOwner"}' \
    | python scripts/research/option_a_campaign.py scan
[]                      # 0 protocol_src hits (raw grep had 2, both in lib/.../mocks)
```
Under P167, H10 would never have been generated as a candidate. Recording it as a lesson requires
`research_override=true`.

## Success metric (P167)
Increase source-refutation **quality** (refutations should be meaningful — DESIGN_INTENT / PRIVILEGED_ONLY /
NO_RECIPIENT_CONTROL / GATE_REFUTED — not lib-noise), reduce obvious junk candidates, **preserve
harnesses_avoided**. No routing/detector/severity change.
