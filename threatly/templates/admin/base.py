ADMIN_BASE_TEMPLATE = r"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{{ title }}</title>
  <style>
    :root{
      /* Zinc / Slate enterprise palette */
      --bg0:#09090b;      /* deep zinc */
      --bg1:#0b0b0f;
      --surface:#18181b;  /* cards */
      --surface2:#141417;
      --border:#27272a;
      --text:#fafafa;
      --muted:#a1a1aa;
      --muted2:#71717a;

      --accent:#22c55e;    /* green */
      --danger:#ef4444;    /* red */
      --warn:#f59e0b;      /* amber */

      --shadow: 0 10px 25px rgba(0,0,0,.40);

      /* tight radius */
      --r: 6px;
      --r2: 4px;

      /* density */
      --fs: 14px;
      --fsSmall: 12px;
    }

    *{ box-sizing:border-box; }
    html,body{ height:100%; }
    body{
      margin:0;
      font-family: Inter, -apple-system, BlinkMacSystemFont, system-ui, Segoe UI, Roboto, Arial, sans-serif;
      font-size: var(--fs);
      color:var(--text);
      background:
        radial-gradient(900px 600px at 20% -10%, rgba(34,197,94,.10), transparent 60%),
        radial-gradient(900px 600px at 110% 0%, rgba(59,130,246,.10), transparent 55%),
        linear-gradient(180deg, var(--bg0), var(--bg1));
    }
    a{ color:inherit; text-decoration:none; }

    .wrap{
      display:grid;
      grid-template-columns: 280px 1fr;
      min-height:100vh;
    }
    @media (max-width: 980px){
      .wrap{ grid-template-columns: 1fr; }
      .side{ position:static; height:auto; }
    }

    .side{
      position:sticky; top:0; height:100vh; overflow:auto;
      padding:14px;
      border-right:1px solid var(--border);
      background: linear-gradient(180deg, rgba(16,16,18,.92), rgba(12,12,14,.92));
    }

    .panel{
      border:1px solid var(--border);
      border-radius: var(--r);
      background: rgba(24,24,27,.70);
      box-shadow: var(--shadow);
    }

    .brand{ padding:12px; }
    .brand .title{
      font-weight:800; letter-spacing:.2px; font-size:14px;
      display:flex; align-items:center; justify-content:space-between; gap:10px;
      text-transform: none;
    }

    .muted{ color: var(--muted); font-weight:600; font-size: var(--fsSmall); margin-top:4px; }
    .muted2{ color: var(--muted2); font-weight:600; font-size: var(--fsSmall); }

    .pill{
      display:inline-flex; align-items:center; gap:8px;
      padding:4px 8px;
      border-radius: 999px;
      border:1px solid var(--border);
      background: rgba(255,255,255,.03);
      font-weight:700; font-size:12px;
      color: rgba(250,250,250,.92);
      white-space:nowrap;
    }
    .pill.good{ border-color: rgba(34,197,94,.35); background: rgba(34,197,94,.10); }
    .pill.warn{ border-color: rgba(245,158,11,.35); background: rgba(245,158,11,.10); }
    .pill.danger{ border-color: rgba(239,68,68,.35); background: rgba(239,68,68,.10); }

    .nav{
      margin-top:12px;
      display:flex; flex-direction:column; gap:8px;
    }
    .nav a{
      display:flex; align-items:center; justify-content:space-between; gap:10px;
      padding:10px 12px;
      border-radius: var(--r);
      border:1px solid var(--border);
      background: rgba(255,255,255,.02);
      font-weight:800;
      color: rgba(250,250,250,.92);
    }
    .nav a:hover{
      background: rgba(255,255,255,.03);
      border-color: rgba(255,255,255,.14);
    }
    .nav a.on{
      border-color: rgba(34,197,94,.45);
      background: rgba(34,197,94,.10);
    }
    .nav small{
      color: rgba(250,250,250,.55);
      font-weight:700;
      font-size: 12px;
    }

    .main{ padding:18px 18px 60px 18px; }

    .topbar{
      display:flex; align-items:center; justify-content:space-between; gap:12px;
      padding:12px 14px;
      border-radius: var(--r);
      border:1px solid var(--border);
      background: rgba(24,24,27,.55);
      box-shadow: var(--shadow);
    }
    .topbar .h{
      font-size:18px; font-weight:850; letter-spacing:-.2px;
    }

    /* Buttons (compact) */
    .btn{
      display:inline-flex; align-items:center; justify-content:center; gap:8px;
      padding:6px 10px;
      border-radius: var(--r2);
      border:1px solid var(--border);
      background: rgba(255,255,255,.03);
      color: var(--text);
      font-weight:800;
      cursor:pointer;
      font-size: 13px;
      line-height: 1;
      -webkit-appearance: none;
      appearance: none;
    }
    .btn:hover{ background: rgba(255,255,255,.05); }
    .btn.primary{ border-color: rgba(34,197,94,.45); background: rgba(34,197,94,.12); }
    .btn.danger{ border-color: rgba(239,68,68,.45); background: rgba(239,68,68,.12); }
    .btn.ghost{ background: transparent; }
    .btn:disabled{ opacity:.55; cursor:not-allowed; }

    /* Inputs (compact) */
    input, select, textarea{
      font-family: inherit;
      font-size: 13px;
      color: var(--text);
      background: rgba(255,255,255,.03);
      border: 1px solid var(--border);
      border-radius: var(--r2);
      padding: 7px 10px;
      outline: none;
      -webkit-appearance: none;
      appearance: none;
    }
    input::placeholder, textarea::placeholder{ color: rgba(250,250,250,.45); }
    input:focus, select:focus, textarea:focus{
      border-color: rgba(34,197,94,.45);
      box-shadow: 0 0 0 3px rgba(34,197,94,.12);
    }

    /* Cards */
    .card{
      margin-top:14px;
      padding:14px;
      border-radius: var(--r);
      border:1px solid var(--border);
      background: rgba(24,24,27,.55);
      box-shadow: var(--shadow);
    }

    /* Breadcrumbs */
    .crumbs{
      margin-top:10px;
      display:flex;
      gap:8px;
      align-items:center;
      flex-wrap:wrap;
      color: rgba(250,250,250,.55);
      font-weight:700;
      font-size: 12px;
    }
    .crumbs a{ color: rgba(250,250,250,.70); }
    .crumbs .sep{ color: rgba(250,250,250,.35); }

    /* Table */
    .table-wrap{
      margin-top:12px;
      border:1px solid var(--border);
      border-radius: var(--r);
      overflow: visible;
      background: rgba(10,10,12,.25);
    }

    table{
      width:100%;
      border-collapse: collapse;
      table-layout: auto;
      border-radius: var(--r);
      overflow: hidden;
    }

    td, th { overflow: visible; }

    thead th{
      text-align:left;
      font-size: 12px;
      color: rgba(250,250,250,.60);
      font-weight:800;
      letter-spacing:.2px;
      text-transform: uppercase;
      padding: 10px 12px;
      border-bottom: 1px solid var(--border);
      background: rgba(24,24,27,.55);
      position: sticky;
      top: 0;
      z-index: 2;
    }
    tbody td{
      padding: 10px 12px;
      border-bottom: 1px solid rgba(39,39,42,.65);
      vertical-align: top;
      font-size: 13px;
      color: rgba(250,250,250,.92);
    }
    tbody tr:hover{
      background: rgba(255,255,255,.03);
    }
    tbody tr:last-child td{ border-bottom: none; }

    /* Status dot */
    .dot{
      width:8px; height:8px; border-radius:999px; display:inline-block;
      background: rgba(250,250,250,.35);
    }
    .dot.ok{ background: rgba(34,197,94,.85); }
    .dot.warn{ background: rgba(245,158,11,.85); }
    .dot.bad{ background: rgba(239,68,68,.85); }

    /* Mono */
    .mono{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono","Courier New", monospace;
      font-size: 12px;
      color: rgba(250,250,250,.75);
    }
    .clip{
      overflow:hidden;
      text-overflow:ellipsis;
      white-space:nowrap;
      max-width: 100%;
    }
    .wrapany{
      overflow-wrap:anywhere;
      word-break:break-word;
    }

    /* Small badges */
    .badge{
      display:inline-flex;
      align-items:center;
      gap:8px;
      padding:4px 8px;
      border-radius:999px;
      border:1px solid var(--border);
      background: rgba(255,255,255,.02);
      font-weight:800;
      font-size: 12px;
      color: rgba(250,250,250,.92);
      white-space: nowrap;
    }
    .badge.code{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono","Courier New", monospace;
      font-size: 12px;
    }

    /* ===== Dropdown (button + JS, reliable) ===== */
    .dd{ position:relative; display:inline-block; }
    .dd-menu{
      position: fixed;
      left:-9999px;
      top:-9999px;
      max-height: 70vh;
      overflow: auto;
      min-width: 220px;
      border:1px solid var(--border);
      border-radius: var(--r);
      background: rgba(24,24,27,.98);
      box-shadow: 0 18px 40px rgba(0,0,0,.55);
      padding:6px;
      display:none;
      z-index: 9999;
    }
    .dd.open .dd-menu{ display:block; }

    .dd-item{
      display:flex;
      width:100%;
      justify-content:space-between;
      align-items:center;
      gap:10px;
      padding:8px 10px;
      border-radius: var(--r2);
      border:1px solid transparent;
      background: transparent;
      color: rgba(250,250,250,.92);
      font-weight:800;
      cursor:pointer;
      font-size: 13px;
      text-align:left;
    }
    .dd-item:hover{
      background: rgba(255,255,255,.05);
      border-color: rgba(255,255,255,.10);
    }
    .dd-item.danger{ color: rgba(239,68,68,.92); }
    .dd-sep{ height:1px; background: rgba(39,39,42,.75); margin:6px 0; }
  </style>
</head>
<body>
  <div class="wrap">
    <aside class="side">
      <div class="panel brand">
        <div class="title">
          <span>Threatly Admin</span>
          <span class="pill good">{{ me.get('role','?') }}</span>
        </div>
        <div class="muted">Signed in as {{ me.get('email','?') }}</div>
        <div style="margin-top:10px; display:flex; gap:10px; flex-wrap:wrap;">
          <a class="btn" href="/">← Back</a>
          <a class="btn ghost" href="/health">Health</a>
          <form method="post" action="/logout" style="margin:0;">
            <input type="hidden" name="csrf" value="{{ csrf_token|default('') }}">
            <button type="submit" class="btn danger">Logout</button>
          </form>

        </div>
      </div>

      <div class="nav">
        <a class="{% if active=='dashboard' %}on{% endif %}" href="/admin/">
          <span>Dashboard</span><small>overview</small>
        </a>
        {% if nav.can_manage_users %}
          <a class="{% if active=='users' %}on{% endif %}" href="/admin/users">
            <span>Users</span><small>provision</small>
          </a>
        {% endif %}
        <a class="{% if active=='roles' %}on{% endif %}" href="/admin/roles">
          <span>Roles</span><small>rbac</small>
        </a>
        <a class="{% if active=='audit' %}on{% endif %}" href="/admin/audit">
          <span>Audit</span><small>events</small>
        </a>
        <a class="{% if active=='settings' %}on{% endif %}" href="/admin/settings">
          <span>Settings</span><small>app</small>
        </a>
      </div>
    </aside>

    <main class="main">
      <div class="topbar">
        <div>
          <div class="h">{{ title }}</div>
          <div class="muted2">Enterprise controls · RBAC enforced</div>
          <div class="crumbs">
            <a href="/admin/">Admin</a>
            <span class="sep">/</span>
            <span>{{ title }}</span>
          </div>
        </div>
      </div>

      {{ content | safe }}
    </main>
  </div>

  <!-- ===== Dropdown logic for button-based menus ===== -->
  <script>
  (function(){
    function closeAll(exceptDd){
      document.querySelectorAll('[data-dd].open').forEach(dd => {
        if (exceptDd && dd === exceptDd) return;
        dd.classList.remove('open');
        const btn = dd.querySelector('[data-dd-trigger]');
        const menu = dd.querySelector('[data-dd-menu]');
        if (btn) btn.setAttribute('aria-expanded', 'false');
        if (menu){
          menu.style.left = '-9999px';
          menu.style.top  = '-9999px';
        }
      });
    }

    function position(dd){
      const btn = dd.querySelector('[data-dd-trigger]');
      const menu = dd.querySelector('[data-dd-menu]');
      if (!btn || !menu) return;

      const br = btn.getBoundingClientRect();
      const mw = menu.offsetWidth || 220;
      const mh = menu.offsetHeight || 200;

      const pad = 10;
      const spaceBelow = window.innerHeight - br.bottom;
      const spaceAbove = br.top;

      let top;
      if (spaceBelow >= mh + 8 || spaceBelow >= spaceAbove){
        top = br.bottom + 8;
      } else {
        top = Math.max(pad, br.top - mh - 8);
      }

      let left = br.right - mw;
      left = Math.max(pad, Math.min(left, window.innerWidth - mw - pad));

      menu.style.left = left + 'px';
      menu.style.top  = top + 'px';

      const maxH = Math.max(160, window.innerHeight - top - pad);
      menu.style.maxHeight = maxH + 'px';
      menu.style.overflow = 'auto';
    }

    document.addEventListener('click', function(e){
      // clicks inside menu shouldn't close it
      if (e.target.closest('[data-dd-menu]')) return;

      const trigger = e.target.closest('[data-dd-trigger]');
      if (trigger){
        e.preventDefault();
        e.stopPropagation();

        const dd = trigger.closest('[data-dd]');
        if (!dd) return;

        const willOpen = !dd.classList.contains('open');
        if (willOpen){
          closeAll(dd);
          dd.classList.add('open');
          trigger.setAttribute('aria-expanded', 'true');
          setTimeout(() => position(dd), 0);
        } else {
          dd.classList.remove('open');
          trigger.setAttribute('aria-expanded', 'false');
          const menu = dd.querySelector('[data-dd-menu]');
          if (menu){
            menu.style.left = '-9999px';
            menu.style.top  = '-9999px';
          }
        }
        return;
      }

      // outside click closes all
      closeAll();
    });

    document.addEventListener('keydown', function(e){
      if (e.key === 'Escape') closeAll();
    });

    window.addEventListener('resize', () => closeAll());
    window.addEventListener('scroll', () => closeAll(), true);
  })();
  </script>
</body>
</html>
"""
