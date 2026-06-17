#!/usr/bin/env python3
"""Recall Lab — persist machine-checkable adjudication for an eval project.

Parses the awarded findings from a project's sealed answer key, lists the cold-pass candidates
(output/merged_findings.json), and writes output/eval_ready/adjudication.json: one row per AWARDED
finding scored STRONG | SAME_AREA | SUBSYSTEM_ONLY | MISSED (the recall-drive taxonomy).

Adjudication is a SEMANTIC judgment (done in-session "by mechanism" per the recall-lab skill). This tool
SCAFFOLDS the file and PRESERVES any label already assigned (existing adjudication.json or the
evals/known_adjudications.json seed). Unassigned rows are written as UNADJUDICATED with a token-overlap
suggestion to assist the human/skill. The scoreboard and regression gate are deterministic consumers of
the persisted labels.

  python scripts/adjudicate.py <audit-id>     # scaffold/update one project
  python scripts/adjudicate.py --all          # every scoreable project in evals/corpus.json
  python scripts/adjudicate.py <audit-id> --print

read_file: whether the awarded bug's locus file was examined in the cold pass. Distinguishes a COVERAGE-gap
miss (file unread) from a REASONING-gap miss (file read, mechanism missed) — the key triage for where to invest.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "evals" / "corpus.json"
KNOWN = ROOT / "evals" / "known_adjudications.json"

LABELS = {"STRONG", "SAME_AREA", "SUBSYSTEM_ONLY", "MISSED", "UNADJUDICATED"}
RECALLED = {"STRONG", "SAME_AREA", "SUBSYSTEM_ONLY"}  # count toward recall_of_surfaced
# Awarded findings appear as: ## [[H-01] title](url)  /  ## [[M-02] title](url)  under "# High/Medium Risk Findings"
_AWARD_RE = re.compile(r"^##\s*\[\[([A-Z]+-\d+)\]\s*(.+?)\]\(", re.MULTILINE)
_SEV_RE = re.compile(r"^#\s*(High|Medium|Low|Critical)\s+Risk\s+Findings", re.IGNORECASE | re.MULTILINE)
# Sherlock format: "# Issue M-1: title"  /  "# Issue H-2: title" — severity is encoded in the ID prefix.
_SHERLOCK_RE = re.compile(r"^#{1,3}\s*Issue\s+([A-Z]+-\d+)\s*:\s*(.+?)\s*$", re.MULTILINE)
_SEV_BY_PREFIX = {"C": "Critical", "H": "High", "M": "Medium", "L": "Low", "Q": "Low"}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_awarded(report_path: Path) -> list[dict]:
    """Return awarded High/Critical/Medium findings as [{id, severity, title}] (Low/QA excluded)."""
    text = report_path.read_text(errors="replace")
    # Build a severity map by scanning section headers in order.
    sections = [(m.start(), m.group(1).capitalize()) for m in _SEV_RE.finditer(text)]

    def sev_at(pos: int) -> str:
        cur = "Unknown"
        for start, sev in sections:
            if start <= pos:
                cur = sev
            else:
                break
        return cur

    out = []
    for m in _AWARD_RE.finditer(text):
        fid, title = m.group(1), m.group(2).strip()
        sev = sev_at(m.start())
        if sev in ("Low",):  # awarded reach denominator excludes Low/QA
            continue
        out.append({"id": fid, "severity": sev, "title": title})
    if out:
        return out
    # Fallback: Sherlock "# Issue M-1: title" format (severity from the ID prefix; no Risk-Findings sections).
    seen = set()
    for m in _SHERLOCK_RE.finditer(text):
        fid, title = m.group(1), m.group(2).strip()
        if fid in seen:  # the report repeats the header in a TOC / per-finding body; keep the first
            continue
        seen.add(fid)
        sev = _SEV_BY_PREFIX.get(fid.split("-")[0][:1].upper(), "Unknown")
        if sev == "Low":  # exclude Low/QA from the awarded reach denominator
            continue
        out.append({"id": fid, "severity": sev, "title": title})
    return out


def load_candidates(merged_path: Path) -> list[dict]:
    if not merged_path.exists():
        return []
    d = json.loads(merged_path.read_text())
    f = d.get("findings", d) if isinstance(d, dict) else d
    cands = []
    for x in (f or []):
        if not isinstance(x, dict):
            continue
        loc = x.get("location", {})
        if isinstance(loc, dict):
            file = loc.get("file") or loc.get("contract") or ""
            contract = loc.get("contract") or ""
            func = loc.get("function") or ""
        else:
            file = str(loc) if loc else ""
            contract = func = ""
        cands.append({
            "id": x.get("id"),
            "title": x.get("title", ""),
            "severity": x.get("severity", ""),
            "file": file,
            "contract": contract,
            "function": func,
            "description": x.get("description", "") or x.get("impact", ""),
        })
    return cands


_TOK = re.compile(r"[a-z0-9]+")


def _suggest(awarded_title: str, candidates: list[dict]) -> str | None:
    aw = set(_TOK.findall(awarded_title.lower()))
    best, score = None, 0
    for c in candidates:
        ov = len(aw & set(_TOK.findall((c["title"] or "").lower())))
        if ov > score:
            best, score = c["id"], ov
    return best if score >= 2 else None


_IDENT = re.compile(r"[A-Za-z_]\w+")
_SOLFILE = re.compile(r"[A-Za-z0-9_]+\.sol")
# generic words that carry no locus/mechanism signal (don't let them create false matches)
_STOP = {"the", "a", "an", "of", "to", "in", "is", "and", "or", "for", "with", "on", "by", "can", "via",
         "not", "be", "it", "that", "this", "as", "at", "function", "contract", "missing", "incorrect",
         "wrong", "allows", "due", "when", "from", "before", "after", "during", "user", "users", "attacker"}


def _toks(*parts: str) -> set[str]:
    s: set[str] = set()
    for p in parts:
        for t in _IDENT.findall((p or "").lower()):
            if len(t) >= 3 and t not in _STOP:
                s.add(t)
    return s


def _norm_from_normalization(path: Path) -> list[dict]:
    """answer_key_normalization.json (prior-eval awarded set, rich loci)."""
    d = json.loads(path.read_text())
    out = []
    for f in d.get("findings", []):
        affected = str(f.get("affected") or "")
        funcs = re.split(r"[,/]", str(f.get("functions") or ""))
        # contract/identifier names from `affected` (e.g. RiskEngine.sol(BuilderWallet) / Contract.func)
        contracts = [m for m in _IDENT.findall(affected) if m.lower() != "sol"]
        out.append({
            "id": f.get("answer_key_id") or f.get("id"),
            "severity": (f.get("severity") or "").capitalize(),
            "title": f.get("title", ""),
            "files": [m for m in _SOLFILE.findall(affected)],
            "contracts": contracts,
            "functions": [x.strip() for x in funcs if x.strip()],
            "text": " ".join([f.get("title", ""), f.get("root_cause", "")]),
        })
    return out


def _norm_from_report(path: Path) -> list[dict]:
    """C4/Sherlock report.md — title only (no structured loci)."""
    out = []
    for a in parse_awarded(path):
        out.append({"id": a["id"], "severity": a["severity"], "title": a["title"],
                    "files": _SOLFILE.findall(a["title"]), "contracts": [], "functions": [], "text": a["title"]})
    return out


def _norm_from_ground_truth(path: Path) -> list[dict]:
    out = []
    for ln in path.read_text().splitlines():
        ln = ln.strip()
        if not ln:
            continue
        try:
            r = json.loads(ln)
        except Exception:
            continue
        if str(r.get("ground_truth_outcome", "")).lower() in ("invalid", "duplicate"):
            continue
        title = r.get("title", "")
        out.append({"id": r.get("finding_id") or r.get("id"), "severity": (r.get("claimed_severity") or "").capitalize(),
                    "title": title, "files": _SOLFILE.findall(title), "contracts": [],
                    "functions": [], "text": " ".join([title, str(r.get("vuln_type", ""))])})
    return out


def load_awarded(adir: Path) -> tuple[list[dict], str]:
    """Load the awarded set from whatever artifact exists. Returns (rows, source_name).

    Priority: sealed C4/Sherlock report.md → prior-eval answer_key_normalization.json → ground_truth.jsonl.
    This is what lets ALREADY-EVALUATED contests (which carry their key in a non-report format) be scored."""
    report = adir / "_sealed_answer_key" / "report.md"
    norm = adir / "output" / "eval_ready" / "answer_key_normalization.json"
    gt = adir / "data" / "evaluation" / "ground_truth.jsonl"
    if report.exists() and parse_awarded(report):
        return _norm_from_report(report), "report.md"
    if norm.exists():
        return _norm_from_normalization(norm), "answer_key_normalization.json"
    if gt.exists():
        return _norm_from_ground_truth(gt), "ground_truth.jsonl"
    if report.exists():
        return _norm_from_report(report), "report.md"
    return [], "none"


def _auto_label(aw: dict, candidates: list[dict]) -> dict:
    """Heuristic miss-detector — CONSERVATIVE BY DESIGN (the goal is to detect misses, so a false 'caught'
    that hides a real miss is the dangerous error; we bias toward MISSED).

    Two distinct signals, kept separate:
      - FUNCTION match: an awarded function name == a candidate's function (the strongest 'same mechanism' cue).
      - MECHANISM overlap: distinctive (stop-word-filtered) token overlap of the awarded title+root_cause vs the
        candidate title+description.
    File/contract overlap alone does NOT grant recall credit — it only sets read_file=true (the cold pass
    examined that file but, lacking function/mechanism overlap, MISSED the bug = a reasoning-gap miss).

    Ladder:  STRONG   = same function AND strong mechanism overlap (>=4)
             SAME_AREA= same function (any mech) OR (same contract AND mech>=3)
             SUBSYSTEM_ONLY = strong mechanism overlap (>=4) without a function match
             MISSED   = everything else (default)."""
    aw_funcs = {t.lower() for t in aw.get("functions", []) if len(t) >= 3}
    aw_contracts = {t.lower() for t in aw.get("contracts", []) if len(t) >= 4}
    aw_files = {f.lower() for f in aw.get("files", [])}
    aw_mech = _toks(aw.get("text", ""), aw.get("title", ""))

    best = {"matched": None, "func": False, "contract": False, "read": False, "mech": 0}
    for c in candidates:
        cand_funcs = {t.lower() for t in _IDENT.findall(c.get("function", "")) if len(t) >= 3}
        cand_file = (c.get("file", "") or "").lower()
        cand_contract = (c.get("contract", "") or "").lower()
        cand_filestem = cand_file.split("/")[-1].replace(".sol", "")
        func = bool(aw_funcs & cand_funcs)
        contract = bool(aw_contracts & ({cand_contract, cand_filestem} - {""})) or any(f in cand_file for f in aw_files)
        mech = len(aw_mech & _toks(c.get("title", ""), c.get("description", "")))
        # rank candidates: prefer function match, then mech, then contract
        key = (func, mech, contract)
        bkey = (best["func"], best["mech"], best["contract"])
        if key > bkey:
            best = {"matched": c.get("id"), "func": func, "contract": contract,
                    "read": contract or func, "mech": mech}

    func, contract, mech = best["func"], best["contract"], best["mech"]
    if func and mech >= 4:
        lab, conf = "STRONG", "medium"
    elif func or (contract and mech >= 3):
        lab, conf = "SAME_AREA", "medium"
    elif mech >= 4:
        lab, conf = "SUBSYSTEM_ONLY", "low"
    else:
        lab, conf = "MISSED", "high"
    return {"label": lab, "confidence": conf,
            "matched_candidate_id": best["matched"] if lab != "MISSED" else None,
            "read_file": best["read"], "func_match": func, "contract_match": contract, "mech_score": mech}


def _load_known() -> dict:
    if KNOWN.exists():
        return json.loads(KNOWN.read_text()).get("adjudications", {})
    return {}


def adjudicate(audit_id: str, set_name: str = "unknown", auto: bool = False) -> dict:
    adir = ROOT / "audits" / audit_id
    merged = adir / "output" / "merged_findings.json"
    out_path = adir / "output" / "eval_ready" / "adjudication.json"

    awarded, awarded_source = load_awarded(adir)
    candidates = load_candidates(merged)

    # preserve existing labels, then the known-seed, else (auto-heuristic if --auto) else UNADJUDICATED
    existing = {}
    if out_path.exists():
        for r in json.loads(out_path.read_text()).get("awarded", []):
            existing[r["id"]] = r
    known = _load_known().get(audit_id, {})

    rows = []
    for a in awarded:
        fid = a["id"]
        prior = existing.get(fid, {})
        # only PRESERVE human/seed labels, never a previously-written auto label (so re-runs re-detect)
        prior_human = prior.get("source") not in (None, "auto-heuristic", "scaffold")
        seed = known.get(fid, {})
        label = prior.get("label") if (prior_human and prior.get("label") in LABELS and prior.get("label") != "UNADJUDICATED") else None
        src = "preserved" if label else None
        matched = prior.get("matched_candidate_id") if prior_human else None
        mech = prior.get("mechanism_class") if prior_human else None
        read_file = prior.get("read_file") if (prior_human and "read_file" in prior) else None
        conf = None
        if label is None and seed.get("label") in LABELS:
            label, src, matched, mech, read_file = seed["label"], "seed", seed.get("matched"), seed.get("mechanism_class"), seed.get("read_file")
        if label is None and auto and candidates:
            al = _auto_label(a, candidates)
            label, src, matched, conf = al["label"], "auto-heuristic", al["matched_candidate_id"], al["confidence"]
            read_file = al["read_file"]
        # persist a prior auto-heuristic detection across plain (non-auto) re-runs, so detected misses stick
        # until --auto recomputes them or a human/seed overrides. Only fires when not already labeled above.
        if label is None and prior.get("source") == "auto-heuristic" and prior.get("label") in LABELS \
                and prior.get("label") != "UNADJUDICATED":
            label, src, matched = prior["label"], "auto-heuristic", prior.get("matched_candidate_id")
            mech, read_file, conf = prior.get("mechanism_class"), prior.get("read_file"), prior.get("confidence")
        row = {
            "id": fid,
            "severity": a.get("severity", ""),
            "title": a.get("title", ""),
            "label": label or "UNADJUDICATED",
            "matched_candidate_id": matched,
            "mechanism_class": mech,
            "read_file": read_file,
            "source": src or "scaffold",
        }
        if conf:
            row["confidence"] = conf
        if row["label"] == "UNADJUDICATED":
            row["suggested_candidate_id"] = _suggest(a.get("title", ""), candidates)
        rows.append(row)

    n = len(rows)
    recalled = sum(1 for r in rows if r["label"] in RECALLED)
    strong = sum(1 for r in rows if r["label"] == "STRONG")
    pending = sum(1 for r in rows if r["label"] == "UNADJUDICATED")
    by_label = {lab: sum(1 for r in rows if r["label"] == lab) for lab in sorted(LABELS)}
    auto_rows = [r for r in rows if r["source"] == "auto-heuristic"]
    misses = [r for r in rows if r["label"] == "MISSED"]
    summary = {
        "awarded_total": n,
        "awarded_source": awarded_source,
        "adjudicated": n - pending,
        "pending": pending,
        "auto_adjudicated": len(auto_rows),
        "misses_detected": len(misses),
        "recall_of_surfaced": round(recalled / n, 3) if n else None,
        "strong_only": round(strong / n, 3) if n else None,
        "by_label": by_label,
        "complete": pending == 0,
    }
    doc = {
        "audit_id": audit_id,
        "set": set_name,
        "generated_at": _now(),
        "awarded_source": awarded_source,
        "auto_heuristic": bool(auto_rows),
        "awarded": rows,
        "candidates": candidates,
        "summary": summary,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(doc, indent=2) + "\n")
    return doc


def _set_of(audit_id: str) -> str:
    if not CORPUS.exists():
        return "unknown"
    c = json.loads(CORPUS.read_text())
    for s in ("training", "holdout"):
        if any(r["id"] == audit_id for r in c["sets"].get(s, [])):
            return s
    return "unknown"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("audit_id", nargs="?")
    ap.add_argument("--all", action="store_true", help="all scoreable projects in evals/corpus.json")
    ap.add_argument("--auto", action="store_true",
                    help="heuristic miss-detection: auto-label awarded findings vs the cold pass (works on "
                         "already-evaluated contests via answer_key_normalization.json / ground_truth). "
                         "Auto labels are advisory (confidence-tagged); human/seed labels always win.")
    ap.add_argument("--print", dest="show", action="store_true")
    args = ap.parse_args()

    targets: list[str] = []
    if args.all:
        c = json.loads(CORPUS.read_text())
        for s in ("training", "holdout"):
            targets += [r["id"] for r in c["sets"].get(s, []) if r.get("scoreable")]
    elif args.audit_id:
        targets = [args.audit_id]
        # AUTO-ENFORCED full coverage: revealing/adjudicating a SCOPED ingested contest requires a complete cold
        # pass (no-op for archived/heuristic contests without scope.json). Mirrors the production coverage gate.
        try:
            import recall_lab_loop as _rll  # one-way import; no import-time side effects
            if _rll.require_full_coverage(args.audit_id) != 0:
                return 1
        except SystemExit:
            raise
        except Exception:
            pass
    else:
        ap.error("give an <audit-id> or --all")

    for t in targets:
        doc = adjudicate(t, _set_of(t), auto=args.auto)
        s = doc["summary"]
        print(f"{t:42} [{doc['set']:8}] awarded={s['awarded_total']:2} src={s['awarded_source']:28} "
              f"recall={s['recall_of_surfaced']} strong={s['strong_only']} "
              f"misses={s['misses_detected']} auto={s['auto_adjudicated']} pending={s['pending']}")
        if args.show:
            for r in doc["awarded"]:
                conf = f" ({r['confidence']})" if r.get("confidence") else ""
                print(f"    {r['id']:6} {r['label']:14}{conf:10} match={r.get('matched_candidate_id') or '-':8} "
                      f"src={r['source']}  {r.get('title','')[:46]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
