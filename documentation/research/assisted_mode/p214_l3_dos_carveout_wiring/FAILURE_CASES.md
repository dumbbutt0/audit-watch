# P214 — failure cases & limitations

1. **Human-judgment criteria are operator-set booleans.** `no_practical_workaround`, `supported_asset_or_path`,
   `affects_user_class_or_protocol_function`, `not_self_inflicted_only` are not auto-derived; the gate enforces they are
   explicitly True + (when human_judgment_required) backed by written notes, but the judgment itself is human. SOPH-03's
   notes record that judgment.
2. **Single live positive (SOPH-03).** The upgrade path has one real record so far; more deterministic-core-path-DoS
   positives across corpora would further harden it.
3. **Dashboard server launch is flaky in this harness** (background-process lifecycle); the `/api/p212` flag-on/off
   behavior was verified deterministically by calling `dashboard.api_p212()` directly rather than via a live server.
4. **Flag must be enabled per process** (`AUDITWATCH_L3_READINESS=1`); default-off everywhere → SOPH-03 still shows
   Medium until an operator enables the flag (intended).
5. **Carve-out reads explicit record fields**, not prose; records authored before P214 lack them → no upgrade (safe).
