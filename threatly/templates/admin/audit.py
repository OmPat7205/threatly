ADMIN_AUDIT_TEMPLATE = r"""
{# --- Pretty formatting helpers --- #}
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

<div class="card">
  <div style="display:flex; align-items:flex-end; justify-content:space-between; gap:12px; flex-wrap:wrap;">
    <div>
      <div style="font-size:30px; font-weight:980; letter-spacing:-.4px;">Audit Log</div>
      <div class="muted">Scan events quickly. Expand details only when needed.</div>
    </div>
  </div>

  <form method="get" style="margin-top:14px; display:flex; gap:12px; flex-wrap:wrap; align-items:center;">
    <input name="q" value="{{ q }}" placeholder="Search actor, target, meta..."
           style="flex:1; min-width:260px; padding:10px 12px; border-radius:12px; border:1px solid rgba(255,255,255,.10); background: rgba(255,255,255,.03); color: var(--text); font-weight:850;">
    <input name="event" value="{{ event }}" placeholder="event (optional)"
           style="width:260px; max-width:100%; padding:10px 12px; border-radius:12px; border:1px solid rgba(255,255,255,.10); background: rgba(255,255,255,.03); color: var(--text); font-weight:850;">
    <button class="btn" type="submit">Filter</button>
    <a class="btn" href="/admin/audit">Clear</a>
  </form>

  {# ---- Active filters banner (chips) ---- #}
  {% set has_filters = (q or event or start_utc or end_utc or ok_raw) %}
  {% if has_filters %}
    <style>
      .filter-banner{
        margin-top:12px;
        padding:10px 12px;
        border-radius:14px;
        border:1px solid rgba(255,255,255,.08);
        background: rgba(255,255,255,.02);
        display:flex;
        align-items:center;
        justify-content:space-between;
        gap:10px;
        flex-wrap:wrap;
      }
      .filter-left{
        display:flex;
        gap:10px;
        align-items:center;
        flex-wrap:wrap;
        min-width:0;
      }
      .filter-title{
        font-weight:950;
        color: rgba(234,241,251,.82);
        letter-spacing:.2px;
        font-size:12px;
        text-transform: uppercase;
      }
      .chipx{
        display:inline-flex;
        align-items:center;
        gap:8px;
        padding:6px 10px;
        border-radius:999px;
        border:1px solid rgba(255,255,255,.10);
        background: rgba(255,255,255,.03);
        color: rgba(234,241,251,.92);
        font-weight:950;
        font-size:12px;
        max-width: 100%;
      }
      .chipx .txt{ max-width: 420px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
      .chipx a{
        text-decoration:none;
        display:inline-flex;
        align-items:center;
        justify-content:center;
        width:18px; height:18px;
        border-radius:999px;
        border:1px solid rgba(255,255,255,.10);
        background: rgba(0,0,0,.18);
        color: rgba(234,241,251,.85);
        font-weight:980;
        line-height:1;
      }
      .chipx a:hover{
        background: rgba(255,255,255,.05);
        border-color: rgba(255,255,255,.16);
      }
      .filter-actions{
        display:flex;
        gap:10px;
        align-items:center;
        flex-wrap:wrap;
      }
    </style>

    {% set base_q = q %}
    {% set base_event = event %}
    {% set base_start = start_utc %}
    {% set base_end = end_utc %}
    {% set base_ok = ok_raw %}

    <div class="filter-banner">
      <div class="filter-left">
        <span class="filter-title">Filtered to</span>

        {% if base_start or base_end %}
          <span class="chipx"
                title="{% if base_start and base_end %}{{ base_start }} → {{ base_end }}{% else %}{{ base_start or base_end }}{% endif %}">
            <span class="txt">
              {% if base_start and base_end %}
                {{ pretty_iso(base_start) }} → {{ pretty_iso(base_end) }}
              {% elif base_start %}
                from {{ pretty_iso(base_start) }}
              {% else %}
                to {{ pretty_iso(base_end) }}
              {% endif %}
            </span>
            <a href="/admin/audit?{% if base_q %}q={{ base_q|urlencode }}&{% endif %}{% if base_event %}event={{ base_event|urlencode }}&{% endif %}{% if base_ok %}ok={{ base_ok|urlencode }}&{% endif %}"
               title="Remove time filter">×</a>
          </span>
        {% endif %}

        {% if base_event %}
          <span class="chipx">
            <span class="txt">event: {{ base_event }}</span>
            <a href="/admin/audit?{% if base_q %}q={{ base_q|urlencode }}&{% endif %}{% if base_start %}start_utc={{ base_start|urlencode }}&{% endif %}{% if base_end %}end_utc={{ base_end|urlencode }}&{% endif %}{% if base_ok %}ok={{ base_ok|urlencode }}&{% endif %}"
               title="Remove event filter">×</a>
          </span>
        {% endif %}

        {% if base_ok %}
          <span class="chipx">
            <span class="txt">
              result:
              {% if base_ok in ('1','true','yes') %}ok{% elif base_ok in ('0','false','no') %}fail{% else %}{{ base_ok }}{% endif %}
            </span>
            <a href="/admin/audit?{% if base_q %}q={{ base_q|urlencode }}&{% endif %}{% if base_event %}event={{ base_event|urlencode }}&{% endif %}{% if base_start %}start_utc={{ base_start|urlencode }}&{% endif %}{% if base_end %}end_utc={{ base_end|urlencode }}&{% endif %}"
               title="Remove result filter">×</a>
          </span>
        {% endif %}

        {% if base_q %}
          <span class="chipx" title="{{ base_q }}">
            <span class="txt">search: {{ base_q }}</span>
            <a href="/admin/audit?{% if base_event %}event={{ base_event|urlencode }}&{% endif %}{% if base_start %}start_utc={{ base_start|urlencode }}&{% endif %}{% if base_end %}end_utc={{ base_end|urlencode }}&{% endif %}{% if base_ok %}ok={{ base_ok|urlencode }}&{% endif %}"
               title="Remove search">×</a>
          </span>
        {% endif %}
      </div>

      <div class="filter-actions">
        <a class="btn ghost" href="/admin/audit">Clear all</a>
      </div>
    </div>
  {% endif %}

  <style>
    /* --- Table-like audit log --- */
    .audit-table{
      margin-top:14px;
      border-radius: 14px;
      border:1px solid rgba(255,255,255,.06);
      overflow:hidden;
      background: rgba(255,255,255,.02);
      box-shadow: var(--shadow2);
    }

    .audit-thead, .audit-tr{
      display:grid;
      grid-template-columns: 200px minmax(260px, 1.3fr) 96px minmax(220px, 1fr) minmax(220px, 1fr) 44px;
      gap:14px;
      align-items:start;
      padding:12px 14px;
    }

    .audit-thead{
      background: rgba(255,255,255,.02);
      font-weight:950;
      color: rgba(234,241,251,.68);
      font-size:12px;
      letter-spacing:.2px;
      text-transform: uppercase;
      border-bottom:1px solid rgba(255,255,255,.06);
    }

    .audit-tr{
      padding:16px 14px;
      border-top:1px solid rgba(255,255,255,.06);
      background: rgba(0,0,0,.08);
    }
    .audit-tr:hover{ background: rgba(255,255,255,.03); }

    .cell{ min-width:0; }
    .clip{ overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
    .wrapany{ overflow-wrap:anywhere; word-break:break-word; }

    /* Make each cell stack cleanly */
    .cell .val{
      display:flex;
      flex-direction:column;
      gap:6px;
      min-width:0;
    }

    .mono{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      font-size:12px;
      color: rgba(234,241,251,.84);
    }
    .dim{ color: rgba(234,241,251,.60); }

    .badge{
      display:inline-flex; align-items:center; gap:8px;
      padding:6px 10px;
      border-radius:999px;
      border:1px solid rgba(255,255,255,.10);
      background: rgba(255,255,255,.03);
      font-weight:950;
      font-size:12px;
      color: rgba(234,241,251,.90);
      white-space:nowrap;
      max-width:100%;
    }

    /* Result badge: consistent + centered */
    .badge.ok, .badge.fail{
      padding:6px 10px;
      min-width:54px;
      justify-content:center;
    }
    .badge.ok{ border-color: rgba(71,227,183,.25); background: rgba(71,227,183,.08); }
    .badge.fail{ border-color: rgba(255,210,120,.22); background: rgba(255,255,255,.06); }

    .chip{
      display:inline-flex;
      align-items:center;
      justify-content:center;
      height:22px;
      padding:0 8px;
      border-radius:999px;
      border:1px solid rgba(255,255,255,.10);
      background: rgba(255,255,255,.03);
      color: rgba(234,241,251,.80);
      font-weight:900;
      font-size:12px;
      white-space:nowrap;
    }

    /* UA pill: smaller so it doesn't crush the Event column */
    .ua{
      display:inline-flex;
      align-items:center;
      gap:6px;
      padding:0 8px;
      height:20px;
      border-radius:999px;
      border:1px solid rgba(255,255,255,.10);
      background: rgba(255,255,255,.02);
      color: rgba(234,241,251,.72);
      font-weight:900;
      font-size:11px;
      cursor:help;
      user-select:none;
      max-width:200px;
    }
    .ua span{
      overflow:hidden; text-overflow:ellipsis; white-space:nowrap;
      display:inline-block;
      max-width:150px;
    }
    .ua:hover{ background: rgba(255,255,255,.04); border-color: rgba(255,255,255,.14); }

    /* Make the result column feel consistent */
    .audit-tr > .cell:nth-child(3){
      display:flex;
      align-items:flex-start;
      justify-content:flex-start;
    }

    /* Action button: smaller + calmer */
    .iconbtn{
      width:28px; height:28px;
      display:inline-flex; align-items:center; justify-content:center;
      border-radius:9px;
      border:1px solid rgba(255,255,255,.10);
      background: rgba(255,255,255,.03);
      cursor:pointer;
      user-select:none;
      color: rgba(234,241,251,.85);
      font-weight:950;
      opacity:.85;
    }
    .iconbtn:hover{ background: rgba(255,255,255,.05); border-color: rgba(255,255,255,.16); }

  /* ...keep your existing styles above... */

  /* ---- Meta overlay drawer (fixes the "vertical JSON" problem) ---- */
    details.audit-details{
      position: relative;
      display: inline-block; /* keep it anchored to the icon */
    }

    details.audit-details > summary{
      list-style:none;
      cursor:pointer;
      user-select:none;
      display:inline-flex;
      align-items:center;
      justify-content:center;
    }
    details.audit-details > summary::-webkit-details-marker{ display:none; }

    /* Overlay panel */
    .meta-box{
      position:absolute;
      right:0;
      top: calc(100% + 10px);
      width: min(720px, 92vw);
      max-height: 60vh;
      overflow:auto;

      padding:12px 14px;
      border-radius:14px;
      border:1px solid rgba(255,255,255,.10);
      background: rgba(10,10,12,.98);
      box-shadow: 0 24px 60px rgba(0,0,0,.65);
      z-index: 99999;
    }

    /* Make JSON readable */
    .meta-pre{
      margin:0;
      white-space: pre;          /* keep indentation */
      overflow-wrap: normal;     /* no character wrapping */
      word-break: normal;
      font-size:12px;
      line-height:1.35;
    }

    /* Optional: close hint row */
    .meta-hint{
      margin-top:10px;
      padding-top:10px;
      border-top:1px solid rgba(255,255,255,.08);
      color: rgba(234,241,251,.55);
      font-weight:800;
      font-size:12px;
    }



    /* Mobile fallback: stacked blocks with labels */
    @media (max-width: 980px){
      .audit-thead{ display:none; }
      .audit-tr{
        grid-template-columns: 1fr;
        gap:10px;
      }
      .audit-tr .cell{
        display:flex;
        align-items:center;
        justify-content:space-between;
        gap:10px;
      }
      .audit-tr .cell .label{
        font-weight:950;
        color: rgba(234,241,251,.70);
        font-size:12px;
        text-transform: uppercase;
        letter-spacing:.2px;
        flex: 0 0 auto;
      }
      .audit-tr .cell .val{
        flex: 1 1 auto;
        text-align:right;
        min-width:0;
      }
      .audit-tr .cell .val .clip, .audit-tr .cell .val .wrapany{
        text-align:right;
      }
      details.audit-details{ margin-top:8px; padding-top:10px; }
    }
  </style>

  <div class="audit-table">
    <div class="audit-thead">
      <div>Time (UTC)</div>
      <div>Event</div>
      <div>Result</div>
      <div>Actor</div>
      <div>Target</div>
      <div></div>
    </div>

    {% for e in events %}
      <div class="audit-tr">
        <!-- Time -->
        <div class="cell">
          <div class="val">
            <div class="mono clip" title="{{ e.ts_utc }}">{{ pretty_iso(e.ts_utc) }}</div>
            {% if e.ip %}
              <div class="dim mono clip" title="{{ e.ip }}">IP {{ e.ip }}</div>
            {% endif %}
          </div>
        </div>

        <!-- Event -->
        <div class="cell">
          <div class="val">
            <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap; min-width:0;">
              <span class="badge clip" title="{{ e.event }}">{{ e.event }}</span>
              {% if e.user_agent %}
                <span class="ua" title="{{ e.user_agent }}">🧭 <span class="clip">{{ e.user_agent }}</span></span>
              {% endif %}
              {% if e.meta and e.meta|length > 0 %}
                <span class="chip" title="Has meta JSON">meta {{ e.meta|length }}</span>
              {% endif %}
            </div>
          </div>
        </div>

        <!-- Result -->
        <div class="cell">
          {% if e.ok == 1 %}
            <span class="badge ok">ok</span>
          {% else %}
            <span class="badge fail">fail</span>
          {% endif %}
        </div>

        <!-- Actor -->
        <div class="cell">
          <div class="val">
            {% if e.actor_email %}
              <div class="mono clip" title="{{ e.actor_email }}">{{ e.actor_email }}</div>
            {% else %}
              <div class="dim">—</div>
            {% endif %}
            {% if e.actor_user_id %}
              <div class="dim mono clip" title="{{ e.actor_user_id }}">id {{ e.actor_user_id }}</div>
            {% endif %}
          </div>
        </div>

        <!-- Target -->
        <div class="cell">
          <div class="val">
            {% if e.target_type or e.target_id %}
              <div style="display:flex; align-items:center; gap:8px; min-width:0;">
                <span class="chip">{{ e.target_type or "target" }}</span>
                <span class="mono clip" title="{{ e.target_id }}">{{ e.target_id }}</span>
              </div>
            {% else %}
              <div class="dim">—</div>
            {% endif %}
          </div>
        </div>

        <!-- Actions -->
        <div class="cell" style="display:flex; justify-content:flex-end;">
          {% if e.meta and e.meta|length > 0 %}
            <details class="audit-details">
              <summary class="iconbtn" title="Expand details">⋯</summary>
              <div class="meta-box">
                <pre class="meta-pre mono">{{ e.meta | tojson(indent=2) }}</pre>
                <div class="meta-hint">Tip: click ⋯ again to close</div>
              </div>

            </details>
          {% else %}
            <span class="iconbtn" style="opacity:.35; cursor:default;" title="No details">⋯</span>
          {% endif %}
        </div>
      </div>
    {% endfor %}
  </div>

  {% if events|length == 0 %}
    <div class="muted" style="margin-top:16px;">No audit events found.</div>
  {% endif %}
</div>

<script>
  (function () {
    document.addEventListener("click", function (e) {
      const openDetails = document.querySelectorAll("details.audit-details[open]");
      openDetails.forEach((details) => {
        if (!details.contains(e.target)) {
          details.removeAttribute("open");
        }
      });
    });

    // Prevent clicks inside the meta panel from bubbling up
    document.addEventListener("click", function (e) {
      if (e.target.closest(".meta-box")) {
        e.stopPropagation();
      }
    }, true);
  })();
</script>

"""
