# P254 — VERDICT

## B — PROCEDURE_PROMISING_BUT_NEEDS_MORE_HELDOUT

### What happened
Blind, freeze-before-reveal, on an unseen contest (loopfi-2024-07), the five-operation routine was performed by
hand on 4 pre-selected `BASE_BORN_INCOMPLETE` loci. It produced the **first genuine blind chain completion in
the entire P246→P253 arc**: at **L2** the **INVARIANT_DELTA_COMPUTATION** (+ STS) operation turned a base "I see
a penalty/collateral asymmetry but haven't computed the exploit" candidate into the awarded **High #399**'s exact
profitable-self-liquidation chain (collateral computed from full `repayAmount`, debt reduced by
`repayAmount·penalty` → liquidator/borrower profit, drains lenders). That is a **procedure-completed-not-base**
recovery of an awarded High, with **0 severe false positives** and manageable burden.

### Why B and not A
This single contest **literally clears the stated strong-pass threshold** (≥1 AWARDED_EQUIVALENT, 0 severe FP,
manageable, recovered chain not base-completed). That is real and is reported as a positive — not buried. But
declaring **A (build the scaffold)** off this evidence would repeat the exact over-optimism the arc has been
correcting (P249/P251 declared architectures "ready," P250/P252 then showed **0** blind lift). Three facts hold A back:

1. **n=1, 1/4 loci.** One awarded recovery on one contest is an existence proof, not a rate.
2. **1/4 awarded-mechanism selection.** On the other 3 loci the routine engaged the *correct awarded code* but
   completed the *wrong mechanism* — it **refuted** the actual awarded bug at L3 (stranded leftover funds #87,
   which it treated as benign) and selected non-awarded mechanisms at L1 (claim-amounts) and L4 (cooldown-reset)
   while the awarded mechanism (L4 MIN_SHARES donation #228/#382) sat visible in the same body. The operations
   execute fine; **mechanism-selection** is the residual gap. A scaffold that performs these operations would
   inherit that gap and complete plausible-but-non-awarded chains 3 times for each awarded one.
3. **Thin margin on the win.** The L2 base candidate had already ~90% identified the asymmetry; the routine's
   genuine marginal contribution was the profit/exploit computation (IDC) — valuable, but a narrow delta.

So the routine is **promising** (it can, blind, complete an awarded High that a checkpoint-only pass could not —
the qualitative shift P253 asked for) but **not yet build-justified**.

### Not C, not D
- **Not C (NOT_USEFUL):** it produced a real awarded-High completion blind, 0 FP, low burden — clearly useful.
- **Not D (OPERATION_SET_WRONG):** the operations are the right ones — IDC/STS closed the awarded chain and CCIT/
  AAS correctly refuted/bounded two over-claims. The gap is selection-among-mechanisms, not the operation set.

### Required next step before any scaffold build
Run the **same manual routine, blind, on 2–3 more unseen contests** (different architectures), measuring two
things: (a) does the L2-style **procedure-completed-not-base awarded recovery recur** (≥1 per contest), and
(b) does the **awarded-mechanism selection rate** rise materially above 1/4 — i.e. can the operator, performing
the operations, be steered toward the awarded mechanism rather than the first plausible one. **Build the
exploit-chain construction scaffold only if both hold across the additional held-out contests.** If recoveries
don't recur, or selection stays ~1/4, the gap is mechanism-discovery (a training/tooling problem), not chain
completion, and a scaffold won't fix it.

### Honest caveats
n=1 contest; no PoCs (the L2 match is by root-cause/impact equivalence to #399, not an executed exploit);
reveal was via the public C4 report/issues post-freeze (no local key existed); same-operator confound (the
confound-light signal is the L2 procedure-completed-not-base delta, which is the one credited). Per the
operator's instruction, **no softening toward A** — the one genuine completion is recorded as promising, and the
build decision stays gated on more held-out evidence.

### Arc
P249(A built)→P250(B 0 blind lift)→P251(A built)→P252(B observe≠complete)→P253(B completion=5 recurring ops,
prove blind first)→**P254(B first genuine blind completion of an awarded High via IDC, but 1/4 mechanism-
selection on n=1 → promising, prove it recurs before building).**
