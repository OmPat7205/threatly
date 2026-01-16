# threatly/admin.py
from __future__ import annotations

import csv
import io
import json
import os
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

from flask import Blueprint, Response, abort, redirect, render_template_string, request, url_for

from threatly.config import STATE_DB_PATH, WATCHLIST_PATH
from threatly.rbac import require_perm, has_perm
from threatly.state_db import (
    create_user,
    ensure_admin_audit_table,
    get_admin_audit_kpis,
    get_user_by_email,
    list_audit_events,
    list_users,
    reset_user_password,
    set_user_role,
    toggle_user_active,
    write_audit_event as write_admin_audit_event,
)
from threatly.templates import (
    ADMIN_BASE_TEMPLATE,
    ADMIN_DASHBOARD_TEMPLATE,
    ADMIN_USERS_TEMPLATE,
    ADMIN_ROLES_TEMPLATE,
    ADMIN_AUDIT_TEMPLATE,
    ADMIN_SETTINGS_TEMPLATE,
)

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

TENANT_ID_DEFAULT = "default"


# -----------------------------
# DB helpers (admin-only tables)
# -----------------------------
def _db() -> sqlite3.Connection:
    conn = sqlite3.connect(STATE_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON;")
    # Optional quality-of-life for concurrency
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
    except Exception:
        pass
    return conn


def ensure_admin_tables() -> None:
    """
    Admin-owned tables:
      - story_seen_events: optional per-review event log (needed to show "who reviewed")
      - org_config: current tenant config blobs (watchlist, etc.)
      - org_config_versions: append-only versions for config rollback

    Admin audit is handled by threatly.state_db (admin_audit_events).
    """
    ensure_admin_audit_table()

    conn = _db()
    try:
        # per-review trail table (admin-only viewing).
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS story_seen_events(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              story_id TEXT NOT NULL,
              user_id TEXT,
              user_email TEXT,
              ts_utc TEXT NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_story_seen_events_story ON story_seen_events(story_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_story_seen_events_email ON story_seen_events(user_email)")

        # org config (current)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS org_config(
              tenant_id TEXT NOT NULL DEFAULT 'default',
              k TEXT NOT NULL,
              value_json TEXT NOT NULL,
              updated_utc TEXT NOT NULL,
              updated_by_user_id TEXT NOT NULL DEFAULT '',
              updated_by_email TEXT NOT NULL DEFAULT '',
              PRIMARY KEY (tenant_id, k)
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_org_config_tenant_key ON org_config(tenant_id, k)")

        # org config versions (append-only)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS org_config_versions(
              version_id TEXT PRIMARY KEY,
              tenant_id TEXT NOT NULL DEFAULT 'default',
              k TEXT NOT NULL,
              value_json TEXT NOT NULL,
              actor_user_id TEXT NOT NULL DEFAULT '',
              actor_email TEXT NOT NULL DEFAULT '',
              ip TEXT NOT NULL DEFAULT '',
              user_agent TEXT NOT NULL DEFAULT '',
              created_utc TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_org_cfg_ver_tenant_key ON org_config_versions(tenant_id, k, created_utc)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_org_cfg_ver_tenant_created ON org_config_versions(tenant_id, created_utc)"
        )

        conn.commit()
    finally:
        conn.close()


def _me() -> Dict[str, Any]:
    from flask import g

    u = getattr(g, "user", None) or {}
    return {
        "user_id": u.get("user_id", ""),
        "email": u.get("email", ""),
        "role": u.get("role", ""),
        "is_active": int(u.get("is_active", 0) or 0),
    }


def _client_ctx() -> Tuple[str, str]:
    ip = (request.headers.get("X-Forwarded-For") or request.remote_addr or "").split(",")[0].strip()
    ua = (request.headers.get("User-Agent") or "")[:300]
    return (ip, ua)


def _nav(active: str) -> Dict[str, Any]:
    return {
        "active": active,
        "can_manage_users": has_perm("manage_users"),
    }


def _render_admin(content_template: str, *, title: str, active: str, **ctx: Any):
    me = _me()
    base_ctx = dict(
        title=title,
        active=active,
        me=me,
        nav=_nav(active),
        **ctx,
    )

    inner_html = render_template_string(content_template, **base_ctx)

    return render_template_string(
        ADMIN_BASE_TEMPLATE,
        **base_ctx,
        content=inner_html,
    )


# -----------------------------
# Watchlist settings (enterprise)
# -----------------------------
def _now_iso_z() -> str:
    return _iso_z(datetime.utcnow())

def _iso_z(dt: datetime) -> str:
    """
    Return an ISO-8601 UTC timestamp with trailing 'Z', seconds precision.
    Example: 2026-01-16T21:34:12Z
    """
    return dt.replace(tzinfo=timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _sha1_id(s: str) -> str:
    import hashlib

    return hashlib.sha1((s or "").encode("utf-8", errors="ignore")).hexdigest()[:20]


def _dedupe_list(xs: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for x in xs:
        if x in seen:
            continue
        seen.add(x)
        out.append(x)
    return out


def _normalize_watchlist_obj(obj: Any) -> Dict[str, List[str]]:
    """
    Accepts:
      - dict: { "Label": ["term", ...], ... }   (preferred)
      - legacy dict: {"terms":[...]} or {"watchlist":[...]} etc. (converted)
      - list: ["term", ...] (converted into {"Watchlist": [...]})
    Returns normalized mapping with de-duped terms.
    """
    if isinstance(obj, dict):
        # legacy wrapper formats
        for k in ("terms", "watchlist", "items", "keywords"):
            if isinstance(obj.get(k), list):
                terms = [str(x).strip() for x in obj.get(k) if str(x).strip()]
                terms = _dedupe_list(terms)
                return {"Watchlist": terms}

        out: Dict[str, List[str]] = {}
        for label, terms in obj.items():
            if not isinstance(label, str):
                continue
            if not isinstance(terms, list):
                continue
            name = label.strip()
            if not name:
                continue
            clean = [str(x).strip() for x in terms if str(x).strip()]
            clean = _dedupe_list(clean)
            if clean:
                out[name] = clean
        return out

    if isinstance(obj, list):
        terms = _dedupe_list([str(x).strip() for x in obj if str(x).strip()])
        return {"Watchlist": terms} if terms else {}

    return {}


def _validate_watchlist(wl: Dict[str, List[str]]) -> Tuple[bool, List[str], Dict[str, List[str]]]:
    """
    Validation + normalization:
      - caps sizes (labels/terms)
      - trims labels/terms
      - removes empties
      - de-dupes
    """
    errs: List[str] = []
    normalized: Dict[str, List[str]] = {}

    if not isinstance(wl, dict):
        return False, ["Watchlist must be a JSON object (mapping labels to term lists)."], {}

    # caps (more realistic than 80/50 for enterprise configs)
    max_labels = 200
    max_terms_per_label = 200
    max_label_len = 80
    max_term_len = 160
    max_regex_len = 300

    if len(wl) > max_labels:
        errs.append(f"Too many labels (max {max_labels}).")

    for label, terms in wl.items():
        if not isinstance(label, str):
            continue
        name = label.strip()
        if not name:
            continue
        if len(name) > max_label_len:
            errs.append(f"Label too long (max {max_label_len}): {name[:max_label_len]}")
            continue

        if not isinstance(terms, list):
            errs.append(f"Label '{name}' must map to a list of terms.")
            continue

        clean: List[str] = []
        for t in terms[:max_terms_per_label]:
            s = (str(t) or "").strip()
            if not s:
                continue

            # allow longer regexes than plain terms
            if s.lower().startswith("re:"):
                if len(s) > max_regex_len:
                    errs.append(f"Regex too long (max {max_regex_len}) under '{name}': {s[:max_term_len]}")
                    continue
            else:
                if len(s) > max_term_len:
                    errs.append(f"Term too long (max {max_term_len}) under '{name}': {s[:max_term_len]}")
                    continue

            clean.append(s)

        clean = _dedupe_list(clean)
        if clean:
            normalized[name] = clean

    if not normalized:
        errs.append("Watchlist is empty after normalization.")

    ok = len(errs) == 0
    return ok, errs, normalized


def _broad_term_warnings(wl: Dict[str, List[str]]) -> List[str]:
    """
    Warnings (not hard errors) for noisy terms.
    """
    warnings: List[str] = []
    noisy_single_words = {"azure", "amazon", "google", "windows", "linux", "microsoft"}

    for label, terms in (wl or {}).items():
        for t in terms:
            s = (t or "").strip().lower()
            if s.startswith("re:"):
                continue
            if len(s) <= 2:
                warnings.append(f"'{label}': term '{t}' is very short and likely noisy.")
            if " " not in s and s in noisy_single_words:
                warnings.append(f"'{label}': term '{t}' is very broad and may match a lot of unrelated stories.")
    return warnings[:20]


def _invalidate_watchlist_runtime_cache() -> None:
    """
    Your runtime loader (threatly.watchlist.load_watchlist) uses a 60s cache.
    If invalidate_watchlist_cache() exists, call it so changes apply immediately.
    """
    try:
        from threatly.watchlist import invalidate_watchlist_cache  # type: ignore

        invalidate_watchlist_cache()
    except Exception:
        # If not implemented yet, runtime will refresh within cache TTL.
        pass


def _org_get_config(key: str, *, tenant_id: str = TENANT_ID_DEFAULT) -> Optional[Dict[str, Any]]:
    ensure_admin_tables()
    conn = _db()
    try:
        row = conn.execute(
            """
            SELECT value_json, updated_utc, updated_by_user_id, updated_by_email
            FROM org_config
            WHERE tenant_id = ? AND k = ?
            LIMIT 1
            """,
            (tenant_id, key),
        ).fetchone()
        if not row:
            return None
        return {
            "value_json": str(row["value_json"] or ""),
            "updated_utc": str(row["updated_utc"] or ""),
            "updated_by_user_id": str(row["updated_by_user_id"] or ""),
            "updated_by_email": str(row["updated_by_email"] or ""),
        }
    finally:
        conn.close()


def _org_list_versions(
    key: str, *, tenant_id: str = TENANT_ID_DEFAULT, limit: int = 20
) -> List[Dict[str, Any]]:
    ensure_admin_tables()
    lim = max(1, min(int(limit or 20), 100))
    conn = _db()
    try:
        rows = conn.execute(
            """
            SELECT version_id, created_utc, actor_user_id, actor_email
            FROM org_config_versions
            WHERE tenant_id = ? AND k = ?
            ORDER BY created_utc DESC
            LIMIT ?
            """,
            (tenant_id, key, lim),
        ).fetchall()
        out: List[Dict[str, Any]] = []
        for r in rows:
            out.append(
                {
                    "version_id": str(r["version_id"]),
                    "created_utc": str(r["created_utc"] or ""),
                    "actor_user_id": str(r["actor_user_id"] or ""),
                    "actor_email": str(r["actor_email"] or ""),
                }
            )
        return out
    finally:
        conn.close()


def _org_get_version(version_id: str, *, tenant_id: str = TENANT_ID_DEFAULT) -> Optional[Dict[str, Any]]:
    ensure_admin_tables()
    vid = (version_id or "").strip()
    if not vid:
        return None
    conn = _db()
    try:
        row = conn.execute(
            """
            SELECT version_id, k, value_json, created_utc, actor_user_id, actor_email
            FROM org_config_versions
            WHERE tenant_id = ? AND version_id = ?
            LIMIT 1
            """,
            (tenant_id, vid),
        ).fetchone()
        if not row:
            return None
        return {
            "version_id": str(row["version_id"]),
            "k": str(row["k"]),
            "value_json": str(row["value_json"] or ""),
            "created_utc": str(row["created_utc"] or ""),
            "actor_user_id": str(row["actor_user_id"] or ""),
            "actor_email": str(row["actor_email"] or ""),
        }
    finally:
        conn.close()


def _org_set_config_with_versioning(
    key: str,
    value_json: str,
    *,
    actor_user_id: str,
    actor_email: str,
    ip: str,
    user_agent: str,
    tenant_id: str = TENANT_ID_DEFAULT,
) -> None:
    """
    Writes a version row (previous value) and then upserts the current value.
    """
    ensure_admin_tables()
    now = _now_iso_z()

    conn = _db()
    try:
        conn.execute("BEGIN")

        prev = conn.execute(
            "SELECT value_json FROM org_config WHERE tenant_id = ? AND k = ? LIMIT 1",
            (tenant_id, key),
        ).fetchone()
        prev_json = str(prev["value_json"] or "") if prev else ""

        if prev_json:
            vid = _sha1_id(f"{tenant_id}|{key}|{now}|{actor_user_id}|{prev_json}")
            conn.execute(
                """
                INSERT OR IGNORE INTO org_config_versions(
                  version_id, tenant_id, k, value_json, actor_user_id, actor_email, ip, user_agent, created_utc
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    vid,
                    tenant_id,
                    key,
                    prev_json,
                    (actor_user_id or "")[:64],
                    (actor_email or "")[:254],
                    (ip or "")[:200],
                    (user_agent or "")[:300],
                    now,
                ),
            )

        conn.execute(
            """
            INSERT INTO org_config(tenant_id, k, value_json, updated_utc, updated_by_user_id, updated_by_email)
            VALUES(?, ?, ?, ?, ?, ?)
            ON CONFLICT(tenant_id, k) DO UPDATE SET
              value_json=excluded.value_json,
              updated_utc=excluded.updated_utc,
              updated_by_user_id=excluded.updated_by_user_id,
              updated_by_email=excluded.updated_by_email
            """,
            (
                tenant_id,
                key,
                value_json,
                now,
                (actor_user_id or "")[:64],
                (actor_email or "")[:254],
            ),
        )

        conn.execute("COMMIT")
    except Exception:
        try:
            conn.execute("ROLLBACK")
        except Exception:
            pass
        raise
    finally:
        conn.close()


def _load_watchlist_for_editor(*, tenant_id: str = TENANT_ID_DEFAULT) -> Dict[str, List[str]]:
    """
    Source of truth (today):
      - file WATCHLIST_PATH if it exists and is valid mapping
      - else org_config('watchlist') if present
      - else DEFAULT_WATCHLIST from threatly.watchlist

    We keep file support because your runtime loader currently reads WATCHLIST_PATH.
    """
    # 1) file (preferred for runtime compatibility)
    if os.path.exists(WATCHLIST_PATH):
        try:
            with open(WATCHLIST_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            wl = _normalize_watchlist_obj(data)
            if wl:
                return wl
        except Exception:
            pass

    # 2) org config
    cfg = _org_get_config("watchlist", tenant_id=tenant_id)
    if cfg and cfg.get("value_json"):
        try:
            wl = _normalize_watchlist_obj(json.loads(cfg["value_json"]))
            if wl:
                return wl
        except Exception:
            pass

    # 3) defaults
    try:
        from threatly.watchlist import DEFAULT_WATCHLIST as WL_DEFAULTS

        return dict(WL_DEFAULTS)
    except Exception:
        return {}


def _save_watchlist_file(wl: Dict[str, List[str]]) -> None:
    os.makedirs(os.path.dirname(WATCHLIST_PATH) or ".", exist_ok=True)
    with open(WATCHLIST_PATH, "w", encoding="utf-8") as f:
        json.dump(wl, f, indent=2, ensure_ascii=False)


def _watchlist_file_updated_utc() -> str:
    """
    For UI display when DB metadata doesn't exist yet.
    """
    try:
        if os.path.exists(WATCHLIST_PATH):
            ts = os.path.getmtime(WATCHLIST_PATH)
            # show UTC-ish; for display only
            return datetime.utcfromtimestamp(ts).isoformat(timespec="seconds") + "Z"
    except Exception:
        pass
    return ""


# -----------------------------
# Routes
# -----------------------------

@admin_bp.get("/")
@require_perm("view_admin")
def admin_home():
    ensure_admin_tables()

    # ---- user state KPIs (not time-windowed) ----
    users = list_users()
    total = len(users)
    active = sum(1 for u in users if int(u.get("is_active", 0) or 0) == 1)
    disabled = total - active
    admins = sum(1 for u in users if (u.get("role") or "") == "admin")

    # ---- helpers ----
    def _parse_date_yyyy_mm_dd(s: str) -> Optional[datetime]:
        """
        Parse HTML <input type="date"> value: YYYY-MM-DD
        Returns naive datetime at 00:00:00 if valid else None.
        """
        try:
            s = (s or "").strip()
            if not s:
                return None
            return datetime.strptime(s, "%Y-%m-%d")
        except Exception:
            return None
    def _q(name: str, default: str = "") -> str:
        vals = request.args.getlist(name)
        return (vals[-1] if vals else default).strip()

    # ---- time window selection (query params) ----
    w = _q("w", "24h").lower()
    raw_from = _q("from", "")
    raw_to = _q("to", "")


    now = datetime.utcnow()

    # defaults
    start_dt = now - timedelta(days=1)
    end_dt = now
    clean_from = raw_from
    clean_to = raw_to

    if w == "7d":
        start_dt = now - timedelta(days=7)
        end_dt = now

    elif w == "30d":
        start_dt = now - timedelta(days=30)
        end_dt = now

    elif w == "90d":
        start_dt = now - timedelta(days=90)
        end_dt = now

   
    elif w == "custom":
        d_from = _parse_date_yyyy_mm_dd(raw_from)
        d_to = _parse_date_yyyy_mm_dd(raw_to)

        # Stay in custom mode even if dates are missing/invalid
        if d_from and d_to:
            start_dt = d_from
            end_dt = d_to + timedelta(days=1) - timedelta(seconds=1)

            # if user flipped them, swap
            if end_dt < start_dt:
                start_dt, end_dt = end_dt, start_dt

            # Clamp future end dates (e.g., selecting "today") to now
            if end_dt > now:
                end_dt = now
        else:
            # keep UI in Custom, but show last 24h data until user selects dates
            start_dt = now - timedelta(days=1)
            end_dt = now
            clean_from = raw_from if d_from else ""
            clean_to = raw_to if d_to else ""


    else:
        # any unknown window -> 24h
        w = "24h"
        start_dt = now - timedelta(days=1)
        end_dt = now
        clean_from = ""
        clean_to = ""









    # Normalize to ISO strings (consistent with created_utc storage)
    start_iso = _iso_z(start_dt)
    end_iso = _iso_z(end_dt)


    # ---- audit KPIs windowed ----
    audit_kpis = get_admin_audit_kpis(
        tenant_id=TENANT_ID_DEFAULT,
        start_utc=start_iso,
        end_utc=end_iso,
        top_n=10,
    )

    return _render_admin(
        ADMIN_DASHBOARD_TEMPLATE,
        title="Admin",
        active="dashboard",
        window={
            "w": w,
            "from": clean_from,
            "to": clean_to,
            "start_utc": start_iso,
            "end_utc": end_iso,
        },
        kpis={
            # state KPIs (all-time)
            "total_users": total,
            "active_users": active,
            "disabled_users": disabled,
            "admin_users": admins,

            # windowed audit KPIs
            "audit_window": int(audit_kpis.get("audit_window", 0)),
            "top_actions": audit_kpis.get("top_actions", []),
            "last_event": audit_kpis.get("last_event", {}),
            "login_fail_window": int(audit_kpis.get("login_fail_window", 0)),
            "privileged_window": int(audit_kpis.get("privileged_window", 0)),
        },
    )


from flask import jsonify

def _query_dashboard_series(*, tenant_id: str, start_utc: str, end_utc: str, bucket: str) -> Dict[str, Any]:
    """
    Returns labels + 3 series:
      - audit_volume
      - login_failures
      - privileged_actions
    """
    conn = _db()
    try:
        # created_utc stored as ISO string; normalize for SQLite datetime
        dt_expr = "datetime(substr(replace(replace(created_utc,'T',' '),'Z',''),1,19))"

        if bucket == "hour":
            key_expr = f"strftime('%Y-%m-%d %H:00', {dt_expr})"
        else:
            key_expr = f"strftime('%Y-%m-%d', {dt_expr})"

        # total audit volume
        rows_total = conn.execute(
            f"""
            SELECT {key_expr} AS k, COUNT(*) AS n
            FROM admin_audit_events
            WHERE tenant_id = ?
              AND {dt_expr} >= datetime(substr(replace(replace(?,'T',' '),'Z',''),1,19))
              AND {dt_expr} <= datetime(substr(replace(replace(?,'T',' '),'Z',''),1,19))
            GROUP BY k
            ORDER BY k ASC
            """,
            (tenant_id, start_utc, end_utc),
        ).fetchall()

        # login failures (login_attempt with ok=false in details_json)
        rows_fail = conn.execute(
            f"""
            SELECT {key_expr} AS k, COUNT(*) AS n
            FROM admin_audit_events
            WHERE tenant_id = ?
              AND action = 'login_attempt'
              AND {dt_expr} >= datetime(substr(replace(replace(?,'T',' '),'Z',''),1,19))
              AND {dt_expr} <= datetime(substr(replace(replace(?,'T',' '),'Z',''),1,19))
              AND (
                instr(lower(COALESCE(details_json,'')), '"ok":false') > 0
                OR instr(lower(COALESCE(details_json,'')), '"ok":0') > 0
              )
            GROUP BY k
            ORDER BY k ASC
            """,
            (tenant_id, start_utc, end_utc),
        ).fetchall()

        privileged = (
            "user_create",
            "user_toggle_active",
            "user_set_role",
            "user_reset_password",
            "watchlist_update",
            "watchlist_rollback",
            "meta_set",
        )
        ph = ",".join(["?"] * len(privileged))
        rows_priv = conn.execute(
            f"""
            SELECT {key_expr} AS k, COUNT(*) AS n
            FROM admin_audit_events
            WHERE tenant_id = ?
              AND action IN ({ph})
              AND {dt_expr} >= datetime(substr(replace(replace(?,'T',' '),'Z',''),1,19))
              AND {dt_expr} <= datetime(substr(replace(replace(?,'T',' '),'Z',''),1,19))
            GROUP BY k
            ORDER BY k ASC
            """,
            (tenant_id, *privileged, start_utc, end_utc),
        ).fetchall()

        def to_map(rows):
            return {str(r["k"]): int(r["n"]) for r in rows if r["k"]}

        m_total = to_map(rows_total)
        m_fail = to_map(rows_fail)
        m_priv = to_map(rows_priv)

        def _parse_bucket_label(s: str) -> datetime:
            # labels are either "YYYY-MM-DD HH:00" or "YYYY-MM-DD"
            if len(s) > 10:
                return datetime.strptime(s, "%Y-%m-%d %H:%M")
            return datetime.strptime(s, "%Y-%m-%d")

        labels = sorted(set(m_total) | set(m_fail) | set(m_priv), key=_parse_bucket_label)
       
        return {
            "labels": labels,
            "series": {
                "audit_volume": [m_total.get(k, 0) for k in labels],
                "login_failures": [m_fail.get(k, 0) for k in labels],
                "privileged_actions": [m_priv.get(k, 0) for k in labels],
            },
            "meta": {"bucket": bucket, "start_utc": start_utc, "end_utc": end_utc},
        }
    finally:
        conn.close()


@admin_bp.get("/api/dashboard/series")
@require_perm("view_admin")
def admin_dashboard_series():
    ensure_admin_tables()

    def _q(name: str, default: str = "") -> str:
        vals = request.args.getlist(name)
        return (vals[-1] if vals else default).strip()

    w = _q("w", "24h").lower()
    raw_from = _q("from", "")
    raw_to = _q("to", "")


    now = datetime.utcnow()
    start_dt = now - timedelta(days=1)
    end_dt = now

    def _parse_date(s: str) -> Optional[datetime]:
        try:
            return datetime.strptime((s or "").strip(), "%Y-%m-%d")
        except Exception:
            return None

    if w == "7d":
        start_dt = now - timedelta(days=7)
    elif w == "30d":
        start_dt = now - timedelta(days=30)
    elif w == "90d":
        start_dt = now - timedelta(days=90)

    elif w == "custom":
        d_from = _parse_date(raw_from)
        d_to = _parse_date(raw_to)

        # Stay in custom even if dates are missing.
        if d_from and d_to:
            start_dt = d_from
            end_dt = d_to + timedelta(days=1) - timedelta(seconds=1)

            # If user flipped them, swap (match admin_home behavior)
            if end_dt < start_dt:
                start_dt, end_dt = end_dt, start_dt

            # Clamp future end dates (e.g., selecting "today") to now
            if end_dt > now:
                end_dt = now
        else:
            start_dt = now - timedelta(days=1)
            end_dt = now




    start_iso = _iso_z(start_dt)
    end_iso = _iso_z(end_dt)


    bucket = "hour" if (end_dt - start_dt) <= timedelta(days=2) else "day"

    data = _query_dashboard_series(
        tenant_id=TENANT_ID_DEFAULT,
        start_utc=start_iso,
        end_utc=end_iso,
        bucket=bucket,
    )

    data["debug"] = {
        "req_w": w,
        "req_from": raw_from,
        "req_to": raw_to,
        "computed_start_iso": start_iso,
        "computed_end_iso": end_iso,
        "bucket": bucket,
    }

    return jsonify(data)



# -----------------------------
# Reviews (who reviewed)
# -----------------------------
@admin_bp.get("/reviews/<story_id>")
@require_perm("view_admin")
def admin_reviews(story_id: str):
    """
    Shows who reviewed a story (admin-only).
    Requires `story_seen_events` to be populated by your reviewed toggle code.
    """
    ensure_admin_tables()

    conn = _db()
    try:
        rows = conn.execute(
            """
            SELECT
              COALESCE(s.user_email,'') AS user_email,
              COALESCE(u.role,'') AS role,
              COUNT(*) AS review_count,
              MAX(s.ts_utc) AS last_review_utc
            FROM story_seen_events s
            LEFT JOIN users u
              ON LOWER(u.email) = LOWER(COALESCE(s.user_email,''))
            WHERE s.story_id = ?
            GROUP BY COALESCE(s.user_email,''), COALESCE(u.role,'')
            ORDER BY review_count DESC, last_review_utc DESC
            """,
            (story_id,),
        ).fetchall()

        total = conn.execute(
            "SELECT COUNT(*) AS c FROM story_seen_events WHERE story_id = ?",
            (story_id,),
        ).fetchone()
        total_count = int(total["c"]) if total else 0
    finally:
        conn.close()

    return _render_admin(
        r"""
        <div class="card">
          <div style="display:flex; justify-content:space-between; gap:10px; flex-wrap:wrap; align-items:flex-end;">
            <div>
              <div style="font-size:20px; font-weight:950;">Reviews</div>
              <div class="muted" style="margin-top:6px;">
                Story ID:
                <span class="mono">{{ story_id }}</span>
                · Total events: <span class="badge code">{{ total_count }}</span>
              </div>
              <div class="muted" style="margin-top:6px;">
                Note: if this is empty, your “Mark reviewed” code is not logging per-review events yet.
              </div>
            </div>

            <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
              <a class="btn" href="/admin/reviews/{{ story_id }}/export.csv">Download CSV</a>
              <a class="btn ghost" href="/">← Back to feed</a>
            </div>
          </div>

          <div class="table-wrap" style="margin-top:14px;">
            <table>
              <thead>
                <tr>
                  <th>Reviewer</th>
                  <th>Count</th>
                  <th>Last reviewed (UTC)</th>
                </tr>
              </thead>
              <tbody>
                {% if rows and rows|length > 0 %}
                  {% for r in rows %}
                    <tr>
                      <td style="font-weight:900;">
                        <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
                          <span class="wrapany">{{ r["user_email"] if r["user_email"] else "Unknown" }}</span>
                          {% if r["role"] %}
                            <span class="badge code">{{ r["role"] }}</span>
                          {% endif %}
                        </div>
                      </td>

                      <td>
                        <span class="badge code">{{ r["review_count"] }}</span>
                      </td>

                      <td>
                        {% if r["last_review_utc"] %}
                          <span class="badge code">{{ r["last_review_utc"] }}</span>
                        {% else %}
                          <span class="muted2">—</span>
                        {% endif %}
                      </td>
                    </tr>
                  {% endfor %}
                {% else %}
                  <tr>
                    <td colspan="3" class="muted">No review events logged for this story yet.</td>
                  </tr>
                {% endif %}
              </tbody>
            </table>
          </div>

          <div class="muted" style="margin-top:12px;">
            Compliance export (global): <span class="mono">/admin/reviews/export.csv?days=30</span>
          </div>
        </div>
        """,
        title="Admin · Reviews",
        active="audit",
        story_id=story_id,
        rows=rows,
        total_count=total_count,
    )


@admin_bp.get("/reviews/<story_id>/export.csv")
@require_perm("view_admin")
def admin_reviews_export_csv(story_id: str):
    """
    CSV export of per-review events for one story.
    """
    ensure_admin_tables()
    conn = _db()
    try:
        rows = conn.execute(
            """
            SELECT
              s.story_id,
              COALESCE(s.user_email,'') AS user_email,
              COALESCE(u.role,'') AS role,
              s.ts_utc
            FROM story_seen_events s
            LEFT JOIN users u
              ON LOWER(u.email) = LOWER(COALESCE(s.user_email,''))
            WHERE s.story_id = ?
            ORDER BY s.ts_utc DESC
            """,
            (story_id,),
        ).fetchall()
    finally:
        conn.close()

    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["story_id", "reviewer_email", "reviewer_role", "reviewed_ts_utc"])
    for r in rows:
        w.writerow([r["story_id"], r["user_email"], r["role"], r["ts_utc"]])

    return Response(
        out.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=threatly_reviews_{story_id}.csv"},
    )


@admin_bp.get("/reviews/export.csv")
@require_perm("view_admin")
def admin_reviews_export_csv_global():
    """
    Global CSV export (last N days). Default 30 days.
    Uses lexicographic compare on ISO-8601 UTC timestamps (works if ts_utc is consistently ISO with Z).
    """
    ensure_admin_tables()

    days_raw = (request.args.get("days") or "30").strip()
    try:
        days = int(days_raw)
    except Exception:
        days = 30
    days = max(1, min(days, 365))

    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat(timespec="seconds") + "Z"

    conn = _db()
    try:
        rows = conn.execute(
            """
            SELECT
              s.story_id,
              COALESCE(s.user_email,'') AS user_email,
              COALESCE(u.role,'') AS role,
              s.ts_utc
            FROM story_seen_events s
            LEFT JOIN users u
              ON LOWER(u.email) = LOWER(COALESCE(s.user_email,''))
            WHERE s.ts_utc >= ?
            ORDER BY s.ts_utc DESC
            """,
            (cutoff,),
        ).fetchall()
    finally:
        conn.close()

    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["story_id", "reviewer_email", "reviewer_role", "reviewed_ts_utc"])
    for r in rows:
        w.writerow([r["story_id"], r["user_email"], r["role"], r["ts_utc"]])

    return Response(
        out.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=threatly_reviews_last_{days}_days.csv"},
    )


# -----------------------------
# Users
# -----------------------------
@admin_bp.get("/users")
@require_perm("manage_users")
def admin_users():
    users = list_users()

    q = (request.args.get("q") or "").strip().lower()
    role = (request.args.get("role") or "").strip().lower()
    active = (request.args.get("active") or "").strip()

    if q:
        users = [u for u in users if q in (u.get("email", "").lower() + " " + u.get("user_id", "").lower())]
    if role in ("viewer", "analyst", "admin"):
        users = [u for u in users if (u.get("role") or "") == role]
    if active in ("1", "0"):
        users = [u for u in users if str(int(u.get("is_active", 0) or 0)) == active]

    users.sort(key=lambda u: (u.get("email") or "").lower())

    return _render_admin(
        ADMIN_USERS_TEMPLATE,
        title="Admin · Users",
        active="users",
        users=users,
        q=q,
        role=role,
        active_filter=active,
    )


@admin_bp.post("/users/create")
@require_perm("manage_users")
def admin_user_create():
    email = (request.form.get("email") or "").strip().lower()
    role = (request.form.get("role") or "viewer").strip().lower()
    password = (request.form.get("password") or "")

    if not email or "@" not in email:
        abort(400)
    if role not in ("viewer", "analyst", "admin"):
        abort(400)
    if len(password) < 10:
        abort(400)

    if get_user_by_email(email):
        return redirect(url_for("admin.admin_users", q=email))

    u = create_user(email=email, password=password, role=role)

    me = _me()
    ip, ua = _client_ctx()
    write_admin_audit_event(
        "user_create",
        actor_user_id=me.get("user_id", ""),
        actor_email=me.get("email", ""),
        target_type="user",
        target_id=u.get("user_id", ""),
        details={"email": email, "role": role},
        ip=ip,
        user_agent=ua,
    )

    return redirect(url_for("admin.admin_users", q=email))


@admin_bp.post("/users/<user_id>/toggle")
@require_perm("manage_users")
def admin_user_toggle(user_id: str):
    me = _me()
    if user_id == me.get("user_id"):
        return redirect(url_for("admin.admin_users"))

    new_state = toggle_user_active(user_id)

    ip, ua = _client_ctx()
    write_admin_audit_event(
        "user_toggle_active",
        actor_user_id=me.get("user_id", ""),
        actor_email=me.get("email", ""),
        target_type="user",
        target_id=user_id,
        details={"is_active": int(new_state)},
        ip=ip,
        user_agent=ua,
    )
    return redirect(url_for("admin.admin_users"))


@admin_bp.post("/users/<user_id>/role")
@require_perm("manage_users")
def admin_user_set_role(user_id: str):
    role = (request.form.get("role") or "").strip().lower()
    if role not in ("viewer", "analyst", "admin"):
        abort(400)

    me = _me()
    if user_id == me.get("user_id") and role != "admin":
        return redirect(url_for("admin.admin_users"))

    set_user_role(user_id, role)

    ip, ua = _client_ctx()
    write_admin_audit_event(
        "user_set_role",
        actor_user_id=me.get("user_id", ""),
        actor_email=me.get("email", ""),
        target_type="user",
        target_id=user_id,
        details={"role": role},
        ip=ip,
        user_agent=ua,
    )
    return redirect(url_for("admin.admin_users"))


@admin_bp.post("/users/<user_id>/reset_password")
@require_perm("manage_users")
def admin_user_reset_password(user_id: str):
    password = (request.form.get("password") or "")
    if len(password) < 10:
        abort(400)

    reset_user_password(user_id, password)

    me = _me()
    ip, ua = _client_ctx()
    write_admin_audit_event(
        "user_reset_password",
        actor_user_id=me.get("user_id", ""),
        actor_email=me.get("email", ""),
        target_type="user",
        target_id=user_id,
        details={"note": "temporary_password_set"},
        ip=ip,
        user_agent=ua,
    )
    return redirect(url_for("admin.admin_users"))


# -----------------------------
# Roles
# -----------------------------
@admin_bp.get("/roles")
@require_perm("view_admin")
def admin_roles():
    from threatly.rbac import ROLE_PERMS

    roles = [{"role": r, "perms": sorted(list(perms))} for r, perms in ROLE_PERMS.items()]
    roles.sort(key=lambda x: x["role"])
    return _render_admin(
        ADMIN_ROLES_TEMPLATE,
        title="Admin · Roles",
        active="roles",
        roles=roles,
    )


# -----------------------------
# Audit
# -----------------------------
@admin_bp.get("/audit")
@require_perm("view_admin")
def admin_audit():
    """
    Admin audit now uses state_db.admin_audit_events (enterprise, tenant-ready).
    """
    ensure_admin_tables()

    q = (request.args.get("q") or "").strip().lower()
    event = (request.args.get("event") or "").strip().lower()

    rows = list_audit_events(limit=300)

    # map to template-friendly shape (similar to your old audit_events table)
    events: List[Dict[str, Any]] = []
    for r in rows:
        e = {
            "id": r.get("event_id", ""),
            "ts_utc": r.get("created_utc", ""),
            "event": r.get("action", ""),
            "ok": 1,
            "actor_user_id": r.get("actor_user_id", ""),
            "actor_email": r.get("actor_email", ""),
            "ip": r.get("ip", ""),
            "user_agent": r.get("user_agent", ""),
            "target_type": r.get("target_type", ""),
            "target_id": r.get("target_id", ""),
            "meta": r.get("details", {}) or {},
        }
        events.append(e)

    if event:
        events = [e for e in events if (e.get("event") or "").lower() == event]
    if q:

        def blob(e: Dict[str, Any]) -> str:
            return " ".join(
                [
                    str(e.get("event", "")),
                    str(e.get("actor_email", "")),
                    str(e.get("target_type", "")),
                    str(e.get("target_id", "")),
                    json.dumps(e.get("meta", {}), default=str),
                ]
            ).lower()

        events = [e for e in events if q in blob(e)]

    return _render_admin(
        ADMIN_AUDIT_TEMPLATE,
        title="Admin · Audit",
        active="audit",
        events=events,
        q=q,
        event=event,
    )


# -----------------------------
# Settings (Watchlist)
# -----------------------------
@admin_bp.get("/settings")
@require_perm("view_admin")
def admin_settings():
    ensure_admin_tables()

    tenant_id = TENANT_ID_DEFAULT

    wl = _load_watchlist_for_editor(tenant_id=tenant_id)
    ok, errs, normalized = _validate_watchlist(wl)
    warnings = _broad_term_warnings(normalized if ok else wl)

    cfg = _org_get_config("watchlist", tenant_id=tenant_id)
    versions = _org_list_versions("watchlist", tenant_id=tenant_id, limit=10)

    # This feeds your existing template; we now store JSON instead of newline terms
    watchlist_text = json.dumps(normalized if ok else wl, indent=2, ensure_ascii=False)

    updated_utc = (cfg or {}).get("updated_utc", "") or _watchlist_file_updated_utc()
    updated_by = (cfg or {}).get("updated_by_email", "") or ""

    return _render_admin(
        ADMIN_SETTINGS_TEMPLATE,
        title="Admin · Settings",
        active="settings",
        watchlist_text=watchlist_text,
        watchlist_path=WATCHLIST_PATH,
        watchlist_ok=bool(ok),
        watchlist_errors=errs,
        watchlist_warnings=warnings,
        watchlist_updated_utc=updated_utc,
        watchlist_updated_by=updated_by,
        watchlist_versions=versions,
    )


@admin_bp.post("/settings/watchlist")
@require_perm("view_admin")
def admin_settings_watchlist_save():
    """
    Saves watchlist as JSON mapping:
      { "Label": ["term1", "term2"], ... }

    Also:
      - writes version history into org_config_versions
      - upserts current org_config
      - writes admin audit event
      - writes WATCHLIST_PATH for runtime compatibility (your loader reads the file)
      - invalidates runtime cache (if implemented)
    """
    ensure_admin_tables()

    tenant_id = TENANT_ID_DEFAULT

    raw = (request.form.get("watchlist") or "").strip()
    if not raw:
        abort(400)

    # Accept JSON object or legacy newline list.
    candidate: Any = None
    if raw.startswith("{") or raw.startswith("["):
        try:
            candidate = json.loads(raw)
        except Exception:
            abort(400)
    else:
        # legacy textarea: one term per line
        terms: List[str] = []
        for line in raw.splitlines():
            s = line.strip()
            if not s:
                continue
            terms.append(s)
        terms = _dedupe_list(terms)
        candidate = {"Watchlist": terms}

    wl = _normalize_watchlist_obj(candidate)
    ok, errs, normalized = _validate_watchlist(wl)
    if not ok:
        # render errors inline (do not silently accept bad config)
        return _render_admin(
            r"""
            <div class="card">
              <div style="font-size:20px; font-weight:950;">Watchlist update failed</div>
              <div class="muted" style="margin-top:8px;">Fix the errors below and try again.</div>
              <ul style="margin-top:12px;">
                {% for e in errs %}
                  <li class="muted">{{ e }}</li>
                {% endfor %}
              </ul>
              <div style="margin-top:14px; display:flex; gap:10px; flex-wrap:wrap;">
                <a class="btn" href="{{ url_for('admin.admin_settings') }}">Back</a>
              </div>
            </div>
            """,
            title="Admin · Settings",
            active="settings",
            errs=errs,
        )

    value_json = json.dumps(normalized, ensure_ascii=False, separators=(",", ":"))

    me = _me()
    ip, ua = _client_ctx()

    # store in DB (current + versioning)
    _org_set_config_with_versioning(
        "watchlist",
        value_json,
        actor_user_id=me.get("user_id", ""),
        actor_email=me.get("email", ""),
        ip=ip,
        user_agent=ua,
        tenant_id=tenant_id,
    )

    # write file for runtime compatibility
    _save_watchlist_file(normalized)
    _invalidate_watchlist_runtime_cache()

    # audit
    warnings = _broad_term_warnings(normalized)
    label_count = len(normalized)
    term_count = sum(len(v) for v in normalized.values())
    write_admin_audit_event(
        "watchlist_update",
        actor_user_id=me.get("user_id", ""),
        actor_email=me.get("email", ""),
        target_type="settings",
        target_id="watchlist",
        details={
            "labels": int(label_count),
            "terms": int(term_count),
            "warnings": int(len(warnings)),
            "storage": "db+file",
        },
        ip=ip,
        user_agent=ua,
        tenant_id=tenant_id,
    )

    return redirect(url_for("admin.admin_settings"))


@admin_bp.post("/settings/watchlist/rollback/<version_id>")
@require_perm("view_admin")
def admin_settings_watchlist_rollback(version_id: str):
    """
    Roll back current watchlist to a previous version_id.
    """
    ensure_admin_tables()

    tenant_id = TENANT_ID_DEFAULT

    v = _org_get_version(version_id, tenant_id=tenant_id)
    if not v or v.get("k") != "watchlist":
        abort(404)

    try:
        wl = _normalize_watchlist_obj(json.loads(v["value_json"]))
    except Exception:
        abort(400)

    ok, errs, normalized = _validate_watchlist(wl)
    if not ok:
        abort(400)

    value_json = json.dumps(normalized, ensure_ascii=False, separators=(",", ":"))

    me = _me()
    ip, ua = _client_ctx()

    _org_set_config_with_versioning(
        "watchlist",
        value_json,
        actor_user_id=me.get("user_id", ""),
        actor_email=me.get("email", ""),
        ip=ip,
        user_agent=ua,
        tenant_id=tenant_id,
    )
    _save_watchlist_file(normalized)
    _invalidate_watchlist_runtime_cache()

    write_admin_audit_event(
        "watchlist_rollback",
        actor_user_id=me.get("user_id", ""),
        actor_email=me.get("email", ""),
        target_type="settings",
        target_id="watchlist",
        details={"version_id": version_id},
        ip=ip,
        user_agent=ua,
        tenant_id=tenant_id,
    )

    return redirect(url_for("admin.admin_settings"))
