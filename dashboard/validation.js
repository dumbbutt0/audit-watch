/* Investigation Workspace — research corpus.
   Invariants: review→prioritize→explain→organize. No bug/severity/exploitability/submit/routing field is ever
   requested or sent. Corpus is read-only; only append-only research JSONLs are written.
*/
"use strict";

const ALLOWED = {
  coherence: ["coherent", "partially_coherent", "weak", "incoherent"],
  investigation_worthiness: ["investigate", "maybe", "skip"],
  poc_followup_worthiness: ["yes", "maybe", "no"],
  expected_review_effort: ["low", "medium", "high"],
  reviewer_confidence: ["high", "medium", "low"],
};
const PROMO_CATEGORIES = [
  "evidence_coherence", "attacker_reachability", "affected_asset_function", "state_or_invariant",
  "missing_validation", "concrete_impact_hypothesis", "counter_signals_reviewed", "poc_feasibility",
  "scope_relevance", "duplicate_known_issue_risk", "next_step_confidence", "chain_completeness",
];
const CAT_STATES = ["met", "partial", "unmet", "unknown"];
const OUTCOMES = ["PROMOTE_TO_CHAIN_ANALYSIS", "NEEDS_MORE_EVIDENCE", "HOLD_AS_WEAK_SIGNAL", "ARCHIVE_AS_NOISE"];
const STATUS_STATES = ["not_started", "researching", "chain_mapping", "poc_planning", "blocked", "archived"];
const EVIDENCE_SOURCES = ["bundle", "human_observation", "external_note"];
const CHAIN_SECTIONS = [
  "Title / Finding Hypothesis", "System Context", "Attacker Preconditions", "Entry Point", "Trust Assumption",
  "Broken Check", "Exploit Path", "State Change", "Impact Hypothesis", "PoC Plan", "Counter Signals",
  "Evidence Inventory", "Open Questions",
];

const state = { corpusHash: null, bundles: [], selected: null, sortKey: "candidate_surface", sortDir: 1,
                promotions: {}, lastTextarea: null };

const $ = (id) => document.getElementById(id);
const demo = () => $("demoToggle").checked;
const dq = () => (demo() ? "?demo=true" : "");
const esc = (s) => String(s == null ? "" : s).replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));

function toast(msg, isErr) {
  const t = $("toast"); t.textContent = msg; t.className = "toast show" + (isErr ? " err" : "");
  setTimeout(() => (t.className = "toast"), 2800);
}
async function api(path, opts) {
  const r = await fetch(path, opts);
  if (!r.ok) { let d = ""; try { d = (await r.json()).detail; } catch (e) {} throw new Error(d || r.status); }
  return r.json();
}
// The dashboard runs in WSL (Linux abs paths); the browser is on Windows, which reaches the repo via
// \\wsl.localhost\<distro>\... — so editor links map the Linux abs path onto that UNC path.
const WSL_DISTRO = "Ubuntu";
const EDITOR_TARGETS = ["wsl-unc", "wsl-remote", "cursor-wsl", "local"];
function editorTarget() { const v = localStorage.getItem("hv_editor"); return EDITOR_TARGETS.includes(v) ? v : "wsl-unc"; }
function uncBackslash(absLinux) { return "\\\\wsl.localhost\\" + WSL_DISTRO + absLinux.replace(/\//g, "\\"); }
function editorUri(absLinux, line) {
  const ln = line || 1, t = editorTarget();
  if (t === "wsl-remote") return `vscode://vscode-remote/wsl+${WSL_DISTRO}${absLinux}:${ln}`;
  if (t === "cursor-wsl") return `cursor://vscode-remote/wsl+${WSL_DISTRO}${absLinux}:${ln}`;
  if (t === "local") return `vscode://file${absLinux}:${ln}`;
  // wsl-unc (default): \\wsl.localhost\Ubuntu\... → file URI //wsl.localhost/Ubuntu/...
  return `vscode://file//wsl.localhost/${WSL_DISTRO}${absLinux}:${ln}`;
}
function displayPath(absLinux, line) {
  const ln = line || 1;
  return (editorTarget() === "local") ? `${absLinux}:${ln}` : `${uncBackslash(absLinux)}:${ln}`;
}
function openInEditorHtml(absPath, line, label) {
  if (!absPath) return `<div class="notice">source not resolvable on this host — open the file manually</div>`;
  const ln = line || 1;
  return `<div class="quick" style="margin:6px 0;align-items:center;flex-wrap:wrap">
    <button class="btn mini openEditorBtn" data-abs="${esc(absPath)}" data-line="${ln}">⤤ ${esc(label || "Open in VS Code")}</button>
    <button class="btn ghost mini copyPathBtn" data-abs="${esc(absPath)}" data-line="${ln}">copy path</button>
    <span class="src">${esc(displayPath(absPath, ln))}</span></div>`;
}
function countTable(obj) {
  return Object.entries(obj || {}).sort((a, b) => b[1] - a[1])
    .map(([k, v]) => `<div class="stat"><span>${esc(k)}</span><b>${v}</b></div>`).join("") || "<span style='color:var(--muted)'>none</span>";
}

/* ----------------------------------------------------------------- load */
async function loadAll() {
  const corpus = await api("/api/validation/corpus");
  state.corpusHash = corpus.corpus_hash;
  $("corpusHash").textContent = corpus.corpus_hash.slice(0, 16) + "…";
  const ov = corpus.overview;
  $("overview").innerHTML =
    `<div class="stat"><span>total bundles</span><b>${ov.total_bundles}</b></div>` +
    `<h2>by detector</h2>${countTable(ov.by_detector)}<h2>by confidence</h2>${countTable(ov.by_confidence)}` +
    `<h2>by declared severity potential</h2>${countTable(ov.by_declared_severity_potential)}` +
    `<h2>by bundle status</h2>${countTable(ov.by_bundle_status)}<h2>by workspace</h2>${countTable(ov.by_workspace)}`;
  state.bundles = (await api("/api/validation/bundles" + dq())).bundles;
  state.promotions = {};
  (await api("/api/validation/promotions" + dq())).promotions.forEach((p) => (state.promotions[p.candidate_id] = p));
  ["fDetector", "fConfidence", "fWorkspace"].forEach((id, i) => fillFilter(id, ["detector", "confidence", "workspace"][i]));
  renderQueue(); await refreshProgress();
}
function fillFilter(id, key) {
  const sel = $(id), cur = sel.value;
  const vals = [...new Set(state.bundles.map((b) => b[key]).filter(Boolean))].sort();
  sel.innerHTML = `<option value="">all ${key}</option>` + vals.map((v) => `<option>${esc(v)}</option>`).join("");
  sel.value = cur;
}

/* --------------------------------------------------------- ① queue + label */
function filteredSorted() {
  const s = $("fSearch").value.toLowerCase(), fd = $("fDetector").value, fc = $("fConfidence").value,
    fw = $("fWorkspace").value, fl = $("fLabel").value;
  let rows = state.bundles.filter((b) =>
    (!fd || b.detector === fd) && (!fc || b.confidence === fc) && (!fw || b.workspace === fw) &&
    (!fl || b.label_status === fl) && (!s || `${b.candidate_surface} ${b.candidate_id}`.toLowerCase().includes(s)));
  const k = state.sortKey, dir = state.sortDir;
  rows.sort((a, b) => (String(a[k]) < String(b[k]) ? -dir : String(a[k]) > String(b[k]) ? dir : 0));
  return rows;
}
function renderQueue() {
  const tb = $("queue").querySelector("tbody");
  tb.innerHTML = filteredSorted().map((b) => {
    const sel = state.selected && state.selected.candidate_id === b.candidate_id ? " sel" : "";
    return `<tr class="row ${b.label_status}${sel}" data-id="${esc(b.candidate_id)}">
      <td>${esc(b.candidate_surface)}</td><td>${esc(b.detector)}</td>
      <td><span class="pill ${esc(b.confidence)}">${esc(b.confidence)}</span></td>
      <td>${esc(b.declared_severity_potential)}</td><td>${esc(b.bundle_status)}</td>
      <td>${esc(b.workspace)}</td><td>${b.label_status}</td></tr>`;
  }).join("");
  tb.querySelectorAll("tr.row").forEach((tr) => tr.addEventListener("click", () => selectBundle(tr.dataset.id)));
}
function selectBundle(cid) {
  state.selected = state.bundles.find((b) => b.candidate_id === cid) || null;
  renderQueue(); renderDetail(); renderLabelForm();
}
function renderDetail() {
  const b = state.selected; if (!b) { $("detail").innerHTML = ""; return; }
  const comp = b.evidence_completeness || { present: [], missing: [] };
  const kv = (k, v) => `<div class="kv"><div class="k">${k}</div><div class="v">${esc(v)}</div></div>`;
  $("detail").innerHTML = `<h2>Bundle Detail</h2>` +
    `<div style="display:flex;gap:8px;margin:6px 0"><span class="badge ok">routing_allowed:false</span><span class="badge ok">research_only:true</span></div>` +
    kv("candidate_id", b.candidate_id) + kv("detector", `${b.detector} ${b.detector_version || ""}`) +
    kv("signal_type", b.signal_type) + kv("candidate_surface", b.candidate_surface) +
    kv("confidence (carried)", b.confidence) + kv("declared_severity_potential (hint)", b.declared_severity_potential) +
    kv("location", b.location ? `${b.location.file}:${b.location.start_line}` : "—") +
    openInEditorHtml(b.abs_path, b.location && b.location.start_line, "Open function in VS Code") +
    `<div class="kv"><div class="k">code_snippet <label style="display:inline;text-transform:none;font-size:11px;color:var(--muted)"><input type="checkbox" id="annotateToggle" style="width:auto" ${annotateEnabled() ? "checked" : ""}/> explain (hypothesis)</label></div><pre class="snippet">${esc(annotateSnippet(b))}</pre></div>` +
    `<div class="kv"><div class="k">evidence_signals</div><pre class="snippet">${esc(JSON.stringify(b.evidence_signals || {}, null, 2))}</pre></div>` +
    kv("rationale", b.rationale) +
    `<div class="kv"><div class="k">evidence present</div><div class="v present">${(comp.present || []).join(", ") || "—"}</div></div>` +
    `<div class="kv"><div class="k">evidence missing</div><div class="v missing">${(comp.missing || []).join(", ") || "none"}</div></div>`;
  const at = $("annotateToggle");
  if (at) at.addEventListener("change", () => { localStorage.setItem("hv_annotate", at.checked ? "1" : "0"); renderDetail(); });
}
/* Build a DISPLAY-ONLY annotated copy of the snippet: the detector's hypothesis as Solidity comments.
   Never mutates the corpus; restates the bundle's own evidence; framed as hypothesis, not a verdict. */
function annotateEnabled() { return localStorage.getItem("hv_annotate") !== "0"; }  // default on
function _wrapComment(text, prefix, width) {
  width = width || 100;
  const words = String(text || "").split(/\s+/), lines = []; let cur = prefix;
  for (const w of words) {
    if ((cur + " " + w).length > width && cur !== prefix) { lines.push(cur); cur = prefix + w; }
    else { cur = cur === prefix ? prefix + w : cur + " " + w; }
  }
  if (cur !== prefix) lines.push(cur);
  return lines;
}
function _inlineTokens(b) {
  const sig = b.evidence_signals || {}, out = [];
  const push = (v) => { if (typeof v === "string" && v.length >= 2 && v.length <= 40 && !/\s/.test(v) && !out.includes(v)) out.push(v); };
  push(sig.permit_source); push(sig.expected_asset_source);
  (sig.invariant_terms || []).forEach(push); (sig.evidence_terms || []).forEach(push);
  if (b.detector === "multicall_invariant") { push("delegatecall"); }
  return out.slice(0, 6);
}
function _hypothesisLine(b) {
  const s = b.signal_type;
  if (s === "asset_binding_missing") return "⚠ HYPOTHESIS: no permitted.token == asset / InvalidToken check here (missing binding)";
  if (s === "batch_invariant_opportunity") return "⚠ HYPOTHESIS: per-call invariant read across an unresolved/opaque batch — may not hold";
  const r = (b.rationale || "").trim();
  return r ? "⚠ HYPOTHESIS: " + (r.length > 120 ? r.slice(0, 117) + "…" : r) : "";
}
function annotateSnippet(b) {
  const code = b.code_snippet || "";
  if (!code) return "(none)";
  if (!annotateEnabled()) return code;  // raw view
  const sig = b.evidence_signals || {};
  const primary = sig.missing_binding_explanation || sig.reason || b.rationale || b.signal_type || ("flagged by " + b.detector);
  const tokens = _inlineTokens(b);
  const header = [
    "// ── RESEARCH HYPOTHESIS — why the detector flagged this (NOT a confirmed bug) ──",
    ..._wrapComment(primary, "//   "),
    `//   detector: ${b.detector} · signal: ${b.signal_type}`,
    tokens.length ? `//   flags: ${tokens.join(", ")}` : "//   flags: (none matched in snippet — see explanation above)",
    "// ──────────────────────────────────────────────────────────────",
    "",
  ].join("\n");
  const hyp = _hypothesisLine(b);
  const used = new Set();  // annotate each token only once (first occurrence) to keep it scannable
  let injected = false;
  const lines = code.split("\n").map((line) => {
    const low = line.toLowerCase();
    const hit = tokens.find((t) => !used.has(t) && low.includes(t.toLowerCase()));
    if (!hit) return line;
    used.add(hit);
    let out = line + "    // ⟵ flag: " + hit;
    if (!injected && hyp) {  // one inserted hypothesis line at the first anchor, matching indentation
      injected = true;
      const indent = (line.match(/^\s*/) || [""])[0];
      out += "\n" + indent + "// " + hyp;
    }
    return out;
  });
  // if no anchor matched, still surface the hypothesis once at the top of the body
  if (!injected && hyp) lines.unshift("// " + hyp, "");
  return header + lines.join("\n");
}
function selOpts(arr, cur) { return arr.map((v) => `<option ${v === cur ? "selected" : ""}>${v}</option>`).join(""); }
function textOf(v) { return Array.isArray(v) ? v.join("\n") : (v || ""); }
function renderLabelForm() {
  const b = state.selected; if (!b) { $("formHost").innerHTML = `<p style="color:var(--muted)">Select a bundle.</p>`; return; }
  const cur = b.current_label || {};
  const sel = (f) => `<select id="f_${f}">${selOpts(ALLOWED[f], cur[f])}</select>`;
  $("formHost").innerHTML = `<form id="labelForm">
    <div class="kv"><div class="k">labeling</div><div class="v">${esc(b.candidate_surface)}</div></div>
    <label>reviewer alias</label><input id="f_reviewer_alias" value="${esc(cur.reviewer_alias || localStorage.getItem('hv_alias') || '')}" />
    <label>coherence</label>${sel("coherence")}<label>investigation worthiness</label>${sel("investigation_worthiness")}
    <label>PoC follow-up worthiness</label>${sel("poc_followup_worthiness")}<label>expected review effort</label>${sel("expected_review_effort")}
    <label>reviewer confidence</label>${sel("reviewer_confidence")}
    <label>missing information</label><textarea id="f_missing_information">${esc(textOf(cur.missing_information))}</textarea>
    <label>counter-signals</label><textarea id="f_counter_signals">${esc(textOf(cur.counter_signals))}</textarea>
    <label>reviewer notes</label><textarea id="f_reviewer_notes">${esc(cur.reviewer_notes || "")}</textarea>
    <div class="row-actions"><button class="btn" type="submit">Save → next</button><button class="btn ghost" type="button" id="saveStay">Save</button></div>
    ${cur.timestamp ? `<div class="notice">Existing label by ${esc(cur.reviewer_alias)} @ ${esc(cur.timestamp)} (saving appends a new row).</div>` : ""}
  </form>`;
  $("labelForm").addEventListener("submit", (e) => { e.preventDefault(); saveLabel(true); });
  $("saveStay").addEventListener("click", () => saveLabel(false));
}
async function saveLabel(advance) {
  const b = state.selected, alias = $("f_reviewer_alias").value.trim();
  if (!alias) return toast("reviewer alias required", true);
  localStorage.setItem("hv_alias", alias);
  const body = { candidate_id: b.candidate_id, reviewer_alias: alias, source_corpus_hash: state.corpusHash, demo: demo() };
  ["coherence", "investigation_worthiness", "poc_followup_worthiness", "expected_review_effort", "reviewer_confidence",
   "missing_information", "counter_signals", "reviewer_notes"].forEach((f) => (body[f] = $("f_" + f).value));
  try { await api("/api/validation/label", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }); }
  catch (e) { return toast("save failed: " + e.message, true); }
  toast("label saved" + (demo() ? " (demo)" : ""));
  state.bundles = (await api("/api/validation/bundles" + dq())).bundles;
  await refreshProgress();
  const next = advance ? filteredSorted().find((x) => x.label_status === "unlabeled") : null;
  state.selected = next || state.bundles.find((x) => x.candidate_id === b.candidate_id);
  renderQueue(); renderDetail(); renderLabelForm();
}
async function refreshProgress() {
  const p = (await api("/api/validation/labels" + dq())).progress;
  $("progFill").style.width = p.percent_complete + "%";
  $("progress").innerHTML =
    `<div class="stat"><span>labeled</span><b>${p.labeled}/${p.total} (${p.percent_complete}%)</b></div>` +
    `<div class="stat"><span>unlabeled</span><b>${p.unlabeled}</b></div>` +
    `<h2>by coherence</h2>${countTable(p.by_coherence)}<h2>by investigation</h2>${countTable(p.by_investigation_worthiness)}` +
    `<h2>by PoC follow-up</h2>${countTable(p.by_poc_followup_worthiness)}`;
  $("driftBanner").style.display = p.corpus_drift ? "block" : "none";
}

/* --------------------------------------------------------- ② promotion */
function promoDraftKey(cid) { return "hv_promo_draft_" + cid; }
function loadPromoDraft(cid) { try { return JSON.parse(localStorage.getItem(promoDraftKey(cid)) || "null"); } catch (e) { return null; } }
function savePromoDraft(cid) {
  if (!cid || !$("p_alias")) return;
  const cats = {};
  PROMO_CATEGORIES.forEach((c) => { cats[c] = { status: $("cat_" + c).value, evidence_ref: $("ev_" + c).value }; });
  const draft = { alias: $("p_alias").value, outcome: $("p_outcome").value, rationale: $("p_rationale").value, cats, ts: Date.now() };
  localStorage.setItem(promoDraftKey(cid), JSON.stringify(draft));
  const note = $("pDraftNote");
  if (note) note.textContent = "✎ draft autosaved locally · " + new Date().toLocaleTimeString();
}
async function renderPromotion() {
  const host = $("promotionHost"), b = state.selected;
  if (!b) { host.innerHTML = `<p style="color:var(--muted)">Select a bundle in ① Review &amp; Label first.</p>`; return; }
  const existing = state.promotions[b.candidate_id];
  const draft = loadPromoDraft(b.candidate_id);
  // A local draft (unsaved edits) takes precedence; else fall back to the committed promotion.
  const src = draft
    ? { alias: draft.alias, outcome: draft.outcome || "—", rationale: draft.rationale || "", cats: draft.cats || {} }
    : { alias: (existing && existing.reviewer_alias) || localStorage.getItem("hv_alias") || "",
        outcome: existing ? existing.outcome : "—", rationale: existing ? existing.rationale : "",
        cats: (existing && existing.categories) || {} };
  const rows = PROMO_CATEGORIES.map((c) => {
    const e = src.cats[c] || {};
    return `<div class="cn">${c.replace(/_/g, " ")}</div>
      <select id="cat_${c}">${selOpts(["—", ...CAT_STATES], e.status || "—")}</select>
      <input id="ev_${c}" placeholder="evidence ref / note" value="${esc(e.evidence_ref || "")}" />`;
  }).join("");
  host.innerHTML = `<h2>Promotion Checklist — ${esc(b.candidate_surface)}</h2>
    <div class="notice">Prioritize, don't verify. 12 categories + a human-chosen outcome. Promotion is <b>not</b> auto-computed; no severity/validity. Edits autosave locally as you type — safe to switch tabs or reload before the formal save.</div>
    <label>reviewer alias</label><input id="p_alias" style="max-width:260px" value="${esc(src.alias)}" />
    <h3>Categories</h3><div class="catgrid"><div class="k">category</div><div class="k">status</div><div class="k">evidence ref</div>${rows}</div>
    <div id="pScore" style="margin-top:10px;color:var(--muted)"></div>
    <label>outcome (human decision)</label><select id="p_outcome" style="max-width:340px">${selOpts(["—", ...OUTCOMES], src.outcome)}</select>
    <label>rationale (no severity / validity / submit / bounty)</label><textarea id="p_rationale">${esc(src.rationale)}</textarea>
    <div class="row-actions"><button class="btn" id="savePromo">Save promotion</button><button class="btn ghost" id="discardDraft">Discard draft</button></div>
    <div id="pDraftNote" style="font-size:11px;color:var(--muted);margin-top:6px">${draft ? "✎ unsaved local draft restored · " + new Date(draft.ts).toLocaleTimeString() : ""}</div>
    ${existing ? `<div class="notice">Last committed: <b>${existing.outcome}</b> · ${existing.progress_score}% · by ${esc(existing.reviewer_alias)}</div>` : ""}`;
  // autosave the local draft on every edit (covers leaving the page / switching tabs / reload)
  const cid = b.candidate_id;
  const onEdit = () => { updatePScore(); savePromoDraft(cid); };
  PROMO_CATEGORIES.forEach((c) => { $("cat_" + c).addEventListener("change", onEdit); $("ev_" + c).addEventListener("input", onEdit); });
  ["p_alias", "p_outcome", "p_rationale"].forEach((id) => { $(id).addEventListener("input", onEdit); $(id).addEventListener("change", onEdit); });
  $("discardDraft").addEventListener("click", () => { localStorage.removeItem(promoDraftKey(cid)); renderPromotion(); toast("local draft discarded"); });
  updatePScore();
  $("savePromo").addEventListener("click", savePromotion);
}
function updatePScore() {
  let score = 0, addressed = 0;
  PROMO_CATEGORIES.forEach((c) => {
    const v = $("cat_" + c).value;
    if (CAT_STATES.includes(v)) { addressed++; score += v === "met" ? 1 : v === "partial" ? 0.5 : 0; }
  });
  const pct = Math.round(1000 * score / PROMO_CATEGORIES.length) / 10;
  $("pScore").textContent = `progress score ${pct}% · ${addressed}/${PROMO_CATEGORIES.length} addressed · ${addressed === PROMO_CATEGORIES.length ? "complete" : "incomplete"}`;
}
async function savePromotion() {
  const b = state.selected, alias = $("p_alias").value.trim(), outcome = $("p_outcome").value;
  if (!alias) return toast("reviewer alias required", true);
  if (!OUTCOMES.includes(outcome)) return toast("choose an outcome", true);
  localStorage.setItem("hv_alias", alias);
  const categories = {};
  for (const c of PROMO_CATEGORIES) {
    const st = $("cat_" + c).value;
    if (!CAT_STATES.includes(st)) return toast(`set status for "${c.replace(/_/g, " ")}"`, true);
    categories[c] = { status: st, evidence_ref: $("ev_" + c).value, notes: "" };
  }
  try {
    await api("/api/validation/promotion", { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ candidate_id: b.candidate_id, reviewer_alias: alias, categories, outcome,
        rationale: $("p_rationale").value, source_corpus_hash: state.corpusHash, demo: demo() }) });
  } catch (e) { return toast("save failed: " + e.message, true); }
  localStorage.removeItem(promoDraftKey(b.candidate_id));  // committed → drop the local draft
  toast("promotion saved" + (demo() ? " (demo)" : ""));
  (await api("/api/validation/promotions" + dq())).promotions.forEach((p) => (state.promotions[p.candidate_id] = p));
  renderPromotion();
}

/* --------------------------------------------------------- ③ chain workspace */
async function renderChain() {
  const host = $("chainHost"), b = state.selected;
  if (!b) { host.innerHTML = `<p style="color:var(--muted)">Select a bundle first.</p>`; return; }
  const promo = state.promotions[b.candidate_id];
  if (!promo || promo.outcome !== "PROMOTE_TO_CHAIN_ANALYSIS") {
    host.innerHTML = `<div class="notice">Chain analysis opens only for <b>PROMOTE_TO_CHAIN_ANALYSIS</b>. Current: <b>${promo ? promo.outcome : "no promotion yet"}</b>. Complete the ② Promotion Checklist first.</div>`;
    return;
  }
  const data = await api(`/api/validation/chain?candidate_id=${encodeURIComponent(b.candidate_id)}` + (demo() ? "&demo=true" : ""));
  const secs = data.sections || {};
  const sectionsHtml = CHAIN_SECTIONS.map((title, i) => {
    const sid = i + 1, s = secs[String(sid)] || {};
    const refs = (s.evidence_references || []).map((r) => `<span class="src">${r.source}</span> ${esc(r.ref)}`).join("<br>");
    return `<div class="section" data-sid="${sid}">
      <div class="sh"><span class="t">${sid}. ${title}</span>
        <span><span class="att ${s.evidence_attached ? "yes" : "no"}">Evidence Attached: ${s.evidence_attached ? "Yes" : "No"}</span></span></div>
      <div class="quick">
        <button class="btn ghost mini" data-ins="⟦UNKNOWN⟧">⟦UNKNOWN⟧</button>
        <button class="btn ghost mini" data-ins="⟦TO CONFIRM VIA PoC⟧">⟦TO CONFIRM VIA PoC⟧</button>
      </div>
      <textarea id="sec_notes_${sid}" placeholder="notes (hypotheses + evidence; tag unknowns)">${esc(s.notes || "")}</textarea>
      <label>code references (comma-sep file:line)</label><input id="sec_code_${sid}" value="${esc((s.code_references || []).join(", "))}" />
      <label>evidence reference</label>
      <div style="display:flex;gap:6px">
        <select id="sec_src_${sid}" style="max-width:170px">${selOpts(EVIDENCE_SOURCES)}</select>
        <input id="sec_ref_${sid}" placeholder="ref (e.g. code_snippet / file:line / observation)" />
      </div>
      <label style="display:inline">evidence attached?</label>
      <select id="sec_att_${sid}" style="max-width:120px">${selOpts(["No", "Yes"], s.evidence_attached ? "Yes" : "No")}</select>
      ${refs ? `<div class="kv"><div class="k">saved evidence</div><div class="v">${refs}</div></div>` : ""}
      <div class="row-actions"><button class="btn mini" data-save="${sid}">Save section ${sid}</button></div>
    </div>`;
  }).join("");
  host.innerHTML = `<div style="display:grid;grid-template-columns:1fr 320px;gap:18px">
    <div>
      <h2>Bug-Chain Builder — ${esc(b.candidate_surface)}</h2>
      <div class="notice">Explain, don't conclude. Hypotheses + evidence + open questions. Impact stays a hypothesis; no severity.</div>
      <div class="kv"><div class="k">candidate_id</div><div class="v">${esc(b.candidate_id)}</div></div>
      <div class="kv"><div class="k">promotion outcome</div><div class="v">${esc(promo.outcome)} · by ${esc(promo.reviewer_alias)}</div></div>
      ${openInEditorHtml(b.abs_path, b.location && b.location.start_line, "Open vulnerable function in VS Code")}
      ${sectionsHtml}
    </div>
    <div>
      <h2>Investigation Status</h2>
      <label>chain reviewer alias</label><input id="c_alias" value="${esc(localStorage.getItem('hv_alias') || '')}" />
      <label>status</label><select id="c_status">${selOpts(STATUS_STATES)}</select>
      <h3>Chain Confidence Evolution</h3>
      <div class="notice">Qualitative, manual — <b>not</b> a verdict / not a severity. Reviewer's confidence in the hypothesis over time.</div>
      <label>initial confidence</label><textarea id="c_init" placeholder="e.g. coherent hypothesis"></textarea>
      <label>current confidence</label><textarea id="c_cur" placeholder="e.g. weaker after counter-signals"></textarea>
      <label>reason for change</label><textarea id="c_reason" placeholder="e.g. invariant protected by secondary check"></textarea>
      <label>status note</label><textarea id="c_note"></textarea>
      <div class="row-actions"><button class="btn" id="saveStatus">Save status</button></div>
      <div class="row-actions"><button class="btn ghost" id="exportPacket">Export investigation packet (.md)</button></div>
      <div class="notice">Export banner: Research Investigation — Not Validated — Not Severity Rated — Not Submission Ready</div>
    </div></div>`;
  host.querySelectorAll("[data-ins]").forEach((btn) => btn.addEventListener("click", (e) => {
    const ta = e.target.closest(".section").querySelector("textarea");
    ta.value += (ta.value && !ta.value.endsWith(" ") ? " " : "") + e.target.dataset.ins; ta.focus();
  }));
  host.querySelectorAll("[data-save]").forEach((btn) => btn.addEventListener("click", () => saveSection(b.candidate_id, +btn.dataset.save)));
  $("saveStatus").addEventListener("click", () => saveStatus(b.candidate_id));
  $("exportPacket").addEventListener("click", () =>
    (window.location = `/api/validation/export/packet?candidate_id=${encodeURIComponent(b.candidate_id)}` + (demo() ? "&demo=true" : "")));
}
async function saveSection(cid, sid) {
  const alias = ($("c_alias") && $("c_alias").value.trim()) || localStorage.getItem("hv_alias") || "";
  if (!alias) return toast("set chain reviewer alias (status panel)", true);
  const ref = $("sec_ref_" + sid).value.trim();
  const body = { candidate_id: cid, reviewer_alias: alias, section_id: sid,
    notes: $("sec_notes_" + sid).value,
    code_references: $("sec_code_" + sid).value.split(",").map((s) => s.trim()).filter(Boolean),
    evidence_references: ref ? [{ source: $("sec_src_" + sid).value, ref }] : [],
    evidence_attached: $("sec_att_" + sid).value === "Yes", demo: demo() };
  try { await api("/api/validation/chain/section", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }); }
  catch (e) { return toast("save failed: " + e.message, true); }
  toast(`section ${sid} saved`); renderChain();
}
async function saveStatus(cid) {
  const alias = $("c_alias").value.trim();
  if (!alias) return toast("reviewer alias required", true);
  localStorage.setItem("hv_alias", alias);
  const body = { candidate_id: cid, reviewer_alias: alias, status: $("c_status").value, note: $("c_note").value,
    initial_confidence: $("c_init").value, current_confidence: $("c_cur").value, reason_for_change: $("c_reason").value, demo: demo() };
  try { await api("/api/validation/status", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }); }
  catch (e) { return toast("save failed: " + e.message, true); }
  toast("status saved");
}

/* --------------------------------------------------------- ④ progress */
async function renderProgressTab() {
  const ov = (await api("/api/validation/investigation" + dq())).overview;
  const card = (n, l) => `<div class="card"><div class="n">${n}</div><div class="l">${l}</div></div>`;
  $("progressHost").innerHTML = `<h2>Investigation Progress</h2>
    <div class="cards">${card(ov.promoted_chains, "Promoted Chains")}${card(ov.chains_in_progress, "In Progress")}
      ${card(ov.chains_blocked, "Blocked")}${card(ov.chains_archived, "Archived")}</div>
    <div class="cards">${card(ov.average_completion + "%", "Avg Completion")}${card(ov.open_questions_count, "Open Questions")}
      ${card(ov.poc_planning_count, "PoC Planning")}${card(Object.keys(ov.by_promotion_outcome || {}).length, "Outcome Types")}</div>
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px">
      <div><h2>by detector</h2>${countTable(ov.by_detector)}</div>
      <div><h2>by confidence</h2>${countTable(ov.by_confidence)}</div>
      <div><h2>by promotion outcome</h2>${countTable(ov.by_promotion_outcome)}</div>
      <div><h2>by investigation status</h2>${countTable(ov.by_investigation_status)}</div>
    </div>`;
}

/* --------------------------------------------------------- tabs + wiring */
function switchTab(name) {
  document.querySelectorAll("nav.tabs button").forEach((b) => b.classList.toggle("active", b.dataset.tab === name));
  document.querySelectorAll(".tabpanel").forEach((p) => p.classList.toggle("active", p.id === "tab-" + name));
  if (name === "promotion") renderPromotion();
  else if (name === "chain") renderChain();
  else if (name === "progress") renderProgressTab();
  else if (name === "allfindings") renderAllFindings();
}

/* (5) All findings (synced) — READ-ONLY mirror across runtime / funnel / detector.
   Runtime & funnel rows are display-only (not labelable/promotable here); each links to its candidate page.
   The corpus label/promote workflow (tabs 1-4) is unchanged and remains detector-corpus-only. */
async function renderAllFindings() {
  const host = $("allFindingsHost");
  let data;
  try { data = await api("/api/validation/all-findings"); }
  catch (e) { host.innerHTML = `<p class="missing">load failed: ${esc(e.message)}</p>`; return; }
  const s = data.summary || {}, bt = s.by_track || {};
  const rows = (data.rows || []).slice().sort((a, b) => (a.glance_rank ?? 99) - (b.glance_rank ?? 99));
  host.innerHTML =
    `<div class="notice">Read-only mirror of every finding across all three tracks
       (<b>runtime</b> ${bt.runtime || 0} &middot; <b>funnel</b> ${bt.funnel || 0} &middot; <b>detector</b> ${bt.detector || 0}).
       Runtime/funnel rows are <b>display-only here</b> — not labelable/promotable from this console; open the
       candidate page for full detail. research_only:true &middot; routing_allowed:false &middot; nothing submittable.</div>
     <table><thead><tr>
       <th>Track</th><th>State</th><th>Readiness</th><th>Subject</th><th>Workspace</th><th>Severity / Conversion</th>
       <th>Duplicate</th><th>Candidate page</th><th>Mode</th>
     </tr></thead><tbody>` +
    rows.map((r) => {
      const href = r.detail_href || ("/candidates?candidate_id=" + encodeURIComponent(r.key || ""));
      const mode = r.labelable ? `labelable (detector)` : `read-only synced`;
      const rd = (r.readiness_state && r.readiness_state !== "not_reviewed") ? esc(r.readiness_state) : "—";
      return `<tr class="row">
        <td>${esc(r.track)}</td><td><b>${esc(r.state)}</b></td><td>${rd}</td><td>${esc(r.subject)}</td>
        <td>${esc(r.workspace)}</td><td>${esc(r.severity_or_conversion ?? "—")}</td>
        <td>${esc(r.duplicate_status ?? "—")}</td>
        <td><a href="${esc(href)}">open →</a></td><td>${esc(mode)}</td></tr>`;
    }).join("") +
    `</tbody></table>`;
}
document.querySelectorAll("nav.tabs button").forEach((b) => b.addEventListener("click", () => switchTab(b.dataset.tab)));
["fSearch", "fDetector", "fConfidence", "fWorkspace", "fLabel"].forEach((id) => $(id).addEventListener("input", renderQueue));
$("queue").querySelectorAll("th[data-k]").forEach((th) => th.addEventListener("click", () => {
  const k = th.dataset.k; state.sortDir = state.sortKey === k ? -state.sortDir : 1; state.sortKey = k; renderQueue();
}));
$("nextUnlabeled").addEventListener("click", () => {
  const n = filteredSorted().find((x) => x.label_status === "unlabeled");
  if (n) selectBundle(n.candidate_id); else toast("no unlabeled bundles in filter");
});
$("demoToggle").addEventListener("change", loadAll);

// editor scheme selector (persisted) for the "Open in VS Code" links
(() => {
  const es = $("editorScheme");
  if (!es) return;
  es.value = editorTarget();
  es.addEventListener("change", () => { localStorage.setItem("hv_editor", es.value);
    if (state.selected) { renderDetail(); if ($("chainHost").innerHTML) renderChain(); } });
})();

// delegated handler for Open-in-editor / copy-path buttons (detail + chain re-render often)
document.addEventListener("click", (e) => {
  const open = e.target.closest(".openEditorBtn");
  if (open) { window.location = editorUri(open.dataset.abs, open.dataset.line); return; }
  const cp = e.target.closest(".copyPathBtn");
  if (cp) {
    const p = displayPath(cp.dataset.abs, cp.dataset.line);
    (navigator.clipboard ? navigator.clipboard.writeText(p) : Promise.reject())
      .then(() => toast("copied: " + p)).catch(() => toast(p));
  }
});

loadAll().catch((e) => toast("load failed: " + e.message, true));
