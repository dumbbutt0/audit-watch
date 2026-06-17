# P223 — Freeze manifest (Step 8)

All P223 candidate artifacts were hashed **before** the sealed answer key was opened. Machine-readable hashes:
`FREEZE_MANIFEST.json` (15 artifacts). Key facts:

- `answer_key_read_before_freeze: false` — discovery/triage/gates/L3/queue all completed blind.
- Sealed answer key sha256 at freeze = `8eacd80…a9c23` (== precheck witness). Re-checked at scoring (Step 9).
- Frozen set: coverage_manifest · findings_deep_trace · merged_findings · triage `_decisions` ·
  submission_pack · L3 records (SC-01/03/04) · dry-run queue (SC-01/03/04 + manifest) · SC-01 harness + MockWETH
  · CANDIDATE_REGISTER.
- After this point, candidate identities/severities/L3 verdicts are frozen; scoring only reads them and the key.
