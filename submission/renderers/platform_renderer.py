#!/usr/bin/env python3
"""
platform_renderer.py — gated platform-draft rendering.

Turns a GATE-VALIDATED submission candidate into a platform-shaped human draft
(Immunefi / Code4rena). Central safety properties:

  - A draft is emitted ONLY when the gate status is non-blocking:
        READY_FOR_HUMAN_REVIEW or READY_TO_SUBMIT_AFTER_APPROVAL
    DO_NOT_SUBMIT and NEEDS_MORE_PROOF can never produce a draft.
  - A gate result is REQUIRED. The renderer either runs the gate itself
    (--run-gate) or is handed a gate-result file (--gate-result). It refuses to
    render a candidate that has not been validated.
  - Every draft is prefixed with a "DRAFT ONLY — NOT SUBMITTED" block so the
    file can never be mistaken for permission to submit.
  - There is NO submission code path here: no API calls, no browser/clipboard
    automation. The output is a markdown file for a human to copy/paste.

CLI:
    python -m submission.renderers.platform_renderer \
        --candidate submission_candidate.json \
        --platform immunefi \
        --run-gate \
        --out immunefi_submission.md

Exit codes:
    0  a draft was written
    3  refused: gate status is blocking (no file written)
    1  input/validation error (missing candidate, no gate result, bad platform)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import code4rena, immunefi

# the submission gate lives in a sibling package; imported in-process for a
# local validation call only (this is the gate, not the detection pipeline).
_GATES_DIR = Path(__file__).resolve().parent.parent / "gates"

ALLOWED_STATUSES = {"READY_FOR_HUMAN_REVIEW", "READY_TO_SUBMIT_AFTER_APPROVAL"}
BLOCKING_STATUSES = {"DO_NOT_SUBMIT", "NEEDS_MORE_PROOF"}

_RENDERERS = {
    "immunefi": immunefi.render_body,
    "code4rena": code4rena.render_body,
}


class RenderError(Exception):
    """Input / validation error (exit 1)."""


# --------------------------------------------------------------------------- #
# gate access (required)                                                       #
# --------------------------------------------------------------------------- #

def _run_gate(candidate: dict) -> dict:
    if str(_GATES_DIR) not in sys.path:
        sys.path.insert(0, str(_GATES_DIR))
    import submission_gate  # noqa: E402  (submission gate, not the pipeline)
    return submission_gate.evaluate_candidate(candidate)


def _load_gate_result(path: str | Path) -> dict:
    """Load a gate-result file. Accepts either a single gate report or the
    submission_gate --json-out envelope {"candidates": [...]}, taking the first."""
    data = json.loads(Path(path).read_text())
    if isinstance(data, dict) and "candidates" in data:
        cands = data.get("candidates") or []
        if not cands:
            raise RenderError("gate-result file has no candidates")
        return cands[0]
    if isinstance(data, dict) and "recommended_status" in data:
        return data
    raise RenderError("gate-result file is not a recognised gate report")


def resolve_gate_report(candidate: dict, *, gate_result_path: str | None,
                        run_gate: bool) -> dict:
    """Obtain a gate report; a gate result is mandatory.

    candidate -> draft without gate validation is refused here."""
    if gate_result_path and run_gate:
        raise RenderError("use either --gate-result or --run-gate, not both")
    if gate_result_path:
        return _load_gate_result(gate_result_path)
    if run_gate:
        return _run_gate(candidate)
    raise RenderError(
        "a gate result is required: pass --run-gate or --gate-result. "
        "Rendering a candidate that has not been validated by the gate is not allowed."
    )


# --------------------------------------------------------------------------- #
# watermark + emit                                                             #
# --------------------------------------------------------------------------- #

def watermark_block(gate_report: dict) -> str:
    """The mandatory 'DRAFT ONLY — NOT SUBMITTED' header for every draft."""
    status = gate_report.get("recommended_status", "")
    lines = [
        "> **DRAFT ONLY — NOT SUBMITTED**",
        ">",
        f"> Gate status: {status}",
        "> Human approval required: true",
    ]
    if status == "READY_FOR_HUMAN_REVIEW":
        lines.append("> This is a REVIEW DRAFT — warnings are present and must be resolved by a human.")
        warnings = gate_report.get("warnings", [])
        if warnings:
            lines.append(">")
            lines.append("> Warnings:")
            for w in warnings:
                lines.append(f"> - {w}")
    elif status == "READY_TO_SUBMIT_AFTER_APPROVAL":
        lines.append("> Final manual review still required before submission.")
    lines.append(">")
    lines.append("> Remove this block (and the Human Review Checklist, if present) before submitting.")
    return "\n".join(lines)


def emit_draft(candidate: dict, gate_report: dict, platform: str):
    """Return (ok, text_or_reason).

    ok=False (with a human-readable reason) when the gate status is blocking —
    no rendering happens in that case. ok=True returns the full draft markdown.
    """
    if platform not in _RENDERERS:
        raise RenderError(f"unknown platform {platform!r}; choose from {sorted(_RENDERERS)}")

    status = gate_report.get("recommended_status")
    if status not in ALLOWED_STATUSES:
        reason = (
            f"refused to render a {platform} draft: gate status {status!r} is blocking. "
            "Drafts are only produced for READY_FOR_HUMAN_REVIEW or "
            "READY_TO_SUBMIT_AFTER_APPROVAL."
        )
        return False, reason

    body = _RENDERERS[platform](candidate, gate_report)
    title = (candidate.get("title") or "").strip() or "Untitled finding"
    draft = (
        watermark_block(gate_report)
        + f"\n\n# {title}\n\n"
        + body
    )
    return True, draft


# --------------------------------------------------------------------------- #
# CLI                                                                          #
# --------------------------------------------------------------------------- #

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Render a gated platform draft (Immunefi/Code4rena) from a "
                    "validated candidate. Drafts only — never submits.",
    )
    ap.add_argument("--candidate", required=True, help="submission_candidate.json")
    ap.add_argument("--platform", required=True, choices=sorted(_RENDERERS))
    ap.add_argument("--gate-result", dest="gate_result",
                    help="path to a gate-result JSON (alternative to --run-gate)")
    ap.add_argument("--run-gate", action="store_true",
                    help="run the submission gate in-process to validate the candidate")
    ap.add_argument("--out", help="write the draft markdown here (else stdout)")
    ap.add_argument("--clean-out", dest="clean_out",
                    help="also write a clean copy (watermark + Human Review Checklist removed) "
                         "to this separate path. Requires --out; the draft is left untouched.")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    if args.clean_out and not args.out:
        print("[renderer] --clean-out requires --out (the watermarked draft must be written "
              "and preserved first)", file=sys.stderr)
        return 1
    if args.clean_out and args.out and Path(args.clean_out).resolve() == Path(args.out).resolve():
        print("[renderer] --clean-out must differ from --out", file=sys.stderr)
        return 1

    try:
        candidate = json.loads(Path(args.candidate).read_text())
        gate_report = resolve_gate_report(
            candidate, gate_result_path=args.gate_result, run_gate=args.run_gate,
        )
    except (OSError, json.JSONDecodeError) as e:
        print(f"[renderer] input error: {e}", file=sys.stderr)
        return 1
    except RenderError as e:
        print(f"[renderer] {e}", file=sys.stderr)
        return 1

    try:
        ok, payload = emit_draft(candidate, gate_report, args.platform)
    except RenderError as e:
        print(f"[renderer] {e}", file=sys.stderr)
        return 1

    if not ok:
        # blocking gate status -> refuse, write nothing.
        print(f"[renderer] {payload}", file=sys.stderr)
        return 3

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(payload)
        if not args.quiet:
            print(f"[renderer] wrote {args.platform} DRAFT to {args.out} "
                  f"(gate status: {gate_report.get('recommended_status')}). "
                  "No submission was performed; human approval is required.")
        # Optional convenience clean copy — produced only from this allowed draft,
        # written to a separate path, original left untouched. Lazy import to
        # avoid any import cycle (clean imports status sets from this module).
        if args.clean_out:
            from . import clean  # noqa: E402
            cok, cpayload = clean.clean_markdown(payload)
            if not cok:
                print(f"[renderer] clean copy NOT written: {cpayload}", file=sys.stderr)
            else:
                Path(args.clean_out).parent.mkdir(parents=True, exist_ok=True)
                Path(args.clean_out).write_text(cpayload)
                if not args.quiet:
                    print(f"[renderer] wrote clean copy to {args.clean_out} "
                          "(convenience output, not proof of readiness).")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
