#!/usr/bin/env python3
"""Recall Lab — looping protocol over all past contests.

A resumable driver that walks EVERY past contest with a cold pass + an answer key, runs the recall-lab
methodology on each (adjudicate -> stage reasoning-gap reincorporation candidates -> author prompt sections ->
regression-guard), one contest per iteration, and — once the on-disk backlog is drained — surfaces fresh past
contests to ingest. Designed to be driven by an autonomous /loop: a fresh-context fire reads evals/loop_state.json
and continues from the cursor.

The driver is DETERMINISTIC scaffolding. The judgment steps (confirming each heuristic miss against the awarded
text, authoring the agents/<specialist>.md section, adding the regression test) are done in-session via the
/recall-lab skill. `next` mines + emits the iteration packet but does NOT advance the cursor; `done` advances it
only after the regression guard is green.

  python scripts/recall_lab_loop.py build              # (re)build/refresh the work queue (idempotent)
  python scripts/recall_lab_loop.py status             # queue + cursor + progress
  python scripts/recall_lab_loop.py next               # mine the next contest + emit the iteration packet
  python scripts/recall_lab_loop.py done <id> [--sections "logic.md#17,dos.md#11"] [--classes "a,b"]
  python scripts/recall_lab_loop.py enqueue-ingest     # when on-disk backlog drained: print the ingest protocol

Eval-only. Never touches the real-world dashboard. Reincorporation candidates stay STAGED in
data/learning/_proposed/ (human-authored sections; pinned rejection_rules.jsonl never auto-mutated).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
AUDITS = ROOT / "audits"
CORPUS = ROOT / "evals" / "corpus.json"
MECH = ROOT / "config" / "mechanism_classes.json"
STATE = ROOT / "evals" / "loop_state.json"
SCOREBOARD = ROOT / "evals" / "scoreboard.json"

STATUS_PENDING, STATUS_MINED, STATUS_DONE = "pending", "mined", "reincorporated"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _has_key(adir: Path) -> bool:
    return ((adir / "_sealed_answer_key" / "report.md").exists()
            or (adir / "output" / "eval_ready" / "answer_key_normalization.json").exists()
            or (adir / "data" / "evaluation" / "ground_truth.jsonl").exists())


def _set_of(aid: str) -> str:
    """Which corpus partition a contest belongs to (training / holdout / pending_key / uncatalogued)."""
    if CORPUS.exists():
        c = json.loads(CORPUS.read_text())
        for set_name in ("training", "holdout"):
            if any(r["id"] == aid for r in c["sets"].get(set_name, [])):
                return set_name
        # pending_key lives at the top level of corpus.json
        if any(r["id"] == aid for r in c.get("pending_key", [])):
            return "pending_key"
    return "uncatalogued"


def _adj_doc(aid: str) -> dict | None:
    p = AUDITS / aid / "output" / "eval_ready" / "adjudication.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


def _adj_summary(aid: str) -> dict | None:
    doc = _adj_doc(aid)
    return doc.get("summary") if doc else None


def _reasoning_misses(aid: str) -> int | None:
    """MISSED rows whose locus file WAS read (read_file=True) — the prompt-addressable misses. None if no
    adjudication yet. (Coverage-gap misses, read_file=False, are a sweep fix, not a prompt fix.)"""
    doc = _adj_doc(aid)
    if not doc:
        return None
    return sum(1 for r in doc.get("awarded", [])
               if r.get("label") == "MISSED" and r.get("read_file") is True)


def _discover_on_disk() -> list[str]:
    """Every audit dir with a cold pass (merged_findings.json) AND an answer key in any format."""
    out = []
    for d in sorted(AUDITS.glob("*/")):
        aid = d.name
        if aid.startswith("_"):
            continue
        if (d / "output" / "merged_findings.json").exists() and _has_key(d):
            out.append(aid)
    return out


def _load_state() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"version": 1, "cursor": 0, "updated_at": _now(), "stats": {}, "queue": []}


def _recompute_stats(state: dict) -> None:
    q = state["queue"]
    by = {STATUS_PENDING: 0, STATUS_MINED: 0, STATUS_DONE: 0}
    misses = 0
    for e in q:
        by[e["status"]] = by.get(e["status"], 0) + 1
        misses += e.get("misses") or 0
    state["stats"] = {
        "contests_total": len(q),
        "pending": by[STATUS_PENDING],
        "mined": by[STATUS_MINED],
        "reincorporated": by[STATUS_DONE],
        "misses_total": misses,
    }


def _save(state: dict) -> None:
    state["updated_at"] = _now()
    _recompute_stats(state)
    STATE.write_text(json.dumps(state, indent=2) + "\n")


def _order_key(e: dict):
    # Highest LEVERAGE first: prompt-addressable reasoning-gap misses dominate (coverage-gap misses are a
    # sweep fix, not a prompt fix); total misses is the tiebreak. Unknown (un-mined, None) ordered last.
    r = e.get("reasoning_misses")
    m = e.get("misses")
    return (0 if (r is None and m is None) else 1, -(r or 0), -(m or 0), e["id"])


def build() -> int:
    state = _load_state()
    existing = {e["id"]: e for e in state["queue"]}
    for aid in _discover_on_disk():
        summ = _adj_summary(aid)
        misses = summ.get("misses_detected") if summ else None
        awarded = summ.get("awarded_total") if summ else None
        reasoning = _reasoning_misses(aid)
        if aid in existing:
            e = existing[aid]
            # refresh measured fields; PRESERVE workflow status + authored work (idempotent).
            if misses is not None:
                e["misses"] = misses
            if awarded is not None:
                e["awarded"] = awarded
            if reasoning is not None:
                e["reasoning_misses"] = reasoning
        else:
            existing[aid] = {
                "id": aid, "source": "on_disk", "set": _set_of(aid), "status": STATUS_PENDING,
                "misses": misses, "reasoning_misses": reasoning, "awarded": awarded,
                "sections_authored": [], "mechanism_classes": [],
            }
    # keep reincorporated entries pinned at the front (done), the rest ordered by leverage.
    done = [e for e in existing.values() if e["status"] == STATUS_DONE]
    rest = [e for e in existing.values() if e["status"] != STATUS_DONE]
    rest.sort(key=_order_key)
    state["queue"] = done + rest
    state["cursor"] = len(done)
    _save(state)
    print(f"queue: {len(state['queue'])} contests "
          f"({state['stats']['reincorporated']} done / {state['stats']['mined']} mined / "
          f"{state['stats']['pending']} pending), {state['stats']['misses_total']} misses known. -> "
          f"{STATE.relative_to(ROOT)}")
    return 0


def _first_active(state: dict) -> int | None:
    for i, e in enumerate(state["queue"]):
        if e["status"] in (STATUS_PENDING, STATUS_MINED):
            return i
    return None


def _mech_meta() -> dict:
    return json.loads(MECH.read_text()).get("classes", {}) if MECH.exists() else {}


def _print_packet(aid: str) -> None:
    """Emit the iteration packet from the contest's adjudication.json: the reasoning-gap misses grouped by
    mechanism class with the target agent/section. The HEURISTIC OVER-REPORTS — confirm each against the
    awarded text before authoring."""
    p = AUDITS / aid / "output" / "eval_ready" / "adjudication.json"
    doc = json.loads(p.read_text())
    mech = _mech_meta()
    misses = [r for r in doc.get("awarded", []) if r.get("label") == "MISSED"]
    reasoning = [r for r in misses if r.get("read_file") is True]
    coverage = [r for r in misses if r.get("read_file") is not True]
    summ = doc.get("summary", {})
    print("\n" + "=" * 78)
    print(f"ITERATION PACKET — {aid}   ({doc.get('set','?')}; key={summ.get('awarded_source')})")
    print(f"  awarded={summ.get('awarded_total')}  heuristic_recall={summ.get('recall_of_surfaced')}  "
          f"misses_detected={summ.get('misses_detected')}")
    print(f"  reasoning-gap (file READ -> author a prompt §): {len(reasoning)}")
    print(f"  coverage-gap  (file UNREAD -> fix sweep): {len(coverage)}")
    print("-" * 78)
    print("  HEURISTIC over-reports MISSED. CONFIRM each below against the AWARDED TEXT + your cold")
    print("  candidates before authoring. The heuristic only PRIORITIZES; it is not ground truth.")
    print("-" * 78)
    for r in reasoning:
        cls = r.get("mechanism_class")
        meta = mech.get(cls, {}) if cls else {}
        tgt = (f"agents/{meta.get('agent')}.md {meta.get('prompt_section')}"
               if meta.get("agent") else "agents/<specialist>.md §N  (assign a mechanism_class)")
        print(f"  [{r.get('severity','?'):>8}] {r['id']}  {r.get('title','')[:62]}")
        print(f"            class={cls or '(unassigned)'}  ->  {tgt}")
    if coverage:
        print("  coverage-gap misses (fix the mandatory sweep / context-pack, not a prompt §):")
        for r in coverage:
            print(f"     - {r['id']}  {r.get('title','')[:60]}")
    print("=" * 78)
    print("NEXT (in-session): confirm -> author agents/*.md §N + tests/ regression test -> "
          "`./run_pipeline.sh eval-regression` (must be GREEN) -> "
          f"`./run_pipeline.sh eval-loop done {aid} --sections ... --classes ...`")


def nxt() -> int:
    state = _load_state()
    if not state["queue"]:
        print("empty queue — run `eval-loop build` first.", file=sys.stderr)
        return 2
    i = _first_active(state)
    if i is None:
        print("on-disk backlog DRAINED (all reincorporated). Run `eval-loop enqueue-ingest` to add fresh "
              "past contests.")
        return 0
    e = state["queue"][i]
    state["cursor"] = i
    aid = e["id"]
    if e["status"] == STATUS_PENDING:
        # AUTO-ENFORCED full coverage: never mine/reveal a thin SCOPED ingested cold pass (override loud+stamped).
        if require_full_coverage(aid) != 0:
            return 1
        print(f"mining {aid} ...")
        # 1. adjudicate (heuristic, advisory) — detect misses in any answer-key format.
        r = subprocess.run([PY, str(ROOT / "scripts" / "adjudicate.py"), aid, "--auto"],
                           cwd=ROOT)
        if r.returncode != 0:
            print(f"adjudicate failed for {aid} (rc={r.returncode}); leaving status=pending.", file=sys.stderr)
            return 1
        # 2. stage reasoning-gap reincorporation candidates -> data/learning/_proposed/recall_sections.jsonl
        subprocess.run([PY, str(ROOT / "scripts" / "derive_learning.py"),
                        "--from-adjudication", aid], cwd=ROOT)
        summ = _adj_summary(aid) or {}
        e["misses"] = summ.get("misses_detected")
        e["awarded"] = summ.get("awarded_total")
        e["reasoning_misses"] = _reasoning_misses(aid)
        e["status"] = STATUS_MINED
        _save(state)
    else:
        print(f"{aid} already mined — re-emitting packet (cursor resumed).")
    _print_packet(aid)
    return 0


def done(aid: str, sections: list[str], classes: list[str]) -> int:
    state = _load_state()
    match = [e for e in state["queue"] if e["id"] == aid]
    if not match:
        print(f"{aid} not in queue — run `eval-loop build`/`next` first.", file=sys.stderr)
        return 2
    e = match[0]
    if e["status"] != STATUS_MINED:
        print(f"{aid} status is '{e['status']}', expected '{STATUS_MINED}' (run `eval-loop next` first).",
              file=sys.stderr)
        return 2
    # AUTO-ENFORCED full coverage: never bank a thin SCOPED ingested pass (override loud+stamped).
    if require_full_coverage(aid) != 0:
        print(f"\nREFUSED: {aid} cold-pass coverage incomplete — bank blocked (finish coverage or set "
              f"AUDITWATCH_COVERAGE_OVERRIDE=1).", file=sys.stderr)
        return 1
    # Regression guard MUST be green to bank an iteration (no training catch dropped by the prompt edit).
    rc = subprocess.run([PY, str(ROOT / "scripts" / "recall_regression_gate.py")], cwd=ROOT).returncode
    if rc != 0:
        print(f"\nREFUSED: eval-regression is RED (rc={rc}). Fix the regression before banking {aid}.",
              file=sys.stderr)
        return 1
    if sections:
        e["sections_authored"] = sorted(set(e.get("sections_authored", []) + sections))
    if classes:
        e["mechanism_classes"] = sorted(set(e.get("mechanism_classes", []) + classes))
    e["status"] = STATUS_DONE
    e["reincorporated_at"] = _now()
    # re-pin done entries to the front so the cursor reflects true progress.
    d = [x for x in state["queue"] if x["status"] == STATUS_DONE]
    rest = [x for x in state["queue"] if x["status"] != STATUS_DONE]
    rest.sort(key=_order_key)
    state["queue"] = d + rest
    state["cursor"] = len(d)
    _save(state)
    print(f"banked {aid}: sections={e['sections_authored']} classes={e['mechanism_classes']}")
    print(f"progress: {state['stats']['reincorporated']}/{state['stats']['contests_total']} reincorporated, "
          f"{state['stats']['pending']} pending. Next: `eval-loop next`.")
    return 0


def status() -> int:
    state = _load_state()
    if not state["queue"]:
        print("empty queue — run `eval-loop build`.")
        return 0
    s = state["stats"]
    print(f"Recall Lab loop — {s['reincorporated']}/{s['contests_total']} reincorporated "
          f"({s['mined']} mined, {s['pending']} pending), {s['misses_total']} misses known. "
          f"cursor={state['cursor']}  updated={state['updated_at']}")
    print(f"{'#':>3} {'status':<14} {'reason':>6} {'total':>6} {'awarded':>7}  {'set':<12} id")
    for i, e in enumerate(state["queue"]):
        mark = "->" if i == state["cursor"] else "  "
        rg = e.get("reasoning_misses")
        print(f"{mark}{i:>2} {e['status']:<14} {('?' if rg is None else rg):>6} "
              f"{str(e.get('misses') if e.get('misses') is not None else '?'):>6} "
              f"{str(e.get('awarded') or '?'):>7}  {e.get('set','?'):<12} {e['id']}")
    if SCOREBOARD.exists():
        try:
            sb = json.loads(SCOREBOARD.read_text())
            classes = sb.get("by_mechanism_class", {})
            untested = sb.get("untested_mechanism_classes", [])
            print(f"\nmechanism-class coverage: {len(classes)} measured, {len(untested)} untested.")
        except Exception:
            pass
    return 0


_INGEST_NOTE = """\
On-disk backlog DRAINED. To extend the loop with fresh past contests (genuine holdout recall):

  1. PICK a past contest with a PUBLIC awarded report not yet on disk. Sources:
       - Sherlock:  https://audits.sherlock.xyz/api/contests   (the `report` field carries the full awarded set)
       - Code4rena: https://code4rena.com/reports/<slug>       (must be PUBLIC, not sponsor-private)
     Prefer post-cutoff (genuinely blind) for honest headline recall; pre-cutoff is regression-only.
  2. FETCH the verified source (curl the repo at the audited commit) into a temp dir, and save the awarded
     report to a .md file. (Source fetch is operator-driven — it varies per contest.)
  3. INGEST (seals the report; do NOT read it before the cold pass; record the scope denominator):
       python scripts/ingest_contest.py --id <slug>-blind --name "<name>" --platform <code4rena|sherlock> \\
           --report /tmp/<slug>-report.md --source /path/to/src --scope-json /tmp/<contest-detail>.json \\
           --set holdout --scoreable
  4. BLIND COLD PASS via /ite-audit — FULL COVERAGE (not thin): examine EVERY in-scope substantive file, log each
     in merged_findings._coverage[]. GATE: `eval-loop cold-coverage <slug>-blind` MUST be green before reveal
     (a thin pass manufactures phantom coverage-gap misses and hides reasoning gaps — see the Cap experiment).
  5. reveal + `eval-adjudicate` -> reincorporate -> `eval-loop build` re-discovers it -> `eval-loop next`/done.
"""


def enqueue_ingest() -> int:
    state = _load_state()
    if _first_active(state) is not None:
        print("on-disk backlog NOT drained yet — keep running `eval-loop next` first.")
        return 0
    print(_INGEST_NOTE)
    return 0


# --- Full-coverage gate for ingested cold passes -----------------------------------------------------------
# The full-coverage experiment (Cap) proved thin cold passes manufacture phantom "coverage-gap" misses and hide
# the real reasoning gaps. This gate BLOCKS reveal/adjudication of an ingested contest until its blind cold pass
# has examined every in-scope SUBSTANTIVE file (recorded in merged_findings._coverage[]). Breadth is mandatory;
# depth is prioritized (a low-value file may be examined at depth:"survey"). Boilerplate (interfaces/, storage
# slot-utils) is reported but does not block.
_BOILERPLATE = ("interfaces/", "/interfaces/")


def _is_boilerplate(rel: str) -> bool:
    r = "/" + rel
    # Solidity boilerplate: interfaces + storage slot-util accessors.
    if rel.startswith("interfaces/") or "/interfaces/" in r:
        return True
    if (rel.startswith("storage/") or "/storage/" in r) and rel.endswith("StorageUtils.sol"):
        return True
    # Rust/Solana boilerplate: tests, build scripts, generated, and pure re-export entrypoints.
    if rel.endswith(".rs"):
        if "/tests/" in r or rel.endswith("_test.rs") or rel.endswith("build.rs"):
            return True
        if rel.endswith("/error.rs") or rel.endswith("errors.rs") or rel.endswith("/constants.rs"):
            return True
    return False


def _in_scope_files(adir: Path) -> list[str] | None:
    """In-scope .sol files (contracts-relative). Prefer scope.json (the audit's recorded scope); else fall back
    to globbing the source tree minus interfaces/mocks/test/script/deploy."""
    sp = adir / "scope.json"
    if sp.exists():
        try:
            return [f["file"] for f in json.loads(sp.read_text()).get("in_scope_files", [])]
        except Exception:
            pass
    src = adir / "contracts" / "_sources"
    if not src.exists():
        return None
    out = []
    # cross-language: enumerate Solidity AND Rust sources (scope.json is the primary, language-agnostic path;
    # this fallback covers either tree).
    for ext in ("*.sol", "*.rs"):
        for p in src.rglob(ext):
            low = str(p).lower()
            if any(seg in low for seg in ("/mock", "/test", "/script", "/deploy", "/testnetcampaign", "/target/")):
                continue
            # contracts-relative: strip everything up to and including the last 'contracts/'
            parts = p.as_posix().split("/contracts/")
            out.append(parts[-1] if len(parts) > 1 else p.name)
    return sorted(set(out))


def cold_coverage(aid: str, block: bool = True) -> int:
    """Report (and optionally enforce) full coverage of an ingested contest's blind cold pass. Exit 1 if any
    SUBSTANTIVE in-scope file was not examined in merged_findings._coverage[]."""
    adir = AUDITS / aid
    scope = _in_scope_files(adir)
    if scope is None:
        print(f"{aid}: no scope.json and no source tree — cannot compute coverage.", file=sys.stderr)
        return 2
    mf = adir / "output" / "merged_findings.json"
    if not mf.exists():
        print(f"{aid}: no cold pass (merged_findings.json) yet.", file=sys.stderr)
        return 2
    cov = json.loads(mf.read_text()).get("_coverage", [])
    examined = {c.get("file", "") for c in cov}
    examined_base = {Path(f).name for f in examined}

    def _covered(rel: str) -> bool:
        return rel in examined or Path(rel).name in examined_base or any(rel.endswith(e) or e.endswith(rel) for e in examined)

    subst = [f for f in scope if not _is_boilerplate(f)]
    boiler = [f for f in scope if _is_boilerplate(f)]
    missing_subst = [f for f in subst if not _covered(f)]
    missing_boiler = [f for f in boiler if not _covered(f)]
    pct = round(100 * (len(subst) - len(missing_subst)) / max(len(subst), 1))
    print(f"{aid} cold-pass coverage: {len(subst)-len(missing_subst)}/{len(subst)} substantive in-scope files "
          f"examined ({pct}%); {len(boiler)-len(missing_boiler)}/{len(boiler)} boilerplate.")
    if missing_subst:
        print(f"  UNEXAMINED SUBSTANTIVE ({len(missing_subst)}) — read these (deep for high value, survey for low) "
              f"and add to _coverage[] before reveal:")
        for f in missing_subst:
            print(f"     - {f}")
    if not missing_subst:
        print("  FULL COVERAGE — every substantive in-scope file examined.")
        # CHECKLIST PASS (auto): turn the reincorporated pattern library into per-site candidates so known
        # patterns get APPLIED, not just known ("having the class != applying it" — secondswap M-13). Advisory.
        try:
            import pattern_checklist
            out = pattern_checklist.build(aid)
            print(f"  CHECKLIST PASS written -> {out.relative_to(ROOT)}")
            print("  Apply every flagged candidate site (and the full per-pattern checklist) BEFORE adjudicating.")
        except Exception as _e:  # noqa: BLE001 — advisory, never block the gate
            print(f"  (pattern checklist skipped: {_e})")
        print("  OK to reveal + adjudicate.")
        return 0
    if block:
        print(f"\nBLOCKED: cold pass is thin ({pct}% substantive). Do NOT reveal/adjudicate — a thin pass "
              f"manufactures phantom coverage-gap misses. Finish coverage first. (override: --no-block)",
              file=sys.stderr)
        return 1
    return 0


def coverage_fraction(aid: str) -> dict | None:
    """Reusable per-audit cold-pass coverage stats for the scoreboard. Returns
    {examined, total_substantive, pct (0-1), full: bool} or None if coverage can't be computed
    (no scope/source or no cold pass). Mirrors cold_coverage()'s logic without printing/blocking."""
    adir = AUDITS / aid
    scope = _in_scope_files(adir)
    if scope is None:
        return None
    mf = adir / "output" / "merged_findings.json"
    if not mf.exists():
        return None
    cov = json.loads(mf.read_text()).get("_coverage", [])
    examined = {c.get("file", "") for c in cov}
    examined_base = {Path(f).name for f in examined}

    def _covered(rel: str) -> bool:
        return rel in examined or Path(rel).name in examined_base or any(rel.endswith(e) or e.endswith(rel) for e in examined)

    subst = [f for f in scope if not _is_boilerplate(f)]
    done = sum(1 for f in subst if _covered(f))
    total = max(len(subst), 1)
    return {"examined": done, "total_substantive": len(subst),
            "pct": round(done / total, 3), "full": done >= len(subst) and len(subst) > 0}


# --- AUTO-ENFORCED full-coverage gate (always-on; mirrors the production AUDITWATCH_COVERAGE_OVERRIDE gate) ----
# require_full_coverage() is wired into every reveal/adjudicate/bank chokepoint (adjudicate.py, eval-loop
# next/done) so a SCOPED ingested contest can never be revealed/banked on a thin cold pass. Discriminator =
# scope.json present (a fresh recall-lab ingest). Archived/heuristic on-disk contests have no scope.json -> not
# gated (their --auto miss-detection is unaffected). Off-by-default override: AUDITWATCH_COVERAGE_OVERRIDE=1
# (loud + stamped into adjudication.json), identical semantics to run_pipeline.sh's production gate.


def _coverage_override() -> bool:
    return os.environ.get("AUDITWATCH_COVERAGE_OVERRIDE", "").strip().lower() in ("1", "true", "yes", "on")


def _stamp_override(aid: str, pct: int, missing: int, total: int) -> None:
    """Record a deliberate fast-forward in adjudication.json so it is permanently auditable (not silent)."""
    p = AUDITS / aid / "output" / "eval_ready" / "adjudication.json"
    if not p.exists():
        return
    try:
        d = json.loads(p.read_text())
        s = d.setdefault("summary", {})
        s["coverage_override"] = True
        s["coverage_pct_substantive"] = pct
        s["coverage_unexamined"] = missing
        s["coverage_substantive_total"] = total
        p.write_text(json.dumps(d, indent=2) + "\n")
    except Exception:
        pass


def require_full_coverage(aid: str) -> int:
    """Auto-enforced precondition for reveal/adjudicate/bank of a SCOPED ingested contest. Returns 0 (proceed) if
    NOT a scoped ingest (no scope.json), or full substantive coverage, or AUDITWATCH_COVERAGE_OVERRIDE is set
    (loud + stamped). Returns 1 (BLOCK) on a thin scoped pass. No-op for archived/heuristic contests."""
    adir = AUDITS / aid
    if not (adir / "scope.json").exists():
        return 0  # not a scoped fresh ingest -> archived/heuristic, not gated
    scope = _in_scope_files(adir) or []
    mf = adir / "output" / "merged_findings.json"
    cov = json.loads(mf.read_text()).get("_coverage", []) if mf.exists() else []
    examined = {c.get("file", "") for c in cov}
    examined_base = {Path(f).name for f in examined}

    def _covered(rel: str) -> bool:
        return rel in examined or Path(rel).name in examined_base or any(rel.endswith(e) or e.endswith(rel) for e in examined)

    subst = [f for f in scope if not _is_boilerplate(f)]
    missing = [f for f in subst if not _covered(f)]
    if not missing:
        return 0
    pct = round(100 * (len(subst) - len(missing)) / max(len(subst), 1))
    if _coverage_override():
        print(f"WARNING: AUDITWATCH_COVERAGE_OVERRIDE=1 — proceeding on a THIN {aid} cold pass "
              f"({pct}% substantive; {len(missing)} unexamined in-scope files). This fast-forward is logged + "
              f"stamped into adjudication.json.", file=sys.stderr)
        _stamp_override(aid, pct, len(missing), len(subst))
        return 0
    print(f"\nBLOCKED: {aid} cold pass is THIN ({pct}% substantive; {len(missing)} unexamined in-scope files). "
          f"Full coverage is AUTO-ENFORCED before reveal/adjudicate/bank — a thin pass manufactures phantom "
          f"coverage-gap misses and hides reasoning gaps. Examine these (deep for high value, survey for low) "
          f"and add them to merged_findings._coverage[]:", file=sys.stderr)
    for f in missing:
        print(f"     - {f}", file=sys.stderr)
    print("Override (logged, not recommended): AUDITWATCH_COVERAGE_OVERRIDE=1", file=sys.stderr)
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Recall Lab looping protocol over all past contests.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build")
    sub.add_parser("status")
    sub.add_parser("next")
    sub.add_parser("enqueue-ingest")
    cc = sub.add_parser("cold-coverage")
    cc.add_argument("id")
    cc.add_argument("--no-block", action="store_true", help="report only, do not exit 1 on incomplete coverage")
    pc = sub.add_parser("pattern-checklist")
    pc.add_argument("id")
    dp = sub.add_parser("done")
    dp.add_argument("id")
    dp.add_argument("--sections", default="", help="comma-separated agents §s authored, e.g. 'logic.md#17,dos.md#11'")
    dp.add_argument("--classes", default="", help="comma-separated mechanism_class slugs reincorporated")
    args = ap.parse_args()

    if args.cmd == "build":
        return build()
    if args.cmd == "status":
        return status()
    if args.cmd == "next":
        return nxt()
    if args.cmd == "enqueue-ingest":
        return enqueue_ingest()
    if args.cmd == "cold-coverage":
        return cold_coverage(args.id, block=not args.no_block)
    if args.cmd == "pattern-checklist":
        import pattern_checklist
        out = pattern_checklist.build(args.id)
        print(f"[checklist] wrote {out} — apply every flagged candidate site before adjudicating.")
        return 0
    if args.cmd == "done":
        secs = [s.strip() for s in args.sections.split(",") if s.strip()]
        cls = [c.strip() for c in args.classes.split(",") if c.strip()]
        return done(args.id, secs, cls)
    return 1


if __name__ == "__main__":
    sys.exit(main())
