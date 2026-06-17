#!/usr/bin/env python3
"""
link_findings_to_manifest.py — Best-effort link findings to coverage-manifest items (no LLM).

For every finding in output/merged_findings.json (falling back to output/findings_*.json), match it
to manifest item(s) by file + function name (+ line-span containment when available). Writes
`manifest_refs` back onto each finding (in merged_findings.json) and flips each matched manifest
item's disposition to `finding` with the finding id in finding_refs (via update_coverage_disposition
semantics). Findings that match nothing get a compatibility warning — never deleted.

Usage:
    python scripts/link_findings_to_manifest.py [--quiet]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
import update_coverage_disposition as ucd  # noqa: E402


def _norm_file(f: str) -> str:
    return (f or "").split("/")[-1].lower()


def _load_findings() -> tuple[list[dict], Path | None]:
    merged = audit_path("output") / "merged_findings.json"
    if merged.exists():
        try:
            data = json.loads(merged.read_text())
            return data.get("findings", []), merged
        except (json.JSONDecodeError, OSError):
            pass
    # fallback: union of findings_*.json
    out: list[dict] = []
    for p in sorted((audit_path("output")).glob("findings_*.json")):
        try:
            d = json.loads(p.read_text())
            out.extend(d.get("findings", []))
        except (json.JSONDecodeError, OSError):
            continue
    return out, None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    man_path = audit_path("output") / "coverage_manifest.json"
    if not man_path.exists():
        raise SystemExit("[link_findings_to_manifest] coverage_manifest.json missing — build it first.")
    items = json.loads(man_path.read_text()).get("items", [])
    # index manifest functions by (file_basename, name_lower)
    by_fn: dict[tuple, list[dict]] = {}
    for it in items:
        if it["kind"] in ("function", "initializer", "constructor"):
            by_fn.setdefault((_norm_file(it["file"]), it["name"].lower()), []).append(it)

    findings, merged_path = _load_findings()
    disp_path = audit_path("output") / "coverage_dispositions.json"
    have_disp = disp_path.exists()

    linked = 0
    unmatched: list[str] = []
    for f in findings:
        fid = f.get("id") or f.get("finding_id")
        loc = f.get("location", {}) or {}
        fil = _norm_file(loc.get("file", ""))
        func_field = (loc.get("function", "") or "")
        # a finding may name multiple functions; split on common separators
        fnames = [x.strip().lower() for x in func_field.replace("/", ",").replace(";", ",").split(",") if x.strip()]
        ls = loc.get("line_start")
        le = loc.get("line_end") or ls
        refs: list[str] = []
        for fn in fnames or [""]:
            cands = by_fn.get((fil, fn), [])
            if not cands:
                continue
            # A matching (file, function) is ALWAYS linked — never dropped on line drift (findings'
            # line_start often points at the NatSpec block above the function keyword). Line span is
            # only a DISAMBIGUATOR when several same-(file,name) items exist: pick the best overlap.
            if len(cands) == 1 or not ls:
                refs.extend(c["id"] for c in cands)
            else:
                def _overlap(c):
                    s = c.get("source_span", {}) or {}
                    a, b = s.get("start_line"), s.get("end_line")
                    if not a:
                        return -1
                    b = b or a
                    return min(le or ls, b) - max(ls, a)  # >=0 ⇒ overlap; higher is better
                best = max(cands, key=_overlap)
                # if nothing overlaps, fall back to the nearest-by-start item (still link one)
                refs.append(best["id"])
        refs = sorted(set(refs))
        if refs:
            f["manifest_refs"] = sorted(set(f.get("manifest_refs", []) + refs))
            linked += 1
            if have_disp and fid:
                # flip matched items to finding
                try:
                    p, data, idx = ucd._load()
                    changed = False
                    for mid in refs:
                        if mid in idx:
                            errs = ucd.apply_update(idx[mid], "finding", finding_ref=[fid],
                                                    assigned_pass="link", assigned_agent="link_findings")
                            if not errs:
                                changed = True
                    if changed:
                        p.write_text(json.dumps(data, indent=2))
                except SystemExit:
                    have_disp = False
        elif fid:
            unmatched.append(fid)

    if merged_path is not None:
        data = json.loads(merged_path.read_text())
        data["findings"] = findings
        merged_path.write_text(json.dumps(data, indent=2))

    if not args.quiet:
        print(f"[ok] linked {linked} findings to manifest items"
              + (f"; {len(unmatched)} unmatched (manifest_refs left empty): {', '.join(unmatched[:12])}"
                 if unmatched else ""))
        if unmatched:
            print("     [warn] unmatched findings have no manifest_refs — finding_requires_manifest_refs "
                  "will flag them at the gate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
