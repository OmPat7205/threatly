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