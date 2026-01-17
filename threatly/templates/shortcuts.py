SHORTCUTS_TEMPLATE = r"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Threatly • Keyboard Shortcuts</title>

  <style>
    :root{
      /* Admin-aligned enterprise palette */
      --bg0:#09090b;
      --bg1:#0b0b0f;
      --panel:#18181b;

      --border:#27272a;
      --text:#fafafa;
      --muted:#a1a1aa;

      --accent:#22c55e;

      --shadow: 0 18px 50px rgba(0,0,0,.55);

      /* Tight, enterprise density */
      --radius:6px;
      --radiusSm:4px;
      --fs:14px;
      --fsSmall:12px;
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

    .wrap{ max-width:960px; margin:0 auto; }

    a{
      color:var(--accent);
      text-decoration:none;
      font-weight:900;
    }
    a:hover{ text-decoration: underline; }

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
      font-size:22px;
      font-weight:980;
      letter-spacing:-.25px;
    }

    .sub{
      margin-top:6px;
      color: var(--muted);
      font-size:13px;
      font-weight:850;
    }

    .btn{
      display:inline-flex;
      align-items:center;
      gap:8px;
      padding:9px 11px;
      border-radius: var(--radiusSm);
      border:1px solid var(--border);
      background: rgba(255,255,255,.03);
      color:var(--text);
      font-weight:950;
      text-decoration:none;
      cursor:pointer;
      transition: border-color .12s ease, background .12s ease, transform .06s ease;
    }
    .btn:hover{
      border-color: rgba(34,197,94,.45);
      background: rgba(34,197,94,.08);
    }
    .btn:active{ transform: translateY(1px); }

    .grid{
      display:grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap:14px;
      margin-top:14px;
    }

    .card{
      border:1px solid var(--border);
      background: rgba(24,24,27,.55);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      padding:14px;
    }

    .card h2{
      margin:0 0 8px;
      font-size:12px;
      font-weight:950;
      letter-spacing:.10em;
      text-transform:uppercase;
      color: rgba(250,250,250,.85);
    }

    .row{
      display:flex;
      justify-content:space-between;
      align-items:center;
      gap:12px;
      padding:8px 0;
      border-bottom:1px solid rgba(255,255,255,.06);
      font-size:13px;
    }
    .row:last-child{ border-bottom:0; }

    .label{
      color: rgba(250,250,250,.92);
      font-weight:850;
    }

    .kbd{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
      font-size:12px;
      padding:4px 10px;
      border:1px solid rgba(255,255,255,.18);
      border-radius: var(--radiusSm);
      background: rgba(0,0,0,.35);
      color: rgba(250,250,250,.95);
      font-weight:900;
      white-space:nowrap;
    }

    .hint{
      margin-top:14px;
      padding:12px 14px;
      border-radius: var(--radius);
      border:1px solid var(--border);
      background: rgba(24,24,27,.55);
      color: rgba(250,250,250,.85);
      font-size:13px;
      font-weight:850;
      line-height:1.5;
    }
  </style>
</head>

<body>
  <div class="wrap">
    <div class="topbar">
      <div>
        <h1 class="title">Keyboard shortcuts</h1>
        <div class="sub">Designed for high-velocity SOC triage.</div>
      </div>
      <a class="btn" href="/">← Back to feed</a>
    </div>

    <div class="grid">
      <div class="card">
        <h2>Navigation</h2>
        <div class="row"><span class="label">Next story</span><span class="kbd">J</span></div>
        <div class="row"><span class="label">Previous story</span><span class="kbd">K</span></div>
        <div class="row"><span class="label">Open active story</span><span class="kbd">Enter</span></div>
      </div>

      <div class="card">
        <h2>Triage</h2>
        <div class="row"><span class="label">Toggle reviewed</span><span class="kbd">R</span></div>
        <div class="row"><span class="label">Set status → New</span><span class="kbd">1</span></div>
        <div class="row"><span class="label">Set status → Investigating</span><span class="kbd">2</span></div>
        <div class="row"><span class="label">Set status → Not Relevant</span><span class="kbd">3</span></div>
        <div class="row"><span class="label">Set status → Mitigated</span><span class="kbd">4</span></div>
      </div>

      <div class="card">
        <h2>Search & Focus</h2>
        <div class="row"><span class="label">Focus search</span><span class="kbd">/</span></div>
        <div class="row"><span class="label">Blur input</span><span class="kbd">Esc</span></div>
      </div>
    </div>

    <div class="hint">
      Tip: shortcuts work best in <strong>List View</strong> with one story focused — optimized for analysts clearing queues quickly.
    </div>
  </div>
</body>
</html>
"""
