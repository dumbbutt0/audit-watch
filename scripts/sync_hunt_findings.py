#!/usr/bin/env python3
"""sync_hunt_findings.py — P217 generic per-hunt dashboard sync wrapper (research-only, read-only on shared files).

Run at the end of ANY hunt/rehearsal/eval to route its candidates into the dashboard mirror
(documentation/research/funnel/synced_findings.generated.json) with fields populated PROGRAMMATICALLY from the real
artifacts. Reuses dashboard_sync.to_synced_finding / validate_synced (P216) as the pure mapping + safety gate; this
wrapper only discovers + extracts + scores + writes safely.

NEVER: enables submission, adds submit/promote controls, computes severity, flips submission_ready, sets
routing_allowed:true, or writes route/submit output. Absent evidence stays "unknown"/"MISSING_EVIDENCE" — never invented.
"""
from __future__ import annotations
import argparse, json, os, re, sys, time, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import dashboard_sync as ds  # noqa: E402
import human_review_priority as hrp  # noqa: E402  (P222: pure priority classifier; display/prioritization only)

DEFAULT_OUT = ROOT / "documentation/research/funnel/synced_findings.generated.json"

EVIDENCE_FIELDS = ["title", "summary", "affected_contracts", "affected_functions", "source_refs", "mechanism",
                   "root_cause", "attacker_model", "exploit_steps", "function_map", "defense_map", "poc_verification",
                   "impact_and_severity", "intent_scope_operator_assumptions", "novelty_duplicate",
                   "conversion_classification", "main_blocker", "final_triager_decision", "red_flags",
                   "evidence_backup", "l3_status"]

_ATTACKER = {"permissionless": "unprivileged user (permissionless entrypoint)",
             "privileged": "privileged role required (TSS / updater / FUNGIBLE_MODULE)",
             "conditional": "conditional — requires a specific protocol state/precondition"}

# P221: reachability CLASS taxonomy — a DISPLAY/EVIDENCE label, decoupled from the attacker_model severity enum.
# Gives trusted-system / TSS-gated paths an honest bucket instead of collapsing the card to 'unknown'. An explicit
# reachability_class in the L3 record overrides this map (e.g. privileged_only via a TSS/cross-chain gate ->
# TRUSTED_SYSTEM_ACTOR_REACHABLE). It NEVER feeds decide() (severity keys off attacker_model only).
_REACH_CLASS = {"permissionless": "UNPRIVILEGED_REACHABLE",
                "program_accepted": "PROGRAM_ACCEPTED_ACTOR_REACHABLE",
                "privileged_only": "PRIVILEGED_ONLY_REACHABLE",
                "privileged": "PRIVILEGED_ONLY_REACHABLE",
                "trusted_admin": "PRIVILEGED_ONLY_REACHABLE",
                "compromise_required": "COMPROMISE_REQUIRED"}

_VERDICT_TO_CONV = {"HIT": "CLEAN_HIT", "PARTIAL": "STRONG_PARTIAL", "ADJACENT": "ADJACENT",
                    "TRUE_NEGATIVE": "REJECTED", "REJECTED": "REJECTED", "MISS": "NONE"}


# ----------------------------------------------------------------- source adapters
# A source adapter supplies ONLY the source-specific bits (subject, record_id prefix, scorecard file names,
# per-candidate register-shape normalization). The shared core (index loaders, build_bundle, to_synced_finding,
# CARD_INJECT, upsert/merge, atomic write) is source-agnostic. The "zeta" adapter reproduces the original P217
# behavior BYTE-FOR-BYTE so existing ZetaChain output never changes.
def _norm_identity(c):
    return c


def _norm_size_credit(c):
    """Map a P223 Size Credit register candidate into the shape build_bundle expects.

    P223 CANDIDATE_REGISTER.json records `id, severity_ceiling, cluster, title, file, function, attacker_model,
    confidence, needs_harness` — no `contract` / `claimed_severity`. Derive contract from the .sol basename and
    carry the severity ceiling as the claimed severity (recorded-only; never the synced severity_recommendation,
    which to_synced_finding pulls from triage/L3)."""
    c = dict(c)
    f = str(c.get("file") or "")
    if not c.get("contract") and f:
        c["contract"] = Path(f).stem
    if not c.get("claimed_severity") and c.get("severity_ceiling"):
        c["claimed_severity"] = c["severity_ceiling"]
    # P225: make the source ref REPO-RELATIVE so evidence_backup.source resolves on disk (register `file` is
    # contract-tree-relative, e.g. "contracts/libraries/actions/Deposit.sol"). No invention — same real file.
    _base = "audits/size-credit-2024-06-blind/contracts/2024-06-size"
    if f and not f.startswith("audits/") and (ROOT / _base / f).exists():
        c["file"] = f"{_base}/{f}"
    return c


ADAPTERS = {
    # rid_prefix: the record_id namespace; main()'s merge keys off f"{rid_prefix}:{phase}:" so a re-sync of one
    # source upserts only its own records and PRESERVES every other source's records.
    "zeta": {
        "rid_prefix": "zetachain-2023-10",
        "subject": lambda audit, phase: f"ZetaChain 2023-10 ({phase})",
        "scorecard_name": "ANSWER_KEY_SCORECARD.md",
        "scorecard_extra": ["FINDING_MATCHES.md", "SEVERITY_CALIBRATION.md"],
        "normalize": _norm_identity,
    },
    "size_credit": {
        "rid_prefix": "size-credit-2024-06-blind",
        "subject": lambda audit, phase: f"Size Credit 2024-06 ({phase})",
        "scorecard_name": "SCORING.md",
        "scorecard_extra": [],
        "normalize": _norm_size_credit,
    },
}


def resolve_adapter(name, audit):
    """Pick the adapter by explicit name, else auto-detect from the audit id (default zeta for byte-compat)."""
    if name and name in ADAPTERS:
        return name, ADAPTERS[name]
    if name and name not in ADAPTERS:
        raise SystemExit(f"[sync_hunt_findings] unknown --source-adapter '{name}' (known: {sorted(ADAPTERS)})")
    a = str(audit or "")
    if "zetachain" in a:
        return "zeta", ADAPTERS["zeta"]
    if "size-credit" in a:
        return "size_credit", ADAPTERS["size_credit"]
    return "zeta", ADAPTERS["zeta"]


def diff_records(old_findings, new_findings):
    """Compare two findings lists by record_id. Returns {added, updated, deleted, unchanged} record-id lists.
    'updated' = same record_id, different content; 'deleted' = in old but not in new."""
    def _index(lst):
        return {r.get("record_id"): r for r in (lst or []) if isinstance(r, dict) and r.get("record_id")}
    o, n = _index(old_findings), _index(new_findings)
    added = sorted(k for k in n if k not in o)
    deleted = sorted(k for k in o if k not in n)
    updated = sorted(k for k in n if k in o and json.dumps(n[k], sort_keys=True) != json.dumps(o[k], sort_keys=True))
    unchanged = sorted(k for k in n if k in o and k not in updated)
    return {"added": added, "updated": updated, "deleted": deleted, "unchanged": unchanged}


def _file_md5(p):
    import hashlib
    try:
        return hashlib.md5(Path(p).read_bytes()).hexdigest()
    except Exception:
        return None


def atomic_write_with_backup(out: Path, text: str):
    """Write `text` to `out` atomically with a timestamped backup of the prior file.
    temp-file -> backup prior -> os.replace(temp, out). Returns the backup path (or None if no prior file)."""
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(out.suffix + ".tmp")
    tmp.write_text(text)
    bak = None
    if out.exists():
        bak = out.with_suffix(out.suffix + f".bak.{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}")
        shutil.copy(out, bak)
    os.replace(tmp, out)
    return str(bak) if bak else None


# ----------------------------------------------------------------- loaders
def _rel(p):
    """Path relative to ROOT for display; falls back to the absolute string for paths outside the repo (e.g. tmp)."""
    try:
        return str(Path(p).relative_to(ROOT))
    except Exception:
        return str(p)


def _read_json(p):
    try:
        return json.loads(Path(p).read_text())
    except Exception:
        return None


def _merged_index(audit):
    d = _read_json(ROOT / "audits" / audit / "output" / "merged_findings.json") or {}
    return {f.get("id"): f for f in d.get("findings", []) if isinstance(f, dict)}


def _triage_index(audit):
    idx = {}
    base = ROOT / "audits" / audit / "data" / "triage"
    for bucket in ("submit", "poc_required", "downgraded", "rejected", "merged"):
        f = base / f"{bucket}.jsonl"
        if f.exists():
            for line in f.read_text().splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    r = json.loads(line)
                    idx[r.get("finding_id")] = r
                except Exception:
                    pass
    return idx


def _confirm_index(audit):
    """{cid: reachability_status} from the confirm reachability analysis (artifact-backed attacker reachability)."""
    d = _read_json(ROOT / "audits" / audit / "output" / "confirm" / "reachability_analysis.json") or {}
    rows = d.get("results") if isinstance(d, dict) else (d if isinstance(d, list) else [])
    return {r.get("finding_id"): r for r in rows if isinstance(r, dict)}


_LOSS_TYPE = {"dos": "denial-of-service / availability", "griefing": "griefing / availability",
              "accounting": "accounting drift (no direct theft shown)", "theft": "asset loss",
              "access_control": "privileged-control / centralization", "cross_chain_auth": "cross-chain authenticity",
              "precision": "rounding/precision"}


def _scorecard_verdict(cid, files):
    """Best-effort, artifact-backed post-score extraction. Verdict (-> conversion) is taken ONLY from a primary
    mention (a FINDING_MATCHES `## <id> ...` header OR a bolded `**<id>**` cell); grouped/parenthetical mentions
    contribute only to the human-readable note, never to the conversion. Never fabricates."""
    tok = re.compile(r"\b(HIT|PARTIAL|ADJACENT|MISS|TRUE_NEGATIVE|WRONG_MECHANISM|SEVERITY_UNDER|SEVERITY_OVER|"
                     r"SEVERITY_MATCH|REJECTED|FALSE_POSITIVE)\b")
    idre = re.compile(r"\b" + re.escape(cid) + r"\b")
    primary_verdict, notes = None, []
    for fp in files:
        if not Path(fp).exists():
            continue
        for ln in Path(fp).read_text().splitlines():
            if not idre.search(ln):
                continue
            clean = ln.strip().strip("|").strip()
            if clean and clean not in notes:
                notes.append(re.sub(r"\s+", " ", clean)[:300])
            is_primary = ln.lstrip().startswith(f"## {cid}") or (f"**{cid}**" in ln)
            if is_primary and primary_verdict is None:
                m = tok.search(ln)
                if m:
                    primary_verdict = m.group(1)
    return {"verdict": primary_verdict, "note": (" | ".join(notes) if notes else None)}


def _l3_decide(l3rec):
    if not l3rec:
        return {}
    try:
        import validate_p208_l3_readiness as v
        saved = os.environ.get("AUDITWATCH_L3_READINESS")
        os.environ["AUDITWATCH_L3_READINESS"] = "1"
        try:
            return v.decide(l3rec)
        finally:
            if saved is None:
                os.environ.pop("AUDITWATCH_L3_READINESS", None)
            else:
                os.environ["AUDITWATCH_L3_READINESS"] = saved
    except Exception:
        return {}


# ----------------------------------------------------------------- bundle build
def _present(v):
    return v is not None and str(v).strip().lower() not in ("", "none", "n/a", "unknown")


def build_bundle(c, phase, audit, subject, merged_idx, triage_idx, l3_dir, drq_dir, scorecard_files, warnings,
                 confirm_idx=None,
                 rid_prefix="zetachain-2023-10",
                 register_rel="documentation/research/assisted_mode/p215_full_funnel_rehearsal/CANDIDATE_REGISTER.json",
                 scorecard_post_rel="documentation/research/assisted_mode/p215_full_funnel_rehearsal/ANSWER_KEY_SCORECARD.md",
                 adapter_name="zeta"):
    cid = c["id"]
    contract, function = c.get("contract"), c.get("function")
    merged = merged_idx.get(cid) or {}
    triage = triage_idx.get(cid) or {}
    l3rec = _read_json(Path(l3_dir) / f"{cid}.json") or {}
    ddec = _l3_decide(l3rec)
    drq = _read_json(Path(drq_dir) / f"{cid}.json") or {}
    sc = _scorecard_verdict(cid, scorecard_files)
    confirm = (confirm_idx or {}).get(cid) or {}
    # P219 HARD RULE: a field is populated only if it ties to a specific artifact PATH; else it stays
    # unknown/MISSING_EVIDENCE. prov[field] = artifact path it came from (post-score notes are NOT blind evidence).
    L3P = f"output_research/l3_readiness/{cid}.json"
    MP = f"audits/{audit}/output/merged_findings.json#{cid}"
    RP = f"{register_rel}#{cid}"
    TP = f"audits/{audit}/data/triage/*.jsonl#{cid}"
    CP = f"audits/{audit}/output/confirm/reachability_analysis.json#{cid}"
    PKG = f"audits/{audit}/output/submission_pack.md#{cid}"
    prov = {}

    def src(field, value, path):
        """Record provenance iff value is artifact-backed and present; return the value unchanged."""
        if _present(value) or (isinstance(value, (list, dict)) and value):
            prov[field] = {"path": path, "blind_evidence": True}
        return value

    for label, ok in (("merged_finding", bool(merged)), ("triage", bool(triage)), ("l3_record", bool(l3rec)),
                      ("dry_run_queue", bool(drq)), ("confirm", bool(confirm)), ("scorecard", bool(sc["note"]))):
        if not ok:
            warnings.append(f"{cid}: missing {label}")

    ice = merged.get("ice_chain") if isinstance(merged.get("ice_chain"), dict) else {}
    ite = merged.get("ite") if isinstance(merged.get("ite"), dict) else {}

    # exploit_steps ← merged.ice_chain.exploit_path (split). Provenance: merged_findings.
    exploit_steps = []
    ep = ice.get("exploit_path") or ""
    if _present(ep):
        exploit_steps = [s.strip() for s in re.split(r"\s*->\s*|\s*→\s*|(?<=[.;])\s+(?=[A-Z0-9])", ep) if s.strip()]
    src("exploit_steps", exploit_steps, MP)

    # defense_map ← recommended fix (triage follow_up_packet) / L3 control / merged.recommendation
    defense_src = triage.get("follow_up_packet") or l3rec.get("expected_delta_or_control") or merged.get("recommendation")
    defense_path = (TP if _present(triage.get("follow_up_packet")) else
                    (L3P if _present(l3rec.get("expected_delta_or_control")) else MP))
    defense_map = []
    if _present(defense_src) and str(defense_src).strip().lower() not in ("see triage", "(none)"):
        defense_map = [{"defense": str(defense_src)[:300], "location": f"{contract}.{function}",
                        "classification": "missing/insufficient (recommended fix)",
                        "source": defense_path,
                        "manual_check": "Does this guard run before the value/state movement, for all callers?"}]
        src("defense_map", defense_map, defense_path)

    # function_map ← register surface + impact_class role
    role = (c.get("impact_class") or merged.get("_impact_class") or "entrypoint")
    function_map = [{"role": role, "function": function or "unknown",
                     "permission": (c.get("attacker_model") or "unknown"),
                     "why_it_matters": (merged.get("description") or c.get("title") or "unknown")[:240],
                     "source_location": f"{c.get('file','?')}:{c.get('lines','?')}"}] if function else []
    src("function_map", function_map, RP)

    am_raw = c.get("attacker_model") or merged.get("_attacker_model")
    attacker_model = _ATTACKER.get(str(am_raw).lower(), am_raw) if _present(am_raw) else None
    src("attacker_model", attacker_model, RP)

    # attacker reachability_verdict ← confirm reachability analysis (artifact-backed), refined by attacker_model
    reach_status = confirm.get("reachability_status")
    reachability_verdict = None
    if am_raw == "permissionless":
        reachability_verdict = "unprivileged-reachable"
        src("reachability_verdict", reachability_verdict, RP)
    elif _present(reach_status):
        reachability_verdict = f"{reach_status} (confirm gate)"
        src("reachability_verdict", reachability_verdict, CP)

    # P221: reachability CLASS taxonomy (DISPLAY/EVIDENCE only — never feeds decide() severity, which keys off the
    # L3 attacker_model enum). Derived deterministically from the L3 attacker_model, overridable by an explicit
    # reachability_class in the L3 record (e.g. a TSS/cross-chain gate -> TRUSTED_SYSTEM_ACTOR_REACHABLE).
    l3_am = l3rec.get("attacker_model")
    reachability_class = None
    if _present(l3rec.get("reachability_class")):
        reachability_class = src("reachability_class", l3rec.get("reachability_class"), L3P)
    elif _present(l3_am):
        reachability_class = src("reachability_class", _REACH_CLASS.get(str(l3_am).lower(), "REACHABILITY_UNKNOWN"), L3P)
    elif _present(am_raw):
        reachability_class = src("reachability_class", _REACH_CLASS.get(str(am_raw).lower(), "REACHABILITY_UNKNOWN"), RP)
    # a richer L3-recorded reachability_verdict (artifact-backed) supersedes the coarse confirm-gate string
    if _present(l3rec.get("reachability_verdict")):
        reachability_verdict = src("reachability_verdict", l3rec.get("reachability_verdict"), L3P)

    # P221: structured attacker-reachability fields — populated ONLY from the L3 record (artifact). HARD RULE:
    # absent -> stays None (card renders 'unknown'); never derived/invented in code.
    privilege_required = src("privilege_required", l3rec.get("privilege_required") or None, L3P)
    victim_action_required = src("victim_action_required", l3rec.get("victim_action_required") or None, L3P)
    operator_or_keeper_dependency = src("operator_or_keeper_dependency", l3rec.get("operator_or_keeper_dependency") or None, L3P)
    self_remediation = src("self_remediation", l3rec.get("self_remediation") or None, L3P)
    attacker_controls = l3rec.get("attacker_controls") if isinstance(l3rec.get("attacker_controls"), list) and l3rec.get("attacker_controls") else None
    attacker_does_not_control = l3rec.get("attacker_does_not_control") if isinstance(l3rec.get("attacker_does_not_control"), list) and l3rec.get("attacker_does_not_control") else None
    src("attacker_controls", attacker_controls, L3P)
    src("attacker_does_not_control", attacker_does_not_control, L3P)

    # P222: impact_type — an artifact-backed classification over the already-PROVEN impact (NOT invented impact).
    # HARD RULE: only when the L3 record records it; absent -> the priority rule simply can't fire.
    impact_type = src("impact_type", l3rec.get("impact_type") or None, L3P)

    # conversion: primary scorecard verdict -> enum; else triage rejected -> REJECTED; else NONE
    conv = _VERDICT_TO_CONV.get(sc["verdict"] or "", None)
    if conv is None:
        conv = "REJECTED" if triage.get("triage_status") == "rejected" else "NONE"
    conv_class = sc["verdict"] or conv

    # PoC verification ← L3 record (actual / expected / control / value-delta). HARD RULE: only when L3 records them.
    poc_status = "REPRODUCED" if (l3rec.get("l3_status") == "PASS" and _present(l3rec.get("poc_path"))) else "NOT_STARTED"
    actual = l3rec.get("actual_delta") or (l3rec.get("poc_result") if poc_status == "REPRODUCED" else None)
    control = l3rec.get("expected_delta_or_control")
    value_delta = l3rec.get("magnitude_basis")
    vulnerable_output = actual if _present(actual) else None
    control_case = control if _present(control) else None
    corrected_output = control if _present(control) else None          # expected = the control's expected outcome
    runtime_delta = value_delta if _present(value_delta) else None
    corrected_reference_type = l3rec.get("dependency_mocks") if _present(l3rec.get("dependency_mocks")) else None
    src("vulnerable_output", vulnerable_output, L3P)
    src("control_case", control_case, L3P)
    src("runtime_delta", runtime_delta, L3P)
    src("corrected_reference_type", corrected_reference_type, L3P)

    # impact ← L3 (who-loses / asset) + impact_class loss-type. who_gains stays unknown unless an artifact states one.
    who_loses = l3rec.get("victim_or_protocol_loss") if _present(l3rec.get("victim_or_protocol_loss")) else None
    asset_or_value = l3rec.get("affected_asset_or_state") if _present(l3rec.get("affected_asset_or_state")) else None
    loss_type = _LOSS_TYPE.get(str(c.get("impact_class") or merged.get("_impact_class")).lower())
    who_gains = None  # no Zeta artifact names a beneficiary (DoS/availability/centralization) -> unknown, not invented
    src("who_loses", who_loses, L3P)
    src("asset_or_value", asset_or_value, L3P)
    src("loss_type", loss_type, RP)

    # red flags — status ONLY from recorded fields (else manual); never fabricated. Each cites its evidence.
    rf = []
    if _present(am_raw):
        st = "pass" if am_raw == "permissionless" else ("fail" if am_raw == "privileged" else "manual")
        rf.append({"check": "PoC calls an admin-only function as the attacker", "status": st,
                   "evidence": f"attacker_model={am_raw} ({RP})"})
    rf.append({"check": "Realized impact proven by an executed PoC",
               "status": ("pass" if poc_status == "REPRODUCED" else "manual"),
               "evidence": f"l3_status={l3rec.get('l3_status', 'unknown')} ({L3P})"})
    rf.append({"check": "Control / expected-vs-actual present",
               "status": ("pass" if _present(control) else "manual"),
               "evidence": (control or "not recorded") + f" ({L3P})"})
    rf.append({"check": "Production source unmodified in the harness",
               "status": ("pass" if l3rec.get("production_source_modified") is False else "manual"),
               "evidence": f"production_source_modified={l3rec.get('production_source_modified')} ({L3P})"})
    rf.append({"check": "Attacker reachability confirmed",
               "status": ("pass" if am_raw == "permissionless" else "manual"),
               "evidence": f"reachability={reachability_verdict or 'unknown'} ({CP if reach_status else RP})"})
    src("red_flags", rf, L3P)

    intent = None
    if am_raw == "privileged":
        intent = "operator/admin-dependent: impact requires a trusted-role action (centralization/by-design boundary to check)"
        src("intent_scope_operator_assumptions", intent, RP)
    elif _present(triage.get("decision_reason")):
        intent = triage.get("decision_reason")
        src("intent_scope_operator_assumptions", intent, TP)

    summary = merged.get("impact") or ice.get("impact") or merged.get("description") or c.get("title")
    src("summary", summary, MP if (merged.get("impact") or ice.get("impact") or merged.get("description")) else RP)
    src("title", c.get("title"), RP)
    src("mechanism", merged.get("description") or c.get("title"), MP if merged.get("description") else RP)
    src("root_cause", ite.get("intent") or l3rec.get("source_validity_notes"),
        MP if ite.get("intent") else (L3P if l3rec.get("source_validity_notes") else None))
    src("limitations", l3rec.get("source_validity_notes"), L3P)

    # report package as an evidence artifact (present iff the candidate is in the pack)
    pkg_present = (ROOT / "audits" / audit / "output" / "submission_pack.md").exists() and \
        cid in ((ROOT / "audits" / audit / "output" / "submission_pack.md").read_text() if
                (ROOT / "audits" / audit / "output" / "submission_pack.md").exists() else "")

    src_refs = {k: v for k, v in {
        "candidate_register": register_rel,
        "source": f"{c.get('file')}:{c.get('lines')}" if c.get("file") else None,
        "merged_finding": MP,
        "confirm_gate": CP if confirm else None,
        "l3_record": L3P if l3rec else None,
        "harness": l3rec.get("poc_path") or None,
        "report_package": PKG if pkg_present else None,
        "dry_run_queue": f"output_research/dry_run_submission_queue/{cid}.json" if drq else None,
        "scorecard_post_score": scorecard_post_rel,
    }.items() if v}
    evidence_backup = [{"label": k, "path": v} for k, v in src_refs.items()]
    src("evidence_backup", evidence_backup, RP)
    src("affected_contracts", [contract] if contract else [], RP)
    src("affected_functions", [function] if function else [], RP)
    src("dry_run_queue", drq.get("readiness_state"), f"output_research/dry_run_submission_queue/{cid}.json" if drq else None)
    if _present(l3rec.get("l3_status")):
        prov["l3_status"] = {"path": L3P, "blind_evidence": True}

    # P222: human-review priority (DISPLAY/PRIORITIZATION only — separate namespace from attacker_model/severity;
    # never sets submission_ready/routing_allowed/high_promotion_allowed). Derived purely from already-recorded
    # display/evidence fields. The 'impact_type' input is artifact-backed (L3 record); absent -> rule can't fire.
    prio = hrp.evaluate_priority({
        "l3_status": l3rec.get("l3_status"),
        "impact_type": impact_type,
        "reachability_class": reachability_class,
        "conversion_outcome": conv,
        "dependency_mocks": l3rec.get("dependency_mocks"),
        "source_validity_notes": l3rec.get("source_validity_notes"),
        "scoring_note": sc["note"],
        "high_promotion_blocker": ddec.get("high_promotion_blocker"),
    })
    human_review_priority = prio["human_review_priority"]
    human_review_reason_codes = prio["human_review_reason_codes"]
    priority_explanation = prio["priority_explanation"]
    priority_blockers = prio["priority_blockers"]
    should_surface_above_noise = prio["should_surface_above_noise"]
    # provenance: the priority is a deterministic classification over L3-recorded evidence
    src("human_review_priority", human_review_priority if human_review_priority != "NONE" else None, L3P)
    src("impact_type", impact_type, L3P)

    return {
        "candidate_id": cid,
        "record_id": f"{rid_prefix}:{phase}:{cid}:{contract}.{function}",
        "source_track": "audit_workspace",
        "source_adapter": adapter_name,
        "source_family": adapter_name,
        "audit_id": audit,
        "subject": subject, "phase_discovered": phase,
        "contract": contract, "function": function,
        "title": c.get("title"),
        "summary": summary,
        "mechanism": merged.get("description") or c.get("title"),
        "suspected_mechanism": merged.get("description") or c.get("title"),
        "root_cause": ite.get("intent") or l3rec.get("source_validity_notes"),
        "attacker_model": attacker_model,
        "exploit_steps": exploit_steps,
        "function_map": function_map,
        "defense_map": defense_map,
        "impact": summary,
        "vulnerable_output": vulnerable_output,
        "corrected_output": corrected_output,
        "control_case": control_case,
        "runtime_delta": runtime_delta,
        "corrected_reference_type": corrected_reference_type,
        "who_loses": who_loses, "who_gains": who_gains,
        "asset_or_value": asset_or_value, "loss_type": loss_type,
        "limitations": l3rec.get("source_validity_notes"),
        "intent_scope_operator_assumptions": intent,
        "novelty_status": "unknown",
        "conversion": conv,
        "conversion_classification": conv_class,
        "mechanism_correctness": ("partial" if conv == "STRONG_PARTIAL" else ("refuted" if conv == "REJECTED" else "correct")),
        "claimed_severity": c.get("claimed_severity"),
        "blocker_reason": (ddec.get("high_promotion_blocker") if c.get("claimed_severity") in ("High", "Critical") else None),
        "triage": {"recommended_severity": triage.get("recommended_severity"),
                   "triage_status": triage.get("triage_status"),
                   "decision_reason": triage.get("decision_reason")},
        "l3": {"l3_status": l3rec.get("l3_status"),
               "high_promotion_allowed": ddec.get("high_promotion_allowed"),
               "high_promotion_blocker": ddec.get("high_promotion_blocker"),
               "calibrated_severity_after_l3": ddec.get("calibrated_severity")},
        "poc": {"poc_status": poc_status, "test_file": l3rec.get("poc_path"),
                "test_command": l3rec.get("poc_command"), "vulnerable_result": l3rec.get("poc_result")},
        # P226-C: surface the L3 executed-PoC facts the card's poc_verification checklist reads, so a funnel
        # card with an L3 PASS shows uses_real_contract / production_source_unchanged / harness_isolated_unwired
        # as real values instead of MISSING_EVIDENCE (artifact-derived from the L3 record; no fabrication).
        "real_contract_deployed": (True if "REAL" in str(l3rec.get("poc_tier") or "").upper() else None),
        "production_source_modified": l3rec.get("production_source_modified"),
        "harness_path": (l3rec.get("poc_path") if _present(l3rec.get("poc_path")) else None),
        "dry_run_queue": {"readiness_state": drq.get("readiness_state")} if drq else {},
        "red_flags": rf,
        "source_false": conv == "REJECTED",
        "source_refs": src_refs,
        "evidence_backup": evidence_backup,
        "reachability_verdict": reachability_verdict,
        "reachability_class": reachability_class,
        "privilege_required": privilege_required,
        "victim_action_required": victim_action_required,
        "operator_or_keeper_dependency": operator_or_keeper_dependency,
        "self_remediation": self_remediation,
        "attacker_controls": attacker_controls,
        "attacker_does_not_control": attacker_does_not_control,
        # P222: human-review priority lane (display/prioritization only; never routes/submits/moves severity)
        "impact_type": impact_type,
        "human_review_priority": human_review_priority,
        "human_review_reason_codes": human_review_reason_codes,
        "priority_explanation": priority_explanation,
        "priority_blockers": priority_blockers,
        "should_surface_above_noise": should_surface_above_noise,
        # post-score answer-key verdict is kept ONLY here, never fed into blind evidence fields above
        "last_reviewer_note": sc["note"],
        "scoring_note": sc["note"],
        "_field_provenance": prov,
    }


# ----------------------------------------------------------------- completeness
def score_record(rec):
    pop = unk = miss = 0
    for f in EVIDENCE_FIELDS:
        v = rec.get(f)
        if isinstance(v, str) and v.strip().upper() == "MISSING_EVIDENCE":
            miss += 1
        elif isinstance(v, list) and v and all(str(x).strip().upper() == "MISSING_EVIDENCE" for x in v):
            miss += 1
        elif isinstance(v, str) and v.strip().lower() in ("", "unknown", "none", "n/a"):
            unk += 1
        elif v is None or (isinstance(v, (list, dict)) and len(v) == 0):
            unk += 1
        else:
            pop += 1
    return {"populated": pop, "unknown": unk, "missing": miss, "total": len(EVIDENCE_FIELDS),
            "pct": round(100 * pop / len(EVIDENCE_FIELDS))}


SAFETY = [("research_only", True), ("review_only", True), ("routes_in_production", False), ("routing_allowed", False),
          ("submission_ready", False), ("no_submit_controls", True), ("browser_computes_severity", False),
          ("human_review_required", True)]


def safety_ok(rec):
    if not all(rec.get(k) is want for k, want in SAFETY):
        return False
    return ds._present(rec.get("canonical_submission_ready_source")) if hasattr(ds, "_present") else bool(rec.get("canonical_submission_ready_source"))


def _validate_mirror_doc(doc, emitted_cids, prefix):
    """Validate the PROPOSED mirror doc before any disk write. Returns a list of hard error strings ([] = OK).

    Checks: schema shape; no duplicate record_id / candidate_id; per-record ds.validate_synced + safety_ok;
    and on the records emitted by THIS run (record_id starts with `prefix`): required fields present
    (candidate_id, audit_id, source_adapter/source_family, a severity field, a readiness field, sync metadata),
    L3 fields populated-or-explicit-unknown, submission readiness populated-or-explicit-not_reviewed.
    Preserved records from other sources are checked for schema/safety only (never retroactively failed)."""
    errs = []
    if not isinstance(doc, dict) or doc.get("schema_version") != "synced-1":
        errs.append("schema_version != 'synced-1'")
    findings = doc.get("findings") if isinstance(doc, dict) else None
    if not isinstance(findings, list):
        return errs + ["findings is not a list"]

    seen_rid, seen_cid = {}, {}
    for r in findings:
        if not isinstance(r, dict):
            errs.append("non-dict record in findings"); continue
        rid = r.get("record_id")
        cid = r.get("candidate_id")
        if rid in seen_rid:
            errs.append(f"duplicate record_id: {rid}")
        seen_rid[rid] = True
        if cid in seen_cid:
            errs.append(f"duplicate candidate_id: {cid}")
        seen_cid[cid] = True
        verrs = ds.validate_synced(r)
        if verrs:
            errs.append(f"{cid}: schema invalid: {verrs[:3]}")
        if not safety_ok(r):
            errs.append(f"{cid}: unsafe flags")
        # strict required-field checks ONLY on this run's emitted records
        if isinstance(rid, str) and rid.startswith(prefix):
            for f in ("candidate_id", "audit_id", "source_adapter", "source_family"):
                if not _present(r.get(f)):
                    errs.append(f"{cid}: missing required field '{f}'")
            if "severity_recommendation" not in r:
                errs.append(f"{cid}: missing severity field")
            if "readiness_state" not in r and not isinstance(r.get("dry_run_queue"), dict):
                errs.append(f"{cid}: missing readiness field")
            if "l3_status" not in r:
                errs.append(f"{cid}: L3 field neither populated nor explicit-unknown")
            sub = r.get("submission") if isinstance(r.get("submission"), dict) else {}
            if "submission_status" not in sub:
                errs.append(f"{cid}: submission readiness neither populated nor not_reviewed")
    return errs


def _unresolved_artifacts(records, prefix):
    """Return [(record_id, path)] for repo-relative artifact paths referenced by THIS run's records that do not
    exist on disk. Glob patterns (containing '*') and external/non-repo paths are skipped. Non-fatal: surfaced so
    missing artifacts are EXPLICITLY recorded rather than silently omitted."""
    out = []
    for r in records:
        rid = r.get("record_id", "")
        if not (isinstance(rid, str) and rid.startswith(prefix)):
            continue
        refs = r.get("source_refs") if isinstance(r.get("source_refs"), dict) else {}
        for _label, val in refs.items():
            if not isinstance(val, str) or not val:
                continue
            p = val.split("#", 1)[0].split(":")[0].strip()  # strip #frag and :line
            if not p or "*" in p or p.startswith(("http://", "https://")):
                continue
            cand = ROOT / p
            if not cand.exists():
                out.append((rid, val))
    return out


# ----------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description="P217 per-hunt dashboard sync wrapper")
    ap.add_argument("--phase", required=True)
    ap.add_argument("--audit", required=True)
    ap.add_argument("--workspace", required=True)
    ap.add_argument("--candidate-register", default=None)
    ap.add_argument("--l3-dir", default="output_research/l3_readiness")
    ap.add_argument("--dry-run-queue", default="output_research/dry_run_submission_queue")
    ap.add_argument("--scorecard", default=None)
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--replace-phase-records", action="store_true")
    ap.add_argument("--source-adapter", default=None,
                    help="source adapter (zeta|size_credit); auto-detected from --audit if omitted")
    ap.add_argument("--allow-delete", action="store_true",
                    help="permit record deletions (default: hard-fail if the write would delete any record)")
    ap.add_argument("--summary-out", default=None,
                    help="optional path to write a machine-readable sync summary JSON")
    args = ap.parse_args(argv)

    adapter_name, adapter = resolve_adapter(args.source_adapter, args.audit)

    ws = ROOT / args.workspace
    reg_path = Path(args.candidate_register) if args.candidate_register else ws / "CANDIDATE_REGISTER.json"
    scorecard = Path(args.scorecard) if args.scorecard else ws / adapter["scorecard_name"]
    scorecard_files = [scorecard] + [ws / n for n in adapter["scorecard_extra"]]
    out = Path(args.out)
    subject = adapter["subject"](args.audit, args.phase)
    prefix = f"{adapter['rid_prefix']}:{args.phase}:"
    register_rel = _rel(reg_path)
    scorecard_post_rel = _rel(scorecard)

    reg = _read_json(reg_path) or {}
    cands = [adapter["normalize"](c) for c in reg.get("candidates", [])]
    if not cands:
        print(f"[abort] no candidates in {reg_path}")
        return 2
    merged_idx = _merged_index(args.audit)
    triage_idx = _triage_index(args.audit)
    confirm_idx = _confirm_index(args.audit)

    # card-consumed raw fields the detail renderer reads directly (build_verifier_evidence); injected onto the synced
    # record after to_synced_finding so dashboard_sync.py stays unchanged.
    CARD_INJECT = ["vulnerable_output", "corrected_output", "control_case", "runtime_delta", "corrected_reference_type",
                   "reachability_verdict", "who_loses", "who_gains", "asset_or_value", "loss_type",
                   "reachability_class", "privilege_required", "victim_action_required", "operator_or_keeper_dependency",
                   "self_remediation", "attacker_controls", "attacker_does_not_control",
                   "impact_type", "human_review_priority", "human_review_reason_codes", "priority_explanation",
                   "priority_blockers", "should_surface_above_noise",
                   "scoring_note", "_field_provenance",
                   # multi-source identity (P224): rides onto the record so the dashboard can show source/adapter
                   "source_adapter", "source_family", "audit_id",
                   # P226-C: L3 executed-PoC facts for the card's poc_verification checklist
                   "real_contract_deployed", "production_source_modified", "harness_path"]

    warnings, records, problems, comp = [], [], [], []
    for c in cands:
        b = build_bundle(c, args.phase, args.audit, subject, merged_idx, triage_idx,
                         args.l3_dir, args.dry_run_queue, scorecard_files, warnings, confirm_idx=confirm_idx,
                         rid_prefix=adapter["rid_prefix"], register_rel=register_rel,
                         scorecard_post_rel=scorecard_post_rel, adapter_name=adapter_name)
        rec = ds.to_synced_finding(b)
        for k in CARD_INJECT:                       # P219: surface card-consumed fields + provenance top-level
            if b.get(k) is not None:
                rec[k] = b[k]
        errs = ds.validate_synced(rec)
        if errs or not safety_ok(rec):
            problems.append((c["id"], errs or ["safety_ok=false"]))
        records.append(rec)
        comp.append((c["id"], score_record(rec)))

    agg_pop = sum(s["populated"] for _, s in comp)
    agg_tot = sum(s["total"] for _, s in comp)
    print(f"[sync_hunt_findings] phase={args.phase} audit={args.audit} candidates={len(records)}")
    print(f"  field completeness: {agg_pop}/{agg_tot} = {round(100*agg_pop/agg_tot)}%")
    for cid, s in comp:
        print(f"    {cid}: {s['populated']}/{s['total']} ({s['pct']}%) unknown={s['unknown']} missing={s['missing']}")
    if warnings:
        print(f"  missing-artifact warnings ({len(warnings)}): " + "; ".join(warnings[:12]) + (" …" if len(warnings) > 12 else ""))
    print(f"  safety validation: {'PASS' if not problems else 'FAIL'}")
    if problems:
        for cid, e in problems:
            print(f"    BAD {cid}: {e}")
        if args.strict:
            print("[strict] refusing to write due to validation failures")
            return 1

    # existing mirror
    existing = _read_json(out) if out.exists() else None
    others = []
    if isinstance(existing, dict):
        for r in existing.get("findings", []):
            if not isinstance(r, dict):
                continue
            rid = str(r.get("record_id", ""))
            if rid.startswith(prefix):
                if args.replace_phase_records:
                    continue  # drop all phase records; re-add only current emit
                # else: will be overwritten by upsert below if same id, kept otherwise
                continue
            others.append(r)
    # upsert: current emit replaces same-id; others preserved
    new_ids = {r["record_id"] for r in records}
    merged_out = [r for r in others if r.get("record_id") not in new_ids] + records
    # de-dup (last wins)
    seen, dedup = set(), []
    for r in reversed(merged_out):
        if r.get("record_id") in seen:
            continue
        seen.add(r.get("record_id"))
        dedup.append(r)
    dedup.reverse()

    doc = {"schema_version": "synced-1", "generated_by": "scripts/sync_hunt_findings.py (P217)",
           "research_only": True, "review_only": True, "routes_in_production": False, "is_gate": False,
           "note": "Read-only generated mirror. Merged additively by funnel.load_records(). No record routes/submits; "
                   "canonical submission_ready stays machine-owned.",
           "findings": dedup}

    # ---- diff summary (added / updated / deleted) vs the existing mirror ----
    old_findings = (existing or {}).get("findings", []) if isinstance(existing, dict) else []
    diff = diff_records(old_findings, dedup)
    new_text = json.dumps(doc, indent=1) + "\n"

    # ---- pre-write validation of the proposed mirror (before touching disk) ----
    pre_errs = _validate_mirror_doc(doc, [c["id"] for c in cands], prefix)
    unresolved = _unresolved_artifacts(records, prefix)

    summary = {
        "phase": args.phase, "audit": args.audit, "adapter": adapter_name,
        "out": _rel(out), "candidates_emitted": len(records),
        "added": diff["added"], "updated": diff["updated"], "deleted": diff["deleted"],
        "preserved": diff["unchanged"],
        "added_count": len(diff["added"]), "updated_count": len(diff["updated"]),
        "deleted_count": len(diff["deleted"]), "preserved_count": len(diff["unchanged"]),
        "total_records": len(dedup),
        "hash_before": _file_md5(out), "hash_after": None, "backup_path": None,
        "validation_errors": pre_errs, "safety_problems": [cid for cid, _ in problems],
        "unresolved_artifacts": [{"record_id": rid, "path": p} for rid, p in unresolved],
        "dry_run": bool(args.dry_run or not args.write), "wrote": False,
    }
    if unresolved:
        print(f"  unresolved artifact paths ({len(unresolved)}): "
              + "; ".join(f"{rid}:{p}" for rid, p in unresolved[:6]) + (" …" if len(unresolved) > 6 else ""))
    print(f"  diff: +{len(diff['added'])} added / ~{len(diff['updated'])} updated / "
          f"-{len(diff['deleted'])} deleted / ={len(diff['unchanged'])} preserved (total {len(dedup)})")

    # ---- deletion guard: refuse to drop any existing record unless explicitly allowed ----
    if diff["deleted"] and not args.allow_delete:
        print(f"[abort] write would DELETE {len(diff['deleted'])} existing record(s): {diff['deleted'][:12]}"
              + (" …" if len(diff['deleted']) > 12 else ""))
        print("        refusing (mirror left unchanged). Pass --allow-delete only if this is intentional.")
        if args.summary_out:
            atomic_write_with_backup(Path(args.summary_out), json.dumps(summary, indent=2) + "\n")
        return 3

    if pre_errs and args.strict:
        print(f"[strict] proposed mirror failed validation ({len(pre_errs)} error(s)); refusing to write:")
        for e in pre_errs[:12]:
            print(f"    {e}")
        if args.summary_out:
            atomic_write_with_backup(Path(args.summary_out), json.dumps(summary, indent=2) + "\n")
        return 1

    if args.dry_run or not args.write:
        print(f"  [dry-run] would write {len(records)} record(s) (total {len(dedup)}) to {_rel(out)} — NOTHING WRITTEN")
        if args.summary_out:
            atomic_write_with_backup(Path(args.summary_out), json.dumps(summary, indent=2) + "\n")
        return 0 if not (problems or pre_errs) else 1

    # ---- atomic write: temp -> backup prior -> os.replace ----
    backup = atomic_write_with_backup(out, new_text)
    summary["wrote"] = True
    summary["backup_path"] = backup
    summary["hash_after"] = _file_md5(out)
    print(f"  [write] emitted {len(records)} (+{len(diff['added'])} new / ~{len(diff['updated'])} updated); "
          f"total {len(dedup)} → {_rel(out)}")
    print(f"  backup: {backup}")
    if args.summary_out:
        atomic_write_with_backup(Path(args.summary_out), json.dumps(summary, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
