HEALTH_TEMPLATE = r"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Threatly • Health</title>

  <style>
    :root{
      /* Admin-aligned enterprise palette (zinc/slate) */
      --bg0:#09090b;
      --bg1:#0b0b0f;
      --panel:#18181b;

      --border:#27272a;
      --text:#fafafa;
      --muted:#a1a1aa;

      --accent:#22c55e;
      --ok:#22c55e;
      --warn:#f59e0b;
      --bad:#ef4444;

      --shadow: 0 18px 50px rgba(0,0,0,.55);

      /* Admin-like tight radius + density */
      --radius: 6px;
      --radiusSm: 4px;
      --fs: 14px;
      --fsSmall: 12px;
    }

    *{ box-sizing:border-box; }
    html,body{ height:100%; }

    body{
      margin:0;
      padding:22px 18px 60px;
      font-family: Inter, -apple-system, BlinkMacSystemFont, system-ui, Segoe UI, Roboto, Arial, sans-serif;
      font-size: var(--fs);
      color:var(--text);
      background:
        radial-gradient(900px 600px at 20% -10%, rgba(34,197,94,.10), transparent 60%),
        radial-gradient(900px 600px at 110% 0%, rgba(59,130,246,.10), transparent 55%),
        linear-gradient(180deg, var(--bg0), var(--bg1));
    }

    .wrap{ max-width:1100px; margin:0 auto; }

    a{ color:var(--accent); text-decoration:none; font-weight:800; }

    .topbar{
      display:flex;
      justify-content:space-between;
      align-items:flex-end;
      gap:12px;
      flex-wrap:wrap;
      margin-bottom:14px;
    }

    .title{
      margin:0;
      font-size:24px;
      letter-spacing:-.3px;
      font-weight:980;
    }
    .sub{
      margin-top:6px;
      color: rgba(250,250,250,.60);
      font-size: 12px;
      font-weight:800;
    }

    /* Admin-like compact buttons */
    .btn{
      display:inline-flex;
      align-items:center;
      gap:8px;
      padding:6px 10px;
      border-radius: var(--radiusSm);
      border:1px solid var(--border);
      background: rgba(255,255,255,.03);
      color:var(--text);
      font-weight:900;
      text-decoration:none;
      cursor:pointer;
      user-select:none;
      transition: border-color .12s ease, background .12s ease, transform .06s ease;
      line-height: 1;
      font-size: 13px;
    }
    .btn:hover{
      background: rgba(255,255,255,.05);
      border-color: rgba(255,255,255,.14);
    }
    .btn:active{ transform: translateY(1px); }

    .card{
      border:1px solid var(--border);
      background: rgba(24,24,27,.55);
      border-radius:var(--radius);
      box-shadow: var(--shadow);
      overflow:hidden;
    }

    .card-hdr{
      padding:14px 14px 12px;
      border-bottom:1px solid rgba(39,39,42,.75);
      display:flex;
      justify-content:space-between;
      align-items:center;
      gap:12px;
      flex-wrap:wrap;
      background: rgba(0,0,0,.10);
    }

    .pill{
      display:inline-flex;
      align-items:center;
      gap:8px;
      padding:6px 10px;
      border-radius:999px;
      border:1px solid var(--border);
      background: rgba(255,255,255,.02);
      color: rgba(250,250,250,.92);
      font-weight:900;
      font-size:12px;
      white-space:nowrap;
    }
    .dot{
      width:8px;
      height:8px;
      border-radius:999px;
      background: rgba(250,250,250,.35);
      box-shadow: 0 0 0 4px rgba(250,250,250,.08);
    }
    .pill.ok{
      border-color: rgba(34,197,94,.35);
      background: rgba(34,197,94,.10);
    }
    .pill.ok .dot{
      background: var(--ok);
      box-shadow: 0 0 0 4px rgba(34,197,94,.14);
    }
    .pill.bad{
      border-color: rgba(239,68,68,.35);
      background: rgba(239,68,68,.10);
    }
    .pill.bad .dot{
      background: var(--bad);
      box-shadow: 0 0 0 4px rgba(239,68,68,.14);
    }

    table{
      width:100%;
      border-collapse:separate;
      border-spacing:0;
      font-size:13px;
    }

    thead th{
      position:sticky;
      top:0;
      z-index:2;
      text-align:left;
      padding:10px 12px;
      color: rgba(250,250,250,.60);
      font-weight:900;
      letter-spacing:.06em;
      text-transform:uppercase;
      background: rgba(24,24,27,.92);
      border-bottom:1px solid rgba(39,39,42,.75);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
    }

    tbody td{
      padding:10px 12px;
      border-bottom:1px solid rgba(39,39,42,.65);
      color: rgba(250,250,250,.90);
      vertical-align:top;
    }

    tbody tr:hover td{
      background: rgba(255,255,255,.03);
    }

    .mono{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      font-variant-numeric: tabular-nums;
      color: rgba(250,250,250,.80);
      font-weight:800;
      font-size: 12px;
    }

    .muted{ color: rgba(250,250,250,.62); font-weight:800; }

    .status{
      font-weight:950;
      letter-spacing:.02em;
    }
    .status.ok{ color: var(--ok); }
    .status.bad{ color: var(--bad); }

    .err{
      color: rgba(250,250,250,.78);
      white-space: normal;
      overflow-wrap:anywhere;
      line-height:1.35;
    }

    .col-source{ width: 22%; }
    .col-status{ width: 12%; }
    .col-utc{ width: 20%; }
    .col-human{ width: 18%; }
    .col-err{ width: 28%; }

    @media (max-width: 900px){
      .col-err{ width:auto; }
      thead{ display:none; }
      table, tbody, tr, td{ display:block; width:100%; }
      tbody tr{ border-bottom:1px solid rgba(39,39,42,.65); }
      tbody td{
        border-bottom:0;
        padding:10px 12px;
      }
      tbody td::before{
        display:block;
        margin-bottom:4px;
        color: rgba(250,250,250,.55);
        font-weight:900;
        letter-spacing:.06em;
        text-transform:uppercase;
        font-size:11px;
      }
      tbody td:nth-child(1)::before{ content:"Source"; }
      tbody td:nth-child(2)::before{ content:"Status"; }
      tbody td:nth-child(3)::before{ content:"Last fetch (UTC)"; }
      tbody td:nth-child(4)::before{ content:"Last fetch (human)"; }
      tbody td:nth-child(5)::before{ content:"Error"; }
    }
  </style>
</head>

<body>
  <div class="wrap">
    <div class="topbar">
      <div>
        <h1 class="title">System health</h1>
        <div class="sub">Refreshed <span class="mono">{{ refreshed_utc }}</span></div>
      </div>
      <a class="btn" href="/?{{ qs({}) }}">← Back to feed</a>
    </div>

    {% set bad_count = (health_rows | selectattr('status', 'ne', 'OK') | list | length) %}
    <div class="card">
      <div class="card-hdr">
        <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
          {% if bad_count == 0 %}
            <span class="pill ok"><span class="dot"></span> All sources healthy</span>
          {% else %}
            <span class="pill bad"><span class="dot"></span> Degraded: {{ bad_count }} source{{ 's' if bad_count != 1 else '' }}</span>
          {% endif %}
          <span class="pill">
            <span class="dot" style="background: rgba(59,130,246,.95); box-shadow:0 0 0 4px rgba(59,130,246,.14);"></span>
            Monitoring RSS fetch pipeline
          </span>
        </div>

        <div class="muted">Tip: errors persist until a successful fetch clears them.</div>
      </div>

      <table>
        <thead>
          <tr>
            <th class="col-source">Source</th>
            <th class="col-status">Status</th>
            <th class="col-utc">Last fetch (UTC)</th>
            <th class="col-human">Last fetch (human)</th>
            <th class="col-err">Error</th>
          </tr>
        </thead>
        <tbody>
          {% for r in health_rows %}
            <tr>
              <td class="mono">{{ r.source }}</td>
              <td class="status {{ 'ok' if r.status=='OK' else 'bad' }}">
                {{ r.status }}
              </td>
              <td class="mono muted">{{ r.last_fetch_utc }}</td>
              <td class="muted">{{ r.last_fetch_human }}</td>
              <td class="err muted">{% if r.error %}{{ r.error }}{% else %}—{% endif %}</td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>
</body>
</html>
"""
