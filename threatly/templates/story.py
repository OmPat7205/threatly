STORY_TEMPLATE = r"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ story.title }} — Threatly</title>
  <style>
    :root{
      /* ===== Enterprise Zinc/Slate system (match Admin + Base) ===== */
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
      font-family: Inter, -apple-system, BlinkMacSystemFont, system-ui, Segoe UI, Roboto, Arial, sans-serif;
      color:var(--text);
      background:
        radial-gradient(900px 600px at 20% -10%, rgba(34,197,94,.10), transparent 60%),
        radial-gradient(900px 600px at 110% 0%, rgba(59,130,246,.10), transparent 55%),
        linear-gradient(180deg, var(--bg0), var(--bg1));
    }
    a{ color:inherit; text-decoration:none; }
    .wrap{ max-width:1200px; margin:0 auto; padding:20px 18px 60px; }

    .topbar{
      display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap;
      margin-bottom:14px;
    }

    /* ===== Buttons (compact enterprise) ===== */
    .btn{
      display:inline-flex; align-items:center; justify-content:center; gap:8px;
      padding:6px 10px;
      border-radius: var(--r2);
      border:1px solid var(--border);
      background: rgba(255,255,255,.03);
      color: var(--text);
      font-weight:850;
      cursor:pointer;
      user-select:none;
      transition: transform .06s ease, border-color .12s ease, background .12s ease, opacity .12s ease;
      font-size:13px;
      line-height:1;
    }
    .btn:hover{ background: rgba(255,255,255,.05); border-color: rgba(255,255,255,.14); }
    .btn:active{ transform: translateY(1px); }
    .btn.primary{ border-color: rgba(34,197,94,.45); background: rgba(34,197,94,.12); }
    .btn.ghost{ background: transparent; }
    .btn.small{ padding:6px 9px; border-radius: var(--r2); font-size:12px; }
    .btn[disabled]{ opacity:.45; cursor:not-allowed; }

    /* ===== Sources dropdown ===== */
    .src-menu{ position:relative; display:inline-flex; }
    .src-panel{
      position:absolute;
      top: calc(100% + 8px);
      right:0;
      min-width: 340px;
      max-width: 520px;
      z-index: 50;

      border:1px solid rgba(255,255,255,.10);
      background: rgba(24,24,27,.96);
      border-radius: 12px;
      box-shadow: var(--shadow2);
      padding:10px;
      display:none;
    }
    .src-panel.on{ display:block; }

    .src-item{
      display:flex;
      gap:10px;
      padding:10px 10px;
      border-radius: 10px;
      border:1px solid rgba(255,255,255,.08);
      background: rgba(255,255,255,.02);
      transition: background .12s ease, border-color .12s ease;
    }
    .src-item:hover{
      background: rgba(34,197,94,.10);
      border-color: rgba(34,197,94,.25);
    }
    .src-item + .src-item{ margin-top:8px; }

    .src-main{
      display:flex; flex-direction:column; gap:4px;
      min-width: 0;
    }
    .src-title{
      font-weight:950;
      color: rgba(250,250,250,.92);
      font-size:13px;
      line-height:1.35;
      overflow:hidden;
      text-overflow:ellipsis;
      white-space:nowrap;
    }
    .src-sub{
      font-weight:850;
      color: rgba(161,161,170,.90);
      font-size:12px;
      overflow:hidden;
      text-overflow:ellipsis;
      white-space:nowrap;
    }
    .src-badge{
      margin-left:auto;
      font-weight:950;
      font-size:12px;
      padding:6px 10px;
      border-radius:999px;
      border:1px solid rgba(255,255,255,.10);
      background: rgba(255,255,255,.03);
      color: rgba(250,250,250,.82);
      white-space:nowrap;
      flex:0 0 auto;
      align-self:flex-start;
    }

    /* ===== Pills (compact) ===== */
    .pill{
      display:inline-flex; align-items:center; gap:8px;
      padding:5px 9px;
      border-radius:999px;
      border:1px solid rgba(255,255,255,.10);
      background: rgba(255,255,255,.03);
      color: rgba(250,250,250,.92);
      font-weight:900;
      font-size:12px;
      white-space:nowrap;
    }
    .pill.good{ border-color: rgba(34,197,94,.35); background: rgba(34,197,94,.12); }
    .pill.warn{ border-color: rgba(245,158,11,.35); background: rgba(245,158,11,.12); }
    .pill.muted{ color: rgba(250,250,250,.70); }

    /* ===== Header card ===== */
    .header{
      border:1px solid var(--border);
      background: rgba(24,24,27,.65);
      border-radius: var(--r);
      box-shadow: var(--shadow2);
      padding:16px 16px 14px;
    }
    .title{
      margin:0;
      font-size:26px;
      line-height:1.12;
      letter-spacing:-.3px;
      font-weight:950;
    }
    .meta-row{
      display:flex; flex-wrap:wrap; gap:10px;
      margin-top:12px;
    }
    .summary{
      margin-top:14px;
      color: rgba(250,250,250,.86);
      line-height:1.6;
      font-size:15px;
      overflow-wrap:anywhere;
    }

    /* ===== Timeline ===== */
    .timeline{
      margin-top:14px;
      border:1px solid rgba(255,255,255,.10);
      background: rgba(255,255,255,.02);
      border-radius: var(--r);
      padding:12px 12px 10px;
      overflow:hidden;
    }
    .timeline-top{
      display:flex; align-items:center; justify-content:space-between; gap:10px; flex-wrap:wrap;
      margin-bottom:10px;
    }
    .timeline-title{
      font-size:12px;
      letter-spacing:.12em;
      text-transform:uppercase;
      color: rgba(250,250,250,.60);
      font-weight:900;
      margin:0;
    }
    .timeline-rail{
      display:grid;
      grid-template-columns: repeat(4, 1fr);
      gap:12px;
      align-items:start;
    }
    @media (max-width: 980px){
      .timeline-rail{ grid-template-columns: 1fr; }
    }
    .t-step{
      position:relative;
      padding:10px 11px 10px 11px;
      border:1px solid rgba(255,255,255,.08);
      background: rgba(0,0,0,.18);
      border-radius: var(--r2);
    }
    .t-head{
      display:flex; align-items:center; gap:10px;
      margin-bottom:6px;
    }
    .t-dot{
      width:10px; height:10px; border-radius:999px;
      background: rgba(161,161,170,.95);
      box-shadow: 0 0 0 4px rgba(161,161,170,.10);
      flex:0 0 auto;
    }
    .t-dot.on{
      background: rgba(34,197,94,.95);
      box-shadow: 0 0 0 4px rgba(34,197,94,.12);
    }
    .t-dot.warn{
      background: rgba(245,158,11,.95);
      box-shadow: 0 0 0 4px rgba(245,158,11,.12);
    }
    .t-label{
      font-weight:950;
      color: rgba(250,250,250,.92);
      font-size:13px;
    }
    .t-val{
      font-weight:900;
      color: rgba(250,250,250,.80);
      font-size:12px;
      overflow-wrap:anywhere;
      line-height:1.45;
    }
    .t-sub{
      margin-top:6px;
      font-size:12px;
      font-weight:800;
      color: rgba(250,250,250,.60);
    }

    /* ===== Grid cards ===== */
    .grid{
      margin-top:16px;
      display:grid;
      grid-template-columns: 1fr 1fr;
      gap:16px;
    }
    @media (max-width: 980px){
      .grid{ grid-template-columns: 1fr; }
    }

    .card{
      border:1px solid var(--border);
      background: rgba(24,24,27,.55);
      border-radius: var(--r);
      box-shadow: var(--shadow2);
      padding:14px;
      min-height: 120px;
    }
    .card h3{
      margin:0 0 10px 0;
      font-size:12px;
      letter-spacing:.12em;
      text-transform:uppercase;
      color: rgba(250,250,250,.60);
      font-weight:900;
    }

    .kv{
      display:grid;
      grid-template-columns: 220px 1fr;
      gap:10px 12px;
      align-items:start;
      font-weight:900;
      color: rgba(250,250,250,.86);
    }
    @media (max-width: 560px){
      .kv{ grid-template-columns: 1fr; }
    }
    .k{ color: rgba(161,161,170,.95); font-weight:900; }
    .v{ color: rgba(250,250,250,.92); font-weight:900; overflow-wrap:anywhere; }

    ul.bul{
      margin:0; padding-left:18px;
      color: rgba(250,250,250,.88);
      font-weight:900;
      line-height:1.6;
      font-size:13px;
    }

    .notes-wrap{ display:flex; flex-direction:column; gap:12px; }

    .field-row{
      display:flex;
      gap:10px;
      flex-wrap:wrap;
      align-items:flex-end;
      justify-content:space-between;
    }
    .field{ flex:1; min-width:240px; }
    .label{ color: rgba(250,250,250,.60); font-weight:900; line-height:1.5; font-size:13px; margin-bottom:6px; }

    /* ===== Unified inputs/select/textarea ===== */
    input, select, textarea{
      font-family: inherit;
      font-size: 13px;
      color: var(--text);
      background: var(--ctl-bg);
      border: 1px solid var(--ctl-border);
      border-radius: var(--r2);
      padding: 7px 10px;
      outline: none;
      color-scheme: dark;
    }
    input:focus, select:focus, textarea:focus{
      border-color: var(--ctl-border-focus);
      box-shadow: 0 0 0 3px rgba(34,197,94,.12);
    }
    .select, .textarea, .input{ width:100%; }
    .textarea{
      min-height:160px;
      resize:vertical;
      line-height:1.5;
      font-weight:800;
      color: rgba(250,250,250,.92);
    }

    .hint{ color: rgba(234,241,251,.62); font-weight:900; line-height:1.5; font-size:13px; }

    .review-link{
      display:inline-flex;
      align-items:center;
      gap:8px;
      color: rgba(234,241,251,.90);
      font-weight:950;
      text-decoration:none;
      padding:6px 10px;
      border-radius:999px;
      border:1px solid rgba(255,255,255,.10);
      background: rgba(255,255,255,.03);
      transition: border-color .12s ease, background .12s ease, transform .06s ease;
    }
    .review-link:hover{ border-color: rgba(34,197,94,.35); background: rgba(34,197,94,.10); }
    .review-link:active{ transform: translateY(1px); }

    .review-muted{
      display:inline-flex;
      align-items:center;
      gap:8px;
      color: rgba(234,241,251,.62);
      font-weight:950;
      padding:6px 10px;
      border-radius:999px;
      border:1px solid rgba(255,255,255,.08);
      background: rgba(255,255,255,.02);
      cursor: default;
    }

    .divider{ margin-top:12px; height:1px; background: rgba(255,255,255,.06); }

    /* Toast */
    .toast{
      position:fixed;
      right:18px;
      bottom:18px;
      max-width:520px;
      padding:12px 14px;
      border-radius: var(--r);
      border:1px solid rgba(255,255,255,.10);
      background: rgba(24,24,27,.92);
      box-shadow: var(--shadow2);
      color: rgba(250,250,250,.92);
      font-weight:900;
      display:none;
      z-index:9999;
    }
    .toast.on{ display:block; }

    .mono{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      font-weight:900;
    }
    .tag{
      display:inline-flex; align-items:center;
      padding:6px 10px;
      border-radius:999px;
      border:1px solid rgba(255,255,255,.10);
      background: rgba(255,255,255,.03);
      color: rgba(250,250,250,.78);
      font-weight:900;
      font-size:12px;
      margin: 4px 6px 0 0;
    }

    .notes-toolbar{
      display:flex; align-items:center; justify-content:space-between; gap:10px; flex-wrap:wrap;
      margin-bottom:8px;
    }
    .seg{
      display:inline-flex;
      border:1px solid rgba(255,255,255,.10);
      background: rgba(255,255,255,.03);
      border-radius: var(--r2);
      overflow:hidden;
    }
    .seg button{
      border:0;
      background: transparent;
      color: rgba(250,250,250,.78);
      padding:7px 10px;
      font-weight:900;
      cursor:pointer;
      font-size:12px;
    }
    .seg button.on{
      background: rgba(34,197,94,.12);
      color: var(--text);
    }

    .preview{
      border:1px solid rgba(255,255,255,.10);
      background: rgba(255,255,255,.02);
      border-radius: var(--r2);
      padding:12px 12px;
      min-height:160px;
      color: rgba(250,250,250,.90);
      line-height:1.6;
      overflow-wrap:anywhere;
      display:none;
      font-size:13px;
    }
    .preview.on{ display:block; }
    .preview code{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      font-size: 12px;
      padding:2px 6px;
      border-radius: 6px;
      border:1px solid rgba(255,255,255,.10);
      background: rgba(255,255,255,.03);
    }
    .preview pre{
      margin:10px 0;
      padding:12px;
      border-radius: var(--r2);
      border:1px solid rgba(255,255,255,.10);
      background: rgba(0,0,0,.30);
      overflow:auto;
    }
    .preview pre code{ border:0; background: transparent; padding:0; }

    .save-chip{
      display:inline-flex; align-items:center; gap:8px;
      padding:6px 10px;
      border-radius:999px;
      border:1px solid rgba(255,255,255,.10);
      background: rgba(255,255,255,.03);
      color: rgba(250,250,250,.78);
      font-weight:900;
      font-size:12px;
      white-space:nowrap;
    }
    .dot{
      width:8px; height:8px; border-radius:999px;
      background: rgba(161,161,170,.95);
      box-shadow: 0 0 0 4px rgba(161,161,170,.10);
    }
    .save-chip.saved .dot{
      background: rgba(34,197,94,.95);
      box-shadow: 0 0 0 4px rgba(34,197,94,.12);
    }
    .save-chip.dirty .dot{
      background: rgba(245,158,11,.95);
      box-shadow: 0 0 0 4px rgba(245,158,11,.12);
    }
    .save-chip.saving .dot{
      background: rgba(59,130,246,.95);
      box-shadow: 0 0 0 4px rgba(59,130,246,.12);
      animation: pulse 1.05s ease-in-out infinite;
    }
    .save-chip.failed .dot{
      background: rgba(239,68,68,.95);
      box-shadow: 0 0 0 4px rgba(239,68,68,.12);
    }
    @keyframes pulse{
      0%{ transform: scale(1.0); opacity: .95; }
      50%{ transform: scale(1.45); opacity: .55; }
      100%{ transform: scale(1.0); opacity: .95; }
    }

    /* ===== Lifecycle v2 (collapsed + grouped, client-rendered) ===== */
    .life-rows{ display:flex; flex-direction:column; gap:8px; }
    .life-row{
      display:flex; align-items:flex-start; justify-content:space-between; gap:10px;
      border:1px solid rgba(255,255,255,.10);
      border-radius:12px;
      background: rgba(255,255,255,.02);
      padding:10px 12px;
    }
    .life-left{ min-width:0; display:flex; flex-direction:column; gap:4px; }
    .life-line1{
      display:flex; align-items:center; gap:10px; flex-wrap:wrap;
      font-weight:950;
      color: rgba(250,250,250,.92);
    }
    .life-line2{
      color: rgba(250,250,250,.78);
      font-weight:850;
      line-height:1.45;
      overflow-wrap:anywhere;
    }
    .life-meta{
      display:flex; align-items:center; gap:10px; flex-wrap:wrap;
      color: rgba(250,250,250,.60);
      font-weight:900;
      font-size:12px;
      white-space:nowrap;
      flex:0 0 auto;
    }
    .life-chip{
      display:inline-flex; align-items:center; gap:8px;
      padding:5px 9px;
      border-radius:999px;
      border:1px solid rgba(255,255,255,.10);
      background: rgba(255,255,255,.03);
      color: rgba(250,250,250,.80);
      font-weight:950;
      font-size:12px;
      white-space:nowrap;
    }
    .life-chip.good{ border-color: rgba(34,197,94,.35); background: rgba(34,197,94,.12); }
    .life-chip.warn{ border-color: rgba(245,158,11,.35); background: rgba(245,158,11,.12); }

    .life-actions{
      margin-top:10px;
      display:flex; align-items:center; justify-content:space-between; gap:10px; flex-wrap:wrap;
    }
    .life-noise{
      display:inline-flex; align-items:center; gap:8px;
      color: rgba(250,250,250,.65);
      font-weight:900;
      font-size:12px;
      user-select:none;
    }
    .life-noise input{ transform: translateY(1px); }

    details.life-details{
      border:1px solid rgba(255,255,255,.10);
      border-radius:12px;
      background: rgba(0,0,0,.18);
      padding:10px 12px;
      margin-top:10px;
    }
    details.life-details > summary{
      cursor:pointer;
      list-style:none;
      color: rgba(250,250,250,.78);
      font-weight:950;
    }
    details.life-details > summary::-webkit-details-marker{ display:none; }
    .life-mono{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono","Courier New", monospace;
      font-weight:900;
      white-space: pre-wrap;
      word-break: break-word;
    }

    /* ===== NEW: View-only banner style ===== */
    .lockbox{
      margin-bottom:10px;
      padding:10px 12px;
      border:1px solid rgba(255,255,255,.10);
      border-radius:12px;
      background: rgba(255,255,255,.03);
      color: rgba(250,250,250,.78);
      font-weight:900;
    }
  </style>
</head>

<body>
  <div class="wrap">
    {% set CAN_EDIT = (can_case_edit|default(false)) %}
    {% set CAN_ADMIN = (can_view_admin|default(false)) %}
    {% set IS_AUTHED = (current_user_email|default('')|length > 0) %}

    <div class="topbar">
      <a class="btn ghost" href="/?{{ qs({}) }}">← Back to feed</a>

      <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
        {% if story.articles and story.articles|length > 0 %}
          {% set srcs = story.articles %}
          {% if srcs|length == 1 %}
            <a class="btn"
               href="{{ srcs[0].link or srcs[0].url }}"
               target="_blank" rel="noopener">Open source</a>
          {% else %}
            <div class="src-menu" id="srcMenu">
              <button class="btn" id="srcBtn" type="button">
                Open sources
                <span class="pill muted" style="border:0;background:transparent;padding:0;">{{ srcs|length }}</span>
              </button>

              <div class="src-panel" id="srcPanel" role="menu" aria-label="Sources">
                {% for a in srcs %}
                  {% set href = (a.link or a.url or "") %}
                  {% if href %}
                    <a class="src-item" href="{{ href }}" target="_blank" rel="noopener" role="menuitem">
                      <div class="src-main">
                        <div class="src-title">{{ a.title or a.source or ("Source " ~ loop.index) }}</div>
                        <div class="src-sub">{{ href }}</div>
                      </div>
                      <div class="src-badge">#{{ loop.index }}</div>
                    </a>
                  {% endif %}
                {% endfor %}
              </div>
            </div>
          {% endif %}
        {% endif %}

        <span class="pill muted mono">Story ID: {{ story.story_id }}</span>
      </div>
    </div>

    <div class="header">
      <h1 class="title">{{ story.title }}</h1>

      {% set sev = story.severity or {} %}
      <div class="meta-row">
        <span class="pill"><span class="muted" style="border:0;background:transparent;padding:0;color:rgba(250,250,250,.65)">Status:</span><strong>{{ story.status }}</strong></span>
        <span class="pill"><span class="muted" style="border:0;background:transparent;padding:0;color:rgba(250,250,250,.65)">Severity:</span> <strong>{{ (sev.level or 'Low') }}</strong> <span class="pill muted" style="border:0;background:transparent;padding:0;">{{ sev.score or 0 }}</span></span>
        <span class="pill"><span class="muted" style="border:0;background:transparent;padding:0;color:rgba(250,250,250,.65)">Trust:</span> <strong>{{ story.trust }}</strong></span>
        <span class="pill"><span class="muted" style="border:0;background:transparent;padding:0;color:rgba(250,250,250,.65)">Sources:</span> <strong>{{ story.sources_count }}</strong></span>
        {% if story.updated_utc %}
          <span class="pill"><span class="pill muted" style="border:0;background:transparent;padding:0;">Updated:</span> <strong>{{ rel_time(story.updated_utc) }}</strong></span>
        {% endif %}
        {% if story.kev %}
          <span class="pill warn"><strong>KEV</strong></span>
        {% endif %}
        {% if story.matches_stack %}
          <span class="pill good"><strong>Matches watchlist</strong></span>
        {% endif %}
        {% if story.seen_before %}
          <span class="pill warn"><strong>Seen before</strong></span>
        {% endif %}
      </div>

      {% if story.summary %}
        <div class="summary">{{ story.summary }}</div>
      {% endif %}

      <div class="timeline">
        <div class="timeline-top">
          <div class="timeline-title">Timeline</div>
          <div class="hint">
            {% if story.seen_count and (story.seen_count|int) > 0 %}
              {% if CAN_ADMIN %}
                <a class="review-link" href="/admin/reviews/{{ story.story_id }}" title="Admin: view who reviewed this story">
                  Reviewed <span class="mono">{{ story.seen_count }}</span>×
                </a>
              {% else %}
                <span class="review-muted" title="Total review count">
                  Reviewed <span class="mono">{{ story.seen_count }}</span>×
                </span>
              {% endif %}
            {% else %}
              Not reviewed yet
            {% endif %}
          </div>
        </div>

        <div class="timeline-rail">
          <div class="t-step">
            <div class="t-head">
              <span class="t-dot on"></span>
              <div class="t-label">Published</div>
            </div>
            <div class="t-val mono">{{ story.published or (story.published_dt|string) }}</div>
            <div class="t-sub">
              {% if story.published %}{{ rel_time(story.published) }}{% endif %}
            </div>
          </div>

          <div class="t-step">
            <div class="t-head">
              <span class="t-dot {% if story.first_seen_utc %}on{% endif %}"></span>
              <div class="t-label">First reviewed</div>
            </div>
            <div class="t-val mono">
              {% if story.first_seen_utc %}
                {{ story.first_seen_utc }}
              {% else %}
                —
              {% endif %}
            </div>
            <div class="t-sub">
              {% if story.first_seen_utc %}{{ rel_time(story.first_seen_utc) }}{% else %}Per-user{% endif %}
            </div>
          </div>

          <div class="t-step">
            <div class="t-head">
              <span class="t-dot {% if story.last_seen_utc %}on{% endif %}"></span>
              <div class="t-label">Last reviewed</div>
            </div>
            <div class="t-val mono">
              {% if story.last_seen_utc %}
                {{ story.last_seen_utc }}
              {% else %}
                —
              {% endif %}
            </div>
            <div class="t-sub">
              {% if story.last_seen_utc %}{{ rel_time(story.last_seen_utc) }}{% else %}Per-user{% endif %}
            </div>
          </div>

          <div class="t-step">
            <div class="t-head">
              <span class="t-dot {% if story.updated_utc %}warn{% endif %}"></span>
              <div class="t-label">Last updated</div>
            </div>
            <div class="t-val mono">
              {% if story.updated_utc %}
                {{ story.updated_utc }}
              {% else %}
                —
              {% endif %}
            </div>
            <div class="t-sub">
              {% if story.updated_utc %}
                {{ rel_time(story.updated_utc) }}
                {% if story.updated_by_email %} · {{ story.updated_by_email }}{% endif %}
              {% else %}
                Global meta
              {% endif %}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="grid">
      <div class="card">
        <h3>Why ranked</h3>
        {% if sev.reasons and sev.reasons|length > 0 %}
          <ul class="bul">
            {% for r in sev.reasons %}
              <li>{{ r }}</li>
            {% endfor %}
          </ul>
        {% else %}
          <div class="hint">No ranking reasons available.</div>
        {% endif %}
      </div>

      <div class="card">
        <h3>Signals</h3>
        <div class="kv">
          <div class="k">Published</div>
          <div class="v mono">{{ story.published or (story.published_dt|string) }}</div>

          <div class="k">Lead source</div>
          <div class="v">{{ story.lead_source or '' }}</div>

          <div class="k">Categories</div>
          <div class="v">
            {% if story.categories and story.categories|length > 0 %}
              {{ story.categories|join(' · ') }}
            {% else %}
              <span class="hint">—</span>
            {% endif %}
          </div>

          <div class="k">CVEs</div>
          <div class="v">
            {% set cves = (story.indicators or {}).get('cves', []) %}
            {% if cves and cves|length > 0 %}
              {% for c in cves[:12] %}
                <span class="tag mono">{{ c }}</span>
              {% endfor %}
            {% else %}
              <span class="hint">—</span>
            {% endif %}
          </div>
        </div>
      </div>

      <div class="card">
        <h3>Indicators</h3>
        {% set ind = story.indicators or {} %}
        <div class="kv">
          <div class="k">IPs</div>
          <div class="v">{{ (ind.get('ips', []) or [])|length }}</div>

          <div class="k">Domains</div>
          <div class="v">{{ (ind.get('domains', []) or [])|length }}</div>

          <div class="k">URLs</div>
          <div class="v">{{ (ind.get('urls', []) or [])|length }}</div>

          <div class="k">Hashes</div>
          <div class="v">
            {% set hc = (ind.get('md5', [])|length) + (ind.get('sha1', [])|length) + (ind.get('sha256', [])|length) %}
            {{ hc }}
          </div>
        </div>
      </div>

      <div class="card">
        <h3>CVE enrichment</h3>
        {% set enr = story.cve_enrichment or {} %}
        <div class="kv">
          <div class="k">CVSS max</div>
          <div class="v">{{ enr.get('cvss_max') if enr.get('cvss_max') is not none else 'None' }}</div>

          <div class="k">EPSS max</div>
          <div class="v">
            {% if enr.get('epss_max') is not none %}
              {{ ('%.2f' % (enr.get('epss_max') * 100.0)) }}%
            {% else %}
              —
            {% endif %}
          </div>

          <div class="k">CVEs</div>
          <div class="v">
            {% set rows = enr.get('cves', []) or [] %}
            {% if rows and rows|length > 0 %}
              <ul class="bul">
                {% for row in rows[:12] %}
                  <li class="mono">{{ row.get('cve','') }}</li>
                {% endfor %}
              </ul>
            {% else %}
              <div class="hint">• No CVE enrichment.</div>
            {% endif %}
          </div>
        </div>
      </div>

      <div class="card" style="grid-column: 1 / -1;">
        <h3>Notes & triage</h3>

        {# ===== NEW: clearer lock messaging ===== #}
        {% if not IS_AUTHED %}
          <div class="lockbox">🔒 Login required to edit status/owner/notes.</div>
        {% elif not CAN_EDIT %}
          <div class="lockbox">🔒 View-only: you don’t have permission to edit status/owner/notes.</div>
        {% endif %}

        <div class="notes-wrap" id="notesWrap">
          <div class="field-row">
            <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
              <span class="save-chip saved" id="saveChip" title="Autosave status">
                <span class="dot"></span>
                <span id="saveText">Saved</span>
              </span>
              <span class="hint" id="saveHint">Autosaves after you stop typing.</span>
            </div>

            <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
              {% if IS_AUTHED and CAN_EDIT %}
                <button class="btn" id="assignBtn" type="button">Assign to me</button>
                <button class="btn primary" id="saveBtn" type="button">Save now</button>
              {% elif not IS_AUTHED %}
                <a class="btn primary" href="/login">Login to edit</a>
              {% endif %}
            </div>
          </div>

          {# ===== NEW: RBAC UI gating (server-side) ===== #}
          {% if IS_AUTHED and CAN_EDIT %}
            <div class="field-row">
              <div class="field">
                <div class="label">Status</div>
                <select class="select" id="statusSel">
                  {% for sv in status_values %}
                    <option value="{{ sv }}" {% if story.status == sv %}selected{% endif %}>{{ sv }}</option>
                  {% endfor %}
                </select>
              </div>

              <div class="field">
                <div class="label">Owner</div>
                <input class="input" id="ownerInput" value="{{ story.owner }}" placeholder="Unassigned" />
              </div>
            </div>

            <div class="notes-toolbar">
              <div class="hint">Markdown supported (bullets, links, code blocks). Preview before saving.</div>
              <div class="seg" role="tablist" aria-label="Notes view">
                <button type="button" id="editTab" class="on">Edit</button>
                <button type="button" id="previewTab">Preview</button>
              </div>
            </div>

            <textarea class="textarea" id="notesTa" placeholder="Example:
- Impact:
- Affected systems:
- Detection:
- Next action:
Links: [CISA advisory](https://...)
Code:
```bash
grep -R &quot;cve&quot; /var/log
```">{{ story.notes }}</textarea>

            <div class="preview" id="notesPreview"></div>

          {% else %}
            {# View-only mode: no editable controls, but still show content #}
            <div class="field-row">
              <div class="field">
                <div class="label">Status</div>
                <div class="hint"><span class="mono">{{ story.status }}</span></div>
              </div>

              <div class="field">
                <div class="label">Owner</div>
                <div class="hint">
                  {% if story.owner %}<span class="mono">{{ story.owner }}</span>{% else %}Unassigned{% endif %}
                </div>
              </div>
            </div>

            <div class="notes-toolbar">
              <div class="hint">Notes (read-only)</div>
              <div class="seg" role="tablist" aria-label="Notes view">
                <button type="button" id="editTab" class="on">View</button>
                <button type="button" id="previewTab">Preview</button>
              </div>
            </div>

            <textarea class="textarea" id="notesTa" readonly>{{ story.notes }}</textarea>
            <div class="preview" id="notesPreview"></div>
          {% endif %}

          <div class="hint" style="margin-top:8px;">
            <span id="lastUpdatedLine">
              {% if story.updated_utc %}
                Last updated {{ rel_time(story.updated_utc) }}
              {% else %}
                Not updated yet
              {% endif %}
              {% if story.updated_by_email %}
                · by <span class="mono">{{ story.updated_by_email }}</span>
              {% endif %}
            </span>
          </div>

          <div class="divider"></div>
          <div class="hint">Tip: decision-first notes win. “So what?”, “What do we do?”, “By when?”</div>
        </div>
      </div>

      <!-- ===== Lifecycle v2 (collapsed by default, rendered client-side) ===== -->
      <div class="card" style="grid-column: 1 / -1;">
        <h3 style="display:flex; align-items:center; justify-content:space-between; gap:10px;">
          <span>Lifecycle</span>
          <span class="pill muted" id="lifeCountPill">0 events</span>
        </h3>

        <div class="life-rows" id="lifePreview"></div>

        <div class="life-actions">
          <button class="btn small" id="lifeToggleBtn" type="button" aria-expanded="false">
            View full history ▾
          </button>
          <label class="life-noise">
            <input type="checkbox" id="lifeHideNoise" checked />
            Hide noisy (autosave) events
          </label>
        </div>

        <div id="lifeFull" style="display:none; margin-top:10px;"></div>

        <div class="hint" style="margin-top:10px;">
          Tip: Preview shows the most recent meaningful changes. Full history is the audit trail.
        </div>
      </div>

    </div>

    <div class="toast" id="toast"></div>
  </div>

  <script>
    const INIT = {{ {
      "story_id": story.story_id,
      "status": story.status,
      "owner": story.owner,
      "notes": story.notes,
      "updated_utc": story.updated_utc,
      "updated_by_email": story.updated_by_email,
      "current_user_email": (current_user_email|default("")),
      "can_case_edit": (CAN_EDIT),
      "csrf_token": (csrf_token|default(""))
    } | tojson }};

    function toast(msg){
      const t = document.getElementById("toast");
      if(!t) return;
      t.textContent = msg;
      t.classList.add("on");
      setTimeout(()=> t.classList.remove("on"), 2200);
    }

    async function postJSON(url, body){
      const headers = {"Content-Type":"application/json"};
      if(INIT && INIT.csrf_token){
        headers["X-CSRF-Token"] = INIT.csrf_token;
      }
      const r = await fetch(url, {
        method: "POST",
        headers,
        credentials: "same-origin",
        body: JSON.stringify(body || {})
      });
      let data = null;
      try{ data = await r.json(); }catch(e){}
      return {ok: r.ok, status: r.status, data};
    }

    function escapeHtml(s){
      return (s || "")
        .replaceAll("&","&amp;")
        .replaceAll("<","&lt;")
        .replaceAll(">","&gt;")
        .replaceAll('"',"&quot;")
        .replaceAll("'","&#039;");
    }

    // Sources dropdown (multi-source stories)
    (function(){
      const btn = document.getElementById("srcBtn");
      const panel = document.getElementById("srcPanel");
      const menu = document.getElementById("srcMenu");
      if(!btn || !panel || !menu) return;

      function close(){ panel.classList.remove("on"); }
      function toggle(){ panel.classList.toggle("on"); }

      btn.addEventListener("click", (e)=>{ e.preventDefault(); e.stopPropagation(); toggle(); });
      panel.addEventListener("click", (e)=>{ e.stopPropagation(); });
      document.addEventListener("click", ()=> close());
      document.addEventListener("keydown", (e)=>{ if(e.key === "Escape") close(); });
    })();

    function mdToHtml(md){
      let s = escapeHtml(md || "");
      s = s.replaceAll("\r\n", "\n").replaceAll("\r", "\n");

      const blocks = [];
      s = s.replace(/```([\s\S]*?)```/g, function(_, code){
        const idx = blocks.length;
        blocks.push(code);
        return `@@CODEBLOCK_${idx}@@`;
      });

      s = s.replace(/^###\s+(.*)$/gm, "<h3>$1</h3>");
      s = s.replace(/^##\s+(.*)$/gm, "<h2>$1</h2>");
      s = s.replace(/^#\s+(.*)$/gm, "<h1>$1</h1>");

      s = s.replace(/\[([^\]]+)\]\(([^)]+)\)/g, function(_, text, url){
        const u = (url || "").trim();
        const safe = (u.startsWith("http://") || u.startsWith("https://")) ? u : "#";
        return `<a href="${safe}" target="_blank" rel="noopener">${text}</a>`;
      });

      s = s.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
      s = s.replace(/(^|[^*])\*([^*]+)\*(?!\*)/g, "$1<em>$2</em>");
      s = s.replace(/`([^`]+)`/g, "<code>$1</code>");

      const lines = s.split("\n");
      let out = [];
      let inUl = false;
      let inOl = false;

      function closeLists(){
        if(inUl){ out.push("</ul>"); inUl = false; }
        if(inOl){ out.push("</ol>"); inOl = false; }
      }

      for(const line of lines){
        const ul = line.match(/^\s*[-*]\s+(.*)$/);
        const ol = line.match(/^\s*\d+\.\s+(.*)$/);

        if(ul){
          if(inOl){ out.push("</ol>"); inOl = false; }
          if(!inUl){ out.push("<ul>"); inUl = true; }
          out.push("<li>" + ul[1] + "</li>");
          continue;
        }
        if(ol){
          if(inUl){ out.push("</ul>"); inUl = false; }
          if(!inOl){ out.push("<ol>"); inOl = true; }
          out.push("<li>" + ol[1] + "</li>");
          continue;
        }

        closeLists();

        const trimmed = line.trim();
        if(trimmed === ""){
          out.push("");
        }else if(/^<h[1-3]>/.test(trimmed)){
          out.push(trimmed);
        }else{
          out.push("<p>" + line + "</p>");
        }
      }
      closeLists();

      s = out.join("\n");

      s = s.replace(/@@CODEBLOCK_(\d+)@@/g, function(_, n){
        const code = blocks[parseInt(n,10)] || "";
        return "<pre><code>" + code + "</code></pre>";
      });

      return s;
    }

    function relTimeFromIso(iso){
      if(!iso) return "";
      const dt = new Date(iso);
      if(isNaN(dt.getTime())) return "";
      const sec = Math.floor((Date.now() - dt.getTime())/1000);
      if(sec < 60) return sec + "s ago";
      const mins = Math.floor(sec/60);
      if(mins < 60) return mins + "m ago";
      const hrs = Math.floor(mins/60);
      if(hrs < 48) return hrs + "h ago";
      const days = Math.floor(hrs/24);
      return days + "d ago";
    }

    const statusSel = document.getElementById("statusSel");
    const ownerInput = document.getElementById("ownerInput");
    const notesTa = document.getElementById("notesTa");
    const saveBtn = document.getElementById("saveBtn");
    const assignBtn = document.getElementById("assignBtn");

    const editTab = document.getElementById("editTab");
    const previewTab = document.getElementById("previewTab");
    const previewEl = document.getElementById("notesPreview");

    const saveChip = document.getElementById("saveChip");
    const saveText = document.getElementById("saveText");
    const lastUpdatedLine = document.getElementById("lastUpdatedLine");

    const authed = (INIT.current_user_email || "").length > 0;
    const canEdit = (INIT.can_case_edit === true);

    function setMode(mode){
      if(mode === "preview"){
        if(previewEl && notesTa){
          previewEl.innerHTML = mdToHtml(notesTa.value || "");
          previewEl.classList.add("on");
          notesTa.style.display = "none";
        }
        if(editTab) editTab.classList.remove("on");
        if(previewTab) previewTab.classList.add("on");
      }else{
        if(previewEl){
          previewEl.classList.remove("on");
          previewEl.innerHTML = "";
        }
        if(notesTa) notesTa.style.display = "block";
        if(editTab) editTab.classList.add("on");
        if(previewTab) previewTab.classList.remove("on");
      }
    }
    if(editTab) editTab.addEventListener("click", ()=> setMode("edit"));
    if(previewTab) previewTab.addEventListener("click", ()=> setMode("preview"));

    let initialStatus = INIT.status || "New";
    let initialOwner  = INIT.owner || "";
    let initialNotes  = INIT.notes || (notesTa ? notesTa.value : "");

    let isSaving = false;
    let saveTimer = null;

    function getCurrentState(){
      return {
        status: statusSel ? statusSel.value : "",
        owner: ownerInput ? ownerInput.value : "",
        notes: notesTa ? notesTa.value : ""
      };
    }

    function isDirty(){
      const s = getCurrentState();
      return (s.status !== initialStatus) || (s.owner !== initialOwner) || (s.notes !== initialNotes);
    }

    function setSaveChip(state, label){
      if(!saveChip || !saveText) return;
      saveChip.classList.remove("saved","dirty","saving","failed");
      saveChip.classList.add(state);
      saveText.textContent = label;
    }

    function updateDirtyUI(){
      if(!authed || !canEdit) return;
      if(isSaving){
        setSaveChip("saving", "Saving…");
        return;
      }
      if(isDirty()){
        setSaveChip("dirty", "Unsaved changes");
      }else{
        setSaveChip("saved", "Saved");
      }
    }

    function scheduleAutosave(){
      if(!authed || !canEdit) return;
      updateDirtyUI();
      if(saveTimer) clearTimeout(saveTimer);
      saveTimer = setTimeout(()=> { autosaveIfDirty(); }, 800);
    }

    async function autosaveIfDirty(){
      if(!authed || !canEdit) return false;
      if(!isDirty()) { updateDirtyUI(); return true; }
      if(isSaving) return false;
      return await saveMeta({silent:true});
    }

    async function saveMeta(opts){
      const silent = opts && opts.silent;
      const sid = INIT.story_id;
      if(!sid) return false;

      const payload = {
        story_id: sid,
        status: (statusSel ? statusSel.value : "New"),
        owner: (ownerInput ? ownerInput.value : ""),
        notes: (notesTa ? notesTa.value : "")
      };

      isSaving = true;
      updateDirtyUI();

      const res = await postJSON("/api/meta/set", payload);
      isSaving = false;

      if(!res.ok){
        // NOTE: 403 might be RBAC (no permission) OR CSRF. We message both cleanly.
        const msg =
          (res.status === 401) ? "Login required" :
          (res.status === 403) ? "Blocked (permission or CSRF)" :
          "Save failed";
        setSaveChip("failed", msg);

        if(!silent){
          const t =
            (res.status === 401) ? "Auth required (login)." :
            (res.status === 403) ? "Blocked (permission or CSRF). Refresh, and make sure your role allows edits." :
            "Save failed.";
          toast(t);
        }
        return false;
      }

      initialStatus = payload.status;
      initialOwner  = payload.owner;
      initialNotes  = payload.notes;

      updateDirtyUI();
      if(!silent) toast("Saved");

      try{
        const meta = (res.data && res.data.meta) ? res.data.meta : null;
        const updatedUtc = meta ? (meta.updated_utc || "") : "";
        const by = meta ? (meta.updated_by_email || INIT.current_user_email) : INIT.current_user_email;
        if(lastUpdatedLine){
          if(updatedUtc){
            lastUpdatedLine.innerHTML =
              "Last updated " + relTimeFromIso(updatedUtc) +
              (by ? " · by <span class=\"mono\">" + escapeHtml(by) + "</span>" : "");
          }else{
            lastUpdatedLine.textContent = "Saved";
          }
        }
      }catch(e){}

      return true;
    }

    if(saveBtn) saveBtn.addEventListener("click", ()=> {
      if(!canEdit){ toast("No permission to edit."); return; }
      saveMeta({silent:false});
    });

    if(statusSel) statusSel.addEventListener("change", scheduleAutosave);
    if(ownerInput){
      ownerInput.addEventListener("input", scheduleAutosave);
      ownerInput.addEventListener("blur", autosaveIfDirty);
    }
    if(notesTa){
      notesTa.addEventListener("input", scheduleAutosave);
      notesTa.addEventListener("blur", autosaveIfDirty);
    }

    if(assignBtn){
      assignBtn.addEventListener("click", async function(){
        if(!canEdit){ toast("No permission to assign."); return; }
        const sid = INIT.story_id;
        if(!sid) return;

        setSaveChip("saving", "Assigning…");
        const res = await postJSON("/api/meta/assign_to_me", {story_id: sid});
        if(!res.ok){
          const msg =
            (res.status === 401) ? "Login required" :
            (res.status === 403) ? "Blocked (permission or CSRF)" :
            "Assign failed";
          setSaveChip("failed", msg);

          toast(
            (res.status === 401) ? "Auth required (login)." :
            (res.status === 403) ? "Blocked (permission or CSRF). Refresh, and make sure your role allows edits." :
            "Assign failed."
          );
          updateDirtyUI();
          return;
        }

        const email = INIT.current_user_email || "";
        if(ownerInput) ownerInput.value = email;

        initialOwner = email;
        updateDirtyUI();
        toast("Assigned to you");

        try{
          const meta = (res.data && res.data.meta) ? res.data.meta : null;
          const updatedUtc = meta ? (meta.updated_utc || "") : "";
          const by = meta ? (meta.updated_by_email || email) : email;
          if(lastUpdatedLine && updatedUtc){
            lastUpdatedLine.innerHTML =
              "Last updated " + relTimeFromIso(updatedUtc) +
              (by ? " · by <span class=\"mono\">" + escapeHtml(by) + "</span>" : "");
          }
        }catch(e){}
      });
    }

    // =============================
    // Lifecycle v2 (collapsed + grouped + humanized)
    // =============================
    const lifePreview = document.getElementById("lifePreview");
    const lifeFull = document.getElementById("lifeFull");
    const lifeToggleBtn = document.getElementById("lifeToggleBtn");
    const lifeCountPill = document.getElementById("lifeCountPill");
    const lifeHideNoise = document.getElementById("lifeHideNoise");

    function shortActor(email){
      const e = (email || "").trim();
      if(!e) return "system";
      return e.split("@",1)[0];
    }

    function humanAction(ev){
      const t = (ev.event_type || "").toLowerCase();
      const f = (ev.field || "").toLowerCase();

      if(f === "seen" || f === "reviewed"){
        if(t.includes("open")) return "Reviewed open";
        if(t.includes("toggle")) return "Reviewed toggled";
        return "Reviewed";
      }
      if(f === "status") return "Status changed";
      if(f === "owner"){
        if(t.includes("assigned_to_me")) return "Assigned to you";
        return "Owner changed";
      }
      if(f === "notes") return "Notes updated";
      return (t || "Updated").replaceAll("_"," ").replace(/\b\w/g, c => c.toUpperCase());
    }

    function humanValue(field, v){
      const f = (field || "").toLowerCase();
      const s = (v === null || v === undefined) ? "" : String(v).trim();

      // Fix "0 -> 1" reviewed display
      if(f === "seen" || f === "reviewed"){
        const low = s.toLowerCase();
        const truthy = new Set(["1","true","yes","y","on","reviewed"]);
        const falsy  = new Set(["0","false","no","n","off","","not reviewed"]);
        if(truthy.has(low)) return "Reviewed";
        if(falsy.has(low)) return "Not reviewed";
      }

      if(!s) return "—";
      return s;
    }

    function isNoisy(ev){
      const t = (ev.event_type || "").toLowerCase();
      const f = (ev.field || "").toLowerCase();
      if(f === "notes" && (t.includes("notes_updated") || t.includes("meta") || t.includes("updated"))) return true;
      return false;
    }

    function groupEvents(events){
      const out = [];
      for(const ev of events){
        const key = [ev.event_type||"", ev.field||"", ev.actor_email||""].join("|");
        const last = out.length ? out[out.length-1] : null;
        if(last && last._key === key){
          last._count += 1;
          last._items.push(ev);
        }else{
          out.push({_key:key, _count:1, _items:[ev]});
        }
      }
      return out;
    }

    function renderGroup(group){
      const first = group._items[0];
      const count = group._count;

      const field = (first.field || "").toLowerCase();
      const action = humanAction(first);
      const actor = shortActor(first.actor_email);
      const when = relTimeFromIso(first.ts_utc);

      const oldV = humanValue(first.field, first.old_value);
      const newV = humanValue(first.field, first.new_value);
      const detail = (first.field && (first.old_value || first.new_value)) ? `${oldV} → ${newV}` : "—";

      const chipClass =
        (field === "seen" || field === "reviewed") ? "good" :
        (field === "status" || field === "owner") ? "warn" : "";

      let detailsHtml = "";
      if(count > 1){
        const lines = group._items.map(it => {
          const o = humanValue(it.field, it.old_value);
          const n = humanValue(it.field, it.new_value);
          const w = relTimeFromIso(it.ts_utc);
          return `• ${w}: ${o} → ${n}`;
        }).join("\n");
        detailsHtml = `
          <details class="life-details">
            <summary>View ${count} changes</summary>
            <div class="life-mono" style="margin-top:10px;">${escapeHtml(lines)}</div>
          </details>
        `;
      }

      return `
        <div class="life-row">
          <div class="life-left">
            <div class="life-line1">
              <span class="life-chip ${chipClass}">${escapeHtml(action)}${count > 1 ? ` ×${count}` : ""}</span>
            </div>
            <div class="life-line2">${escapeHtml(detail)}</div>
            ${detailsHtml}
          </div>
          <div class="life-meta">
            <span>${escapeHtml(when || "")}</span>
            <span>·</span>
            <span>${escapeHtml(actor)}</span>
          </div>
        </div>
      `;
    }

    async function loadLifecycle(){
      if(!lifePreview || !lifeFull) return;

      if(!authed){
        lifePreview.innerHTML = `<div class="hint">Login to view lifecycle history.</div>`;
        if(lifeToggleBtn) lifeToggleBtn.disabled = true;
        if(lifeCountPill) lifeCountPill.textContent = "—";
        return;
      }

      const sid = INIT.story_id;
      const url = `/api/story/lifecycle?story_id=${encodeURIComponent(sid)}&limit=200`;

      const r = await fetch(url, {credentials:"same-origin"});
      if(!r.ok){
        lifePreview.innerHTML = `<div class="hint">Lifecycle unavailable (${r.status}).</div>`;
        if(lifeToggleBtn) lifeToggleBtn.disabled = true;
        if(lifeCountPill) lifeCountPill.textContent = "—";
        return;
      }

      const data = await r.json();
      let events = (data && data.events) ? data.events : [];
      if(!Array.isArray(events)) events = [];

      const hideNoise = lifeHideNoise ? lifeHideNoise.checked : true;
      const filtered = hideNoise ? events.filter(ev => !isNoisy(ev)) : events.slice();

      if(lifeCountPill) lifeCountPill.textContent = `${filtered.length} events`;

      if(filtered.length === 0){
        lifePreview.innerHTML = `<div class="hint">No lifecycle events yet.</div>`;
        lifeFull.innerHTML = "";
        if(lifeToggleBtn) lifeToggleBtn.disabled = true;
        return;
      }

      const grouped = groupEvents(filtered);

      lifePreview.innerHTML = grouped.slice(0,3).map(renderGroup).join("");
      lifeFull.innerHTML = grouped.map(renderGroup).join("");

      if(lifeToggleBtn) lifeToggleBtn.disabled = false;
    }

    if(lifeToggleBtn){
      lifeToggleBtn.addEventListener("click", ()=>{
        const open = (lifeFull.style.display !== "none");
        if(open){
          lifeFull.style.display = "none";
          lifeToggleBtn.setAttribute("aria-expanded","false");
          lifeToggleBtn.textContent = "View full history ▾";
        }else{
          lifeFull.style.display = "block";
          lifeToggleBtn.setAttribute("aria-expanded","true");
          lifeToggleBtn.textContent = "Hide full history ▴";
        }
      });
    }

    if(lifeHideNoise){
      lifeHideNoise.addEventListener("change", ()=> loadLifecycle());
    }

    // initial lifecycle load
    loadLifecycle();

    // Enterprise gating: since the editor controls may not exist in view-only mode,
    // do NOT force "Login to edit" here; the lockbox already communicates it.
    // We only initialize save chip state when we can actually edit.
    if(authed && canEdit){
      updateDirtyUI();
    }
  </script>
</body>
</html>
"""
