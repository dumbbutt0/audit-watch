/* Audit Watch — frontend logic.
   Single-file vanilla JS. Polls /api/state; falls back to MOCK_STATE
   when the backend is unreachable (e.g. opening the file directly). */

(() => {
  "use strict";

  // ───────────────────────────────────────────────────────── persisted state
  // Global state (chat, UI prefs) — keyed by "auditwatch_v1_global"
  const LS_GLOBAL_KEY = "auditwatch_v1_global";
  // Per-audit state (filters, sort, starred, detail, page) — keyed by audit id
  const lsAuditKey = (auditId) => `auditwatch_v1_${auditId || "default"}`;

  const _loadObj = (key) => { try { return JSON.parse(localStorage.getItem(key)) || {}; } catch { return {}; } };
  const _saveObj = (key, obj) => { try { localStorage.setItem(key, JSON.stringify(obj)); } catch {} };

  // Global persisted (chat etc.)
  const global_p = _loadObj(LS_GLOBAL_KEY);
  global_p.chat = global_p.chat || { open: false, history: [] };
  global_p.chat.queue = global_p.chat.queue || [];
  global_p.chat.queueOpen = global_p.chat.queueOpen ?? true;
  global_p.chat.height = Math.max(220, global_p.chat.height || 360);
  const saveGlobal = () => _saveObj(LS_GLOBAL_KEY, global_p);

  // Per-audit persisted state (mutable; re-loaded when audit switches)
  let _auditLsKey = lsAuditKey(null);
  let _auditP = _loadObj(_auditLsKey);
  const _initAuditP = (p) => {
    p.starred = p.starred || [];
    p.filters = p.filters || {};
    p.sort = p.sort || { col: "triage_score", dir: "desc" };
    p.detail = p.detail || { open: false, id: null };
    p.page = p.page ?? 1;
    return p;
  };
  _initAuditP(_auditP);

  // Proxy-like object so all existing `persisted.X` references work unchanged
  const persisted = new Proxy({}, {
    get(_, k) {
      if (k === "chat") return global_p.chat;
      return _auditP[k];
    },
    set(_, k, v) {
      if (k === "chat") { global_p.chat = v; return true; }
      _auditP[k] = v; return true;
    },
  });
  const savePersisted = () => {
    _saveObj(_auditLsKey, _auditP);
    saveGlobal();
  };

  // Switch per-audit state when active audit changes
  let _currentAuditId = null;
  function _switchAuditState(auditId) {
    if (auditId === _currentAuditId) return;
    // Save current state before switching
    _saveObj(_auditLsKey, _auditP);
    _currentAuditId = auditId;
    _auditLsKey = lsAuditKey(auditId);
    _auditP = _initAuditP(_loadObj(_auditLsKey));
  }

  document.documentElement.style.setProperty("--chat-h", global_p.chat.height + "px");

  // ─────────────────────────────────────────────────────────── live state
  let state = null;           // latest server state
  let prevState = null;       // for diff highlighting
  const POLL_MS = 10_000;
  const ERROR_RETRY_MS = 5_000;
  let countdown = POLL_MS / 1000;
  let pollTimer = null;
  let countTimer = null;
  let polling = false;

  // ────────────────────────── SSE (instant push; falls back to polling)
  let _evtSource = null;
  function _connectSSE() {
    if (_evtSource) { try { _evtSource.close(); } catch(_) {} }
    _evtSource = new EventSource("/api/events");
    _evtSource.addEventListener("state_changed", () => {
      clearTimeout(pollTimer);
      countdown = POLL_MS / 1000;
      if (!polling) poll();
    });
    _evtSource.onerror = () => {
      // SSE will auto-reconnect — polling acts as fallback safety net
    };
  }
  _connectSSE();


  // ────────────────────────────────────────────────────────── DOM refs
  const $ = (id) => document.getElementById(id);
  const refs = {
    contractName: $("contractName"),
    lastUpdated:  $("lastUpdated"),
    countdown:    $("countdown"),
    refreshBtn:   $("refreshBtn"),
    pollDot:      $("pollDot"),
    reconnect:    $("reconnect"),
    pillSubmit:   $("pillSubmit"),
    pillPoc:      $("pillPoc"),
    pillDown:     $("pillDown"),
    pillRej:      $("pillRej"),
    stepper:      $("stepper"),
    kbStatus:     $("kbStatus"),
    kbStatusLbl:  $("kbStatusLbl"),
    kbCount:      $("kbCount"),
    kbLastSync:   $("kbLastSync"),
    kbCycles:     $("kbCycles"),
    kbLog:        $("kbLog"),
    searchInp:    $("searchInp"),
    sevSel:       $("sevSel"),
    triageSel:    $("triageSel"),
    agentSel:     $("agentSel"),
    actionSel:    $("actionSel"),
    gateSel:      $("gateSel"),
    clearBtn:     $("clearBtn"),
    donut:        $("donut"),
    donutTotal:   $("donutTotal"),
    legend:       $("legend"),
    funnelBar:    $("funnelBar"),
    showingN:     $("showingN"),
    showingM:     $("showingM"),
    tblHead:      $("tblHead"),
    tblBody:      $("tblBody"),
    pageInfo:     $("pageInfo"),
    prevBtn:      $("prevBtn"),
    nextBtn:      $("nextBtn"),
    detailPanel:  $("detailPanel"),
    mainGrid:     $("mainGrid"),
    barLeft:      $("barLeft"),
    barCenter:    $("barCenter"),
    barRight:     $("barRight"),
    toast:        $("toast"),
    chatPanel:    $("chatPanel"),
    chatMsgs:     $("chatMsgs"),
    runQueue:     $("runQueue"),
    chatInput:    $("chatInput"),
    chatSend:     $("chatSend"),
    chatToggle:   $("chatToggle"),
    chatReset:    $("chatReset"),
    chatClose:    $("chatClose"),
    chatHandle:   $("chatHandle"),
  };

  // ──────────────────────────────────────────────────────────── helpers
  const PAGE_SIZE = 25;
  const SEV_RANK = { Critical: 4, High: 3, Medium: 2, Low: 1, Informational: 0 };
  const SEV_KEY  = (s) => (s || "").toLowerCase();
  const sevClass = (s) => "sev-" + SEV_KEY(s).replace(/\s+/g, "-");
  const titleCase = (s) => s ? s[0].toUpperCase() + s.slice(1) : s;
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]));

  const relTime = (iso) => {
    if (!iso) return "—";
    const t = new Date(iso).getTime();
    if (isNaN(t)) return iso;
    const diff = Math.max(0, Date.now() - t) / 1000;
    if (diff < 60) return Math.floor(diff) + "s ago";
    if (diff < 3600) return Math.floor(diff / 60) + "m ago";
    if (diff < 86400) return Math.floor(diff / 3600) + "h ago";
    return Math.floor(diff / 86400) + "d ago";
  };
  const timeShort = (iso) => {
    if (!iso) return "—";
    const d = new Date(iso);
    if (isNaN(d)) return iso;
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  };

  const scoreColor = (score, max = 35) => {
    if (score == null) return "var(--muted)";
    const t = Math.max(0, Math.min(1, score / max));
    const hue = Math.round(t * 110); // 0=red → 110=green
    return `hsl(${hue} 60% 50%)`;
  };

  // ─────────────────────────────────────────────────────── data fetching
  async function poll() {
    polling = true;
    refs.pollDot.classList.add("polling");
    try {
      let data;
      try {
        const res = await fetch("/api/state", { cache: "no-store" });
        if (!res.ok) throw new Error(res.statusText);
        data = await res.json();
      } catch {
        // Backend unreachable → mock fallback.
        data = JSON.parse(JSON.stringify(window.MOCK_STATE));
        data.timestamp = new Date().toISOString();
      }
      refs.reconnect.classList.remove("show");
      onState(data);
      countdown = POLL_MS / 1000;
    } catch (err) {
      console.error("poll", err);
      refs.reconnect.classList.add("show");
      refs.pollDot.classList.add("error");
      // retry sooner on error
      clearTimeout(pollTimer);
      pollTimer = setTimeout(poll, ERROR_RETRY_MS);
      return;
    } finally {
      polling = false;
      refs.pollDot.classList.remove("polling");
    }
    clearTimeout(pollTimer);
    pollTimer = setTimeout(poll, POLL_MS);
  }

  function onState(next) {
    prevState = state;
    state = next;
    refs.lastUpdated.textContent = timeShort(next.timestamp);
    // Switch per-audit localStorage if active audit changed
    const newAuditId = (next.active_audit || {}).audit_id || null;
    if (newAuditId !== _currentAuditId) {
      _switchAuditState(newAuditId);
    }
    render();
    renderAuditInfoCard(next.active_audit || null);
    renderSyncStatusCard(next.sync_status || null);
    renderAllTracksCard(next.all_tracks || null);
    // Keep switcher in sync (audit_id may change after a switch command)
    if ((next.active_audit || {}).audit_id !== ((prevState || {}).active_audit || {}).audit_id) {
      fetchAudits().then(d => renderAuditSwitcher(d.audits, d.active_audit_id));
    }
    if (prevState && prevState.timestamp !== next.timestamp) {
      showToast("Updated");
    }
  }

  function showToast(msg) {
    refs.toast.textContent = msg;
    refs.toast.classList.add("show");
    clearTimeout(showToast._t);
    showToast._t = setTimeout(() => refs.toast.classList.remove("show"), 2000);
  }

  // ────────────────────────────────────────────────────── countdown
  function tickCountdown() {
    if (countdown <= 0) {
      refs.countdown.textContent = "0s";
      return;
    }
    countdown -= 1;
    refs.countdown.textContent = countdown + "s";
  }
  countTimer = setInterval(tickCountdown, 1000);
  refs.refreshBtn.addEventListener("click", () => {
    clearTimeout(pollTimer);
    countdown = POLL_MS / 1000;
    poll();
  });

  // ────────────────────────────────────────────────────── header
  function renderHeader(s) {
    const stat1 = s.pipeline.stage_1_static;
    const auditName = (s.active_audit || {}).name || null;
    refs.contractName.textContent = auditName || stat1.contract_path || "—";
    refs.contractName.title = stat1.contract_path || stat1.detail || "";

    const f = s.triage_funnel;
    refs.pillSubmit.textContent = f.submit;
    refs.pillPoc.textContent    = f.poc_required;
    refs.pillDown.textContent   = f.downgraded;
    refs.pillRej.textContent    = f.rejected;
    const pillChain = document.getElementById("pillChain");
    if (pillChain) pillChain.textContent = f.chained || 0;
  }

  // ────────────────────────────────────────────────────── sidebar
  function stageIcon(stage) {
    if (stage.done) return { cls: "done", glyph: "●" };
    const hasAny = Object.values(stage).some(v => typeof v === "number" && v > 0);
    if (hasAny) return { cls: "progress", glyph: "⟳" };
    return { cls: "idle", glyph: "○" };
  }

  function renderSidebar(s) {
    const p = s.pipeline;
    const stages = [
      {
        n: "01", title: "Static Analysis", stage: p.stage_1_static,
        body: () => p.stage_1_static.contract_path
          ? `<div class="detail">${esc(p.stage_1_static.contract_path)}</div>
             <div class="breakdown"><span>solc <b>${esc(p.stage_1_static.compiler)}</b></span><span><b>${p.stage_1_static.function_count}</b> functions</span></div>`
          : `<div class="detail">awaiting compile</div>`
      },
      {
        n: "02", title: "Agent Discovery", stage: p.stage_2_agents,
        body: () => {
          const fpa = p.stage_2_agents.findings_per_agent || {};
          const agents = (p.stage_2_agents.agents_run || []);
          const rows = agents.map(a => `<div class="row"><span>${esc(a)}</span><span>${fpa[a] ?? 0}</span></div>`).join("");
          return `<div class="breakdown">
              <span><b>${agents.length}</b> agents run</span>
              <span class="info"><b>${p.stage_2_agents.total_raw ?? p.stage_2_agents.finding_count}</b> raw findings</span>
            </div>
            ${agents.length ? `<details class="agent-list" style="margin-top:6px"><summary style="font-size:11px;cursor:pointer;color:var(--muted);list-style:none;padding-bottom:4px">Per-agent breakdown</summary>${rows}</details>` : ""}`;
        }
      },
      {
        n: "03", title: "Report Generation", stage: p.stage_3_report,
        body: () => `<div class="breakdown">
            <span class="ok">merged.json ✓</span>
            <span><b>${p.stage_3_report.compound_risk_count}</b> compound</span>
          </div>`
      },
      {
        n: "04", title: "Triage", stage: p.stage_4_triage,
        body: () => {
          const t = p.stage_4_triage;
          return `<div class="mini-funnel">
            <div class="cell submit"><span class="n">${t.submit}</span><span class="l">Submit</span></div>
            <div class="cell poc"><span class="n">${t.poc_required}</span><span class="l">PoC</span></div>
            <div class="cell down"><span class="n">${t.downgraded}</span><span class="l">Down</span></div>
            <div class="cell rej"><span class="n">${t.rejected}</span><span class="l">Reject</span></div>
          </div>`;
        }
      },
      {
        n: "05", title: "Specialist Review", stage: p.stage_5_specialist,
        body: () => {
          const t = p.stage_5_specialist;
          const tot = t.total_findings;
          return `<div class="breakdown">
            <span>Exploit <b>${t.exploitability_done}/${tot}</b></span>
            <span>Judge <b>${t.judge_done}/${tot}</b></span>
            <span>Severity <b>${t.severity_done}/${tot}</b></span>
          </div>`;
        }
      },
      {
        n: "06", title: "PoC Execution", stage: p.stage_6_poc,
        body: () => {
          const t = p.stage_6_poc;
          const ld = t.level_dist || {};
          return `<div class="breakdown">
            <span class="ok">✓ <b>${t.proved}</b></span>
            <span class="bad">✗ <b>${t.failed}</b></span>
            <span>○ <b>${t.pending}</b></span>
          </div>
          <div class="breakdown" style="margin-top:4px">
            <span>L3C <b>${ld.L3C ?? 0}</b></span>
            <span>L3B <b>${ld.L3B ?? 0}</b></span>
            <span>L3A <b>${ld.L3A ?? 0}</b></span>
            <span>L2 <b>${ld.L2 ?? 0}</b></span>
          </div>`;
        }
      },
      {
        n: "07", title: "Quality Checklist", stage: p.stage_7_checklist,
        body: () => {
          const t = p.stage_7_checklist;
          return `<div class="breakdown">
            <span class="ok">✓ <b>${t.passed ?? t.ready ?? 0}</b> passed</span>
            <span class="warn">⚠ <b>${t.conditional ?? 0}</b> cond</span>
            <span class="bad">✗ <b>${t.failed ?? t.blocked ?? 0}</b> failed</span>
          </div>`;
        }
      },
      {
        n: "08", title: "Completeness Gate", stage: p.stage_8_gate,
        body: () => {
          const t = p.stage_8_gate;
          return `<div class="breakdown">
            <span class="ok"><b>${t.high_supported}</b> High supported</span>
            <span class="warn"><b>${t.ceiling_downgraded ?? t.downgraded_to_medium ?? 0}</b> capped → Med</span>
            <span class="bad"><b>${t.upgrade_required ?? 0}</b> upgrade req</span>
          </div>`;
        }
      },
      {
        n: "8.5", title: "PoC Validation",
        stage: (() => { const m = (s.poc_validation || {}).summary || {}; return { done: (m.submission_ready || 0) > 0, ...m }; })(),
        body: () => {
          const v = s.poc_validation || {}; const m = v.summary || {};
          if (!v.summary) return `<div class="d">no engagement report yet — run poc-engagement-report</div>`;
          const fixes = (v.top_fix_items || []).slice(0, 3)
            .map(it => `${esc(it.finding_id)} → ${esc(it.recommended_next_action)}`).join("<br>");
          const fallback = (v.top_next_actions || []).slice(0, 3).map(a => `${a[0]} ×${a[1]}`).join(", ");
          const modeTag = v.mode ? `<span class="d" style="font-size:10px;opacity:.7"> [${esc(v.mode)}]</span>` : "";
          return `<div class="breakdown">
            <span class="ok"><b>${m.submission_ready || 0}</b> submit-ready${modeTag}</span>
            <span class="bad"><b>${m.high_critical_blocked || 0}</b> H/C blocked</span>
            <span class="warn"><b>${m.missing_poc || 0}</b> missing PoC</span>
            <span class="info"><b>${m.invalid_or_setup_only || 0}</b> invalid/setup</span>
          </div>${fixes
            ? `<div class="d" style="margin-top:6px;font-size:11px">fix next:<br>${fixes}</div>`
            : (fallback ? `<div class="d" style="margin-top:6px;font-size:11px">next: ${esc(fallback)}</div>` : "")
          }${v.operator_worklist_count
            ? `<div class="d" style="margin-top:4px;font-size:10px;opacity:.7">worklist: ${v.operator_worklist_count} item(s)</div>`
            : ""}`;
        }
      },
    ];

    refs.stepper.innerHTML = stages.map(({ n, title, stage, body }) => {
      const ic = stageIcon(stage);
      return `<div class="stage ${ic.cls}">
        <div class="icon">${ic.glyph}</div>
        <div class="title"><span class="num">${n}</span> ${esc(title)}</div>
        ${body()}
      </div>`;
    }).join("");

    // Deep Analysis card
    const da = s.deep_analysis || {};
    const $da = (id) => document.getElementById(id);
    if ($da("daInvariants")) {
      $da("daInvariants").textContent = da.invariants_extracted == null ? "—" : `${da.invariants_extracted} (${da.high_suspicion_invariants ?? 0} high)`;
      $da("daHighSusp").textContent   = da.high_suspicion_invariants ?? "—";
      $da("daChains").textContent     = da.interaction_chains_mapped ?? "—";
      $da("daDangerous").textContent  = da.dangerous_chains ?? "—";
      $da("daThreads").textContent    = da.threads_traced ?? "—";
      $da("daCritHigh").textContent   = da.threads_traced == null ? "—" : `${da.critical_threads ?? 0} / ${da.high_threads ?? 0}`;
      $da("daDeadEnds").textContent   = da.dead_ends ?? "—";
      $da("daDtFindings").textContent = da.deep_trace_findings ?? "—";
    }

    // KB card
    const kb = s.kb || {};
    if (kb.continuous_running) {
      refs.kbStatus.classList.remove("off");
      refs.kbStatusLbl.textContent = "RUNNING";
    } else {
      refs.kbStatus.classList.add("off");
      refs.kbStatusLbl.textContent = "STOPPED";
    }
    refs.kbCount.textContent    = kb.total_findings == null ? "—" : kb.total_findings.toLocaleString();
    refs.kbLastSync.textContent = relTime(kb.last_run);
    refs.kbCycles.textContent   = kb.cycles ?? "—";
    refs.kbLog.textContent      = (kb.scraper_log_tail || []).slice(-3).join("\n") || "(no log lines)";
  }

  // ────────────────────────────────────────────────────── filter bar
  function rebuildAgentFilter(findings) {
    const agents = [...new Set(findings.map(f => f.agent).filter(Boolean))].sort();
    const cur = refs.agentSel.value;
    refs.agentSel.innerHTML = `<option value="">All</option>` +
      agents.map(a => `<option value="${esc(a)}"${a === cur ? " selected" : ""}>${esc(a)}</option>`).join("");
  }

  function applyFiltersAndSort(findings) {
    const f = persisted.filters;
    let rows = findings.slice();

    if (f.search) {
      const q = f.search.toLowerCase();
      rows = rows.filter(r =>
        (r.id || "").toLowerCase().includes(q) ||
        (r.title || "").toLowerCase().includes(q));
    }
    if (f.severity) {
      rows = rows.filter(r => {
        const sev = r.severity_ceiling || r.calibrated_severity || r.recommended_severity || r.raw_severity;
        return (sev || "").toLowerCase() === f.severity.toLowerCase();
      });
    }
    if (f.triage) rows = rows.filter(r => r.triage_status === f.triage);
    if (f.agent)  rows = rows.filter(r => r.agent === f.agent);
    if (f.action) rows = rows.filter(r => (r.final_action || "").toLowerCase() === f.action);
    if (f.gate) {
      rows = rows.filter(r => {
        const ceil = (r.severity_ceiling || "").toLowerCase();
        if (f.gate === "supported") return ceil === "high" && !r.upgrade_required;
        if (f.gate === "capped")    return ceil === "medium" || ceil === "low";
        if (f.gate === "upgrade")   return !!r.upgrade_required;
        return true;
      });
    }

    const { col, dir } = persisted.sort;
    const mul = dir === "asc" ? 1 : -1;
    rows.sort((a, b) => {
      let av, bv;
      if (col === "severity") {
        av = SEV_RANK[a.severity_ceiling || a.calibrated_severity || a.raw_severity] ?? -1;
        bv = SEV_RANK[b.severity_ceiling || b.calibrated_severity || b.raw_severity] ?? -1;
      } else if (col === "starred") {
        av = persisted.starred.includes(a.id) ? 1 : 0;
        bv = persisted.starred.includes(b.id) ? 1 : 0;
      } else if (col === "poc_level") {
        const rank = { L3C: 4, L3B: 3, L3A: 2, L2: 1 };
        av = rank[a.poc_level] ?? 0;
        bv = rank[b.poc_level] ?? 0;
      } else if (col === "duplicate_risk") {
        const rank = { low: 1, medium: 2, high: 3 };
        av = rank[a.duplicate_risk] ?? 0;
        bv = rank[b.duplicate_risk] ?? 0;
      } else {
        av = a[col]; bv = b[col];
      }
      if (av == null && bv == null) return 0;
      if (av == null) return 1;
      if (bv == null) return -1;
      if (typeof av === "string" && typeof bv === "string") return av.localeCompare(bv) * mul;
      return (av < bv ? -1 : av > bv ? 1 : 0) * mul;
    });

    return rows;
  }

  function renderSortIndicators() {
    const { col, dir } = persisted.sort;
    refs.tblHead.querySelectorAll("th").forEach(th => {
      th.classList.toggle("sorted", th.dataset.col === col);
      const span = th.querySelector(".sort");
      if (span) span.textContent = th.dataset.col === col ? (dir === "asc" ? "▴" : "▾") : "▾";
    });
  }

  // ────────────────────────────────────────────────────── summary
  let donutChart = null;
  function renderSummary(s, visible) {
    const sd = s.severity_distribution || {};
    // recompute from visible rows so the donut tracks active filters
    const dist = { Critical: 0, High: 0, Medium: 0, Low: 0, Informational: 0 };
    visible.forEach(r => {
      const sev = r.severity_ceiling || r.calibrated_severity || r.raw_severity || "Informational";
      const key = ["Critical","High","Medium","Low","Informational"].find(k => k.toLowerCase() === sev.toLowerCase()) || "Informational";
      dist[key] += 1;
    });

    const labels = ["Critical", "High", "Medium", "Low", "Informational"];
    const colors = ["#dc2626", "#ea580c", "#d97706", "#65a30d", "#6b7280"];
    const values = labels.map(l => dist[l] || 0);
    const total = values.reduce((a, b) => a + b, 0);
    refs.donutTotal.textContent = total;

    if (donutChart) {
      donutChart.data.datasets[0].data = values;
      donutChart.update("none");
    } else {
      donutChart = new Chart(refs.donut, {
        type: "doughnut",
        data: { labels, datasets: [{ data: values, backgroundColor: colors, borderWidth: 0 }] },
        options: {
          cutout: "68%",
          responsive: false,
          animation: false,
          plugins: { legend: { display: false }, tooltip: { enabled: true } }
        }
      });
    }

    refs.legend.innerHTML = labels.map((l, i) =>
      `<div class="item"><span class="swatch" style="background:${colors[i]}"></span>${l} <b>${values[i]}</b></div>`
    ).join("");

    // funnel bar from total state (not filtered) so it reflects real pipeline
    const f = s.triage_funnel;
    const segs = [
      { v: f.submit,       cls: "submit",    color: "var(--submit)" },
      { v: f.poc_required, cls: "poc",       color: "var(--poc)" },
      { v: f.downgraded,   cls: "downgrade", color: "var(--downgrade)" },
      { v: f.rejected,     cls: "reject",    color: "var(--reject)" },
      { v: f.chained || 0, cls: "chain",     color: "var(--chain)" },
    ];
    const ftot = segs.reduce((a, s) => a + s.v, 0) || 1;
    refs.funnelBar.innerHTML = segs.map(s =>
      s.v ? `<div class="seg ${s.cls}" style="width:${(s.v / ftot * 100).toFixed(1)}%;background:${s.color}" title="${s.cls}: ${s.v}">${s.v}</div>` : ""
    ).join("");

    refs.showingN.textContent = visible.length;
    refs.showingM.textContent = s.findings.length;
  }

  // ────────────────────────────────────────────────────── table
  function dotRow(score, max = 5) {
    if (score == null) return `<span class="dots">${Array.from({length: max}, () => `<span class="d"></span>`).join("")}</span>`;
    let html = "";
    for (let i = 0; i < max; i++) html += `<span class="d${i < score ? " on" : ""}"></span>`;
    return `<span class="dots">${html}</span>`;
  }

  function sevBadge(sev) {
    if (!sev) return `<span class="badge sev-info">—</span>`;
    return `<span class="badge ${sevClass(sev)}">${esc(sev)}</span>`;
  }

  function sevChain(raw, ceiling, upgrade) {
    if (!ceiling || raw === ceiling) {
      return `<span class="sev-chain">${sevBadge(raw || ceiling)}${upgrade ? `<span class="warn" title="Upgrade required">⚠</span>` : ""}</span>`;
    }
    return `<span class="sev-chain">${sevBadge(raw)}<span class="arrow">→</span>${sevBadge(ceiling)}${upgrade ? `<span class="warn" title="Upgrade required">⚠</span>` : ""}</span>`;
  }

  function pocCell(r) {
    if (!r.poc_level) return `<span class="poc-cell"><span class="ico pending">○</span><span style="color:var(--muted)">—</span></span>`;
    const ico = r.poc_status === "proved" ? `<span class="ico proved">✓</span>`
             : r.poc_status === "failed"   ? `<span class="ico failed">✗</span>`
             : `<span class="ico pending">○</span>`;
    const lvlClass = r.poc_level.toLowerCase().replace(/[^a-z0-9]/g, "");
    return `<span class="poc-cell"><span class="lvl ${lvlClass}${r.upgrade_required ? " upgrade" : ""}">${esc(r.poc_level)}</span>${ico}</span>`;
  }

  function actionPill(act) {
    if (!act) return `<span class="action-pill dash">—</span>`;
    const k = String(act).toLowerCase();
    return `<span class="action-pill ${k}">${esc(act.toUpperCase())}</span>`;
  }

  function judgePill(o) {
    if (!o) return `<span class="judge-pill dash">—</span>`;
    const k = String(o).toLowerCase();
    return `<span class="judge-pill ${k}">${esc(o)}</span>`;
  }

  function dupPill(r) {
    const v = (r || "").toLowerCase();
    if (!v || v === "unknown") return `<span class="dup-pill dash">—</span>`;
    return `<span class="dup-pill ${v}">${esc(v)}</span>`;
  }

  function renderTable(visible) {
    const total = visible.length;
    const pages = Math.max(1, Math.ceil(total / PAGE_SIZE));
    // Clamp read-only — never mutate persisted.page inside render()
    const page = Math.max(1, Math.min(persisted.page, pages));
    const start = (page - 1) * PAGE_SIZE;
    const slice = visible.slice(start, start + PAGE_SIZE);

    const prevIds = new Set((prevState?.findings || []).map(x => x.id));
    const prevByIdRow = new Map((prevState?.findings || []).map(x => [x.id, x]));

    refs.tblBody.innerHTML = slice.length === 0
      ? `<tr class="empty-row"><td colspan="11">No findings match the current filters.</td></tr>`
      : slice.map(r => {
        const cls = [];
        if (r.compound) cls.push("compound");
        if (r.is_chain) cls.push("chain-finding");
        if (r.upgrade_required) cls.push("upgrade");
        if (r.submission_ready) cls.push("ready");
        if (persisted.detail.open && persisted.detail.id === r.id) cls.push("active");
        // Flash if status/severity/checklist changed since last poll
        const prev = prevByIdRow.get(r.id);
        if (prev && (prev.triage_status !== r.triage_status
                  || prev.severity_ceiling !== r.severity_ceiling
                  || prev.checklist_overall !== r.checklist_overall)) cls.push("flash");

        const starOn = persisted.starred.includes(r.id);
        const tScore = r.triage_score;
        return `<tr data-id="${esc(r.id)}" class="${cls.join(" ")}">
          <td><div class="id-cell">${r.submission_ready ? `<span class="check">✓</span>` : ""}${r.is_chain ? `<span class="chain-icon" title="Chained exploit: ${esc((r.chain_components||[]).join(' + '))}">⛓</span>` : ""}${esc(r.id)}</div></td>
          <td><div class="title-cell" title="${esc(r.title)}">${esc(r.title)}</div></td>
          <td><span class="badge agent">${esc(r.agent || "—")}</span>${r.thread_id ? ` <span class="badge" style="background:rgba(99,102,241,0.15);color:#818cf8;border:1px solid rgba(129,140,248,0.4);font-size:10px;padding:1px 5px" title="Deep Trace: ${esc(r.thread_id)}${r.trace_depth ? ` (depth ${r.trace_depth})` : ""}">DT</span>` : ""}</td>
          <td>${sevChain(r.raw_severity, r.severity_ceiling || r.calibrated_severity, r.upgrade_required)}</td>
          <td>${tScore == null
              ? `<span class="score-cell" style="color:var(--muted)">—</span>`
              : `<span class="score-bar"><span class="v" style="color:${scoreColor(tScore)}">${tScore}/35</span><span class="track"><span class="fill" style="width:${(tScore/35*100).toFixed(0)}%;background:${scoreColor(tScore)}"></span></span></span>`}</td>
          <td>${dotRow(r.exploitability_score)}</td>
          <td>${dupPill(r.duplicate_risk)}</td>
          <td>${pocCell(r)}</td>
          <td>${judgePill(r.predicted_outcome)}</td>
          <td>${actionPill(r.final_action)}</td>
          <td style="text-align:center"><button class="star-btn ${starOn ? "on" : ""}" data-star="${esc(r.id)}" aria-label="Star">${starOn ? "★" : "☆"}</button></td>
        </tr>`;
      }).join("");

    refs.pageInfo.textContent = `Page ${page} of ${pages} · ${total} rows`;
    refs.prevBtn.disabled = page <= 1;
    refs.nextBtn.disabled = page >= pages;
  }

  // ────────────────────────────────────────────────────── detail panel
  function getDetail(id) {
    return (window.MOCK_DETAIL && window.MOCK_DETAIL[id]) || null;
  }

  async function loadDetail(id) {
    // Try backend
    try {
      const res = await fetch(`/api/finding/${encodeURIComponent(id)}`, { cache: "no-store" });
      if (res.ok) return await res.json();
    } catch {}
    return getDetail(id);
  }

  function chkSym(sym) {
    // Map raw symbols to colored renderings.
    if (!sym) return `<span style="color:var(--muted)">·</span>`;
    if (sym.includes("✅")) return `<span style="color:var(--submit)">✅</span>`;
    if (sym.includes("⚠"))  return `<span style="color:var(--medium)">⚠️</span>`;
    if (sym.includes("❌")) return `<span style="color:var(--high)">❌</span>`;
    if (sym.includes("❓")) return `<span style="color:var(--muted)">❓</span>`;
    return esc(sym);
  }

  const CHECKLIST_LABELS = {
    q1_level2_proved: "Proved Level 2?",
    q2_level3_proved: "Proved Level 3?",
    q3_direct_loss: "Direct loss?",
    q4_permissionless: "Permissionless?",
    q5_victim_realistic: "Victim condition realistic?",
    q6_likely_duplicate: "Likely duplicate?",
    q7_one_sentence_impact: "One-sentence impact?",
  };

  // Naive Solidity-ish syntax highlighter for code blocks.
  function hl(code) {
    let s = esc(code);
    s = s.replace(/(\/\/[^\n]*)/g, '<span class="cm">$1</span>');
    s = s.replace(/\b(function|external|public|internal|private|view|pure|payable|return|returns|require|emit|if|else|for|while|storage|memory|calldata|uint256|uint|address|bool|true|false|new|nonReentrant|onlyAdmin|virtual|override)\b/g, '<span class="kw">$1</span>');
    s = s.replace(/(\b[A-Z][A-Za-z0-9_]*\b)/g, '<span class="fn">$1</span>');
    s = s.replace(/("[^"]*")/g, '<span class="str">$1</span>');
    s = s.replace(/\b(\d+(?:_\d+)*)\b/g, '<span class="num">$1</span>');
    return s;
  }

  function renderDetail(id, payload) {
    if (!payload) {
      refs.detailPanel.innerHTML = `<div style="padding:24px;color:var(--muted)">Finding not found.</div>`;
      return;
    }
    const f   = payload.finding || {};
    const tri = payload.triage  || {};
    const exp = payload.exploitability || {};
    const dup = payload.duplicates || {};
    const sev = payload.severity || {};
    const rp  = payload.runtime_poc || {};
    const jg  = payload.judge || {};
    const cl  = payload.checklist || {};
    const cg  = payload.completeness || {};

    const ceiling = cg.severity_ceiling || sev.calibrated_severity || f.severity;
    const starOn  = persisted.starred.includes(id);
    const tScore  = tri.score?.total;

    const checklistObj = cl.checklist || {};
    const checklistOverall = cl.overall || "—";

    const isChain = !!(f.is_chain || payload.definition?.is_chain);
    const chainComponents = f.chain_components || payload.definition?.chain_components || [];
    const chainType = f.chain_type || payload.definition?.chain_type || "";
    const chainDesc = payload.definition?.chain_description || "";

    refs.detailPanel.innerHTML = `
      <div class="detail-head">
        <div class="top">
          <div>
            <div class="fid">${isChain ? `<span style="color:var(--chain);margin-right:5px">⛓</span>` : ""}${esc(id)}</div>
            <div class="title">${esc(f.title || id)}</div>
          </div>
          <button class="close" id="closeDetail" aria-label="Close">✕</button>
        </div>
        <div class="detail-actions">
          <button class="star ${starOn ? "on" : ""}" id="starDetail">${starOn ? "★ Starred" : "☆ Star"}</button>
          <button id="copyIdBtn" title="Copy finding ID">⧉ Copy ID</button>
          ${payload.submission_file
            ? `<a href="/view/submission/${encodeURIComponent(id)}" target="_blank" rel="noopener" title="Open submission: ${esc(payload.submission_file)}">↗ Report</a>`
            : `<a href="/view/report" target="_blank" rel="noopener" title="Open full submission pack">↗ Pack</a>`}
          ${payload.poc_file ? `<a href="/view/poc/${encodeURIComponent(id)}" target="_blank" rel="noopener" title="Open PoC: ${esc(payload.poc_file)}">↗ PoC</a>` : (rp.poc_level || cg.poc_level_achieved) ? `<a href="/view/poc/${esc(id)}" target="_blank" rel="noopener" title="Open PoC test">↗ PoC</a>` : ""}
          ${payload.fork_poc_file ? `<a href="/view/fork-poc/${encodeURIComponent(id)}" target="_blank" rel="noopener" title="Fork test: ${esc(payload.fork_poc_file)}" style="border-color:rgba(14,165,233,0.5);color:#38bdf8">🔱 Fork</a>` : ""}
          ${payload.source_file ? `<a href="/view/source/${encodeURIComponent(id)}" target="_blank" rel="noopener" title="Open source: ${esc(payload.source_file)}">📄 Source</a>` : ""}
          ${cg.upgrade_required ? `<a href="#" title="Open upgrade task">↗ Upgrade Task</a>` : ""}
        </div>
      </div>

      ${isChain ? `
      <details class="detail-section" open><summary style="color:var(--chain)">⛓ Chain Components</summary>
        <div class="detail-body">
          <div class="kv">
            <span class="k">Type</span><span class="v" style="color:var(--chain)">${esc(chainType || "sequential")}</span>
            <span class="k">Components</span><span class="v">${chainComponents.map(c => `<span class="badge agent" style="border-color:rgba(129,140,248,0.4);color:var(--chain)">${esc(c)}</span>`).join(" → ")}</span>
          </div>
          ${chainDesc ? `<div style="font-size:11px;color:var(--muted);margin-top:8px;line-height:1.5">${esc(chainDesc)}</div>` : ""}
        </div>
      </details>` : ""}

      <details class="detail-section" open><summary>Status</summary>
        <div class="detail-body">
          <div class="status-row">
            <span class="k" style="color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:0.06em">Raw</span>${sevBadge(f.severity)}
            <span class="arrow">→</span>
            <span class="k" style="color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:0.06em">Ceiling</span>${sevBadge(ceiling)}
            <span class="arrow">·</span>
            <span class="k" style="color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:0.06em">Triage</span>${actionPill(tri.triage_status)}
          </div>
          <div class="kv">
            <span class="k">Calibrated</span><span class="v">${esc(sev.calibrated_severity || "—")}</span>
            <span class="k">Source</span><span class="v">${esc(sev.calibration_source || "—")}</span>
            <span class="k">Upgrade req</span><span class="v">${cg.upgrade_required ? `<span style="color:var(--medium)">YES</span>` : "no"}</span>
          </div>
        </div>
      </details>

      <details class="detail-section" open><summary>Scores</summary>
        <div class="detail-body">
          <div class="score-detail">
            <div class="row"><span>Triage Score</span><b>${tScore ?? "—"} / 35</b></div>
            <div class="track"><div class="fill" style="width:${tScore ? (tScore/35*100).toFixed(0) : 0}%;background:${scoreColor(tScore)}"></div></div>
          </div>
          <div class="score-detail">
            <div class="row"><span>Exploitability</span><b>${exp.exploitability_score ?? "—"} / 5</b></div>
            <div style="margin-top:4px">${dotRow(exp.exploitability_score)}</div>
          </div>
        </div>
      </details>

      <details class="detail-section" open><summary>Specialist Review</summary>
        <div class="detail-body">
          <div class="kv">
            <span class="k">Attacker</span><span class="v">${esc(exp.attacker?.type || "—")}</span>
            <span class="k">Damage</span><span class="v">${esc(exp.profit_or_damage?.type || "—")}</span>
            <span class="k">Dup risk</span><span class="v">${dupPill(dup.duplicate_risk)} <span style="color:var(--muted);margin-left:6px">${dup.probability != null ? (dup.probability*100).toFixed(0)+"%" : ""}</span></span>
            <span class="k">PoC</span><span class="v">${esc(rp.poc_level || cg.poc_level_achieved || "—")} · ${esc(rp.status || "—")}</span>
            ${rp.run_command ? `<span class="k">Run cmd</span><span class="v body"><div class="code-block" style="max-height:80px">${esc(rp.run_command)}</div></span>` : ""}
            <span class="k">Judge</span><span class="v">${judgePill(jg.predicted_outcome)} <span style="color:var(--muted);margin-left:4px">${esc(jg.predicted_severity || "")}</span> <span style="color:var(--muted);margin-left:4px">${jg.confidence != null ? "conf " + (jg.confidence*100).toFixed(0)+"%" : ""}</span></span>
            ${jg.strongest_objection ? `<span class="k">Objection</span><span class="v body" style="color:#cbd5e1;font-style:italic">${esc(jg.strongest_objection)}</span>` : ""}
          </div>
        </div>
      </details>

      <details class="detail-section" open><summary>Quality Checklist</summary>
        <div class="detail-body">
          <div class="checklist">
            ${Object.entries(CHECKLIST_LABELS).map(([k, label]) => {
              const q = checklistObj[k] || {};
              return `<div class="q">
                <div class="sym">${chkSym(q.symbol)}</div>
                <div>
                  <div class="text">${esc(label)}</div>
                  ${q.detail ? `<span class="detail">${esc(q.detail)}</span>` : ""}
                </div>
                <div class="ovr">${k.split("_")[0].toUpperCase()}</div>
              </div>`;
            }).join("")}
          </div>
          <div class="checklist-overall ${checklistOverall.toLowerCase()}">Overall: ${esc(checklistOverall)}</div>
        </div>
      </details>

      <details class="detail-section" open><summary>PoC Completeness Gate</summary>
        <div class="detail-body">
          <div class="gate-grid">
            <div><div class="lbl">Claimed</div><div class="val">${esc(f.severity || "—")}</div></div>
            <div><div class="lbl">Level achieved</div><div class="val">${esc(cg.poc_level_achieved || "—")}</div></div>
            <div><div class="lbl">Ceiling</div><div class="val">${esc(cg.severity_ceiling || "—")}</div></div>
            <div><div class="lbl">Supports claim</div><div class="val">${cg.poc_supports_claimed_severity ? `<span style="color:var(--submit)">YES</span>` : `<span style="color:var(--medium)">NO</span>`}</div></div>
          </div>
          ${cg.found_steps && cg.found_steps.length ? `
            <div style="font-size:10px;letter-spacing:0.1em;text-transform:uppercase;color:var(--muted);margin:8px 0 4px">Proof steps found</div>
            <ul class="steps-list">${cg.found_steps.map(s => `<li><span class="ico">✓</span><span>${esc(s)}</span></li>`).join("")}</ul>` : ""}
          ${cg.missing_steps && cg.missing_steps.length ? `
            <div style="font-size:10px;letter-spacing:0.1em;text-transform:uppercase;color:var(--muted);margin:10px 0 4px">Missing steps</div>
            <ul class="steps-list missing">${cg.missing_steps.map(s => `<li><span class="ico">✗</span><span>${esc(s)}</span></li>`).join("")}</ul>` : ""}
        </div>
      </details>

      <details class="detail-section" open><summary>Description</summary>
        <div class="detail-body">
          <div class="desc-body" id="descBody"></div>
        </div>
      </details>

      <details class="detail-section" open><summary>Location</summary>
        <div class="detail-body">
          <div class="kv">
            <span class="k">File</span><span class="v">${esc(f.file || "—")}</span>
            <span class="k">Function</span><span class="v">${esc(f.function || "—")}</span>
            <span class="k">Lines</span><span class="v">${esc(f.lines || "—")}</span>
          </div>
        </div>
      </details>

      ${f.code ? `
      <details class="detail-section" open><summary>Vulnerable Code</summary>
        <div class="detail-body">
          <pre class="code-block"><code>${hl(f.code)}</code></pre>
        </div>
      </details>` : ""}

      ${f.attack_steps && f.attack_steps.length ? `
      <details class="detail-section" open><summary>Attack Sequence</summary>
        <div class="detail-body">
          <ol class="attack">${f.attack_steps.map(s => `<li>${esc(s)}</li>`).join("")}</ol>
        </div>
      </details>` : ""}

      ${(jg.likely_judge_questions && jg.likely_judge_questions.length) ? `
      <details class="detail-section" open><summary>Judge Objections</summary>
        <div class="detail-body">
          <ul class="bullets">${jg.likely_judge_questions.map(s => `<li>${esc(s)}</li>`).join("")}</ul>
        </div>
      </details>` : ""}

      ${f.recommendation ? `
      <details class="detail-section" open><summary>Recommended Fix</summary>
        <div class="detail-body">
          <div class="desc-body">${esc(f.recommendation)}</div>
        </div>
      </details>` : ""}
    `;

    // Description show-more behaviour.
    const descEl = refs.detailPanel.querySelector("#descBody");
    if (descEl && f.description) {
      const FULL = f.description;
      let expanded = false;
      const render = () => {
        if (expanded || FULL.length <= 300) {
          descEl.innerHTML = esc(FULL);
        } else {
          descEl.innerHTML = esc(FULL.slice(0, 300)) + "… <a class='show-more' href='#'>Show more</a>";
          const link = descEl.querySelector("a.show-more");
          link.addEventListener("click", (e) => { e.preventDefault(); expanded = true; render(); });
        }
      };
      render();
    }

    // Wire actions.
    refs.detailPanel.querySelector("#closeDetail").addEventListener("click", closeDetail);
    refs.detailPanel.querySelector("#starDetail").addEventListener("click", () => toggleStar(id));
    refs.detailPanel.querySelector("#copyIdBtn").addEventListener("click", () => {
      navigator.clipboard?.writeText(id).then(() => showToast("ID copied"));
    });
  }

  async function openDetail(id) {
    persisted.detail = { open: true, id };
    savePersisted();
    refs.mainGrid.classList.add("detail-open");
    refs.detailPanel.innerHTML = `<div style="padding:24px;color:var(--muted)">Loading…</div>`;
    const payload = await loadDetail(id);
    renderDetail(id, payload);
    render(); // re-highlight active row
  }
  function closeDetail() {
    persisted.detail = { open: false, id: null };
    savePersisted();
    refs.mainGrid.classList.remove("detail-open");
    render();
  }
  function toggleStar(id) {
    const idx = persisted.starred.indexOf(id);
    if (idx === -1) persisted.starred.push(id); else persisted.starred.splice(idx, 1);
    savePersisted();
    render();
    if (persisted.detail.open && persisted.detail.id === id) {
      // re-render detail star button
      openDetail(id);
    }
  }

  // ────────────────────────────────────────────────────── bottom bar
  function renderBottom(s) {
    const p = s.pipeline;
    const stages = [
      ["Static",     p.stage_1_static],
      ["Agents",     p.stage_2_agents],
      ["Report",     p.stage_3_report],
      ["Triage",     p.stage_4_triage],
      ["Specialist", p.stage_5_specialist],
      ["PoC",        p.stage_6_poc],
      ["Checklist",  p.stage_7_checklist],
      ["Gate",       p.stage_8_gate],
    ];
    let lastDone = -1, nextIdx = -1;
    stages.forEach(([_, st], i) => { if (st.done) lastDone = i; else if (nextIdx === -1) nextIdx = i; });

    let left;
    if (nextIdx === -1) {
      left = `<b class="ok">All 8 stages complete</b>`;
    } else {
      left = `<b>Stage ${lastDone + 1} (${esc(stages[lastDone]?.[0] || "—")})</b> complete · <b class="warn">Stage ${nextIdx + 1}: ${esc(stages[nextIdx][0])}</b> in progress`;
    }
    refs.barLeft.innerHTML = left;

    const ready   = s.findings.filter(f => f.submission_ready).length;
    const needPoc = s.findings.filter(f => f.triage_status === "poc_required").length;
    const blocked = s.findings.filter(f => f.upgrade_required || f.checklist_overall === "failed").length;
    refs.barCenter.innerHTML = `<b class="ok">${ready}</b> ready to submit · <b class="warn">${needPoc}</b> need PoC · <b class="bad">${blocked}</b> blocked by gate`;

    const kb = s.kb || {};
    if (kb.total_findings == null) {
      refs.barRight.innerHTML = `KB: <b class="warn">offline</b>`;
    } else {
      refs.barRight.innerHTML = `KB: <b>${kb.total_findings.toLocaleString()}</b> findings · synced <b>${relTime(kb.last_run)}</b> · continuous <b class="${kb.continuous_running ? "ok" : ""}">${kb.continuous_running ? "ON" : "OFF"}</b>`;
    }
  }

  // ────────────────────────────────────────────────────── master render
  function render() {
    if (!state) return;
    renderHeader(state);
    renderSidebar(state);
    rebuildAgentFilter(state.findings);
    const visible = applyFiltersAndSort(state.findings);
    renderSummary(state, visible);
    renderSortIndicators();
    renderTable(visible);
    renderRealWorldFindings();
    renderBottom(state);
  }

  // ────────────────────────────────────────────────────── chat panel
  function parseChatContent(content, role) {
    if (role !== "assistant") return `<div class="chat-text">${esc(content)}</div>`;
    const segs = [];
    let last = 0;
    const re = /```(\w*)\n?([\s\S]*?)```/g;
    let m;
    while ((m = re.exec(content)) !== null) {
      if (m.index > last) segs.push({ type: "text", content: content.slice(last, m.index) });
      segs.push({ type: "code", code: m[2].trim() });
      last = m.index + m[0].length;
    }
    if (last < content.length) segs.push({ type: "text", content: content.slice(last) });
    return segs.map(seg => {
      if (seg.type === "text") return `<div class="chat-text">${esc(seg.content)}</div>`;
      const runnable = /^python\s+(scripts|tools)\/[\w_]+\.py/.test(seg.code) && !seg.code.includes("\n");
      return `<div class="chat-code-wrap">
        <pre class="chat-code"><code>${esc(seg.code)}</code></pre>
        ${runnable ? `<button class="run-btn" data-cmd="${esc(seg.code)}">▶ Run</button>` : ""}
      </div>`;
    }).join("");
  }

  function toggleChat() {
    persisted.chat.open = !persisted.chat.open;
    document.body.classList.toggle("chat-open", persisted.chat.open);
    savePersisted();
    if (persisted.chat.open) refs.chatInput.focus();
  }

  function renderChatMsgs() {
    refs.chatMsgs.innerHTML = persisted.chat.history.map(m =>
      `<div class="chat-msg ${esc(m.role)}">${parseChatContent(m.content, m.role)}</div>`
    ).join("");
    refs.chatMsgs.scrollTop = refs.chatMsgs.scrollHeight;
  }

  async function sendChat() {
    const text = refs.chatInput.value.trim();
    if (!text) return;
    refs.chatInput.value = "";
    persisted.chat.history.push({ role: "user", content: text });
    if (persisted.chat.history.length > 40) persisted.chat.history = persisted.chat.history.slice(-40);
    savePersisted();
    renderChatMsgs();

    const thinking = document.createElement("div");
    thinking.className = "chat-msg assistant thinking";
    thinking.textContent = "…";
    refs.chatMsgs.appendChild(thinking);
    refs.chatMsgs.scrollTop = refs.chatMsgs.scrollHeight;

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: persisted.chat.history.filter(m => m.role !== "terminal") }),
      });
      thinking.remove();
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      persisted.chat.history.push({ role: "assistant", content: data.reply });
      savePersisted();
    } catch (err) {
      thinking.remove();
      persisted.chat.history.push({ role: "assistant", content: `Error: ${err.message}` });
      savePersisted();
    }
    renderChatMsgs();
    syncQueueFromHistory();
    renderQueue();
  }

  function syncQueueFromHistory() {
    const inQueue = new Set(persisted.chat.queue.map(q => q.cmd));
    const re = /```(\w*)\n?([\s\S]*?)```/g;
    for (const msg of persisted.chat.history) {
      if (msg.role !== "assistant") continue;
      re.lastIndex = 0;
      let m;
      while ((m = re.exec(msg.content)) !== null) {
        const code = m[2].trim();
        if (/^python\s+(scripts|tools)\/[\w_]+\.py/.test(code) && !code.includes("\n") && !inQueue.has(code)) {
          persisted.chat.queue.push({ id: crypto.randomUUID(), cmd: code,
            status: "pending", output: null, exitCode: null, outputOpen: false });
          inQueue.add(code);
        }
      }
    }
    savePersisted();
  }

  async function runQueueItem(id) {
    const item = persisted.chat.queue.find(q => q.id === id);
    if (!item || item.status === "running") return;
    item.status = "running";
    savePersisted(); renderQueue();
    try {
      const res = await fetch("/api/run", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: item.cmd }),
      });
      const data = await res.json();
      item.exitCode = data.returncode ?? null;
      if (data.error) {
        item.status = "error";
        item.output = `Error: ${data.error}`;
      } else {
        item.status = data.returncode === 0 ? "done" : "error";
        const parts = [];
        if (data.stdout?.trim()) parts.push(data.stdout.trim());
        if (data.stderr?.trim()) parts.push(`[stderr]\n${data.stderr.trim()}`);
        parts.push(`Exit: ${data.returncode}`);
        item.output = parts.join("\n\n");
      }
      item.outputOpen = true;
      savePersisted();
      clearTimeout(pollTimer); poll();
    } catch (err) {
      item.status = "error";
      item.output = `Error: ${err.message}`;
      item.outputOpen = true;
      savePersisted();
    }
    renderQueue();
    await autoSummarize(item.cmd, item.output || "", item.exitCode ?? -1);
  }

  async function autoSummarize(cmd, output, exitCode) {
    if (!persisted.chat.open) {
      persisted.chat.open = true;
      document.body.classList.add("chat-open");
      savePersisted();
    }
    const truncated = output.length > 2500 ? output.slice(0, 2500) + "\n…[truncated]" : output;
    const autoMsg = `I just ran:\n\`${cmd}\`\n\nOutput (exit ${exitCode}):\n\`\`\`\n${truncated}\n\`\`\`\n\nPlease give me a thorough summary of what this output means, what was found or changed, and what specific next steps I need to take.`;
    persisted.chat.history.push({ role: "user", content: autoMsg });
    if (persisted.chat.history.length > 40) persisted.chat.history = persisted.chat.history.slice(-40);
    savePersisted();
    renderChatMsgs();

    const thinking = document.createElement("div");
    thinking.className = "chat-msg assistant thinking";
    thinking.textContent = "Analyzing output…";
    refs.chatMsgs.appendChild(thinking);
    refs.chatMsgs.scrollTop = refs.chatMsgs.scrollHeight;
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: persisted.chat.history.filter(m => m.role !== "terminal") }),
      });
      thinking.remove();
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      persisted.chat.history.push({ role: "assistant", content: data.reply });
      savePersisted();
    } catch (err) {
      thinking.remove();
      persisted.chat.history.push({ role: "assistant", content: `Error: ${err.message}` });
      savePersisted();
    }
    renderChatMsgs();
    syncQueueFromHistory();
    renderQueue();
  }

  function filterDroppedFromQueue() {
    if (!state) return;
    const dropped = new Set(
      state.findings
        .filter(f => (f.exploitability_score ?? 0) < 3)
        .map(f => f.id)
    );
    const POC_SCRIPTS = /generate_poc_plan|generate_poc_test|run_poc_tests/;
    const before = persisted.chat.queue.length;
    persisted.chat.queue = persisted.chat.queue.filter(item => {
      if (item.status !== "pending") return true;
      if (!POC_SCRIPTS.test(item.cmd)) return true;
      const m = item.cmd.match(/--finding-id\s+(\S+)/);
      if (!m) return true;
      return !dropped.has(m[1]);
    });
    const removed = before - persisted.chat.queue.length;
    savePersisted();
    renderQueue();
    if (removed > 0) showToast(`Removed ${removed} dropped PoC command(s)`);
  }

  async function runCommand(cmd) {
    let item = persisted.chat.queue.find(q => q.cmd === cmd);
    if (!item) {
      item = { id: crypto.randomUUID(), cmd, status: "pending",
               output: null, exitCode: null, outputOpen: false };
      persisted.chat.queue.push(item);
      savePersisted();
    }
    await runQueueItem(item.id);
  }

  function renderQueue() {
    const el = refs.runQueue;
    if (!el) return;
    const q = persisted.chat.queue;
    const pending = q.filter(x => x.status === "pending").length;
    const open = persisted.chat.queueOpen;
    const ico = { pending: "○", running: "⟳", done: "✓", error: "✗" };
    el.innerHTML = `
      <div class="rq-header">
        <span class="rq-title">Commands <span class="rq-badge">${q.length}</span>
          ${pending ? `<span class="rq-pending-lbl">${pending} pending</span>` : ""}</span>
        <span class="rq-actions">
          ${pending ? `<button class="rq-run-all" id="rqRunAll">▶ Run All</button>` : ""}
          <button class="rq-filter" id="rqFilter" title="Remove PoC commands for downgraded findings">⊘ Filter</button>
          <button class="rq-clear" id="rqClear" title="Clear completed">⊘ Clear done</button>
          <button class="rq-toggle" id="rqToggle">${open ? "▾" : "▴"}</button>
        </span>
      </div>
      ${open ? `<div class="rq-list">${q.map(item => `
        <div class="rq-item rq-${esc(item.status)}" data-id="${esc(item.id)}">
          <span class="rq-ico">${ico[item.status] ?? "○"}</span>
          <span class="rq-cmd" title="${esc(item.cmd)}">${esc(item.cmd.length > 62 ? item.cmd.slice(0, 62) + "…" : item.cmd)}</span>
          <span class="rq-btns">
            ${item.status === "pending" ? `<button class="rq-run" data-run="${esc(item.id)}">▶</button>` : ""}
            ${item.status === "done" || item.status === "error" ? `<button class="rq-retry" data-run="${esc(item.id)}">↺</button>` : ""}
            ${item.output ? `<button class="rq-out-toggle" data-out="${esc(item.id)}">${item.outputOpen ? "▾" : "▸"}</button>` : ""}
            <button class="rq-remove" data-rm="${esc(item.id)}">×</button>
          </span>
          ${item.output && item.outputOpen ? `<pre class="rq-output">${esc(item.output)}</pre>` : ""}
        </div>`).join("")}</div>` : ""}
    `;
    el.querySelector("#rqToggle")?.addEventListener("click", () => {
      persisted.chat.queueOpen = !persisted.chat.queueOpen; savePersisted(); renderQueue();
    });
    el.querySelector("#rqClear")?.addEventListener("click", () => {
      persisted.chat.queue = persisted.chat.queue.filter(x => x.status === "pending" || x.status === "running");
      savePersisted(); renderQueue();
    });
    el.querySelector("#rqRunAll")?.addEventListener("click", async () => {
      filterDroppedFromQueue();
      const pending = persisted.chat.queue.filter(x => x.status === "pending").slice();
      for (const item of pending) await runQueueItem(item.id);
    });
    el.querySelector("#rqFilter")?.addEventListener("click", filterDroppedFromQueue);
    el.querySelectorAll("[data-run]").forEach(btn =>
      btn.addEventListener("click", () => runQueueItem(btn.dataset.run)));
    el.querySelectorAll("[data-rm]").forEach(btn =>
      btn.addEventListener("click", () => {
        persisted.chat.queue = persisted.chat.queue.filter(x => x.id !== btn.dataset.rm);
        savePersisted(); renderQueue();
      }));
    el.querySelectorAll("[data-out]").forEach(btn =>
      btn.addEventListener("click", () => {
        const item = persisted.chat.queue.find(x => x.id === btn.dataset.out);
        if (item) { item.outputOpen = !item.outputOpen; savePersisted(); renderQueue(); }
      }));
  }

  // ────────────────────────────────────────────────────── events
  refs.tblBody.addEventListener("click", (e) => {
    const starBtn = e.target.closest("[data-star]");
    if (starBtn) {
      e.stopPropagation();
      toggleStar(starBtn.dataset.star);
      return;
    }
    const row = e.target.closest("tr[data-id]");
    if (row) openDetail(row.dataset.id);
  });

  refs.tblHead.addEventListener("click", (e) => {
    const th = e.target.closest("th[data-col]");
    if (!th) return;
    const col = th.dataset.col;
    if (persisted.sort.col === col) {
      persisted.sort.dir = persisted.sort.dir === "asc" ? "desc" : "asc";
    } else {
      persisted.sort.col = col;
      persisted.sort.dir = "desc";
    }
    savePersisted();
    render();
  });

  refs.prevBtn.addEventListener("click", () => {
    persisted.page -= 1; savePersisted();
    refs.tblBody.closest(".table-wrap")?.scrollTo(0, 0);
    render();
  });
  refs.nextBtn.addEventListener("click", () => {
    const before = persisted.page;
    persisted.page += 1; savePersisted();
    refs.tblBody.closest(".table-wrap")?.scrollTo(0, 0);
    render();
    console.log(`[next] page ${before} → ${persisted.page}, state findings=${state?.findings?.length}`);
  });

  function bindFilter(el, key, isText = false) {
    const ev = isText ? "input" : "change";
    if (key in persisted.filters) el.value = persisted.filters[key];
    el.addEventListener(ev, () => {
      persisted.filters[key] = el.value || undefined;
      persisted.page = 1;
      savePersisted();
      render();
    });
  }
  bindFilter(refs.searchInp, "search", true);
  bindFilter(refs.sevSel,    "severity");
  bindFilter(refs.triageSel, "triage");
  bindFilter(refs.agentSel,  "agent");
  bindFilter(refs.actionSel, "action");
  bindFilter(refs.gateSel,   "gate");

  refs.clearBtn.addEventListener("click", () => {
    persisted.filters = {};
    refs.searchInp.value = "";
    [refs.sevSel, refs.triageSel, refs.agentSel, refs.actionSel, refs.gateSel].forEach(s => s.value = "");
    persisted.page = 1;
    savePersisted();
    render();
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && persisted.detail.open) closeDetail();
    if (e.key === "Escape" && persisted.chat.open) toggleChat();
    if (e.key === "c" && !e.ctrlKey && !e.metaKey && !e.altKey
        && document.activeElement.tagName !== "INPUT"
        && document.activeElement.tagName !== "TEXTAREA") {
      toggleChat();
    }
  });

  refs.chatMsgs.addEventListener("click", (e) => {
    const btn = e.target.closest(".run-btn");
    if (btn) runCommand(btn.dataset.cmd);
  });
  refs.chatHandle.addEventListener("mousedown", (e) => {
    e.preventDefault();
    const startY = e.clientY;
    const startH = persisted.chat.height;
    refs.chatPanel.style.transition = "none";
    const MIN_H = 220;
    const MAX_H = window.innerHeight * 0.85;
    const onMove = (ev) => {
      const newH = Math.max(MIN_H, Math.min(MAX_H, startH + (startY - ev.clientY)));
      document.documentElement.style.setProperty("--chat-h", newH + "px");
    };
    const onUp = (ev) => {
      const newH = Math.max(MIN_H, Math.min(MAX_H, startH + (startY - ev.clientY)));
      persisted.chat.height = Math.round(newH);
      savePersisted();
      refs.chatPanel.style.transition = "";
      document.removeEventListener("mousemove", onMove);
      document.removeEventListener("mouseup", onUp);
    };
    document.addEventListener("mousemove", onMove);
    document.addEventListener("mouseup", onUp);
  });

  refs.chatReset.addEventListener("click", () => {
    persisted.chat.history = [];
    persisted.chat.queue = [];
    savePersisted();
    renderChatMsgs();
    renderQueue();
  });
  refs.chatClose.addEventListener("click", () => {
    if (persisted.chat.open) toggleChat();
  });
  refs.chatToggle.addEventListener("click", toggleChat);
  refs.chatSend.addEventListener("click", sendChat);
  refs.chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendChat(); }
  });

  // ──────────────────────────────────────────────────── audit management

  let allAuditsData = [];
  let auditsTblSort = { col: "name", dir: "asc" };
  let auditsScope = "bounty";  // (P100) all-audits filter: bounty | eval | all
  let hiddenKinds = [];        // (P100) view-only: audit kinds hidden by config/dashboard_view.json
  let auditsScopeInit = false; // pick a sensible default scope once, based on hiddenKinds

  function deadlineClass(isoStr) {
    if (!isoStr) return "";
    const d = new Date(isoStr);
    if (isNaN(d)) return "";
    const days = (d - Date.now()) / 86400000;
    if (days < 0)  return "dl-red";
    if (days < 3)  return "dl-red";
    if (days < 7)  return "dl-orange";
    if (days < 14) return "dl-amber";
    return "dl-green";
  }

  function deadlineText(isoStr) {
    if (!isoStr) return null;
    const d = new Date(isoStr);
    if (isNaN(d)) return null;
    const days = Math.ceil((d - Date.now()) / 86400000);
    if (days < 0)  return `EXPIRED ${Math.abs(days)}d ago`;
    if (days === 0) return "DUE TODAY";
    if (days === 1) return "1 day remaining";
    return `${days} days remaining`;
  }

  function renderAuditInfoCard(activeAudit) {
    const card = document.getElementById("auditInfoCard");
    if (!card) return;
    if (!activeAudit || !activeAudit.audit_id) {
      card.style.display = "none";
      return;
    }
    const rows = [
      ["Contest",  activeAudit.contest  || "—"],
      ["Platform", activeAudit.platform || "—"],
      ["Language", activeAudit.language || "—"],
      ["Status",   activeAudit.status   || "—"],
    ].map(([l, v]) =>
      `<div class="ai-row"><span class="lbl">${esc(l)}</span><span class="val">${esc(v)}</span></div>`
    ).join("");
    const dlText = deadlineText(activeAudit.deadline);
    const dlCls  = deadlineClass(activeAudit.deadline);
    const dlHtml = dlText
      ? `<div class="audit-deadline ${dlCls}">${esc(dlText)}</div>`
      : "";
    card.innerHTML = `<div class="ai-name" title="${esc(activeAudit.name)}">${esc(activeAudit.name || activeAudit.audit_id)}</div>${rows}${dlHtml}`;
    card.style.display = "";
  }

  function renderSyncStatusCard(sync) {
    const card = document.getElementById("syncStatusCard");
    if (!card) return;
    if (!sync || !sync.status) {
      card.style.display = "none";
      return;
    }
    const statusColors = { OK: "#3fb950", PARTIAL: "#d29922", FAILED: "#f85149", DRY_RUN: "#8b949e" };
    const col = statusColors[sync.status] || "#8b949e";
    const rows = [
      ["Active audit", sync.audit_id || "—"],
      ["Last phase",   sync.phase_id || "—"],
      ["Last sync",    sync.timestamp ? relTime(sync.timestamp) : "—"],
      ["Adapter",      sync.adapter || "—"],
      ["Visible globally", (sync.global_candidate_count_live ?? sync.global_candidate_count ?? "—") + ""],
      ["Unsynced",     (sync.unsynced_count ?? "—") + ""],
    ].map(([l, v]) =>
      `<div class="ai-row"><span class="lbl">${esc(l)}</span><span class="val">${esc(v)}</span></div>`
    ).join("");
    const report = sync.sync_report
      ? `<div class="ai-row"><span class="lbl">Report</span><span class="val" title="${esc(sync.sync_report)}">${esc(sync.sync_report.split("/").pop())}</span></div>`
      : "";
    card.innerHTML =
      `<div class="ai-name"><span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${col};margin-right:6px"></span>Sync: ${esc(sync.status)}</div>${rows}${report}`;
    card.style.display = "";
  }

  // Live all-tracks findings summary (real-world funnel PoCs + research tracks), sourced from the SAME
  // findings_overview the /findings and /candidates pages use — so the main page reflects the real-world
  // findings. Display-only; always visible (shows "—" when the source is empty).
  function renderAllTracksCard(at) {
    const card = document.getElementById("allTracksCard");
    if (!card) return;
    const a = at || {};
    const v = (n) => (n === undefined || n === null) ? "—" : (n + "");
    const rows = [
      ["Total", v(a.total)],
      ["Reproduced (real-world)", v(a.reproduced)],
      ["Rejected / abstained", v(a.rejected_or_abstained)],
      ["Not run", v(a.not_run)],
    ].map(([l, val]) =>
      `<div class="row"><span class="lbl">${esc(l)}</span><span class="val">${esc(val)}</span></div>`
    ).join("");
    card.innerHTML = rows +
      `<div class="row"><a href="/findings" title="Full at-a-glance list across every track"><b>→ Findings (all tracks)</b></a></div>`;
  }

  // Individual real-world PoC-proven findings, listed under the filter bar in the Dashboard tab. Source:
  // state.real_world_findings (real_world_results.json). Filter-reactive: respects the Severity + Search
  // controls (the other selects are active-audit-pipeline concepts that don't apply here). Each row
  // deep-links to its funnel detail packet. Display-only.
  function renderRealWorldFindings() {
    const box = document.getElementById("realWorldFindings");
    if (!box) return;
    const all = Array.isArray(state && state.real_world_findings) ? state.real_world_findings : [];
    const f = persisted.filters || {};
    let items = all.slice();
    if (f.search) {
      const q = f.search.toLowerCase();
      items = items.filter(r =>
        (r.title || "").toLowerCase().includes(q) ||
        (r.target || "").toLowerCase().includes(q));
    }
    if (f.severity) {
      const want = f.severity.toLowerCase();
      items = items.filter(r =>
        (r.severity || "").toLowerCase().split("/").map(s => s.trim()).includes(want));
    }
    const total = all.length;
    const countLabel = (items.length === total) ? `${total}` : `${items.length} of ${total}`;
    const head =
      `<div class="rw-head">Real-World Findings — PoC-proven (${countLabel}) ` +
      `<a href="/results" style="font-weight:400;font-size:11px;margin-left:6px">→ Real-World Results</a></div>`;
    if (items.length === 0) {
      const msg = total === 0 ? "none yet" : "none match the current filters";
      box.innerHTML = head +
        `<div class="rw-empty" style="color:var(--muted);font-size:12px;padding:6px 12px">${msg}</div>`;
      return;
    }
    const rows = items.map((r) => {
      const href = "/candidates?candidate_id=" + encodeURIComponent("funnel:" + (r.title || ""));
      return `<a class="rw-row" href="${href}" title="${esc(r.title || "")}">
        <span class="rw-sev">${sevBadge(r.severity)}</span>
        <span class="rw-target">${esc(r.target || "—")}</span>
        <span class="rw-title">${esc(r.title || "")}</span>
      </a>`;
    }).join("");
    box.innerHTML = head + `<div class="rw-list">${rows}</div>`;
  }

  async function fetchAudits() {
    try {
      const res = await fetch("/api/audits", { cache: "no-store" });
      if (!res.ok) throw new Error(res.statusText);
      const j = await res.json();
      hiddenKinds = j.hidden_audit_kinds || [];
      // default the all-audits scope to a VISIBLE kind once (so hidden kinds aren't shown by default).
      if (!auditsScopeInit) {
        auditsScopeInit = true;
        if (hiddenKinds.includes(auditsScope)) auditsScope = hiddenKinds.includes("eval") ? "all" : "eval";
      }
      return j;
    } catch { return { audits: [], active_audit_id: null, hidden_audit_kinds: [] }; }
  }

  // (P100) derived audit kind: prefer the server-provided `kind`; fall back to the same rule client-side.
  function auditKind(a) {
    if (a && a.kind) return a.kind;
    const c = String((a && a.contest) || "").toLowerCase();
    if (c.includes("immunefi") || c.includes("hackerone")) return "bounty";
    if (["k2-kinetic-2026-04", "circle-2026-05"].includes(a && a.audit_id)) return "bounty";
    return "eval";
  }

  function renderAuditSwitcher(audits, activeId) {
    const sel = document.getElementById("auditSel");
    if (!sel) return;
    if (!audits || audits.length === 0) {
      sel.innerHTML = `<option value="">No audits</option>`;
      return;
    }
    const opt = (a) =>
      `<option value="${esc(a.audit_id)}"${a.audit_id === activeId ? " selected" : ""}>${esc(a.name || a.audit_id)}</option>`;
    // view-only: drop hidden kinds from the selector (but always keep the active audit so switching still works).
    const visible = audits.filter(a => !hiddenKinds.includes(auditKind(a)) || a.audit_id === activeId);
    const bounty = visible.filter(a => auditKind(a) === "bounty");
    const evalc = visible.filter(a => auditKind(a) !== "bounty");
    let html = "";
    if (bounty.length) html += `<optgroup label="Bug-bounty audits (${bounty.length})">${bounty.map(opt).join("")}</optgroup>`;
    if (evalc.length) html += `<optgroup label="Eval / research corpus (${evalc.length})">${evalc.map(opt).join("")}</optgroup>`;
    sel.innerHTML = html || audits.map(opt).join("");
  }

  async function doSwitchAudit(auditId) {
    try {
      const res = await fetch("/api/audits/switch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ audit_id: auditId }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || res.statusText);
      // Clear per-audit filter state for the new audit so we start fresh
      history.replaceState(null, "", "?audit=" + encodeURIComponent(auditId));
      showToast(`Switched to ${auditId}`);
      clearTimeout(pollTimer);
      poll();
    } catch (err) {
      showToast("Switch failed: " + err.message);
    }
  }

  // ──────────────────────────────────────────── All Audits tab

  function renderAllAuditsTab(audits, activeId) {
    allAuditsData = audits || [];
    const body = document.getElementById("auditsTblBody");
    const summaryBar = document.getElementById("auditsSummaryBar");
    if (!body) return;

    const nBounty = allAuditsData.filter(a => auditKind(a) === "bounty").length;
    const nEval = allAuditsData.length - nBounty;
    const totalSubmit = allAuditsData.reduce((s, a) => s + (a.submit_count || 0), 0);
    if (summaryBar) {
      const hidden = (kind) => hiddenKinds.includes(kind);
      const btn = (s, label, kind) => `<button class="btn ghost auditScopeBtn" data-scope="${s}" style="${auditsScope === s ? "background:var(--surface-2);font-weight:700;" : ""}${kind && hidden(kind) ? "opacity:.6;" : ""}">${label}${kind && hidden(kind) ? " · hidden" : ""}</button>`;
      const hiddenNote = hiddenKinds.length
        ? ` &nbsp;<span style="color:var(--muted);font-size:11px">${hiddenKinds.join("/")} hidden by default (view-only — files & registry kept; click to reveal, or set config/dashboard_view.json hidden_audit_kinds:[] to restore)</span>`
        : ` &nbsp;<span style="color:var(--muted);font-size:11px">(derived view — registry unchanged; the active audit always shows)</span>`;
      summaryBar.innerHTML =
        `${btn("bounty", "Bounty (" + nBounty + ")", "bounty")} ${btn("eval", "Eval/corpus (" + nEval + ")", "eval")} ${btn("all", "All (" + allAuditsData.length + ")")}` +
        ` &nbsp;·&nbsp; <b>${totalSubmit}</b> findings ready to submit` + hiddenNote;
      summaryBar.querySelectorAll(".auditScopeBtn").forEach(b =>
        b.addEventListener("click", () => { auditsScope = b.dataset.scope; renderAllAuditsTab(allAuditsData, activeId); }));
    }

    // scope filter: Bounty (default) | Eval | All — table rows only; the ACTIVE audit is always shown.
    const inScope = (a) => auditsScope === "all" || auditKind(a) === auditsScope || a.audit_id === activeId;
    const visible = allAuditsData.filter(inScope);

    const { col, dir } = auditsTblSort;
    const mul = dir === "asc" ? 1 : -1;
    const sorted = [...visible].sort((a, b) => {
      const av = a[col] ?? ""; const bv = b[col] ?? "";
      if (col === "deadline") return (new Date(av) - new Date(bv)) * mul;
      if (typeof av === "number") return (av - bv) * mul;
      return String(av).localeCompare(String(bv)) * mul;
    });

    // update sort indicators
    document.getElementById("auditsTblHead")?.querySelectorAll("th").forEach(th => {
      th.classList.toggle("sorted", th.dataset.col === col);
      const sp = th.querySelector(".sort");
      if (sp) sp.textContent = th.dataset.col === col ? (dir === "asc" ? "▴" : "▾") : "▾";
    });

    body.innerHTML = sorted.length ? sorted.map(a => {
      const dlDays = a.deadline ? Math.ceil((new Date(a.deadline) - Date.now()) / 86400000) : null;
      const dlStr = dlDays === null ? "—" : dlDays < 0 ? `<span style="color:var(--high)">expired</span>` : `${dlDays}d`;
      const statusCls = "sp-" + (a.status || "archived").replace(/[^a-z]/g, "");
      const kind = auditKind(a);
      const kindPill = kind === "bounty"
        ? `<span class="status-pill" style="color:var(--submit);border-color:rgba(22,163,74,0.4)">bounty</span>`
        : `<span class="status-pill" style="color:var(--muted)">eval/corpus</span>`;
      return `<tr data-audit-id="${esc(a.audit_id)}" class="${a.audit_id === activeId ? "audits-active-row" : ""}">
        <td><span style="font-weight:600">${esc(a.name || a.audit_id)}</span><br><span style="color:var(--muted);font-size:11px;font-family:var(--mono)">${esc(a.audit_id)}</span></td>
        <td>${kindPill}</td>
        <td>${esc(a.platform || "—")}</td>
        <td><span class="status-pill ${statusCls}">${esc(a.status || "unknown")}</span></td>
        <td style="font-family:var(--mono)">${dlStr}</td>
        <td style="font-family:var(--mono);font-weight:600">${a.submit_count ?? "—"}</td>
        <td style="font-family:var(--mono)">${a.poc_count ?? "—"}</td>
      </tr>`;
    }).join("") : `<tr><td colspan="7" style="text-align:center;color:var(--muted);padding:36px">No audits in this view — try "All".</td></tr>`;

    body.querySelectorAll("tr[data-audit-id]").forEach(row => {
      row.addEventListener("click", () => doSwitchAudit(row.dataset.auditId));
    });
  }

  // ──────────────────────────────────────────── Tab switching
  let activeTab = "dashboard";

  function showTab(tab) {
    activeTab = tab;
    const dashView = document.getElementById("mainGrid");
    const allView  = document.getElementById("allAuditsView");
    const pagBar   = document.getElementById("paginationBar");
    const dashBtn  = document.getElementById("tabDashBtn");
    const allBtn   = document.getElementById("tabAllAuditsBtn");
    if (tab === "dashboard") {
      if (dashView) dashView.style.display = "";
      if (pagBar)   pagBar.style.display = "";
      if (allView)  allView.style.display = "none";
      dashBtn?.classList.add("active");
      allBtn?.classList.remove("active");
    } else {
      if (dashView) dashView.style.display = "none";
      if (pagBar)   pagBar.style.display = "none";
      if (allView)  allView.style.display = "";
      dashBtn?.classList.remove("active");
      allBtn?.classList.add("active");
      // Refresh audit list
      const activeId = (state?.active_audit || {}).audit_id || null;
      fetchAudits().then(data => {
        renderAuditSwitcher(data.audits, data.active_audit_id);
        renderAllAuditsTab(data.audits, data.active_audit_id);
      });
    }
  }

  document.getElementById("tabDashBtn")?.addEventListener("click", () => showTab("dashboard"));
  document.getElementById("tabAllAuditsBtn")?.addEventListener("click", () => showTab("all-audits"));

  // Sort header for All Audits table
  document.getElementById("auditsTblHead")?.addEventListener("click", (e) => {
    const th = e.target.closest("th[data-col]");
    if (!th) return;
    const col = th.dataset.col;
    if (auditsTblSort.col === col) {
      auditsTblSort.dir = auditsTblSort.dir === "asc" ? "desc" : "asc";
    } else {
      auditsTblSort.col = col;
      auditsTblSort.dir = "asc";
    }
    const activeId = (state?.active_audit || {}).audit_id || null;
    renderAllAuditsTab(allAuditsData, activeId);
  });

  // Audit switcher dropdown
  document.getElementById("auditSel")?.addEventListener("change", (e) => {
    if (e.target.value) doSwitchAudit(e.target.value);
  });

  // New Audit modal
  const modal = document.getElementById("newAuditModal");
  document.getElementById("auditNewBtn")?.addEventListener("click", () => {
    modal?.classList.add("show");
    document.getElementById("naError").textContent = "";
    document.getElementById("naCreate").disabled = false;
  });
  document.getElementById("naCancel")?.addEventListener("click", () => modal?.classList.remove("show"));
  modal?.addEventListener("click", (e) => { if (e.target === modal) modal.classList.remove("show"); });

  document.getElementById("naCreate")?.addEventListener("click", async () => {
    const auditId = document.getElementById("naId").value.trim();
    const name    = document.getElementById("naName").value.trim();
    if (!auditId || !name) {
      document.getElementById("naError").textContent = "Audit ID and Name are required.";
      return;
    }
    const deadlineVal = document.getElementById("naDeadline").value;
    const body = {
      audit_id:      auditId,
      name,
      contest:       document.getElementById("naContest").value.trim(),
      platform:      document.getElementById("naPlatform").value,
      language:      document.getElementById("naLanguage").value,
      framework:     document.getElementById("naFramework").value.trim(),
      contract_path: document.getElementById("naContractPath").value.trim(),
      deadline:      deadlineVal ? new Date(deadlineVal).toISOString() : "",
      switch_to:     document.getElementById("naSwitchTo").checked,
    };
    document.getElementById("naCreate").disabled = true;
    document.getElementById("naError").textContent = "";
    try {
      const res = await fetch("/api/audits/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || res.statusText);
      modal.classList.remove("show");
      showToast(`Created ${auditId}`);
      if (body.switch_to) {
        history.replaceState(null, "", "?audit=" + encodeURIComponent(auditId));
      }
      // Refresh audits + state
      fetchAudits().then(d => renderAuditSwitcher(d.audits, d.active_audit_id));
      clearTimeout(pollTimer);
      poll();
    } catch (err) {
      document.getElementById("naError").textContent = err.message;
      document.getElementById("naCreate").disabled = false;
    }
  });

  // ──────────────────────────────────────────── URL routing
  (async () => {
    const params = new URLSearchParams(window.location.search);
    const auditParam = params.get("audit");
    if (auditParam) {
      try {
        await fetch("/api/audits/switch", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ audit_id: auditParam }),
        });
      } catch {}
    }
    // Load initial audit list for the switcher
    const auditData = await fetchAudits();
    renderAuditSwitcher(auditData.audits, auditData.active_audit_id);
  })();

  // ────────────────────────────────────────────────────── boot
  poll();
  // Restore chat panel open state
  if (persisted.chat.open) document.body.classList.add("chat-open");
  renderChatMsgs();
  syncQueueFromHistory();
  renderQueue();

  // Restore detail panel if previously open
  if (persisted.detail.open && persisted.detail.id) {
    // Defer until first state arrives.
    const reopen = setInterval(() => {
      if (state && state.findings.some(f => f.id === persisted.detail.id)) {
        clearInterval(reopen);
        openDetail(persisted.detail.id);
      }
    }, 200);
    setTimeout(() => clearInterval(reopen), 3000);
  }
})();
