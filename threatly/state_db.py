# threatly/state_db.py
from __future__ import annotations

import os
import sqlite3
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from werkzeug.security import check_password_hash, generate_password_hash

from .config import (
    STATE_DB_PATH,
    STATUS_VALUES,
    OPEN_STATUS_VALUES,
    DONE_STATUS_VALUES,
)


# =============================
# CORE DB UTIL
# =============================
def now_utc() -> datetime:
    return datetime.now(timezone.utc)

def iso_utc_now() -> str:
    # Canonical UTC ISO seconds + trailing 'Z' for safe lexicographic compares
    return now_utc().replace(tzinfo=timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def db_connect() -> sqlite3.Connection:
    conn = sqlite3.connect(STATE_DB_PATH, timeout=10, isolation_level=None)  # autocommit
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_parent_dir() -> None:
    d = os.path.dirname(STATE_DB_PATH)
    if d:
        os.makedirs(d, exist_ok=True)


def _table_columns(conn: sqlite3.Connection, table: str) -> List[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return [str(r["name"]) for r in rows]


def _add_column_if_missing(conn: sqlite3.Connection, table: str, col_name: str, col_def: str) -> None:
    cols = _table_columns(conn, table)
    if col_name in cols:
        return
    conn.execute(f"ALTER TABLE {table} ADD COLUMN {col_def}")


def _truthy_env(name: str, default: str = "") -> bool:
    v = (os.getenv(name, default) or "").strip().lower()
    return v in ("1", "true", "yes", "y", "on")


def _norm_email(email: str) -> str:
    return (email or "").strip().lower()


def _valid_role(role: str) -> str:
    rl = (role or "").strip().lower()
    return rl if rl in ("viewer", "analyst", "admin") else "viewer"


# =============================
# USERS (Email/Password Auth) + RBAC
# =============================
def ensure_users_table() -> None:
    _ensure_parent_dir()
    conn = db_connect()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
              user_id TEXT PRIMARY KEY,
              email   TEXT NOT NULL UNIQUE,
              password_hash TEXT NOT NULL,
              created_utc TEXT NOT NULL,
              last_login_utc TEXT NOT NULL DEFAULT '',
              prev_login_utc TEXT NOT NULL DEFAULT '',
              role TEXT NOT NULL DEFAULT 'viewer',
              is_active INTEGER NOT NULL DEFAULT 1,
              created_by_user_id TEXT
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")

        # --- Migrations for older DBs (idempotent) ---
        _add_column_if_missing(conn, "users", "role", "role TEXT NOT NULL DEFAULT 'viewer'")
        _add_column_if_missing(conn, "users", "is_active", "is_active INTEGER NOT NULL DEFAULT 1")
        _add_column_if_missing(conn, "users", "created_by_user_id", "created_by_user_id TEXT")
        _add_column_if_missing(conn, "users", "prev_login_utc", "prev_login_utc TEXT NOT NULL DEFAULT ''")
    finally:
        conn.close()


def create_user(
    email: str,
    password: str,
    *,
    role: str = "viewer",
    is_active: int = 1,
    created_by_user_id: str = "",
) -> Dict[str, Any]:
    """
    Creates a user with deterministic user_id derived from email.
    NOTE: deterministic IDs are okay for a demo/SQLite; for Postgres switch to UUID.
    """
    email_norm = _norm_email(email)
    if not email_norm or "@" not in email_norm or len(email_norm) > 254:
        raise ValueError("invalid email")
    if not password or len(password) < 10:
        raise ValueError("password must be at least 10 characters")

    import hashlib

    user_id = hashlib.sha1(email_norm.encode("utf-8", errors="ignore")).hexdigest()[:16]
    ph = generate_password_hash(password)

    now = iso_utc_now()
    rl = _valid_role(role)
    active = 1 if int(is_active or 0) == 1 else 0
    cb = (created_by_user_id or "").strip()[:64] or None

    conn = db_connect()
    try:
        conn.execute(
            """
            INSERT INTO users(
              user_id, email, password_hash, created_utc,
              last_login_utc, prev_login_utc,
              role, is_active, created_by_user_id
            )
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, email_norm, ph, now, "", "", rl, active, cb),
        )
    finally:
        conn.close()

    return {
        "user_id": user_id,
        "email": email_norm,
        "role": rl,
        "is_active": active,
        "created_utc": now,
        "last_login_utc": "",
        "prev_login_utc": "",
    }


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    email_norm = _norm_email(email)
    if not email_norm:
        return None
    conn = db_connect()
    try:
        row = conn.execute(
            """
            SELECT user_id, email, password_hash, role, is_active,
                   created_utc, last_login_utc, prev_login_utc, created_by_user_id
            FROM users
            WHERE email = ?
            LIMIT 1
            """,
            (email_norm,),
        ).fetchone()
        if not row:
            return None
        return {
            "user_id": str(row["user_id"]),
            "email": str(row["email"]),
            "password_hash": str(row["password_hash"]),
            "role": _valid_role(str(row["role"] or "viewer")),
            "is_active": int(row["is_active"] or 0),
            "created_utc": str(row["created_utc"] or ""),
            "last_login_utc": str(row["last_login_utc"] or ""),
            "prev_login_utc": str(row["prev_login_utc"] or ""),
            "created_by_user_id": str(row["created_by_user_id"] or ""),
        }
    finally:
        conn.close()


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    uid = (user_id or "").strip()
    if not uid:
        return None
    conn = db_connect()
    try:
        row = conn.execute(
            """
            SELECT user_id, email, password_hash, role, is_active,
                   created_utc, last_login_utc, prev_login_utc, created_by_user_id
            FROM users
            WHERE user_id = ?
            LIMIT 1
            """,
            (uid,),
        ).fetchone()
        if not row:
            return None
        return {
            "user_id": str(row["user_id"]),
            "email": str(row["email"]),
            "password_hash": str(row["password_hash"]),
            "role": _valid_role(str(row["role"] or "viewer")),
            "is_active": int(row["is_active"] or 0),
            "created_utc": str(row["created_utc"] or ""),
            "last_login_utc": str(row["last_login_utc"] or ""),
            "prev_login_utc": str(row["prev_login_utc"] or ""),
            "created_by_user_id": str(row["created_by_user_id"] or ""),
        }
    finally:
        conn.close()


def verify_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Verifies password and updates last_login_utc + prev_login_utc.
    Returns a compact dict used by auth code.

    Behavior:
      - prev_login_utc becomes the *previous* last_login_utc value
      - last_login_utc becomes now (UTC ISO string)
    """
    u = get_user_by_email(email)
    if not u:
        return None
    if int(u.get("is_active", 0) or 0) != 1:
        return None
    if not check_password_hash(u["password_hash"], password or ""):
        return None

    prev_last = str(u.get("last_login_utc") or "")
    now = iso_utc_now()

    conn = db_connect()
    try:
        conn.execute(
            """
            UPDATE users
            SET prev_login_utc = last_login_utc,
                last_login_utc = ?
            WHERE user_id = ?
            """,
            (now, u["user_id"]),
        )
    finally:
        conn.close()

    return {
        "user_id": u["user_id"],
        "email": u["email"],
        "role": u.get("role", "viewer"),
        "is_active": int(u.get("is_active", 0) or 0),
        "last_login_utc": now,
        "prev_login_utc": prev_last,
    }


def list_users() -> List[Dict[str, Any]]:
    conn = db_connect()
    try:
        rows = conn.execute(
            """
            SELECT user_id, email, role, is_active, created_utc,
                   last_login_utc, prev_login_utc, created_by_user_id
            FROM users
            ORDER BY created_utc DESC
            """
        ).fetchall()
        out: List[Dict[str, Any]] = []
        for r in rows:
            out.append(
                {
                    "user_id": str(r["user_id"]),
                    "email": str(r["email"]),
                    "role": _valid_role(str(r["role"] or "viewer")),
                    "is_active": int(r["is_active"] or 0),
                    "created_utc": str(r["created_utc"] or ""),
                    "last_login_utc": str(r["last_login_utc"] or ""),
                    "prev_login_utc": str(r["prev_login_utc"] or ""),
                    "created_by_user_id": str(r["created_by_user_id"] or ""),
                }
            )
        return out
    finally:
        conn.close()


def set_user_role(user_id: str, role: str) -> None:
    uid = (user_id or "").strip()
    rl = _valid_role(role)
    if not uid:
        raise ValueError("missing user_id")
    conn = db_connect()
    try:
        conn.execute("UPDATE users SET role = ? WHERE user_id = ?", (rl, uid))
    finally:
        conn.close()


def set_user_active(user_id: str, is_active: bool) -> None:
    uid = (user_id or "").strip()
    if not uid:
        raise ValueError("missing user_id")
    v = 1 if bool(is_active) else 0
    conn = db_connect()
    try:
        conn.execute("UPDATE users SET is_active = ? WHERE user_id = ?", (v, uid))
    finally:
        conn.close()


def toggle_user_active(user_id: str) -> int:
    """
    Convenience wrapper used by admin UI.
    Flips is_active and returns the NEW value (1 or 0).
    """
    uid = (user_id or "").strip()
    if not uid:
        raise ValueError("missing user_id")

    conn = db_connect()
    try:
        row = conn.execute(
            "SELECT is_active FROM users WHERE user_id = ? LIMIT 1",
            (uid,),
        ).fetchone()
        if not row:
            raise ValueError("user not found")

        cur = int(row["is_active"] or 0)
        newv = 0 if cur == 1 else 1
        conn.execute("UPDATE users SET is_active = ? WHERE user_id = ?", (newv, uid))
        return int(newv)
    finally:
        conn.close()


def set_user_password(user_id: str, password: str) -> None:
    uid = (user_id or "").strip()
    if not uid:
        raise ValueError("missing user_id")
    if not password or len(password) < 10:
        raise ValueError("password must be at least 10 characters")
    ph = generate_password_hash(password)
    conn = db_connect()
    try:
        conn.execute("UPDATE users SET password_hash = ? WHERE user_id = ?", (ph, uid))
    finally:
        conn.close()


def reset_user_password(user_id: str, password: str) -> None:
    """
    Backwards/compat alias for admin.py.
    """
    set_user_password(user_id, password)


def delete_user(user_id: str) -> None:
    """
    Hard delete. Use carefully; often better to disable instead.
    """
    uid = (user_id or "").strip()
    if not uid:
        raise ValueError("missing user_id")
    conn = db_connect()
    try:
        conn.execute("DELETE FROM users WHERE user_id = ?", (uid,))
    finally:
        conn.close()


def count_users() -> int:
    conn = db_connect()
    try:
        row = conn.execute("SELECT COUNT(1) AS n FROM users").fetchone()
        return int(row["n"] or 0) if row else 0
    finally:
        conn.close()


# =============================
# STATE DB INIT (all tables)
# =============================
def init_state_db() -> None:
    _ensure_parent_dir()
    ensure_users_table()

    conn = db_connect()
    try:
        # Per-user seen table (tenant-ready)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS seen_stories (
              tenant_id TEXT NOT NULL DEFAULT 'default',
              user_id TEXT NOT NULL,
              story_id TEXT NOT NULL,
              first_seen_utc TEXT NOT NULL,
              last_seen_utc  TEXT NOT NULL,
              seen_count INTEGER NOT NULL DEFAULT 1,
              PRIMARY KEY (tenant_id, user_id, story_id)
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_seen_tenant_user_last_seen
            ON seen_stories(tenant_id, user_id, last_seen_utc)
            """
        )

        # Shared story meta (global per tenant)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS story_meta (
              tenant_id TEXT NOT NULL DEFAULT 'default',
              story_id TEXT NOT NULL,
              status TEXT NOT NULL DEFAULT 'New',
              owner TEXT NOT NULL DEFAULT '',
              notes TEXT NOT NULL DEFAULT '',
              updated_utc TEXT NOT NULL,
              updated_by_user_id TEXT NOT NULL DEFAULT '',
              updated_by_email TEXT NOT NULL DEFAULT '',
              PRIMARY KEY (tenant_id, story_id)
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_meta_tenant_status ON story_meta(tenant_id, status)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_meta_tenant_updated ON story_meta(tenant_id, updated_utc)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_meta_tenant_owner_status ON story_meta(tenant_id, owner, status)")

        # Append-only audit events (paper trail)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS story_meta_events (
              event_id TEXT PRIMARY KEY,
              tenant_id TEXT NOT NULL DEFAULT 'default',
              story_id TEXT NOT NULL,
              actor_user_id TEXT NOT NULL DEFAULT '',
              actor_email TEXT NOT NULL DEFAULT '',
              action TEXT NOT NULL,
              before_json TEXT NOT NULL DEFAULT '',
              after_json TEXT NOT NULL DEFAULT '',
              ip TEXT NOT NULL DEFAULT '',
              user_agent TEXT NOT NULL DEFAULT '',
              created_utc TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_meta_events_tenant_story ON story_meta_events(tenant_id, story_id, created_utc)"
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_meta_events_tenant_created ON story_meta_events(tenant_id, created_utc)")

        # Institutional memory (deterministic fingerprints)
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS story_memory (
              tenant_id TEXT NOT NULL DEFAULT 'default',
              fingerprint TEXT NOT NULL,
              first_seen_utc TEXT NOT NULL,
              last_seen_utc TEXT NOT NULL,
              seen_count INTEGER NOT NULL DEFAULT 1,
              last_story_id TEXT NOT NULL DEFAULT '',
              title_sample TEXT NOT NULL DEFAULT '',
              PRIMARY KEY (tenant_id, fingerprint)
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_tenant_last_seen ON story_memory(tenant_id, last_seen_utc)")

        # --- MIGRATIONS for older DBs (safe, idempotent) ---
        try:
            cols = _table_columns(conn, "story_meta")
            if "tenant_id" not in cols:
                _add_column_if_missing(conn, "story_meta", "tenant_id", "tenant_id TEXT NOT NULL DEFAULT 'default'")
            if "updated_by_user_id" not in cols:
                _add_column_if_missing(conn, "story_meta", "updated_by_user_id", "updated_by_user_id TEXT NOT NULL DEFAULT ''")
            if "updated_by_email" not in cols:
                _add_column_if_missing(conn, "story_meta", "updated_by_email", "updated_by_email TEXT NOT NULL DEFAULT ''")
        except sqlite3.OperationalError:
            pass

        # Admin audit/events table (used by admin.py patches)
        _ensure_admin_audit_table(conn)
    finally:
        conn.close()


# =============================
# SEEN helpers (PER USER, tenant-ready)
# =============================
def is_seen(story_id: str, user_id: str, tenant_id: str = "default") -> bool:
    conn = db_connect()
    try:
        row = conn.execute(
            "SELECT 1 FROM seen_stories WHERE tenant_id = ? AND user_id = ? AND story_id = ? LIMIT 1",
            (tenant_id, user_id, story_id),
        ).fetchone()
        return row is not None
    finally:
        conn.close()


def mark_seen(story_id: str, user_id: str, tenant_id: str = "default") -> None:
    now = iso_utc_now()
    conn = db_connect()
    try:
        conn.execute(
            """
            INSERT INTO seen_stories(tenant_id, user_id, story_id, first_seen_utc, last_seen_utc, seen_count)
            VALUES(?, ?, ?, ?, ?, 1)
            ON CONFLICT(tenant_id, user_id, story_id) DO UPDATE SET
              last_seen_utc=excluded.last_seen_utc,
              seen_count=seen_count+1
            """,
            (tenant_id, user_id, story_id, now, now),
        )
    finally:
        conn.close()


def mark_unseen(story_id: str, user_id: str, tenant_id: str = "default") -> None:
    conn = db_connect()
    try:
        conn.execute(
            "DELETE FROM seen_stories WHERE tenant_id = ? AND user_id = ? AND story_id = ?",
            (tenant_id, user_id, story_id),
        )
    finally:
        conn.close()


def toggle_seen(story_id: str, user_id: str, tenant_id: str = "default") -> bool:
    if is_seen(story_id, user_id, tenant_id):
        mark_unseen(story_id, user_id, tenant_id)
        return False
    mark_seen(story_id, user_id, tenant_id)
    return True


def get_seen_map(story_ids: List[str], user_id: str, tenant_id: str = "default") -> Dict[str, bool]:
    if not story_ids:
        return {}
    conn = db_connect()
    try:
        out: Dict[str, bool] = {}
        chunk = 900
        for i in range(0, len(story_ids), chunk):
            batch = story_ids[i: i + chunk]
            placeholders = ",".join(["?"] * len(batch))
            rows = conn.execute(
                f"""
                SELECT story_id
                FROM seen_stories
                WHERE tenant_id = ?
                  AND user_id = ?
                  AND story_id IN ({placeholders})
                """,
                (tenant_id, user_id, *batch),
            ).fetchall()
            for r in rows:
                out[str(r["story_id"])] = True
        return out
    finally:
        conn.close()


def get_seen_info(story_id: str, user_id: str, tenant_id: str = "default") -> Dict[str, Any]:
    conn = db_connect()
    try:
        row = conn.execute(
            """
            SELECT first_seen_utc, last_seen_utc, seen_count
            FROM seen_stories
            WHERE tenant_id = ? AND user_id = ? AND story_id = ?
            LIMIT 1
            """,
            (tenant_id, user_id, story_id),
        ).fetchone()
        if not row:
            return {"first_seen_utc": "", "last_seen_utc": "", "seen_count": 0}
        return {
            "first_seen_utc": str(row["first_seen_utc"] or ""),
            "last_seen_utc": str(row["last_seen_utc"] or ""),
            "seen_count": int(row["seen_count"] or 0),
        }
    finally:
        conn.close()


# =============================
# META helpers (shared, tenant-ready)
# =============================
def _sanitize_status(status: str) -> str:
    s = (status or "").strip()
    return s if s in STATUS_VALUES else "New"


def get_meta_map(story_ids: List[str], tenant_id: str = "default") -> Dict[str, Dict[str, Any]]:
    if not story_ids:
        return {}
    conn = db_connect()
    try:
        out: Dict[str, Dict[str, Any]] = {}
        chunk = 900
        for i in range(0, len(story_ids), chunk):
            batch = story_ids[i: i + chunk]
            placeholders = ",".join(["?"] * len(batch))
            rows = conn.execute(
                f"""
                SELECT story_id, status, owner, notes, updated_utc, updated_by_user_id, updated_by_email
                FROM story_meta
                WHERE tenant_id = ?
                  AND story_id IN ({placeholders})
                """,
                (tenant_id, *batch),
            ).fetchall()
            for r in rows:
                out[str(r["story_id"])] = {
                    "status": str(r["status"] or "New"),
                    "owner": str(r["owner"] or ""),
                    "notes": str(r["notes"] or ""),
                    "updated_utc": str(r["updated_utc"] or ""),
                    "updated_by_user_id": str(r["updated_by_user_id"] or ""),
                    "updated_by_email": str(r["updated_by_email"] or ""),
                }
        return out
    finally:
        conn.close()


def _make_event_id(tenant_id: str, story_id: str, created_utc: str, actor_user_id: str, after_json: str) -> str:
    import hashlib

    base = f"{tenant_id}|{story_id}|{created_utc}|{actor_user_id}|{after_json}"
    return hashlib.sha1(base.encode("utf-8", errors="ignore")).hexdigest()[:20]


def _sha256_hex(s: str) -> str:
    import hashlib
    return hashlib.sha256((s or "").encode("utf-8", errors="ignore")).hexdigest()


def _audit_view(meta: Dict[str, Any], *, include_notes: bool, notes_hash: str, notes_len: int) -> Dict[str, Any]:
    out = {
        "status": meta.get("status", "New"),
        "owner": meta.get("owner", ""),
        "updated_utc": meta.get("updated_utc", ""),
        "updated_by_user_id": meta.get("updated_by_user_id", ""),
        "updated_by_email": meta.get("updated_by_email", ""),
        "notes_changed": bool(meta.get("notes_changed", False)),
        "notes_len": int(notes_len),
        "notes_sha256": notes_hash,
    }
    if include_notes:
        out["notes"] = meta.get("notes", "")
    return out


def upsert_story_meta(
    story_id: str,
    status: str,
    owner: str,
    notes: str,
    *,
    actor_user_id: str = "",
    actor_email: str = "",
    ip: str = "",
    user_agent: str = "",
    tenant_id: str = "default",
) -> Dict[str, Any]:
    st = _sanitize_status(status)
    ow = (owner or "").strip()[:120]
    nt = (notes or "").strip()[:5000]
    now = iso_utc_now()

    store_full_notes_in_audit = _truthy_env("AUDIT_STORE_FULL_NOTES", "0")

    conn = db_connect()
    try:
        conn.execute("BEGIN")

        before_row = conn.execute(
            """
            SELECT status, owner, notes, updated_utc, updated_by_user_id, updated_by_email
            FROM story_meta
            WHERE tenant_id = ? AND story_id = ?
            LIMIT 1
            """,
            (tenant_id, story_id),
        ).fetchone()

        before_state: Dict[str, Any] = {}
        before_notes = ""
        if before_row:
            before_notes = str(before_row["notes"] or "")
            before_state = {
                "status": str(before_row["status"] or "New"),
                "owner": str(before_row["owner"] or ""),
                "notes": before_notes,
                "updated_utc": str(before_row["updated_utc"] or ""),
                "updated_by_user_id": str(before_row["updated_by_user_id"] or ""),
                "updated_by_email": str(before_row["updated_by_email"] or ""),
            }

        notes_changed = (before_notes != nt)
        before_hash = _sha256_hex(before_notes)
        after_hash = _sha256_hex(nt)

        conn.execute(
            """
            INSERT INTO story_meta(tenant_id, story_id, status, owner, notes, updated_utc, updated_by_user_id, updated_by_email)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(tenant_id, story_id) DO UPDATE SET
              status=excluded.status,
              owner=excluded.owner,
              notes=excluded.notes,
              updated_utc=excluded.updated_utc,
              updated_by_user_id=excluded.updated_by_user_id,
              updated_by_email=excluded.updated_by_email
            """,
            (tenant_id, story_id, st, ow, nt, now, actor_user_id or "", actor_email or ""),
        )

        after_state = {
            "status": st,
            "owner": ow,
            "notes": nt,
            "updated_utc": now,
            "updated_by_user_id": actor_user_id or "",
            "updated_by_email": actor_email or "",
        }

        before_audit = {}
        if before_state:
            before_state_with_flag = dict(before_state)
            before_state_with_flag["notes_changed"] = notes_changed
            before_audit = _audit_view(
                before_state_with_flag,
                include_notes=store_full_notes_in_audit,
                notes_hash=before_hash,
                notes_len=len(before_notes),
            )

        after_state_with_flag = dict(after_state)
        after_state_with_flag["notes_changed"] = notes_changed
        after_audit = _audit_view(
            after_state_with_flag,
            include_notes=store_full_notes_in_audit,
            notes_hash=after_hash,
            notes_len=len(nt),
        )

        before_json = json.dumps(before_audit, ensure_ascii=False, separators=(",", ":")) if before_audit else ""
        after_json = json.dumps(after_audit, ensure_ascii=False, separators=(",", ":"))

        event_id = _make_event_id(tenant_id, story_id, now, actor_user_id or "", after_json)
        conn.execute(
            """
            INSERT INTO story_meta_events(
              event_id, tenant_id, story_id,
              actor_user_id, actor_email,
              action, before_json, after_json,
              ip, user_agent, created_utc
            )
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                tenant_id,
                story_id,
                actor_user_id or "",
                actor_email or "",
                "meta_update",
                before_json,
                after_json,
                (ip or "")[:200],
                (user_agent or "")[:300],
                now,
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

    return {"story_id": story_id, **after_state}


def get_meta_history(story_id: str, *, tenant_id: str = "default", limit: int = 50) -> List[Dict[str, Any]]:
    lim = int(limit or 50)
    lim = max(1, min(lim, 200))
    conn = db_connect()
    try:
        rows = conn.execute(
            """
            SELECT event_id, created_utc, actor_user_id, actor_email, action, before_json, after_json, ip, user_agent
            FROM story_meta_events
            WHERE tenant_id = ? AND story_id = ?
            ORDER BY created_utc DESC
            LIMIT ?
            """,
            (tenant_id, story_id, lim),
        ).fetchall()

        out: List[Dict[str, Any]] = []
        for r in rows:
            before: Dict[str, Any] = {}
            after: Dict[str, Any] = {}

            try:
                if r["before_json"]:
                    before = json.loads(r["before_json"])
            except Exception:
                before = {}

            try:
                if r["after_json"]:
                    after = json.loads(r["after_json"])
            except Exception:
                after = {}

            if not _truthy_env("AUDIT_STORE_FULL_NOTES", "0"):
                before.pop("notes", None)
                after.pop("notes", None)

            out.append(
                {
                    "event_id": str(r["event_id"]),
                    "created_utc": str(r["created_utc"] or ""),
                    "actor_user_id": str(r["actor_user_id"] or ""),
                    "actor_email": str(r["actor_email"] or ""),
                    "action": str(r["action"] or ""),
                    "before": before,
                    "after": after,
                    "ip": str(r["ip"] or ""),
                    "user_agent": str(r["user_agent"] or ""),
                }
            )
        return out
    finally:
        conn.close()


# =============================
# INSTITUTIONAL MEMORY
# =============================
def record_story_fingerprint(
    fingerprint: str,
    *,
    story_id: str = "",
    title_sample: str = "",
    tenant_id: str = "default",
) -> None:
    fp = (fingerprint or "").strip()
    if not fp:
        return
    now = iso_utc_now()
    title_s = (title_sample or "").strip()[:180]
    conn = db_connect()
    try:
        conn.execute(
            """
            INSERT INTO story_memory(tenant_id, fingerprint, first_seen_utc, last_seen_utc, seen_count, last_story_id, title_sample)
            VALUES(?, ?, ?, ?, 1, ?, ?)
            ON CONFLICT(tenant_id, fingerprint) DO UPDATE SET
              last_seen_utc=excluded.last_seen_utc,
              seen_count=story_memory.seen_count+1,
              last_story_id=excluded.last_story_id,
              title_sample=excluded.title_sample
            """,
            (tenant_id, fp, now, now, story_id[:24], title_s),
        )
    finally:
        conn.close()


def get_memory_map(fingerprints: List[str], tenant_id: str = "default") -> Dict[str, Dict[str, Any]]:
    fps = [f.strip() for f in (fingerprints or []) if (f or "").strip()]
    if not fps:
        return {}
    conn = db_connect()
    try:
        out: Dict[str, Dict[str, Any]] = {}
        chunk = 900
        for i in range(0, len(fps), chunk):
            batch = fps[i : i + chunk]
            placeholders = ",".join(["?"] * len(batch))
            rows = conn.execute(
                f"""
                SELECT fingerprint, first_seen_utc, last_seen_utc, seen_count, last_story_id, title_sample
                FROM story_memory
                WHERE tenant_id = ?
                  AND fingerprint IN ({placeholders})
                """,
                (tenant_id, *batch),
            ).fetchall()
            for r in rows:
                out[str(r["fingerprint"])] = {
                    "first_seen_utc": str(r["first_seen_utc"] or ""),
                    "last_seen_utc": str(r["last_seen_utc"] or ""),
                    "seen_count": int(r["seen_count"] or 0),
                    "last_story_id": str(r["last_story_id"] or ""),
                    "title_sample": str(r["title_sample"] or ""),
                }
        return out
    finally:
        conn.close()

# =============================
# STORY KPI HELPERS (status + assignment)
# =============================
def get_story_status_counts(
    *,
    tenant_id: str = "default",
    owner: str = "",  # if set -> filter to this owner (user-scoped)
) -> Dict[str, int]:
    """
    Returns counts by status from story_meta.
    If owner is provided, filters to that owner.
    """
    conn = db_connect()
    try:
        where = ["tenant_id = ?"]
        params: List[Any] = [tenant_id]

        if owner.strip():
            where.append("COALESCE(owner,'') = ?")
            params.append(owner.strip())

        rows = conn.execute(
            f"""
            SELECT status, COUNT(1) AS n
            FROM story_meta
            WHERE {" AND ".join(where)}
            GROUP BY status
            """,
            params,
        ).fetchall()

        out: Dict[str, int] = {}
        for r in rows:
            out[str(r["status"] or "New")] = int(r["n"] or 0)
        return out
    finally:
        conn.close()


def get_story_assignment_counts(
    *,
    tenant_id: str = "default",
    top_n: int = 12,
) -> List[Dict[str, Any]]:
    """
    Returns counts by owner (assignee). Includes 'Unassigned'.
    This is current workload (current story_meta state).
    """
    top_n = max(1, min(int(top_n or 12), 50))
    conn = db_connect()
    try:
        rows = conn.execute(
            """
            SELECT
              CASE WHEN COALESCE(owner,'') = '' THEN 'Unassigned' ELSE owner END AS assignee,
              COUNT(1) AS n
            FROM story_meta
            WHERE tenant_id = ?
            GROUP BY assignee
            ORDER BY n DESC, assignee ASC
            LIMIT ?
            """,
            (tenant_id, top_n),
        ).fetchall()

        return [{"assignee": str(r["assignee"]), "n": int(r["n"] or 0)} for r in rows]
    finally:
        conn.close()


# --- WINDOWED story KPI helpers (time-filter aware) ---

def _dt_expr(col: str) -> str:
    """
    Normalizes ISO-ish strings for SQLite datetime comparisons.
    Works whether col has 'Z' or not.
    """
    return f"datetime(substr(replace(replace({col},'T',' '),'Z',''),1,19))"


def get_story_status_counts_window(
    *,
    tenant_id: str = "default",
    start_utc: str,
    end_utc: str,
    owner: str = "",
) -> Dict[str, int]:
    """
    Counts by status for stories whose story_meta.updated_utc falls within [start_utc, end_utc].
    Interprets windowed as "stories updated/touched in this time window".
    """
    conn = db_connect()
    try:
        where = ["tenant_id = ?"]
        params: List[Any] = [tenant_id]

        if owner.strip():
            where.append("COALESCE(owner,'') = ?")
            params.append(owner.strip())

        dt = _dt_expr("updated_utc")
        where.append(f"{dt} >= datetime(substr(replace(replace(?,'T',' '),'Z',''),1,19))")
        params.append(start_utc)
        where.append(f"{dt} <= datetime(substr(replace(replace(?,'T',' '),'Z',''),1,19))")
        params.append(end_utc)

        rows = conn.execute(
            f"""
            SELECT status, COUNT(1) AS n
            FROM story_meta
            WHERE {" AND ".join(where)}
            GROUP BY status
            """,
            params,
        ).fetchall()

        out: Dict[str, int] = {}
        for r in rows:
            out[str(r["status"] or "New")] = int(r["n"] or 0)
        return out
    finally:
        conn.close()


def get_story_assignment_counts_window(
    *,
    tenant_id: str = "default",
    start_utc: str,
    end_utc: str,
    top_n: int = 12,
) -> List[Dict[str, Any]]:
    """
    Counts by owner (assignee) for stories whose story_meta.updated_utc falls within [start_utc, end_utc].
    This is "activity in window by assignee", NOT current workload.
    """
    top_n = max(1, min(int(top_n or 12), 50))
    conn = db_connect()
    try:
        dt = _dt_expr("updated_utc")
        rows = conn.execute(
            f"""
            SELECT
              CASE WHEN COALESCE(owner,'') = '' THEN 'Unassigned' ELSE owner END AS assignee,
              COUNT(1) AS n
            FROM story_meta
            WHERE tenant_id = ?
              AND {dt} >= datetime(substr(replace(replace(?,'T',' '),'Z',''),1,19))
              AND {dt} <= datetime(substr(replace(replace(?,'T',' '),'Z',''),1,19))
            GROUP BY assignee
            ORDER BY n DESC, assignee ASC
            LIMIT ?
            """,
            (tenant_id, start_utc, end_utc, top_n),
        ).fetchall()

        return [{"assignee": str(r["assignee"]), "n": int(r["n"] or 0)} for r in rows]
    finally:
        conn.close()


# =============================
# USER KPI HELPERS
# =============================

def user_assigned_open_count(*, tenant_id: str, owner_email: str) -> int:
    """
    Count stories assigned to this owner that are still "open".
    Open statuses are New + Investigating.
    """
    conn = db_connect()
    try:
        row = conn.execute(
            f"""
            SELECT COUNT(1) AS n
            FROM story_meta
            WHERE tenant_id = ?
              AND COALESCE(owner,'') = ?
              AND COALESCE(status,'New') IN ({",".join(["?"] * len(OPEN_STATUS_VALUES))})
            """,
            [tenant_id, (owner_email or "").strip()] + list(OPEN_STATUS_VALUES),
        ).fetchone()
        return int(row["n"] or 0) if row else 0
    finally:
        conn.close()


def user_assigned_done_count(*, tenant_id: str, owner_email: str) -> int:
    """
    Count stories assigned to this owner that are "done".
    Done statuses are Not Relevant + Mitigated.
    """
    conn = db_connect()
    try:
        row = conn.execute(
            f"""
            SELECT COUNT(1) AS n
            FROM story_meta
            WHERE tenant_id = ?
              AND COALESCE(owner,'') = ?
              AND COALESCE(status,'New') IN ({",".join(["?"] * len(DONE_STATUS_VALUES))})
            """,
            [tenant_id, (owner_email or "").strip()] + list(DONE_STATUS_VALUES),
        ).fetchone()
        return int(row["n"] or 0) if row else 0
    finally:
        conn.close()


def user_reviewed_total(*, tenant_id: str, user_id: str) -> int:
    """
    Total stories this user has reviewed (ever).
    """
    conn = db_connect()
    try:
        row = conn.execute(
            """
            SELECT COUNT(1) AS n
            FROM seen_stories
            WHERE tenant_id = ?
              AND user_id = ?
            """,
            (tenant_id, user_id),
        ).fetchone()
        return int(row["n"] or 0) if row else 0
    finally:
        conn.close()


def user_reviewed_since(*, tenant_id: str, user_id: str, cutoff_utc_iso: str) -> int:
    """
    How many stories this user reviewed since cutoff.
    last_seen_utc is stored as ISO; lexicographic compare works.
    """
    conn = db_connect()
    try:
        row = conn.execute(
            """
            SELECT COUNT(1) AS n
            FROM seen_stories
            WHERE tenant_id = ?
              AND user_id = ?
              AND last_seen_utc >= ?
            """,
            (tenant_id, user_id, cutoff_utc_iso),
        ).fetchone()
        return int(row["n"] or 0) if row else 0
    finally:
        conn.close()


def user_unreviewed_assigned_open_count(*, tenant_id: str, user_id: str, owner_email: str) -> int:
    """
    Open stories assigned to owner_email that this user has NOT reviewed.
    """
    conn = db_connect()
    try:
        row = conn.execute(
            f"""
            SELECT COUNT(1) AS n
            FROM story_meta m
            LEFT JOIN seen_stories s
              ON s.tenant_id = m.tenant_id
             AND s.story_id = m.story_id
             AND s.user_id = ?
            WHERE m.tenant_id = ?
              AND COALESCE(m.owner,'') = ?
              AND COALESCE(m.status,'New') IN ({",".join(["?"] * len(OPEN_STATUS_VALUES))})
              AND s.story_id IS NULL
            """,
            [user_id, tenant_id, (owner_email or "").strip()] + list(OPEN_STATUS_VALUES),
        ).fetchone()
        return int(row["n"] or 0) if row else 0
    finally:
        conn.close()


# =============================
# ADMIN AUDIT (compat layer for admin.py patches)
# =============================
def _ensure_admin_audit_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS admin_audit_events (
          event_id TEXT PRIMARY KEY,
          tenant_id TEXT NOT NULL DEFAULT 'default',
          actor_user_id TEXT NOT NULL DEFAULT '',
          actor_email TEXT NOT NULL DEFAULT '',
          action TEXT NOT NULL,
          target_type TEXT NOT NULL DEFAULT '',
          target_id TEXT NOT NULL DEFAULT '',
          details_json TEXT NOT NULL DEFAULT '',
          ip TEXT NOT NULL DEFAULT '',
          user_agent TEXT NOT NULL DEFAULT '',
          created_utc TEXT NOT NULL
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_admin_audit_tenant_created ON admin_audit_events(tenant_id, created_utc)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_admin_audit_tenant_action ON admin_audit_events(tenant_id, action)")


def ensure_admin_audit_table() -> None:
    _ensure_parent_dir()
    conn = db_connect()
    try:
        _ensure_admin_audit_table(conn)
    finally:
        conn.close()


def _make_admin_event_id(
    tenant_id: str,
    created_utc: str,
    actor_user_id: str,
    action: str,
    target_type: str,
    target_id: str,
    details_json: str,
) -> str:
    import hashlib

    base = f"{tenant_id}|{created_utc}|{actor_user_id}|{action}|{target_type}|{target_id}|{details_json}"
    return hashlib.sha1(base.encode("utf-8", errors="ignore")).hexdigest()[:20]


def write_audit_event(
    action: str,
    *,
    actor_user_id: str = "",
    actor_email: str = "",
    target_type: str = "",
    target_id: str = "",
    details: Optional[Dict[str, Any]] = None,
    ip: str = "",
    user_agent: str = "",
    tenant_id: str = "default",
) -> str:
    act = (action or "").strip()[:80]
    if not act:
        raise ValueError("missing action")

    tt = (target_type or "").strip()[:40]
    tid = (target_id or "").strip()[:80]

    payload: Dict[str, Any] = {}
    if details:
        for k, v in list(details.items())[:40]:
            kk = str(k)[:60]
            if isinstance(v, (str, int, float, bool)) or v is None:
                payload[kk] = v
            else:
                payload[kk] = str(v)[:300]

    details_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":")) if payload else ""

    # ✅ Canonical UTC timestamp: ISO-8601 seconds + trailing 'Z'
    # Works perfectly with lexicographic compares and SQLite datetime() parsing.
    created = now_utc()
    try:
        created_utc = created.replace(tzinfo=timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    except Exception:
        # ultra-safe fallback
        created_utc = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    eid = _make_admin_event_id(tenant_id, created_utc, (actor_user_id or ""), act, tt, tid, details_json)

    conn = db_connect()
    try:
        _ensure_admin_audit_table(conn)
        conn.execute(
            """
            INSERT OR IGNORE INTO admin_audit_events(
              event_id, tenant_id,
              actor_user_id, actor_email,
              action, target_type, target_id,
              details_json, ip, user_agent, created_utc
            )
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                eid,
                tenant_id,
                (actor_user_id or "")[:64],
                (actor_email or "")[:254],
                act,
                tt,
                tid,
                details_json,
                (ip or "")[:200],
                (user_agent or "")[:300],
                created_utc,
            ),
        )
    finally:
        conn.close()

    return eid



def list_audit_events(
    *,
    tenant_id: str = "default",
    limit: int = 100,
    offset: int = 0,
    start_utc: str = "",
    end_utc: str = "",
    action: str = "",
    ok: Optional[bool] = None,
    actor_email: str = "",
    target_type: str = "",
    target_id: str = "",
    ip: str = "",
) -> List[Dict[str, Any]]:
    """
    Optional filters:
      - start_utc/end_utc: ISO strings (lexicographic compare works with Z)
      - action: exact match
      - ok: if set, filters details_json for ok:true/false (no JSON1 required)
      - actor_email: exact match (case-insensitive normalized on read)
      - target_type: exact match
      - target_id: exact match
      - ip: exact match
      - offset: for "Load more" pagination
    """
    lim = max(1, min(int(limit or 100), 500))
    off = max(0, int(offset or 0))
    act = (action or "").strip()
    ae = (actor_email or "").strip().lower()
    tt = (target_type or "").strip().lower()
    tid = (target_id or "").strip()
    ipf = (ip or "").strip()

    where = ["tenant_id = ?"]
    params: List[Any] = [tenant_id]

    if start_utc:
        where.append("created_utc >= ?")
        params.append(start_utc)
    if end_utc:
        where.append("created_utc <= ?")
        params.append(end_utc)
    if act:
        where.append("action = ?")
        params.append(act)
    if ae:
        where.append("lower(COALESCE(actor_email,'')) = ?")
        params.append(ae)
    if tt:
        where.append("lower(COALESCE(target_type,'')) = ?")
        params.append(tt)
    if tid:
        where.append("COALESCE(target_id,'') = ?")
        params.append(tid)
    if ipf:
        where.append("COALESCE(ip,'') = ?")
        params.append(ipf)

    if ok is True:
        where.append("""(
            instr(lower(COALESCE(details_json,'')), '"ok":true') > 0
            OR instr(lower(COALESCE(details_json,'')), '"ok":1') > 0
        )""")
    elif ok is False:
        where.append("""(
            instr(lower(COALESCE(details_json,'')), '"ok":false') > 0
            OR instr(lower(COALESCE(details_json,'')), '"ok":0') > 0
        )""")

    where_sql = " AND ".join(where)

    conn = db_connect()
    try:
        _ensure_admin_audit_table(conn)
        rows = conn.execute(
            f"""
            SELECT event_id, created_utc, actor_user_id, actor_email, action, target_type, target_id, details_json, ip, user_agent
            FROM admin_audit_events
            WHERE {where_sql}
            ORDER BY created_utc DESC
            LIMIT ? OFFSET ?
            """,
            (*params, lim, off),
        ).fetchall()

        out: List[Dict[str, Any]] = []
        for r in rows:
            details: Dict[str, Any] = {}
            try:
                if r["details_json"]:
                    details = json.loads(r["details_json"])
            except Exception:
                details = {}

            out.append(
                {
                    "event_id": str(r["event_id"]),
                    "created_utc": str(r["created_utc"] or ""),
                    "actor_user_id": str(r["actor_user_id"] or ""),
                    "actor_email": str(r["actor_email"] or ""),
                    "action": str(r["action"] or ""),
                    "target_type": str(r["target_type"] or ""),
                    "target_id": str(r["target_id"] or ""),
                    "details": details,
                    "ip": str(r["ip"] or ""),
                    "user_agent": str(r["user_agent"] or ""),
                }
            )
        return out
    finally:
        conn.close()



# =============================
# ADMIN AUDIT KPI HELPERS
# =============================
def _iso_utc(dt: datetime) -> str:
    # Canonical UTC ISO seconds + 'Z' (matches write_audit_event storage)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.isoformat(timespec="seconds").replace("+00:00", "Z")



def admin_audit_count_since(*, cutoff_utc: datetime, tenant_id: str = "default") -> int:
    cutoff_iso = _iso_utc(cutoff_utc)
    conn = db_connect()
    try:
        _ensure_admin_audit_table(conn)
        row = conn.execute(
            """
            SELECT COUNT(1) AS n
            FROM admin_audit_events
            WHERE tenant_id = ?
              AND created_utc >= ?
            """,
            (tenant_id, cutoff_iso),
        ).fetchone()
        return int(row["n"] or 0) if row else 0
    finally:
        conn.close()


def admin_audit_counts_by_action_since(
    *,
    cutoff_utc: datetime,
    tenant_id: str = "default",
    limit: int = 12,
) -> List[Dict[str, Any]]:
    lim = max(1, min(int(limit or 12), 50))
    cutoff_iso = _iso_utc(cutoff_utc)

    conn = db_connect()
    try:
        _ensure_admin_audit_table(conn)
        rows = conn.execute(
            """
            SELECT action, COUNT(1) AS n
            FROM admin_audit_events
            WHERE tenant_id = ?
              AND created_utc >= ?
            GROUP BY action
            ORDER BY n DESC, action ASC
            LIMIT ?
            """,
            (tenant_id, cutoff_iso, lim),
        ).fetchall()
        return [{"action": str(r["action"] or ""), "n": int(r["n"] or 0)} for r in rows]
    finally:
        conn.close()


def admin_audit_last_event(*, tenant_id: str = "default") -> Dict[str, Any]:
    conn = db_connect()
    try:
        _ensure_admin_audit_table(conn)
        row = conn.execute(
            """
            SELECT created_utc, action, actor_email, target_type, target_id
            FROM admin_audit_events
            WHERE tenant_id = ?
            ORDER BY created_utc DESC
            LIMIT 1
            """,
            (tenant_id,),
        ).fetchone()
        if not row:
            return {"created_utc": "", "action": "", "actor_email": "", "target_type": "", "target_id": ""}
        return {
            "created_utc": str(row["created_utc"] or ""),
            "action": str(row["action"] or ""),
            "actor_email": str(row["actor_email"] or ""),
            "target_type": str(row["target_type"] or ""),
            "target_id": str(row["target_id"] or ""),
        }
    finally:
        conn.close()


def get_admin_audit_kpis(
    *,
    tenant_id: str = "default",
    start_utc: str | None = None,
    end_utc: str | None = None,
    top_n: int = 10,
) -> Dict[str, Any]:
    """
    Supports:
      1) Rolling KPIs (audit_24h/7d/30d, top_actions_24h, last_event)
      2) Window KPIs (start_utc/end_utc) for the admin dashboard tiles

    NOTE:
    - admin_audit_events.created_utc is stored as UTC ISO string (e.g. 2026-01-17T17:41:25Z or without Z).
      Lexicographic comparisons work as long as format stays consistent.
    - Login failures in your system are stored as:
        action = 'login_attempt'
        details_json contains `"ok":false` (or `"ok":0`)
      NOT as action='login_fail' etc.
    """
    top_n = max(1, min(int(top_n or 10), 20))

    # Privileged definitions (keep yours)
    privileged_prefixes = ("user_", "watchlist_", "role_", "settings_")
    privileged_actions = {
        "user_create",
        "user_created",
        "user_toggle_active",
        "user_disabled",
        "user_enabled",
        "user_set_role",
        "role_changed",
        "user_reset_password",
        "password_reset",
        "watchlist_update",
        "watchlist_rollback",
        "settings_updated",
        "meta_set",
    }

    def _count_login_failures(
        conn: sqlite3.Connection, *, tenant_id: str, start_utc: str, end_utc: str
    ) -> int:
        """
        Counts failed login attempts in [start_utc, end_utc] based on your real schema:
          action='login_attempt' AND details_json contains ok=false (or ok:0)
        Uses instr/lower to avoid requiring SQLite JSON1.
        """
        row = conn.execute(
            """
            SELECT COUNT(1) AS n
            FROM admin_audit_events
            WHERE tenant_id = ?
              AND created_utc >= ?
              AND created_utc <= ?
              AND action = 'login_attempt'
              AND (
                instr(lower(COALESCE(details_json,'')), '"ok":false') > 0
                OR instr(lower(COALESCE(details_json,'')), '"ok":0') > 0
              )
            """,
            (tenant_id, start_utc, end_utc),
        ).fetchone()
        return int(row["n"] or 0) if row else 0
    



    # -----------------------------
    # WINDOW MODE (used by admin dashboard time filter)
    # -----------------------------
    if start_utc and end_utc:
        conn = db_connect()
        try:
            _ensure_admin_audit_table(conn)

            # total events in window
            row = conn.execute(
                """
                SELECT COUNT(1) AS n
                FROM admin_audit_events
                WHERE tenant_id = ?
                  AND created_utc >= ?
                  AND created_utc <= ?
                """,
                (tenant_id, start_utc, end_utc),
            ).fetchone()
            total = int(row["n"] or 0) if row else 0

            # top actions in window
            rows = conn.execute(
                """
                SELECT action, COUNT(1) AS n
                FROM admin_audit_events
                WHERE tenant_id = ?
                  AND created_utc >= ?
                  AND created_utc <= ?
                GROUP BY action
                ORDER BY n DESC, action ASC
                LIMIT ?
                """,
                (tenant_id, start_utc, end_utc, top_n),
            ).fetchall()
            top_actions = [{"action": str(r["action"]), "n": int(r["n"] or 0)} for r in rows]

            # most recent event in window
            last = conn.execute(
                """
                SELECT created_utc, actor_email, actor_user_id, action, target_type, target_id
                FROM admin_audit_events
                WHERE tenant_id = ?
                  AND created_utc >= ?
                  AND created_utc <= ?
                ORDER BY created_utc DESC
                LIMIT 1
                """,
                (tenant_id, start_utc, end_utc),
            ).fetchone()
            last_event: Dict[str, Any] = {}
            if last:
                last_event = {
                    "created_utc": str(last["created_utc"] or ""),
                    "actor_email": str(last["actor_email"] or ""),
                    "actor_user_id": str(last["actor_user_id"] or ""),
                    "action": str(last["action"] or ""),
                    "target_type": str(last["target_type"] or ""),
                    "target_id": str(last["target_id"] or ""),
                }

            # login failures in window
            login_fail_window = _count_login_failures(
                conn, tenant_id=tenant_id, start_utc=start_utc, end_utc=end_utc
            )

            # privileged actions in window: explicit list
            qmarks = ",".join(["?"] * len(privileged_actions))
            pa1 = conn.execute(
                f"""
                SELECT COUNT(1) AS n
                FROM admin_audit_events
                WHERE tenant_id = ?
                  AND created_utc >= ?
                  AND created_utc <= ?
                  AND action IN ({qmarks})
                """,
                (tenant_id, start_utc, end_utc, *sorted(privileged_actions)),
            ).fetchone()
            privileged_count = int(pa1["n"] or 0) if pa1 else 0

            # privileged actions in window: prefix match (future-proof)
            pa2 = 0
            for p in privileged_prefixes:
                r2 = conn.execute(
                    """
                    SELECT COUNT(1) AS n
                    FROM admin_audit_events
                    WHERE tenant_id = ?
                      AND created_utc >= ?
                      AND created_utc <= ?
                      AND action LIKE ?
                    """,
                    (tenant_id, start_utc, end_utc, f"{p}%"),
                ).fetchone()
                pa2 += int(r2["n"] or 0) if r2 else 0

            privileged_window = max(privileged_count, pa2)

            # unique actors in window (distinct emails)
            ua = conn.execute(
                """
                SELECT COUNT(DISTINCT actor_email) AS n
                FROM admin_audit_events
                WHERE tenant_id = ?
                  AND created_utc >= ?
                  AND created_utc <= ?
                  AND actor_email <> ''
                """,
                (tenant_id, start_utc, end_utc),
            ).fetchone()
            unique_actors_window = int(ua["n"] or 0) if ua else 0

            # top actors in window
            rows = conn.execute(
                """
                SELECT actor_email, COUNT(1) AS n
                FROM admin_audit_events
                WHERE tenant_id = ?
                  AND created_utc >= ?
                  AND created_utc <= ?
                  AND actor_email <> ''
                GROUP BY actor_email
                ORDER BY n DESC, actor_email ASC
                LIMIT 5
                """,
                (tenant_id, start_utc, end_utc),
            ).fetchall()
            top_actors = [{"actor_email": str(r["actor_email"]), "n": int(r["n"] or 0)} for r in rows]

            # events by day (for mini trend)
            rows = conn.execute(
                """
                SELECT substr(created_utc, 1, 10) AS day, COUNT(1) AS n
                FROM admin_audit_events
                WHERE tenant_id = ?
                  AND created_utc >= ?
                  AND created_utc <= ?
                GROUP BY day
                ORDER BY day ASC
                """,
                (tenant_id, start_utc, end_utc),
            ).fetchall()
            events_by_day = [{"day": str(r["day"]), "n": int(r["n"] or 0)} for r in rows]

            return {
                # window-native keys (used by admin dashboard tiles)
                "start_utc": start_utc,
                "end_utc": end_utc,
                "audit_window": total,
                "top_actions": top_actions,
                "action_mix": top_actions,
                "last_event": last_event,
                "login_fail_window": login_fail_window,
                "privileged_window": privileged_window,
                "unique_actors_window": unique_actors_window,
                "top_actors": top_actors,
                "events_by_day": events_by_day,

                # aliases (keeps older templates/logic from breaking)
                "audit_24h": total,
                "top_actions_24h": top_actions,
                "audit_last_event": last_event,
                "login_fail_24h": login_fail_window,
                "privileged_24h": privileged_window,
            }
        finally:
            conn.close()

    # -----------------------------
    # ROLLING MODE (backwards compatible)
    # -----------------------------
    now = now_utc()

    k24 = admin_audit_count_since(cutoff_utc=now - timedelta(days=1), tenant_id=tenant_id)
    k7 = admin_audit_count_since(cutoff_utc=now - timedelta(days=7), tenant_id=tenant_id)
    k30 = admin_audit_count_since(cutoff_utc=now - timedelta(days=30), tenant_id=tenant_id)

    top_actions_24h = admin_audit_counts_by_action_since(
        cutoff_utc=now - timedelta(days=1),
        tenant_id=tenant_id,
        limit=top_n,
    )
    last = admin_audit_last_event(tenant_id=tenant_id)

    # rolling login failures (24h)
    start_24h = (now - timedelta(days=1)).replace(tzinfo=timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    end_now = now.replace(tzinfo=timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    login_fail_24h = 0
    conn = db_connect()
    try:
        _ensure_admin_audit_table(conn)
        login_fail_24h = _count_login_failures(conn, tenant_id=tenant_id, start_utc=start_24h, end_utc=end_now)
    finally:
        conn.close()

    return {
        "audit_24h": int(k24),
        "audit_7d": int(k7),
        "audit_30d": int(k30),
        "top_actions_24h": top_actions_24h,
        "last_event": last,
        "login_fail_24h": int(login_fail_24h),
    }



def story_drilldown(
    *,
    kind: str,
    value: str,
    mode: str = "snapshot",
    start_utc: str | None = None,
    end_utc: str | None = None,
    limit: int = 50,
    offset: int = 0,
    tenant_id: str = "default",
):
    """
    Returns:
      {"rows": [...], "total": int}

    NOTE:
    - This function expects you already implemented the working drilldown query (you did, since modal shows rows now).
    - We keep the row payload as-is.
    - We compute total via SELECT COUNT(*) FROM (<base_query_without_limit_offset>).
    """
    kind = (kind or "").strip().lower()
    value = (value or "").strip()
    mode = (mode or "snapshot").strip().lower()
    limit = max(1, min(int(limit or 50), 200))
    offset = max(0, int(offset or 0))

    if kind not in ("status", "assignee"):
        return {"rows": [], "total": 0}
    if not value:
        return {"rows": [], "total": 0}
    if mode not in ("snapshot", "windowed"):
        mode = "snapshot"

    conn = db_connect()
    try:
        # ---- IMPORTANT ----
        # This should match the same query you already had working.
        # If your current query differs, replace ONLY the base_sql/base_params
        # block with your existing SELECT ... FROM ... WHERE ... (without LIMIT/OFFSET).
        #
        # Columns expected by frontend:
        #   title, story_id, status, assignee, updated_at

        where = ["m.tenant_id = ?"]
        params: list = [tenant_id]

        if kind == "status":
            where.append("m.status = ?")
            params.append(value)
        else:
            # assignee bucket includes "Unassigned" bucket in UI sometimes
            if value.lower() == "unassigned":
                where.append("(COALESCE(m.owner,'') = '')")
            else:
                where.append("m.owner = ?")
                params.append(value)

        # windowed = only stories updated in time range
        if mode == "windowed" and start_utc and end_utc:
            # created_utc/updated_utc are stored as ISO strings; normalize for sqlite datetime compares
            dt_expr = "datetime(substr(replace(replace(m.updated_utc,'T',' '),'Z',''),1,19))"
            where.append(
                f"""{dt_expr} >= datetime(substr(replace(replace(?,'T',' '),'Z',''),1,19))"""
            )
            where.append(
                f"""{dt_expr} <= datetime(substr(replace(replace(?,'T',' '),'Z',''),1,19))"""
            )
            params.extend([start_utc, end_utc])

        where_sql = " AND ".join(where)

        # ---- BASE QUERY (NO LIMIT/OFFSET HERE) ----
        # If your existing working version pulls title from somewhere else,
        # edit ONLY the SELECT/JOIN below (keep the total-count wrapper logic).
        base_sql = f"""
            SELECT
              COALESCE(m2.title_sample, '') AS title,
              m.story_id AS story_id,
              COALESCE(m.status,'') AS status,
              COALESCE(m.owner,'') AS assignee,
              COALESCE(m.updated_utc,'') AS updated_at
            FROM story_meta m
            LEFT JOIN story_memory m2
              ON m2.tenant_id = m.tenant_id
             AND m2.last_story_id = m.story_id
            WHERE {where_sql}
            ORDER BY m.updated_utc DESC
        """

        # ---- TOTAL COUNT (wrap base query) ----
        total_row = conn.execute(
            f"SELECT COUNT(*) AS c FROM ({base_sql}) AS q",
            params,
        ).fetchone()

        total = int(total_row["c"] or 0) if total_row else 0

        # ---- PAGINATED ROWS ----
        rows = conn.execute(
            base_sql + " LIMIT ? OFFSET ?",
            params + [limit, offset],
        ).fetchall()

        out = []
        for r in rows:
            out.append(
                {
                    "title": str(r["title"] or ""),
                    "story_id": str(r["story_id"] or ""),
                    "status": str(r["status"] or ""),
                    "assignee": str(r["assignee"] or ""),
                    "updated_at": str(r["updated_at"] or ""),
                }
            )

        return {"rows": out, "total": total}
    finally:
        conn.close()

