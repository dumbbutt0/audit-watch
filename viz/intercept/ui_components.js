/**
 * viz/intercept/ui_components.js — Intercept layer UI for the reasoning graph.
 *
 * Adds to existing index.html:
 *   - Intercept toolbar below the header
 *   - Pending events panel (overlays detail panel)
 *   - Modify modal
 *   - Breakpoint manager panel
 *   - Fork comparison container
 *   - Cassette status indicator
 *
 * Served at /intercept/ui.js and loaded via <script> tag in index.html.
 * All functions namespaced under window.intercept to avoid collisions.
 */

(function() {
'use strict';

// ── State ─────────────────────────────────────────────────────────────────────

const intercept = {
  enabled: true,
  pendingCount: 0,
  pendingEvents: [],
  breakpoints: [],
  cassetteCount: 0,
  sessionId: null,
  forkMode: false,
  forkSessions: [],
};

window._intercept = intercept;

// ── CSS injection ─────────────────────────────────────────────────────────────

function injectCSS() {
  const style = document.createElement('style');
  style.textContent = `
  /* ── Intercept toolbar ── */
  #intercept-toolbar {
    height: 36px; background: #1a1f2e; border-bottom: 1px solid #1e2433;
    display: flex; align-items: center; padding: 0 14px; gap: 10px;
    flex-shrink: 0; z-index: 19;
  }
  .ibt-btn {
    background: #141720; border: 1px solid #1e2433; color: #5a6478;
    font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 600;
    padding: 3px 10px; cursor: pointer; border-radius: 3px; white-space: nowrap;
    transition: color .15s, border-color .15s, background .15s;
    display: flex; align-items: center; gap: 5px;
  }
  .ibt-btn:hover { color: #c8d0e0; border-color: #5a6478; }
  .ibt-btn.active { color: #00d4aa; border-color: #00d4aa; }
  .ibt-btn.pending-badge { color: #ffaa00; border-color: #ffaa00; }
  .ibt-badge {
    background: #ffaa00; color: #0a0b0d; border-radius: 10px;
    padding: 1px 6px; font-size: 9px; font-weight: 700; min-width: 16px; text-align: center;
  }
  .cassette-status { font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #5a6478;
    cursor: pointer; margin-left: auto; }
  .cassette-status:hover { color: #c8d0e0; }

  /* ── Slide panels (pending, breakpoints, cassette) ── */
  .slide-panel {
    position: fixed; top: 0; right: -420px; width: 420px; height: 100vh;
    background: #141720; border-left: 1px solid #1e2433; z-index: 100;
    display: flex; flex-direction: column;
    transition: right .25s cubic-bezier(.4,0,.2,1);
    box-shadow: -4px 0 24px rgba(0,0,0,.5);
  }
  .slide-panel.open { right: 0; }
  .sp-header {
    height: 44px; display: flex; align-items: center; padding: 0 16px;
    border-bottom: 1px solid #1e2433; flex-shrink: 0;
    font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: 600;
    color: #c8d0e0; gap: 10px;
  }
  .sp-close { margin-left: auto; cursor: pointer; color: #5a6478; font-size: 16px; }
  .sp-close:hover { color: #c8d0e0; }
  .sp-body { flex: 1; overflow-y: auto; padding: 12px; }
  .sp-body::-webkit-scrollbar { width: 4px; }
  .sp-body::-webkit-scrollbar-thumb { background: #1e2433; border-radius: 2px; }

  /* ── Pending event cards ── */
  .pend-card {
    background: #0d0f12; border: 1px solid #1e2433; border-radius: 4px;
    padding: 10px 12px; margin-bottom: 8px;
  }
  .pend-card.locked { border-color: #ffaa00; opacity: .95; }
  .pend-card-header {
    display: flex; align-items: center; gap: 8px; margin-bottom: 6px;
  }
  .pend-time { font-family: 'JetBrains Mono', monospace; font-size: 9px; color: #5a6478; }
  .pend-type { font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 600; color: #ffaa00; }
  .pend-target { font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #00d4aa; }
  .pend-payload { font-size: 9px; color: #5a6478; font-family: 'JetBrains Mono', monospace;
    white-space: pre-wrap; word-break: break-all; margin-bottom: 8px; max-height: 80px; overflow: auto; }
  .pend-actions { display: flex; gap: 6px; }
  .pend-btn {
    font-family: 'JetBrains Mono', monospace; font-size: 9px; font-weight: 600;
    padding: 3px 9px; border: 1px solid; border-radius: 3px; cursor: pointer;
    background: transparent; transition: background .12s;
  }
  .pend-btn.release { color: #00d4aa; border-color: #00d4aa; }
  .pend-btn.release:hover { background: rgba(0,212,170,.1); }
  .pend-btn.modify  { color: #ffaa00; border-color: #ffaa00; }
  .pend-btn.modify:hover  { background: rgba(255,170,0,.1); }
  .pend-btn.drop    { color: #ff3355; border-color: #ff3355; }
  .pend-btn.drop:hover    { background: rgba(255,51,85,.1); }

  /* ── Modify modal ── */
  #modify-modal {
    position: fixed; inset: 0; background: rgba(0,0,0,.7); z-index: 200;
    display: none; align-items: center; justify-content: center;
  }
  #modify-modal.open { display: flex; }
  .modal-box {
    background: #141720; border: 1px solid #1e2433; border-radius: 6px;
    width: 480px; padding: 20px; position: relative;
  }
  .modal-title { font-family: 'JetBrains Mono', monospace; font-size: 12px; font-weight: 600;
    color: #c8d0e0; margin-bottom: 16px; }
  .modal-row { margin-bottom: 12px; }
  .modal-label { font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #5a6478;
    margin-bottom: 4px; }
  .modal-val { font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #ffaa00;
    background: #0d0f12; padding: 4px 8px; border-radius: 3px; }
  .modal-select, .modal-input {
    width: 100%; background: #0d0f12; border: 1px solid #1e2433; color: #c8d0e0;
    font-family: 'JetBrains Mono', monospace; font-size: 11px;
    padding: 5px 8px; border-radius: 3px; outline: none;
  }
  .modal-select:focus, .modal-input:focus { border-color: #00d4aa; }
  .modal-preview { background: #0d0f12; border: 1px solid #1e2433; border-radius: 3px;
    padding: 8px; font-size: 9px; color: #5a6478; font-family: 'JetBrains Mono', monospace;
    margin-top: 4px; min-height: 40px; }
  .modal-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 16px; }
  .modal-btn {
    font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 600;
    padding: 5px 14px; border: 1px solid; border-radius: 3px; cursor: pointer;
    background: transparent; transition: background .12s;
  }
  .modal-btn.cancel { color: #5a6478; border-color: #5a6478; }
  .modal-btn.cancel:hover { background: rgba(90,100,120,.1); }
  .modal-btn.apply { color: #00d4aa; border-color: #00d4aa; }
  .modal-btn.apply:hover { background: rgba(0,212,170,.1); }

  /* ── Breakpoint manager ── */
  .bp-card {
    background: #0d0f12; border: 1px solid #1e2433; border-radius: 4px;
    padding: 8px 12px; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;
  }
  .bp-toggle { width: 12px; height: 12px; border-radius: 50%; border: 2px solid #00d4aa;
    cursor: pointer; flex-shrink: 0; }
  .bp-toggle.on { background: #00d4aa; }
  .bp-toggle.off { background: transparent; border-color: #3d4458; }
  .bp-label { flex: 1; font-family: 'JetBrains Mono', monospace; font-size: 10px; color: #c8d0e0; }
  .bp-del { color: #ff3355; cursor: pointer; font-size: 14px; }
  .bp-del:hover { color: #ff5577; }
  .bp-add-form {
    border: 1px dashed #1e2433; border-radius: 4px; padding: 10px 12px; margin-top: 8px;
  }
  .bp-add-row { display: flex; gap: 6px; margin-bottom: 8px; }
  .bp-add-row select, .bp-add-row input {
    flex: 1; background: #0d0f12; border: 1px solid #1e2433; color: #c8d0e0;
    font-family: 'JetBrains Mono', monospace; font-size: 10px; padding: 4px 7px; border-radius: 3px;
  }
  .bp-submit {
    width: 100%; font-family: 'JetBrains Mono', monospace; font-size: 10px; font-weight: 600;
    padding: 5px; border: 1px solid #00d4aa; color: #00d4aa; background: transparent;
    border-radius: 3px; cursor: pointer;
  }
  .bp-submit:hover { background: rgba(0,212,170,.1); }

  /* ── Swimlane pending indicator ── */
  .pending-lock {
    animation: lock-pulse 1.2s ease-in-out infinite;
  }
  @keyframes lock-pulse {
    0%, 100% { opacity: .9; }
    50% { opacity: .35; }
  }

  /* ── Fork comparison ── */
  #fork-compare {
    display: none; position: fixed; inset: 0; background: #0a0b0d;
    z-index: 90; flex-direction: column;
  }
  #fork-compare.open { display: flex; }
  #fork-compare-header {
    height: 44px; background: #141720; border-bottom: 1px solid #1e2433;
    display: flex; align-items: center; padding: 0 16px; gap: 14px;
    font-family: 'JetBrains Mono', monospace; font-size: 11px; color: #c8d0e0;
  }
  #fork-compare-body { flex: 1; display: flex; overflow: hidden; }
  .fork-pane { flex: 1; overflow: auto; border-right: 1px solid #1e2433; }
  .fork-pane:last-child { border-right: none; }
  .fork-pane-title {
    position: sticky; top: 0; background: #141720; border-bottom: 1px solid #1e2433;
    padding: 6px 12px; font-family: 'JetBrains Mono', monospace; font-size: 10px;
    color: #5a6478; z-index: 5;
  }

  /* ── Cassette panel ── */
  .cass-frame {
    background: #0d0f12; border: 1px solid #1e2433; border-radius: 3px;
    padding: 7px 10px; margin-bottom: 6px;
    font-family: 'JetBrains Mono', monospace; font-size: 9px;
  }
  .cass-agent { color: #00d4aa; font-weight: 600; }
  .cass-tokens { color: #5a6478; }
  .cass-time { color: #3d4458; }
  `;
  document.head.appendChild(style);
}

// ── HTML injection ────────────────────────────────────────────────────────────

function injectHTML() {
  // 1. Intercept toolbar (injected after #header)
  const header = document.getElementById('header');
  if (header) {
    const toolbar = document.createElement('div');
    toolbar.id = 'intercept-toolbar';
    toolbar.innerHTML = `
      <button class="ibt-btn active" id="ibt-toggle" onclick="window._intercept.toggleIntercept()">
        ● INTERCEPT
      </button>
      <button class="ibt-btn" onclick="window._intercept.openPanel('bp-panel')">
        + BREAKPOINT
      </button>
      <button class="ibt-btn" id="ibt-pending" onclick="window._intercept.openPanel('pending-panel')">
        ⚡ <span id="ibt-pending-count">0</span> PENDING
      </button>
      <button class="ibt-btn" onclick="window._intercept.openPanel('rep-panel')">
        ▶ REPEATER
      </button>
      <button class="ibt-btn" id="ibt-forks" onclick="window._intercept.openForkCompare()">
        ⑂ FORKS
      </button>
      <span class="cassette-status" id="cassette-status" onclick="window._intercept.openPanel('cass-panel')">
        📼 cassette: <span id="cass-count">0</span> frames
      </span>
    `;
    header.insertAdjacentElement('afterend', toolbar);
  }

  // 2. Pending events panel
  document.body.insertAdjacentHTML('beforeend', `
    <div class="slide-panel" id="pending-panel">
      <div class="sp-header">
        HELD EVENTS
        <span id="pending-panel-count" style="color:#ffaa00"></span>
        <span class="sp-close" onclick="window._intercept.closePanel('pending-panel')">✕</span>
      </div>
      <div class="sp-body" id="pending-list"></div>
    </div>
  `);

  // 3. Breakpoint manager panel
  document.body.insertAdjacentHTML('beforeend', `
    <div class="slide-panel" id="bp-panel">
      <div class="sp-header">
        BREAKPOINTS
        <span class="sp-close" onclick="window._intercept.closePanel('bp-panel')">✕</span>
      </div>
      <div class="sp-body">
        <div id="bp-list"></div>
        <div class="bp-add-form">
          <div style="font-family:var(--mono);font-size:10px;color:#5a6478;margin-bottom:8px">+ Add condition:</div>
          <div class="bp-add-row">
            <select id="bp-field">
              <option>event_type</option>
              <option>target_node_id</option>
              <option>source_agent</option>
              <option>payload.confidence</option>
              <option>payload.severity_ceiling</option>
              <option>payload.decision</option>
              <option>payload.reason</option>
            </select>
            <select id="bp-op">
              <option>eq</option>
              <option>neq</option>
              <option>lt</option>
              <option>gt</option>
              <option>contains</option>
              <option>matches</option>
            </select>
            <input id="bp-val" placeholder="value" />
          </div>
          <button class="bp-submit" onclick="window._intercept.addBreakpoint()">ADD BREAKPOINT</button>
        </div>
      </div>
    </div>
  `);

  // 4. Cassette panel
  document.body.insertAdjacentHTML('beforeend', `
    <div class="slide-panel" id="cass-panel">
      <div class="sp-header">
        CASSETTE — LLM CALL HISTORY
        <span class="sp-close" onclick="window._intercept.closePanel('cass-panel')">✕</span>
      </div>
      <div class="sp-body" id="cass-list"></div>
    </div>
  `);

  // 5. Repeater panel (minimal for now)
  document.body.insertAdjacentHTML('beforeend', `
    <div class="slide-panel" id="rep-panel">
      <div class="sp-header">
        EVENT REPEATER
        <span class="sp-close" onclick="window._intercept.closePanel('rep-panel')">✕</span>
      </div>
      <div class="sp-body">
        <div style="color:#5a6478;font-family:var(--mono);font-size:10px">
          Right-click any event row and choose "Send to Repeater"<br/><br/>
          Or enter an event ID:<br/>
          <input id="rep-event-id" placeholder="event_id" style="width:100%;background:#0d0f12;border:1px solid #1e2433;color:#c8d0e0;font-family:var(--mono);font-size:10px;padding:5px 8px;border-radius:3px;margin-top:6px"/>
          <button class="bp-submit" style="margin-top:8px" onclick="window._intercept.captureAndReplay()">CAPTURE &amp; DRY RUN</button>
        </div>
        <div id="rep-result" style="margin-top:12px;font-family:var(--mono);font-size:9px;color:#5a6478"></div>
      </div>
    </div>
  `);

  // 6. Modify modal
  document.body.insertAdjacentHTML('beforeend', `
    <div id="modify-modal">
      <div class="modal-box">
        <div class="modal-title" id="modify-modal-title">MODIFY EVENT</div>
        <div class="modal-row">
          <div class="modal-label">Field</div>
          <select class="modal-select" id="modify-field">
            <option>payload.decision</option>
            <option>payload.reason</option>
            <option>payload.confidence</option>
            <option>payload.severity_ceiling</option>
            <option>event_type</option>
          </select>
        </div>
        <div class="modal-row">
          <div class="modal-label">Old value</div>
          <div class="modal-val" id="modify-old-val">—</div>
        </div>
        <div class="modal-row">
          <div class="modal-label">New value</div>
          <input class="modal-input" id="modify-new-val" placeholder="new value" oninput="window._intercept.updateModifyPreview()"/>
        </div>
        <div class="modal-row">
          <div class="modal-label">Effect preview</div>
          <div class="modal-preview" id="modify-preview">—</div>
        </div>
        <div class="modal-actions">
          <button class="modal-btn cancel" onclick="window._intercept.closeModifyModal()">CANCEL</button>
          <button class="modal-btn apply" onclick="window._intercept.applyModification()">APPLY &amp; RELEASE</button>
        </div>
      </div>
    </div>
  `);

  // 7. Fork comparison container
  document.body.insertAdjacentHTML('beforeend', `
    <div id="fork-compare">
      <div id="fork-compare-header">
        <span>FORK COMPARISON</span>
        <button class="ibt-btn" onclick="window._intercept.closeForkCompare()">✕ CLOSE</button>
        <span id="fork-compare-label" style="color:#5a6478;font-size:10px"></span>
      </div>
      <div id="fork-compare-body">
        <div class="fork-pane" id="fork-pane-left">
          <div class="fork-pane-title">ORIGINAL SESSION</div>
          <div id="fork-pane-left-body" style="padding:12px;font-family:var(--mono);font-size:10px;color:#5a6478">Loading…</div>
        </div>
        <div class="fork-pane" id="fork-pane-right">
          <div class="fork-pane-title">FORK</div>
          <div id="fork-pane-right-body" style="padding:12px;font-family:var(--mono);font-size:10px;color:#5a6478">Loading…</div>
        </div>
      </div>
    </div>
  `);
}

// ── Panel management ──────────────────────────────────────────────────────────

intercept.openPanel = function(id) {
  document.querySelectorAll('.slide-panel').forEach(p => p.classList.remove('open'));
  const panel = document.getElementById(id);
  if (panel) panel.classList.add('open');
  if (id === 'pending-panel') intercept.refreshPending();
  if (id === 'bp-panel') intercept.refreshBreakpoints();
  if (id === 'cass-panel') intercept.refreshCassette();
};

intercept.closePanel = function(id) {
  const panel = document.getElementById(id);
  if (panel) panel.classList.remove('open');
};

// ── Intercept toggle ──────────────────────────────────────────────────────────

intercept.toggleIntercept = function() {
  intercept.enabled = !intercept.enabled;
  const btn = document.getElementById('ibt-toggle');
  if (btn) btn.className = `ibt-btn ${intercept.enabled ? 'active' : ''}`;
};

// ── Pending events ────────────────────────────────────────────────────────────

intercept.refreshPending = async function() {
  const sid = intercept.sessionId;
  if (!sid) return;
  try {
    const r = await fetch(`/api/session/${sid}/pending`);
    const data = await r.json();
    intercept.pendingEvents = data.pending || [];
    intercept.updatePendingBadge(intercept.pendingEvents.length);
    intercept.renderPendingList(intercept.pendingEvents);
  } catch (_) {}
};

intercept.updatePendingBadge = function(n) {
  intercept.pendingCount = n;
  const badge = document.getElementById('ibt-pending-count');
  if (badge) badge.textContent = n;
  const btn = document.getElementById('ibt-pending');
  if (btn) btn.className = `ibt-btn ${n > 0 ? 'pending-badge' : ''}`;
  const header = document.getElementById('pending-panel-count');
  if (header) header.textContent = n > 0 ? `(${n})` : '';
};

intercept.renderPendingList = function(events) {
  const list = document.getElementById('pending-list');
  if (!list) return;
  if (!events.length) {
    list.innerHTML = '<div style="color:#3d4458;font-family:var(--mono);font-size:10px;text-align:center;padding:24px">No held events</div>';
    return;
  }
  list.innerHTML = events.map(e => {
    const ts   = (e.timestamp || '').slice(11, 19);
    const eid  = e.event_id || '';
    const pld  = JSON.stringify(e.payload || {}, null, 1).slice(0, 200);
    return `
      <div class="pend-card locked" id="pcard-${eid}">
        <div class="pend-card-header">
          <span class="pend-time">${esc(ts)}</span>
          <span class="pend-type">${esc(e.event_type || '')}</span>
          <span class="pend-target">${esc(e.target_node_id || '')}</span>
        </div>
        <pre class="pend-payload">${esc(pld)}</pre>
        <div class="pend-actions">
          <button class="pend-btn release" onclick="window._intercept.releaseEvent('${eid}')">RELEASE</button>
          <button class="pend-btn modify"  onclick="window._intercept.openModifyModal('${eid}')">MODIFY</button>
          <button class="pend-btn drop"    onclick="window._intercept.dropEvent('${eid}')">DROP</button>
        </div>
      </div>`;
  }).join('');
};

intercept.releaseEvent = async function(eventId) {
  const sid = intercept.sessionId;
  if (!sid) return;
  try {
    await fetch(`/api/session/${sid}/pending/${eventId}/release`, { method: 'POST' });
    intercept.refreshPending();
    intercept.removePendingLock(eventId);
  } catch (_) {}
};

intercept.dropEvent = async function(eventId) {
  const sid = intercept.sessionId;
  if (!sid) return;
  try {
    await fetch(`/api/session/${sid}/pending/${eventId}/drop`, { method: 'POST' });
    intercept.refreshPending();
    intercept.removePendingLock(eventId);
  } catch (_) {}
};

// ── Modify modal ──────────────────────────────────────────────────────────────

intercept._modifyingEventId = null;
intercept._modifyingEvent   = null;

intercept.openModifyModal = function(eventId) {
  const event = intercept.pendingEvents.find(e => e.event_id === eventId);
  if (!event) return;
  intercept._modifyingEventId = eventId;
  intercept._modifyingEvent   = event;

  document.getElementById('modify-modal-title').textContent =
    `MODIFY EVENT · ${event.event_type} · ${event.target_node_id || ''}`;
  document.getElementById('modify-preview').textContent = '—';
  document.getElementById('modify-new-val').value = '';

  // Set default old value for selected field
  intercept.updateModifyOldVal();
  document.getElementById('modify-modal').classList.add('open');
};

intercept.closeModifyModal = function() {
  document.getElementById('modify-modal').classList.remove('open');
};

intercept.updateModifyOldVal = function() {
  if (!intercept._modifyingEvent) return;
  const field = document.getElementById('modify-field').value;
  const parts = field.split('.');
  let obj = intercept._modifyingEvent;
  for (const p of parts) obj = (obj && typeof obj === 'object') ? obj[p] : undefined;
  document.getElementById('modify-old-val').textContent = obj != null ? String(obj) : '—';
  intercept.updateModifyPreview();
};

intercept.updateModifyPreview = function() {
  const field  = document.getElementById('modify-field').value;
  const newVal = document.getElementById('modify-new-val').value;
  const event  = intercept._modifyingEvent;
  if (!event || !field) return;

  let effect = '';
  if (field === 'payload.decision') {
    if (newVal === 'submit')   effect = `${event.target_node_id} → ESCALATED (▶ SUBMIT)`;
    if (newVal === 'rejected') effect = `${event.target_node_id} → INVALIDATED (red wall)`;
  } else if (field === 'payload.confidence') {
    const n = parseFloat(newVal);
    if (!isNaN(n)) effect = `Confidence set to ${n.toFixed(2)}`;
  } else if (field === 'event_type') {
    effect = `Event type overridden to ${newVal}`;
  }
  document.getElementById('modify-preview').textContent = effect || `${field} → ${newVal}`;
};

intercept.applyModification = async function() {
  const sid = intercept.sessionId;
  const eid = intercept._modifyingEventId;
  if (!sid || !eid) return;

  const field  = document.getElementById('modify-field').value;
  let   newVal = document.getElementById('modify-new-val').value;

  // Parse numeric values
  if (!isNaN(parseFloat(newVal)) && field.includes('confidence')) {
    newVal = parseFloat(newVal);
  }

  try {
    const r = await fetch(`/api/session/${sid}/pending/${eid}/modify`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ field, new_value: newVal }),
    });
    const data = await r.json();
    if (data.ok) {
      intercept.closeModifyModal();
      intercept.refreshPending();
      intercept.removePendingLock(eid);
    }
  } catch (_) {}
};

// ── Breakpoints ───────────────────────────────────────────────────────────────

intercept.refreshBreakpoints = async function() {
  const sid = intercept.sessionId;
  if (!sid) return;
  try {
    const r = await fetch(`/api/session/${sid}/breakpoints`);
    intercept.breakpoints = await r.json();
    intercept.renderBreakpointList();
  } catch (_) {}
};

intercept.renderBreakpointList = function() {
  const list = document.getElementById('bp-list');
  if (!list) return;
  if (!intercept.breakpoints.length) {
    list.innerHTML = '<div style="color:#3d4458;font-family:var(--mono);font-size:10px;margin-bottom:10px">No breakpoints set</div>';
    return;
  }
  list.innerHTML = intercept.breakpoints.map(bp => {
    const cond = (bp.conditions || []).map(c =>
      `${c.field} ${c.operator} ${c.value}`).join(` ${bp.match_mode === 'all' ? 'AND' : 'OR'} `);
    return `
      <div class="bp-card">
        <div class="bp-toggle ${bp.enabled ? 'on' : 'off'}"
             onclick="window._intercept.toggleBP('${bp.id}', ${!bp.enabled})"
             title="${bp.enabled ? 'Enabled' : 'Disabled'}"></div>
        <div class="bp-label">${esc(cond || bp.label || bp.id)}</div>
        <div class="bp-del" onclick="window._intercept.deleteBP('${bp.id}')">✕</div>
      </div>`;
  }).join('');
};

intercept.addBreakpoint = async function() {
  const sid   = intercept.sessionId;
  const field = document.getElementById('bp-field').value;
  const op    = document.getElementById('bp-op').value;
  let   val   = document.getElementById('bp-val').value.trim();
  if (!sid || !field || !val) return;

  // Coerce numeric value for lt/gt operators
  if ((op === 'lt' || op === 'gt') && !isNaN(parseFloat(val))) val = parseFloat(val);

  try {
    await fetch(`/api/session/${sid}/breakpoints`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        conditions: [{ field, operator: op, value: val }],
        match_mode: 'any',
      }),
    });
    document.getElementById('bp-val').value = '';
    intercept.refreshBreakpoints();
  } catch (_) {}
};

intercept.toggleBP = async function(bpId, enabled) {
  const sid = intercept.sessionId;
  if (!sid) return;
  try {
    await fetch(`/api/session/${sid}/breakpoints/${bpId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled }),
    });
    intercept.refreshBreakpoints();
  } catch (_) {}
};

intercept.deleteBP = async function(bpId) {
  const sid = intercept.sessionId;
  if (!sid) return;
  try {
    await fetch(`/api/session/${sid}/breakpoints/${bpId}`, { method: 'DELETE' });
    intercept.refreshBreakpoints();
  } catch (_) {}
};

// ── Cassette ──────────────────────────────────────────────────────────────────

intercept.refreshCassette = async function() {
  const sid = intercept.sessionId;
  if (!sid) return;
  try {
    const r = await fetch(`/api/session/${sid}/cassette`);
    const data = await r.json();
    const count = data.count || 0;
    intercept.cassetteCount = count;
    const badge = document.getElementById('cass-count');
    if (badge) badge.textContent = count;
    intercept.renderCassetteList(data.frames || []);
  } catch (_) {}
};

intercept.renderCassetteList = function(frames) {
  const list = document.getElementById('cass-list');
  if (!list) return;
  if (!frames.length) {
    list.innerHTML = '<div style="color:#3d4458;font-family:var(--mono);font-size:10px;text-align:center;padding:24px">No LLM calls recorded yet.<br/>Run a pipeline step to populate the cassette.</div>';
    return;
  }
  list.innerHTML = [...frames].reverse().map(f => `
    <div class="cass-frame">
      <span class="cass-agent">${esc(f.agent || '?')}</span>
      <span class="cass-tokens">  in:${f.input_tokens || 0} out:${f.output_tokens || 0}</span>
      <span class="cass-time">  ${esc((f.timestamp || '').slice(11, 19))}</span>
    </div>`).join('');
};

// ── Repeater ──────────────────────────────────────────────────────────────────

intercept.captureAndReplay = async function() {
  const sid = intercept.sessionId;
  const eid = document.getElementById('rep-event-id').value.trim();
  if (!sid || !eid) return;
  const result = document.getElementById('rep-result');
  try {
    const r = await fetch(`/api/session/${sid}/repeater/replay`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ event_id: eid, dry_run: true }),
    });
    const data = await r.json();
    result.textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    result.textContent = `Error: ${e.message}`;
  }
};

// ── Fork comparison ───────────────────────────────────────────────────────────

intercept.openForkCompare = async function() {
  const sid = intercept.sessionId;
  if (!sid) return;
  try {
    const r = await fetch(`/api/session/${sid}/forks`);
    const data = await r.json();
    const forks = data.forks || [];
    if (!forks.length) {
      alert('No forks created yet. Use POST /api/session/{id}/fork to create one.');
      return;
    }
    // Show most recent fork compared to original
    const fork = forks[forks.length - 1];
    document.getElementById('fork-compare-label').textContent =
      `${sid} vs ${fork.fork_id} — ${fork.fork_label || ''}`;
    document.getElementById('fork-compare').classList.add('open');
    intercept.loadForkPane('left', sid);
    intercept.loadForkPane('right', fork.fork_id, fork.branch_from_event_index);
  } catch (_) {}
};

intercept.loadForkPane = async function(side, sessionId, forkIdx) {
  const body = document.getElementById(`fork-pane-${side}-body`);
  if (!body) return;
  try {
    const url = forkIdx !== undefined
      ? `/api/session/${sessionId}/graph?at=${forkIdx}`
      : `/api/session/${sessionId}/graph`;
    const r = await fetch(url);
    const graph = await r.json();
    const nodes = (graph.nodes || []).filter(n => n.node_type === 'hypothesis');
    body.innerHTML = nodes.map(n => `
      <div style="padding:6px 0;border-bottom:1px solid #1e2433">
        <span style="color:${statusColor(n.status)}">${esc(n.id)}</span>
        <span style="color:#5a6478"> ${esc(n.label || '').slice(0, 40)}</span>
        <span style="color:#5a6478"> conf=${((n.confidence || 0) * 100).toFixed(0)}%</span>
        <span style="color:${statusColor(n.status)};margin-left:8px">${esc(n.status)}</span>
      </div>`).join('') || '<div style="color:#3d4458">No hypotheses</div>';
  } catch (e) {
    body.textContent = `Error: ${e.message}`;
  }
};

intercept.closeForkCompare = function() {
  document.getElementById('fork-compare').classList.remove('open');
};

function statusColor(s) {
  const m = { LIVE: '#00d4aa', CONVERGED: '#00ff88', INVALIDATED: '#ff3355',
    PRUNED: '#3d4458', ESCALATED: '#ffaa00' };
  return m[s] || '#5a6478';
}

// ── Swimlane visual indicators ────────────────────────────────────────────────

intercept.addPendingLock = function(nodeId, stageX) {
  // Called by WebSocket handler when GATE_OPENED arrives
  const svg = d3 && typeof d3 !== 'undefined' ? d3.select('#graph-svg') : null;
  if (!svg) return;
  const rows = (typeof layoutRows === 'function' && typeof graphData !== 'undefined')
    ? layoutRows(graphData.nodes || []) : [];
  const row = rows.find(r => r.node && r.node.id === nodeId);
  if (!row) return;

  svg.select(`#lock-${nodeId}`).remove();
  const g = svg.select('#lanes-group');
  if (g.empty()) return;

  g.append('text')
    .attr('id', `lock-${nodeId}`)
    .attr('x', stageX || 660)
    .attr('y', row.y + 4)
    .attr('text-anchor', 'middle')
    .attr('font-size', 14)
    .attr('fill', '#ffaa00')
    .attr('class', 'pending-lock')
    .text('⊙');

  // Dim the row
  const rowGroup = svg.select(`#lane-${nodeId}`);
  if (!rowGroup.empty()) rowGroup.style('opacity', 0.4);
};

intercept.removePendingLock = function(eventId) {
  // Find node for this event
  const event = intercept.pendingEvents.find(e => e.event_id === eventId);
  if (!event) return;
  const nodeId = event.target_node_id;
  if (!nodeId) return;

  const svg = typeof d3 !== 'undefined' ? d3.select('#graph-svg') : null;
  if (!svg) return;
  svg.select(`#lock-${nodeId}`).remove();
  svg.select(`#lane-${nodeId}`).style('opacity', null);
};

// ── WebSocket handler integration ─────────────────────────────────────────────

intercept.handleWsMessage = function(msg) {
  if (msg.type === 'intercept_state') {
    intercept.breakpoints = msg.breakpoints || [];
    intercept.updatePendingBadge((msg.pending || []).length);
    intercept.pendingEvents = msg.pending || [];
    // Refresh open panels
    if (document.getElementById('pending-panel').classList.contains('open')) {
      intercept.renderPendingList(intercept.pendingEvents);
    }
    if (document.getElementById('bp-panel').classList.contains('open')) {
      intercept.renderBreakpointList();
    }
  } else if (msg.type === 'event' && msg.event) {
    const et = msg.event.event_type;
    if (et === 'GATE_OPENED') {
      intercept.updatePendingBadge(intercept.pendingCount + 1);
    } else if (et === 'GATE_RELEASED' || et === 'GATE_MODIFIED' || et === 'GATE_DROPPED') {
      intercept.updatePendingBadge(Math.max(0, intercept.pendingCount - 1));
    }
  }
};

// ── Utility ───────────────────────────────────────────────────────────────────

function esc(s) {
  return String(s ?? '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// ── Init ──────────────────────────────────────────────────────────────────────

intercept.init = function(sessionId) {
  intercept.sessionId = sessionId;
  injectCSS();
  injectHTML();

  // Wire modify-field select to update old-val preview
  setTimeout(() => {
    const sel = document.getElementById('modify-field');
    if (sel) sel.addEventListener('change', intercept.updateModifyOldVal);
  }, 100);

  // Poll cassette count every 30s
  setInterval(intercept.refreshCassette, 30000);
  intercept.refreshCassette();
};

// Export
window._intercept = intercept;

})();
