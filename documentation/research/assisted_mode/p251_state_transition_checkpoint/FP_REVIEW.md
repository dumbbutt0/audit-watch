# P251 — Part D: FP / Burden Review (3 mixed contests + negative controls)

Success bar: 0 high-confidence FP, no unrelated candidate-volume increase, 0 findings / 0 severity. Cleared by
construction (firing is interrogative).

## 1. Zero findings / zero conclusions (invariant verified on every run)
All four runs (munchables, kleidi, spectra, decent): `emits_findings:false`, `concludes_vulnerability:false`,
`output_type:"reasoning_records"`, **records with a conclusion = 0**. Every record: `severity:null`,
`exploit_hypothesis:""`. Runtime assert + unit test enforce it.

## 2. Three mixed contests — question-records vs constructed candidates (firing ≠ finding)
| Contest | type | question-records | constructed candidates | findings |
|---|---|---|---|---|
| munchables | state-transition **anchor** | 46 | 5 (the anchors) | 0 |
| spectra | accounting / vault | 12 | 0 (spectra's bugs are accounting/permission/cross-contract, not state-transition) | 0 |
| decent | cross-chain / mostly-routing low-state | 1 | 0 | 0 |
| **Total** | | **59** | **5** | **0** |
On the anchor contest the checkpoint asks 46 questions; 5 become candidates once answered. On the
accounting/vault and low-state contests it asks 12 / 1 — and **0** advance (no state-transition bug present).
Unrelated **candidate** volume increase = **0**. Volume is far below the P249 accounting checkpoint (234) and
dropped ~2× after the bounded tuning.

## 3. Benign code → no record / answered-no → no candidate
Negative controls (direct taxonomy): pure access-control `Guard.checkTransaction`, pure math `RayMath.fromRay`,
a plain getter, and a **CEI-correct standard ERC20 `transfer` (a real state update)** → **all fire NONE**. The
checkpoint does not flag CEI-correct/benign state updates → no generic state-change noise. On spectra/decent
the ~13 question-records that do fire (mostly S5 maturity/expiry views, one S4 branch) answer "no
attacker-chosen/repeatable/cross-user state transition" → 0 advance.

## 4. Operator burden
59 question-records across 3 contests (anchor-heavy munchables 46 + 12 + 1) + answering. Bounded and lower
than accounting; the tuning kept S3/S4 from generic-noise blow-up. As with P249, before any future
default-ON, scope firing to higher-attack-surface manifest items.

## Conclusion
0 high-confidence FP, 0 findings, 0 unrelated candidate-volume increase, no generic state-change noise
(CEI-correct updates and stateless/pure code fire nothing). The state-transition checkpoint is a reasoning
aid, not a detector — same FP-safety profile as the P249 accounting checkpoint, on a broader (state) surface.
