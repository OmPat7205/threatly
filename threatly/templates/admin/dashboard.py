ADMIN_DASHBOARD_TEMPLATE = r"""
<style>
  /* ---- KPI layout + tooltip (scoped to dashboard) ---- */
  .kpi-grid{
    margin-top:12px;
    display:grid;
    grid-template-columns: repeat(5, minmax(160px, 1fr));
    gap:12px;
  }
  @media (max-width: 1100px){
    .kpi-grid{ grid-template-columns: repeat(2, minmax(160px, 1fr)); }
  }

  /* ---- Range selector ---- */
  .range-row{
    margin-top:12px;
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:12px;
    flex-wrap:wrap;
  }
  .seg{
    display:inline-flex;
    gap:8px;
    padding:6px;
    border:1px solid rgba(255,255,255,.10);
    border-radius: calc(var(--r) + 4px);
    background: rgba(24,24,27,.25);
  }
  .seg a{
    text-decoration:none;
    color: rgba(250,250,250,.85);
    font-weight:850;
    font-size:12px;
    padding:8px 10px;
    border-radius: 10px;
    border:1px solid transparent;
    background: rgba(255,255,255,.02);
    transition: transform .05s ease, background .15s ease, border-color .15s ease;
    user-select:none;
  }
  .seg a:hover{ background: rgba(255,255,255,.04); border-color: rgba(255,255,255,.08); }
  .seg a.active{
    background: rgba(34,197,94,.14);
    border-color: rgba(34,197,94,.35);
    color: rgba(250,250,250,.95);
  }

  /* Hide custom date picker unless Custom is active */
  .custom{
    display:none;
    align-items:center;
    gap:8px;
    padding:6px 8px;
    border:1px solid rgba(255,255,255,.10);
    border-radius: calc(var(--r) + 4px);
    background: rgba(24,24,27,.25);
  }
  .custom.show{ display:flex; }

  .custom input{
    background: rgba(255,255,255,.03);
    border:1px solid rgba(255,255,255,.08);
    color: rgba(250,250,250,.9);
    border-radius: 10px;
    padding:8px 10px;
    font-weight:800;
    font-size:12px;
    outline:none;
  }
  .custom input:focus{ border-color: rgba(34,197,94,.45); }

  .btn{
    display:inline-flex;
    align-items:center;
    justify-content:center;
    gap:8px;
    padding:8px 10px;
    border-radius: 10px;
    border:1px solid rgba(255,255,255,.10);
    background: rgba(255,255,255,.04);
    color: rgba(250,250,250,.92);
    font-weight:900;
    font-size:12px;
    cursor:pointer;
    user-select:none;
  }
  .btn:hover{ background: rgba(255,255,255,.06); }
  .btn:active{ transform: translateY(1px); }

  .btn.ghost{
    background: rgba(255,255,255,.02);
    border-color: rgba(255,255,255,.08);
    color: rgba(250,250,250,.82);
  }
  .btn.ghost:hover{ background: rgba(255,255,255,.04); }

  /* ---- ONE audit window banner (wrap-safe) ---- */
  .audit-window{
    margin-top:10px;
    display:flex;
    align-items:center;
    gap:8px;
    flex-wrap:wrap;
    min-width:0;
  }
  .audit-window-label{
    color: var(--muted2);
    font-weight:750;
    font-size:12px;
    white-space:nowrap;
  }
  .audit-window-pill{
    display:inline-flex;
    align-items:center;
    padding:6px 10px;
    border-radius:999px;
    border:1px solid rgba(255,255,255,.12);
    background: rgba(255,255,255,.04);
    color: rgba(250,250,250,.92);
    font-weight:850;
    font-size:12px;
    white-space:normal;
    overflow-wrap:anywhere;
    word-break:break-word;
    max-width:100%;
  }

  /* ---- KPI cards ---- */
  .kpi-card{
    position: relative;
    padding:14px 14px;
    border:1px solid rgba(255,255,255,.10);
    border-radius: 16px;
    background: rgba(24,24,27,.28);
    box-shadow: 0 10px 26px rgba(0,0,0,.28);
    overflow: visible; /* let tooltip escape */
  }

  /* Window-based KPI emphasis */
  .kpi-card.window{
    border-color: rgba(34,197,94,.18);
    box-shadow:
      0 10px 26px rgba(0,0,0,.28),
      0 0 0 1px rgba(34,197,94,.07) inset;
  }

  .kpi-head{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:10px;
    min-width:0;
  }

  .kpi-label{
    color: rgba(250,250,250,.68);
    font-weight:800;
    font-size:12px;
    letter-spacing:.2px;
    min-width:0;
    white-space:nowrap;
    overflow:hidden;
    text-overflow:ellipsis;
  }

  .kpi-value{
    font-size:26px;
    font-weight:950;
    margin-top:6px;
    letter-spacing:.2px;
  }

  .kpi-value.small{
    font-size:16px;
    font-weight:900;
    margin-top:8px;
    letter-spacing:0;
  }

  .kpi-sub{
    color: rgba(250,250,250,.55);
    font-weight:750;
    font-size:12px;
    margin-top:10px;
  }

  /* Icon-only window badge */
  .kpi-badge{
    display:inline-flex;
    align-items:center;
    justify-content:center;
    width:26px;
    height:20px;
    border-radius:999px;
    border:1px solid rgba(255,255,255,.12);
    background: rgba(255,255,255,.04);
    color: rgba(250,250,250,.82);
    font-weight:900;
    font-size:11px;
    line-height:1;
    user-select:none;
    margin-left:8px;
  }
  .kpi-badge.window{
    border-color: rgba(34,197,94,.18);
    background: rgba(34,197,94,.10);
    color: rgba(250,250,250,.90);
  }

  /* Styled tooltip using data-tip */
  .tip{
    position:relative;
    display:inline-flex;
    align-items:center;
    justify-content:center;
    width:18px; height:18px;
    border-radius:999px;
    border:1px solid rgba(255,255,255,.12);
    background: rgba(255,255,255,.03);
    color: rgba(250,250,250,.75);
    font-weight:950;
    font-size:12px;
    flex:0 0 auto;
    cursor:help;
    user-select:none;
  }
  .tip::after{
    content: attr(data-tip);
    position:absolute;
    left:50%;
    bottom: calc(100% + 10px);
    transform: translateX(-50%);
    width: 260px;
    max-width: min(340px, 70vw);
    padding:10px 12px;
    border-radius: 10px;
    border:1px solid rgba(255,255,255,.10);
    background: rgba(18,18,20,.98);
    box-shadow: 0 18px 40px rgba(0,0,0,.55);
    color: rgba(250,250,250,.92);
    font-size:12px;
    font-weight:750;
    line-height:1.35;
    opacity:0;
    pointer-events:none;
    white-space:normal;
    z-index: 99999;
  }
  .tip::before{
    content:"";
    position:absolute;
    left:50%;
    bottom: calc(100% + 4px);
    transform: translateX(-50%);
    width:0; height:0;
    border-left:7px solid transparent;
    border-right:7px solid transparent;
    border-top:7px solid rgba(18,18,20,.98);
    opacity:0;
    pointer-events:none;
    z-index: 99999;
  }
  .tip:hover::after,
  .tip:hover::before{ opacity:1; }
  .tip:focus::after,
  .tip:focus::before{ opacity:1; }

  /* Top action card internals */
  .top-action{
    margin-top:10px;
    display:flex;
    gap:12px;
    align-items:flex-end;
    justify-content:space-between;
    min-width:0;
  }

@media (max-width: 1100px){
  .top-action{
    flex-direction:column;
    align-items:flex-start;
  }
  .top-right{
    flex: 0 0 auto;
    width: 100%;
    max-width: none;
  }
}

  .top-left{
    min-width:0;
    flex: 1 1 62%;
  }


  .top-name{
    font-size:22px;
    font-weight:950;
    margin-top:10px;
    letter-spacing:.2px;
    line-height:1.15;

    /* ✅ allow normal wrapping, never letter-split */
    white-space: normal !important;
    word-break: normal !important;
    overflow-wrap: normal !important;

    /* ✅ show up to 2 full lines, no weird crop */
    display: block !important;
    overflow: visible !important;
  }

  .top-name wbr{ display:inline; }



  .pill{
    display:inline-flex;
    align-items:center;
    padding:4px 8px;
    border-radius:999px;
    border:1px solid rgba(255,255,255,.12);
    background: rgba(255,255,255,.03);
    font-weight:900;
    font-size:12px;
    color: rgba(250,250,250,.92);
    white-space:nowrap;
  }
  .top-right{
    flex: 0 0 38%;
    min-width:120px;
    max-width:240px;
  }

  .bar{
    height:8px;
    border-radius:999px;
    background: rgba(255,255,255,.06);
    border:1px solid rgba(255,255,255,.08);
    overflow:hidden;
  }
  .bar > div{
    height:100%;
    background: rgba(34,197,94,.85);
    width:0%;
  }
</style>

{# --- Pretty formatting helpers (no Python needed) --- #}
{% set MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'] %}

{% macro pretty_iso(s) -%}
  {%- set x = (s or '') -%}
  {%- if x|length >= 19 -%}
    {%- set mm = x[5:7]|int -%}
    {%- set dd = x[8:10]|int -%}
    {%- set yyyy = x[0:4] -%}
    {%- set hhmm = x[11:16] -%}
    {{ MONTHS[mm-1] }} {{ dd }}, {{ yyyy }} · {{ hhmm }} UTC
  {%- elif x|length >= 10 -%}
    {%- set mm = x[5:7]|int -%}
    {%- set dd = x[8:10]|int -%}
    {%- set yyyy = x[0:4] -%}
    {{ MONTHS[mm-1] }} {{ dd }}, {{ yyyy }}
  {%- else -%}
    {{ x }}
  {%- endif -%}
{%- endmacro %}

{% macro window_label(w) -%}
  {%- if w == '24h' -%}Last 24h
  {%- elif w == '7d' -%}Last 7d
  {%- elif w == '30d' -%}Last 30d
  {%- elif w == '90d' -%}Last 90d
  {%- elif w == 'custom' -%}Custom
  {%- else -%}{{ w }}
  {%- endif -%}
{%- endmacro %}

<div class="card">
  <div style="display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap;">
    <div>
      <div style="font-size:18px; font-weight:850;">Summary</div>
      <div class="muted2">Core admin KPIs (live from state DB)</div>
    </div>
  </div>

  {# ---- window model ---- #}
  {% set w = (window.w if window and window.w else '24h') %}
  {% set w_from = (window.from if window and window.from else '') %}
  {% set w_to = (window.to if window and window.to else '') %}
  {% set w_start = (window.start_utc if window and window.start_utc else '') %}
  {% set w_end = (window.end_utc if window and window.end_utc else '') %}

  {# ---- ONE banner only ---- #}
  <div class="audit-window">
    <span class="audit-window-label">Showing audit window:</span>
    <span class="audit-window-pill"
          title="{% if w_start and w_end %}{{ w_start }} → {{ w_end }}{% else %}{{ window_label(w) }}{% endif %}">
      {% if w_start and w_end %}
        {{ pretty_iso(w_start) }} → {{ pretty_iso(w_end) }}
      {% else %}
        {{ window_label(w) }}
      {% endif %}
    </span>
  </div>

  <div class="range-row">
    <div class="seg" aria-label="Time range">
      <a class="{{ 'active' if w=='24h' else '' }}" href="/admin/?w=24h">24h</a>
      <a class="{{ 'active' if w=='7d' else '' }}" href="/admin/?w=7d">7d</a>
      <a class="{{ 'active' if w=='30d' else '' }}" href="/admin/?w=30d">30d</a>
      <a class="{{ 'active' if w=='90d' else '' }}" href="/admin/?w=90d">90d</a>
      <a class="{{ 'active' if w=='custom' else '' }}"
        href="/admin/?w=custom{% if w_from %}&from={{ w_from }}{% endif %}{% if w_to %}&to={{ w_to }}{% endif %}">
        Custom
      </a>
    </div>

    <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
      <form class="custom {{ 'show' if w=='custom' else '' }}" method="get" action="/admin/">
        <input type="hidden" name="w" value="custom"/>
        <input type="date" name="from" value="{{ w_from }}" aria-label="From date"/>
        <span class="muted2" style="font-weight:900;">→</span>
        <input type="date" name="to" value="{{ w_to }}" aria-label="To date"/>
        <button class="btn" type="submit">Apply</button>
      </form>

      <a class="btn ghost" id="btnExportSeries" href="#">Export chart data (CSV)</a>
      <a class="btn ghost" id="btnExportAudit" href="#">Export audit log (CSV)</a>
    </div>
  </div>

  {# ---- normalize top action safely (WINDOWED KEYS) ---- #}
  {% set top = (kpis.top_actions[0] if kpis.top_actions and kpis.top_actions|length > 0 else None) %}
  {% set top_action = (top.get('action') if top is not none else '') %}
  {% set top_n = (top.get('n', 0) if top is not none else 0) %}
  {% set aw = (kpis.audit_window|int if kpis.audit_window is not none else 0) %}
  {% set denom = (aw if aw > 0 else (top_n|int if top_n|int > 0 else 0)) %}
  {% set pct = ((top_n|int * 100) / denom if denom > 0 else 0) %}
  {% if pct > 100 %}{% set pct = 100 %}{% endif %}

  <!-- Row 1 (state KPIs) -->
  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-head">
        <div class="kpi-label">Total users</div>
        <span class="tip" tabindex="0" data-tip="All users in the users table (including disabled).">i</span>
      </div>
      <div class="kpi-value">{{ kpis.total_users }}</div>
    </div>

    <div class="kpi-card">
      <div class="kpi-head">
        <div class="kpi-label">Active</div>
        <span class="tip" tabindex="0" data-tip="Users with is_active=1 (can sign in).">i</span>
      </div>
      <div class="kpi-value">{{ kpis.active_users }}</div>
    </div>

    <div class="kpi-card">
      <div class="kpi-head">
        <div class="kpi-label">Disabled</div>
        <span class="tip" tabindex="0" data-tip="Users with is_active=0 (cannot sign in).">i</span>
      </div>
      <div class="kpi-value">{{ kpis.disabled_users }}</div>
    </div>

    <div class="kpi-card">
      <div class="kpi-head">
        <div class="kpi-label">Admins</div>
        <span class="tip" tabindex="0" data-tip="Users with role=admin (full admin access).">i</span>
      </div>
      <div class="kpi-value">{{ kpis.admin_users }}</div>
    </div>

    <div class="kpi-card window">
      <div class="kpi-head">
        <div class="kpi-label">Audit <span class="kpi-badge window" title="Respects selected time window">⏱</span></div>
        <span class="tip" tabindex="0" data-tip="Count of admin audit events in the selected time window.">i</span>
      </div>
      <div class="kpi-value" style="text-align:center; font-size:34px; margin-top:8px;">{{ kpis.audit_window }}</div>
    </div>
  </div>

  <!-- Row 2 (windowed audit intelligence) -->
  <div class="kpi-grid" style="margin-top:12px;">
    <div class="kpi-card window">
      <div class="kpi-head">
        <div class="kpi-label">Top action <span class="kpi-badge window" title="Respects selected time window">⏱</span></div>
        <span class="tip" tabindex="0" data-tip="Most common audit event in the selected window. Bar shows its share of total window events.">i</span>
      </div>

      <div class="top-action">
        <div class="top-left">
          <div class="top-name" title="{{ top_action.replace('_', '_<wbr>') | safe }}">
            {% if top_action %}
              {{ top_action.replace('_', '_<wbr>') | safe }}
            {% else %}
              —
            {% endif %}
          </div>

          <div class="kpi-sub">
            <span class="pill">{{ top_n|int }}</span>
            <span class="muted2" style="margin-left:6px;">events</span>
            {% if denom > 0 %}
              <span class="muted2" style="margin-left:10px;">{{ '%.0f' % pct }}% of window</span>
            {% endif %}
          </div>
        </div>

        {% if denom > 0 %}
          <div class="top-right">
            <div class="bar">
              <div style="width: {{ '%.0f' % pct }}%;"></div>
            </div>
          </div>
        {% endif %}
      </div>
    </div>

    <div class="kpi-card window">
      <div class="kpi-head">
        <div class="kpi-label">Last event <span class="kpi-badge window" title="Respects selected time window">⏱</span></div>
        <span class="tip" tabindex="0" data-tip="Most recent admin audit event within the selected window (action + actor).">i</span>
      </div>

      <div class="kpi-value small"
           style="white-space:normal; overflow:hidden; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical;"
           title="{% if kpis.last_event and kpis.last_event.action %}{{ kpis.last_event.action }}{% endif %}">
        {% if kpis.last_event and kpis.last_event.action %}
          {{ kpis.last_event.action.replace('_', '_<wbr>') | safe }}
        {% else %}
          —
        {% endif %}
      </div>

      <div class="kpi-sub"
           style="white-space:normal; overflow:hidden; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical;"
           title="{% if kpis.last_event and kpis.last_event.actor_email %}{{ kpis.last_event.actor_email }}{% endif %}">
        {% if kpis.last_event and kpis.last_event.actor_email %}
          {{ kpis.last_event.actor_email }}
        {% else %}
          —
        {% endif %}
      </div>
    </div>

    <div class="kpi-card window">
      <div class="kpi-head">
        <div class="kpi-label">Login failures <span class="kpi-badge window" title="Respects selected time window">⏱</span></div>
        <span class="tip" tabindex="0" data-tip="Failed login attempts in the selected window (only increases if your auth code logs failures).">i</span>
      </div>
      <div class="kpi-value">{{ kpis.login_fail_window or 0 }}</div>
    </div>

    <div class="kpi-card window">
      <div class="kpi-head">
        <div class="kpi-label">Privileged actions <span class="kpi-badge window" title="Respects selected time window">⏱</span></div>
        <span class="tip" tabindex="0" data-tip="Sensitive admin actions in the selected window (user/role/password/settings).">i</span>
      </div>
      <div class="kpi-value">{{ kpis.privileged_window or 0 }}</div>
    </div>

    <div class="kpi-card window">
      <div class="kpi-head">
        <div class="kpi-label">Window <span class="kpi-badge window" title="Respects selected time window">⏱</span></div>
        <span class="tip" tabindex="0" data-tip="Quick sanity check: which window is currently applied.">i</span>
      </div>

      <div class="kpi-value small" style="white-space:nowrap;">
        {% if w == 'custom' and w_from and w_to %}
          <span class="badge code">{{ w_from }}</span> → <span class="badge code">{{ w_to }}</span>
        {% else %}
          <span class="badge code">{{ window_label(w) }}</span>
        {% endif %}
      </div>
      <div class="kpi-sub">All audit KPIs above follow this window.</div>
    </div>
  </div>

  <hr style="margin:16px 0; border:none; border-top:1px solid var(--border);">

  <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px; margin-top:12px;">
    <div class="kpi-card">
      <div class="kpi-head">
        <div class="kpi-label">Audit volume over time</div>
        <span class="tip" tabindex="0" data-tip="Total audit events per bucket (hour for ~2d windows, day for longer).">i</span>
      </div>
      <div style="height:260px; margin-top:10px;">
        <canvas id="chartAudit"></canvas>
      </div>
    </div>

    <div class="kpi-card">
      <div class="kpi-head">
        <div class="kpi-label">Signals</div>
        <span class="tip" tabindex="0" data-tip="Login failures and privileged actions per bucket in the selected window.">i</span>
      </div>
      <div style="height:260px; margin-top:10px;">
        <canvas id="chartSignals"></canvas>
      </div>
    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script>
  (function(){
    let chartAudit = null;
    let chartSignals = null;

    function buildCharts(data){
      const labels = data.labels || [];
      const s = (data.series || {});

      if (chartAudit) { chartAudit.destroy(); chartAudit = null; }
      if (chartSignals) { chartSignals.destroy(); chartSignals = null; }

      const ctxA = document.getElementById("chartAudit").getContext("2d");
      chartAudit = new Chart(ctxA, {
        type: "line",
        data: { labels, datasets: [{ label: "Audit events", data: s.audit_volume || [], tension: 0.25 }] },
        options: { responsive: true, maintainAspectRatio: false, interaction: { mode: "index", intersect: false } }
      });

      const ctxS = document.getElementById("chartSignals").getContext("2d");
      chartSignals = new Chart(ctxS, {
        type: "line",
        data: {
          labels,
          datasets: [
            { label: "Login failures", data: s.login_failures || [], tension: 0.25 },
            { label: "Privileged actions", data: s.privileged_actions || [], tension: 0.25 }
          ]
        },
        options: { responsive: true, maintainAspectRatio: false, interaction: { mode: "index", intersect: false } }
      });
    }

    const params = new URLSearchParams(window.location.search);

    if (params.get("w") === "custom") {
      const f = params.get("from") || "";
      const t = params.get("to") || "";
      if (!f || !t) {
        params.delete("from");
        params.delete("to");
      }
    }

    const qs = params.toString();
    const suffix = qs ? ("?" + qs) : "";

    const btnSeries = document.getElementById("btnExportSeries");
    if (btnSeries) btnSeries.href = "/admin/export/dashboard_series.csv" + suffix;

    const btnAudit = document.getElementById("btnExportAudit");
    if (btnAudit) btnAudit.href = "/admin/export/audit.csv" + suffix;

    fetch("/admin/api/dashboard/series?" + params.toString(), {
      credentials: "same-origin",
      cache: "no-store"
    })
      .then(r => r.json())
      .then(data => buildCharts(data))
      .catch(err => console.error("dashboard series fetch failed", err));
  })();
  </script>

  <div class="muted" style="margin-top:10px;">
    Tip: Provision users in <span class="badge code">Users</span>, verify changes in <span class="badge code">Audit</span>.
  </div>
</div>
"""