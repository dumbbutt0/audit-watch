#!/usr/bin/env python3
"""build_submission_packages.py — materialize a real-world audit's PoC-proven / confirmed findings into
`reports/<dir>/submissions/<report-id>/` packages, NON-DESTRUCTIVELY, so findings are never stranded in the
gitignored `harness/` and every one is routed for human review + editing.

Selection mirrors sync_audit_to_ledger.py (single-sourced helpers) so the report tree and the dashboard never
disagree: a finding is packaged when it is PoC-proven (`poc.proved`) OR confidently confirmed
(`confirmation.score >= threshold`) AND testable (has a PoC plan). Folder name = meta.ledger_report_ids[id]
(e.g. "N-1"), else the finding id.

FILE OWNERSHIP (the non-destructive contract):
  * GENERATED, always refreshed (machine snapshot, clearly marked, never human-authored):
      - candidate_record.generated.json   (verbatim snapshot of output/candidates/<id>.json + resolved metadata)
  * CREATED ONLY IF MISSING, never overwritten (human owns these once they exist):
      - report.md, SUBMISSION.md, repro.md   (scaffolds opening with a loud NEEDS-REVIEW banner)
      - submission_candidate.json            (machine-derived scaffold; recommended_status NEEDS_HUMAN_REVIEW)
      - poc/<Name>.t.sol                     (copied from the gitignored harness test)
      - vulnerable/<File>.sol                (copied from the harness src for the affected file(s))
  * BUILDER-OWNED aggregate (regenerated, but only the status table — NOT the curated INDEX.md):
      - REVIEW_QUEUE.md                      (one "what still needs me" view: NEEDS REVIEW vs HUMAN-EDITED)

HONESTY RAILS (identical spirit to the ledger sync):
  * REAL-WORLD GATE: eval/blind audits are a no-op (the precision report tree is never polluted).
  * Nothing is marked submitted / submission-ready; scaffolds are banner-stamped NEEDS REVIEW.
  * poc_output.log is NEVER fabricated — if no captured run exists the package is flagged, not invented.
  * Human-authored prose is never overwritten; INDEX.md (curated) is never touched.

Usage: python scripts/build_submission_packages.py [--audit <id>] [--dry-run] [--quiet]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

# reuse the ledger sync's helpers so selection + naming stay single-sourced
import sync_audit_to_ledger as sal  # noqa: E402

SCAFFOLD_BANNER = "> ⚠ AUTO-SCAFFOLD — NEEDS HUMAN REVIEW & EDITING (not submission-ready)"


# ─────────────────────────────────────────────────────────────────────────────
# selection (mirrors sal.build's card bar: proven OR confirmed-and-testable)
# ─────────────────────────────────────────────────────────────────────────────
def _select(adir: Path) -> tuple[list[dict], list[dict]]:
    """Return (packaged, weak): packaged = proven + confirmed-testable cards; weak = real-but-below-bar (notes)."""
    cdir = adir / "output" / "candidates"
    thr = sal._conf_threshold()
    packaged, weak = [], []
    for cp in sorted(cdir.glob("*.json")) if cdir.is_dir() else []:
        c = sal._load(cp, {})
        if c.get("state") in ("duplicate", "rejected"):
            continue
        if (c.get("poc") or {}).get("proved"):
            packaged.append(c)
            continue
        score = (c.get("confirmation") or {}).get("score")
        if (c.get("state") in ("ready", "poc_required", "human_pending")
                and isinstance(score, (int, float)) and score >= thr and sal._poc_plan(c).strip()):
            packaged.append(c)
        else:
            weak.append(c)
    return packaged, weak


def _poc_rows(adir: Path) -> dict[str, dict]:
    p = adir / "data" / "runtime_poc" / "results.jsonl"
    rows: dict[str, dict] = {}
    if p.exists():
        for line in p.read_text().splitlines():
            line = line.strip()
            if line:
                try:
                    r = json.loads(line)
                    rows[r.get("finding_id")] = r
                except json.JSONDecodeError:
                    pass
    return rows


def _report_dir(adir: Path, meta: dict, poc_by_id: dict) -> Path | None:
    """Resolve reports/<dir>/ for this audit: meta.report_dir -> a proven poc test_file prefix -> reports/<id>."""
    rd = meta.get("report_dir")
    if rd:
        return ROOT / rd
    import re
    for r in poc_by_id.values():
        m = re.search(r"(reports/[^/]+)/", str(r.get("test_file") or ""))
        if m:
            return ROOT / m.group(1)
    cand = ROOT / "reports" / adir.name
    return cand if (cand / "submissions").exists() or (cand / "harness").exists() else None


def _rid(meta: dict, fid: str) -> str:
    return str((meta.get("ledger_report_ids") or {}).get(fid) or fid)


# ─────────────────────────────────────────────────────────────────────────────
# resolve the affected source files for the vulnerable/ copies
# ─────────────────────────────────────────────────────────────────────────────
def _vulnerable_srcs(c: dict, src_root: Path) -> list[Path]:
    import re
    names: list[str] = []
    loc = c.get("location") or {}
    for s in [loc.get("file") or ""] + [str(x) for x in (c.get("manifest_refs") or [])]:
        m = re.search(r"([A-Za-z0-9_]+\.sol)", s)
        if m:
            names.append(m.group(1))
    out, seen = [], set()
    for n in names:
        if n in seen:
            continue
        seen.add(n)
        hit = next(iter(src_root.rglob(n)), None) if src_root.is_dir() else None
        if hit:
            out.append(hit)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# scaffold writers (only used when the human file does not exist yet)
# ─────────────────────────────────────────────────────────────────────────────
def _scaffold_report_md(c: dict, rid: str) -> str:
    ev = c.get("evidence") or {}
    advisories = c.get("readiness_advisories") or []
    checklist = "\n".join(f"- [ ] {a}" for a in advisories) or "- [ ] confirm deployment reachability & novelty"
    return f"""# {rid} ({sal._sev(c)}) — {c.get('title','')}

{SCAFFOLD_BANNER}

This file was auto-scaffolded from the canonical candidate record so the finding is not stranded in the gitignored
harness. **Replace this scaffold with a human-authored standalone writeup before any submission** (mirror the format
of a finalized sibling package, e.g. `../N-1/report.md`).

- **Internal id:** `{c.get('id','')}`
- **Severity (system):** {sal._sev(c)}
- **Location:** `{(c.get('location') or {}).get('file','')}`

## Root cause / mechanism
{ev.get('impact') or c.get('description') or '(fill in)'}

## Exploit path
{sal._poc_plan(c) or '(fill in)'}

## Impact
- **Who loses:** {ev.get('who_loses') or '(fill in)'}
- **Who gains:** {ev.get('who_gains') or '(fill in)'}

## Suggested fix
{ev.get('suggested_fix') or '(fill in)'}

## Review checklist (from system advisories — clear before submitting)
{checklist}
"""


def _scaffold_repro_md(c: dict, rid: str, poc: dict) -> str:
    tc = poc.get("test_contract", "")
    cmd = f"forge test --match-contract {tc} -vv" if tc else "forge test --match-path 'test/PoC_*.t.sol' -vv"
    return f"""# Reproduce — {rid}

{SCAFFOLD_BANNER}

```bash
cd reports/<audit>/harness
{cmd}
```

PoC file: `poc/{Path(poc.get('test_file','')).name or '(copy from harness/test/)'}`. Capture the passing run into
`poc_output.log` (this builder never fabricates output). See `harness/SETUP.md` for toolchain setup. Nothing here is
submitted; human review + KYC + submission are the operator's responsibility.
"""


def _scaffold_submission_md(c: dict, rid: str) -> str:
    return f"""<!-- {SCAFFOLD_BANNER} — replace with a platform-paste-ready writeup before submitting. -->

# Field: Category
{c.get('vrt_category') or 'Business Logic Errors'}
<!-- MUST be a verbatim value from reports/SUBMISSION_CATEGORIES.md (HackenProof VRT). Pick the most specific. -->

# Field: Severity
{sal._sev(c)}

# Field: Title
{c.get('title','')}

# Field: Vulnerability details
{(c.get('evidence') or {}).get('impact') or c.get('description') or '(fill in)'}

# Field: Validation steps
(fill in — capture the passing PoC run; never paste fabricated output)
"""


def _scaffold_candidate_json(c: dict, rid: str, poc: dict) -> dict:
    ev = c.get("evidence") or {}
    return {
        "finding_id": rid,
        "internal_id": c.get("id", ""),
        "_auto_scaffold": True,
        "title": c.get("title", ""),
        "root_cause": ev.get("impact") or c.get("description") or "",
        "affected_contracts": [(c.get("location") or {}).get("file", "")],
        "severity_claim": sal._sev(c),
        "attacker_entrypoint": sal._poc_plan(c),
        "who_loses": ev.get("who_loses", ""),
        "who_gains": ev.get("who_gains", ""),
        "suggested_fix": ev.get("suggested_fix", ""),
        "proof_type": "runnable_poc" if (c.get("poc") or {}).get("proved") else "analysis_confirmed",
        "poc_path": poc.get("test_file", ""),
        "poc_status": "passing" if (c.get("poc") or {}).get("proved") else "not_started",
        "recommended_status": "NEEDS_HUMAN_REVIEW",
        "human_approval_required": True,
        "readiness_advisories": c.get("readiness_advisories") or [],
    }


def _generated_snapshot(c: dict, rid: str, poc: dict, vuln: list[str]) -> dict:
    return {
        "_generated": True,
        "_note": "machine snapshot of the canonical candidate record — safe to overwrite; do not hand-edit",
        "report_id": rid,
        "candidate": c,
        "poc": {"test_contract": poc.get("test_contract", ""), "test_file": poc.get("test_file", ""),
                "status": poc.get("status", "")},
        "vulnerable_files": vuln,
    }


# ─────────────────────────────────────────────────────────────────────────────
# write helpers (dirty-checked so a clean run touches nothing)
# ─────────────────────────────────────────────────────────────────────────────
def _write_if_changed(path: Path, content: str, planned: list, dry: bool) -> bool:
    if path.exists() and path.read_text() == content:
        return False
    planned.append(("write" if path.exists() else "create", str(path.relative_to(ROOT))))
    if not dry:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    return True


def _create_if_missing(path: Path, content: str, planned: list, dry: bool) -> bool:
    if path.exists():
        return False
    planned.append(("create", str(path.relative_to(ROOT))))
    if not dry:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    return True


def _copy_if_missing(src: Path, dst: Path, planned: list, dry: bool) -> bool:
    if dst.exists() or not src.exists():
        return False
    planned.append(("copy", str(dst.relative_to(ROOT))))
    if not dry:
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(src.read_text())
    return True


# ─────────────────────────────────────────────────────────────────────────────
# REVIEW_QUEUE.md — the single "what still needs me" view
# ─────────────────────────────────────────────────────────────────────────────
def _review_status(pkg: Path) -> str:
    rep = pkg / "report.md"
    if not rep.exists():
        return "NEEDS REVIEW (no report.md)"
    edited = SCAFFOLD_BANNER not in rep.read_text()
    log_ok = (pkg / "poc_output.log").exists()
    if not log_ok:
        return ("HUMAN-EDITED" if edited else "NEEDS REVIEW") + " · NEEDS POC LOG"
    return "HUMAN-EDITED" if edited else "NEEDS REVIEW"


def _review_queue_md(audit_id: str, sub_dir: Path, rids: list[str]) -> str:
    rows = []
    for rid in rids:
        pkg = sub_dir / rid
        rows.append(f"| {rid} | {_review_status(pkg)} | `{pkg.relative_to(ROOT)}/` |")
    body = "\n".join(rows) or "| _(none)_ | | |"
    return (f"# Submission review queue — {audit_id}\n\n"
            "Auto-generated by `scripts/build_submission_packages.py`. **HUMAN-EDITED** = the auto-scaffold banner "
            "was removed (prose finalized). **NEEDS REVIEW** = still a scaffold / advisories open. "
            "**NEEDS POC LOG** = capture a passing `poc_output.log` (never fabricated). Nothing is submitted "
            "automatically.\n\n"
            "| Report | Review status | Package |\n|---|---|---|\n" + body + "\n")


# ─────────────────────────────────────────────────────────────────────────────
def build(audit_id: str, dry: bool) -> tuple[dict, list[str]]:
    log: list[str] = []
    adir = ROOT / "audits" / audit_id
    meta = sal._load(adir / "meta.json", {})
    ok, why = sal._is_real_world(meta, audit_id)
    if not ok:
        return {"skipped": True, "reason": why, "planned": []}, [f"SKIP {audit_id}: {why}"]

    poc_by_id = _poc_rows(adir)
    rdir = _report_dir(adir, meta, poc_by_id)
    if rdir is None:
        return {"skipped": True, "reason": "no report dir resolved", "planned": []}, \
            [f"SKIP {audit_id}: could not resolve a reports/<dir> (set meta.report_dir)"]

    sub_dir = rdir / "submissions"
    src_root = rdir / "harness" / "src"
    test_root = rdir / "harness" / "test"
    packaged, weak = _select(adir)

    planned: list = []
    rids: list[str] = []
    for c in packaged:
        fid = c.get("id")
        rid = _rid(meta, fid)
        rids.append(rid)
        pkg = sub_dir / rid
        poc = poc_by_id.get(fid, {})

        # GENERATED snapshot — always refreshed (dirty-checked)
        vuln_srcs = _vulnerable_srcs(c, src_root)
        snap = _generated_snapshot(c, rid, poc, [s.name for s in vuln_srcs])
        _write_if_changed(pkg / "candidate_record.generated.json",
                          json.dumps(snap, indent=2) + "\n", planned, dry)

        # CREATE-IF-MISSING — copies from the gitignored harness
        tf = poc.get("test_file", "")
        tname = Path(tf).name if tf else f"PoC_{fid}.t.sol"
        src_test = (ROOT / tf) if tf else (test_root / tname)
        if not src_test.exists() and test_root.is_dir():
            src_test = next((p for p in test_root.glob("PoC_*.t.sol")
                             if poc.get("test_contract") and poc["test_contract"] in p.read_text()), src_test)
        _copy_if_missing(src_test, pkg / "poc" / tname, planned, dry)
        for s in vuln_srcs:
            _copy_if_missing(s, pkg / "vulnerable" / s.name, planned, dry)

        # CREATE-IF-MISSING — human-owned prose scaffolds (banner-stamped)
        _create_if_missing(pkg / "report.md", _scaffold_report_md(c, rid), planned, dry)
        _create_if_missing(pkg / "SUBMISSION.md", _scaffold_submission_md(c, rid), planned, dry)
        _create_if_missing(pkg / "repro.md", _scaffold_repro_md(c, rid, poc), planned, dry)
        _create_if_missing(pkg / "submission_candidate.json",
                           json.dumps(_scaffold_candidate_json(c, rid, poc), indent=2) + "\n", planned, dry)

    # BUILDER-OWNED aggregate — REVIEW_QUEUE.md (status table only; INDEX.md is curated, never touched)
    if sub_dir.exists() or rids:
        _write_if_changed(sub_dir / "REVIEW_QUEUE.md",
                          _review_queue_md(audit_id, sub_dir, sorted(rids)), planned, dry)

    log.append(f"{audit_id} -> {sub_dir.relative_to(ROOT)}: {len(packaged)} packaged "
               f"({len(rids)} report-ids), {len(weak)} below-bar (not packaged), "
               f"{len(planned)} file action(s){' [dry-run]' if dry else ''}")
    for kind, p in planned:
        log.append(f"  {kind}: {p}")
    return {"skipped": False, "planned": planned, "packaged": len(packaged),
            "report_dir": str(rdir.relative_to(ROOT))}, log


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    audit_id = args.audit or sal._active_audit_id()
    if not audit_id:
        print("[pkg-build] no audit id (pass --audit or set active audit)")
        return 0
    result, log = build(audit_id, args.dry_run)
    if not args.quiet:
        for ln in log:
            print(ln if ln.startswith(audit_id) else f"[pkg-build] {ln}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
