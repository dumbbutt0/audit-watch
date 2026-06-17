#!/usr/bin/env python3
"""
clean.py — strip internal-only blocks from a gated platform draft.

This is a ONE-WAY, NON-AUTHORITATIVE convenience helper. It takes a watermarked
platform draft (produced by platform_renderer) and writes a separate "clean" copy
with the internal blocks removed, ready for a human to copy/paste.

What it removes (and ONLY this):
  - the leading "DRAFT ONLY — NOT SUBMITTED" watermark blockquote (incl. the
    embedded warnings and the "remove before submitting" note)
  - the "## Human Review Checklist" section (Immunefi drafts)

What it never does:
  - rewrite report wording, fill missing fields, change severity, or drop
    caveats / limitations that are part of the vulnerability explanation
  - re-run the gate, call the pipeline, a browser, or any submission logic
  - erase or modify the original draft (the clean copy goes to a separate path)

Safety stance: the clean file is convenience output, NOT proof of readiness.
It is produced only from an already-allowed (non-blocking) watermarked draft;
human approval is still required before any submission.

Exit codes (CLI):
    0  clean copy written
    3  refused (no watermark / blocking gate status / already a clean copy)
    1  input error (unreadable file, --out == --draft)
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Reuse the gate-status vocabulary from the renderer (NOT the gate itself).
from .platform_renderer import ALLOWED_STATUSES, BLOCKING_STATUSES

WATERMARK_MARKER = "> **DRAFT ONLY — NOT SUBMITTED**"
CLEAN_PROVENANCE = (
    "<!-- Clean copy generated from a gated draft. Human approval still required. -->"
)
_CHECKLIST_HEADING = "## Human Review Checklist"
_GATE_STATUS_RE = re.compile(r"^>\s*Gate status:\s*(?P<status>\S+)\s*$", re.MULTILINE)


@dataclass
class CleanDraftResult:
    ok: bool
    reason: str = ""
    gate_status: str = ""


class CleanError(Exception):
    """Input error (exit 1)."""


def _parse_gate_status(markdown: str) -> str:
    m = _GATE_STATUS_RE.search(markdown)
    return m.group("status").strip() if m else ""


def validate_clean_draft(markdown: str) -> CleanDraftResult:
    """Decide whether a markdown draft may be cleaned.

    Refuses (ok=False) when the input is already a clean copy, is not a gated
    draft (no watermark), or carries a blocking / unknown gate status.
    """
    if CLEAN_PROVENANCE in markdown:
        return CleanDraftResult(False, "input is already a clean copy (no further transformation).")
    if WATERMARK_MARKER not in markdown:
        return CleanDraftResult(
            False,
            "input is not a gated draft: the 'DRAFT ONLY — NOT SUBMITTED' watermark is absent.",
        )
    status = _parse_gate_status(markdown)
    if not status:
        return CleanDraftResult(False, "could not read the gate status from the watermark.")
    if status in BLOCKING_STATUSES:
        return CleanDraftResult(
            False,
            f"refused to clean a draft with blocking gate status {status!r}.",
            gate_status=status,
        )
    if status not in ALLOWED_STATUSES:
        return CleanDraftResult(False, f"unknown gate status {status!r}.", gate_status=status)
    return CleanDraftResult(True, gate_status=status)


def _strip_watermark(lines: list[str]) -> list[str]:
    """Drop the leading contiguous '>' blockquote and a single trailing blank line."""
    i = 0
    n = len(lines)
    # the watermark is the leading run of blockquote lines
    while i < n and lines[i].lstrip().startswith(">"):
        i += 1
    # consume exactly one blank separator line if present
    if i < n and lines[i].strip() == "":
        i += 1
    return lines[i:]


def _strip_checklist(lines: list[str]) -> list[str]:
    """Remove the '## Human Review Checklist' section (heading through the line
    before the next '## ' heading or EOF). No-op if absent."""
    out: list[str] = []
    skipping = False
    for line in lines:
        if line.strip() == _CHECKLIST_HEADING:
            skipping = True
            continue
        if skipping:
            if line.startswith("## "):
                skipping = False
                out.append(line)
            # else: still inside the checklist section -> drop
            continue
        out.append(line)
    return out


def strip_draft_artifacts(markdown: str) -> str:
    """Remove the watermark and Human Review Checklist; prepend the provenance
    comment. Touches nothing else.

    Precondition: the input must be a watermarked draft. Raises ValueError
    otherwise so this cannot be misused to "clean" arbitrary text.
    """
    if WATERMARK_MARKER not in markdown:
        raise ValueError("strip_draft_artifacts requires a watermarked draft")

    lines = markdown.splitlines()
    lines = _strip_watermark(lines)
    lines = _strip_checklist(lines)

    body = "\n".join(lines).strip("\n")
    return f"{CLEAN_PROVENANCE}\n\n{body}\n"


def clean_markdown(markdown: str):
    """Validate then strip. Returns (ok, text_or_reason)."""
    result = validate_clean_draft(markdown)
    if not result.ok:
        return False, result.reason
    return True, strip_draft_artifacts(markdown)


# --------------------------------------------------------------------------- #
# CLI                                                                          #
# --------------------------------------------------------------------------- #

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Strip internal blocks (watermark + Human Review Checklist) from a "
                    "gated platform draft, writing a separate clean copy. Never submits.",
    )
    ap.add_argument("--draft", required=True, help="the watermarked platform draft markdown")
    ap.add_argument("--out", required=True, help="path for the clean copy (must differ from --draft)")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    draft_path = Path(args.draft)
    out_path = Path(args.out)
    try:
        if draft_path.resolve() == out_path.resolve():
            raise CleanError("--out must be a different path from --draft "
                             "(the original draft is never overwritten)")
        markdown = draft_path.read_text()
    except OSError as e:
        print(f"[clean] input error: {e}", file=sys.stderr)
        return 1
    except CleanError as e:
        print(f"[clean] {e}", file=sys.stderr)
        return 1

    ok, payload = clean_markdown(markdown)
    if not ok:
        print(f"[clean] refused: {payload}", file=sys.stderr)
        return 3

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(payload)
    if not args.quiet:
        print(f"[clean] wrote clean copy to {out_path} "
              "(original draft left untouched). Human approval is still required; "
              "no submission was performed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
