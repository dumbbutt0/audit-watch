#!/usr/bin/env python3
"""Recall Lab — ingest a fresh scored contest as a HOLDOUT target.

Deterministic scaffolding for the blind-ingest protocol (the source fetch — curl of the contest's verified
source/repo — is operator-driven since it varies per contest):
  1. register the audit in audits/registry.json
  2. create the audit subdirs (reuses audit_context._AUDIT_SUBDIRS) + meta.json
  3. SEAL the awarded report under audits/<id>/_sealed_answer_key/report.md (do NOT read it before the cold pass)
  4. add the project to evals/corpus.json (default set: holdout)

Then run the blind cold pass (/ite-audit) and `run_pipeline.sh eval-adjudicate <id>` after revealing.

  python scripts/ingest_contest.py --id intuition-2026-07-blind --name "Intuition" --platform code4rena \
      --report /tmp/2026-07-intuition-report.md [--source /path/to/fetched/src] [--set holdout] [--scoreable]

Use a post-cutoff contest id with a -blind suffix so it auto-filters from the real-world dashboard.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from audit_context import _AUDIT_SUBDIRS  # noqa: E402
import compute_metrics as cm  # noqa: E402

AUDITS = ROOT / "audits"
REGISTRY = AUDITS / "registry.json"
CORPUS = ROOT / "evals" / "corpus.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f%z")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", required=True, help="audit id (use a -blind suffix; auto-filters from dashboard)")
    ap.add_argument("--name", required=True)
    ap.add_argument("--platform", default="code4rena")
    ap.add_argument("--contest", default="")
    ap.add_argument("--report", help="path to the awarded-findings report.md to SEAL")
    ap.add_argument("--source", help="optional dir of fetched verified source -> contracts/")
    ap.add_argument("--set", dest="set_name", choices=["holdout", "training"], default="holdout")
    ap.add_argument("--scoreable", action="store_true", help="mark scoreable now (has report + will have a cold pass)")
    ap.add_argument("--scope-json", help="path to a JSON with the in-scope file list (Sherlock contest detail "
                    "with scope[].files[], or {\"in_scope_files\":[...]}) -> writes audits/<id>/scope.json so the "
                    "cold-pass full-coverage gate has an accurate denominator")
    ap.add_argument("--language", default="solidity", choices=["solidity", "rust", "vyper", "move"],
                    help="audit language (routes the manifest taxonomy + ite-audit specialist set + coverage gate)")
    args = ap.parse_args()

    aid = args.id
    if not cm._is_eval_audit(aid):
        print(f"WARNING: '{aid}' is NOT recognized as an eval id by compute_metrics._is_eval_audit — it would "
              f"COUNT toward the real-world dashboard. Use a -blind/-eval/-holdout suffix.", file=sys.stderr)
        return 2

    adir = AUDITS / aid
    if adir.exists():
        print(f"'{aid}' already exists at {adir}", file=sys.stderr)
        return 1

    # 2. subdirs + meta
    for sub in _AUDIT_SUBDIRS:
        (adir / sub).mkdir(parents=True, exist_ok=True)
    (adir / "_sealed_answer_key").mkdir(parents=True, exist_ok=True)
    (adir / "meta.json").write_text(json.dumps({
        "audit_id": aid, "name": args.name, "contest": args.contest, "platform": args.platform,
        "status": "active", "language": args.language, "created_at": _now(),
        "recall_lab": True, "set": args.set_name,
    }, indent=2) + "\n")

    # 1. registry
    reg = json.loads(REGISTRY.read_text()) if REGISTRY.exists() else {"audits": []}
    if not any(a["audit_id"] == aid for a in reg.get("audits", [])):
        reg.setdefault("audits", []).append({
            "audit_id": aid, "name": args.name, "contest": args.contest, "platform": args.platform,
            "status": "active", "start_date": _now()[:10], "submit_count": 0, "poc_count": 0,
            "last_active": _now(),
        })
        REGISTRY.write_text(json.dumps(reg, indent=2) + "\n")

    # 3. seal report
    sealed = False
    if args.report:
        rp = Path(args.report)
        if not rp.exists():
            print(f"--report not found: {rp}", file=sys.stderr)
            return 1
        shutil.copy(rp, adir / "_sealed_answer_key" / "report.md")
        sealed = True

    # optional scope.json (the in-scope denominator for the cold-pass full-coverage gate)
    if args.scope_json:
        try:
            raw = json.loads(Path(args.scope_json).read_text())
            files = []
            if isinstance(raw, dict) and raw.get("in_scope_files"):
                files = [f if isinstance(f, dict) else {"file": f} for f in raw["in_scope_files"]]
            else:  # Sherlock contest-detail shape: scope[].files[]
                for s in raw.get("scope", []) if isinstance(raw, dict) else []:
                    for f in s.get("files", []):
                        n = f.get("name", "")
                        if n.endswith((".sol", ".rs", ".vy")):  # cross-language scope denominator
                            files.append({"file": n[len("contracts/"):] if n.startswith("contracts/") else n,
                                          "nsloc": f.get("nsloc")})
            if files:
                (adir / "scope.json").write_text(json.dumps(
                    {"audit_id": aid, "source": args.scope_json, "in_scope_files": files, "count": len(files)},
                    indent=2) + "\n")
                print(f"wrote scope.json: {len(files)} in-scope file(s)")
        except Exception as e:
            print(f"WARNING: could not parse --scope-json ({e}); skipping scope.json", file=sys.stderr)

    # optional source
    if args.source:
        sp = Path(args.source)
        if sp.exists():
            shutil.copytree(sp, adir / "contracts" / "_sources" / sp.name, dirs_exist_ok=True)

    # 4. corpus
    corpus = json.loads(CORPUS.read_text())
    entry = {"id": aid, "cutoff": "post", "scoreable": bool(args.scoreable and sealed),
             "answer_key": "_sealed_answer_key/report.md" if sealed else None, "cold_pass": False}
    s = corpus["sets"].setdefault(args.set_name, [])
    if not any(r["id"] == aid for r in s):
        s.append(entry)
        s.sort(key=lambda r: r["id"])
    CORPUS.write_text(json.dumps(corpus, indent=2) + "\n")

    if entry["scoreable"] and not (adir / "scope.json").exists():
        print("WARNING: no scope.json written (pass --scope-json <sherlock-contest.json | {in_scope_files:[...]}>). "
              "The AUTO-ENFORCED full-coverage gate cannot enforce a complete cold pass without the in-scope "
              "denominator — this ingest could be revealed on a thin pass. Add scope.json before the cold pass.",
              file=sys.stderr)

    print(f"ingested {aid} -> {args.set_name} (sealed_report={sealed}, scoreable={entry['scoreable']})")
    print("next: fetch source into contracts/ if not provided; sandbox_check.py; blind /ite-audit (KEY SEALED);")
    print("      then reveal + ./run_pipeline.sh eval-adjudicate " + aid)
    return 0


if __name__ == "__main__":
    sys.exit(main())
