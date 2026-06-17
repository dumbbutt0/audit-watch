#!/usr/bin/env python3
"""
evidence_extractors.py — pure parsing helpers for the candidate author.

Rules of this module:
  - stdlib only; no network, no repository scanning, no hidden state.
  - extract ONLY what is explicitly present in the text passed in.
  - when something is absent, return "" / [] / None — never a guess.
  - no imports from the detection pipeline or the gates.

The functions here are intentionally conservative: a heading must be present for
a section to be extracted, and structured facts (PoC status, duplicate status,
defenses) are read only from explicit markers.
"""
from __future__ import annotations

import json
import re

# --- low level --------------------------------------------------------------


def read_text(path) -> str:
    """Read a UTF-8 text file. Caller decides whether the path was provided."""
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


# A markdown heading or a "Label:" line introduces a section.
_HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.*?)\s*#*\s*$")
_LABEL_RE = re.compile(r"^\s*\*{0,2}([A-Za-z][\w /&-]{1,40})\*{0,2}\s*:\s*(.*)$")


def _norm_heading(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def extract_section(md: str | None, aliases: list[str]) -> str:
    """Return the body text under the first heading/label matching any alias.

    Matches markdown headings (## Root Cause) and inline labels (Root Cause: ...).
    A heading section runs until the next heading of equal-or-higher level. An
    inline label captures the remainder of that line plus following indented or
    bullet lines until a blank line or the next label/heading.

    Returns "" when no matching heading/label is present (absent -> missing).
    """
    if not md:
        return ""
    wanted = {_norm_heading(a) for a in aliases}
    lines = md.splitlines()

    # 1) heading-style sections
    for i, line in enumerate(lines):
        hm = _HEADING_RE.match(line)
        if not hm:
            continue
        level = len(hm.group(1))
        title = _norm_heading(hm.group(2))
        # Exact match, or the heading starts with the alias followed by more words
        # (e.g. "root cause analysis" matches alias "root cause"). We deliberately
        # do NOT allow the reverse (a short heading matching a longer alias), which
        # would let "Impact" hijack "impact table".
        if title in wanted or any(title.startswith(w + " ") for w in wanted):
            body: list[str] = []
            for nxt in lines[i + 1:]:
                nh = _HEADING_RE.match(nxt)
                if nh and len(nh.group(1)) <= level:
                    break
                body.append(nxt)
            text = "\n".join(body).strip()
            if text:
                return text

    # 2) inline "Label: value" style
    for i, line in enumerate(lines):
        lm = _LABEL_RE.match(line)
        if not lm:
            continue
        label = _norm_heading(lm.group(1))
        if label in wanted or any(label == w for w in wanted):
            parts = [lm.group(2).strip()]
            for nxt in lines[i + 1:]:
                if not nxt.strip():
                    break
                if _LABEL_RE.match(nxt) or _HEADING_RE.match(nxt):
                    break
                parts.append(nxt.strip())
            text = "\n".join(p for p in parts if p).strip()
            return text  # may be "" if the label had no value -> still "absent-ish"

    return ""


def extract_list_section(md: str | None, aliases: list[str]) -> list[str]:
    """Extract a section and split it into list items.

    Splits on markdown bullets / numbered lines; if none, splits non-empty lines.
    Returns [] when the section is absent.
    """
    body = extract_section(md, aliases)
    if not body:
        return []
    items: list[str] = []
    for raw in body.splitlines():
        line = raw.strip()
        if not line:
            continue
        m = re.match(r"^(?:[-*+]\s+|\d+[.)]\s+)(.*)$", line)
        items.append(m.group(1).strip() if m else line)
    # drop any leftover heading-ish lines
    return [it for it in items if it]


# --- severity ---------------------------------------------------------------

def extract_severity(md: str | None) -> str:
    """Return the raw severity string as stated, or '' if not stated."""
    return extract_section(md, ["severity", "severity claim", "claimed severity"]).strip()


# --- program.json -----------------------------------------------------------

def extract_program(json_text: str | None) -> dict:
    """Parse a program.json describing the bounty program / scope rules.

    Recognised keys (all optional): program, platform, scope_reference,
    in_scope_impacts (list), privileged_in_scope (bool), in_scope_assets (list),
    out_of_scope (list). Returns {} on absent/invalid input.
    """
    if not json_text:
        return {}
    try:
        data = json.loads(json_text)
    except (json.JSONDecodeError, TypeError):
        return {}
    return data if isinstance(data, dict) else {}


# --- PoC log ----------------------------------------------------------------

_POC_PASS_RE = re.compile(
    r"(\b[1-9]\d*\s+passed\b|test result:\s*ok|\[PASS\]|\ball tests passed\b)",
    re.IGNORECASE,
)
# Only count a genuine failure: a NON-ZERO failed count, an explicit FAIL marker,
# a panic, or an assertion failure. "0 failed" must NOT register as failing.
_POC_FAIL_RE = re.compile(
    r"(\b[1-9]\d*\s+failed\b|test result:\s*FAILED|\[FAIL\]|\bpanicked\b|assertion failed)",
    re.IGNORECASE,
)
_POC_COMPILE_RE = re.compile(r"\b(compiling|compiled|compilation finished|solc)\b", re.IGNORECASE)
_POC_RUN_RE = re.compile(r"\b(forge test|hardhat test|running \d+ test|test result:|\[PASS\]|\[FAIL\])\b",
                         re.IGNORECASE)


def extract_poc(log_text: str | None) -> dict:
    """Classify a PoC log into {status, is_run, has_trace}.

    status: 'passing' | 'failing' | 'compiling' | 'none'
    is_run: whether the log shows a test actually executing (forge/hardhat)
    has_trace: whether there is any trace/log content at all

    Absent log -> {status: 'none', is_run: False, has_trace: False}. Never
    fabricates a pass.
    """
    if not log_text or not log_text.strip():
        return {"status": "none", "is_run": False, "has_trace": False}
    is_run = bool(_POC_RUN_RE.search(log_text))
    if _POC_FAIL_RE.search(log_text):
        status = "failing"
    elif _POC_PASS_RE.search(log_text):
        status = "passing"
    elif _POC_COMPILE_RE.search(log_text):
        status = "compiling"
    else:
        status = "none"
    return {"status": status, "is_run": is_run, "has_trace": bool(log_text.strip())}


# --- duplicate / known-issue search ----------------------------------------

def extract_duplicate_status(md: str | None) -> str:
    """Classify a duplicate-search note into the schema enum.

    'confirmed_duplicate' | 'possible_duplicate' | 'searched_clear' | 'not_searched'

    Absent file -> 'not_searched' (handled by the caller, which knows whether the
    file was provided). Given text, reads only explicit conclusions; a note that
    exists but states nothing conclusive stays 'not_searched'.
    """
    if md is None:
        return "not_searched"
    low = md.lower()
    if not low.strip():
        return "not_searched"
    # Precedence: confirmed > possible > clear. Patterns are deliberately strict
    # so that "no known duplicates" is NOT read as confirmed, and "possible
    # duplicate of an earlier issue" is NOT read as confirmed.
    if re.search(r"\bconfirmed duplicate\b|duplicate of\s+#\d|\bis a duplicate of\b|"
                 r"\bknown to be a duplicate\b", low):
        return "confirmed_duplicate"
    if re.search(r"\bpossible duplicate\b|\bpotential duplicate\b|possibly a duplicate|"
                 r"may be a duplicate|similar (finding|report|issue)|may overlap|"
                 r"overlaps with", low):
        return "possible_duplicate"
    if re.search(r"\bno (known )?duplicates?\b|no overlap|searched.*clear|not a duplicate|"
                 r"unique finding|no prior report", low):
        return "searched_clear"
    return "not_searched"


def extract_prior_reports(md: str | None) -> list[str]:
    """Pull explicit prior-report references from a duplicate-search note."""
    return extract_list_section(md, ["prior reports", "prior report", "known issues",
                                     "related reports", "overlapping reports"])


# --- defenses ---------------------------------------------------------------

def extract_defenses(md: str | None) -> list[dict]:
    """Parse defense notes into schema defense_analysis entries.

    Preferred structured form (per defense):

        ### Defense: nonReentrant modifier
        Blocks: yes
        Why it fails: withdraw() has no nonReentrant modifier (Vault.sol:142)

    Also accepts bullet lines of the form
        - <defense> | blocks: yes | why: <text>

    Any defense without an explicit rebuttal is recorded honestly:
      - blocks=yes + no rebuttal -> {blocks_path: true, why_it_fails: ""}  (gate FAILs)
      - no blocks/why info        -> {uncertain: true}                      (gate WARNs)

    Absent file -> [] (caller leaves defense_analysis empty -> gate NEEDS_PROOF).
    """
    if not md or not md.strip():
        return []

    entries: list[dict] = []

    # structured "### Defense:" blocks
    blocks = re.split(r"^\s{0,3}#{1,6}\s*defense\s*:?\s*", md, flags=re.IGNORECASE | re.MULTILINE)
    if len(blocks) > 1:
        for blk in blocks[1:]:
            lines = blk.splitlines()
            name = lines[0].strip() if lines else ""
            if not name:
                continue
            entry = _parse_defense_fields(name, "\n".join(lines[1:]))
            entries.append(entry)
        if entries:
            return entries

    # bullet form: "- name | blocks: yes | why: ..."
    for raw in md.splitlines():
        line = raw.strip()
        m = re.match(r"^(?:[-*+]\s+|\d+[.)]\s+)(.*)$", line)
        if not m:
            continue
        content = m.group(1)
        if "|" in content:
            name = content.split("|", 1)[0].strip()
            entry = _parse_defense_fields(name, content)
        else:
            # an unstructured defense bullet -> mark uncertain (honest unknown)
            name = content.strip()
            entry = {"defense": name, "blocks_path": False, "why_it_fails": "", "uncertain": True}
        if entry["defense"]:
            entries.append(entry)

    return entries


_BLOCKS_RE = re.compile(r"blocks?(?:_path)?\s*[:=]\s*(yes|true|no|false)", re.IGNORECASE)
_WHY_RE = re.compile(r"why(?:[ _]it[ _]fails)?\s*[:=]\s*(.+?)(?:\s*\|\s*|$)",
                     re.IGNORECASE | re.DOTALL)


def _parse_defense_fields(name: str, body: str) -> dict:
    blocks_path = False
    why = ""
    bm = _BLOCKS_RE.search(body)
    if bm:
        blocks_path = bm.group(1).lower() in ("yes", "true")
    wm = _WHY_RE.search(body)
    if wm:
        why = wm.group(1).strip()
    # honest unknown: no blocks info AND no rebuttal -> uncertain
    uncertain = (bm is None) and (not why)
    return {
        "defense": name.strip().rstrip(":"),
        "blocks_path": blocks_path,
        "why_it_fails": why,
        "uncertain": uncertain,
    }


# --- scope ------------------------------------------------------------------

def match_in_scope_asset(affected: list[str], scope_text: str | None,
                         program: dict) -> str:
    """Return the in-scope asset name IFF an affected contract is explicitly
    listed in the scope text or program.in_scope_assets. Otherwise "".

    This never claims in-scope on its own; it only confirms an explicit match.
    """
    candidates: list[str] = []
    if program:
        for a in program.get("in_scope_assets", []) or []:
            if isinstance(a, str):
                candidates.append(a)
    if scope_text:
        candidates.append(scope_text)

    haystack = "\n".join(candidates).lower()
    if not haystack.strip():
        return ""

    for contract in affected:
        base = contract.split("/")[-1].strip()
        if base and base.lower() in haystack:
            return base
    return ""
