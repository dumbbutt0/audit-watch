# P253 — Exploit-Chain Construction Scaffold (DESIGN SKETCH ONLY — nothing built)

A design hypothesis for the architecture the forensic points to. **Not built; not wired; design-only.** It
must be validated on a held-out contest before any implementation (see VERDICT).

## Where it sits (the new bottleneck location)
```
Coverage gate (P245)            observation        ✓ works
Examine-time checkpoints (P249/P251)  candidate birth + "ask the question"   ✓ works (P252: fired on exact loci)
>>> EXPLOIT-CHAIN CONSTRUCTION SCAFFOLD <<<   complete the chain for a born candidate   ✗ the gap
Existing precision pipeline     adjudication (ICE/multi-pass/FP/triage)   (unchanged)
```
Checkpoint = *observe a locus and ask*. Scaffold = *for a candidate that already exists, run the operations
that COMPLETE its chain*. Different stage (post-birth, pre-validation), different job (perform, not ask).

## The procedure (ordered, per born candidate)
Run the 5 recurring operations as an explicit, ordered completion routine; each produces a concrete artifact:
1. **ADVERSARIAL_ACTOR_SUBSTITUTION** — replace the assumed honest/average actor with an attacker; ask who can
   call it, on whose behalf, who chooses the inputs. Artifact: the attacker + their controlled inputs.
2. **STATE_TRANSITION_SIMULATION** — instantiate the relevant state, **especially the edge/first/empty state**
   (the single most productive case here: salty `existingTotalShares==0`), and step the transition under the
   adversary's inputs, including repetition. Artifact: pre→post state trace.
3. **CROSS_CALL_IDENTITY_TRACKING** — resolve who each address/`msg.sender`/`from` actually is across the call
   chain. Artifact: identity map per hop.
4. **INVARIANT_DELTA_COMPUTATION** — compute the numeric delta of the protected quantity (rounding direction,
   share/reward proportion, length/index exactness) before vs after. Artifact: the delta + who it favors.
5. **TERMINAL_STATE_EVALUATION** — evaluate the end state: who holds what, who is deprived, is it permanent.
   Artifact: who-wins / who-loses / magnitude → the completed chain (or an explicit abandonment).

Output = a completed exploit chain OR an explicit "no path" abandonment — routed to the **existing** precision
pipeline. Invariants (same as the checkpoints): emits no findings, sets no severity, concludes nothing on its
own; default-off; un-wired; never auto-submits.

## Per-operation hypothesis (expected completion-recovery / cost / FP-risk) — to be TESTED, not promised
| Operation | recovers (this corpus) | cost | FP-risk |
|---|---|---|---|
| STATE_TRANSITION_SIMULATION (edge/first-state) | salty H-02/H-04, vultisig M-03, munchables M-03 (8 wt) | MED | LOW–MED (speculative state paths → gate-filtered) |
| ADVERSARIAL_ACTOR_SUBSTITUTION | salty M-01, vultisig H-02, centrifuge M-04, munchables H-01 (6 wt) | LOW | LOW |
| TERMINAL_STATE_EVALUATION | decent H-04, centrifuge M-05 (4 wt) | LOW–MED | LOW |
| INVARIANT_DELTA_COMPUTATION | kleidi M-02, centrifuge M-07 (2 wt) | LOW | LOW (mechanical) |
| CROSS_CALL_IDENTITY_TRACKING | decent H-03 (3 wt) | MED | LOW |

## The honest risk this sketch carries (why it is only a sketch)
P252 proved that adding reasoning STRUCTURE to a prompt (the checkpoint's questions) did NOT yield completion
on unseen code — observation ≠ completion. The scaffold is *more* structure (an ordered perform-procedure, not
a question), so it is a better-motivated attempt — but it could hit the **same wall**: prompting "simulate the
first-depositor state" does not guarantee the model performs the simulation correctly on unseen code. The
forensic establishes WHICH operations are needed (recurring, cross-contest); it does NOT establish that a
scaffold can PERFORM them blind. That is the open question the next phase must test, not assume.
