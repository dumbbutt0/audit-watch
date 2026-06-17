// Blind-to-Reproducible Funnel — read-only view. Renders /api/funnel.
// Reject-first display: REPRODUCED shows a green PoC-proven status AND a distinct amber
// "NOT submitted — human review required" note; the SUBMITTED badge appears only when a human
// recorded submission_status === "SUBMITTED".
(function () {
  "use strict";

  const METRIC_LABELS = [
    ["total_leads_surfaced", "Leads surfaced"],
    ["leads_investigated", "Investigated"],
    ["clean_hits", "Clean hits", true],
    ["strong_partials", "Strong partials"],
    ["severity_fps_before_gate", "Sev FP (pre-gate)"],
    ["severity_fps_after_gate", "Sev FP (post-gate)"],
    ["controls_promoted_incorrectly", "Controls mis-promoted"],
    ["poc_handoffs_started", "PoC handoffs"],
    ["poc_reproduced_total", "PoCs reproduced", true],
    ["partial_reproductions", "Partial repros"],
    ["not_reproduced", "Not reproduced"],
    ["submission_packages_ready_for_human_review", "Submission-ready (human)"],
    ["blocked_submissions", "Blocked submissions"],
    ["not_run", "Not run (excluded)"],
    ["blind_records", "Blind records"],
    ["assisted_records", "Assisted records", true],
    ["assisted_validated_for_poc_handoff", "Assisted → PoC handoff", true],
    ["ready_for_human_review_count", "Ready for human review"],
    ["approved_to_submit_count", "Approved to submit"],
    ["submitted_count", "Submitted"],
    ["accepted_count", "Accepted", true],
    ["duplicate_count", "Duplicate"],
    ["rejected_count", "Rejected"],
    ["pending_count", "Pending outcome"],
    ["invalid_count", "Invalid"],
  ];

  // (P98) assisted-mode provenance + validation-status cell.
  function sourceCell(row) {
    const src = `<span class="pill ${row.source === "assisted" ? "clean" : ""}">${esc(row.source || "blind")}</span>`;
    let av = "";
    if (row.source === "assisted" || row.assisted_validation_status) {
      const cls = { VALIDATED_FOR_POC_HANDOFF: "clean", REJECTED_SOURCE_PROVEN_SAFE: "rej",
                    NEEDS_MORE_CONTEXT: "adj", NEEDS_EXECUTION: "adj",
                    BLOCKED_UNSUPPORTED_CLAIM: "blocked", BLOCKED_SCOPE_OR_DUPLICATE_PENDING: "blocked",
                    NOT_RUN: "" }[row.assisted_validation_status] || "";
      av = `<div><span class="pill ${cls}">${esc(row.assisted_validation_status || "—")}</span></div>`;
      if (row.candidate_invariant_present) av += `<div class="muted" style="font-size:10px">invariant ✓</div>`;
    }
    return src + av;
  }

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  }

  function statusPill(status) {
    const map = {
      POC_REPRODUCED: "repro", PARTIAL_REPRO: "partial", NOT_REPRODUCED: "notrepro",
      BLOCKED: "blocked", CONVERTED_CLEAN_HIT: "clean", CONVERTED_STRONG_PARTIAL: "clean",
      CONVERTED_ADJACENT: "adj", REJECTED_OR_ABSTAINED: "rej", SEVERITY_GATED: "gated",
      SUBMISSION_READY_HUMAN_REVIEW: "repro", SUBMISSION_PACKAGE_STARTED: "adj",
      POC_HANDOFF_STARTED: "adj", NOT_RUN: "rej",
    };
    return `<span class="pill ${map[status] || ""}">${esc(status)}</span>`;
  }

  function convPill(c) {
    const cls = { CLEAN_HIT: "clean", STRONG_PARTIAL: "clean", ADJACENT: "adj",
                  REJECTED: "rej", ABSTAINED: "rej", NONE: "rej" }[c] || "";
    return `<span class="pill ${cls}">${esc(c)}</span>`;
  }

  function pocPill(p) {
    const cls = { REPRODUCED: "repro", PARTIAL_REPRO: "partial", NOT_REPRODUCED: "notrepro",
                  IN_PROGRESS: "adj", NOT_STARTED: "rej" }[p] || "";
    return `<span class="pill ${cls}">${esc(p)}</span>`;
  }

  // Reject-first submission cell: explicit badge + an unmistakable "not submitted" note whenever a
  // finding is proven but not actually submitted. SUBMITTED is driven ONLY by row.submitted (a human
  // outcome record); it is NEVER inferred from READY_FOR_HUMAN_REVIEW / submission_status.
  function submissionCell(row) {
    const badge = `<span class="subbadge sub-${esc(row.submission_badge)}">${esc(row.submission_badge)}</span>`;
    let note = "";
    const proven = row.pipeline_status === "POC_REPRODUCED" || row.poc_status === "REPRODUCED";
    if (proven && !row.submitted) {
      note = `<div class="notsubmitted">⚠ NOT submitted — human review required</div>`;
    }
    return badge + note;
  }

  // (P99) Human-final-gate + outcome cell. SUBMITTED chip appears ONLY when an explicit human outcome record
  // set submitted=true. Everything else surfaces the gate + outcome status.
  function humanGateCell(row) {
    const gcls = { APPROVED_TO_SUBMIT: "clean", PENDING: "" }[row.human_final_gate] || "blocked";
    const gate = `<span class="pill ${gcls}">${esc(row.human_final_gate || "PENDING")}</span>`;
    const submitted = row.submitted
      ? `<div><span class="pill clean">SUBMITTED</span>${row.platform ? " " + esc(row.platform) : ""}${row.submission_id ? " #" + esc(row.submission_id) : ""}</div>`
      : `<div class="muted" style="font-size:10px">not submitted</div>`;
    const ocls = { accepted: "clean", duplicate: "adj", rejected: "rej", invalid: "rej",
                   pending: "", informative: "adj", withdrawn: "rej", needs_revision: "blocked" }[row.outcome] || "";
    let outcome = `<div><span class="pill ${ocls}">${esc(row.outcome || "pending")}</span></div>`;
    if (row.awarded_severity) outcome += `<div class="muted" style="font-size:10px">awarded ${esc(row.awarded_severity)}</div>`;
    if (row.duplicate_of) outcome += `<div class="muted" style="font-size:10px">dup of ${esc(row.duplicate_of)}</div>`;
    if (row.rejection_reason) outcome += `<div class="muted" style="font-size:10px">${esc(row.rejection_reason)}</div>`;
    // human-review sub-checks (scope / duplicate / severity) — shown when the package is in human review.
    let checks = "";
    if (row.pipeline_status === "SUBMISSION_READY_HUMAN_REVIEW") {
      checks = `<div class="muted" style="font-size:10px">scope ${esc(row.scope_check || "PENDING")} ·`
             + ` dup ${esc(row.duplicate_check || "PENDING")} · sev ${esc(row.severity_check || "PENDING")}</div>`;
    }
    return gate + submitted + outcome + checks;
  }

  function artifactCell(row) {
    const links = row.artifact_links || {};
    const parts = [];
    if (links.test_file) parts.push(`<div class="src">test: ${esc(row.poc.test_file)}</div>`);
    if (links.poc_artifact_dir) parts.push(`<div class="src">dir: ${esc(row.poc.poc_artifact_dir)}</div>`);
    if (links.evidence_bundle_path) parts.push(`<div class="src">bundle: ${esc(row.submission.evidence_bundle_path)}</div>`);
    return parts.join("") || '<span class="muted">—</span>';
  }

  function renderMetrics(m) {
    const el = document.getElementById("metrics");
    el.innerHTML = METRIC_LABELS.map(([k, label, hi]) => {
      const v = m && m[k] != null ? m[k] : 0;
      return `<div class="metric ${hi ? "hi" : ""}"><div class="l">${esc(label)}</div><div class="v">${esc(v)}</div></div>`;
    }).join("");

    const bel = document.getElementById("blockers");
    const tb = (m && m.top_blocker_reasons) || [];
    if (tb.length) {
      bel.style.display = "block";
      bel.innerHTML = "<b>Top blocker reasons</b>" +
        tb.map(([reason, n]) => `<div class="b"><span>${esc(reason)}</span><span class="muted">×${esc(n)}</span></div>`).join("");
    } else {
      bel.style.display = "none";
    }
  }

  // (P100) Focused-view scope. Default "focused" = assisted arc + ready-for-human-review (the proven set);
  // "all" shows every record. Non-destructive: filters table rows only — metric tiles always reflect all N.
  let SCOPE = "focused";
  let ALL_ROWS = [];

  function renderScopeBar(rows) {
    const total = rows.length;
    const foc = rows.filter((r) => r.focused).length;
    const bar = document.getElementById("scopeBar");
    if (!bar) return;
    const on = (s) => (SCOPE === s ? "background:var(--panel);font-weight:700;" : "");
    bar.innerHTML =
      `<button id="scopeFocused" class="btn ghost" style="${on("focused")}">Focused (${foc})</button>` +
      `<button id="scopeAll" class="btn ghost" style="${on("all")}">Show all (${total})</button>` +
      `<span class="muted" style="font-size:11px">` +
      (SCOPE === "focused"
        ? `Showing ${foc} of ${total} findings (assisted arc + ready-for-human-review). Metric tiles above reflect all ${total}.`
        : `Showing all ${total} findings. Metric tiles reflect all ${total}.`) +
      `</span>`;
    document.getElementById("scopeFocused").onclick = () => { SCOPE = "focused"; draw(); };
    document.getElementById("scopeAll").onclick = () => { SCOPE = "all"; draw(); };
  }

  function draw() {
    renderScopeBar(ALL_ROWS);
    const shown = SCOPE === "focused" ? ALL_ROWS.filter((r) => r.focused) : ALL_ROWS;
    renderRows(shown);
  }

  function renderRows(rows) {
    const body = document.getElementById("fnBody");
    if (!rows || !rows.length) {
      const msg = SCOPE === "focused"
        ? 'No findings in the Focused view — click "Show all".'
        : "No funnel records found.";
      body.innerHTML = `<tr><td colspan="16" class="muted">${msg}</td></tr>`;
      return;
    }
    body.innerHTML = rows.map((r) => {
      const rankScore = `${r.blind_rank != null ? "#" + esc(r.blind_rank) : "—"} / ${r.surface_score != null ? esc(r.surface_score) : "—"}`;
      const ctrl = r.control ? ' <span class="pill ctrl">control</span>' : "";
      const cmd = r.test_command ? `<div class="cmd">${esc(r.test_command)}</div>` : "";
      return `<tr>
        <td>${esc(r.subject)}${ctrl}</td>
        <td>${esc(r.phase_discovered)}</td>
        <td>${esc(r.finding_id || "—")}</td>
        <td class="src">${esc(r.contract_function)}</td>
        <td>${sourceCell(r)}</td>
        <td>${rankScore}</td>
        <td>${convPill(r.conversion)}</td>
        <td>${esc(r.mechanism_correctness || "—")}</td>
        <td>${esc(r.severity_gate)}${r.severity_fp ? ' <span class="pill notrepro">FP</span>' : ""}</td>
        <td>${esc(r.adversarial_result)}</td>
        <td>${statusPill(r.pipeline_status)}</td>
        <td>${pocPill(r.poc_status)}${cmd}</td>
        <td>${submissionCell(r)}</td>
        <td>${humanGateCell(r)}</td>
        <td class="muted">${esc(r.blocker_reason || "")}</td>
        <td>${artifactCell(r)}</td>
      </tr>`;
    }).join("");
  }

  async function load() {
    try {
      const res = await fetch("/api/funnel");
      const data = await res.json();
      renderMetrics(data.metrics);
      ALL_ROWS = data.records || [];
      draw();  // (P100) scope-aware render: tiles = all N; table = Focused subset by default
    } catch (e) {
      document.getElementById("fnBody").innerHTML =
        `<tr><td colspan="16" class="muted">Failed to load: ${esc(e)}</td></tr>`;
    }
  }

  load();
  setInterval(load, 10000);
})();
