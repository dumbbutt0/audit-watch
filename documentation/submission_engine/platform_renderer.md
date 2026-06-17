# Platform Draft Rendering

The **platform renderer** (`submission/renderers/`) turns a **gate-validated**
candidate into a platform-shaped human draft (Immunefi / Code4rena). It is the
step after readiness:

```
candidate.json
  -> submission_gate.py        (validate — the authority)
  -> non-blocking status
  -> platform DRAFT (.md)      (this layer)
  -> human copy/paste          (the only way anything is ever submitted)
```

## What it is — and is not

- It produces a **draft markdown file** for a human to read and copy/paste.
- It is **not** a submitter. There is no API call, no browser/clipboard
  automation, no "open the platform with fields filled". By design the maturity
  path stops at a watermarked draft.

## The gating rule

A draft is emitted **only** for a non-blocking gate status. A gate result is
**mandatory** — `candidate.json → draft.md` without validation is refused.

| Gate result | Platform draft? |
|---|---|
| `DO_NOT_SUBMIT` | **No** |
| `NEEDS_MORE_PROOF` | **No** |
| `READY_FOR_HUMAN_REVIEW` | Yes — watermarked "REVIEW DRAFT, warnings present" |
| `READY_TO_SUBMIT_AFTER_APPROVAL` | Yes — watermarked "final manual review still required" |

`emit_draft(candidate, gate_report, platform)` returns `(False, reason)` for a
blocking status and never renders anything in that case.

## The DRAFT watermark

Every emitted draft begins with:

```
> **DRAFT ONLY — NOT SUBMITTED**
>
> Gate status: <status>
> Human approval required: true
> <REVIEW DRAFT + warnings>  |  <Final manual review still required before submission.>
>
> Remove this block (and the Human Review Checklist, if present) before submitting.
```

This prevents a rendered `.md` from being mistaken for permission to submit.

## CLI (standalone renderer)

```bash
python -m submission.renderers.platform_renderer \
  --candidate submission_candidate.json \
  --platform immunefi \
  --run-gate \
  --out immunefi_submission.md
```

- `--candidate` (required), `--platform immunefi|code4rena` (required).
- A gate result is required: pass **`--run-gate`** (validate in-process) **or**
  `--gate-result <file>` (a gate report, or a `submission_gate --json-out`
  envelope). Passing both is an error.
- `--out` writes the draft (else stdout).

**Exit codes:** `0` draft written · `3` refused (blocking gate status — no file) ·
`1` input/validation error (missing candidate, no gate result, bad platform).

## CLI (via the candidate author)

```bash
python -m submission.author.candidate_author \
  --report report.md --poc-output poc.log --scope scope.md \
  --out submission_candidate.json \
  --emit-platform immunefi --platform-out immunefi_submission.md
```

`--emit-platform` forces a gate run and then renders. A **blocking** status is a
soft refusal: the author prints `platform draft NOT emitted: …`, writes no draft,
and still exits `0` (authoring itself succeeded). An allowed status writes the
draft to `--platform-out`.

## Section maps

**Immunefi:** Program · Asset / Target · Impact · Severity · Title · Description ·
Vulnerability Details · Impact Details · Proof of Concept · Recommended Mitigation ·
Evidence · Assumptions / Limitations · Human Review Checklist.

**Code4rena:** Title · Summary · Vulnerability Details · Impact · Proof of
Concept · Recommended Mitigation · Links to Affected Code.

Fields are formatted straight from the candidate; absent fields render
`_Not provided._` / `_None provided._` rather than inventing content. The schema
has no mitigation field, so **Recommended Mitigation** is an explicit
`_To be completed by the human reviewer._` placeholder.

## Clean copy (strip internal artifacts)

A watermarked draft carries internal-only blocks a human must delete before
pasting into the platform: the `DRAFT ONLY — NOT SUBMITTED` watermark and the
Immunefi `## Human Review Checklist`. The **cleaner** (`submission/renderers/clean.py`)
removes exactly those and writes a separate clean copy.

It is **convenience output, not proof of readiness**: it operates only on an
already-allowed watermarked draft, never re-runs the gate, never rewrites report
content, and never erases the original draft.

| Input | Clean copy allowed? |
|---|---|
| No gated draft (no watermark) | **No** |
| Watermark with a blocking gate status | **No** |
| Watermarked draft (non-blocking status) | Yes — emits clean copy |
| A clean copy already | **No** (no further transformation) |

The cleaner removes **only** the watermark block (incl. its warnings and the
"remove before submitting" note) and the `## Human Review Checklist` section. It
does not change severity, fill missing fields, reword anything, or drop
caveats/limitations that are part of the vulnerability explanation. Every clean
copy begins with a provenance comment:

```markdown
<!-- Clean copy generated from a gated draft. Human approval still required. -->
```

CLI (standalone, or via the renderer's `--clean-out`):

```bash
python -m submission.renderers.clean \
  --draft immunefi_submission.draft.md --out immunefi_submission.clean.md

python -m submission.renderers.platform_renderer \
  --candidate submission_candidate.json --platform immunefi --run-gate \
  --out draft.md --clean-out draft.clean.md          # --clean-out requires --out
```

Exit codes: `0` clean copy written · `3` refused (no watermark / blocking status /
already clean) · `1` input error (`--out == --draft`, unreadable file). The
original draft is always left byte-identical.

## Safety guarantees

1. Drafts only — no submission, no API, no browser/clipboard automation.
2. `DO_NOT_SUBMIT` / `NEEDS_MORE_PROOF` can never produce a draft.
3. A gate result is required before any rendering.
4. Every draft carries the DRAFT-ONLY watermark; human approval is always required.
5. The internal **Human Review Checklist** and the watermark are draft-only and
   must be stripped before submitting (the draft says so). The clean-copy helper
   strips exactly those and nothing else, to a separate file, leaving the
   original untouched — and refuses blocking-status or non-gated input.
6. No evidence is fabricated; mitigation is a human TODO.
7. `submission/renderers/*.py` imports nothing from the detection pipeline.

## Testing

```bash
/home/dummy/.local/bin/pytest tests/submission/test_platform_renderer.py -v
```

The headline acceptance test proves that `DO_NOT_SUBMIT` and `NEEDS_MORE_PROOF`
candidates cannot emit an Immunefi or Code4rena draft.
