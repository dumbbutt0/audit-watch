#!/usr/bin/env python3
"""Generate per-finding submission packs (report.md + bundled vulnerable source files) for both
Cartha and 0xMarkets. Read-only inputs: each workspace's merged_findings.json / findings_*.json +
(Cartha) the triage buckets. Writes reports/submission_packs/{cartha,0xmarkets}/<ID>/."""
import json, re, shutil
from pathlib import Path

ROOT = Path("/home/dummy/clones/audit-watch/smart-contract-auditor")
SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4, "qa": 4}

REPOS = {
    "cartha": Path("/home/dummy/clones/cartha-vaults-main"),
    "0xmarkets": Path("/home/dummy/clones/0xMarkets_contract-main"),
}
SRC_ROOTS = {"cartha": ["src"], "0xmarkets": ["contracts"]}

# Each program gets its own dated folder directly under reports/ (matching the audit-workspace IDs and
# the existing reports/<program>-<date>/ convention). Distinct from the prior 2026-06-13 passes.
PROGRAM_DIR = {
    "cartha": ROOT / "reports/cartha-vaults-2026-06-23",
    "0xmarkets": ROOT / "reports/0xmarkets-2026-06-23",
}
PROGRAM_TITLE = {
    "cartha": "Cartha Vaults (cartha-vaults-main, commit 4c51f2a8) — audit 2026-06-23/24",
    "0xmarkets": "0xMarkets (0xMarkets_contract-main, commit e94daee6) — audit 2026-06-23/24",
}
PROGRAM_POC_REPRO = {
    "cartha": (
        "## Reproduce the PoCs (Foundry)\n"
        "```bash\n"
        "cd ~/clones/cartha-vaults-main\n"
        "forge test --match-path 'test/poc/PoC_GmDecimalMismatch.t.sol' -vv   # CARTHA-SEAM-001 (Critical)\n"
        "forge test --match-path 'test/poc/PoC_AsyncWindowDilution.t.sol' -vv # DT-001 (High)\n"
        "```\n"
        "In-pack copies of the tests live under `CARTHA-SEAM-001/poc/` and `DT-001/poc/` (with `run_output.txt`).\n"
    ),
    "0xmarkets": (
        "## Reproduce the PoC (Hardhat integration)\n"
        "```bash\n"
        "cd ~/clones/0xMarkets_contract-main\n"
        "npm install --legacy-peer-deps --ignore-scripts\n"
        "node_modules/.bin/hardhat test test/guardian/PoC_LeverageLadderBypass.ts  # POS-001 (Medium)\n"
        "```\n"
        "In-pack copy of the test lives under `POS-001/poc/` (with `run_output.txt`).\n"
    ),
}


# HackenProof VRT category per finding — chosen VERBATIM from reports/SUBMISSION_CATEGORIES.md.
# SC findings map mostly to Business Logic Errors / Broken Access Control (BAC) / Unsecure Design /
# Blockchain; proxy-storage items with no VRT entry use "Other".
CATEGORY = {
    # --- Cartha ---
    "AC-001": "Improper Access Control",
    "AC-002": "Improper Access Control",
    "AC-003": "Improper Access Control",
    "AC-004": "Privilege Escalation",
    "AC-005": "Improper Authentication",
    "AR-001": "Business Logic Errors",
    "AR-002": "Integer Underflow",
    "AR-003": "Business Logic Errors",
    "AR-005": "Timestamp Dependence",
    "AR-006": "Business Logic Errors",
    "CARTHA-SEAM-001": "Business Logic Errors",
    "DOS-001": "DoS with (Unexpected) revert",
    "DOS-002": "DoS with (Unexpected) revert",
    "DOS-003": "DoS with (Unexpected) revert",
    "DOS-005": "DoS with (Unexpected) revert",
    "DT-001": "Transaction-Ordering Dependence (TOD) / Front Running",
    "DT-003": "Business Logic Errors",
    "DT-004": "Violation of Secure Design Principles",
    "DT-005": "Improper Access Control",
    "DT-006": "Reentrancy",
    "EA-001": "Transaction-Ordering Dependence (TOD) / Front Running",
    "EA-004": "Business Logic Errors",
    "LG-002": "Improper Authentication",
    "LG-003": "Business Logic Errors",
    "LG-004": "Business Logic Errors",
    "OR-001": "Business Logic Errors",
    "TI-004": "DoS with (Unexpected) revert",
    "TI-005": "Business Logic Errors",
    "UP-001": "Other",
    "UP-002": "Improper Access Control",
    "UP-003": "Other",
    "UP-004": "Other",
    # --- 0xMarkets ---
    "CFG-001": "Violation of Secure Design Principles",
    "CFG-002": "Business Logic Errors",
    "CFG-003": "DoS with (Unexpected) revert",
    "CFG-004": "Business Logic Errors",
    "INS-001": "Business Logic Errors",
    "INS-002": "Business Logic Errors",
    "INS-003": "Business Logic Errors",
    "INS-004": "Business Logic Errors",
    "POS-001": "Business Logic Errors",
    "PYO-001": "Business Logic Errors",
    "PYO-002": "Business Logic Errors",
    "PYO-003": "Business Logic Errors",
    "PYO-004": "Business Logic Errors",
}


def build_index(repo: Path, src_dirs):
    idx = {}
    for sd in src_dirs:
        for p in (repo / sd).rglob("*.sol"):
            idx.setdefault(p.name.lower(), p)  # first (shortest path) wins
    return idx


def sol_files_in(*texts):
    found = []
    for t in texts:
        for m in re.findall(r"([A-Za-z0-9_]+\.sol)", t or ""):
            if m.lower() not in [f.lower() for f in found]:
                found.append(m)
    return found


def loc_text(loc):
    if isinstance(loc, dict):
        return loc.get("raw") or " ".join(str(v) for v in loc.values())
    return str(loc or "")


DISPO_BANNER = {
    "real": None,
    "merged": "> **DISPOSITION: MERGED — duplicate.** This is the same root cause as another finding; "
              "it is kept here for traceability only and should NOT be submitted separately (see Triage reasoning for the primary).",
    "rejected": "> **DISPOSITION: REJECTED — honest negative (NOT a vulnerability).** Investigated and cleared; "
                "included for audit completeness. Do NOT submit. See Disproof / boundary below.",
    "info": "> **DISPOSITION: INFO — informational / hardening note.** Not a security vulnerability on its own.",
}


def write_report(d, sev, status, reason, follow, disproof, srcs, disposition="real"):
    L = []
    L.append(f"# {d['id']} — {d['title']}\n")
    banner = DISPO_BANNER.get(disposition)
    if banner:
        L.append(banner + "\n")
    L.append(f"- **Severity (recommended):** {sev}")
    L.append(f"- **Category (HackenProof VRT):** {CATEGORY.get(d['id'], 'Other')}")
    if status:
        L.append(f"- **Triage status:** {status}")
    L.append(f"- **Confidence:** {d.get('confidence','-')}")
    ice = d.get("ice_chain") or {}
    if ice:
        L.append(f"- **ICE:** Impact={ice.get('impact','-')} · Confidence={ice.get('confidence','-')} · Exploitability={ice.get('exploitability','-')}")
    L.append(f"- **Location(s):** `{loc_text(d.get('location'))}`")
    if srcs:
        L.append(f"- **Vulnerable files (bundled in `sources/`):** {', '.join('`'+s+'`' for s in srcs)}")
    L.append("\n## Description\n")
    L.append(d.get("description", "").strip())
    L.append("\n## Impact\n")
    L.append((d.get("impact") or "-").strip())
    ite = d.get("ite") or {}
    if ite:
        L.append("\n## Attack path (Intent / Technique / Evasion)\n")
        L.append(f"- **Intent:** {ite.get('intent','-')}")
        L.append(f"- **Technique:** {ite.get('technique','-')}")
        L.append(f"- **Evasion:** {ite.get('evasion','-')}")
    if follow:
        L.append("\n## Reachability / follow-up\n")
        L.append(follow if isinstance(follow, str) else json.dumps(follow))
    if reason:
        L.append("\n## Triage reasoning\n")
        L.append(reason)
    if disproof:
        L.append("\n## Disproof / boundary\n")
        L.append(disproof)
    return "\n".join(L) + "\n"


def gen(repo_key):
    repo = REPOS[repo_key]
    idx = build_index(repo, SRC_ROOTS[repo_key])
    wsname = "cartha-vaults-2026-06-23" if repo_key == "cartha" else "0xmarkets-2026-06-23"
    ws = ROOT / "audits" / wsname / "output"
    base = PROGRAM_DIR[repo_key]

    # load all findings (id -> finding)
    findings = {}
    merged = ws / "merged_findings.json"
    if merged.exists():
        for f in json.loads(merged.read_text()).get("findings", []):
            findings[f.get("id") or f.get("finding_id")] = f
    for p in sorted(ws.glob("findings_*.json")):
        try:
            for f in json.loads(p.read_text()).get("findings", []):
                fid = f.get("id") or f.get("finding_id")
                findings.setdefault(fid, f)
        except Exception:
            continue

    # decide which ids are "real" + their recommended severity / triage meta
    # disposition by bucket: real findings vs merged duplicates vs rejected honest-negatives vs info
    BUCKET_DISPO = {"submit": "real", "poc_required": "real", "downgraded": "real",
                    "merged": "merged", "rejected": "rejected"}
    decisions = {}
    if repo_key == "cartha":
        tri = ROOT / "audits" / wsname / "data/triage"
        for bucket in ("submit", "poc_required", "downgraded", "merged", "rejected"):
            fp = tri / f"{bucket}.jsonl"
            if not fp.exists():
                continue
            for line in fp.read_text().splitlines():
                if not line.strip():
                    continue
                r = json.loads(line)
                fid = r.get("finding_id") or r.get("id")
                decisions[fid] = {
                    "status": r.get("triage_status", bucket),
                    "sev": r.get("recommended_severity") or (findings.get(fid, {}).get("severity")),
                    "reason": r.get("decision_reason"),
                    "follow": r.get("follow_up_packet"),
                    "disproof": r.get("disproof"),
                    "disposition": BUCKET_DISPO.get(bucket, "real"),
                }
    else:
        for fid, f in findings.items():
            is_info = (f.get("severity") or "").lower() == "info"
            decisions[fid] = {"status": None, "sev": f.get("severity"), "reason": None,
                              "follow": (f.get("ice_chain") or {}).get("exploitability"), "disproof": None,
                              "disposition": "info" if is_info else "real"}

    rows = []
    for fid, meta in decisions.items():
        d = findings.get(fid)
        if not d:
            continue
        sev = meta["sev"] or d.get("severity") or "Info"
        srcnames = sol_files_in(d.get("title"), d.get("description"), loc_text(d.get("location")))
        # also pull from manifest_refs (format: kind:File:fn#hash)
        for ref in d.get("manifest_refs", []) or []:
            parts = ref.split(":")
            if len(parts) >= 2:
                cand = parts[1] + ".sol"
                if cand.lower() not in [s.lower() for s in srcnames]:
                    srcnames.append(cand)
        pdir = base / fid
        sdir = pdir / "sources"
        sdir.mkdir(parents=True, exist_ok=True)
        copied = []
        for sn in srcnames:
            sp = idx.get(sn.lower())
            if sp and sp.exists():
                shutil.copy2(sp, sdir / sp.name)
                copied.append(sp.name)
        (pdir / "report.md").write_text(
            write_report(d, sev, meta["status"], meta["reason"], meta["follow"], meta["disproof"], copied,
                         meta.get("disposition", "real"))
        )
        rows.append((meta.get("disposition", "real"), sev, fid, d.get("title", ""), ", ".join(copied) or "-", meta["status"] or "", CATEGORY.get(fid, "Other")))

    DISPO_ORDER = {"real": 0, "merged": 1, "rejected": 2, "info": 3}
    DISPO_LABEL = {"real": "Real findings (recommended for submission)",
                   "merged": "Merged duplicates (do not submit separately)",
                   "rejected": "Rejected — honest negatives (do not submit)",
                   "info": "Informational"}
    rows.sort(key=lambda r: (DISPO_ORDER.get(r[0], 9), SEV_ORDER.get(r[1].lower(), 9), r[2]))
    n_real = sum(1 for r in rows if r[0] == "real")
    idx_md = [f"# Submission Packs — {repo_key}\n",
              f"{len(rows)} findings total ({n_real} real + {len(rows)-n_real} merged/rejected/info). "
              f"Each folder has `report.md` + `sources/` (full vulnerable files).\n"]
    for dispo in ("real", "merged", "rejected", "info"):
        drows = [r for r in rows if r[0] == dispo]
        if not drows:
            continue
        idx_md.append(f"## {DISPO_LABEL[dispo]} ({len(drows)})\n")
        idx_md.append("| ID | Severity | Category (VRT) | Title | Vulnerable files | Status |")
        idx_md.append("|---|---|---|---|---|---|")
        for _, sev, fid, title, files, status, cat in drows:
            idx_md.append(f"| [{fid}]({fid}/report.md) | {sev} | {cat} | {title[:70]} | {files} | {status} |")
        idx_md.append("")
    (base).mkdir(parents=True, exist_ok=True)
    (base / "INDEX.md").write_text("\n".join(idx_md) + "\n")

    # per-program README
    rd = [f"# Submission packs — {PROGRAM_TITLE[repo_key]}\n",
          f"{len(rows)} finding folders ({n_real} real + {len(rows)-n_real} merged/rejected/info). "
          "Each `<ID>/` is self-contained: `report.md` + `sources/` (full vulnerable files). "
          "The permissionless PoC bugs additionally have `SUBMISSION.md` (bounty-ready) + `poc/` (test + run output).\n",
          "See **`INDEX.md`** for the full table grouped by disposition (real / merged duplicate / rejected honest-negative / info).\n",
          "Every `report.md` carries a disposition banner — merged duplicates and rejected honest-negatives are kept "
          "for traceability and must NOT be submitted.\n",
          PROGRAM_POC_REPRO.get(repo_key, "")]
    (base / "README.md").write_text("\n".join(rd) + "\n")
    return len(rows), n_real


if __name__ == "__main__":
    for k in REPOS:
        n, n_real = gen(k)
        print(f"{k}: {n} packs ({n_real} real) -> {PROGRAM_DIR[k]}")
