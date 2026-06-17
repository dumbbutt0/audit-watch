#!/usr/bin/env python3
"""assert_blind.py (T4) — mechanically wall off the sealed answer key during a recall-lab BLIND cold pass.

Today "blind" is prompt-discipline only — a cold-pass agent CAN read audits/<id>/_sealed_answer_key/report.md, so
recall numbers are only as honest as the agent's restraint (a contaminated Move pass had to be discarded). This
makes blind physical:

  seal   <id>  → move audits/<id>/_sealed_answer_key/ OUT of the repo to ~/.audit_watch_keyvault/<id>/ and drop a
                 marker output/_blind_pass.json. The cold pass then literally cannot open the key (it's not in the
                 working tree the agents operate in).
  check  <id>  → exit 0 if the audit is currently sealed-blind (key absent + marker); exit 1 otherwise. Use as a
                 cold-pass preflight so a non-blind pass can't proceed.
  reveal <id>  → move the key back for adjudication; the marker remains so we know the pass WAS blind.
  leakage <id> → backstop after reveal: flag verbatim answer-key title overlap in merged_findings (contamination).

Read-only on source; only moves the key dir + writes the marker.
"""
import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDITS = ROOT / "audits"
VAULT = Path.home() / ".audit_watch_keyvault"


def _paths(aid: str):
    adir = AUDITS / aid
    return adir, adir / "_sealed_answer_key", VAULT / aid / "_sealed_answer_key", adir / "output" / "_blind_pass.json"


def seal(aid: str) -> int:
    adir, key, vault, marker = _paths(aid)
    if not adir.exists():
        print(f"[assert_blind] no audit {aid}", file=sys.stderr)
        return 2
    if vault.exists():
        print(f"[assert_blind] {aid} already sealed (key in vault) — leaving as-is.")
        return 0
    if not key.exists():
        print(f"[assert_blind] {aid}: no _sealed_answer_key/ to seal (already moved or none).", file=sys.stderr)
        return 1
    vault.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(key), str(vault))
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(json.dumps({"sealed_at": datetime.now(timezone.utc).isoformat(),
                                  "vault": str(vault), "blind": True}, indent=2))
    print(f"[assert_blind] SEALED {aid}: key moved out of the repo → {vault}. Cold pass is now physically blind.")
    return 0


def reveal(aid: str) -> int:
    adir, key, vault, marker = _paths(aid)
    if key.exists():
        print(f"[assert_blind] {aid}: key already present — nothing to reveal.")
        return 0
    if not vault.exists():
        print(f"[assert_blind] {aid}: no vaulted key to restore.", file=sys.stderr)
        return 1
    key.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(vault), str(key))
    print(f"[assert_blind] REVEALED {aid}: key restored from vault for adjudication (blind marker kept).")
    return 0


def check(aid: str) -> int:
    adir, key, vault, marker = _paths(aid)
    if key.exists():
        print(f"[assert_blind] NOT BLIND: {aid}/_sealed_answer_key/ is present in the working tree — "
              f"seal it first: ./run_pipeline.sh eval-seal {aid}", file=sys.stderr)
        return 1
    if not marker.exists():
        print(f"[assert_blind] {aid}: key absent but no blind marker — run eval-seal to record a blind pass.",
              file=sys.stderr)
        return 1
    print(f"[assert_blind] BLIND OK: {aid} key is vaulted; cold pass cannot read it.")
    return 0


_WORD = re.compile(r"[a-z0-9_]{4,}")


def _titles_from_report(text: str) -> list[str]:
    out = []
    for ln in text.splitlines():
        m = re.match(r"^#{1,3}\s*(?:Issue\s+)?\[?[A-Z]+-\d+[:\]]?\s*(.+)$", ln.strip())
        if m:
            out.append(m.group(1).strip())
    return out


def leakage(aid: str) -> int:
    adir, key, vault, marker = _paths(aid)
    report = key / "report.md"
    merged = adir / "output" / "merged_findings.json"
    if not report.exists() or not merged.exists():
        print(f"[assert_blind] leakage: need both revealed report.md and merged_findings.json — skipping.")
        return 0
    awarded = _titles_from_report(report.read_text(errors="replace"))
    aw_sets = [set(_WORD.findall(t.lower())) for t in awarded if t]
    findings = json.loads(merged.read_text()).get("findings", [])
    hits = []
    for f in findings:
        toks = set(_WORD.findall((f.get("title", "")).lower()))
        for t, aw in zip(awarded, aw_sets):
            # verbatim-ish overlap: a cold finding title sharing >=5 distinctive tokens with an awarded title
            if aw and len(toks & aw) >= 5:
                hits.append((f.get("id"), t))
    if hits:
        print(f"[assert_blind] ⚠ POSSIBLE LEAKAGE in {aid}: {len(hits)} cold finding title(s) closely match awarded "
              f"titles — verify the pass was blind:", file=sys.stderr)
        for fid, t in hits[:10]:
            print(f"    {fid} ~ \"{t[:60]}\"", file=sys.stderr)
        return 1
    print(f"[assert_blind] leakage check: no suspicious answer-key title overlap in {aid}.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Mechanically enforce a blind recall-lab cold pass")
    ap.add_argument("action", choices=["seal", "reveal", "check", "leakage"])
    ap.add_argument("audit_id")
    args = ap.parse_args()
    return {"seal": seal, "reveal": reveal, "check": check, "leakage": leakage}[args.action](args.audit_id)


if __name__ == "__main__":
    sys.exit(main())
