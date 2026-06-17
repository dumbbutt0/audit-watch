# P300 — EVIDENCE_AUDIT

## Confirmations (each = verifier-judged, real forge run; confirmed-FP=0)
- **silo M-05** (logic_differential) — verbatim `_accrueFee`/`_update`/`_afterTokenTransfer` ordering; bug test:
  feeRecipient earns 50e18 of rewards accrued to pre-existing holders; control (settle pre-mint): feeRecipient 0,
  user 100e18. Divergence asserted; assertion_map present.
- **silo M-06** (logic_differential) — verbatim `_accruedFeeShares` Floor rounding; bug: fee stranded / residual to
  LPs (500005 vs control 500004); control: vault-favoring Ceil removes the gain. Honest direction note recorded by
  the builder (Floor under-credits the fee recipient — opposite of the naive framing, but a real misallocation).
- **panoptic M-01** (logic_differential, ADJACENT) — verbatim getLiquidationBonus cross-shortfall: add leg floor
  (convert0to1) vs deduct leg RoundingUp → bonus 4533 vs consistent-rounding 4534 (delta 1); control at exact price
  matches. Honest caveat: whether the RoundingUp is deliberate protocol-favoring is a design-intent question → MEDIUM,
  human-review tier.

## Honest non-confirmation
- **revert-lend H-03** — built as exploit, **REFUTED**: per-token NPM approval gates the claimed cross-position
  impact; a callee acting on a different tokenId reverts at the approval gate. exploit_tests:[], validity_confirmed
  False → needs_human. (The surfaced PARTIAL was transformer-trust framing; the executed PoC showed the cross-position
  vector is unreachable from `transform` alone.)

## Submission filter (precision)
4 records → 3 submit (the confirmed), 1 needs_human (H-03), **0 filter leaks**. Synthetic probes: a fabricated
record (validity flag set, status=inconclusive) → needs_human (the filter requires a real confirmed status).

## Integrity
confirmed-FP=0; verifier byte-identical (1a005811); answer-key match_matrices + rejection_rules.jsonl + ground_truth
byte-identical (read-only honored); proposals staged ONLY in data/learning/_proposed/ (promoted=false); contest source
untouched (PoCs copy control-flow into pocs/p300/); symlink unchanged; un-wired from confirm gates.
