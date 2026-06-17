# P279 — EVIDENCE_AUDIT (manual inspection, 11 packages)

Machine record: `outputs/sample_audit.json`. Inspected the 3 READY + 8 NEEDS_MORE_EVIDENCE across classes against the
coverage manifest. Checks: evidence complete? source-backed? hallucinated field? placeholder leaked? assertion
implementable? correct status?

## The 3 READY (verified manifest-true, no hallucination)
| candidate | class | manifest basis (verified) | assertion implementable? | verdict |
|---|---|---|---|---|
| `IBeanstalk.cancelPodListing` | ORDER | external, modifiers=[], tags=[accounting] | yes — assert a non-owner cancels/redirects the listing | READY ✓ |
| `L2Governor.execute` | ACCESS | public, payable, modifiers=[], tags=[config,migration] | yes — assert an unauthorized EOA executes the config/migration path | READY ✓ |
| `V3Vault.transform` | ACCESS | external, modifiers=[], tags=[config,token], **external_calls=true** | yes — assert the arbitrary external call moves value while end-checks pass | READY ✓ |

All three: source_basis cites the exact manifest fields (not award text); no placeholder leaked; PoC assertion is
implementable; status correct. **No hallucinated core evidence.**

## NEEDS_MORE_EVIDENCE spot-checks (correctly blocked)
- `AccountingManager.fulfillCurrentWithdrawGroup` — has `onlyManager` ⇒ auth-guarded ⇒ attacker_path LOW (caught by the
  audit; the auth-guard override was added because a substring false-match had let it through). Correct.
- `V3Vault.liquidate` / `mint` / `withdrawReserves` (ACCOUNTING/SHARE) — value-flow anomaly not manifest-visible ⇒ LOW
  ⇒ blocked. Correct (needs value-flow derivation).
- `Swapper:_routerSwap`, `Automator:_transferToken`, `V3Vault:_withdraw` — internal helpers / not clean external entry
  ⇒ LOW ⇒ blocked. Correct.

## Audit result
- placeholder leaked into any READY: **none**.
- hallucinated core field in any READY: **none** (all source_basis manifest-verified).
- mis-classified READY (should be blocked): **none after the auth-guard fix**.
- The gate is strict: auth-guarded + value-flow-invisible classes are correctly held at NEEDS_MORE_EVIDENCE.
