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