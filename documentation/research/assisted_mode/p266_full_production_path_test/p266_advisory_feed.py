#!/usr/bin/env python3
"""P266 — standalone advisory-only dashboard surface (analysis-only; NOT a production module).

Reads the FROZEN shadow harness output (recall_advisory_candidates.json) and emits:
  * outputs/advisory_recall_feed.json  — a static advisory feed (every record ADVISORY_RECALL_CANDIDATE,
    severity null, all promotion flags false)
  * outputs/p266_advisory.html         — a standalone static page rendering ONLY advisory candidates, each
    visibly stamped ADVISORY ONLY / NOT CONFIRMED / NOT REPORTABLE / NOT SUBMISSION-READY / severity HUMAN_PENDING.

SAFETY: This NEVER imports/touches scripts/dashboard.py, scripts/dashboard_sync.py, dashboard/*.html, or any
canonical finding record. The page has NO promote/confirm/submit control. The only operator action — "select for
PoC queue" — is a static checkbox that maps to the isolated P266 PoC queue (written by hand in Phase 3), never to a
canonical record. It is a read-only advisory view; it makes it structurally impossible for a candidate to look
confirmed.
"""
import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
SHADOW = OUT / "phi_shadow" / "recall_advisory_candidates.json"

# Fields that MUST be false/null on every advisory record (mirrors the harness guard).
PROMO_FALSE = ("reportable", "submission_ready", "concluded", "emits_finding", "production_routing")
BANNER = "ADVISORY ONLY · NOT CONFIRMED · NOT REPORTABLE · NOT SUBMISSION-READY · severity: HUMAN_PENDING"


def build_feed(shadow: dict) -> dict:
    rows = []
    for c in shadow["advisory_candidates"]:
        # re-assert the advisory contract on every row (defensive; do not trust upstream blindly)
        assert c["status"] == "ADVISORY_RECALL_CANDIDATE", f"non-advisory status: {c['status']}"
        assert c["severity"] is None
        for f in PROMO_FALSE:
            assert c[f] is False, f"{f} set on {c['candidate_id']}"
        r = c.get("prioritizer_score")
        rows.append({
            "candidate_id": c["candidate_id"],
            "locus": c["locus"],
            "contract": c["contract"], "function": c["function"],
            "prioritizer_rank": r,
            "recall_class": "RECALL_DELTA" if (r is None or r >= 5) else "NARROW_BASELINE",
            "templates_applied": c["templates_applied"],
            "sweep_inclusion_reason": c["sweep_inclusion_reason"],
            "bc_ranking_handoff": c["bc_ranking_handoff"],
            "generated_mechanism_count": len(c.get("generated_mechanisms", [])),
            "status": "ADVISORY_RECALL_CANDIDATE",
            "promotion_label": c["promotion_label"],
            # the operator action surface — advisory-only, routes ONLY to the isolated P266 PoC queue
            "operator_action": "SELECT_FOR_P266_POC_QUEUE (advisory; writes isolated queue only)",
            # hard-stamped non-authority fields
            "severity": None, "reportable": False, "submission_ready": False,
            "concluded": False, "emits_finding": False, "production_routing": False,
            "confirmed": False, "canonical_record": False,
        })
    return {
        "feed": "p266_advisory_recall_feed",
        "surface": "standalone (does NOT touch dashboard.py / dashboard_sync.py / canonical records)",
        "is_gate": False, "research_only": True, "routes_in_production": False, "routed_manifest_ids": [],
        "emits_findings": False, "concludes_vulnerability": False,
        "controls_present": ["select_for_p266_poc_queue (advisory)"],
        "controls_absent": ["promote_to_finding", "confirm", "set_severity", "mark_reportable",
                            "mark_submission_ready", "submit"],
        "banner": BANNER,
        "advisory_candidate_count": len(rows),
        "advisory_candidates": rows,
    }


def render_html(feed: dict) -> str:
    rows = []
    for r in feed["advisory_candidates"]:
        cls = "delta" if r["recall_class"] == "RECALL_DELTA" else "narrow"
        tmpl = ", ".join(t.split("_")[0] for t in r["templates_applied"])
        rows.append(
            f'<tr class="{cls}">'
            f'<td><input type="checkbox" disabled title="advisory select → isolated P266 PoC queue only"></td>'
            f'<td>{html.escape(str(r["prioritizer_rank"]))}</td>'
            f'<td>{html.escape(r["recall_class"])}</td>'
            f'<td><code>{html.escape(r["contract"])}.{html.escape(r["function"])}</code></td>'
            f'<td>{html.escape(tmpl)}</td>'
            f'<td>{html.escape(", ".join(r["sweep_inclusion_reason"]))}</td>'
            f'<td class="adv">ADVISORY</td>'
            f'<td>null</td>'
            f'</tr>')
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>P266 — Advisory Recall Candidates (ADVISORY ONLY)</title>
<style>
 body{{font-family:system-ui,sans-serif;margin:1.5rem;background:#fafafa;color:#111}}
 .topbanner{{background:#7a1f1f;color:#fff;padding:.75rem 1rem;border-radius:6px;font-weight:700;letter-spacing:.3px}}
 .sub{{color:#555;margin:.5rem 0 1rem}}
 table{{border-collapse:collapse;width:100%;background:#fff}}
 th,td{{border:1px solid #ddd;padding:.4rem .55rem;font-size:13px;text-align:left}}
 th{{background:#eee}}
 tr.delta td:first-child+td{{font-weight:700}}
 .delta{{background:#fffdf5}} .narrow{{background:#f5f9ff}}
 td.adv{{color:#7a1f1f;font-weight:700}}
 .legend{{margin-top:1rem;font-size:12px;color:#555}}
 .nocontrols{{margin-top:1rem;padding:.6rem .8rem;border-left:4px solid #7a1f1f;background:#fff;font-size:12px}}
</style></head><body>
<div class="topbanner">{html.escape(feed['banner'])}</div>
<p class="sub">Standalone advisory recall feed (P266). {feed['advisory_candidate_count']} candidates.
This page renders <b>only</b> ADVISORY_RECALL_CANDIDATE records. It does not read or write canonical findings and
has no promote/confirm/submit control. Checkboxes are disabled here; candidate selection for the PoC queue is a
manual, isolated step that writes only to the P266 PoC queue.</p>
<table>
<thead><tr><th>select</th><th>rank</th><th>recall class</th><th>locus</th><th>templates</th>
<th>inclusion</th><th>status</th><th>severity</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
<div class="nocontrols"><b>Controls present:</b> {', '.join(feed['controls_present'])}<br>
<b>Controls ABSENT (by design):</b> {', '.join(feed['controls_absent'])}</div>
<p class="legend">RECALL_DELTA = forced in beyond the P260 narrow top-5 (the recall-first contribution).
NARROW_BASELINE = the old narrow path would have surfaced it. None of these are findings; each requires downstream
B/C ranking + five-op completion + PoC + human review before any escalation.</p>
</body></html>"""


def main():
    shadow = json.loads(SHADOW.read_text())
    feed = build_feed(shadow)
    (OUT / "advisory_recall_feed.json").write_text(json.dumps(feed, indent=2))
    (OUT / "p266_advisory.html").write_text(render_html(feed))
    print(f"advisory candidates: {feed['advisory_candidate_count']}")
    print(f"controls_present: {feed['controls_present']}")
    print(f"controls_absent: {feed['controls_absent']}")
    # final guard: no record carries any authority field
    for r in feed["advisory_candidates"]:
        assert r["severity"] is None and r["confirmed"] is False and r["canonical_record"] is False
        for f in PROMO_FALSE:
            assert r[f] is False
    print("GUARD: all records advisory-only (severity null, 0 promotion flags, not confirmed, not canonical)")


if __name__ == "__main__":
    main()
