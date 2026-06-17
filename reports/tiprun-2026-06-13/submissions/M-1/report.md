# M-1 — MERGED into F-1 (same root cause)

M-1 (inverted ratio guard blocks legitimate de-risking of an unhealthy account) is **not a separate root
cause**. It is the opposite-direction symptom of the **same single inverted comparison** at
`Risk.sol:133` that drives F-1. A single fix to `Risk.checkValidTransition` resolves both.

➡ **The authoritative writeup is the combined report:** [`../F-1/report.md`](../F-1/report.md)
(F-1 Critical = collateral-withdraw bypass; M-1 Medium = de-risk DoS — "Manifestation B").

This folder is retained only as a self-contained **reproduction** of the M-1 manifestation:
- PoC: `poc/PoC_DeriskDoS.t.sol` (also in `../F-1/poc/` and `../../harness/test/`)
- Captured run: `poc_output.log` · steps: `repro.md`
- The original standalone writeup is preserved as `report.merged.md` for history.

Do **not** submit M-1 as a separate report — it would be deduped against F-1. Submit the combined F-1 report.
