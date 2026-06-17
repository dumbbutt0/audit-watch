#!/usr/bin/env python3
"""Surface VRT category + CVSS onto the dashboard data (and submission_candidate.json packages).

Single source of truth = reports/add_classification_cvss.py (DATA: category + CVSS vectors). This script
writes those values into:
  1. each submission_candidate.json  -> top-level `vrt_category` + `cvss` (list of {aspect,vector,score,severity})
  2. documentation/real_world_results.json -> each matching candidate_finding's `verifier.vrt_category`/`verifier.cvss`
     (the card reads verifier-block keys via funnel._records_from_real_world -> build_verifier_evidence).
Idempotent (overwrites only these two keys); backs up real_world_results.json first. Display-only; never
touches severity/routing/eval corpus.
"""
import importlib.util, json, os, time, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("acc", os.path.join(ROOT, "reports/add_classification_cvss.py"))
acc = importlib.util.module_from_spec(spec); spec.loader.exec_module(acc)


def cvss_list(meta):
    out = []
    for label, vec in meta["rows"]:
        s = acc.cvss(vec)
        out.append({"aspect": label, "vector": vec, "score": s, "severity": acc.band(s)})
    return out


def vrt_str(meta):
    s = meta["primary"]
    if meta.get("secondary"):
        s += "  ·  " + meta["secondary"]
    return s


# ---- 1. submission_candidate.json packages ----
for report_rel, meta in acc.DATA.items():
    sc = os.path.join(ROOT, report_rel.replace("report.md", "submission_candidate.json"))
    if not os.path.exists(sc):
        print("skip (no json):", sc)
        continue
    d = json.load(open(sc))
    d["vrt_category"] = vrt_str(meta)
    d["cvss"] = cvss_list(meta)
    json.dump(d, open(sc, "w"), indent=2)
    print("pkg  ", os.path.relpath(sc, ROOT), "->", ", ".join(f"{c['score']:.1f} {c['severity']}" for c in d["cvss"]))

# ---- 2. real_world_results.json candidate_findings (match by title substring -> DATA folder) ----
# substring(found in cf.title) -> DATA key (report.md path)
MATCH = [
    ("Broken health-transition", "reports/tiprun-2026-06-13/submissions/F-1/report.md"),
    ("Maintenance-margin bypass", "reports/tiprun-2026-06-13/submissions/F-1/report.md"),
    ("Inverted ratio guard", "reports/tiprun-2026-06-13/submissions/F-1/report.md"),  # M-1 row -> use F-1 meta (covers B)
    ("Risk-segment freeze", "reports/tiprun-2026-06-13/submissions/F-2/report.md"),
    ("no read-side staleness", "reports/tiprun-2026-06-13/submissions/M-2/report.md"),
    ("Liquidate/Deleverage", "reports/tiprun-2026-06-13/submissions/M-3/report.md"),
    ("configVersion", "reports/tiprun-2026-06-13/submissions/M-4/report.md"),
    ("Stale/zero-TVL", "reports/cartha-2026-06-13/submissions/C-1/report.md"),
    ("Child shares transferable", "reports/cartha-2026-06-13/submissions/L-2/report.md"),
]
# For the M-1 row, narrow the category + CVSS to the de-risk (Manifestation B) only. M-1 is a redirect to
# F-1 (no DATA entry of its own), so its classification is defined inline here.
M1_META = dict(
    primary="Blockchain → DoS with (Unexpected) revert (inverted ratio guard reverts legitimate de-risking; merged into F-1 — same root cause)",
    rows=[("de-risk DoS / unexpected revert (Manifestation B of F-1)", "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L")],
)

rw = os.path.join(ROOT, "documentation/real_world_results.json")
bak = rw + ".bak." + time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
shutil.copy(rw, bak)
data = json.load(open(rw))
n = 0
for cf in data.get("candidate_findings", []):
    if cf.get("target") not in ("TipRun", "Cartha"):
        continue
    title = cf.get("title", "")
    meta = None
    is_m1 = "Inverted ratio guard" in title or "MERGED INTO F-1" in title
    for sub, key in MATCH:
        if sub in title:
            meta = M1_META if is_m1 else acc.DATA[key]
            break
    if not meta:
        continue
    v = cf.setdefault("verifier", {})
    v["vrt_category"] = vrt_str(meta)
    v["cvss"] = cvss_list(meta)
    n += 1
    print("rw   ", cf.get("severity"), "|", title[:48], "->", ", ".join(f"{c['score']:.1f} {c['severity']}" for c in v["cvss"]))

json.dump(data, open(rw, "w"), indent=2)
print(f"\nbackup: {bak}")
print(f"updated candidate_findings: {n}")
