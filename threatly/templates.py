
# threatly/templates.py
from __future__ import annotations

# NOTE:
# This file defines server-rendered Jinja templates as Python strings.
# Keep it self-contained: CSS + JS embedded to avoid static file setup.

# threatly/templates.py

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
                    <a href="/admin/users">🛠️ Admin</a>
                  {% endif %}

                  <div class="sep"></div>
                  <a href="/health">🩺 Health</a>
                  <a href="/logout">🚪 Logout</a>
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

      <div class="headline">
        <div>
          <h1>Threat feed</h1>

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





# story_template.py

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



LOGIN_TEMPLATE = r"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Threatly • {{ 'Login' if mode=='login' else 'Account setup' }}</title>

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
      --danger:#ef4444;

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
      min-height:100vh;
      display:flex;
      align-items:center;
      justify-content:center;
      padding:20px;
      font-family: Inter, -apple-system, BlinkMacSystemFont, system-ui, Segoe UI, Roboto, Arial, sans-serif;
      font-size: var(--fs);
      color:var(--text);
      background:
        radial-gradient(900px 600px at 20% -10%, rgba(34,197,94,.10), transparent 60%),
        radial-gradient(900px 600px at 110% 0%, rgba(59,130,246,.10), transparent 55%),
        linear-gradient(180deg, var(--bg0), var(--bg1));
    }

    .card{
      width:420px;
      max-width: calc(100vw - 40px);
      background: rgba(24,24,27,.55);
      border:1px solid var(--border);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      padding:18px;
      overflow:hidden;
    }

    .brand{
      display:flex;
      align-items:center;
      gap:10px;
      margin-bottom:12px;
    }
    .logo{
      width:34px;
      height:34px;
      border-radius: var(--radiusSm);
      background: rgba(34,197,94,.12);
      border:1px solid rgba(34,197,94,.35);
      display:flex;
      align-items:center;
      justify-content:center;
      font-weight:980;
      color: var(--accent);
      user-select:none;
    }
    .brand h1{
      margin:0;
      font-size:18px;
      letter-spacing:.2px;
      font-weight:980;
    }

    .subtitle{
      font-size:13px;
      color: rgba(250,250,250,.65);
      margin-bottom:14px;
      line-height:1.45;
      font-weight:850;
    }

    .err{
      margin-top:10px;
      margin-bottom:10px;
      padding:10px 12px;
      border-radius: var(--radiusSm);
      border:1px solid rgba(239,68,68,.35);
      background: rgba(239,68,68,.10);
      color: rgba(255,230,230,.95);
      font-size:13px;
      font-weight:900;
      line-height:1.45;
    }

    label{
      display:block;
      margin-top:12px;
      font-size:11px;
      color: rgba(250,250,250,.55);
      font-weight:900;
      letter-spacing:.08em;
      text-transform:uppercase;
    }

    input{
      width:100%;
      margin-top:6px;
      padding:10px 11px;
      border-radius: var(--radiusSm);
      border:1px solid var(--border);
      background: rgba(0,0,0,.28);
      color: var(--text);
      outline:none;
      font-weight:900;
      font-size: 13px;
    }
    input::placeholder{ color:rgba(250,250,250,.35); }
    input:focus{
      border-color: rgba(34,197,94,.45);
      box-shadow: 0 0 0 4px rgba(34,197,94,.10);
    }

    .btn{
      width:100%;
      margin-top:14px;
      padding:10px 11px;
      border-radius: var(--radiusSm);
      border:1px solid rgba(34,197,94,.35);
      background: rgba(34,197,94,.12);
      color: var(--text);
      font-weight:950;
      cursor:pointer;
      transition: background .12s ease, border-color .12s ease, transform .06s ease, opacity .12s ease;
    }
    .btn:hover{
      background: rgba(34,197,94,.18);
      border-color: rgba(34,197,94,.45);
    }
    .btn:active{ transform: translateY(1px); }

    .footer{
      margin-top:12px;
      font-size:12px;
      color: rgba(250,250,250,.60);
      text-align:center;
      font-weight:850;
    }

    a{
      color: var(--accent);
      text-decoration:none;
      font-weight:900;
    }
    a:hover{ text-decoration: underline; }

    .trust{
      margin-top:14px;
      padding-top:10px;
      border-top:1px solid rgba(39,39,42,.75);
      font-size:11px;
      color: rgba(250,250,250,.50);
      text-align:center;
      line-height:1.45;
      font-weight:850;
    }
  </style>
</head>

<body>
  <div class="card">
    <div class="brand">
      <div class="logo">T</div>
      <h1>Threatly</h1>
    </div>

    <div class="subtitle">
      {% if mode=='login' %}
        Secure access to your threat intelligence workspace.
      {% else %}
        Create an account to enable analyst workflows and audit tracking.
      {% endif %}
    </div>

    {% if error %}
      <div class="err">{{ error }}</div>
    {% endif %}

    <form method="POST" action="{{ '/login' if mode=='login' else '/signup' }}">
      <input type="hidden" name="next" value="{{ next_url|e }}">

      <label>Email address</label>
      <input name="email" type="email" value="{{ email|e }}" placeholder="analyst@company.com" required>

      <label>Password</label>
      <input name="password" type="password" minlength="10" placeholder="Minimum 10 characters" required>

      <button class="btn" type="submit">
        {{ 'Sign in' if mode=='login' else 'Create account' }}
      </button>
    </form>

    <div class="footer">
      {% if mode=='login' %}
        No account? <a href="/signup">Request access</a>
      {% else %}
        Already onboarded? <a href="/login">Sign in</a>
      {% endif %}
    </div>

    <div class="trust">
      • Role-based access control<br>
      • Per-user audit trails<br>
      • Enterprise-first design
    </div>
  </div>
</body>
</html>
"""



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
          <a class="btn danger" href="/logout">Logout</a>
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


ADMIN_DASHBOARD_TEMPLATE = r"""
<style>
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
    border:1px solid var(--border);
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
    border:1px solid var(--border);
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
    padding:10px 12px;
    border:1px solid var(--border);
    border-radius: var(--r);
    background: rgba(24,24,27,.35);
    overflow: visible; /* let tooltip escape */
  }

  /* Window-based KPI emphasis */
  .kpi-card.window{
    border-color: rgba(34,197,94,.22);
    box-shadow: 0 0 0 1px rgba(34,197,94,.08) inset;
  }

  .kpi-head{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:10px;
    min-width:0;
  }
  .kpi-label{
    color: var(--muted2);
    font-weight:700;
    font-size:12px;
    min-width:0;
    white-space:nowrap;
    overflow:hidden;
    text-overflow:ellipsis;
  }

  .kpi-value{
    font-size:22px;
    font-weight:900;
    margin-top:4px;
  }

  .kpi-sub{
    color: var(--muted2);
    font-weight:700;
    font-size:12px;
    margin-top:8px;
  }

  .kpi-badge{
    display:inline-flex;
    align-items:center;
    gap:6px;
    padding:3px 8px;
    border-radius:999px;
    border:1px solid rgba(255,255,255,.10);
    background: rgba(255,255,255,.03);
    color: rgba(250,250,250,.78);
    font-weight:900;
    font-size:11px;
    line-height:1;
    user-select:none;
    margin-left:8px;
  }
  .kpi-badge.window{
    border-color: rgba(34,197,94,.22);
    background: rgba(34,197,94,.10);
    color: rgba(250,250,250,.88);
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
  .top-left{
    min-width:0;
    flex: 1 1 auto;
  }

  .top-right{
  flex: 0 0 32%;
  min-width:110px;
  max-width:180px;
}


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
    flex: 0 0 46%;
    min-width:110px;
    max-width:200px;
  }
  .bar{
    height:10px;
    border-radius:999px;
    background: rgba(255,255,255,.08);
    border:1px solid rgba(255,255,255,.10);
    overflow:hidden;
  }
  .bar > div{
    height:100%;
    background: rgba(34,197,94,.85);
    width:0%;
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

  <div class="range-row">
    <div class="seg" aria-label="Time range">
      <a class="{{ 'active' if w=='24h' else '' }}" href="?w=24h">24h</a>
      <a class="{{ 'active' if w=='7d' else '' }}" href="?w=7d">7d</a>
      <a class="{{ 'active' if w=='30d' else '' }}" href="?w=30d">30d</a>
      <a class="{{ 'active' if w=='90d' else '' }}" href="?w=90d">90d</a>
      <a class="{{ 'active' if w=='custom' else '' }}" href="?w=custom">Custom</a>
    </div>

    <form class="custom {{ 'show' if w=='custom' else '' }}" method="get" action="">
      <input type="hidden" name="w" value="custom"/>
      <input type="date" name="from" value="{{ w_from }}" aria-label="From date"/>
      <span class="muted2" style="font-weight:900;">→</span>
      <input type="date" name="to" value="{{ w_to }}" aria-label="To date"/>
      <button class="btn" type="submit">Apply</button>
    </form>
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

    <div class="kpi-card window">
      <div class="kpi-head">
        <div class="kpi-label">
          Audit
          <span class="kpi-badge window" title="This KPI respects the selected time range">⏱ window</span>
        </div>
        <span class="tip" tabindex="0" data-tip="Count of admin audit events in the selected time window.">i</span>
      </div>
      <div class="kpi-value">{{ kpis.audit_window }}</div>
    </div>
  </div>

  <!-- Row 2 (windowed audit intelligence) -->
  <div class="kpi-grid" style="margin-top:12px;">
    <div class="kpi-card window">
      <div class="kpi-head">
        <div class="kpi-label">
          Top action
          <span class="kpi-badge window" title="This KPI respects the selected time range">⏱ window</span>
        </div>
        <span class="tip" tabindex="0" data-tip="Most common audit event in the selected window. Bar shows its share of total window events.">i</span>
      </div>

      <div class="top-action">
        <div class="top-left">
          <div class="top-name" title="{{ top_action }}">
            {% if top_action %}
              {{ top_action }}
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
        <div class="kpi-label">
          Last event
          <span class="kpi-badge window" title="This KPI respects the selected time range">⏱ window</span>
        </div>
        <span class="tip" tabindex="0" data-tip="Most recent admin audit event within the selected window (action + actor).">i</span>
      </div>
      <div class="kpi-value" style="font-size:16px; margin-top:8px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;"
           title="{% if kpis.last_event and kpis.last_event.action %}{{ kpis.last_event.action }}{% endif %}">
        {% if kpis.last_event and kpis.last_event.action %}
          {{ kpis.last_event.action }}
        {% else %}
          —
        {% endif %}
      </div>
      <div class="kpi-sub" style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis;"
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
        <div class="kpi-label">
          Login failures
          <span class="kpi-badge window" title="This KPI respects the selected time range">⏱ window</span>
        </div>
        <span class="tip" tabindex="0" data-tip="Failed login attempts in the selected window (only increases if your auth code logs failures).">i</span>
      </div>
      <div class="kpi-value">{{ kpis.login_fail_window or 0 }}</div>
    </div>

    <div class="kpi-card window">
      <div class="kpi-head">
        <div class="kpi-label">
          Privileged actions
          <span class="kpi-badge window" title="This KPI respects the selected time range">⏱ window</span>
        </div>
        <span class="tip" tabindex="0" data-tip="Sensitive admin actions in the selected window (user/role/password/settings).">i</span>
      </div>
      <div class="kpi-value">{{ kpis.privileged_window or 0 }}</div>
    </div>

    <div class="kpi-card window">
      <div class="kpi-head">
        <div class="kpi-label">
          Window
          <span class="kpi-badge window" title="This KPI respects the selected time range">⏱ window</span>
        </div>
        <span class="tip" tabindex="0" data-tip="Quick sanity check: which window is currently applied.">i</span>
      </div>
      <div class="kpi-value" style="font-size:16px; margin-top:8px;">
        {% if w == 'custom' and w_from and w_to %}
          <span class="badge code">{{ w_from }}</span> → <span class="badge code">{{ w_to }}</span>
        {% else %}
          <span class="badge code">{{ window_label(w) }}</span>
        {% endif %}
      </div>
      <div class="kpi-sub">All audit KPIs above follow this window.</div>
    </div>
  </div>

  <div class="muted" style="margin-top:10px;">
    Tip: Provision users in <span class="badge code">Users</span>, verify changes in <span class="badge code">Audit</span>.
  </div>
</div>
"""








ADMIN_USERS_TEMPLATE = r"""
<div class="card">
  <div style="display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap;">
    <div>
      <div style="font-size:18px; font-weight:850;">Create user</div>
      <div class="muted2">Provision an account with a temporary password (rotate after first login).</div>
    </div>
  </div>

  <form method="post" action="/admin/users/create" style="margin-top:12px; display:flex; gap:10px; flex-wrap:wrap;">
    <input name="email" placeholder="email@company.com" required style="flex:1; min-width:240px;">
    <select name="role" style="min-width:160px;">
      <option value="viewer">viewer</option>
      <option value="analyst">analyst</option>
      <option value="admin">admin</option>
    </select>
    <input name="password" placeholder="temporary password (min 10 chars)" required style="flex:1; min-width:240px;">
    <button class="btn primary" type="submit">Create</button>
  </form>
</div>

<div class="card">
  <div style="display:flex; align-items:flex-end; justify-content:space-between; gap:12px; flex-wrap:wrap;">
    <div>
      <div style="font-size:18px; font-weight:850;">Users</div>
      <div class="muted2">Search, filter, and manage accounts.</div>
    </div>
  </div>

  <form method="get" action="/admin/users" style="margin-top:12px; display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
    <input name="q" value="{{ q }}" placeholder="Search email or user_id…" style="flex:1; min-width:260px;">
    <select name="role" style="min-width:160px;">
      <option value="">Any role</option>
      <option value="viewer" {% if role=='viewer' %}selected{% endif %}>viewer</option>
      <option value="analyst" {% if role=='analyst' %}selected{% endif %}>analyst</option>
      <option value="admin" {% if role=='admin' %}selected{% endif %}>admin</option>
    </select>
    <select name="active" style="min-width:160px;">
      <option value="">Any status</option>
      <option value="1" {% if active_filter=='1' %}selected{% endif %}>active</option>
      <option value="0" {% if active_filter=='0' %}selected{% endif %}>disabled</option>
    </select>
    <button class="btn" type="submit">Filter</button>
    <a class="btn ghost" href="/admin/users">Clear</a>
  </form>

  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th style="width: 32%;">User</th>
          <th style="width: 10%;">Role</th>
          <th style="width: 12%;">Status</th>
          <th style="width: 18%;">Created</th>
          <th style="width: 18%;">Last login</th>
          <th style="width: 10%; text-align:right;">Actions</th>
        </tr>
      </thead>
      <tbody>
        {% for u in users %}
          <tr>
            <td>
              <div style="font-weight:900;">{{ u.email }}</div>
              <div class="mono clip" title="{{ u.user_id }}">{{ u.user_id }}</div>
            </td>

            <td>
              <span class="badge code">{{ u.role }}</span>
            </td>

            <td>
              {% if u.is_active == 1 %}
                <span class="dot ok"></span>
                <span style="margin-left:8px; font-weight:800; color: rgba(250,250,250,.88);">active</span>
              {% else %}
                <span class="dot warn"></span>
                <span style="margin-left:8px; font-weight:800; color: rgba(250,250,250,.78);">disabled</span>
              {% endif %}
            </td>

            <td class="mono">{{ u.created_utc or '-' }}</td>
            <td class="mono">{{ u.last_login_utc or '-' }}</td>

            <td style="text-align:right;">
              {# ✅ Reliable dropdown: real button + JS (no checkbox/label quirks) #}
              <div class="dd" data-dd>
                <button type="button"
                        class="btn dd-trigger"
                        data-dd-trigger
                        aria-haspopup="menu"
                        aria-expanded="false"
                        aria-label="Actions">
                  ⋯
                </button>

                <div class="dd-menu" data-dd-menu role="menu" aria-label="User actions">
                  <div class="muted2" style="padding:6px 8px;">{{ u.email }}</div>
                  <div class="dd-sep"></div>

                  <form method="post" action="/admin/users/{{ u.user_id }}/role"
                        onsubmit="return confirm('Change role for this user?');">
                    <div style="display:flex; gap:8px; padding:6px;">
                      <select name="role" style="flex:1; min-width:140px;">
                        <option value="viewer" {{ 'selected' if u.role=='viewer' else '' }}>viewer</option>
                        <option value="analyst" {{ 'selected' if u.role=='analyst' else '' }}>analyst</option>
                        <option value="admin" {{ 'selected' if u.role=='admin' else '' }}>admin</option>
                      </select>
                      <button class="btn" type="submit">Set</button>
                    </div>
                  </form>

                  <div class="dd-sep"></div>

                  <form method="post" action="/admin/users/{{ u.user_id }}/reset_password"
                        onsubmit="return confirm('Reset password? Send temporary password securely.');">
                    <div style="padding:6px;">
                      <input name="password" placeholder="new temporary password (min 10)" required style="width:100%;">
                      <button class="btn" type="submit" style="margin-top:8px; width:100%;">Reset password</button>
                    </div>
                  </form>

                  <div class="dd-sep"></div>

                  <form method="post" action="/admin/users/{{ u.user_id }}/toggle"
                        onsubmit="return confirm('Are you sure? This affects access immediately.');">
                    {% if u.is_active==1 %}
                      <button class="dd-item danger" type="submit">Disable user</button>
                    {% else %}
                      <button class="dd-item" type="submit">Re-enable user</button>
                    {% endif %}
                  </form>
                </div>
              </div>
            </td>
          </tr>
        {% endfor %}

        {% if users|length == 0 %}
          <tr><td colspan="6" class="muted">No users match your filters.</td></tr>
        {% endif %}
      </tbody>
    </table>
  </div>
</div>
"""


ADMIN_ROLES_TEMPLATE = r"""
<div class="card">
  <div style="display:flex; align-items:flex-end; justify-content:space-between; gap:12px; flex-wrap:wrap;">
    <div>
      <div style="font-size:18px; font-weight:850;">Roles & Permissions</div>
      <div class="muted2">RBAC truth table. A 403 means the role lacks the permission.</div>
    </div>
  </div>

  <div class="table-wrap" style="margin-top:12px;">
    <table>
      <thead>
        <tr>
          <th style="width:20%;">Role</th>
          <th style="width:80%;">Permissions</th>
        </tr>
      </thead>
      <tbody>
        {% for r in roles %}
          <tr>
            <td>
              <div style="display:flex; align-items:center; justify-content:space-between; gap:10px;">
                <div style="font-weight:900;">{{ r.role }}</div>
                <span class="badge">{{ r.perms|length }} perms</span>
              </div>
            </td>
            <td>
              <div style="display:flex; gap:8px; flex-wrap:wrap;">
                {% for p in r.perms %}
                  <span class="ghost-tag">{{ p }}</span>
                {% endfor %}
              </div>
            </td>
          </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</div>
"""


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


ADMIN_SETTINGS_TEMPLATE = r"""
<div class="card">
  <div style="display:flex; align-items:flex-end; justify-content:space-between; gap:12px; flex-wrap:wrap;">
    <div>
      <div style="font-size:18px; font-weight:850;">Settings</div>
      <div class="muted2">Operational settings. Runtime env vars still override core auth behavior.</div>
    </div>
  </div>
</div>

<div class="card">
  <div style="display:flex; align-items:center; justify-content:space-between; gap:12px; flex-wrap:wrap;">
    <div>
      <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
        <div style="font-size:18px; font-weight:850;">Watchlist</div>

        {% if watchlist_ok %}
          <span class="badge" style="border:1px solid rgba(71,227,183,.45); color: var(--accent); background: rgba(71,227,183,.08);">Valid</span>
        {% else %}
          <span class="badge" style="border:1px solid rgba(255,122,122,.45); color: var(--danger); background: rgba(255,122,122,.08);">Invalid</span>
        {% endif %}
      </div>

      <div class="muted2" style="margin-top:6px;">
        Stored at: <span class="mono wrapany">{{ watchlist_path }}</span>
      </div>

      <div class="muted2" style="margin-top:6px;">
        {% if watchlist_updated_utc %}
          Last updated: <span class="badge code">{{ watchlist_updated_utc }}</span>
        {% endif %}
        {% if watchlist_updated_by %}
          <span class="muted2">by</span> <span class="badge code">{{ watchlist_updated_by }}</span>
        {% endif %}
      </div>
    </div>

    <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
      <a class="btn ghost" href="{{ url_for('admin.admin_settings') }}">Refresh</a>
      <button class="btn primary" type="button" id="wlSaveBtnTop">Save watchlist</button>
    </div>
  </div>

  {% if watchlist_errors and watchlist_errors|length > 0 %}
    <div style="margin-top:12px; border:1px solid rgba(255,122,122,.35); background: rgba(255,122,122,.06); border-radius: var(--r); padding:12px;">
      <div style="font-weight:900;">Errors</div>
      <div class="muted2" style="margin-top:6px;">These will block saving.</div>
      <ul style="margin:10px 0 0 18px;">
        {% for e in watchlist_errors %}
          <li class="muted">{{ e }}</li>
        {% endfor %}
      </ul>
    </div>
  {% endif %}

  {% if watchlist_warnings and watchlist_warnings|length > 0 %}
    <div style="margin-top:12px; border:1px solid rgba(255,210,120,.35); background: rgba(255,210,120,.06); border-radius: var(--r); padding:12px;">
      <div style="font-weight:900;">Warnings</div>
      <div class="muted2" style="margin-top:6px;">These won’t block saving, but they can create noisy matches.</div>
      <ul style="margin:10px 0 0 18px;">
        {% for w in watchlist_warnings %}
          <li class="muted">{{ w }}</li>
        {% endfor %}
      </ul>
    </div>
  {% endif %}

  <form method="post" action="/admin/settings/watchlist" style="margin-top:14px;" id="wlForm">
    <!-- Hidden payload that admin.py already understands -->
    <textarea name="watchlist" id="wlPayload" style="display:none;"></textarea>

    <div style="display:grid; grid-template-columns: 320px 1fr; gap:14px; margin-top:8px;">
      <!-- LEFT: Groups -->
      <div style="border:1px solid var(--border); border-radius: var(--r); background: rgba(0,0,0,.14); overflow:hidden;">
        <div style="padding:12px; border-bottom:1px solid var(--border); display:flex; align-items:center; justify-content:space-between; gap:10px;">
          <div>
            <div style="font-weight:950;">Groups</div>
            <div class="muted2" style="margin-top:4px;">Vendors / products / systems.</div>
          </div>
          <button class="btn" type="button" id="wlAddGroupBtn">+ Group</button>
        </div>

        <div style="padding:10px;">
          <input id="wlGroupSearch" placeholder="Search groups..."
            style="width:100%; border-radius: var(--r); padding:10px 12px;
              background: rgba(0,0,0,.18);
              border:1px solid var(--border);
              color: var(--text);
              font-weight:700;
            " />
        </div>

        <div id="wlGroupList" style="max-height: 420px; overflow:auto; padding: 6px 8px 12px 8px;"></div>

        <div style="padding:12px; border-top:1px solid var(--border); display:flex; gap:10px; flex-wrap:wrap;">
          <button class="btn ghost" type="button" id="wlExportJsonBtn">Export JSON</button>
          <button class="btn ghost" type="button" id="wlImportJsonBtn">Import JSON</button>
        </div>
      </div>

      <!-- RIGHT: Terms editor -->
      <div style="border:1px solid var(--border); border-radius: var(--r); background: rgba(0,0,0,.14); overflow:hidden;">
        <div style="padding:12px; border-bottom:1px solid var(--border); display:flex; align-items:center; justify-content:space-between; gap:10px; flex-wrap:wrap;">
          <div>
            <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
              <div style="font-weight:950;">Selected group</div>
              <span class="badge code" id="wlSelectedLabelBadge" style="display:none;"></span>
            </div>
            <div class="muted2" style="margin-top:4px;">Add terms (substring match). Regex terms allowed via <span class="mono">re:&lt;pattern&gt;</span>.</div>
          </div>

          <div style="display:flex; gap:10px; flex-wrap:wrap;">
            <button class="btn danger" type="button" id="wlDeleteGroupBtn" style="display:none;">Delete group</button>
            <button class="btn primary" type="button" id="wlSaveBtn">Save watchlist</button>
          </div>
        </div>

        <div style="padding:12px;">
          <div id="wlEmptyState" class="muted2" style="padding:18px; border:1px dashed var(--border); border-radius: var(--r); text-align:center;">
            Pick a group on the left, or create one.
          </div>

          <div id="wlEditor" style="display:none;">
            <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:flex-end;">
              <div style="flex:1; min-width: 220px;">
                <div class="muted2" style="margin-bottom:6px;">Group label</div>
                <input id="wlLabelInput"
                  style="width:100%; border-radius: var(--r); padding:10px 12px;
                    background: rgba(0,0,0,.18);
                    border:1px solid var(--border);
                    color: var(--text);
                    font-weight:800;
                  " />
              </div>

              <div style="flex:2; min-width: 260px;">
                <div class="muted2" style="margin-bottom:6px;">Add term</div>
                <div style="display:flex; gap:10px;">
                  <input id="wlTermInput" placeholder="e.g., exchange, owa, re:^cve-\d{4}-\d+$"
                    style="flex:1; border-radius: var(--r); padding:10px 12px;
                      background: rgba(0,0,0,.18);
                      border:1px solid var(--border);
                      color: var(--text);
                      font-weight:700;
                    " />
                  <button class="btn" type="button" id="wlAddTermBtn">+ Add</button>
                </div>
              </div>
            </div>

            <div style="margin-top:14px;">
              <div class="muted2" style="margin-bottom:8px;">Terms</div>
              <div id="wlChips" style="display:flex; gap:8px; flex-wrap:wrap;"></div>
              <div class="muted2" style="margin-top:10px;">Tip: keep terms specific. Broad single words can be noisy.</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    {% if watchlist_versions and watchlist_versions|length > 0 %}
      <div style="margin-top:14px; border:1px solid var(--border); border-radius: var(--r); background: rgba(0,0,0,.12); overflow:hidden;">
        <div style="padding:12px; border-bottom:1px solid var(--border);">
          <div style="font-weight:950;">Rollback</div>
          <div class="muted2" style="margin-top:4px;">Restore a previous watchlist version.</div>
        </div>
        <div style="padding:12px;">
          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Created (UTC)</th>
                  <th>Actor</th>
                  <th>Version ID</th>
                  <th style="text-align:right;">Action</th>
                </tr>
              </thead>
              <tbody>
                {% for v in watchlist_versions %}
                  <tr>
                    <td><span class="badge code">{{ v["created_utc"] }}</span></td>
                    <td class="wrapany">{{ v["actor_email"] }}</td>
                    <td><span class="mono wrapany">{{ v["version_id"] }}</span></td>
                    <td style="text-align:right;">
                      <form method="post" action="/admin/settings/watchlist/rollback/{{ v['version_id'] }}" style="display:inline;">
                        <button class="btn ghost" type="submit" onclick="return confirm('Rollback watchlist to this version?');">Rollback</button>
                      </form>
                    </td>
                  </tr>
                {% endfor %}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    {% endif %}
  </form>
</div>

<!-- Seed JSON from backend -->
<script>
(function(){
  // ---- state ----
  let state = {};
  let selected = null;

  const initialText = {{ (watchlist_text or "{}") | tojson }};
  function safeParse(text){
    try { return JSON.parse(text); } catch(e){ return null; }
  }

  function normalize(obj){
    // Expect mapping: { "Label": ["term", ...], ... }
    if (!obj || typeof obj !== "object" || Array.isArray(obj)) return {};
    const out = {};
    for (const k of Object.keys(obj)){
      const label = String(k || "").trim();
      if (!label) continue;
      const arr = obj[k];
      if (!Array.isArray(arr)) continue;
      const terms = [];
      const seen = new Set();
      for (const t of arr){
        const s = String(t || "").trim();
        if (!s) continue;
        if (seen.has(s)) continue;
        seen.add(s);
        terms.push(s);
      }
      if (terms.length) out[label] = terms;
      else out[label] = [];
    }
    return out;
  }

  function sortedLabels(){
    return Object.keys(state).sort((a,b)=>a.toLowerCase().localeCompare(b.toLowerCase()));
  }

  function setSelected(label){
    selected = label;
    render();
  }

  function renderGroupList(){
    const list = document.getElementById("wlGroupList");
    const q = (document.getElementById("wlGroupSearch").value || "").trim().toLowerCase();
    list.innerHTML = "";

    const labels = sortedLabels().filter(l => !q || l.toLowerCase().includes(q));
    if (!labels.length){
      const empty = document.createElement("div");
      empty.className = "muted2";
      empty.style.padding = "10px";
      empty.textContent = q ? "No groups match your search." : "No groups yet. Click + Group.";
      list.appendChild(empty);
      return;
    }

    for (const label of labels){
      const row = document.createElement("button");
      row.type = "button";
      row.style.width = "100%";
      row.style.textAlign = "left";
      row.style.border = "1px solid var(--border)";
      row.style.borderRadius = "var(--r)";
      row.style.padding = "10px 12px";
      row.style.margin = "6px 0";
      row.style.background = (label === selected) ? "rgba(71,227,183,.10)" : "rgba(0,0,0,.14)";
      row.style.color = "var(--text)";
      row.style.fontWeight = "900";
      row.style.display = "flex";
      row.style.justifyContent = "space-between";
      row.style.alignItems = "center";
      row.style.gap = "10px";

      const left = document.createElement("div");
      left.style.display = "flex";
      left.style.flexDirection = "column";
      left.style.gap = "4px";

      const title = document.createElement("div");
      title.textContent = label;

      const meta = document.createElement("div");
      meta.className = "muted2";
      const n = (state[label] || []).length;
      meta.textContent = n + (n === 1 ? " term" : " terms");

      left.appendChild(title);
      left.appendChild(meta);

      const badge = document.createElement("span");
      badge.className = "badge code";
      badge.textContent = (state[label] || []).length;

      row.appendChild(left);
      row.appendChild(badge);

      row.addEventListener("click", ()=>setSelected(label));
      list.appendChild(row);
    }
  }

  function renderEditor(){
    const empty = document.getElementById("wlEmptyState");
    const editor = document.getElementById("wlEditor");
    const delBtn = document.getElementById("wlDeleteGroupBtn");
    const badge = document.getElementById("wlSelectedLabelBadge");

    if (!selected || !(selected in state)){
      empty.style.display = "block";
      editor.style.display = "none";
      delBtn.style.display = "none";
      badge.style.display = "none";
      return;
    }

    empty.style.display = "none";
    editor.style.display = "block";
    delBtn.style.display = "inline-flex";
    badge.style.display = "inline-flex";
    badge.textContent = selected;

    // label input
    const labelInput = document.getElementById("wlLabelInput");
    labelInput.value = selected;

    // chips
    const chips = document.getElementById("wlChips");
    chips.innerHTML = "";
    const terms = state[selected] || [];
    if (!terms.length){
      const m = document.createElement("div");
      m.className = "muted2";
      m.textContent = "No terms yet. Add one above.";
      chips.appendChild(m);
      return;
    }

    for (const t of terms){
      const chip = document.createElement("div");
      chip.style.display = "inline-flex";
      chip.style.alignItems = "center";
      chip.style.gap = "8px";
      chip.style.padding = "8px 10px";
      chip.style.borderRadius = "999px";
      chip.style.border = "1px solid var(--border)";
      chip.style.background = "rgba(0,0,0,.18)";
      chip.style.fontWeight = "800";

      const txt = document.createElement("span");
      txt.textContent = t;

      const hint = document.createElement("span");
      hint.className = "muted2";
      hint.style.fontWeight = "900";
      hint.style.fontSize = "12px";
      if (String(t).toLowerCase().startsWith("re:")){
        hint.textContent = "regex";
      } else {
        hint.textContent = "term";
      }

      const x = document.createElement("button");
      x.type = "button";
      x.className = "btn ghost";
      x.style.padding = "6px 10px";
      x.textContent = "×";
      x.addEventListener("click", ()=>{
        state[selected] = (state[selected] || []).filter(v => v !== t);
        render();
      });

      chip.appendChild(txt);
      chip.appendChild(hint);
      chip.appendChild(x);
      chips.appendChild(chip);
    }
  }

  function render(){
    renderGroupList();
    renderEditor();
  }

  function ensureUniqueLabel(base){
    let name = base;
    let i = 2;
    while (name in state){
      name = base + " " + i;
      i += 1;
    }
    return name;
  }

  function addGroup(){
    const name = ensureUniqueLabel("New Group");
    state[name] = [];
    setSelected(name);
    // focus label input next tick
    setTimeout(()=>{ try{ document.getElementById("wlLabelInput").focus(); }catch(e){} }, 0);
  }

  function deleteGroup(){
    if (!selected || !(selected in state)) return;
    const ok = confirm("Delete group '" + selected + "'?");
    if (!ok) return;
    delete state[selected];
    selected = null;
    render();
  }

  function renameGroup(newName){
    const old = selected;
    const nn = String(newName || "").trim();
    if (!old || !(old in state)) return;
    if (!nn) { alert("Group label cannot be empty."); return; }
    if (nn.length > 80) { alert("Group label too long (max 80)."); return; }
    if (nn === old) return;
    if (nn in state) { alert("A group with that label already exists."); return; }

    state[nn] = state[old];
    delete state[old];
    selected = nn;
    render();
  }

  function addTerm(){
    if (!selected || !(selected in state)) return;
    const input = document.getElementById("wlTermInput");
    const term = String(input.value || "").trim();
    if (!term) return;
    if (term.length > 80) { alert("Term too long (max 80)."); return; }
    const arr = state[selected] || [];
    if (!arr.includes(term)) arr.push(term);
    state[selected] = arr;
    input.value = "";
    render();
  }

  function buildPayload(){
    // remove truly empty labels? keep them; backend validation might reject empty watchlist, not empty label.
    // We'll keep labels even if empty; admin.py validation will reject full empty watchlist anyway.
    return JSON.stringify(state, null, 2);
  }

  function submitSave(){
    // basic client sanity (backend is source of truth)
    const labels = Object.keys(state);
    if (!labels.length){
      alert("Watchlist is empty. Add at least one group with terms.");
      return;
    }
    const payload = buildPayload();
    document.getElementById("wlPayload").value = payload;
    document.getElementById("wlForm").submit();
  }

  function exportJson(){
    const payload = buildPayload();
    try{
      navigator.clipboard.writeText(payload);
      alert("Copied JSON to clipboard.");
    } catch(e){
      // fallback prompt
      window.prompt("Copy JSON:", payload);
    }
  }

  function importJson(){
    const raw = window.prompt("Paste watchlist JSON mapping here:");
    if (!raw) return;
    const obj = safeParse(raw);
    if (!obj){ alert("Invalid JSON."); return; }
    state = normalize(obj);
    selected = null;
    render();
  }

  // ---- init ----
  const parsed = safeParse(initialText);
  state = normalize(parsed || {});
  // auto-select first label if exists
  const labs = sortedLabels();
  if (labs.length) selected = labs[0];

  // ---- wire events ----
  document.getElementById("wlAddGroupBtn").addEventListener("click", addGroup);
  document.getElementById("wlDeleteGroupBtn").addEventListener("click", deleteGroup);

  document.getElementById("wlSaveBtn").addEventListener("click", submitSave);
  document.getElementById("wlSaveBtnTop").addEventListener("click", submitSave);

  document.getElementById("wlAddTermBtn").addEventListener("click", addTerm);

  document.getElementById("wlTermInput").addEventListener("keydown", function(e){
    if (e.key === "Enter"){
      e.preventDefault();
      addTerm();
    }
  });

  document.getElementById("wlLabelInput").addEventListener("blur", function(e){
    renameGroup(e.target.value);
  });
  document.getElementById("wlLabelInput").addEventListener("keydown", function(e){
    if (e.key === "Enter"){
      e.preventDefault();
      e.target.blur();
    }
  });

  document.getElementById("wlGroupSearch").addEventListener("input", renderGroupList);

  document.getElementById("wlExportJsonBtn").addEventListener("click", exportJson);
  document.getElementById("wlImportJsonBtn").addEventListener("click", importJson);

  render();
})();
</script>
"""




CAMPAIGN_TEMPLATE = r"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Campaign · {{ campaign.get("label","Campaign") }}</title>
  <style>
    body{ margin:0; font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; background:#0b0f18; color:#eaf1fb; }
    a{ color: inherit; text-decoration:none; }
    .wrap{ max-width: 1100px; margin: 0 auto; padding: 18px; }
    .card{ border:1px solid rgba(255,255,255,.10); border-radius: 14px; background: rgba(255,255,255,.03); padding: 14px; }
    .muted{ color: rgba(234,241,251,.70); font-weight:700; }
    .mono{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono","Courier New", monospace; font-size: 12px; color: rgba(234,241,251,.75); }
    .pill{ display:inline-flex; gap:8px; align-items:center; padding:6px 10px; border-radius:999px; border:1px solid rgba(255,255,255,.10); background: rgba(255,255,255,.03); font-weight:800; font-size:12px; }
    .grid{ margin-top:12px; display:grid; grid-template-columns: repeat(4, minmax(160px, 1fr)); gap:10px; }
    @media (max-width: 980px){ .grid{ grid-template-columns: 1fr 1fr; } }
    .story{ margin-top:10px; padding:12px; border:1px solid rgba(255,255,255,.08); border-radius: 14px; background: rgba(255,255,255,.02); }
    .title{ font-weight:950; font-size: 15px; letter-spacing:-.1px; }
    .row{ margin-top:8px; display:flex; gap:8px; flex-wrap:wrap; align-items:center; }
    .btn{ display:inline-flex; align-items:center; justify-content:center; gap:8px; padding:8px 10px; border-radius:12px; border:1px solid rgba(255,255,255,.10); background: rgba(255,255,255,.03); font-weight:900; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="card">
      <div style="display:flex; justify-content:space-between; gap:12px; flex-wrap:wrap; align-items:flex-end;">
        <div>
          <div style="font-size:20px; font-weight:980; letter-spacing:-.2px;">
            Campaign · {{ campaign.get("label","Campaign") }}
          </div>
          <div class="muted" style="margin-top:6px;">
            {{ campaign.get("summary","") }}
          </div>
          <div class="row" style="margin-top:10px;">
            <span class="pill">ID <span class="mono">{{ campaign_id }}</span></span>
            {% if campaign.get("first_seen_utc") %}<span class="pill">First seen <span class="mono">{{ campaign.get("first_seen_utc") }}</span></span>{% endif %}
            {% if campaign.get("last_seen_utc") %}<span class="pill">Last seen <span class="mono">{{ campaign.get("last_seen_utc") }}</span></span>{% endif %}
            <span class="pill">Stories <b>{{ campaign.get("story_count",0) }}</b></span>
          </div>
        </div>
        <div style="display:flex; gap:10px; flex-wrap:wrap;">
          <a class="btn" href="/">← Back to feed</a>
        </div>
      </div>

      <div class="grid">
        <div class="card" style="padding:12px;">
          <div class="muted">Top categories</div>
          <div style="margin-top:6px;">
            {% for c in campaign.get("top_categories",[]) %}
              <div class="mono">{{ c }}</div>
            {% endfor %}
            {% if (campaign.get("top_categories") or [])|length == 0 %}<div class="mono">—</div>{% endif %}
          </div>
        </div>
        <div class="card" style="padding:12px;">
          <div class="muted">Top keywords</div>
          <div style="margin-top:6px;">
            {% for k in campaign.get("top_keywords",[]) %}
              <div class="mono">{{ k }}</div>
            {% endfor %}
            {% if (campaign.get("top_keywords") or [])|length == 0 %}<div class="mono">—</div>{% endif %}
          </div>
        </div>
        <div class="card" style="padding:12px;">
          <div class="muted">Top CVEs</div>
          <div style="margin-top:6px;">
            {% for c in campaign.get("top_cves",[]) %}
              <div class="mono">{{ c }}</div>
            {% endfor %}
            {% if (campaign.get("top_cves") or [])|length == 0 %}<div class="mono">—</div>{% endif %}
          </div>
        </div>
        <div class="card" style="padding:12px;">
          <div class="muted">Top domains</div>
          <div style="margin-top:6px;">
            {% for d in campaign.get("top_domains",[]) %}
              <div class="mono">{{ d }}</div>
            {% endfor %}
            {% if (campaign.get("top_domains") or [])|length == 0 %}<div class="mono">—</div>{% endif %}
          </div>
        </div>
      </div>
    </div>

    <div style="margin-top:14px;">
      <div class="muted" style="font-weight:900; letter-spacing:.2px;">Related stories</div>

      {% for s in stories %}
        <div class="story">
          <div class="title"><a href="/story/{{ s.story_id }}">{{ s.title }}</a></div>
          <div class="row">
            <span class="pill">{{ (s.get("severity") or {}).get("level","") }}</span>
            {% if s.get("kev") %}<span class="pill">KEV</span>{% endif %}
            <span class="pill">{{ s.get("status","New") }}</span>
            <span class="pill">Sources <b>{{ s.get("sources_count",0) }}</b></span>
            {% if s.get("published") %}<span class="pill"><span class="mono">{{ s.get("published","") }}</span></span>{% endif %}
          </div>
          {% if s.get("summary") %}
            <div class="muted" style="margin-top:8px;">{{ s.summary }}</div>
          {% endif %}
        </div>
      {% endfor %}

      {% if stories|length == 0 %}
        <div class="card" style="margin-top:12px;">
          <div class="muted">No stories found for this campaign in the current snapshot window.</div>
        </div>
      {% endif %}
    </div>
  </div>
</body>
</html>
"""
