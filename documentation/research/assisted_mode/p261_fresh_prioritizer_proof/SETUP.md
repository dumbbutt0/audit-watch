# P261 — SETUP
First FRESH blind run of the P260 locus-shape prioritizer. PROOF, not build: `scripts/research/locus_shape_prioritizer.py`
+ config UNCHANGED (hashes recorded; verified unchanged at end). Target = 2026-04-monetrix (operator-committed).

## Isolation
monetrix SOURCE cloned (content-safe, public) to /tmp/p261_fresh/monetrix (NOT under audits/, not committed).
Manifest built via `build_coverage_manifest.py --contract <src> --out <P261 outputs>` (uses monetrix scope.txt;
only READS size-credit static.json, keyed by file → no cross-contamination). Checkpoints + prioritizer run with
--manifest/--out into P261 outputs. Active audit `size-credit-2024-06-blind` unchanged (no switch). Findings repo
NOT cloned (not public; sealed by unavailability).

## Outcome
Reveal-unavailable (findings not public) ⇒ cannot score ⇒ VERDICT NEEDS_MORE_FRESH_HELDOUT. Full pre-reveal
pipeline (manifest→checkpoints→prioritizer→selected loci→B/C→5 ops) run + frozen+hashed for a DEFERRED reveal.
