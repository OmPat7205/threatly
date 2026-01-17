
DAILY_TEMPLATE = r"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Threatly • Daily</title>
  <style>
    :root{
      /* ===== Enterprise Zinc/Slate system (match Admin + Story) ===== */
      --bg0:#09090b;
      --bg1:#0b0b0f;

      --surface:#18181b;
      --surface2:#141417;

      --border:#27272a;
      --text:#fafafa;
      --muted:#a1a1aa;
      --muted2:#71717a;

      --accent:#22c55e;
      --danger:#ef4444;
      --warn:#f59e0b;

      --shadow: 0 18px 60px rgba(0,0,0,.45);
      --shadow2: 0 10px 25px rgba(0,0,0,.40);

      --r: 6px;
      --r2: 4px;

      --ctl-bg: rgba(255,255,255,.03);
      --ctl-bg-hover: rgba(255,255,255,.05);
      --ctl-border: var(--border);
      --ctl-border-focus: rgba(34,197,94,.45);
    }

    *{ box-sizing:border-box; }
    html,body{ height:100%; }

    body{
      margin:0;
      font-family: Inter, -apple-system,BlinkMacSystemFont,system-ui,Segoe UI,Roboto,Arial,sans-serif;
      background:
        radial-gradient(900px 650px at 20% -15%, rgba(34,197,94,.10), transparent 60%),
        radial-gradient(900px 650px at 110% 0%, rgba(59,130,246,.10), transparent 55%),
        linear-gradient(180deg, var(--bg0), var(--bg1));
      color: var(--text);
      padding:18px;
    }

    a{ color: var(--accent); text-decoration:none; }
    .wrap{ max-width: 1100px; margin:0 auto; }

    .top{
      display:flex;
      justify-content:space-between;
      gap:12px;
      flex-wrap:wrap;
      align-items:flex-end;
      margin-bottom:14px;
    }

    h1{
      margin:0;
      font-size:20px;
      letter-spacing:-.25px;
      font-weight:950;
    }

    .sub{
      color: rgba(250,250,250,.70);
      margin-top:6px;
      font-weight:850;
      font-size:13px;
    }

    .actions{ display:flex; gap:10px; flex-wrap:wrap; align-items:center; }

    /* ===== Buttons (compact enterprise) ===== */
    .btn{
      display:inline-flex;
      align-items:center;
      justify-content:center;
      gap:8px;
      padding:6px 10px;
      border-radius: var(--r2);
      border:1px solid var(--border);
      background: rgba(255,255,255,.03);
      color: rgba(250,250,250,.92);
      font-weight:850;
      text-decoration:none;
      transition: border-color .12s ease, background .12s ease, transform .06s ease;
      font-size:13px;
      line-height:1;
    }
    .btn:hover{
      background: rgba(255,255,255,.05);
      border-color: rgba(255,255,255,.14);
    }
    .btn:active{ transform: translateY(1px); }
    .btn.primary{
      border-color: rgba(34,197,94,.45);
      background: rgba(34,197,94,.12);
      color: rgba(250,250,250,.96);
    }
    .btn.ghost{
      background: transparent;
      border-color: rgba(255,255,255,.10);
      color: rgba(250,250,250,.86);
    }

    .grid{
      display:grid;
      grid-template-columns: 1fr;
      gap:12px;
    }

    /* ===== Report card ===== */
    .card{
      border:1px solid var(--border);
      border-radius: var(--r);
      background: rgba(24,24,27,.62);
      box-shadow: var(--shadow2);
      overflow:hidden;
    }

    .card-head{
      padding:12px 14px;
      display:flex;
      justify-content:space-between;
      align-items:flex-start;
      gap:12px;
      border-bottom:1px solid rgba(255,255,255,.06);
      background: rgba(0,0,0,.12);
    }

    .title{
      font-size:15px;
      font-weight:950;
      margin:0;
      line-height:1.25;
      color: rgba(250,250,250,.96);
    }

    .meta{
      margin-top:8px;
      display:flex;
      flex-wrap:wrap;
      gap:8px;
    }

    /* ===== Chips ===== */
    .chip{
      display:inline-flex;
      align-items:center;
      gap:8px;
      border:1px solid rgba(255,255,255,.10);
      border-radius:999px;
      padding:5px 9px;
      background: rgba(255,255,255,.03);
      color: rgba(250,250,250,.80);
      font-weight:900;
      font-size:12px;
      white-space:nowrap;
    }
    .chip.warn{
      border-color: rgba(245,158,11,.35);
      background: rgba(245,158,11,.12);
      color: rgba(250,250,250,.95);
    }
    .chip.good{
      border-color: rgba(34,197,94,.35);
      background: rgba(34,197,94,.12);
      color: rgba(250,250,250,.95);
    }

    .mono{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      font-variant-numeric: tabular-nums;
      font-weight:900;
    }

    .body{
      padding:12px 14px 14px;
      color: rgba(250,250,250,.86);
      line-height:1.55;
      font-weight:800;
      font-size:13px;
      overflow-wrap:anywhere;
    }

    .card-foot{
      padding:10px 14px 12px;
      border-top:1px solid rgba(255,255,255,.06);
      display:flex;
      justify-content:space-between;
      align-items:center;
      gap:10px;
      flex-wrap:wrap;
      background: rgba(0,0,0,.10);
    }

    .muted{
      color: rgba(250,250,250,.60);
      font-weight:800;
      font-size:12px;
      overflow-wrap:anywhere;
    }

    /* ===== Severity dot (Zinc system) ===== */
    .sev-dot{
      display:inline-block;
      width:10px; height:10px;
      border-radius:999px;
      border:1px solid rgba(255,255,255,.18);
      background: rgba(59,130,246,.92); /* Low default */
      box-shadow: 0 0 0 4px rgba(59,130,246,.10);
      transform: translateY(1px);
    }
    .sev-medium{
      background: rgba(245,158,11,.95);
      box-shadow: 0 0 0 4px rgba(245,158,11,.12);
    }
    .sev-high{
      background: rgba(239,68,68,.95);
      box-shadow: 0 0 0 4px rgba(239,68,68,.12);
    }
    .sev-critical{
      background: rgba(244,63,94,.98);
      box-shadow: 0 0 0 4px rgba(244,63,94,.12);
    }

    /* Make long URLs behave */
    .url{
      word-break: break-word;
      overflow-wrap:anywhere;
    }

          /* ===== Bulk mode ===== */
      .bulk-only{ display:none !important; }
      body.bulk-on .bulk-only{ display:inline-flex !important; }

      .bulk-toggle.on{
        border-color: rgba(34,197,94,.45);
        background: rgba(34,197,94,.12);
      }

      .bulk-check{
        width:18px;
        height:18px;
        accent-color: var(--accent);
        cursor:pointer;
      }

      .bulkbar{
        position: sticky;
        bottom: 0;
        margin-top: 18px;
        padding: 10px 12px;
        border-radius: var(--r);
        border:1px solid rgba(255,255,255,.10);
        background: rgba(24,24,27,.92);
        box-shadow: var(--shadow2);
        display:none;
        align-items:center;
        gap:10px;
        z-index: 50;
      }
      .bulkbar.on{ display:flex; }
      .bulkbar .spacer{ flex:1; }
      .bulkbar .meta{
        font-weight: 950;
        color: rgba(250,250,250,.92);
      }

  </style>
</head>

<body>
  <div class="wrap">
    <div class="top">
      <div>
        <h1>Daily report — {{ report_date }}</h1>
        <div class="sub">Generated <span class="mono">{{ generated_utc }}</span></div>
      </div>

      <div class="actions">
        <!-- ✅ Back button -->
        <a class="btn ghost" href="/">← Back to feed</a>

        {% if app_url %}
          <a class="btn primary" href="{{ app_url }}">Open app</a>
        {% endif %}
        <a class="btn" href="{{ json_url }}">JSON</a>
      </div>
    </div>

    <div class="grid">
      {% for st in stories %}
        {% set sev = st.get('severity') or {} %}
        {% set lvl = sev.get('level','Low') %}
        {% set score = sev.get('score',0) %}

        <div class="card">
          <div class="card-head">
            <div style="min-width:0;">
              <p class="title">{{ st.get('title','Untitled') }}</p>

              <div class="meta">
                <span class="chip">
                  <span class="sev-dot {% if lvl=='Critical' %}sev-critical{% elif lvl=='High' %}sev-high{% elif lvl=='Medium' %}sev-medium{% endif %}"></span>
                  Severity: <strong>{{ lvl }}</strong>
                  <span class="mono">{{ score }}</span>
                </span>

                <span class="chip">Status: <strong>{{ st.get('status','New') }}</strong></span>
                <span class="chip">Trust: <strong>{{ st.get('trust','Research') }}</strong></span>
                <span class="chip">Sources: <strong class="mono">{{ st.get('sources_count',1) }}</strong></span>

                {% if st.get('kev') %}
                  <span class="chip warn"><strong>KEV</strong></span>
                {% endif %}
                {% if sev.get('ioc_count',0)|int > 0 %}
                  <span class="chip">IOCs: <strong class="mono">{{ sev.get('ioc_count',0) }}</strong></span>
                {% endif %}
              </div>
            </div>

            <div class="muted">
              {% set lead = (st.get('articles') or [{}])[0] %}
              {% if lead.get('link') %}
                <a class="btn" href="{{ lead.get('link') }}" target="_blank" rel="noopener">Source ↗</a>
              {% endif %}
            </div>
          </div>

          <div class="body">{{ (st.get('summary') or '') }}</div>

          <div class="card-foot">
            <div class="muted url">
              {% set lead2 = (st.get('articles') or [{}])[0] %}
              {% if lead2.get('link') %}
                {{ lead2.get('link') }}
              {% else %}
                —
              {% endif %}
            </div>
            <div class="muted">
              {{ st.get('lead_source','') }}
            </div>
          </div>
        </div>
      {% endfor %}
    </div>
  </div>
</body>
</html>
"""