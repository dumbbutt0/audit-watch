# Dashboard Operator Guide — How to read & use the Funnel

A practical guide for a human operator. The dashboard is **read-only and reject-first**: it shows what the
evidence supports, never what it hopes. Nothing here submits anything. Your job is to read it correctly and
decide the human gates it cannot.

---

## 1. Launch it
```bash
python scripts/dashboard.py        # serves on http://localhost:8765  (uvicorn, port 8765)
```
Open a browser at **http://localhost:8765**. (If the server runs in WSL and your browser is on Windows,
`localhost:8765` normally works; otherwise use the WSL IP.) Every page auto-refreshes (~10s); it never writes.

> **Operational note:** after code changes, **restart `python scripts/dashboard.py` and hard-refresh `/funnel`**
> to clear stale server modules and cached JS. (A running server holds an in-memory copy of `funnel.py`, and the
> browser caches `funnel.js`; if metric tiles ever disagree with the table rows, this is almost always the cause —
> the tiles are computed from the same rows the table renders and cannot drift within a fresh load.)

## 2. The pages
| URL | What it is | When to use |
|---|---|---|
| `/` | Main audit dashboard (active audit, status, runs) | day-to-day pipeline status |
| **`/funnel`** | **Blind-to-Reproducible Funnel** — the assisted-mode lifecycle view | **the page you live in for finding triage → human review** |
| `/candidates` | Per-candidate detail | drill into one candidate |
| `/validation` | Validation console (label/promote bundles) | manual validation labeling |
| `/metrics` | Calibration metrics (FP/recall) | tuning review |
| `/view/submission/{id}`, `/view/poc/{id}`, `/view/source/{id}` | render a package/PoC/source | open the evidence behind a row |

The rest of this guide is about **`/funnel`** — the surface that tracks each finding from lead → reproduced PoC →
submission package → **human review** → recorded outcome.

### Three pages, one source of truth
- **`/funnel` is the authoritative assisted-mode surface** for submission readiness, PoC handoff, human-final-gate,
  and outcome. If you want to know whether something is reproduced / ready / submitted / accepted, look here.
- **`/candidates` and `/validation` are separate research-detector domains** (judge corpus, candidate folders,
  human labels). They intentionally carry **no** submission/outcome/SUBMITTED state and **no** funnel metrics —
  seeing none there is **correct, not a bug**. They are reject-first by construction (`routing_allowed:false`,
  "never route/severity/submit"), with their own counts computed single-source per request (so they can't drift).
- **All three** share one operational rule: after code changes, **restart `python scripts/dashboard.py` and
  hard-refresh** the page to clear stale server modules and cached JS.

### Audit dropdown & all-audits list (bounty vs eval/research corpus)
The dashboard **derives** a read-only `kind` per audit — **bounty** (contest contains `immunefi`/`hackerone`, or
the k2-kinetic / circle allowlist) vs **eval/research corpus** (everything else) — and uses it to group the
**audit dropdown** (optgroups) and give the **All-audits tab** a Kind column + a **Bounty / Eval / All** filter
(the **active audit always shows**). `config/dashboard_view.json → hidden_audit_kinds` can hide a kind from the
view (UI-only, reversible).

> **2026-06 cleanup:** the operator hard-deleted 10 bug-bounty engagements they declared invalid — origin,
> circle, enzyme, flare, gearbox, rhinofi, stacks, tools-for-humanity, wormhole, xterio — removing their
> `audits/<id>/` workspaces, `contracts/` source clones, and `registry.json` entries (irreversible; repo not under
> git). **k2-kinetic-2026-04 was kept** (the one remaining bounty). The registry is now 42 entries (1 bounty +
> 41 eval); `hidden_audit_kinds` was cleared to `[]` so k2 stays visible. Memory notes about the deleted
> engagements were intentionally retained as historical records.

### Focused view (and why nothing was deleted)
`/funnel` defaults to a **Focused view** — the assisted-mode arc + the findings that are ready for human review
(currently Vultisig H-01 and SecondSwap M-11). Use the **Focused / Show all** toggle above the table to switch.
This is a **reversible display filter on the table rows only**; the metric tiles always reflect **all** records
(the caption shows "X of N"). The legacy/eval/bounty history is **intentionally kept on disk** — it is
load-bearing (the eval corpus the phases ran against, real bug-bounty deliverables, test fixtures) and the repo
is **not under git**, so it was *not* deleted. Clutter is reduced by the filter, not by destroying evidence.

---

## 3. The mental model (read this first)
A finding flows through one pipeline:

> Lead surfaced → Investigation safe → Converted → Severity gated → PoC handoff → **Reproduced** →
> Submission package → **Human review** → *(human records)* Submitted → Outcome

Two load-bearing rules the dashboard enforces — internalize them:
- **REPRODUCED ≠ SUBMITTED.** An executable PoC existing does not mean anything was sent anywhere.
- **SUBMITTED appears ONLY when a human recorded it** (via the outcome recorder). It is never inferred from
  "Ready for human review." If you see no SUBMITTED chip, nothing was submitted — that is the normal, safe state.

`pipeline_status` is **computed from the evidence**, not from a record's wishful label. A record claiming it is
"ready" but missing a PoC or evidence bundle will be shown at its real, lower stage.

---

## 4. Metric tiles (top of `/funnel`) — what each means and what "good" looks like

**Pipeline volume**
- *Leads surfaced / Investigated* — how much surface was examined.
- *Clean hits / Strong partials* — conversions worth pursuing.
- *PoC handoffs* — candidates that passed the handoff gate.
- *PoCs reproduced* — **executable** PoCs that fail-on-vuln / pass-under-patch (counts them even after they
  advance to a package). This is the real "we proved it" number.
- *Partial repros / Not reproduced* — incomplete or failed reproductions.

**Safety (these are the trust signals — watch them)**
- *Sev FP (post-gate)* — **must be 0.** A non-zero value means a weak/over-rated finding survived the severity
  gate; investigate before trusting anything else on the page.
- *Sev FP (pre-gate)* — informational (caught before the gate).
- *Controls mis-promoted* — **must be 0.** Known-safe privileged controls should never be promoted.
- *Not run (excluded)* — honestly excluded items (not failures).

**Provenance**
- *Blind records* — found by the (now-paused) autonomous path.
- *Assisted records* — a human/tool supplied the invariant and Audit-Watch validated it.
- *Assisted → PoC handoff* — assisted candidates that reached validated-for-handoff.

**Human review & outcome (the action zone)**
- *Submission-ready (human)* / *Ready for human review* — packages waiting for **you**. Each one is a to-do.
- *Approved to submit* — count a human marked `APPROVED_TO_SUBMIT`. **0 until you decide.**
- *Submitted* — count actually submitted (human-recorded). **0 means nothing has been sent.**
- *Accepted / Duplicate / Rejected / Invalid* — program outcomes; only ever non-zero **after** submission.
- *Pending outcome* — awaiting a recorded human decision/outcome.

> Current truth at the time of writing: Ready for human review = **2**, Submitted = **0**, Accepted/Duplicate/
> Rejected = **0**. That is correct and safe — two packages await your review; nothing was submitted.

---

## 5. The findings table — column by column
| Column | What to read | What to look for |
|---|---|---|
| **Subject** | which audit/contest | (control rows are tagged `control`) |
| **Phase** | when discovered | provenance only |
| **Finding** | finding id | join key to the package |
| **Contract.fn** | localized mechanism | where the bug lives |
| **Source / assisted status** | `blind` vs `assisted` (+`invariant ✓` and the assisted validation state) | is this human-supplied or autonomous? assisted rows show the validation verdict |
| **Blind rank / score** | lens surface score | low-signal context |
| **Conversion** | CLEAN_HIT / STRONG_PARTIAL / ADJACENT / REJECTED | did it convert to a real lead? |
| **Mechanism** | mechanism-correctness note | sanity of the root-cause |
| **Severity gate** | passed / demoted / blocked + an `FP` flag | **`FP` flag = stop and investigate** |
| **Adversarial** | PASS / bounded | did an independent review hold it up? |
| **Pipeline status** | the computed stage (the truth) | `SUBMISSION_READY_HUMAN_REVIEW` = needs you |
| **PoC** | poc_status + the `forge test` command (when reproduced) | copy this command and rerun it locally |
| **Submission** | the submission badge + **"⚠ NOT submitted — human review required"** | confirms it is *not* sent |
| **Human gate / outcome** | `human_final_gate`, *not submitted*, `outcome`, and the **scope / dup / sev** sub-checks | your checklist status lives here |
| **Blocker** | the top reason it can't advance | what's missing |
| **Artifacts** | links to test file / PoC dir / evidence bundle | open the evidence |

---

## 6. What to do when you see a "Ready for human review" row
This is the only place the dashboard hands work to a human. For each such row:
1. **Open the evidence** (Artifacts column → evidence bundle, PoC test) and the submission package
   (`submission_draft.md`, `evidence_bundle.md`, `reviewer_notes.md`).
2. **Rerun the PoC** — copy the command from the **PoC** column and run it locally; confirm it passes on the
   pinned source. Re-check the patch test if present.
3. **Work the human final gate** (`human_final_gate.md`): asset in scope · impact in scope · duplicate /
   publicly-known search · program severity tier · no internal/tool language in the report body · no overclaim ·
   minimal source-backed mitigation · every claim cites source or PoC.
4. **Record the decision** with the outcome recorder (nothing is sent — this only records your call):
   ```bash
   # edit a record JSON (schema: schemas/assisted_outcome_record.schema.json), then:
   python scripts/assisted/record_assisted_outcome.py --record <your_outcome>.json
   ```
   Set `human_final_gate` to `APPROVED_TO_SUBMIT` or a `DO_NOT_SUBMIT_*` reason. `submitted=true` is **rejected**
   unless `human_final_gate=APPROVED_TO_SUBMIT`; `accepted/duplicate/rejected` are **rejected** unless
   `submitted=true`. The dashboard then reflects your decision (and a SUBMITTED chip only if you actually
   submitted and recorded it).
5. **Submission itself is manual and external.** Audit-Watch never submits.

The two packages currently waiting: **Vultisig H-01** (blind, claimed High) and **SecondSwap M-11** (assisted,
claimed Medium) — both REPRODUCED, both pending your scope/duplicate/severity review.

---

## 7. Red flags — scan for these every time
- **Sev FP (post-gate) > 0**, or any row with an `FP` flag in the Severity-gate column → do not trust that row; investigate.
- **Controls mis-promoted > 0** → a known-safe control was promoted; bug.
- A **SUBMITTED chip you did not record** → should be impossible; investigate the outcome records.
- A row at `SUBMISSION_READY_HUMAN_REVIEW` whose **PoC column is empty** or whose Artifacts don't resolve → the
  package is not actually backed; treat as not-ready.
- `scope`/`dup`/`sev` sub-checks still `PENDING` on something you're about to approve → finish the checks first.

---

## 8. What the dashboard is NOT telling you
- It does **not** mean a finding is valid for a program — **scope and duplicate are your call**, shown `PENDING`.
- It does **not** mean severity is program-final — `claimed_severity` is conservative; the program's matrix may differ.
- It does **not** mean anything was submitted or accepted unless the Submitted/Accepted tiles and the row's
  Human-gate column explicitly say so (from your recorded outcome).
- It is **not** a claim of autonomous discovery reliability — the blind path is paused; see
  `autonomous_blind_discovery_ceiling.md`.

---

## 9. One-line cheat sheet
> Live in `/funnel`. Treat every **Ready for human review** row as a to-do: open evidence → rerun the PoC →
> work the human final gate → record `APPROVED_TO_SUBMIT`/`DO_NOT_SUBMIT`. Trust the page only while
> **Sev FP (post-gate) = 0** and **Controls mis-promoted = 0**. **Submitted = 0** is the normal safe state until
> *you* decide. READY never means SENT.
