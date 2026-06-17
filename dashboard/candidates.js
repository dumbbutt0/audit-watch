/* Candidate Validation review surface — READ-ONLY.
   Reads /api/candidates + /api/candidate; renders the full validation packet (sections A–N).
   Never writes/promotes/generates. Separates the 4 confidences. POC_READY shown as "local PoC task allowed" only.
*/
"use strict";

const GROUP_ORDER = ["POC_READY", "REPORT_READY", "VALIDATION_READY", "PARTIAL", "CONTEXT_MAPPED",
                     "RAW/NEEDS_CONTEXT", "KILLED"];
const GROUP_LABEL = {
  "POC_READY": "POC_READY — local PoC task allowed", "REPORT_READY": "REPORT_READY",
  "VALIDATION_READY": "VALIDATION_READY", "PARTIAL": "PARTIAL", "CONTEXT_MAPPED": "CONTEXT_MAPPED / in-progress",
  "RAW/NEEDS_CONTEXT": "RAW / NEEDS_CONTEXT", "KILLED": "KILLED",
};
const WSL_DISTRO = "Ubuntu";
const state = { rows: [], selected: null, fTrack: "", fText: "" };

const $ = (id) => document.getElementById(id);
const esc = (s) => String(s == null ? "" : s).replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
const toast = (m) => { const t = $("toast"); t.textContent = m; t.className = "toast show"; setTimeout(() => (t.className = "toast"), 2400); };
async function api(p) { const r = await fetch(p); if (!r.ok) { let d=""; try{d=(await r.json()).detail;}catch(e){} throw new Error(d || r.status); } return r.json(); }
async function apiPost(p, body) { const r = await fetch(p, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }); let j={}; try{j=await r.json();}catch(e){} if (!r.ok) throw new Error(j.detail || r.status); return j; }

/* -------- classified-status tokens (display hint; the verifier emits these for blank fields) -------- */
const STATUS_TOKENS = { MISSING_EVIDENCE: 1, HUMAN_PENDING: 1, NOT_APPLICABLE: 1, SOURCE_REFUTED: 1, INCOMPLETE_EVIDENCE: 1, PENDING: 1, EXTRACTED: 1 };
function decorateStatusTokens(root) {
  if (!root) return;
  root.querySelectorAll(".kv .v, td.src, .vlist li, p.muted").forEach((el) => {
    const t = (el.textContent || "").trim();
    if (STATUS_TOKENS[t]) el.classList.add("tok", "tok-" + t);
  });
}

/* -------- submission readiness overlay (human-owned note; never submits/routes/changes the finding) -------- */
function readinessBadge(s) {
  if (!s || s === "not_reviewed") return "";
  const cls = s === "ready_for_submission_package" ? "rdy-ok" : (s.startsWith("blocked") ? "rdy-block" : "rdy-warn");
  return `<span class="rbadge ${cls}">${esc(s)}</span>`;
}
function renderReadinessSection(d) {
  const rd = d.readiness || {}, st = rd.readiness_state || "not_reviewed";
  const ve = d.verifier_evidence || {}, cv = ve.conversion || {}, rs = ve.report_summary || {};
  const ec = ve.evidence_completeness || {};
  // derived, display-only packaging status (separate concept from the canonical submission_ready flag)
  const pkgStatus = rd.submission_package_status || "NOT_REVIEWED";
  const pkgCls = pkgStatus === "SUBMISSION_READY" ? "rdy-ok"
              : (pkgStatus.startsWith("BLOCKED") || pkgStatus === "NOT_READY") ? "rdy-block" : "rdy-warn";
  let h = `<h2 class="sec">Submission Readiness Checklist</h2>`;
  h += `<div class="safetycopy">Readiness review is a human packaging note. "Submission package status" is a derived human label; the canonical <code>submission_ready</code> flag is machine-owned and is never flipped by this review (it stays false until the submission gate passes).</div>`;
  if (ec.status === "INCOMPLETE_EVIDENCE") {
    h += `<div class="banner ill">⚠ INCOMPLETE_EVIDENCE — missing before human submission review: ${esc((ec.missing || []).join(", "))}</div>`;
  }
  // (P225) three DECOUPLED axes: card completeness ≠ evidence sufficiency ≠ submission readiness.
  const cc = ec.card_completeness || {}, es = ec.evidence_sufficiency || {}, sr = ec.submission_readiness || {};
  if (es.status === "WARNING_LOW_EVIDENCE_DEPTH") {
    h += `<div class="banner ill">⚠ WARNING_LOW_EVIDENCE_DEPTH — only ${es.pct_artifact_backed}% of evidence-bearing fields are artifact-backed (threshold ${es.threshold_pct}%); the rest are honest placeholders. Not fabricated, not blocking — this card needs more real proof before submission.</div>`;
  }
  if (cc.status || es.status || sr.status) {
    h += kv("card completeness", `${cc.status || "—"}${cc.total_fields ? ` (${cc.total_fields} fields, all answered)` : ""}`) +
         kv("evidence sufficiency", `${es.status || "—"}${es.pct_artifact_backed != null ? ` — ${es.artifact_backed} artifact / ${es.placeholder} placeholder / ${es.human_pending} human-pending (${es.pct_artifact_backed}% real)` : ""}`) +
         kv("submission readiness (independent)", sr.status || "—");
  }
  if (ec.disclaimer) {
    h += `<div class="safetycopy">${esc(ec.disclaimer)}</div>`;
  }
  // severity must come from the validated verifier field (never the conversion/decision label).
  h += kv("conversion outcome", d.conversion_outcome || cv.conversion_outcome || "—") +
       kv("severity recommendation", rs.severity_recommendation || "—") +
       kv("novelty status", rs.novelty_status || cv.novelty_clear || "—") +
       `<div class="kv"><div class="k">submission package status (derived)</div><div class="v"><span class="rbadge ${pkgCls}">${esc(pkgStatus)}</span></div></div>` +
       kv("canonical submission_ready", String(d.submission_ready)) +
       kv("routing_allowed", String(d.routing_allowed)) +
       `<div class="kv"><div class="k">readiness_state</div><div class="v">${readinessBadge(st) || esc(st)}</div></div>` +
       kv("last reviewer note", (rd.last_note || "—"));
  h += `<button class="btn ghost" id="rdReviewBtn">Review submission readiness</button>`;
  h += `<div id="rdPanel" style="display:none;margin-top:8px"></div>`;
  return h;
}
function _rsel(id, label, opts, cur) {
  return `<div class="kv"><div class="k">${esc(label)}</div><div class="v"><select id="${id}">` +
    opts.map((o) => `<option${cur===o?" selected":""}>${esc(o)}</option>`).join("") + `</select></div></div>`;
}
function readinessPanelHtml() {
  const yn = ["", "yes", "no", "unknown"];
  return `<div class="notice">Required-for-ready answers are enforced server-side against the canonical finding facts; a "ready" decision is rejected (with reasons) if any gate fails.</div>` +
    _rsel("rq1", "1. Mechanism confirmed?", yn) +
    _rsel("rq2", "2. Attacker reachability confirmed (production flow)?", yn) +
    _rsel("rq3", "3. Severity-bearing impact shown?", yn) +
    _rsel("rq4", "4. PoC evidence complete (real contract, actual vs expected, control, command/result)?", yn) +
    _rsel("rq5", "5. Impact wording not overclaimed (no 'drain' if redistribution; no High if Low/QA)?", yn) +
    _rsel("rq6", "6. Severity recommendation chosen?", ["", "High", "Medium", "Low", "QA", "no_security_impact", "unknown"]) +
    _rsel("rq7", "7. Scope caveats reviewed (keeper/operator, privileged, intent, accepted design)?", yn) +
    _rsel("rq8", "8. Novelty / duplicate checked?", ["", "novelty_clear", "public_known_but_not_duplicate", "duplicate_unknown", "duplicate_found", "cannot_assess"]) +
    `<div class="kv"><div class="k">8b. novelty override note (if unknown/cannot_assess)</div><div class="v"><input id="rq8note" placeholder="optional"/></div></div>` +
    _rsel("rq9", "9. Report draft exists?", yn) +
    _rsel("rq10", "10. Recommended mitigation included?", yn) +
    _rsel("rq11", "11. Assumptions and limitations included?", yn) +
    _rsel("rq12", "12. Human triager decision", ["", "ready_for_submission_package", "not_ready", "needs_more_context", "blocked_by_duplicate", "blocked_by_scope", "blocked_by_severity_too_low", "blocked_by_missing_poc", "blocked_by_missing_reachability", "blocked_by_missing_impact", "blocked_by_missing_novelty"]) +
    `<div class="kv"><div class="k">13. Reviewer notes</div><div class="v"><textarea id="rq13" rows="3" placeholder="required for ready"></textarea></div></div>` +
    `<div style="margin-top:8px"><button class="btn" id="rdSaveBtn">Save readiness review</button> <span id="rdResult" class="muted"></span></div>`;
}
function wireReadiness(d) {
  const btn = $("rdReviewBtn"); if (!btn) return;
  btn.addEventListener("click", () => {
    const p = $("rdPanel");
    if (p.style.display === "none") { p.innerHTML = readinessPanelHtml(); p.style.display = "block"; wireReadinessSave(d); }
    else { p.style.display = "none"; }
  });
}
function wireReadinessSave(d) {
  const save = $("rdSaveBtn"); if (!save) return;
  save.addEventListener("click", async () => {
    const g = (id) => { const e = $(id); return e ? e.value : ""; };
    const answers = {
      mechanism_confirmed: g("rq1"), reachability_confirmed: g("rq2"), severity_bearing: g("rq3"),
      poc_complete: g("rq4"), impact_not_overclaimed: g("rq5"), severity_recommendation: g("rq6"),
      scope_caveats_reviewed: g("rq7"), novelty: g("rq8"), novelty_override_note: g("rq8note"),
      report_draft_exists: g("rq9"), mitigation_included: g("rq10"), assumptions_included: g("rq11"),
      notes: g("rq13"),
    };
    const decision = g("rq12");
    if (!decision) { $("rdResult").textContent = "pick a human triager decision (q12)"; return; }
    try {
      const res = await apiPost("/api/submission-readiness", { candidate_id: d.candidate_id, reviewer: "browser", answers, decision, notes: g("rq13") });
      if (res.saved) { toast("readiness saved: " + res.readiness_state); loadDetail(d.candidate_id); }
      else { $("rdResult").innerHTML = `<span class="rdy-block">blocked — failed: ${esc((res.failed_checks || []).join("; "))}</span>`; }
    } catch (e) { $("rdResult").textContent = "save failed: " + e.message; }
  });
}

/* ---- editor link (WSL UNC, self-contained) ---- */
function editorTarget() { const v = localStorage.getItem("hv_editor"); return ["wsl-unc","wsl-remote","cursor-wsl","local"].includes(v) ? v : "wsl-unc"; }
function editorUri(abs, line) {
  const ln = line || 1, t = editorTarget();
  if (t === "wsl-remote") return `vscode://vscode-remote/wsl+${WSL_DISTRO}${abs}:${ln}`;
  if (t === "cursor-wsl") return `cursor://vscode-remote/wsl+${WSL_DISTRO}${abs}:${ln}`;
  if (t === "local") return `vscode://file${abs}:${ln}`;
  return `vscode://file//wsl.localhost/${WSL_DISTRO}${abs}:${ln}`;
}

/* ---- list (unified across all 3 tracks: runtime / funnel / detector) ---- */
async function loadList() {
  const data = await api("/api/candidates");
  state.rows = data.candidates || [];
  $("listCol").innerHTML = `
    <div class="filterbar">
      <span id="cCount" style="font-size:11px;color:var(--muted)"></span>
      <span style="flex:1"></span>
      <select id="cTrack"><option value="">all tracks</option><option value="runtime">runtime</option><option value="funnel">funnel</option><option value="detector">detector</option><option value="option_a_campaign">option_a_campaign</option></select>
      <input id="cSearch" placeholder="filter…" size="12"/>
    </div>
    <div id="cList"></div>`;
  $("cTrack").addEventListener("change", (e) => { state.fTrack = e.target.value; renderCards(); });
  $("cSearch").addEventListener("input", (e) => { state.fText = e.target.value.toLowerCase(); renderCards(); });
  renderCards();
}
function renderCards() {
  const rows = state.rows
    .filter((r) => (!state.fTrack || r.track === state.fTrack) &&
      (!state.fText || `${r.candidate_surface} ${r.audit_id} ${r.candidate_id}`.toLowerCase().includes(state.fText)))
    .sort((a, b) => (a.glance_rank ?? 99) - (b.glance_rank ?? 99));  // reportable → confirmed/ready → leads → refuted
  $("cList").innerHTML = rows.map(cardHtml).join("") || `<p class="missing">none</p>`;
  $("cCount").textContent = `${rows.length} / ${state.rows.length} findings`;
  $("cList").querySelectorAll(".card").forEach((c) => {
    c.addEventListener("click", () => selectCandidate(c.dataset.id));
    if (state.selected && c.dataset.id === state.selected.candidate_id) c.classList.add("sel");
  });
}
function cardHtml(r) {
  const cf = r.confidence || {}, det = r.track === "detector";
  const st = r.state || r.outcome || "";
  return `<div class="card" data-id="${esc(r.candidate_id)}">
    <div class="row2">
      <span class="tbadge ${esc(r.track || "detector")}">${esc(r.track || "detector")}</span>
      <span class="sbadge ${esc(st)}">${esc(st)}</span>
      ${r.illustrative ? '<span class="chip ill">illustrative</span>' : ''}
      ${r.labelable ? '' : '<span class="chip" title="read-only synced finding">read-only</span>'}
    </div>
    <div class="surf" style="margin-top:4px">${esc(r.candidate_surface || r.candidate_id_short)}</div>
    <div class="meta">${esc(r.detector)} · ${esc(r.audit_id || "?")} · <span class="src">${esc(r.source_location || "")}</span></div>
    <div class="row2">
      ${det ? `<span class="chip">${esc(r.outcome || r.lifecycle_state)}</span>
        <span class="chip">det:${esc(cf.detector_confidence ?? "—")}</span>
        <span class="chip">val:${esc(cf.validation_confidence ?? "—")}</span>
        <span class="chip">exp:${esc(cf.exploit_confidence ?? "—")}</span>
        <span class="chip">imp:${esc(cf.impact_confidence ?? "—")}</span>
        ${r.poc_lock ? '<span class="chip lock">PoC lock</span>' : ''}
        ${r.report_lock ? '<span class="chip lock">report lock</span>' : ''}
        <span class="chip">blockers:${r.hard_blockers_count}</span>
        <span class="chip">missing:${r.missing_artifacts_count}</span>`
      : `${r.severity_or_conversion ? `<span class="chip">${esc(r.severity_or_conversion)}</span>` : ''}
        ${r.duplicate_status ? `<span class="chip">${esc(r.duplicate_status)}</span>` : ''}`}
    </div></div>`;
}

/* ---- detail ---- */
// Visible error panel — never fail silently. Always shows the candidate_id + the API/render error.
function renderError(cid, msg) {
  $("detailCol").innerHTML =
    `<div class="banner kill"><b>Could not show this candidate.</b></div>` +
    kv("candidate_id", cid) + kv("error", msg) +
    `<p class="missing">No detail rendered. The URL is still updated so the link can be shared/refreshed once the issue is resolved.</p>`;
}
// Fetch + render, decoupled and crash-safe. URL/history is managed by the callers (selectCandidate / popstate / load).
async function loadDetail(cid) {
  if (!cid) return;
  document.querySelectorAll(".card").forEach((c) => c.classList.toggle("sel", c.dataset.id === cid));
  let d;
  try { d = await api(`/api/candidate?candidate_id=${encodeURIComponent(cid)}`); }
  catch (e) { renderError(cid, e.message); return; }
  if (!d || d.state === "NOT_FOUND") { renderError(cid, "candidate not found"); return; }
  try { state.selected = d; renderDetail(d); }
  catch (e) { renderError(cid, "render failed: " + e.message); }
}
// Card click: push a history entry, then load. Refresh + back/forward both reload from the URL.
function selectCandidate(cid) {
  if (!cid) return;
  const url = `/candidates?candidate_id=${encodeURIComponent(cid)}`;
  history.pushState({ cid }, "", url);
  loadDetail(cid);
}
window.addEventListener("popstate", (e) => {
  const cid = (e.state && e.state.cid) || new URLSearchParams(location.search).get("candidate_id");
  if (cid) loadDetail(cid);
});
function sumBox(t) { return `<div class="summary">${t}</div>`; }
function rawAccordion(label, obj) {
  if (obj == null) return "";
  return `<details><summary>raw ${esc(label)}</summary><pre>${esc(JSON.stringify(obj, null, 2))}</pre></details>`;
}
function missing(name) { return `<p class="missing">${esc(name)}: missing / not yet generated</p>`; }
function kv(k, v) { return `<div class="kv"><div class="k">${esc(k)}</div><div class="v">${esc(v ?? "—")}</div></div>`; }

function renderDetail(d) {
  if (d.read_only_synced) { renderSyncedDetail(d); return; }   // runtime / funnel synced findings
  const S = d.source || {}, cf = d.confidence || {};
  let h = "";
  h += renderReadinessSection(d);   // submission-readiness overlay (top of every detail page)
  // ILLUSTRATIVE / status banners
  if (d.illustrative) h += `<div class="banner ill">⚠ ILLUSTRATIVE — the validation pipeline has not been run for this candidate. Values are placeholder demo content (reusing verified source facts) to exercise this view.</div>`;
  // A. Header
  h += `<h2 class="sec">A · Header</h2>`;
  h += kv("candidate_id", d.candidate_id) + kv("detector", d.detector) + kv("audit_id", d.audit_id) +
       kv("lifecycle state", d.lifecycle_state) + kv("outcome", d.outcome) +
       kv("candidate surface", d.candidate_surface) + kv("source location", S.file ? `${S.file}:${S.line}` : "—") +
       kv("declared severity potential", d.declared_severity_potential) +
       kv("routing_allowed", String(d.routing_allowed)) + kv("research_only", String(d.research_only)) +
       kv("latest decision", d.promotion_decision ? `${d.promotion_decision.from_state}→${d.promotion_decision.to_state} by ${d.promotion_decision.decided_by||"?"}` : "—");
  // four confidences — always separate, labeled
  h += `<div class="confgrid">
    ${confCard("Detector", cf.detector_confidence, "detector flagged it (NOT proof)")}
    ${confCard("Validation", cf.validation_confidence, "gate artifacts present")}
    ${confCard("Exploit", cf.exploit_confidence, "a concrete surviving sequence")}
    ${confCard("Impact", cf.impact_confidence, "measurable protocol harm")}</div>`;
  // N. Next action (shown high)
  h += `<div class="nextbox"><b>Recommended next action:</b> ${esc(d.next_action)}</div>`;

  // B. Source
  h += `<h2 class="sec">B · Source</h2>`;
  if (S.file) {
    h += sumBox("<b>What code was flagged.</b> The function the detector pointed at.");
    h += kv("file", S.file) + kv("line", S.line) + kv("function signature", S.function_signature) +
         kv("source hash", S.source_hash) + kv("resolution status", S.resolution_status);
    if (S.abs_path) h += `<div style="margin:6px 0"><button class="btn openEditor" data-abs="${esc(S.abs_path)}" data-line="${S.line||1}">⤤ Open in VS Code</button> <span class="src">${esc(S.abs_path)}:${S.line||1}</span></div>`;
    if (S.code_snippet) h += `<pre>${esc(S.code_snippet)}</pre>`;
  } else h += missing("source_resolution");

  // C. Detector rationale
  h += `<h2 class="sec">C · Detector rationale</h2>`;
  h += sumBox("<b>Why it was flagged.</b> The detector's own reasoning — a signal, not a verdict.");
  h += kv("detector confidence", cf.detector_confidence) + kv("rationale", d.rationale);
  h += rawAccordion("evidence_signals", d.rationale_evidence);

  // D. Reachability
  h += `<h2 class="sec">D · Reachability</h2>`; h += panel(d.reachability, "reachability_map", (R) => {
    let x = sumBox("<b>Can an attacker reach it?</b> Entry points and the call path to the flagged code.");
    x += kv("attacker can reach", String(R.attacker_can_reach)) + kv("verdict", R.reachability_verdict) + kv("reason", R.reason);
    if (R.entrypoints) x += evTable(["function","file","line","visibility"], R.entrypoints);
    if (R.call_path) x += `<pre>${esc(R.call_path.join("\n"))}</pre>`;
    if (R.access_controls) x += kv("access controls", (R.access_controls||[]).join("; "));
    if (R.privileged_blockers) x += kv("privileged blockers", (R.privileged_blockers||[]).join("; ") || "none");
    return x;
  });

  // E. Callable surface
  h += `<h2 class="sec">E · Callable surface</h2>`; h += panel(d.callable_surface, "callable_surface", (C) => {
    let x = sumBox("<b>What can run inside the batch.</b> Sub-calls reachable through multicall/delegatecall.");
    return x + evTable(["function","file","line","mutability","callable_in_multicall","blocked_in_multicall","mutates_accounting","validation_sensitive"], C.callable_subcalls || []);
  });

  // F. State mutation map
  h += `<h2 class="sec">F · State mutation map</h2>`; h += panel(d.state_mutation_map, "state_mutation_map", (M) => {
    let x = sumBox("<b>What state is in play.</b> Variables/balances the invariant compares and the functions that touch them.");
    x += kv("state variables", (M.state_variables||[]).join("; "));
    x += kv("token balances", (M.token_balances||[]).join("; ")) + kv("totalSupply refs", (M.totalsupply_refs||[]).join("; "));
    x += kv("mutating functions", (M.mutating_functions||[]).join(", ")) + kv("reading functions", (M.reading_functions||[]).join(", "));
    x += kv("before/after vars", (M.before_after_variables||[]).join(", "));
    return x;
  });

  // G. Defense map
  h += `<h2 class="sec">G · Defenses</h2>`; h += panel(d.defense_map, "defense_map", (G) => {
    let x = sumBox("<b>What stops it.</b> Guards present, and whether each covers the flagged behavior.");
    (G.defenses||[]).forEach((df) => { x += `<div class="defense"><span>${esc(df.type)} · <span class="src">${esc(df.name)} @ ${esc(df.location)}</span></span><span class="cov-${esc(df.coverage)}">${esc(df.coverage)}${df.skipped_in_multicall?" · skipped in multicall":""}</span></div>`; });
    if (G.checks_skipped_when_isMulticall) x += kv("skipped when isMulticall", (G.checks_skipped_when_isMulticall||[]).join("; "));
    return x;
  });

  // H. Invariant analysis
  h += `<h2 class="sec">H · Invariant analysis</h2>`; h += panel(d.invariant_analysis, "invariant_analysis", (I) => {
    let x = sumBox("<b>What may be broken.</b> The exact invariant claim and whether the final check fully covers it.");
    x += kv("invariant", I.invariant_statement) + kv("expected relationship", I.expected_relationship);
    x += kv("final validation fn", I.final_validation_function) + kv("sufficient/incomplete", I.sufficient_or_incomplete);
    x += kv("covers", (I.covers||[]).join("; ")) + kv("may NOT cover", (I.may_not_cover||[]).join("; "));
    x += kv("security property", I.security_property);
    return x;
  });

  // I. Exploit path (most important)
  h += `<h2 class="sec">I · Exploit path</h2>`;
  if (d.exploit_sequences && d.exploit_sequences.length) {
    d.exploit_sequences.forEach((seq, idx) => {
      h += `<div style="margin:8px 0"><b>Exploit Path Candidate #${idx+1}: ${esc(seq.title||"")}</b> — status: ${esc(seq.status||"?")}</div>`;
      h += sumBox(`<b>Expected violated invariant:</b> ${esc(seq.expected_violated_invariant||"?")}<br><b>Expected impact (hypothesis):</b> ${esc(seq.expected_impact||"?")}`);
      h += kv("preconditions", (seq.preconditions||[]).join("; "));
      (seq.steps||[]).forEach((s) => {
        const loc = s.file ? ` <span class="m">${esc(s.file)}</span>` : "";
        h += `<div class="step"><span class="n">Step ${s.step}</span> ${esc(s.function || s.desc || "")}${loc}
          ${s.effect||s.detail ? `<div>${esc(s.effect||s.detail)}</div>` : ""}
          <div class="m">${s.rw?("rw:"+esc(s.rw)+" · "):""}conf:${esc(s.confidence||"—")}${s.evidence_ref?(" · ev:"+esc(s.evidence_ref)):""}</div></div>`;
      });
      h += rawAccordion(`sequence #${idx+1}`, seq);
    });
  } else {
    h += `<div class="banner kill">No complete exploit path has survived validation yet.</div>`;
    h += missing("sequence_candidates") + `<p class="missing">Missing to build one: ${esc((d.missing_artifacts||[]).join(", "))}</p>`;
  }

  // J. Negative tests
  h += `<h2 class="sec">J · Negative tests / kill checks</h2>`; h += panel(d.negative_tests, "negative_tests", (N) => {
    let x = sumBox("<b>Did we try to kill it?</b> Each check tries to refute the candidate; it advances only if a sequence survives.");
    x += kv("survived", String(N.survived)) + kv("test output", N.test_command_output_summary);
    x += evTable(["name","result","evidence"], N.kill_checks || []);
    return x;
  });

  // K. PoC readiness
  h += `<h2 class="sec">K · PoC readiness</h2>`;
  if (d.poc_ready && d.poc_ready.exists) {
    const L = d.poc_ready.data || {};
    h += `<div class="banner poc">✔ poc_ready.lock.json present. <b>${esc(d.poc_ready.warning)}</b></div>`;
    h += kv("authorizes", L.authorizes) + kv("NOT authorized", (L.not_authorized||[]).join(", "));
    h += kv("expected assertion", L.expected_assertion) + kv("target test file", L.target_test_file_suggestion);
    h += kv("gates passed", (L.gates_passed||[]).join(", "));
    if (L.exact_sequence_to_test) h += `<div class="src">approved sequence to test:</div><pre>${esc((L.exact_sequence_to_test||[]).join("\n"))}</pre>`;
    h += kv("unresolved risks", (L.unresolved_risks||[]).join("; ")) + kv("report generation allowed", String(L.report_generation_allowed));
  } else {
    h += `<p class="missing">poc_ready.lock.json: not present — a local PoC task is NOT yet allowed.</p>`;
    if (d.scorecard && d.scorecard.required) h += kv("required gates", JSON.stringify(d.scorecard.required));
  }

  // L. Report readiness
  h += `<h2 class="sec">L · Report readiness</h2>`;
  if (d.report_ready && d.report_ready.exists) h += kv("report lock", "present") + rawAccordion("report_ready.lock", d.report_ready.data);
  else h += `<p class="missing">report_ready.lock.json: not present — report drafting is blocked (separate human gate; never implied by POC_READY).</p>`;

  // M. Evidence timeline
  h += `<h2 class="sec">M · Evidence timeline</h2><ul class="timeline">`;
  (d.evidence_timeline||[]).forEach((t) => { h += `<li class="${t.present?"done":"todo"}">${esc(t.stage)}${t.present?"":" — not yet"}</li>`; });
  h += `</ul>`;

  // notes/verdict + missing summary
  if (d.verdict_md) h += `<h2 class="sec">Verdict</h2><pre>${esc(d.verdict_md)}</pre>`;
  if (d.notes_md) h += rawAccordion("notes.md", d.notes_md);
  if (d.missing_artifacts && d.missing_artifacts.length) h += `<p class="missing">Missing artifacts (${d.missing_artifacts.length}): ${esc(d.missing_artifacts.join(", "))}</p>`;

  $("detailCol").innerHTML = h;
  decorateStatusTokens($("detailCol"));
  $("detailCol").querySelectorAll(".openEditor").forEach((b) => b.addEventListener("click", () => {
    window.location = editorUri(b.dataset.abs, b.dataset.line);
  }));
  wireReadiness(d);
}
/* runtime / funnel synced finding — Bug Report Verifier layout (READ-ONLY).
   Rendered from d.verifier_evidence (extracted from the track artifacts) so the page reads as a report
   without opening links. Absent values show "unknown" (never "needs review"). The browser computes no
   severity/submission and exposes no label/promote controls for synced findings. */
function renderSyncedDetail(d) {
  const raw = d.raw_row || d.raw_record || {};
  const VE = d.verifier_evidence || {};
  const sec = (n, t) => `<h2 class="sec">${n}. ${esc(t)}</h2>`;
  const vq = (q) => `<div class="vq">❓ ${esc(q)}</div>`;
  const hint = (t) => `<div class="hint">${t}</div>`;
  const v = (x) => (x === null || x === undefined || x === "") ? "unknown" : x;       // never "needs review"
  const sv = (x) => (x === null || x === undefined || x === "") ? "unknown" : String(x);
  const openBtn = (abs) => abs ? ` <button class="btn ghost openEditor" data-abs="${esc(abs)}" data-line="1">⤤ open</button>` : "";
  const lst = (arr) => (arr && arr.length) ? `<ul class="vlist">${arr.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>` : `<p class="muted">unknown</p>`;
  const tbl = (cols, rows) => (rows && rows.length)
    ? `<table class="ev"><thead><tr>${cols.map((c) => `<th>${esc(c[1])}</th>`).join("")}</tr></thead><tbody>` +
      rows.map((r) => `<tr>${cols.map((c) => `<td class="src">${esc(sv(r[c[0]]))}</td>`).join("")}</tr>`).join("") + `</tbody></table>`
    : `<p class="muted">unknown</p>`;

  const rs = VE.report_summary || {}, me = VE.mechanism || {}, am = VE.attacker_model || {},
        pv = VE.poc_verification || {}, im = VE.impact_severity || {}, iso = VE.intent_scope_operator || {},
        nd = VE.novelty_duplicate || {}, cv = VE.conversion || {}, mb = VE.main_blocker || {}, ft = VE.final_triage || {};

  let h = `<div class="banner synced">🔗 Synced finding (${esc(d.track)}) — <b>read-only verifier report</b>. Every value below is mirrored from the track's recorded artifacts (no link-opening required); blanks show "unknown". The browser computes no severity/submission and exposes no label/promote controls. research_only:true · routing_allowed:false · submission_ready:false.</div>`;
  if (d.status_text) h += `<div class="statustext"><b>Status:</b> ${esc(d.status_text)}</div>`;
  h += renderReadinessSection(d);   // submission-readiness overlay (near the top)

  // 1. Report Summary
  h += sec(1, "Report Summary");
  h += sumBox(`<b>Bug.</b> ${esc(v(rs.bug))}`);
  h += kv("affected contracts", v((rs.affected_contracts || []).join(", "))) +
       kv("affected functions", v((rs.affected_functions || []).join(", "))) +
       kv("attacker", v(rs.attacker)) + kv("impact", v(rs.impact_summary)) +
       kv("VRT category", v(rs.vrt_category)) + kv("CVSS v3.1", v(rs.cvss)) +
       kv("current decision", v(rs.current_decision)) + kv("severity (recorded)", v(rs.severity_recommendation)) +
       kv("novelty", v(rs.novelty_status)) + kv("submission boundary", v(rs.submission_boundary)) +
       kv("candidate_id", d.candidate_id) + kv("workspace / audit", v(d.audit_id));

  // Campaign (Option-A) block — shown for ledger-only campaign candidates with no runtime harness.
  if (d.campaign) {
    const cm = d.campaign;
    h += sec("·", "Campaign (Option-A)");
    h += kv("severity ceiling estimate", v(cm.severity_ceiling_estimate)) +
         kv("deploy blocker", v(cm.deploy_blocker)) + kv("selection reason", v(cm.selection_reason));
    if (cm.why_no_harness && cm.why_no_harness !== "unknown") h += sumBox(`<b>Why no harness was run.</b> ${esc(cm.why_no_harness)}`);
    if (cm.source_refutation && cm.source_refutation !== "unknown") h += sumBox(`<b>Source refutation.</b> ${esc(cm.source_refutation)}`);
    if (cm.what_taught && cm.what_taught !== "unknown") h += sumBox(`<b>What this taught the campaign.</b> ${esc(cm.what_taught)}`);
  }

  // 2. One-Sentence Mechanism
  h += sec(2, "One-Sentence Mechanism");
  h += sumBox(esc(v(me.one_sentence)));
  h += kv("root cause", v(me.root_cause)) + kv("refutation condition", v(me.refutation_condition)) +
       kv("why not refuted", v(me.why_not_refuted)) + vq("Can I explain the mechanism in one sentence?");

  // 3. Function Map
  h += sec(3, "Function Map");
  h += tbl([["role", "Role"], ["function", "Function"], ["permission", "Permission"],
            ["why_it_matters", "Why it matters"], ["source_location", "Source"]], VE.function_map);
  h += vq("Which functions are involved, and can an unprivileged user reach the entrypoint?");

  // 4. Attacker Model
  h += sec(4, "Attacker Model");
  h += kv("attacker", v(am.attacker)) + kv("privilege required", v(am.privilege_required)) +
       kv("victim action required", v(am.victim_action_required)) +
       kv("operator / keeper dependency", v(am.operator_or_keeper_dependency)) +
       kv("self-remediation", v(am.self_remediation)) +
       kv("reachability verdict", v(am.reachability_verdict)) + kv("reason", v(am.reason));
  h += `<div class="kv"><div class="k">controls</div><div class="v">${lst(am.controls)}</div></div>`;
  h += `<div class="kv"><div class="k">does not control</div><div class="v">${lst(am.does_not_control)}</div></div>`;
  h += vq("Can an unprivileged attacker reach it without victim action?");

  // 5. Exploit Steps
  h += sec(5, "Exploit Steps");
  h += (VE.exploit_steps && VE.exploit_steps.length)
    ? `<ol class="vsteps">${VE.exploit_steps.map((s) => `<li>${esc(s)}</li>`).join("")}</ol>`
    : `<p class="muted">unknown</p>`;
  h += vq("Through what production flow does the attacker reach the bad state?");

  // 6. Defense Map
  h += sec(6, "Defense Map");
  h += tbl([["defense", "Defense"], ["location", "Location"], ["classification", "Classification"],
            ["reason", "Reason"], ["manual_check", "Manual check"]], VE.defense_map);
  h += vq("What defense should stop it — and does it run before/after the loss, only by operator, or never?");

  // 7. PoC Verification
  h += sec(7, "PoC Verification");
  h += kv("uses real contract", sv(pv.uses_real_contract)) +
       kv("production source unchanged", sv(pv.production_source_unchanged)) +
       kv("harness isolated / un-wired", sv(pv.harness_isolated_unwired)) +
       kv("command", v(pv.command)) + kv("test result", v(pv.test_result)) +
       kv("actual (vulnerable)", v(pv.actual_result)) + kv("expected (corrected)", v(pv.expected_result)) +
       kv("control", v(pv.control_result)) + kv("state / value delta", v(pv.state_or_value_delta));
  h += tbl([["window", "Window"], ["a (locker)", "A (locker)"], ["b (unlocked)", "B (unlocked)"],
            ["a:b", "A:B"], ["reading", "Reading"]], pv.result_table);
  h += vq("Does the PoC use the real contract? What is actual vs expected vs control?");

  // 8. Impact and Severity
  h += sec(8, "Impact and Severity");
  h += kv("who loses", v(im.who_loses)) + kv("who gains", v(im.who_gains)) +
       kv("asset / value", v(im.asset_or_value)) + kv("loss type", v(im.loss_type)) +
       kv("permanence", v(im.permanence)) + kv("repeatability", v(im.repeatability)) +
       kv("bounds", v(im.bounds)) + kv("severity (recorded)", v(im.severity_recommendation));
  h += `<div class="kv"><div class="k">downgrade arguments</div><div class="v">${lst(im.downgrade_arguments)}</div></div>`;
  h += `<div class="kv"><div class="k">upgrade arguments</div><div class="v">${lst(im.upgrade_arguments)}</div></div>`;
  h += `<div class="kv"><div class="k">assumptions</div><div class="v">${lst(im.assumptions)}</div></div>`;
  h += `<div class="kv"><div class="k">unresolved questions</div><div class="v">${lst(im.unresolved_questions)}</div></div>`;
  h += vq("Who loses and who gains? Is this protocol loss or user-to-user redistribution?");

  // 9. Intent, Scope, and Operator Assumptions
  h += sec(9, "Intent, Scope, and Operator Assumptions");
  h += kv("intent verdict", v(iso.intent_verdict)) + kv("operator scope", v(iso.operator_scope_status)) +
       kv("operator / keeper fact", v(iso.operator_or_keeper_fact)) +
       kv("ambiguity: kill or bound?", v(iso.does_ambiguity_kill_or_bound));
  h += `<div class="kv"><div class="k">scope caveats</div><div class="v">${lst(iso.scope_caveats)}</div></div>`;
  h += vq("Does intent/scope kill it or only bound severity?");

  // 10. Novelty and Duplicate Status
  h += sec(10, "Novelty and Duplicate Status");
  h += kv("duplicate status", v(nd.duplicate_status)) + kv("novelty status", v(nd.novelty_status)) +
       kv("exact duplicate found", v(nd.exact_duplicate_found)) +
       kv("materially equivalent found", v(nd.materially_equivalent_found)) +
       kv("public-known context", v(nd.public_known_context)) +
       kv("sources checked", v(nd.sources_checked_summary)) + kv("residual limit", v(nd.residual_limit));
  h += vq("Is novelty clear, unknown, duplicate, or public-known?");

  // 11. Conversion Classification
  h += sec(11, "Conversion Classification");
  ["mechanism_confirmed", "attacker_reachable", "severity_bearing", "novelty_clear", "reportable",
   "runtime_status", "reachability_verdict", "severity_class", "duplicate_status", "conversion_outcome",
   "primary_blocker", "human_review_required", "submission_ready", "routing_allowed"].forEach((k) => { h += kv(k, sv(cv[k])); });
  h += vq("What is the conversion outcome?");

  // 12. Main Blocker
  h += sec(12, "Main Blocker");
  h += kv("blocker", v(mb.blocker)) + kv("why it matters", v(mb.why_it_matters)) +
       kv("what would clear it", v(mb.what_would_clear_it)) + vq("What is the blocker if not reportable?");

  // 13. Final Triager Decision
  h += sec(13, "Final Triager Decision");
  h += kv("decision (recorded)", v(ft.decision)) + kv("why", v(ft.why)) +
       kv("what this taught the system", v(ft.what_this_taught_the_system)) +
       hint("Recorded decision — the browser does not promote, submit, or set severity.");

  // 14. Red Flags (status extracted where a recorded field is unambiguous; else manual)
  h += sec(14, "Red Flags");
  h += tbl([["check", "Check"], ["status", "Status"], ["evidence", "Evidence"]], VE.red_flags);
  h += hint("'manual' = needs a human eyeball; status is derived only where a recorded field is unambiguous.");

  // 15. Evidence Backup (collapsed — links/raw only; nothing dropped)
  h += sec(15, "Evidence Backup");
  const bk = VE.evidence_backup || {};
  h += `<details><summary>Backup links &amp; raw artifacts (${(bk.top_source_files || []).length} links · ${(d.documents || []).length} records · ${(d.evidence || []).length} artifacts) — optional source confirmation</summary>`;
  if ((bk.top_source_files || []).length) {
    h += `<div class="keylinks"><b>Top source files:</b> ` +
      bk.top_source_files.map((k) => `<span class="kl"><span class="src">${esc(k.label)}</span>${openBtn(k.abs_path)} <span class="src">${esc(k.path || "")}</span></span>`).join(" · ") + `</div>`;
  }
  if ((d.evidence || []).length) {
    h += `<table class="ev"><thead><tr><th>label</th><th>kind</th><th>path</th><th></th></tr></thead><tbody>`;
    d.evidence.forEach((e) => { h += `<tr><td>${esc(e.label)}</td><td class="src">${esc(e.kind || "")}</td><td class="src">${esc(e.path || "")}</td><td>${openBtn(e.abs_path)}</td></tr>`; });
    h += `</tbody></table>`;
  }
  (d.documents || []).forEach((doc) => {
    h += `<details><summary>${esc(doc.label)} <span class="src">${esc(doc.path || "")}</span> [${esc(doc.kind || "")}]${openBtn(doc.abs_path)}</summary><pre>${esc(doc.content || "")}</pre></details>`;
  });
  h += `<details><summary>All raw fields (${Object.keys(raw).length})</summary><pre>${esc(JSON.stringify(raw, null, 2))}</pre></details>`;
  h += `</details>`;

  $("detailCol").innerHTML = h;
  decorateStatusTokens($("detailCol"));
  $("detailCol").querySelectorAll(".openEditor").forEach((b) => b.addEventListener("click", () => {
    window.location = editorUri(b.dataset.abs, b.dataset.line);
  }));
  wireReadiness(d);
}
function confCard(label, val, hint) {
  return `<div class="confcard"><div class="l">${esc(label)} confidence</div><div class="v">${esc(val ?? "—")}</div><div class="l">${esc(hint)}</div></div>`;
}
function panel(data, name, fn) {
  if (data == null) return missing(name);
  try { return fn(data) + rawAccordion(name, data); } catch (e) { return `<p class="missing">${esc(name)}: failed to render</p>`; }
}
function evTable(cols, rows) {
  if (!rows || !rows.length) return `<p class="missing">none</p>`;
  return `<table class="ev"><thead><tr>${cols.map((c)=>`<th>${esc(c)}</th>`).join("")}</tr></thead><tbody>` +
    rows.map((r) => `<tr>${cols.map((c)=>`<td>${esc(typeof r[c]==="boolean"?String(r[c]):(r[c]??""))}</td>`).join("")}</tr>`).join("") +
    `</tbody></table>`;
}

/* ---- wiring ---- */
(() => { const es = $("editorScheme"); if (es) { es.value = editorTarget(); es.addEventListener("change", () => { localStorage.setItem("hv_editor", es.value); if (state.selected) renderDetail(state.selected); }); } })();
// On load: render the URL's detail IMMEDIATELY (don't block on the list), and load the list in parallel.
// The list's .sel highlight is applied by renderCards() via state.selected/dataset.id once it resolves.
(function bootstrap() {
  const cid = new URLSearchParams(location.search).get("candidate_id");
  if (cid) { history.replaceState({ cid }, "", location.pathname + location.search); loadDetail(cid); }
  loadList().catch((e) => { $("listCol").innerHTML = `<p class="missing">load failed: ${esc(e.message)}</p>`; });
})();
