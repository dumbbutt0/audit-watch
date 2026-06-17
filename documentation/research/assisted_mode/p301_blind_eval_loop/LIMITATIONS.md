# P301 — LIMITATIONS

- **Recall-gap mining ≠ fresh blind discovery.** For the match_matrix targets the misses come from the PRIOR eval's
  scoring (read-only), not a new virgin run. True-blind (freeze→reveal) applies only to unrevealed holdouts and is run
  via p276_corpus_replay when their key is ingested.
- **7 of 20 need key ingestion** (kb_assemble holdouts: spectra/predy/munchables/vultisig/decent/dittoeth/basin) —
  marked `needs_key_ingestion` until a human ingests their public findings. They contribute no recall gap until then.
- **Recovery is PoC-bounded.** This iteration recovered 2 under-recalled loci (reusing P300 PoCs); the 56 remaining
  gap items are needs_execution — recovered as subagents build PoCs over subsequent /loop iterations. Full recovery is
  a multi-iteration grind, not one pass.
- **Human-only loop.** The loop stages recall recoveries + learning proposals; it cannot promote them or write
  ground_truth. The "don't miss it again" effect requires the human promote step.
- **Not auto-started.** The harness is loop-ready + iteration-1 validated; it does not self-launch an unbounded
  autonomous run — invoke `/loop` to grind the queue.
