ADMIN_AUDIT_TEMPLATE = r"""
<div class="card">
  <div style="display:flex; align-items:flex-end; justify-content:space-between; gap:12px; flex-wrap:wrap;">
    <div>
      <div style="font-size:30px; font-weight:980; letter-spacing:-.4px;">Audit log</div>
      <div class="muted">Search and review admin/security events. Expand meta only when needed.</div>
    </div>
  </div>

  <form method="get" style="margin-top:14px; display:flex; gap:12px; flex-wrap:wrap; align-items:center;">
    <input name="q" value="{{ q }}" placeholder="Search actor, target, meta..."
           style="flex:1; min-width:280px; padding:10px 12px; border-radius:12px; border:1px solid rgba(255,255,255,.10); background: rgba(255,255,255,.03); color: var(--text); font-weight:850;">
    <input name="event" value="{{ event }}" placeholder="event (optional)"
           style="width:280px; max-width:100%; padding:10px 12px; border-radius:12px; border:1px solid rgba(255,255,255,.10); background: rgba(255,255,255,.03); color: var(--text); font-weight:850;">
    <button class="btn" type="submit">Filter</button>
    <a class="btn" href="/admin/audit">Clear</a>
  </form>

  <style>
    .audit-head{
      margin-top:14px;
      display:grid;
      grid-template-columns: 190px 1.1fr 90px 1fr 1fr;
      gap:10px;
      padding:10px 12px;
      border-radius: 12px;
      border:1px solid rgba(255,255,255,.06);
      background: rgba(255,255,255,.02);
      font-weight:950;
      color: rgba(234,241,251,.70);
      font-size:12px;
      letter-spacing:.2px;
      text-transform: uppercase;
    }
    @media (max-width: 980px){
      .audit-head{ display:none; }
    }

    .audit-row{
      margin-top:10px;
      display:grid;
      grid-template-columns: 190px 1.1fr 90px 1fr 1fr;
      gap:10px;
      padding:12px;
      border-radius: 14px;
      border:1px solid rgba(255,255,255,.06);
      background: rgba(255,255,255,.02);
      box-shadow: var(--shadow2);
      align-items:start;
    }
    @media (max-width: 980px){
      .audit-row{
        grid-template-columns: 1fr;
      }
    }

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
    }
    .badge.ok{ border-color: rgba(71,227,183,.25); background: rgba(71,227,183,.08); }
    .badge.fail{ border-color: rgba(255,210,120,.25); background: rgba(255,210,120,.08); }

    .mono{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      font-size:12px;
      color: rgba(234,241,251,.80);
    }
    .dim{ color: rgba(234,241,251,.62); }
    .cell-title{
      font-weight:980;
      margin-bottom:6px;
      color: rgba(234,241,251,.92);
    }
    .cell{
      min-width: 0;
    }
    .clip{
      overflow:hidden;
      text-overflow:ellipsis;
      white-space:nowrap;
    }
    .wrapany{
      overflow-wrap:anywhere;
      word-break:break-word;
    }
    details.audit-details{
      margin-top:10px;
      border-top:1px solid rgba(255,255,255,.06);
      padding-top:10px;
    }
    details.audit-details > summary{
      list-style:none;
      cursor:pointer;
      user-select:none;
      display:inline-flex;
      align-items:center;
      gap:10px;
      font-weight:950;
      color: rgba(234,241,251,.85);
    }
    details.audit-details > summary::-webkit-details-marker{ display:none; }
    .meta-box{
      margin-top:10px;
      padding:10px 12px;
      border-radius:12px;
      border:1px solid rgba(255,255,255,.06);
      background: rgba(0,0,0,.22);
    }
  </style>

  <div class="audit-head">
    <div>Time (UTC)</div>
    <div>Event</div>
    <div>Result</div>
    <div>Actor</div>
    <div>Target</div>
  </div>

  {% for e in events %}
    <div class="audit-row">
      <div class="cell">
        <div class="cell-title">Time</div>
        <div class="mono wrapany">{{ e.ts_utc }}</div>
        {% if e.ip %}
          <div class="dim" style="margin-top:6px;">IP <span class="mono">{{ e.ip }}</span></div>
        {% endif %}
      </div>

      <div class="cell">
        <div class="cell-title">Event</div>
        <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
          <span class="badge">{{ e.event }}</span>
          {% if e.user_agent %}
            <span class="dim mono clip" title="{{ e.user_agent }}" style="max-width:420px;">{{ e.user_agent }}</span>
          {% endif %}
        </div>

        {% if e.meta and e.meta|length > 0 %}
          <details class="audit-details">
            <summary>View meta JSON <span class="dim mono">({{ e.meta|length }} keys)</span></summary>
            <div class="meta-box mono wrapany">{{ e.meta | tojson(indent=2) }}</div>
          </details>
        {% endif %}
      </div>

      <div class="cell">
        <div class="cell-title">Result</div>
        {% if e.ok == 1 %}
          <span class="badge ok">ok</span>
        {% else %}
          <span class="badge fail">fail</span>
        {% endif %}
      </div>

      <div class="cell">
        <div class="cell-title">Actor</div>
        {% if e.actor_email %}
          <div class="wrapany"><span class="badge">actor</span> <span class="mono">{{ e.actor_email }}</span></div>
        {% else %}
          <div class="dim">—</div>
        {% endif %}
        {% if e.actor_user_id %}
          <div class="dim" style="margin-top:6px;">id <span class="mono wrapany">{{ e.actor_user_id }}</span></div>
        {% endif %}
      </div>

      <div class="cell">
        <div class="cell-title">Target</div>
        {% if e.target_type or e.target_id %}
          <div class="wrapany"><span class="badge">{{ e.target_type or "target" }}</span> <span class="mono">{{ e.target_id }}</span></div>
        {% else %}
          <div class="dim">—</div>
        {% endif %}
      </div>
    </div>
  {% endfor %}

  {% if events|length == 0 %}
    <div class="muted" style="margin-top:16px;">No audit events found.</div>
  {% endif %}
</div>
"""