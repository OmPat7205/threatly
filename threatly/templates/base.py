BASE_TEMPLATE = r"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Threatly</title>

  <style>
    :root{
      /* ===== Enterprise Zinc/Slate system (same as Admin) ===== */
      --bg0:#09090b;      /* deep zinc */
      --bg1:#0b0b0f;
      --surface:#18181b;  /* cards */
      --surface2:#141417;
      --border:#27272a;

      --text:#fafafa;
      --muted:#a1a1aa;
      --muted2:#71717a;

      --accent:#22c55e;   /* green */
      --danger:#ef4444;   /* red */
      --warn:#f59e0b;     /* amber */

      --shadow: 0 18px 60px rgba(0,0,0,.45);
      --shadow2: 0 10px 25px rgba(0,0,0,.40);

      /* Tight radius + density */
      --r: 6px;
      --r2: 4px;

      /* Typography base */
      --fs: 14px;
      --fsSmall: 12px;

      /* Controls */
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
      font-size: var(--fs);
      color:var(--text);
      background:
        radial-gradient(900px 600px at 20% -10%, rgba(34,197,94,.10), transparent 60%),
        radial-gradient(900px 600px at 110% 0%, rgba(59,130,246,.10), transparent 55%),
        linear-gradient(180deg, var(--bg0), var(--bg1));
    }
    body.compact{
      /* Compact mode scales (kept subtle, not tiny) */
      --fs: 13px;
      --fsSmall: 11px;
    }

    a{ color:inherit; text-decoration:none; }

    .wrap{
      display:grid;
      grid-template-columns: 320px 1fr;
      min-height:100vh;
    }
    @media (max-width: 980px){
      .wrap{ grid-template-columns: 1fr; }
      .sidebar{ position:static; height:auto; }
      .sidebar-wrap{ position:static !important; top:auto !important; }
    }

    /* ===== Sidebar ===== */
    .sidebar{
      position:sticky;
      top:0;
      height:100vh;
      overflow:auto;
      padding:14px;
      border-right:1px solid var(--border);
      background: linear-gradient(180deg, rgba(16,16,18,.92), rgba(12,12,14,.92));
    }
    body.compact .sidebar{ padding:12px; }

    .sidebar-wrap{ position: sticky; top: 14px; }
    body.compact .sidebar-wrap{ top: 12px; }

    .brand{
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap:12px;
      padding:12px 12px;
      border-radius: var(--r);
      border:1px solid var(--border);
      background: rgba(24,24,27,.70);
      box-shadow: var(--shadow2);
    }
    body.compact .brand{ padding:10px 10px; }

    .brand .title{
      font-weight:900;
      letter-spacing:.2px;
      font-size:16px;
    }
    body.compact .brand .title{ font-size:15px; }

    .pill{
      display:inline-flex;
      align-items:center;
      gap:8px;
      padding:4px 8px;
      border-radius:999px;
      border:1px solid var(--border);
      background: rgba(255,255,255,.03);
      color: rgba(250,250,250,.92);
      font-weight:800;
      font-size:12px;
      white-space:nowrap;
    }
    body.compact .pill{ font-size:11px; padding:3px 7px; }
    .pill.good{ border-color: rgba(34,197,94,.35); background: rgba(34,197,94,.10); }
    .pill.warn{ border-color: rgba(245,158,11,.35); background: rgba(245,158,11,.10); }
    .pill.danger{ border-color: rgba(239,68,68,.35); background: rgba(239,68,68,.10); }

    .section{
      margin-top:12px;
      padding:12px;
      border-radius: var(--r);
      border:1px solid var(--border);
      background: rgba(24,24,27,.55);
      box-shadow: var(--shadow2);
    }
    body.compact .section{ padding:10px; margin-top:10px; }

    .section h3{
      margin:0 0 10px 0;
      font-size:12px;
      letter-spacing:.12em;
      text-transform:uppercase;
      color: rgba(250,250,250,.60);
      font-weight:900;
    }
    body.compact .section h3{ font-size:11px; margin-bottom:8px; }

    .row{
      display:flex;
      gap:10px;
      align-items:center;
      flex-wrap:wrap;
    }
    body.compact .row{ gap:8px; }

    /* ===== Inputs (unified) ===== */
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
    body.compact input, body.compact select, body.compact textarea{
      font-size:12px;
      padding:6px 9px;
    }
    input::placeholder, textarea::placeholder{ color: rgba(250,250,250,.45); }
    input:focus, select:focus, textarea:focus{
      border-color: var(--ctl-border-focus);
      box-shadow: 0 0 0 3px rgba(34,197,94,.12);
    }
    .input, .select{ width:100%; } /* keep your existing class usage */

    /* ===== Buttons (compact + consistent) ===== */
    .btn{
      display:inline-flex;
      align-items:center;
      justify-content:center;
      gap:8px;
      padding:6px 10px;
      border-radius: var(--r2);
      border:1px solid var(--border);
      background: rgba(255,255,255,.03);
      color: var(--text);
      font-weight:850;
      cursor:pointer;
      user-select:none;
      transition: background .12s ease, border-color .12s ease, transform .06s ease, opacity .12s ease;
      font-size: 13px;
      line-height: 1;
    }
    .btn:hover{ background: rgba(255,255,255,.05); border-color: rgba(255,255,255,.14); }
    .btn:active{ transform: translateY(1px); }
    .btn.primary{ border-color: rgba(34,197,94,.45); background: rgba(34,197,94,.12); }
    .btn.ghost{ background: transparent; }
    .btn.danger{ border-color: rgba(239,68,68,.45); background: rgba(239,68,68,.12); }
    .btn:disabled{ opacity:.55; cursor:not-allowed; transform:none; }

    .btn.small{
      padding:5px 8px;
      font-size:12px;
      border-radius: 999px;
    }
    body.compact .btn{ font-size:12px; padding:5px 9px; }
    body.compact .btn.small{ font-size:11px; padding:4px 8px; }

    /* ===== Compact toggle chip ===== */
    .mode-chip{
      display:inline-flex;
      align-items:center;
      gap:8px;
      padding:5px 9px;
      border-radius:999px;
      border:1px solid rgba(255,255,255,.10);
      background: rgba(255,255,255,.03);
      color: rgba(250,250,250,.86);
      font-weight:900;
      font-size:12px;
      cursor:pointer;
      user-select:none;
      transition: background .12s ease, border-color .12s ease, transform .06s ease;
    }
    .mode-chip:hover{
      background: rgba(255,255,255,.05);
      border-color: rgba(255,255,255,.14);
    }
    .mode-chip:active{ transform: translateY(1px); }
    .mode-chip .dotx{
      width:8px; height:8px; border-radius:999px;
      background: rgba(161,161,170,.95);
      box-shadow: 0 0 0 4px rgba(161,161,170,.12);
    }
    .mode-chip.on{
      border-color: rgba(34,197,94,.40);
      background: rgba(34,197,94,.10);
      color: rgba(250,250,250,.95);
    }
    .mode-chip.on .dotx{
      background: rgba(34,197,94,.95);
      box-shadow: 0 0 0 4px rgba(34,197,94,.14);
    }
    body.compact .mode-chip{ font-size:11px; padding:4px 8px; }

    /* ===== User menu dropdown (reliable, closes on outside click) ===== */
    .user-menu{ position: relative; display:flex; align-items:center; gap:8px; }
    .user-btn{
      display:inline-flex;
      align-items:center;
      gap:8px;
      padding:6px 8px;
      border-radius:999px;
      border:1px solid var(--border);
      background: rgba(255,255,255,.03);
      cursor:pointer;
      user-select:none;
      font-weight:900;
    }
    .user-btn:hover{ background: rgba(255,255,255,.05); border-color: rgba(255,255,255,.14); }
    .user-initials{
      display:inline-flex;
      align-items:center;
      justify-content:center;
      width:28px;
      height:28px;
      border-radius:999px;
      border:1px solid rgba(34,197,94,.35);
      background: rgba(34,197,94,.12);
      font-weight:950;
    }
    body.compact .user-initials{ width:26px; height:26px; }
    .caret{ opacity:.85; font-weight:950; transform: translateY(-1px); }

    .menu{
      position:absolute;
      right:0;
      top:44px;
      width:240px;
      border-radius: var(--r);
      border:1px solid var(--border);
      background: rgba(24,24,27,.98);
      box-shadow: 0 18px 40px rgba(0,0,0,.55);
      padding:8px;
      display:none;
      z-index:9999;
    }
    .menu.on{ display:block; }
    .menu .hdr{
      padding:10px 10px 8px 10px;
      border-bottom:1px solid rgba(255,255,255,.06);
      margin-bottom:6px;
    }
    .menu .hdr .email{
      font-weight:900;
      font-size:13px;
      color: rgba(250,250,250,.92);
      overflow:hidden;
      text-overflow:ellipsis;
      white-space:nowrap;
    }
    .menu .hdr .muted{
      margin-top:2px;
      font-size:12px;
      color: rgba(250,250,250,.60);
      font-weight:800;
    }
    .menu a{
      display:flex;
      align-items:center;
      gap:10px;
      padding:10px 10px;
      border-radius: var(--r2);
      font-weight:900;
      color: rgba(250,250,250,.92);
      border:1px solid transparent;
    }
    .menu a:hover{
      background: rgba(255,255,255,.05);
      border-color: rgba(255,255,255,.10);
    }
    .menu .sep{
      height:1px;
      background: rgba(255,255,255,.06);
      margin:6px 0;
    }

        /* Make a POST logout button look like the dropdown links */
    .menu-link-btn{
      width:100%;
      display:flex;
      align-items:center;
      gap:10px;
      padding:10px 10px;
      border-radius: var(--r2);
      font-weight:900;
      color: rgba(250,250,250,.92);
      border:1px solid transparent;
      background: transparent;
      cursor:pointer;
      text-align:left;
      font-family: inherit;
      font-size: inherit;
    }
    .menu-link-btn:hover{
      background: rgba(255,255,255,.05);
      border-color: rgba(255,255,255,.10);
    }


    /* Sources */
    .source-list{ display:flex; flex-direction:column; gap:8px; margin-top:10px; }
    body.compact .source-list{ gap:7px; margin-top:8px; }

    .source-item{
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap:10px;
      padding:9px 10px;
      border-radius: var(--r2);
      border:1px solid var(--border);
      background: rgba(255,255,255,.02);
      cursor:pointer;
      transition: border-color .12s ease, background .12s ease;
    }
    body.compact .source-item{ padding:8px 9px; }

    .source-item:hover{
      border-color: rgba(255,255,255,.14);
      background: rgba(255,255,255,.03);
    }
    .source-left{ display:flex; align-items:center; gap:10px; min-width:0; }
    .dot{
      width:10px; height:10px;
      border-radius:50%;
      border:1px solid rgba(255,255,255,.22);
      background: rgba(255,255,255,.05);
      flex:0 0 auto;
    }
    .dot.on{
      border-color: rgba(34,197,94,.60);
      background: rgba(34,197,94,.85);
      box-shadow: 0 0 0 4px rgba(34,197,94,.10);
    }
    .source-name{
      font-weight:900;
      color: rgba(250,250,250,.92);
      white-space:nowrap;
      overflow:hidden;
      text-overflow:ellipsis;
      font-size:13px;
    }
    body.compact .source-name{ font-size:12px; }

    .count{
      font-variant-numeric: tabular-nums;
      color: rgba(250,250,250,.70);
      font-weight:900;
      background: rgba(255,255,255,.03);
      border:1px solid rgba(255,255,255,.08);
      padding:5px 9px;
      border-radius:999px;
      font-size:12px;
      white-space:nowrap;
    }
    body.compact .count{ font-size:11px; padding:4px 8px; }

    /* Categories */
    .chips{ display:flex; flex-wrap:wrap; gap:8px; margin-top:10px; }
    body.compact .chips{ gap:7px; margin-top:8px; }

    .chip-link{
      display:inline-flex;
      align-items:center;
      gap:8px;
      padding:7px 9px;
      border-radius:999px;
      border:1px solid var(--border);
      background: rgba(255,255,255,.03);
      color: rgba(250,250,250,.86);
      font-weight:900;
      font-size:12px;
      cursor:pointer;
      transition: border-color .12s ease, background .12s ease;
      max-width:100%;
    }
    body.compact .chip-link{ font-size:11px; padding:6px 8px; }

    .chip-link:hover{
      border-color: rgba(255,255,255,.14);
      background: rgba(255,255,255,.05);
    }
    .chip-link.on{
      border-color: rgba(34,197,94,.45);
      background: rgba(34,197,94,.12);
      color: rgba(250,250,250,.95);
    }

    /* ===== Premium filter panel (kept, re-skinned) ===== */
    .fpanel{
      margin-top:12px;
      padding:14px;
      border-radius: var(--r);
      border: 1px solid var(--border);
      background: rgba(24,24,27,.70);
      box-shadow: var(--shadow2);
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
    }
    body.compact .fpanel{ padding:12px; margin-top:10px; }

    .fhead{
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap:10px;
      margin-bottom: 12px;
    }
    body.compact .fhead{ margin-bottom:10px; }

    .fhead .ttl{
      margin:0;
      letter-spacing: 0.12em;
      font-size: 12px;
      font-weight: 900;
      text-transform:uppercase;
      color: rgba(250,250,250,.60);
    }
    body.compact .fhead .ttl{ font-size:11px; }

    .fclear{
      font-size: 12px;
      color: rgba(250,250,250,.70);
      text-decoration: none;
      padding: 6px 10px;
      border-radius: 999px;
      border: 1px solid rgba(255,255,255,0.10);
      background: rgba(255,255,255,0.03);
      font-weight:900;
    }
    body.compact .fclear{ font-size:11px; padding:5px 9px; }

    .fclear:hover{
      background: rgba(255,255,255,0.05);
      border-color: rgba(255,255,255,0.14);
    }

    .fsection{ padding: 12px 0; border-top: 1px solid rgba(255,255,255,0.06); }
    .fsection:first-of-type{ border-top:0; padding-top: 6px; }
    body.compact .fsection{ padding:10px 0; }

    .flabel{
      font-size: 12px;
      color: rgba(250,250,250,.60);
      font-weight: 900;
      margin-bottom: 8px;
      display:flex;
      align-items:center;
      justify-content:space-between;
      letter-spacing:.02em;
    }
    body.compact .flabel{ font-size:11px; margin-bottom:7px; }

    .chip-grid{ display:grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    body.compact .chip-grid{ gap:8px; }

    .fchip{
      border: 1px solid rgba(255,255,255,0.10);
      background: rgba(255,255,255,0.03);
      color: rgba(250,250,250,.92);
      padding: 10px 12px;
      border-radius: 999px;
      font-size: 13px;
      font-weight: 900;
      display:flex;
      align-items:center;
      justify-content:space-between;
      gap: 10px;
      transition: transform 0.08s ease, background 0.12s ease, border-color 0.12s ease;
      min-width: 0;
    }
    body.compact .fchip{ font-size:12px; padding:9px 11px; }
    .fchip:hover{
      background: rgba(255,255,255,0.05);
      border-color: rgba(255,255,255,0.14);
    }
    .fchip:active{ transform: translateY(1px); }
    .fchip.on{
      background: rgba(34,197,94,.12);
      border-color: rgba(34,197,94,.45);
      color: rgba(250,250,250,.98);
    }

    .fcontrol select{
      width: 100%;
      height: 40px;
      border-radius: var(--r2);
      border: 1px solid rgba(255,255,255,0.10);
      background: rgba(255,255,255,0.03);
      color: rgba(250,250,250,0.92);
      padding: 0 12px;
      font-size: 13px;
      font-weight: 900;
      outline: none;
      color-scheme: dark;
    }
    body.compact .fcontrol select{
      height: 38px;
      font-size: 12px;
    }
    .fcontrol select:hover{
      border-color: rgba(255,255,255,0.14);
      background: rgba(255,255,255,0.04);
    }
    .fcontrol select:focus{
      border-color: rgba(34,197,94,.45);
      box-shadow: 0 0 0 3px rgba(34,197,94,.12);
    }

          /* KPI cards as links */
          .kpi-link{
            display:block;
            text-decoration:none;
            color: inherit;
          }
          .kpi-link:focus{
            outline: none;
          }
          .kpi-link:focus .kpi{
            box-shadow: 0 0 0 3px rgba(34,197,94,.18), var(--shadow2);
            border-color: rgba(34,197,94,.35);
          }


    
        /* ===== User KPI strip (Phase 2) ===== */
        .kpi-strip{
          margin-top: 14px;
          display:grid;
          grid-template-columns: repeat(5, minmax(150px, 1fr));
          gap: 12px;
        }
        @media (max-width: 1200px){
          .kpi-strip{ grid-template-columns: repeat(3, minmax(150px, 1fr)); }
        }
        @media (max-width: 820px){
          .kpi-strip{ grid-template-columns: repeat(2, minmax(150px, 1fr)); }
        }

        .kpi{
          border: 1px solid rgba(255,255,255,.10);
          background: rgba(24,24,27,.55);
          border-radius: var(--r);
          box-shadow: var(--shadow2);
          padding: 12px 12px 10px;
          min-width: 0;
        }
        .kpi .k{
          font-size: 12px;
          letter-spacing: .12em;
          text-transform: uppercase;
          color: rgba(250,250,250,.60);
          font-weight: 950;
        }
        .kpi .v{
          margin-top: 8px;
          font-size: 22px;
          font-weight: 980;
          letter-spacing: -.3px;
          font-variant-numeric: tabular-nums;
        }
        .kpi .s{
          margin-top: 6px;
          font-size: 12px;
          color: rgba(250,250,250,.62);
          font-weight: 850;
          line-height: 1.35;
        }

        /* optional “risk tint” */
        .kpi.good{ border-color: rgba(34,197,94,.25); }
        .kpi.warn{ border-color: rgba(245,158,11,.28); }
        .kpi.danger{ border-color: rgba(239,68,68,.30); }



    /* ===== Main ===== */
    .main{ padding:20px 20px 60px 20px; }
    body.compact .main{ padding:16px 16px 52px 16px; }

    .headline{
      display:flex;
      align-items:flex-end;
      justify-content:space-between;
      gap:14px;
      flex-wrap:wrap;
    }
    .headline h1{
      margin:0;
      font-size:22px;
      letter-spacing:-.3px;
      font-weight:950;
    }
    body.compact .headline h1{ font-size:20px; }

    .sub{
      color: rgba(250,250,250,.60);
      font-weight:800;
      margin-top:6px;
      font-size:13px;
    }
    body.compact .sub{ font-size:12px; }

    .active-filter-bar{
      margin-top:12px;
      display:flex;
      flex-wrap:wrap;
      gap:10px;
      align-items:center;
    }
    body.compact .active-filter-bar{ margin-top:10px; gap:8px; }

    .filter-pill{
      display:inline-flex;
      align-items:center;
      gap:10px;
      padding:7px 9px;
      border-radius:999px;
      border:1px solid rgba(255,255,255,.10);
      background: rgba(255,255,255,.03);
      font-weight:900;
      color: rgba(250,250,250,.88);
      max-width:100%;
      font-size:12px;
    }
    body.compact .filter-pill{ font-size:11px; padding:6px 8px; gap:8px; }

    .filter-pill .x{
      opacity:.75;
      cursor:pointer;
      font-weight:950;
    }

    .list{
      margin-top:16px;
      display:flex;
      flex-direction:column;
      gap:14px;
    }
    body.compact .list{ margin-top:12px; gap:12px; }

    /* ===== Story cards (kept, re-skinned) ===== */
    .story-card{
      position:relative;
      overflow:hidden;
      border:1px solid var(--border);
      background: rgba(24,24,27,.55);
      border-radius: var(--r);
      box-shadow: var(--shadow2);
    }
    .story-card:hover{
      border-color: rgba(255,255,255,.14);
      box-shadow: 0 14px 38px rgba(0,0,0,.42);
    }

    .sev-bar{ position:absolute; left:0; top:0; bottom:0; width:6px; opacity:.95; }
    .sev-low{ background: rgba(59,130,246,.80); }
    .sev-medium{ background: rgba(245,158,11,.90); }
    .sev-high{ background: rgba(239,68,68,.88); }
    .sev-critical{ background: rgba(239,68,68,.98); }

    .story-grid{
      display:grid;
      grid-template-columns: 170px 1fr 260px;
      gap:14px;
      padding:16px 16px 12px 16px;
    }
    body.compact .story-grid{
      gap:12px;
      padding:14px 14px 10px 14px;
    }

    @media (max-width: 980px){
      .story-grid{ grid-template-columns: 1fr; }
      .story-right{ justify-self:start !important; align-items:flex-start !important; }
    }

    .story-left{
      display:flex;
      flex-direction:column;
      gap:10px;
      padding-left:8px;
    }
    body.compact .story-left{ gap:8px; }

    /* ===== FIX: Source pill should NOT cut off (wrap to 2 lines, tidy) ===== */
    .source-pill2{
      display:-webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow:hidden;
      white-space:normal;
      line-height:1.25;
      align-items:flex-start;
    }

    .source-pill2, .sev-pill2{
      display:inline-flex;
      align-items:center;
      gap:10px;
      padding:9px 10px;
      border-radius: var(--r2);
      background: rgba(255,255,255,.03);
      border:1px solid rgba(255,255,255,.08);
      font-weight:900;
      letter-spacing:.2px;
      font-size:13px;
      max-width:100%;
    }
    body.compact .source-pill2, body.compact .sev-pill2{
      padding:8px 9px;
      font-size:12px;
    }

    .sev-pill2{ width:100%; }
    .sev-pill2 .sev-score{ margin-left:auto; font-variant-numeric: tabular-nums; opacity:.9; }

    .why{
      display:inline-flex;
      align-items:center;
      gap:10px;
      padding:9px 10px;
      border-radius: var(--r2);
      border:1px solid rgba(34,197,94,.35);
      background: rgba(34,197,94,.12);
      color: rgba(250,250,250,.95);
      font-weight:900;
      cursor:default;
      font-size:13px;
    }
    body.compact .why{ padding:8px 9px; font-size:12px; }

    .story-main{ min-width:0; }

    /* Typography tweak: title slightly smaller + tighter tracking */
    .story-title{
      margin:0;
      font-size:21px;
      line-height:1.12;
      letter-spacing:-.25px;
      font-weight:950;
    }
    body.compact .story-title{ font-size:19px; }

    .story-title a:hover{
      text-decoration: underline;
      text-decoration-color: rgba(34,197,94,.65);
    }

    .chip-row{ display:flex; flex-wrap:wrap; gap:10px; margin-top:10px; }
    body.compact .chip-row{ gap:8px; margin-top:8px; }

    .chip{
      display:inline-flex;
      align-items:center;
      gap:8px;
      padding:7px 9px;
      border-radius:999px;
      background: rgba(255,255,255,.03);
      border:1px solid rgba(255,255,255,.08);
      color: rgba(250,250,250,.92);
      font-weight:900;
      font-size:13px;
      max-width:100%;
    }
    body.compact .chip{ font-size:12px; padding:6px 8px; gap:7px; }

    .chip strong{ color: var(--text); font-weight:950; }
    .chip.good{ border-color: rgba(34,197,94,.35); background: rgba(34,197,94,.12); }
    .chip.warn{ border-color: rgba(245,158,11,.35); background: rgba(245,158,11,.12); }
    .chip.muted{ color: rgba(250,250,250,.70); font-weight:900; }

    /* Typography tweak: summary slightly smaller + better line-height */
    .story-summary{
      margin-top:12px;
      color: rgba(250,250,250,.86);
      line-height:1.52;
      font-size:14px;
      max-width: 980px;
      white-space: normal;
      overflow-wrap:anywhere;
    }
    body.compact .story-summary{
      margin-top:10px;
      font-size:13px;
      line-height:1.48;
    }

    .summary-clamp{
      display:-webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
      overflow:hidden;
    }
    body.compact .summary-clamp{ -webkit-line-clamp: 2; }

    .expand-btn{
      margin-top:9px;
      display:inline-flex;
      align-items:center;
      gap:8px;
      cursor:pointer;
      color: rgba(34,197,94,.95);
      font-weight:900;
      user-select:none;
      font-size:13px;
    }
    body.compact .expand-btn{ font-size:12px; margin-top:8px; }
    .expand-btn:hover{ text-decoration:underline; }

    .story-right{
      justify-self:end;
      display:flex;
      flex-direction:column;
      align-items:flex-end;
      gap:10px;
    }
    body.compact .story-right{ gap:8px; }

    .kv{ display:flex; flex-wrap:wrap; gap:10px; justify-content:flex-end; }
    body.compact .kv{ gap:8px; }

    .kv-pill{
      padding:7px 9px;
      border-radius:999px;
      background: rgba(255,255,255,.03);
      border:1px solid rgba(255,255,255,.08);
      color: rgba(250,250,250,.75);
      font-weight:900;
      font-size:12px;
      font-variant-numeric: tabular-nums;
    }
    body.compact .kv-pill{ font-size:11px; padding:6px 8px; }

    .actions-row{
      display:flex;
      gap:10px;
      padding: 0 16px 14px 16px;
      align-items:center;
      flex-wrap:wrap;
      border-top:1px solid rgba(255,255,255,.06);
      background: rgba(0,0,0,.10);
    }
    body.compact .actions-row{
      gap:8px;
      padding: 0 14px 12px 14px;
    }
    .actions-row select{ border-radius: var(--r2); }

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
      bottom: 12px;
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
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
    }
    .bulkbar.on{ display:flex; }
    .bulkbar .spacer{ flex:1; }
    .bulkbar .meta{
      font-weight: 950;
      color: rgba(250,250,250,.92);
      white-space: nowrap;
    }
    .bulkbar select{
      height: 36px;
      font-weight: 900;
    }

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
  </style>
</head>

<body>
  {% set days = (days|default(7))|int %}
  <div class="wrap">
    <!-- SIDEBAR -->
    <aside class="sidebar">
      <div class="sidebar-wrap">
        <div class="brand">
          <div>
            <div class="title">Threatly</div>

            <div style="margin-top:6px; display:flex; gap:8px; flex-wrap:wrap; align-items:center;">
              {% if kev_status %}
                <span class="pill {% if kev_status == 'OK' %}good{% else %}warn{% endif %}">KEV: {{ kev_status }}</span>
              {% endif %}
              {% if auth_require_login %}
                <span class="pill">Auth: required</span>
              {% endif %}

              {# ===== Delta indicator badge (shows only when Delta filter is ON) ===== #}
              {% if delta == '1' and (delta_new_count|default(0))|int > 0 %}
                <span class="pill good" title="New items in this window vs prior window">New: {{ (delta_new_count|default(0))|int }}</span>
              {% elif delta == '1' %}
                <span class="pill" title="No new items in this window vs prior window">New: 0</span>
              {% endif %}

              <!-- Compact mode toggle (client-side only) -->
              <button class="mode-chip" id="compactToggle" type="button" title="Toggle compact density">
                <span class="dotx" id="compactDot"></span>
                <span id="compactLabel">Compact</span>
              </button>
            </div>
          </div>

          <div style="display:flex; gap:8px; align-items:center;">
            {% set _can_view_admin = (can_view_admin|default(false)) %}
            {% set _can_export = (can_export_reports|default(false)) %}
            {% if is_authed %}
              <div class="user-menu" id="userMenu">
                <div class="user-btn" id="userBtn" title="{{ current_user_email }}">
                  <span class="user-initials">{{ current_user_initials }}</span>
                  <span class="caret">▾</span>
                </div>
                <div class="menu" id="userDropdown">
                  <div class="hdr">
                    <div class="email">{{ current_user_email }}</div>
                    <div class="muted">
                      {% if _can_view_admin %}Admin{% else %}User{% endif %}
                    </div>
                  </div>

                  <a href="/">🏠 Feed</a>
                  <a href="/shortcuts">⚡ Shortcuts</a>

                  {% if _can_export %}
                    <div class="sep"></div>
                    <a href="/daily">🧾 Daily report</a>
                    <a href="/export.csv?{{ qs({}) }}">📤 Export CSV</a>
                  {% endif %}

                  {% if _can_view_admin %}
                    <div class="sep"></div>
                    <a href="{{ url_for('admin.admin_home') }}">🛠️ Admin</a>
                  {% endif %}

                  <div class="sep"></div>
                  <a href="/health">🩺 Health</a>
                  <form method="post" action="/logout" style="margin:0;">
                    <input type="hidden" name="csrf" value="{{ csrf_token|default('') }}">

                    <button type="submit" class="menu-link-btn">🚪 Logout</button>
                  </form>

                </div>
              </div>
            {% else %}
              <a class="btn primary" href="/login">Login</a>
            {% endif %}
          </div>
        </div>

        <!-- Search -->
        <div class="section">
          <h3>Search</h3>
          <form method="get" action="/" style="display:flex; gap:10px;">
            <input class="input" name="q" value="{{ q }}" placeholder="Search titles + summaries…" />
            <!-- keep current params via hidden -->
            <input type="hidden" name="sort" value="{{ sort }}">
            <input type="hidden" name="days" value="{{ (days|default(7))|int }}">
            <input type="hidden" name="min_sources" value="{{ min_sources }}">
            <input type="hidden" name="view" value="{{ view }}">
            {% if selected_sources and selected_sources|length > 0 %}
              <input type="hidden" name="sources" value="{{ selected_sources|join(',') }}">
            {% endif %}
            {% if selected_cats and selected_cats|length > 0 %}
              <input type="hidden" name="cat" value="{{ selected_cats|join(',') }}">
            {% endif %}
            {% if sev_min %}<input type="hidden" name="sev_min" value="{{ sev_min }}">{% endif %}
            {% if kev %}<input type="hidden" name="kev" value="{{ kev }}">{% endif %}
            {% if has_iocs %}<input type="hidden" name="has_iocs" value="{{ has_iocs }}">{% endif %}
            {% if reviewed_filter %}<input type="hidden" name="seen" value="{{ reviewed_filter }}">{% endif %}
            {% if status_filter %}<input type="hidden" name="status" value="{{ status_filter }}">{% endif %}
            {% if stack_filter %}<input type="hidden" name="stack" value="{{ stack_filter }}">{% endif %}
            {% if exclude %}<input type="hidden" name="exclude" value="{{ exclude }}">{% endif %}
            {% if include_kw %}<input type="hidden" name="kw" value="{{ include_kw }}">{% endif %}
            {% if delta %}<input type="hidden" name="delta" value="{{ delta }}">{% endif %}
            <button class="btn primary" type="submit">Go</button>
          </form>

          <div class="row" style="margin-top:10px;">
            <a class="btn ghost" href="/?{{ qs_clear_all() }}">Clear all</a>

            {% if (can_export_reports|default(false)) %}
              <a class="btn ghost" href="/export.csv?{{ qs({}) }}">Export CSV</a>
              <a class="btn ghost" href="/daily">Daily</a>
            {% endif %}

            <a class="btn ghost" href="/health">Health</a>
          </div>
        </div>

        <!-- PREMIUM FILTER PANEL -->
        <div class="fpanel">
          <div class="fhead">
            <div class="ttl">Filters</div>
            <a class="fclear" href="/?{{ qs_clear_all() }}">Clear</a>
          </div>

          <div class="fsection">
            <div class="flabel">Quick filters</div>
            <div class="chip-grid">
              <a class="fchip {% if delta == '1' %}on{% endif %}" href="/?{{ qs({'delta': '' if delta == '1' else '1'}) }}">
                <span>Delta (24h)</span>
                <span class="count">{{ (filter_counts.delta|default(0))|int }}</span>
              </a>

              <a class="fchip {% if stack_filter == '1' %}on{% endif %}" href="/?{{ qs({'stack': '' if stack_filter == '1' else '1'}) }}">
                <span>Relevant</span>
                <span class="count">{{ (filter_counts.relevant|default(0))|int }}</span>
              </a>

              <a class="fchip {% if kev == '1' %}on{% endif %}" href="/?{{ qs({'kev': '' if kev == '1' else '1'}) }}">
                <span>KEV only</span>
                <span class="count">{{ (filter_counts.kev|default(0))|int }}</span>
              </a>

              <a class="fchip {% if has_iocs == '1' %}on{% endif %}" href="/?{{ qs({'has_iocs': '' if has_iocs == '1' else '1'}) }}">
                <span>Has IOCs</span>
                <span class="count">{{ (filter_counts.has_iocs|default(0))|int }}</span>
              </a>

              <a class="fchip {% if sev_min == 'High' %}on{% endif %}" href="/?{{ qs({'sev_min': '' if sev_min == 'High' else 'High'}) }}">
                <span>High+</span>
                <span class="count">{{ (filter_counts.high_plus|default(0))|int }}</span>
              </a>

              <a class="fchip {% if sev_min == 'Critical' %}on{% endif %}" href="/?{{ qs({'sev_min': '' if sev_min == 'Critical' else 'Critical'}) }}">
                <span>Critical</span>
                <span class="count">{{ (filter_counts.critical|default(0))|int }}</span>
              </a>

              <a class="fchip {% if reviewed_filter == 'hide' %}on{% endif %}" href="/?{{ qs({'seen': '' if reviewed_filter == 'hide' else 'hide'}) }}">
                <span>Hide reviewed</span>
                <span class="count">{{ (filter_counts.reviewed_hide|default(0))|int }}</span>
              </a>

              <a class="fchip {% if reviewed_filter == 'only' %}on{% endif %}" href="/?{{ qs({'seen': '' if reviewed_filter == 'only' else 'only'}) }}">
                <span>Reviewed only</span>
                <span class="count">{{ (filter_counts.reviewed_only|default(0))|int }}</span>
              </a>
            </div>
          </div>

          <div class="fsection">
            <div class="flabel">Time range</div>
            <div class="fcontrol">
              <select onchange="location.href='/?' + this.value;">
                <option value="{{ qs({'days': 1}) }}" {% if days == 1 %}selected{% endif %}>Last 1 day</option>
                <option value="{{ qs({'days': 7}) }}" {% if days == 7 %}selected{% endif %}>Last 7 days</option>
                <option value="{{ qs({'days': 30}) }}" {% if days == 30 %}selected{% endif %}>Last 30 days</option>
              </select>
            </div>
          </div>

          <div class="fsection">
            <div class="flabel">Sort</div>
            <div class="fcontrol">
              <select onchange="location.href='/?' + this.value;">
                <option value="{{ qs({'sort': 'newest'}) }}" {% if sort == 'newest' %}selected{% endif %}>Newest</option>
                <option value="{{ qs({'sort': 'oldest'}) }}" {% if sort == 'oldest' %}selected{% endif %}>Oldest</option>
                <option value="{{ qs({'sort': 'severity'}) }}" {% if sort == 'severity' %}selected{% endif %}>Severity</option>
              </select>
            </div>
          </div>

          <div class="fsection">
            <div class="flabel">Min sources</div>
            <div class="fcontrol">
              <select onchange="location.href='/?' + this.value;">
                <option value="{{ qs({'min_sources': 1}) }}" {% if min_sources == 1 %}selected{% endif %}>1</option>
                <option value="{{ qs({'min_sources': 2}) }}" {% if min_sources == 2 %}selected{% endif %}>2</option>
                <option value="{{ qs({'min_sources': 3}) }}" {% if min_sources == 3 %}selected{% endif %}>3</option>
              </select>
            </div>
          </div>

          {% if (can_case_edit|default(false)) %}
            <div class="fsection">
              <div class="flabel">Status</div>
              <div class="fcontrol">
                <select onchange="location.href='/?' + this.value;">
                  <option value="{{ qs({'status': ''}) }}" {% if not status_filter %}selected{% endif %}>Any</option>
                  {% for sv in status_values %}
                    <option value="{{ qs({'status': sv}) }}" {% if status_filter == sv %}selected{% endif %}>{{ sv }}</option>
                  {% endfor %}
                </select>
              </div>
            </div>
          {% endif %}

          <div class="fsection">
            <div class="flabel">View</div>
            <div class="fcontrol">
              <select onchange="location.href='/?' + this.value;">
                <option value="{{ qs({'view': 'cards'}) }}" {% if view == 'cards' %}selected{% endif %}>Cards</option>
                <option value="{{ qs({'view': 'list'}) }}" {% if view == 'list' %}selected{% endif %}>List</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Sources (multi-select) -->
        <div class="section">
          <h3>Sources</h3>
          <div class="source-list">
            {% for src in source_names %}
              {% if src != 'All' %}
                {% set is_on = (src in selected_sources) %}
                <a class="source-item" href="/?{{ qs_toggle_source(src) }}" title="Toggle source">
                  <div class="source-left">
                    <span class="dot {% if is_on %}on{% endif %}"></span>
                    <span class="source-name">{{ src }}</span>
                  </div>
                  <span class="count">{{ source_counts.get(src, 0) }}</span>
                </a>
              {% endif %}
            {% endfor %}
          </div>
        </div>

        <!-- Categories (multi-select) -->
        <div class="section">
          <h3>Categories</h3>
          <div class="chips">
            {% for c in cat_union %}
              {% set on = (c in selected_cats) %}
              <a class="chip-link {% if on %}on{% endif %}" href="/?{{ qs_toggle_cat(c) }}">{{ c }}</a>
            {% endfor %}
            {% if cat_union|length == 0 %}
              <span style="color:rgba(250,250,250,.55); font-weight:850; font-size:13px;">No categories in current window.</span>
            {% endif %}
          </div>
        </div>

        <!-- Watchlist hint -->
        <div class="section">
          <h3>Watchlist</h3>
          <div style="color:rgba(250,250,250,.72); font-weight:800; line-height:1.5; font-size:13px;">
            Stored at <span style="color:rgba(250,250,250,.92);">{{ watchlist_path }}</span>
          </div>
          <div style="margin-top:10px; color:rgba(250,250,250,.60); font-weight:800; line-height:1.5; font-size:13px;">
            Tip: “Relevant (watchlist)” shows stories that match your environment terms.
          </div>
        </div>
      </div>
    </aside>

    <!-- MAIN -->
    <main class="main">

      {# =============================
         Threat Actor Profiles (MVP)
         ============================= #}
      {% if actor_profiles and actor_profiles|length %}
        <section class="section" style="margin-top:0; padding:14px; border-radius: var(--r); border:1px solid var(--border); background: rgba(24,24,27,.55); box-shadow: var(--shadow2);">
          <div style="display:flex; align-items:flex-end; justify-content:space-between; gap:12px; flex-wrap:wrap;">
            <div>
              <div style="font-weight:950; letter-spacing:-.2px; font-size:16px;">
                🕵️ Threat Actor Profiles
              </div>
              <div style="margin-top:6px; color: rgba(250,250,250,.62); font-weight:850; font-size:12px;">
                Auto-grouped from stories in the current view (actors + top CVEs/IOCs).
              </div>
            </div>

            <div style="display:flex; gap:8px; flex-wrap:wrap;">
              <span style="display:inline-flex; align-items:center; gap:8px; padding:6px 10px; border-radius:999px; border:1px solid rgba(255,255,255,.10); background: rgba(255,255,255,.03); color: rgba(250,250,250,.78); font-weight:900; font-size:12px;">
                {{ actor_profiles|length }} profiles
              </span>
            </div>
          </div>

          <div style="margin-top:12px; display:grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap:12px;">
            {% for ap in actor_profiles[:12] %}
              <a href="{{ ap.href }}" style="text-decoration:none;">
                <div style="border:1px solid rgba(255,255,255,.10); border-radius:14px; background: rgba(24,24,27,.55); box-shadow: 0 10px 25px rgba(0,0,0,.40); padding:12px 12px 10px;">
                  <div style="display:flex; justify-content:space-between; gap:10px; align-items:flex-start;">
                    <div style="font-weight:950; color: rgba(250,250,250,.95);">
                      {{ ap.label }}
                    </div>
                    <div style="display:inline-flex; align-items:center; gap:8px; padding:5px 9px; border-radius:999px; border:1px solid rgba(255,255,255,.10); background: rgba(255,255,255,.03); color: rgba(250,250,250,.80); font-weight:900; font-size:12px; white-space:nowrap;">
                      {{ ap.story_count }} stories
                    </div>
                  </div>

                  <div style="margin-top:8px; color: rgba(250,250,250,.65); font-weight:850; font-size:12px; line-height:1.35;">
                    <div><span style="opacity:.8;">Last seen:</span> <span style="font-weight:950;">{{ ap.last_seen }}</span></div>
                    {% if ap.top_cves and ap.top_cves|length %}
                      <div style="margin-top:6px;">
                        <span style="opacity:.8;">Top CVEs:</span>
                        <span style="font-weight:950;">{{ ap.top_cves|join(", ") }}</span>
                      </div>
                    {% endif %}
                    {% if ap.top_iocs and ap.top_iocs|length %}
                      <div style="margin-top:6px;">
                        <span style="opacity:.8;">Top IOCs:</span>
                        <span style="font-weight:950;">{{ ap.top_iocs|join(", ") }}</span>
                      </div>
                    {% endif %}
                  </div>

                  <div style="margin-top:10px; display:flex; justify-content:space-between; align-items:center;">
                    <div style="color: rgba(34,197,94,.92); font-weight:950; font-size:12px;">
                      Open profile →
                    </div>
                    <div style="color: rgba(250,250,250,.45); font-weight:900; font-size:12px;">
                      ID: {{ ap.campaign_id }}
                    </div>
                  </div>
                </div>
              </a>
            {% endfor %}
          </div>
        </section>
      {% endif %}

      {# =============================
        Phase 2: User KPIs (non-admin safe)
        ============================= #}
      {% if is_authed and (user_kpis is defined) %}
        {% set uk = user_kpis or {} %}
        <section class="kpi-strip" aria-label="Your KPIs">
          {# Assigned open #}
          {% set v_open = (uk.assigned_open|default(0))|int %}
          <a class="kpi-link" href="/?{{ qs({'mine':'1','kpi':'assigned_open'}) }}" title="View your open assigned stories">
            <div class="kpi {% if v_open >= 30 %}danger{% elif v_open >= 15 %}warn{% else %}good{% endif %}">
              <div class="k">Assigned open</div>
              <div class="v">{{ v_open }}</div>
              <div class="s">Cases assigned to you that still need action.</div>
            </div>
          </a>



          {# Assigned done #}
            {% set v_done = (uk.assigned_done|default(0))|int %}
            <a class="kpi-link" href="/?{{ qs({'mine':'1','kpi':'assigned_done'}) }}" title="View your done/closed assigned stories">
              <div class="kpi good">
                <div class="k">Assigned done</div>
                <div class="v">{{ v_done }}</div>
                <div class="s">Cases you’ve closed (Mitigated / Not Relevant).</div>
              </div>
            </a>

            {# Reviewed total #}
            {% set v_total = (uk.reviewed_total|default(0))|int %}
            <a class="kpi-link" href="/?{{ qs({'kpi':'reviewed_total'}) }}" title="View all stories you have reviewed">
              <div class="kpi">
                <div class="k">Reviewed total</div>
                <div class="v">{{ v_total }}</div>
                <div class="s">Total stories you’ve reviewed (all time).</div>
              </div>
            </a>

            {# Reviewed 24h #}
            {% set v_24 = (uk.reviewed_24h|default(0))|int %}
            <a class="kpi-link" href="/?{{ qs({'kpi':'reviewed_24h'}) }}" title="View stories you reviewed in the last 24 hours">
              <div class="kpi {% if v_24 >= 25 %}good{% elif v_24 >= 10 %}good{% else %}warn{% endif %}">
                <div class="k">Reviewed (24h)</div>
                <div class="v">{{ v_24 }}</div>
                <div class="s">Stories you reviewed in the last 24 hours.</div>
              </div>
            </a>


          {# Unreviewed assigned open #}
              {% set v_unrev = (uk.unreviewed_assigned|default(0))|int %}
              <a class="kpi-link" href="/?{{ qs({'mine':'1','kpi':'unreviewed_assigned'}) }}" title="View your unreviewed assigned stories">

            <div class="kpi {% if v_unrev >= 10 %}danger{% elif v_unrev >= 4 %}warn{% else %}good{% endif %}">
              <div class="k">Unreviewed assigned</div>
              <div class="v">{{ v_unrev }}</div>
              <div class="s">Open assigned stories you haven’t reviewed yet.</div>
            </div>
          </a>

        </section>
      {% endif %}

      <div class="headline">
        <div>
          <h1>Threat Feed</h1>

          {# ===== Delta subline (shows only when Delta filter is ON) ===== #}
          <div class="sub">
            Showing {{ items|length }} stories
            {% if delta == '1' %}
              <span style="margin-left:10px; color: rgba(250,250,250,.72); font-weight:900;">
                • {{ (delta_new_count|default(0))|int }} new since {{ delta_since_label|default("previous window") }}
              </span>
            {% endif %}
          </div>
        </div>

        <div class="row">
          {% if is_authed and ((can_mark_seen|default(false)) or (can_case_edit|default(false))) %}
            <button class="btn ghost bulk-toggle" id="bulkToggle" type="button" title="Toggle bulk selection">
              Bulk mode
            </button>
          {% endif %}
          <a class="btn ghost" href="/shortcuts">Shortcuts</a>
        </div>
      </div>

      {% if active_filters and active_filters|length > 0 %}
        <div class="active-filter-bar">
          {% for f in active_filters %}
            <div class="filter-pill" title="{{ f.key }}={{ f.value }}">
              {{ f.label }}
              <a class="x" href="/?{{ qs({ f.key: '' }) }}" title="Remove">×</a>
            </div>
          {% endfor %}
        </div>
      {% endif %}

      {% if errors and errors|length > 0 %}
        <div class="section" style="margin-top:14px; border-color: rgba(239,68,68,.35); background: rgba(239,68,68,.10);">
          <h3 style="color: rgba(239,68,68,.95);">Degraded sources</h3>
          <div style="color: rgba(250,250,250,.85); font-weight:800; line-height:1.6; font-size:13px;">
            {% for e in errors %}
              <div>• {{ e }}</div>
            {% endfor %}
          </div>
        </div>
      {% endif %}

      <div class="list">
        {% if view == 'list' %}
          {% for it in items %}
            {% set sev = it.severity or {} %}
            <div class="story-card">
              <div class="sev-bar {% if (sev.level or 'Low') == 'Critical' %}sev-critical{% elif (sev.level or 'Low') == 'High' %}sev-high{% elif (sev.level or 'Low') == 'Medium' %}sev-medium{% else %}sev-low{% endif %}"></div>
              <div style="padding:14px 16px 12px 16px;">
                <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
                  <span class="pill">{{ it.lead_source or 'Source' }}</span>
                  <span class="pill">{{ sev.level or 'Low' }} · {{ sev.score or 0 }}</span>
                  <span class="pill">Status: {{ it.status }}</span>
                  {% if it.kev %}<span class="pill warn">KEV</span>{% endif %}
                  {% if it.seen_before %}<span class="pill warn">Seen before</span>{% endif %}
                </div>
                <div style="margin-top:10px; font-weight:950; font-size:16px;">
                  <a href="/story/{{ it.story_id }}?{{ qs({}) }}">{{ it.title }}</a>
                </div>
                <div style="margin-top:8px; color:rgba(250,250,250,.75); font-weight:800; font-size:13px; line-height:1.5;">
                  {{ it.summary }}
                </div>
              </div>
            </div>
          {% endfor %}
        {% else %}
          {% for it in items %}
            {% set sev = it.severity or {} %}
            {% set sev_level = (sev.level or 'Low') %}
            {% set sev_score = (sev.score or 0) %}
            {% set sev_class = 'sev-low' %}
            {% if sev_level == 'Medium' %}{% set sev_class = 'sev-medium' %}{% endif %}
            {% if sev_level == 'High' %}{% set sev_class = 'sev-high' %}{% endif %}
            {% if sev_level == 'Critical' %}{% set sev_class = 'sev-critical' %}{% endif %}

            <div class="story-card"
                 data-story-id="{{ it.story_id }}"
                 data-owner="{{ it.owner|e }}"
                 data-notes="{{ (((it.notes or '')[:600]) ~ ('…' if (it.notes or '')|length > 600 else ''))|e }}"
                 data-status="{{ it.status|e }}"
                 data-seen="{{ 1 if it.seen else 0 }}">
              <div class="sev-bar {{ sev_class }}"></div>

              <div class="story-grid">
                <div class="story-left">
                  <div class="source-pill2" title="{{ it.lead_source or '' }}">{{ it.lead_source or 'Source' }}</div>

                  <div class="sev-pill2">
                    <span>{{ sev_level }}</span>
                    <span class="sev-score">{{ sev_score }}</span>
                  </div>

                  {% if sev.reasons %}
                    <div class="why" title="{{ (sev.reasons|join(' • ')) }}">
                      <span style="opacity:.9;">ⓘ</span> Why ranked
                    </div>
                  {% endif %}
                </div>

                <div class="story-main">
                  <h2 class="story-title">
                    <a href="/story/{{ it.story_id }}?{{ qs({}) }}">{{ it.title }}</a>
                  </h2>

                  <div class="chip-row">
                    <div class="chip"><span class="chip muted">Status:</span><strong>{{ it.status }}</strong></div>
                    <div class="chip"><span class="chip muted">Sources:</span> <strong>{{ it.sources_count }}</strong></div>
                    <div class="chip"><span class="chip muted">Trust:</span> <strong>{{ it.trust }}</strong></div>

                    {% if it.kev %}
                      <div class="chip warn"><strong>KEV</strong></div>
                    {% endif %}

                    {% if (sev.ioc_count or 0)|int > 0 %}
                      <div class="chip"><span class="chip">IOCs:</span> <strong>{{ sev.ioc_count }}</strong></div>
                    {% endif %}

                    {% if it.seen_before %}
                      <div class="chip warn"><strong>Seen before</strong></div>
                    {% endif %}

                    {% if it.matches_stack %}
                      <div class="chip good"><strong>Matches watchlist</strong></div>
                    {% endif %}
                  </div>

                  <div class="story-summary js-summary summary-clamp" data-collapsed="1">
                    {{ it.summary }}
                  </div>

                  <div class="expand-btn js-expand">Expand <span style="opacity:.85;">▾</span></div>
                </div>

                <div class="story-right">
                  <div class="kv">
                    {% if it.updated_utc %}
                      <div class="kv-pill">Updated {{ rel_time(it.updated_utc) }}</div>
                    {% endif %}
                    {% if it.owner %}
                      {% set _own = it.owner %}
                      <div class="kv-pill" title="{{ _own }}">Owner: <strong style="color:var(--text)">{{ _own.split('@',1)[0] }}</strong></div>
                    {% endif %}

                    {% if it.updated_by_email %}
                      <div class="kv-pill" title="{{ it.updated_by_email }}">By {{ it.updated_by_email.split('@',1)[0] }}</div>
                    {% endif %}
                  </div>
                </div>
              </div>

              <div class="actions-row">
                {% if is_authed and ((can_mark_seen|default(false)) or (can_case_edit|default(false))) %}
                  <input class="bulk-only bulk-check js-bulk-check" type="checkbox" data-story-id="{{ it.story_id }}" title="Select">
                {% endif %}

                <a class="btn primary" href="/story/{{ it.story_id }}?{{ qs({}) }}">Open</a>

                {% if is_authed and (can_mark_seen|default(false)) %}
                  <button class="btn js-toggle-reviewed" type="button" data-story-id="{{ it.story_id }}">
                    {% if it.seen %}Reviewed ✓{% else %}Mark reviewed{% endif %}
                  </button>
                {% endif %}

                {% if is_authed and (can_case_edit|default(false)) %}
                  <select class="js-status" data-story-id="{{ it.story_id }}">
                    {% for sv in status_values %}
                      <option value="{{ sv }}" {% if it.status == sv %}selected{% endif %}>{{ sv }}</option>
                    {% endfor %}
                  </select>

                  <button class="btn js-assign" type="button" data-story-id="{{ it.story_id }}">Assign to me</button>
                  <button class="btn ghost js-notes" type="button" data-story-id="{{ it.story_id }}">Notes</button>
                {% endif %}
              </div>
            </div>
          {% endfor %}
        {% endif %}

        {% if items|length == 0 %}
          <div class="section">
            <h3>No results</h3>
            <div style="color:rgba(250,250,250,.72); font-weight:900; line-height:1.6; font-size:13px;">
              Try clearing filters or widening the time range.
            </div>
            <div style="margin-top:10px;">
              <a class="btn primary" href="/?{{ qs_clear_all() }}">Clear all</a>
            </div>
          </div>
        {% endif %}
      </div>

      {% if is_authed and ((can_mark_seen|default(false)) or (can_case_edit|default(false))) %}
        <div class="bulkbar" id="bulkBar">
          <div class="meta" id="bulkMeta">0 selected</div>
          <div class="spacer"></div>

          {% if can_mark_seen|default(false) %}
            <button class="btn" id="bulkReview" type="button">Mark reviewed</button>
          {% endif %}

          {% if can_case_edit|default(false) %}
            <button class="btn" id="bulkAssign" type="button">Assign to me</button>

            <select id="bulkStatus" style="min-width: 180px;">
              {% for sv in status_values %}
                <option value="{{ sv }}">{{ sv }}</option>
              {% endfor %}
            </select>
            <button class="btn" id="bulkSetStatus" type="button">Set status</button>
          {% endif %}
        </div>
      {% endif %}

      <div class="toast" id="toast"></div>
    </main>
  </div>

  <script>
    const INIT = {{ {
      "csrf_token": (csrf_token|default("")),
      "is_authed": (is_authed|default(false))
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
      return { ok: r.ok, status: r.status, data };
    }

    /* ===== Compact mode toggle (persistent) ===== */
    (function(){
      const KEY = "threatly_compact";
      const btn = document.getElementById("compactToggle");
      const dot = document.getElementById("compactDot");
      const lab = document.getElementById("compactLabel");

      function apply(on){
        document.body.classList.toggle("compact", !!on);
        if(btn) btn.classList.toggle("on", !!on);
        if(dot) dot.style.opacity = "1";
        if(lab) lab.textContent = on ? "Compact: On" : "Compact: Off";
      }

      let on = false;
      try{
        on = (localStorage.getItem(KEY) === "1");
      }catch(e){}
      apply(on);

      if(btn){
        btn.addEventListener("click", function(){
          on = !document.body.classList.contains("compact");
          apply(on);
          try{ localStorage.setItem(KEY, on ? "1" : "0"); }catch(e){}
        });
      }
    })();

    /* ===== User dropdown: robust close behavior ===== */
    (function(){
      const btn = document.getElementById("userBtn");
      const dd = document.getElementById("userDropdown");
      if(!btn || !dd) return;

      function close(){ dd.classList.remove("on"); }
      function isOpen(){ return dd.classList.contains("on"); }

      btn.addEventListener("click", function(e){
        e.preventDefault();
        e.stopPropagation();
        if (isOpen()) close();
        else dd.classList.add("on");
      });

      dd.addEventListener("click", function(e){
        e.stopPropagation();
      });

      document.addEventListener("click", function(){ close(); });
      document.addEventListener("keydown", function(e){ if (e.key === "Escape") close(); });

      window.addEventListener("resize", close);
      window.addEventListener("scroll", close, true);
    })();

    // Expand / Collapse summary
    document.addEventListener("click", function(e){
      const exp = e.target.closest(".js-expand");
      if(!exp) return;
      const card = exp.closest(".story-card");
      if(!card) return;
      const sum = card.querySelector(".js-summary");
      if(!sum) return;

      const collapsed = sum.getAttribute("data-collapsed") === "1";
      if(collapsed){
        sum.classList.remove("summary-clamp");
        sum.setAttribute("data-collapsed","0");
        exp.innerHTML = 'Collapse <span style="opacity:.85;">▴</span>';
      } else {
        sum.classList.add("summary-clamp");
        sum.setAttribute("data-collapsed","1");
        exp.innerHTML = 'Expand <span style="opacity:.85;">▾</span>';
      }
    });

    // Reviewed toggle
    document.addEventListener("click", async function(e){
      const btn = e.target.closest(".js-toggle-reviewed");
      if(!btn) return;
      const storyId = btn.getAttribute("data-story-id");
      if(!storyId) return;

      const res = await postJSON("/api/seen/toggle", {story_id: storyId});

      if(!res.ok){
        if(res.status === 401) toast("Session expired — please log in.");
        else if(res.status === 403) toast("Not permitted for your role.");
        else toast("Request failed.");
        return;
      }

      const seen = !!(res.data && res.data.seen);
      btn.textContent = seen ? "Reviewed ✓" : "Mark reviewed";
      toast(seen ? "Marked reviewed" : "Marked unreviewed");
    });

    // Status set (preserves current owner/notes from data-attrs)
    document.addEventListener("change", async function(e){
      const sel = e.target.closest(".js-status");
      if(!sel) return;

      const card = sel.closest(".story-card");
      const storyId = sel.getAttribute("data-story-id");
      if(!card || !storyId) return;

      const status = sel.value;
      const owner = card.getAttribute("data-owner") || "";
      const notes = card.getAttribute("data-notes") || "";

      const res = await postJSON("/api/meta/set", {
        story_id: storyId,
        status: status,
        owner: owner,
        notes: notes
      });

      if(!res.ok){
        if(res.status === 401) toast("Session expired — please log in.");
        else if(res.status === 403) toast("Not permitted for your role.");
        else toast("Request failed.");
        return;
      }

      card.setAttribute("data-status", status);
      toast("Status updated");
    });

    // Assign to me
    document.addEventListener("click", async function(e){
      const btn = e.target.closest(".js-assign");
      if(!btn) return;
      const storyId = btn.getAttribute("data-story-id");
      if(!storyId) return;

      const res = await postJSON("/api/meta/assign_to_me", {story_id: storyId});

      if(!res.ok){
        if(res.status === 401) toast("Session expired — please log in.");
        else if(res.status === 403) toast("Not permitted for your role.");
        else toast("Request failed.");
        return;
      }

      toast("Assigned to you");
      window.setTimeout(()=> location.reload(), 250);
    });

    // Notes (prompt for now, simple + reliable)
    document.addEventListener("click", async function(e){
      const btn = e.target.closest(".js-notes");
      if(!btn) return;
      const storyId = btn.getAttribute("data-story-id");
      const card = btn.closest(".story-card");
      if(!storyId || !card) return;

      const curNotes = card.getAttribute("data-notes") || "";
      const curOwner = card.getAttribute("data-owner") || "";
      const curStatus = card.getAttribute("data-status") || "New";

      const next = prompt("Notes (saved globally for this story):", curNotes);
      if(next === null) return;

      const res = await postJSON("/api/meta/set", {
        story_id: storyId,
        status: curStatus,
        owner: curOwner,
        notes: String(next)
      });

      if(!res.ok){
        if(res.status === 401) toast("Session expired — please log in.");
        else if(res.status === 403) toast("Not permitted for your role.");
        else toast("Request failed.");
        return;
      }

      toast("Notes updated");
      window.setTimeout(()=> location.reload(), 250);
    });

    /* ===== Bulk Mode (Option 3) ===== */
    (function(){
      const KEY = "threatly_bulk_mode";
      const toggle = document.getElementById("bulkToggle");
      const bar = document.getElementById("bulkBar");
      const meta = document.getElementById("bulkMeta");
      const btnReview = document.getElementById("bulkReview");
      const btnAssign = document.getElementById("bulkAssign");
      const selStatus = document.getElementById("bulkStatus");
      const btnSetStatus = document.getElementById("bulkSetStatus");

      if(!toggle && !bar) return; // bulk not enabled for this user

      const selected = new Set();

      function setMode(on){
        document.body.classList.toggle("bulk-on", !!on);
        if(toggle) toggle.classList.toggle("on", !!on);
        try{ localStorage.setItem(KEY, on ? "1" : "0"); }catch(e){}

        // Clear selection when turning OFF
        if(!on){
          selected.clear();
          document.querySelectorAll(".js-bulk-check").forEach(cb => { cb.checked = false; });
          updateBar();
        }
      }

      function isModeOn(){
        return document.body.classList.contains("bulk-on");
      }

      function updateBar(){
        const n = selected.size;
        if(meta) meta.textContent = `${n} selected`;
        if(bar) bar.classList.toggle("on", isModeOn() && n > 0);

        const disabled = !(isModeOn() && n > 0);
        if(btnReview) btnReview.disabled = disabled;
        if(btnAssign) btnAssign.disabled = disabled;
        if(btnSetStatus) btnSetStatus.disabled = disabled;
      }

      // init mode from storage
      let on = false;
      try{ on = (localStorage.getItem(KEY) === "1"); }catch(e){}
      setMode(on);
      updateBar();

      if(toggle){
        toggle.addEventListener("click", function(){
          setMode(!isModeOn());
          updateBar();
          toast(isModeOn() ? "Bulk mode ON" : "Bulk mode OFF");
        });
      }

      // checkbox selection handler
      document.addEventListener("change", function(e){
        const cb = e.target.closest(".js-bulk-check");
        if(!cb) return;
        const id = cb.getAttribute("data-story-id");
        if(!id) return;

        if(cb.checked) selected.add(id);
        else selected.delete(id);

        updateBar();
      });

      async function bulkReview(){
        const ids = Array.from(selected);
        if(ids.length === 0) return;

        let changed = 0;

        for(const id of ids){
          const card = document.querySelector(`.story-card[data-story-id="${CSS.escape(id)}"]`);
          const seen = card ? (card.getAttribute("data-seen") === "1") : false;
          if(seen) continue;

          const res = await postJSON("/api/seen/toggle", {story_id: id});
          if(res.ok){
            changed += 1;
            if(card) card.setAttribute("data-seen","1");
          } else {
            if(res.status === 401) toast("Session expired — please log in.");
            else if(res.status === 403) toast("Not permitted for your role.");
            else toast("Request failed.");
            return;
          }
        }

        toast(changed > 0 ? `Marked ${changed} reviewed` : "All selected already reviewed");
        window.setTimeout(()=> location.reload(), 250);
      }

      async function bulkAssign(){
        const ids = Array.from(selected);
        if(ids.length === 0) return;

        for(const id of ids){
          const res = await postJSON("/api/meta/assign_to_me", {story_id: id});
          if(!res.ok){
            if(res.status === 401) toast("Session expired — please log in.");
            else if(res.status === 403) toast("Not permitted for your role.");
            else toast("Request failed.");
            return;
          }
        }

        toast(`Assigned ${ids.length} to you`);
        window.setTimeout(()=> location.reload(), 250);
      }

      async function bulkSetStatus(){
        const ids = Array.from(selected);
        if(ids.length === 0) return;

        const status = selStatus ? selStatus.value : "";
        if(!status){
          toast("Pick a status");
          return;
        }

        for(const id of ids){
          const card = document.querySelector(`.story-card[data-story-id="${CSS.escape(id)}"]`);
          if(!card) continue;

          const owner = card.getAttribute("data-owner") || "";
          const notes = card.getAttribute("data-notes") || "";

          const res = await postJSON("/api/meta/set", {
            story_id: id,
            status: status,
            owner: owner,
            notes: notes
          });

          if(!res.ok){
            if(res.status === 401) toast("Session expired — please log in.");
            else if(res.status === 403) toast("Not permitted for your role.");
            else toast("Request failed.");
            return;
          }

          card.setAttribute("data-status", status);
        }

        toast(`Status set to "${status}" on ${ids.length}`);
        window.setTimeout(()=> location.reload(), 250);
      }

      if(btnReview) btnReview.addEventListener("click", bulkReview);
      if(btnAssign) btnAssign.addEventListener("click", bulkAssign);
      if(btnSetStatus) btnSetStatus.addEventListener("click", bulkSetStatus);
    })();
  </script>
</body>
</html>
"""