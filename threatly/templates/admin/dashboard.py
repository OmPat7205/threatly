ADMIN_DASHBOARD_TEMPLATE = r"""
<style>

    /* ---- Risk hierarchy + deltas ---- */
    .kpi-card.neutral{ opacity:.92; }
    .kpi-card.risk{
      border-width:1.5px;
      box-shadow: 0 12px 28px rgba(0,0,0,.34);
    }
    .kpi-card.level-normal{ border-color: rgba(34,197,94,.22); }
    .kpi-card.level-warn{ border-color: rgba(245,158,11,.55); box-shadow: 0 12px 30px rgba(245,158,11,.06); }
    .kpi-card.level-crit{ border-color: rgba(239,68,68,.70); box-shadow: 0 14px 34px rgba(239,68,68,.08); }

    .kpi-delta{
      margin-top:8px;
      font-size:12px;
      font-weight:850;
      color: rgba(250,250,250,.75);
      display:flex;
      gap:8px;
      align-items:center;
      flex-wrap:wrap;
    }
    .kpi-delta .up{ color: rgba(34,197,94,.95); }
    .kpi-delta .down{ color: rgba(239,68,68,.95); }
    .kpi-delta .flat{ color: rgba(250,250,250,.60); }

    .risk-banner{
      margin-top:12px;
      padding:12px 14px;
      border-radius:16px;
      border:1px solid rgba(255,255,255,.10);
      background: rgba(24,24,27,.26);
      display:flex;
      align-items:flex-start;
      justify-content:space-between;
      gap:12px;
      flex-wrap:wrap;
    }
    .risk-banner strong{ font-weight:950; }
    .risk-reasons{ color: rgba(250,250,250,.70); font-weight:800; font-size:12px; margin-top:6px; }
    .risk-reasons .badgeish{
      display:inline-flex; align-items:center; gap:6px;
      padding:4px 8px; border-radius:999px;
      border:1px solid rgba(255,255,255,.10);
      background: rgba(255,255,255,.03);
      margin-right:6px;
      margin-top:6px;
    }

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

  /* ---- Charts -> action (click + callouts) ---- */
  .chart-wrap{
    position:relative;
  }
  .chart-hint{
    margin-top:10px;
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:10px;
    flex-wrap:wrap;
  }
  .chart-hint .muted2{
    font-weight:850;
    font-size:12px;
  }
  .chart-callouts{
    margin-top:10px;
    display:flex;
    gap:8px;
    flex-wrap:wrap;
    align-items:center;
  }
  .callout{
    display:inline-flex;
    align-items:center;
    gap:8px;
    padding:6px 10px;
    border-radius:999px;
    border:1px solid rgba(255,255,255,.10);
    background: rgba(255,255,255,.03);
    cursor:pointer;
    user-select:none;
  }
  .callout:hover{ background: rgba(255,255,255,.05); border-color: rgba(255,255,255,.14); }
  .callout .ts{ font-weight:950; font-size:12px; color: rgba(250,250,250,.92); }
  .callout .desc{ font-weight:850; font-size:12px; color: rgba(250,250,250,.70); }
  .callout .badge{
    display:inline-flex;
    align-items:center;
    justify-content:center;
    min-width:22px;
    height:18px;
    padding:0 7px;
    border-radius:999px;
    border:1px solid rgba(255,255,255,.12);
    background: rgba(255,255,255,.04);
    font-weight:950;
    font-size:12px;
    color: rgba(250,250,250,.92);
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

  {# ---- risk summary ---- #}
  {% set overall = (kpis.overall_status if kpis and kpis.overall_status else None) %}
  {% if overall %}
    <div class="risk-banner">
      <div style="min-width:0;">
        <div style="font-size:14px; font-weight:950;">
          {{ overall.icon }} <strong>{{ overall.label }}</strong>
        </div>
        {% if overall.reasons and overall.reasons|length > 0 %}
          <div class="risk-reasons">
            {% for r in overall.reasons %}
              <span class="badgeish">
                {% if r.level == 'crit' %}🚨{% elif r.level == 'warn' %}⚠️{% else %}✅{% endif %}
                {{ r.label }}
              </span>
            {% endfor %}
          </div>
        {% else %}
          <div class="risk-reasons">No elevated risk signals detected in this window.</div>
        {% endif %}
      </div>
      <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
        <a class="btn ghost" href="/admin/audit?start_utc={{ w_start }}&end_utc={{ w_end }}">View audit for window</a>
      </div>
    </div>
  {% endif %}

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

    {% set m_audit = (kpis.window_metrics.audit_window if kpis.window_metrics else None) %}
    <div class="kpi-card window {{ m_audit.kind if m_audit else '' }} level-{{ m_audit.level if m_audit else 'neutral' }}">
      {% if m_audit %}
        <div class="kpi-delta">
          {% if m_audit.trend == 'up' %}
            <span class="up">↑ {{ '%.1f' % m_audit.delta_pct }}% vs prev</span>
          {% elif m_audit.trend == 'down' %}
            <span class="down">↓ {{ '%.1f' % m_audit.delta_pct }}% vs prev</span>
          {% else %}
            <span class="flat">— vs prev</span>
          {% endif %}
          <span class="muted2">{{ m_audit.hint }}</span>
        </div>
      {% endif %}

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
        <span class="tip" tabindex="0" data-tip="Failed login attempts in the selected window (action=login_attempt with ok=false in details).">i</span>
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
        <span class="tip" tabindex="0" data-tip="Hover for values. Click a point to open the audit log filtered to that bucket.">i</span>
      </div>
      <div class="chart-wrap" style="height:260px; margin-top:10px;">
        <canvas id="chartAudit"></canvas>
      </div>
      <div class="chart-hint">
        <div class="muted2">Hover → details · Click → open audit for that time bucket</div>
        <a class="btn ghost" id="btnAuditDrill" href="#">Open full window</a>
      </div>
      <div id="calloutsAudit" class="chart-callouts"></div>
    </div>

    <div class="kpi-card">
      <div class="kpi-head">
        <div class="kpi-label">Signals</div>
        <span class="tip" tabindex="0" data-tip="Hover for values. Click a point to jump into the audit log for that bucket. Spikes are auto-flagged.">i</span>
      </div>
      <div class="chart-wrap" style="height:260px; margin-top:10px;">
        <canvas id="chartSignals"></canvas>
      </div>
      <div class="chart-hint">
        <div class="muted2">Click points to investigate · Spikes generate quick-callouts below</div>
        <a class="btn ghost" id="btnSignalsDrill" href="#">Open full window</a>
      </div>
      <div id="calloutsSignals" class="chart-callouts"></div>
    </div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <script>
  (function(){
    let chartAudit = null;
    let chartSignals = null;

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

    // "Open full window" buttons (respect selected window)
    const btnAuditDrill = document.getElementById("btnAuditDrill");
    const btnSignalsDrill = document.getElementById("btnSignalsDrill");
    if (btnAuditDrill) btnAuditDrill.href = "/admin/audit" + suffix;
    if (btnSignalsDrill) btnSignalsDrill.href = "/admin/audit" + suffix;

    function isHourLabel(lbl){
      return (lbl || "").length > 10; // "YYYY-MM-DD HH:00"
    }
    function bucketToIso(lbl, which){
      // returns ISO Z timestamps for start/end of bucket
      // hour: YYYY-MM-DD HH:00
      // day: YYYY-MM-DD
      const s = (lbl || "").trim();
      if (!s) return "";

      if (isHourLabel(s)){
        const y = s.slice(0,4), m = s.slice(5,7), d = s.slice(8,10);
        const hh = s.slice(11,13);
        if (which === "start") return `${y}-${m}-${d}T${hh}:00:00Z`;
        return `${y}-${m}-${d}T${hh}:59:59Z`;
      } else {
        // day bucket
        if (which === "start") return `${s}T00:00:00Z`;
        return `${s}T23:59:59Z`;
      }
    }

    function openAuditForBucket(lbl, opts){
      opts = opts || {};
      const start = bucketToIso(lbl, "start");
      const end = bucketToIso(lbl, "end");
      const u = new URL(window.location.origin + "/admin/audit");
      if (start) u.searchParams.set("start_utc", start);
      if (end) u.searchParams.set("end_utc", end);
      // optionally constrain to an action
      if (opts.event) u.searchParams.set("event", opts.event);
      window.location.href = u.toString();
    }

    function stats(arr){
      const xs = (arr || []).map(v => Number(v||0)).filter(v => Number.isFinite(v));
      if (!xs.length) return {mean:0, std:0, max:0};
      let sum = 0;
      for (const v of xs) sum += v;
      const mean = sum / xs.length;
      let varsum = 0;
      for (const v of xs) varsum += (v - mean) * (v - mean);
      const std = Math.sqrt(varsum / xs.length);
      let max = 0;
      for (const v of xs) if (v > max) max = v;
      return {mean, std, max};
    }

    function spikeMask(arr){
      // flags: value >= max(3, mean + 2*std) OR > previous*2 and >= 3
      const xs = (arr || []).map(v => Number(v||0));
      const st = stats(xs);
      const hard = Math.max(3, st.mean + 2*st.std);
      const out = xs.map((v, i) => {
        const prev = (i > 0 ? xs[i-1] : 0);
        const spike2x = (prev > 0 && v >= (prev * 2) && v >= 3);
        return (v >= hard) || spike2x;
      });
      return {mask: out, threshold: hard};
    }

    function topSpikes(labels, arr, mask, limit){
      const xs = (arr || []).map(v => Number(v||0));
      const items = [];
      for (let i=0; i<labels.length; i++){
        if (!mask[i]) continue;
        items.push({i, label: labels[i], v: xs[i]});
      }
      items.sort((a,b) => (b.v - a.v));
      return items.slice(0, limit || 3);
    }

    function renderCallouts(elId, items, opts){
      opts = opts || {};
      const el = document.getElementById(elId);
      if (!el) return;
      el.innerHTML = "";

      if (!items || !items.length) {
        // keep it subtle: show nothing if no spikes
        return;
      }

      for (const it of items){
        const d = document.createElement("div");
        d.className = "callout";
        d.title = "Click to open audit log for this bucket";
        d.addEventListener("click", () => openAuditForBucket(it.label, opts));

        const ts = document.createElement("span");
        ts.className = "ts";
        ts.textContent = it.label;

        const badge = document.createElement("span");
        badge.className = "badge";
        badge.textContent = String(it.v);

        const desc = document.createElement("span");
        desc.className = "desc";
        desc.textContent = opts.desc || "spike";

        d.appendChild(ts);
        d.appendChild(badge);
        d.appendChild(desc);
        el.appendChild(d);
      }
    }

    // Plugin: draw small "alert dots" on spike points
    const SpikeDotsPlugin = {
      id: "spikeDots",
      afterDatasetsDraw(chart, args, pluginOptions){
        const meta = chart.getDatasetMeta(0);
        if (!meta || !meta.data) return;

        const spikes = (pluginOptions && pluginOptions.spikes) || [];
        if (!spikes.length) return;

        const ctx = chart.ctx;
        ctx.save();
        for (let i=0; i<meta.data.length; i++){
          if (!spikes[i]) continue;
          const pt = meta.data[i];
          if (!pt) continue;
          const x = pt.x, y = pt.y;
          // draw a small ring (no hard-coded colors elsewhere; this is minimal)
          ctx.beginPath();
          ctx.arc(x, y, 6, 0, Math.PI*2);
          ctx.lineWidth = 2;
          ctx.strokeStyle = "rgba(239,68,68,.85)";
          ctx.stroke();

          ctx.beginPath();
          ctx.arc(x, y, 2.8, 0, Math.PI*2);
          ctx.fillStyle = "rgba(239,68,68,.85)";
          ctx.fill();
        }
        ctx.restore();
      }
    };

    function buildCharts(data){
      const labels = data.labels || [];
      const s = (data.series || {});
      const audit = (s.audit_volume || []);
      const login = (s.login_failures || []);
      const priv = (s.privileged_actions || []);

      const auditSpike = spikeMask(audit);
      const loginSpike = spikeMask(login);
      const privSpike = spikeMask(priv);

      // Callouts (top spikes only)
      renderCallouts("calloutsAudit", topSpikes(labels, audit, auditSpike.mask, 3), { desc: "audit spike" });
      // Signals: prioritize login spikes, then privileged spikes
      const sigItems = []
        .concat(topSpikes(labels, login, loginSpike.mask, 3).map(x => ({...x, kind:"login"})))
        .concat(topSpikes(labels, priv, privSpike.mask, 3).map(x => ({...x, kind:"priv"})));
      sigItems.sort((a,b) => (b.v - a.v));
      renderCallouts("calloutsSignals", sigItems.slice(0, 4).map(x => {
        return { i:x.i, label:x.label, v:x.v };
      }), { desc: "signal spike" });

      if (chartAudit) { chartAudit.destroy(); chartAudit = null; }
      if (chartSignals) { chartSignals.destroy(); chartSignals = null; }

      const ctxA = document.getElementById("chartAudit").getContext("2d");
      chartAudit = new Chart(ctxA, {
        type: "line",
        data: {
          labels,
          datasets: [{
            label: "Audit events",
            data: audit,
            tension: 0.25,
            pointRadius: 3,
            pointHoverRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: { mode: "index", intersect: false },
          plugins: {
            tooltip: {
              callbacks: {
                afterBody: function(){
                  return ["Click to view events for this bucket"];
                }
              }
            }
          },
          onHover: (evt, activeEls) => {
            const canvas = evt?.native?.target;
            if (!canvas) return;
            canvas.style.cursor = activeEls && activeEls.length ? "pointer" : "default";
          },
          onClick: (evt, activeEls) => {
            if (!activeEls || !activeEls.length) return;
            const idx = activeEls[0].index;
            const lbl = labels[idx];
            openAuditForBucket(lbl, {});
          }
        },
        plugins: [SpikeDotsPlugin],
        pluginOptions: { spikeDots: { spikes: auditSpike.mask } }
      });

      // Chart.js doesn't pass pluginOptions like that; set on chart instance for our plugin:
      chartAudit.options.plugins.spikeDots = { spikes: auditSpike.mask };

      const ctxS = document.getElementById("chartSignals").getContext("2d");
      chartSignals = new Chart(ctxS, {
        type: "line",
        data: {
          labels,
          datasets: [
            { label: "Login failures", data: login, tension: 0.25, pointRadius: 3, pointHoverRadius: 6 },
            { label: "Privileged actions", data: priv, tension: 0.25, pointRadius: 3, pointHoverRadius: 6 }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: { mode: "index", intersect: false },
          plugins: {
            tooltip: {
              callbacks: {
                afterBody: function(ctx){
                  // ctx = array of tooltip items (one per dataset)
                  const lines = ["Click to view events for this bucket"];
                  // helpful hint if login failures are present
                  const hasLogin = ctx && ctx.length ? (ctx[0].label && true) : false;
                  if (hasLogin) lines.push("Tip: filter action=login_attempt to inspect auth activity");
                  return lines;
                }
              }
            }
          },
          onHover: (evt, activeEls) => {
            const canvas = evt?.native?.target;
            if (!canvas) return;
            canvas.style.cursor = activeEls && activeEls.length ? "pointer" : "default";
          },
          onClick: (evt, activeEls) => {
            if (!activeEls || !activeEls.length) return;
            const idx = activeEls[0].index;
            const dsIndex = activeEls[0].datasetIndex;
            const lbl = labels[idx];

            // If they click the login series, jump with event filter (action name).
            if (dsIndex === 0) {
              openAuditForBucket(lbl, { event: "login_attempt" });
            } else {
              openAuditForBucket(lbl, {});
            }
          }
        }
      });

      // draw spike dots on both datasets by layering two plugin instances (simple + robust)
      chartSignals.config.plugins = chartSignals.config.plugins || [];
      chartSignals.config.plugins.push({
        id: "spikeDotsSignals",
        afterDatasetsDraw(chart){
          const ctx = chart.ctx;
          const ds0 = chart.getDatasetMeta(0);
          const ds1 = chart.getDatasetMeta(1);
          const s0 = loginSpike.mask || [];
          const s1 = privSpike.mask || [];
          ctx.save();

          function draw(meta, spikes, color){
            if (!meta || !meta.data) return;
            for (let i=0; i<meta.data.length; i++){
              if (!spikes[i]) continue;
              const pt = meta.data[i];
              if (!pt) continue;
              ctx.beginPath();
              ctx.arc(pt.x, pt.y, 6, 0, Math.PI*2);
              ctx.lineWidth = 2;
              ctx.strokeStyle = color;
              ctx.stroke();
              ctx.beginPath();
              ctx.arc(pt.x, pt.y, 2.8, 0, Math.PI*2);
              ctx.fillStyle = color;
              ctx.fill();
            }
          }

          draw(ds0, s0, "rgba(239,68,68,.85)"); // login spikes
          draw(ds1, s1, "rgba(245,158,11,.85)"); // privileged spikes

          ctx.restore();
        }
      });
      chartSignals.update();
    }

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
