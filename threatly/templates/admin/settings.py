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