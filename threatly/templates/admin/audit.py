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

{# --- relative time helper (best-effort) --- #}
{% macro rel_time(s) -%}
  {%- set x = (s or '') -%}
  {%- if x|length >= 19 -%}
    {%- set yyyy = x[0:4]|int -%}
    {%- set mm = x[5:7]|int -%}
    {%- set dd = x[8:10]|int -%}
    {%- set hh = x[11:13]|int -%}
    {%- set mi = x[14:16]|int -%}
    {%- set ss = (x[17:19]|int if x|length >= 19 else 0) -%}
    {%- set now_ts = (now_ts_utc or 0)|int -%}
    {# JS will overwrite these labels anyway; keep server-safe fallback #}
    {{ pretty_iso(x) }}
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

    <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
      <button class="btn ghost" type="button" id="auditCompactBtn" title="Toggle compact rows">Compact</button>
      <button class="btn ghost" type="button" id="auditTimeBtn" title="Toggle time display">Time: Absolute</button>
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
      overflow:auto; /* enables sticky header inside */
      background: rgba(255,255,255,.02);
      box-shadow: var(--shadow2);
      max-height: 70vh;
    }

    /* Sticky header */
    .audit-thead{
      position: sticky;
      top: 0;
      z-index: 10;
      backdrop-filter: blur(10px);
    }

    .audit-thead, .audit-tr{
      display:grid;
      grid-template-columns: 200px minmax(260px, 1.3fr) 96px minmax(220px, 1fr) minmax(220px, 1fr) 44px;
      gap:14px;
      align-items:start;
      padding:12px 14px;
    }

    .audit-thead{
      background: rgba(14,14,18,.92);
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

    /* Zebra striping */
    .audit-tr:nth-child(odd){ background: rgba(0,0,0,.06); }
    .audit-tr:nth-child(even){ background: rgba(26,31,38,.18); }
    .audit-tr:hover{ background: rgba(255,255,255,.04); }

    /* Compact mode */
    .audit-table.compact .audit-tr{ padding:10px 14px; }
    .audit-table.compact .audit-thead{ padding:10px 14px; }
    .audit-table.compact .cell .val{ gap:4px; }
    .audit-table.compact .badge{ padding:5px 9px; }
    .audit-table.compact .chip{ height:20px; }
    .audit-table.compact .iconbtn{ width:26px; height:26px; }

    .cell{ min-width:0; }
    .clip{ overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
    .wrapany{ overflow-wrap:anywhere; word-break:break-word; }

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

    /* Result badge: higher contrast */
    .badge.ok, .badge.fail{
      padding:6px 10px;
      min-width:54px;
      justify-content:center;
    }
    .badge.ok{
      border-color: rgba(0,255,160,.28);
      background: rgba(0,120,70,.28);
      color: rgba(90,255,190,.95);
    }
    .badge.fail{
      border-color: rgba(255,70,70,.30);
      background: rgba(120,0,0,.30);
      color: rgba(255,140,140,.98);
    }

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
      cursor: default;
    }

    /* Click-to-filter on event badge */
    .badge.ev{
      cursor:pointer;
      user-select:none;
    }
    .badge.ev:hover{
      background: rgba(255,255,255,.06);
      border-color: rgba(255,255,255,.16);
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

    .audit-tr > .cell:nth-child(3){
      display:flex;
      align-items:flex-start;
      justify-content:flex-start;
    }

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
      opacity:.9;
    }
    .iconbtn:hover{ background: rgba(255,255,255,.06); border-color: rgba(255,255,255,.18); }

    /* ---- Meta overlay drawer ---- */
    details.audit-details{
      position: relative;
      display: inline-block;
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

    .meta-pre{
      margin:0;
      white-space: pre;
      overflow-wrap: normal;
      word-break: normal;
      font-size:12px;
      line-height:1.35;
    }

    .meta-hint{
      margin-top:10px;
      padding-top:10px;
      border-top:1px solid rgba(255,255,255,.08);
      color: rgba(234,241,251,.55);
      font-weight:800;
      font-size:12px;
    }

    /* Copy-to-clipboard icon */
    .copybtn{
      display:inline-flex;
      align-items:center;
      justify-content:center;
      width:18px; height:18px;
      border-radius:8px;
      border:1px solid rgba(255,255,255,.10);
      background: rgba(255,255,255,.03);
      color: rgba(234,241,251,.80);
      font-size:11px;
      font-weight:950;
      opacity:0;
      transform: translateY(-1px);
      cursor:pointer;
    }
    .copywrap:hover .copybtn{ opacity:.95; }
    .copybtn:hover{ background: rgba(255,255,255,.06); border-color: rgba(255,255,255,.18); }

    /* Truncation strategy for long emails/ids */
    .truncate{
      max-width: 240px;
      overflow:hidden;
      text-overflow:ellipsis;
      white-space:nowrap;
      display:inline-block;
      vertical-align:bottom;
    }

    @media (max-width: 980px){
      .audit-thead{ display:none; }
      .audit-table{ max-height: none; overflow: visible; }
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
    }
  </style>

  <div class="audit-table" id="auditTable">
    <div class="audit-thead">
      <div>Time</div>
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
            <div class="mono clip"
                 data-ts="{{ e.ts_utc }}"
                 data-time="abs"
                 title="{{ e.ts_utc }}">
              {{ pretty_iso(e.ts_utc) }}
            </div>
            {% if e.ip %}
              <div class="dim mono clip copywrap" title="{{ e.ip }}">
                <span class="mono">IP <span class="copyval">{{ e.ip }}</span></span>
                <span class="copybtn" data-copy="{{ e.ip }}" title="Copy IP">⧉</span>
              </div>
            {% endif %}
          </div>
        </div>

        <!-- Event -->
        <div class="cell">
          <div class="val">
            <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap; min-width:0;">
              <span class="badge ev clip"
                    data-event="{{ e.event }}"
                    title="Click to filter by this event">{{ e.event }}</span>
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
              <div class="mono clip copywrap" title="{{ e.actor_email }}">
                <span class="truncate copyval">{{ e.actor_email }}</span>
                <span class="copybtn" data-copy="{{ e.actor_email }}" title="Copy email">⧉</span>
              </div>
            {% else %}
              <div class="dim">—</div>
            {% endif %}
            {% if e.actor_user_id %}
              <div class="dim mono clip copywrap" title="{{ e.actor_user_id }}">
                id <span class="copyval">{{ e.actor_user_id }}</span>
                <span class="copybtn" data-copy="{{ e.actor_user_id }}" title="Copy user id">⧉</span>
              </div>
            {% endif %}
          </div>
        </div>

        <!-- Target -->
        <div class="cell">
          <div class="val">
            {% if e.target_type or e.target_id %}
              <div style="display:flex; align-items:center; gap:8px; min-width:0;">
                <span class="chip">{{ e.target_type or "target" }}</span>
                <span class="mono clip copywrap" title="{{ e.target_id }}">
                  <span class="truncate copyval">{{ e.target_id }}</span>
                  <span class="copybtn" data-copy="{{ e.target_id }}" title="Copy target id">⧉</span>
                </span>
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
                <div class="meta-hint">Tip: click anywhere outside to close</div>
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
    // ---- Close meta drawers when clicking outside ----
    document.addEventListener("click", function (e) {
      document.querySelectorAll("details.audit-details[open]").forEach((d) => {
        if (!d.contains(e.target)) d.removeAttribute("open");
      });
    }, false);

    // prevent inside clicks from bubbling to the document handler
    document.addEventListener("click", function (e) {
      if (e.target.closest(".meta-box")) e.stopPropagation();
    }, true);

    // ---- Copy-to-clipboard ----
    function copyText(t) {
      if (!t) return;
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(t).catch(function(){});
      } else {
        // fallback
        const ta = document.createElement("textarea");
        ta.value = t;
        ta.style.position = "fixed";
        ta.style.left = "-9999px";
        document.body.appendChild(ta);
        ta.select();
        try { document.execCommand("copy"); } catch (e) {}
        document.body.removeChild(ta);
      }
    }
    document.addEventListener("click", function (e) {
      const btn = e.target.closest(".copybtn");
      if (!btn) return;
      e.preventDefault();
      e.stopPropagation();
      copyText(btn.getAttribute("data-copy") || "");
    }, true);

    // ---- Compact mode toggle ----
    const table = document.getElementById("auditTable");
    const compactBtn = document.getElementById("auditCompactBtn");
    const timeBtn = document.getElementById("auditTimeBtn");

    function setCompact(on) {
      if (!table) return;
      if (on) table.classList.add("compact");
      else table.classList.remove("compact");
      try { localStorage.setItem("audit_compact", on ? "1" : "0"); } catch (e) {}
    }

    const savedCompact = (function(){
      try { return localStorage.getItem("audit_compact"); } catch (e) { return null; }
    })();
    if (savedCompact === "1") setCompact(true);

    if (compactBtn) {
      compactBtn.addEventListener("click", function () {
        const on = !table.classList.contains("compact");
        setCompact(on);
      });
    }

    // ---- Time toggle (absolute vs relative) ----
    function parseIsoToMs(iso) {
      if (!iso) return null;
      // Accept "YYYY-MM-DDTHH:MM:SSZ" or without Z; normalize to Z for UTC
      let s = iso.trim();
      if (s.length >= 19 && s.indexOf("T") === -1) return null;
      if (s.endsWith("Z")) {
        const ms = Date.parse(s);
        return isNaN(ms) ? null : ms;
      }
      // If no timezone, assume UTC (append Z)
      if (s.length >= 19 && (s.indexOf("+") === -1 && s.indexOf("Z") === -1)) s = s + "Z";
      const ms = Date.parse(s);
      return isNaN(ms) ? null : ms;
    }

    function relLabel(ms) {
      const now = Date.now();
      let d = Math.floor((now - ms) / 1000);
      if (d < 0) d = 0;
      if (d < 60) return d + "s ago";
      const m = Math.floor(d / 60);
      if (m < 60) return m + "m ago";
      const h = Math.floor(m / 60);
      if (h < 48) return h + "h ago";
      const days = Math.floor(h / 24);
      return days + "d ago";
    }

    function setTimeMode(mode) {
      const nodes = document.querySelectorAll('[data-ts]');
      nodes.forEach((n) => {
        const iso = n.getAttribute("data-ts") || "";
        if (mode === "rel") {
          const ms = parseIsoToMs(iso);
          if (ms) n.textContent = relLabel(ms);
          n.setAttribute("data-time", "rel");
        } else {
          // restore from title-ish: easiest is to re-render from iso with a simple absolute fallback
          // Keep what server rendered in a data-abs attribute (first time)
          if (!n.getAttribute("data-abs")) n.setAttribute("data-abs", n.textContent);
          n.textContent = n.getAttribute("data-abs") || iso;
          n.setAttribute("data-time", "abs");
        }
      });
      try { localStorage.setItem("audit_time_mode", mode); } catch (e) {}
      if (timeBtn) timeBtn.textContent = "Time: " + (mode === "rel" ? "Relative" : "Absolute");
    }

    const savedTime = (function(){
      try { return localStorage.getItem("audit_time_mode"); } catch (e) { return null; }
    })();
    setTimeMode(savedTime === "rel" ? "rel" : "abs");

    if (timeBtn) {
      timeBtn.addEventListener("click", function () {
        const cur = timeBtn.textContent.indexOf("Relative") !== -1 ? "rel" : "abs";
        setTimeMode(cur === "rel" ? "abs" : "rel");
      });
    }

    // ---- Click-to-filter on Event badge ----
    function qs(params) {
      const out = [];
      for (const k in params) {
        if (params[k] === null || params[k] === undefined) continue;
        const v = String(params[k]);
        if (!v) continue;
        out.push(encodeURIComponent(k) + "=" + encodeURIComponent(v));
      }
      return out.join("&");
    }

    document.addEventListener("click", function (e) {
      const badge = e.target.closest(".badge.ev");
      if (!badge) return;
      const ev = badge.getAttribute("data-event") || "";
      if (!ev) return;

      // Preserve existing query params but set/override "event"
      const u = new URL(window.location.href);
      u.searchParams.set("event", ev);
      u.searchParams.delete("offset"); // reset paging when filtering
      window.location.href = u.toString();
    }, false);
  })();
</script>
"""
