#!/usr/bin/env python3
"""
validate_spec_checklist_clears.py — flag spec-checklist clears (reward_accounting / erc4626 / permit / …)
whose checklist fields are CONFIRMATORY BOILERPLATE rather than concrete evidence. Mirrors
validate_math_estimator_clears.py.

`spec_checklist_utils.classify` only requires each checklist field to be NON-EMPTY, so a clear whose fields
read "reviewed; conserves accounting; no issue" passes the gate. The Hybra eval proved the cost: the
reward_accounting surface routed the EXACT functions of 4 awarded bugs (receivePenaltyReward,
notifyRewardAmount, claimRewards, _createGauge) onto deep passes, and each was then cleared with that kind of
boilerplate → 0 HIT. This validator adds the math-surface's adversarial rejection to the spec surfaces: a
field-complete clear is INVALID unless its checklist cites concrete evidence — a named function, a named
accounting/state variable, a file:line where available, and a yes/no answer to the bug-shape question.

Pure-classification core (`validate_clear`, `classify_surface`) — no I/O; used by coverage_sweep_write.py and
deep_pass_write.py. `main()` produces output/spec_checklist_clear_validation.{json,md} (advisory|strict),
read-only on dispositions.

Statuses per (clear, surface):
  not_spec_surface | finding_linked | duplicate_or_known | spec_checklist_valid | confirmatory_spec_clear
Blocking (strict): confirmatory_spec_clear
Advisory/normal mode never blocks (mirrors the existing spec_checklist advisory behaviour).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_context import audit_path  # noqa: E402
import spec_checklist_utils as scu  # noqa: E402

CONFIRMATORY_STATUS = "confirmatory_spec_clear"
BLOCKING_STATUSES = {CONFIRMATORY_STATUS}

# A field is "thin" (boilerplate) if, after removing these phrases/words and punctuation, almost nothing
# concrete remains. These are the generic clear words the user enumerated + their close cousins.
_BOILERPLATE = [
    "reviewed", "review", "standard", "conserves accounting", "conserves", "no issue", "no issues",
    "no impact", "nothing", "safe", "checked", "looks good", "look good", "ok", "okay", "fine",
    "correct", "as expected", "as intended", "works as designed", "behaves as documented", "n/a", "na",
    "none", "good", "verified", "confirmed", "handled", "no problem", "not applicable", "trivial",
    "straightforward", "benign", "intended", "expected", "normal", "standard accounting", "no bug",
]
# Concrete-evidence signals: a function call, a file:line span, or a private/internal identifier.
_RE_CONCRETE = re.compile(r"\.sol:\d+|\b[a-zA-Z_][a-zA-Z0-9_]*\s*\(|\b_[a-z][a-zA-Z0-9_]+\b|:\d{1,5}\b")
# Decision signals: an explicit yes/no-shaped answer to the bug-shape question.
_RE_DECISION = re.compile(
    r"\b(yes|no|does not|doesn'?t|do not|don'?t|cannot|can'?t|calls?|called|missing|absent|present|"
    r"reverts?|excluded?|included?|skips?|skipped|lacks?|fails? to|before|after|updates?|updated|"
    r"not\s+\w+|without|with no|is not|are not)\b", re.I)
# Accounting/state vocabulary a genuine reward review must name (so a reward clear that never mentions the
# accounting machinery is treated as not-concrete). Broad on purpose — any one hit is enough.
_REWARD_ACCT_RE = re.compile(
    r"reward|index|\brate\b|rollover|leftover|balance|\bstake|liquidit|epoch|checkpoint|totalsupply|"
    r"feegrowth|rewarddebt|rewardpertoken|periodfinish|updatereward|accrue|notifyreward|claim|"
    r"share|fee|emission|distribut|veNFT|locked|weight", re.I)

# Surfaces that get the STRICTER reward-style contract (must also name accounting vocab). Other surfaces use
# the base contract (concrete token + decision token).
_ACCT_SURFACES = {"reward_accounting", "vault_market_inflation_deflation", "erc4626"}


def _strip_boilerplate(text: str) -> str:
    t = text.lower()
    for ph in _BOILERPLATE:
        t = t.replace(ph, " ")
    return re.sub(r"[^a-z0-9_]+", "", t)  # keep only substantive alphanumerics


def _surface_text(disp: dict, surface: str, fields: list[str]) -> tuple[str, list[str]]:
    """Return (combined lowercased checklist text, list of filled field values) for a surface."""
    vals = []
    for f in fields:
        v = scu._field(disp, surface, f)
        if v is not None and str(v).strip():
            vals.append(str(v))
    return " ".join(vals), vals


def classify_surface(disp: dict, surface: str, fields: list[str]) -> dict:
    """Adversarially validate ONE surface's filled checklist. Assumes the fields are already field-complete
    (caller only invokes this when scu.classify said the surface is satisfied). Returns {status, reasons}."""
    text, vals = _surface_text(disp, surface, fields)
    if not vals:
        # nothing filled — not this validator's job (scu.classify already routes missing fields)
        return {"status": "spec_checklist_valid", "reasons": []}
    reasons: list[str] = []
    # 1) all-boilerplate: every filled field collapses to (near) nothing after removing generic words.
    substantive = [v for v in vals if len(_strip_boilerplate(v)) >= 6]
    if not substantive:
        reasons.append("every checklist field is generic boilerplate (reviewed/standard/safe/no issue/…) "
                       "with no substantive content")
    # 2) no concrete reference anywhere (named function, file:line, or _private identifier).
    if not _RE_CONCRETE.search(text):
        reasons.append("no concrete reference: name the function/state-var (and a file:line where available) "
                       "the checklist conclusion rests on")
    # 3) no decision token — the bug-shape question is never actually answered yes/no.
    if not _RE_DECISION.search(text):
        reasons.append("no yes/no-shaped answer (calls/does not/missing/before-after/excluded/…): state the "
                       "actual behaviour, not that it was 'reviewed'")
    # 4) reward/4626/inflation surfaces must name the accounting machinery they claim to have checked.
    if surface in _ACCT_SURFACES and not _REWARD_ACCT_RE.search(text):
        reasons.append("names no reward/accounting variable (reward index/rate/rollover/updateReward/epoch/…)"
                       " — the accounting path was never concretely traced")
    if reasons:
        return {"status": CONFIRMATORY_STATUS, "reasons": reasons}
    return {"status": "spec_checklist_valid", "reasons": []}


def validate_clear(disp: dict, item: dict, context: dict | None = None) -> dict:
    """Entry point for the write points. For each surface the item matches whose checklist is FIELD-COMPLETE,
    run the adversarial check; return the FIRST confirmatory surface (so one fix at a time). Finding-linked /
    duplicate clears are exempt. Returns {status, surface, reasons}."""
    if not item or disp.get("finding_refs"):
        return {"status": "spec_checklist_valid", "surface": None, "reasons": []}
    if disp.get("duplicate_of") or disp.get("known_ref"):
        return {"status": "duplicate_or_known", "surface": None, "reasons": []}
    context = context or {}
    fields_by_name = {name: fields for name, _, fields in scu.SURFACES}
    for surface in scu.surfaces_for(item, context):
        fields = fields_by_name[surface]
        # only adversarially check surfaces whose fields are all present (scu.classify routes the rest)
        if any(not str(scu._field(disp, surface, f) or "").strip() for f in fields):
            continue
        res = classify_surface(disp, surface, fields)
        if res["status"] == CONFIRMATORY_STATUS:
            return {"status": CONFIRMATORY_STATUS, "surface": surface, "reasons": res["reasons"]}
    return {"status": "spec_checklist_valid", "surface": None, "reasons": []}


def reason(cls: dict) -> str:
    return (f"{CONFIRMATORY_STATUS} on {cls['surface']} surface: " + "; ".join(cls["reasons"]) +
            " — a field-complete checklist of generic prose is not a review; cite concrete evidence or file a finding")


# ---------------------------------------------------------------- standalone report
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["advisory", "strict"], default="advisory")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    disp_path = audit_path("output") / "coverage_dispositions.json"
    if not disp_path.exists():
        raise SystemExit("[validate_spec_checklist_clears] coverage_dispositions.json missing — run the coverage pipeline first.")
    man_path = audit_path("output") / "coverage_manifest.json"
    items = {}
    if man_path.exists():
        try:
            items = {i["id"]: i for i in json.loads(man_path.read_text()).get("items", [])}
        except (json.JSONDecodeError, OSError):
            items = {}
    ctx = scu.build_context([i for i in items.values() if i.get("in_scope")])

    dispositions = json.loads(disp_path.read_text()).get("dispositions", [])
    rows = []
    for d in dispositions:
        if d.get("status") != "cleared":
            continue
        item = items.get(d.get("manifest_id"))
        if not item:
            continue
        res = validate_clear(d, item, ctx)
        if res["status"] == CONFIRMATORY_STATUS:
            rows.append({"manifest_id": d["manifest_id"], "surface": res["surface"],
                         "attack_surface_score": item.get("attack_surface_score", 0),
                         "reasons": res["reasons"],
                         "clear_reason": (d.get("clear_reason") or "")[:160]})

    counts = Counter(r["surface"] for r in rows)
    out = {
        "mode": args.mode,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "confirmatory_spec_clears": len(rows),
        "by_surface": dict(counts),
        "rows": rows,
    }
    (audit_path("output") / "spec_checklist_clear_validation.json").write_text(json.dumps(out, indent=2))
    md = ["# Spec-checklist clear validation (adversarial)", "",
          f"- mode: **{args.mode}**", f"- confirmatory (boilerplate) spec clears: **{len(rows)}**", "",
          "| manifest_id | score | surface | why |", "|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: -r["attack_surface_score"]):
        md.append(f"| {r['manifest_id']} | {r['attack_surface_score']} | {r['surface']} | "
                  f"{'; '.join(r['reasons'])[:120]} |")
    (audit_path("output") / "spec_checklist_clear_validation.md").write_text("\n".join(md) + "\n")

    if not args.quiet:
        print(f"[spec-checklist-clears] mode={args.mode} · confirmatory={len(rows)} · by_surface={dict(counts)}")
        for r in rows[:12]:
            print(f"   CONFIRMATORY {r['manifest_id']} [{r['surface']}]")

    if args.mode == "strict" and rows:
        print(f"[FAIL] strict mode: {len(rows)} spec-checklist clear(s) are confirmatory boilerplate. "
              f"See output/spec_checklist_clear_validation.md.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
