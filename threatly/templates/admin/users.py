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