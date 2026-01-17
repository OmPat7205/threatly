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