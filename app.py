from __future__ import annotations

import csv
import hashlib
import io
import json
import logging
import os
import re
import sqlite3
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote, urlencode

from flask import (
    Flask,
    Response,
    abort,
    g,
    redirect,
    render_template_string,
    request,
    send_file,
    session,
)

from threatly import feeds
from threatly.admin import admin_bp, ensure_admin_tables
from threatly.state_db import write_audit_event
from threatly.cve_enrich import enrich_story_cves
from threatly.kev import get_kev_cves, story_is_kev
from threatly.rbac import has_perm, require_perm
from threatly.config import (
    KEYWORDS,
    SOURCES,
    MAX_ITEMS_PER_SOURCE,
    STORY_SIMILARITY_THRESHOLD,
    CACHE_TTL_SECONDS,
    MAX_FEED_BYTES,
    REQUEST_TIMEOUT_SECONDS,
    REPORT_DIR,
    SOURCE_WEIGHT,
    STATE_DB_PATH,
    STATUS_VALUES,
    WATCHLIST_PATH,
    REFRESH_TTL_SECONDS,
    SNAPSHOT_MAX_DAYS,
    DONE_STATUS_VALUES
)


def _db_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(STATE_DB_PATH, timeout=10)
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
    except Exception:
        pass
    return conn


from threatly.state_db import (
    init_state_db,
    # Seen is per-user:
    get_seen_map,
    toggle_seen,
    mark_seen,
    get_seen_info,
    # Meta stays global:
    get_meta_map,
    upsert_story_meta,
    _sanitize_status,
    get_meta_history,
    # Auth helpers:
    ensure_users_table,
    create_user,
    get_user_by_id,
    get_user_by_email,
    verify_user,
    # Institutional memory:
    record_story_fingerprint,
    get_memory_map,
    # User KPIs
    user_assigned_open_count,
    user_assigned_done_count,
    user_reviewed_total,
    user_reviewed_since,
    user_unreviewed_assigned_open_count,
)
from threatly.templates import TEMPLATES


from threatly.utils import (
    now_utc,
    parse_dt,
    canonicalize_url,
    RE_CVE,
    extract_indicators,
    parse_sources_param,
    parse_csv_param,
    human_dt,
    today_utc_str,
)
from threatly.watchlist import (
    ensure_watchlist_file,
    load_watchlist,
    watchlist_matches_for_story,
)

# =============================
# AUTH CONFIG
# =============================
from threatly.config import AUTH_REQUIRE_LOGIN, SECRET_KEY
APP_SECRET_KEY = (os.environ.get("SECRET_KEY") or SECRET_KEY or "").strip()


# Enterprise default: signup OFF
SIGNUP_ENABLED = os.environ.get("SIGNUP_ENABLED", "0").strip() == "1"

_last_daily_write: Dict[str, float] = {}  # date_str -> epoch


def _get_snapshot_items() -> Tuple[List[Dict[str, Any]], List[str]]:
    return feeds.get_snapshot_items()


# =============================
# APP + LOGGING
# =============================
app = Flask(__name__)
app.secret_key = APP_SECRET_KEY
if not APP_SECRET_KEY:
    raise RuntimeError("SECRET_KEY must be set (refuse to start without it).")


logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger("threatly")

# =============================
# SESSION HARDENING (enterprise)
# =============================
from threatly.config import (
    SESSION_COOKIE_SECURE,
    SESSION_COOKIE_HTTPONLY,
    SESSION_COOKIE_SAMESITE,
)

app.config.update(
    SESSION_COOKIE_HTTPONLY=bool(SESSION_COOKIE_HTTPONLY),
    SESSION_COOKIE_SAMESITE=str(SESSION_COOKIE_SAMESITE or "Lax"),
    SESSION_COOKIE_SECURE=bool(SESSION_COOKIE_SECURE),
    PERMANENT_SESSION_LIFETIME=timedelta(hours=int(os.environ.get("SESSION_HOURS", "12"))),
)



# Admin blueprint
app.register_blueprint(admin_bp)

# =============================
# TENANT (future SaaS-safe; single tenant now)
# =============================
def current_tenant_id() -> str:
    return "default"


# =============================
# SOURCE TRUST (deterministic)
# =============================
SOURCE_TRUST: Dict[str, str] = {
    "CISA Advisories": "Gov",
    "SANS Internet Storm Center (Full)": "Research",
    "Microsoft Security Blog": "Vendor",
    "Google Security Blog": "Vendor",
    "Google Threat Analysis Group (TAG)": "Research",
    "Google Cloud - Threat Intelligence (Mandiant/GTIG)": "Research",
    "Palo Alto Unit 42": "Research",
    "Proofpoint (main RSS)": "Vendor",
    "Sophos - Threat Research": "Vendor",
    "Sophos - Security Operations": "Vendor",
    "Cisco Security - Event Responses": "Vendor",
    "JPCERT/CC (English RSS)": "Research",
    "JPCERT/CC Blog (Atom)": "Research",
    "GovCERT.HK - Security Alerts": "Gov",
    "GovCERT.HK - Security Blogs": "Gov",
    "Kaspersky Securelist": "Vendor",
    "Krebs on Security": "Blog",
}

TRUST_ORDER = ["Gov", "Vendor", "Research", "Blog"]


# =============================
# REQUEST HELPERS
# =============================
def _client_ip() -> str:
    xff = (request.headers.get("X-Forwarded-For") or "").strip()
    if xff:
        return xff.split(",")[0].strip()
    return (request.remote_addr or "").strip()


def _user_agent() -> str:
    return (request.headers.get("User-Agent") or "").strip()


# =============================
# LOGIN RATE LIMIT + AUDIT (enterprise)
# =============================
LOGIN_RATE_WINDOW_SEC = int(os.environ.get("LOGIN_RATE_WINDOW_SEC", "900"))  # 15 min
LOGIN_MAX_FAILS = int(os.environ.get("LOGIN_MAX_FAILS", "6"))
LOGIN_LOCKOUT_SEC = int(os.environ.get("LOGIN_LOCKOUT_SEC", "900"))

_LOGIN_FAILS: Dict[str, Dict[str, Any]] = {}  # key -> {"fails":[ts...], "lock_until": float}
_LOGIN_LOCK = threading.Lock()


def _auth_key(ip: str, email: str) -> str:
    ip = (ip or "").strip()[:80]
    email = (email or "").strip().lower()[:254]
    return f"{ip}|{email}"


def _prune_fail_list(fails: List[float], now_ts: float) -> List[float]:
    cutoff = now_ts - float(LOGIN_RATE_WINDOW_SEC)
    return [t for t in fails if t >= cutoff]


def _check_lockout(ip: str, email: str) -> Tuple[bool, int]:
    now_ts = time.time()
    keys = [_auth_key(ip, email), _auth_key(ip, "*")]

    with _LOGIN_LOCK:
        for k in keys:
            rec = _LOGIN_FAILS.get(k)
            if not rec:
                continue
            lock_until = float(rec.get("lock_until", 0) or 0)
            if lock_until > now_ts:
                return True, int(lock_until - now_ts)

            fails = _prune_fail_list(list(rec.get("fails", []) or []), now_ts)
            if fails:
                rec["fails"] = fails
                rec["lock_until"] = 0
                _LOGIN_FAILS[k] = rec
            else:
                _LOGIN_FAILS.pop(k, None)

    return False, 0


def _record_login_failure(ip: str, email: str) -> Tuple[bool, int, int]:
    now_ts = time.time()
    pair_key = _auth_key(ip, email)
    ip_key = _auth_key(ip, "*")

    with _LOGIN_LOCK:
        pair = _LOGIN_FAILS.get(pair_key, {"fails": [], "lock_until": 0})
        pair_fails = _prune_fail_list(list(pair.get("fails", []) or []), now_ts)
        pair_fails.append(now_ts)
        pair["fails"] = pair_fails

        locked = False
        retry_after = 0
        if len(pair_fails) >= int(LOGIN_MAX_FAILS):
            pair["lock_until"] = now_ts + float(LOGIN_LOCKOUT_SEC)
            locked = True
            retry_after = int(LOGIN_LOCKOUT_SEC)

        _LOGIN_FAILS[pair_key] = pair

        ipr = _LOGIN_FAILS.get(ip_key, {"fails": [], "lock_until": 0})
        ip_fails = _prune_fail_list(list(ipr.get("fails", []) or []), now_ts)
        ip_fails.append(now_ts)
        ipr["fails"] = ip_fails
        if len(ip_fails) >= int(LOGIN_MAX_FAILS):
            ipr["lock_until"] = now_ts + float(LOGIN_LOCKOUT_SEC)
            locked = True
            retry_after = int(LOGIN_LOCKOUT_SEC)
        _LOGIN_FAILS[ip_key] = ipr

        return locked, retry_after, len(pair_fails)


def _clear_login_failures(ip: str, email: str) -> None:
    with _LOGIN_LOCK:
        _LOGIN_FAILS.pop(_auth_key(ip, email), None)
        _LOGIN_FAILS.pop(_auth_key(ip, "*"), None)


def audit_auth_event(
    event: str,
    *,
    ok: bool,
    email: str = "",
    user_id: str = "",
    reason: str = "",
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    payload = {
        "event": (event or "")[:60],
        "ok": bool(ok),
        "email": (email or "")[:254],
        "user_id": (user_id or "")[:64],
        "ip": _client_ip(),
        "ua": (_user_agent() or "")[:240],
        "reason": (reason or "")[:200],
        "ts_utc": now_utc().replace(tzinfo=timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
    }

    if extra:
        for k, v in list(extra.items())[:20]:
            payload[str(k)[:40]] = (
                v if isinstance(v, (str, int, float, bool)) else str(v)[:200]
            )

    # ✅ Persist auth events into admin_audit_events (so dashboard + enterprise audit trail work)
    try:
        details: Dict[str, Any] = {
            "ok": bool(ok),
            "reason": (reason or "")[:200],
            "fail_count_pair": None,
            "locked": None,
        }

        if extra:
            # Flatten extra into details (safe + capped)
            for k, v in list(extra.items())[:20]:
                details[str(k)[:40]] = (
                    v if isinstance(v, (str, int, float, bool)) else str(v)[:200]
                )

        write_audit_event(
            action=(event or "")[:60],
            actor_user_id=(user_id or "")[:80],
            actor_email=(email or "")[:254],
            target_type="auth",
            target_id=(email or user_id or "")[:120],
            details=details,
            ip=_client_ip(),
            user_agent=_user_agent(),
            tenant_id=current_tenant_id(),
        )
    except Exception:
        # Never break login UX if audit persistence fails
        pass

    # Keep stdout audit log too (useful in container logs)
    try:
        log.info("AUDIT %s", json.dumps(payload, separators=(",", ":"), default=str))
    except Exception:
        log.info(
            "AUDIT event=%s ok=%s email=%s user_id=%s reason=%s",
            event,
            ok,
            email,
            user_id,
            reason,
        )



# =============================
# SESSION USER HELPERS
# =============================
def current_user_id() -> Optional[str]:
    uid = session.get("uid")
    return str(uid) if uid else None


def current_user_email() -> str:
    em = (session.get("email") or "").strip()
    if em:
        return em
    uid = current_user_id()
    if not uid:
        return ""
    u = get_user_by_id(uid)
    return (u or {}).get("email", "")


def current_user_new_since_dt() -> Tuple[datetime, str]:
    """
    Returns (window_start_dt, label)
    - If user has prev_login_utc, use it: "last login"
    - Else fall back to 24h ago: "yesterday"
    """
    # Prefer session (set on login), then g.user (loaded on request), then fallback.
    prev = (session.get("prev_login_utc") or "").strip()
    if not prev:
        try:
            prev = str((g.user or {}).get("prev_login_utc") or "").strip()
        except Exception:
            prev = ""

    dt = parse_dt(prev) if prev else None
    if dt:
        return dt, "last login"

    return now_utc() - timedelta(hours=24), "yesterday"


def login_required() -> Optional[Response]:
    if current_user_id():
        return None
    next_url = request.full_path if request.query_string else request.path
    return redirect("/login?next=" + quote(next_url, safe=""))


def require_auth_or_401() -> Optional[Response]:
    if current_user_id():
        return None
    return Response(
        json.dumps({"ok": False, "error": "auth_required"}),
        status=401,
        mimetype="application/json",
    )


def enforce_login_if_configured() -> Optional[Response]:
    if AUTH_REQUIRE_LOGIN and not current_user_id():
        return login_required()
    return None


# =============================
# CSRF (enterprise-friendly)
# =============================
def _ensure_csrf_token() -> str:
    tok = session.get("csrf")
    if tok:
        return str(tok)
    tok = hashlib.sha256(os.urandom(32)).hexdigest()
    session["csrf"] = tok
    return tok


def _require_csrf_or_403() -> Optional[Response]:
    if request.method != "POST":
        return None
    if not request.path.startswith("/api/"):
        return None
    if not current_user_id():
        return None

    host = (request.host_url or "").rstrip("/")
    origin = (request.headers.get("Origin") or "").strip().rstrip("/")
    if origin and origin == host:
        return None

    referer = (request.headers.get("Referer") or "").strip()
    if referer and (referer.startswith(host + "/") or referer == host):
        return None

    expected = (session.get("csrf") or "").strip() or _ensure_csrf_token()

    sent = (request.headers.get("X-CSRF-Token") or "").strip()
    if not sent:
        try:
            data = request.get_json(silent=True) or {}
            sent = str(data.get("csrf") or "").strip()
        except Exception:
            sent = ""

    if not sent or sent != expected:
        return Response(
            json.dumps({"ok": False, "error": "csrf_failed"}),
            status=403,
            mimetype="application/json",
        )

    return None


# =============================
# RBAC USER LOADER (CRITICAL)
# =============================
@app.before_request
def load_user():
    g.user = None
    uid = session.get("uid")
    if not uid:
        return

    u = get_user_by_id(str(uid))
    if not u:
        session.clear()
        return

    role = (u.get("role") or "viewer").strip().lower()
    is_active = int(u.get("is_active", 0) or 0)

    if is_active != 1:
        session.clear()
        return

    g.user = {
        "user_id": u["user_id"],
        "email": u.get("email", ""),
        "role": role,
        "is_active": is_active,
        # ✅ login timestamps (for "new since last login")
        "last_login_utc": str(u.get("last_login_utc", "") or ""),
        "prev_login_utc": str(u.get("prev_login_utc", "") or ""),
    }


@app.before_request
def csrf_guard():
    gate = _require_csrf_or_403()
    if gate:
        return gate
    if current_user_id():
        _ensure_csrf_token()


# =============================
# BOOTSTRAP FIRST ADMIN (env-based)
# =============================
def bootstrap_first_admin_if_empty() -> None:
    try:
        from threatly.state_db import count_users, set_user_role
    except Exception:
        return

    try:
        if count_users() > 0:
            return

        email = (os.getenv("BOOTSTRAP_ADMIN_EMAIL") or "").strip().lower()
        pw = os.getenv("BOOTSTRAP_ADMIN_PASSWORD") or ""
        if not email or "@" not in email or len(pw) < 10:
            return

        create_user(email=email, password=pw)
        user_id = hashlib.sha1(email.encode("utf-8", errors="ignore")).hexdigest()[:16]
        set_user_role(user_id, "admin")
        log.info("Bootstrapped first admin: %s", email)
    except Exception as ex:
        log.warning("Admin bootstrap degraded: %s", ex)


# =============================
# STORIES / DEDUPE
# =============================
STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "to",
    "of",
    "in",
    "on",
    "for",
    "with",
    "by",
    "from",
    "at",
    "as",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "this",
    "that",
    "these",
    "those",
    "it",
    "its",
    "into",
    "over",
    "after",
    "before",
    "new",
    "update",
    "security",
    "blog",
}


def normalize_title(title: str) -> List[str]:
    t = (title or "").lower()
    t = re.sub(r"[^a-z0-9\s\-_/]", " ", t)
    toks = [w for w in t.split() if w and w not in STOPWORDS]
    toks = [w.replace("cve–", "cve-").replace("cve—", "cve-") for w in toks]
    return toks


def jaccard(a: List[str], b: List[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def story_key(item: Dict[str, Any]) -> str:
    title = item.get("title", "") or ""
    m = RE_CVE.search(title)
    if m:
        return m.group(0).upper()
    toks = normalize_title(title)
    base = " ".join(toks) if toks else (item.get("link") or "")
    return hashlib.sha1(base.encode("utf-8", errors="ignore")).hexdigest()[:12]


def choose_story_lead(cluster: List[Dict[str, Any]]) -> Dict[str, Any]:
    def score(a: Dict[str, Any]) -> Tuple[int, datetime]:
        w = SOURCE_WEIGHT.get(a.get("source", ""), 10)
        dt = a.get("published_dt") or datetime.min
        return (w, dt)

    return max(cluster, key=score)


def categorize_story(title: str, summary: str, matched_keywords: List[str]) -> List[str]:
    t = f"{title or ''} {summary or ''} {' '.join(matched_keywords or [])}".lower()
    cats: List[str] = []

    if any(x in t for x in ["ransomware", "double extortion", "wiper"]):
        cats.append("Ransomware")
    if any(
        x in t
        for x in [
            "phishing",
            "spear phishing",
            "bec",
            "business email compromise",
            "smishing",
            "vishing",
            "account takeover",
            "ato",
            "impersonation",
        ]
    ):
        cats.append("Phishing/Identity")
    if any(
        x in t
        for x in [
            "cloud",
            "iam",
            "oauth",
            "token theft",
            "api abuse",
            "credential exposure",
            "cloud misconfiguration",
        ]
    ):
        cats.append("Cloud/IAM")
    if any(
        x in t
        for x in [
            "supply chain",
            "dependency confusion",
            "typosquatting",
            "malicious package",
            "open source compromise",
            "ci/cd",
            "pipeline compromise",
        ]
    ):
        cats.append("Supply chain")
    if any(
        x in t
        for x in [
            "cve",
            "zero-day",
            "0day",
            "n-day",
            "remote code execution",
            " rce",
            "authentication bypass",
            "privilege escalation",
            "sandbox escape",
            "weaponized",
            "public exploit",
            "metasploit",
            "proof of concept",
            "poc",
        ]
    ):
        cats.append("Vuln/Exploit")
    if any(
        x in t
        for x in [
            "apt",
            "nation-state",
            "threat actor",
            "campaign",
            "operation",
            "intrusion set",
            "cluster",
            "espionage",
        ]
    ):
        cats.append("Threat actor/Campaign")
    if any(
        x in t
        for x in [
            "botnet",
            "backdoor",
            "dropper",
            "loader",
            "beaconing",
            "command and control",
            "c2",
        ]
    ):
        cats.append("Malware")

    out: List[str] = []
    seen = set()
    for c in cats:
        if c not in seen:
            seen.add(c)
            out.append(c)
    return out


def _rel_time_from_any(value: Any) -> str:
    """
    Robust relative time for timestamps that may be:
      - ISO strings with trailing Z (e.g. 2026-01-06T03:12:11Z)
      - ISO strings with offsets (e.g. ...+00:00)
      - naive ISO (assume UTC)
    We compute deltas using naive UTC to avoid tz-mismatch surprises.
    """
    if value is None:
        return ""
    s = str(value).strip()
    if not s:
        return ""

    def _parse_to_utc_naive(ts: str) -> Optional[datetime]:
        t = (ts or "").strip()
        if not t:
            return None

        # Normalize "Z" into "+00:00" for fromisoformat
        t_iso = (t[:-1] + "+00:00") if t.endswith("Z") else t

        dt: Optional[datetime] = None

        # Try Python ISO parser first
        try:
            dt = datetime.fromisoformat(t_iso)
        except Exception:
            dt = None

        # Fall back to your shared parser
        if dt is None:
            try:
                dt = parse_dt(t)
            except Exception:
                dt = None

        if dt is None:
            return None

        # Convert aware -> UTC naive
        try:
            if dt.tzinfo is not None:
                dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
        except Exception:
            # If conversion fails, treat as UTC naive
            try:
                dt = dt.replace(tzinfo=None)
            except Exception:
                return None

        return dt

    try:
        dt = _parse_to_utc_naive(s)
        if not dt:
            return ""

        now = datetime.now(timezone.utc).replace(tzinfo=None)  # naive UTC
        sec = int((now - dt).total_seconds())
        if sec < 0:
            sec = 0

        if sec < 60:
            return f"{sec}s ago"
        mins = sec // 60
        if mins < 60:
            return f"{mins}m ago"
        hrs = mins // 60
        if hrs < 48:
            return f"{hrs}h ago"
        days = hrs // 24
        return f"{days}d ago"
    except Exception:
        return ""

def iso_utc_z(dt: datetime) -> str:
    return dt.replace(tzinfo=timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")




def compute_severity(story: Dict[str, Any]) -> Dict[str, Any]:
    title = (story.get("title") or "").lower()
    summary = (story.get("summary") or "").lower()
    text = f"{title} {summary}"

    score = 0
    reasons: List[str] = []

    lead = (story.get("articles") or [{}])[0]
    lead_src = lead.get("source", "")
    w = SOURCE_WEIGHT.get(lead_src, 10)
    score += int(w / 10)
    if lead_src:
        reasons.append(f"Lead source: {lead_src}")

    src_count = int(story.get("sources_count", 1) or 1)
    if src_count >= 3:
        score += 12
        reasons.append("Corroborated by ≥3 sources")
    elif src_count == 2:
        score += 7
        reasons.append("Corroborated by 2 sources")

    cves = (story.get("indicators") or {}).get("cves", []) or []
    if cves:
        score += 12
        reasons.append(f"CVE mentioned ({min(len(cves), 5)} shown)")

    if story.get("kev", False):
        score += 28
        reasons.append("CISA KEV listed (known exploited)")

    if any(
        p in text
        for p in [
            "actively exploited",
            "in the wild",
            "exploitation observed",
            "mass exploitation",
            "weaponized",
        ]
    ):
        score += 25
        reasons.append("Active exploitation signal (in-the-wild/weaponized)")

    if any(
        p in text
        for p in [
            "remote code execution",
            " rce",
            "authentication bypass",
            "privilege escalation",
            "sandbox escape",
        ]
    ):
        score += 18
        reasons.append("High-impact exploit class (RCE/Auth bypass/EoP)")

    if any(p in text for p in ["ransomware", "double extortion", "wiper"]):
        score += 22
        reasons.append("Ransomware/wiper signal")

    if any(
        p in text
        for p in [
            "supply chain",
            "typosquatting",
            "dependency confusion",
            "token theft",
            "oauth",
            "iam misconfiguration",
            "api abuse",
        ]
    ):
        score += 10
        reasons.append("High blast-radius vector (supply chain/cloud identity)")

    i = story.get("indicators") or {}
    ioc_count = sum(
        len(i.get(k, []) or [])
        for k in ["ips", "domains", "urls", "md5", "sha1", "sha256"]
    )
    if ioc_count >= 10:
        score += 8
        reasons.append("High IOC density (≥10)")
    elif ioc_count >= 1:
        score += 3
        reasons.append("Has IOCs")

    dt: Optional[datetime] = story.get("published_dt")
    if dt:
        age_hours = (now_utc() - dt).total_seconds() / 3600.0
        if age_hours <= 24:
            score += 10
            reasons.append("Fresh (≤24h)")
        elif age_hours <= 72:
            score += 5
            reasons.append("Recent (≤72h)")

    if score >= 70:
        level = "Critical"
    elif score >= 50:
        level = "High"
    elif score >= 30:
        level = "Medium"
    else:
        level = "Low"

    return {
        "level": level,
        "score": score,
        "reasons": reasons[:6],
        "ioc_count": ioc_count,
    }


def _stable_story_id(story_key_value: str, lead_link: str, title: str) -> str:
    if (story_key_value or "").upper().startswith("CVE-"):
        return hashlib.sha1(
            story_key_value.upper().encode("utf-8", errors="ignore")
        ).hexdigest()[:12]

    link = canonicalize_url(lead_link or "")
    if link:
        return hashlib.sha1(link.encode("utf-8", errors="ignore")).hexdigest()[:12]

    toks = normalize_title(title or "")
    base = " ".join(toks) if toks else (title or "")
    return hashlib.sha1(base.encode("utf-8", errors="ignore")).hexdigest()[:12]


def _trust_for_source(src: str) -> str:
    s = (src or "").strip()
    if not s:
        return "Research"
    if s in SOURCE_TRUST:
        return SOURCE_TRUST[s]
    sl = s.lower()
    if "cisa" in sl or "gov" in sl:
        return "Gov"
    if "microsoft" in sl or "google" in sl or "sophos" in sl or "proofpoint" in sl:
        return "Vendor"
    if "blog" in sl:
        return "Blog"
    return "Research"


def _memory_fingerprint(story: Dict[str, Any]) -> str:
    cves = ((story.get("indicators") or {}).get("cves") or [])
    if cves:
        return str(cves[0]).upper()
    return str(story.get("key") or "")


# =============================
# CAMPAIGNS (Threat Actor Profiling + Relationship Graph MVP)
# =============================
RE_ACTOR = re.compile(
    r"\b("
    r"apt\s?\d{1,3}|"
    r"fin\s?\d{1,4}|"
    r"lazarus|sandworm|cozy\s?bear|"
    r"midnight\s?blizzard|nobelium|"
    r"scattered\s?spider|"
    r"lockbit|alphv|blackcat|cl0p|akira|"
    r"conti|ryuk|revil|darkside"
    r")\b",
    flags=re.IGNORECASE,
)


def _canon_actor_label(raw: str) -> str:
    s = (raw or "").strip()
    if not s:
        return ""
    s = re.sub(r"\s+", " ", s)
    return s.title().replace("Apt", "APT").replace("Fin", "FIN").replace("Cl0P", "Cl0p")


def _campaign_seed_for_story(story: Dict[str, Any]) -> Tuple[str, str]:
    ind = story.get("indicators") or {}
    cves = sorted({str(x).upper() for x in (ind.get("cves") or []) if str(x).strip()})
    if cves:
        return f"CVE:{cves[0]}", cves[0]

    text = f"{story.get('title','')} {story.get('summary','')}"
    m = RE_ACTOR.search(text or "")
    if m:
        actor = _canon_actor_label(m.group(0))
        return f"ACTOR:{actor.lower()}", actor

    domains = sorted({str(x).lower() for x in (ind.get("domains") or []) if str(x).strip()})
    if domains:
        return f"DOM:{domains[0]}", domains[0]

    toks = normalize_title(story.get("title", ""))[:5]
    lead_src = (story.get("lead_source") or "").strip().lower()
    seed = " ".join(toks) if toks else (story.get("title") or "campaign")
    seed = seed[:120]
    return f"TXT:{seed}|SRC:{lead_src}", (story.get("title") or "Campaign")[:80]


def compute_campaign_id(story: Dict[str, Any]) -> str:
    seed, _ = _campaign_seed_for_story(story)
    return hashlib.sha1(seed.encode("utf-8", errors="ignore")).hexdigest()[:12]


def compute_campaign_label(story: Dict[str, Any]) -> str:
    _, label = _campaign_seed_for_story(story)
    if (label or "").upper().startswith("CVE-"):
        return f"Campaign: {label.upper()}"
    if RE_ACTOR.search(label or ""):
        return f"Actor: {label}"
    return f"Campaign: {label}"


def ensure_campaign_tables() -> None:
    conn = _db_conn()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS campaigns(
              campaign_id TEXT PRIMARY KEY,
              tenant_id TEXT NOT NULL,
              label TEXT NOT NULL,
              first_seen_utc TEXT,
              last_seen_utc TEXT,
              story_count INTEGER NOT NULL DEFAULT 0,
              meta_json TEXT NOT NULL DEFAULT '{}'
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS story_campaign_events(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              ts_utc TEXT NOT NULL,
              tenant_id TEXT NOT NULL,
              campaign_id TEXT NOT NULL,
              story_id TEXT NOT NULL,
              actor_user_id TEXT,
              actor_email TEXT,
              event TEXT NOT NULL,
              meta_json TEXT
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_campaigns_tenant ON campaigns(tenant_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sce_campaign ON story_campaign_events(campaign_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sce_story ON story_campaign_events(story_id)")
        conn.commit()
    finally:
        conn.close()


def upsert_campaign_from_story(*, tenant_id: str, story: Dict[str, Any]) -> None:
    ensure_campaign_tables()
    cid = (story.get("campaign_id") or "").strip()
    if not cid:
        return

    label = (story.get("campaign_label") or "").strip() or "Campaign"
    pub = story.get("published_dt")
    pub_utc = ""
    if isinstance(pub, datetime):
        pub_utc = pub.isoformat(timespec="seconds") + "Z"

    conn = _db_conn()
    try:
        row = conn.execute(
            "SELECT story_count, first_seen_utc, last_seen_utc FROM campaigns WHERE tenant_id=? AND campaign_id=?",
            (tenant_id, cid),
        ).fetchone()
        if not row:
            conn.execute(
                """
                INSERT INTO campaigns(campaign_id, tenant_id, label, first_seen_utc, last_seen_utc, story_count, meta_json)
                VALUES(?,?,?,?,?,?,?)
                """,
                (cid, tenant_id, label, pub_utc or "", pub_utc or "", 1, json.dumps({}, separators=(",", ":"))),
            )
            conn.commit()
            return

        story_count = int(row[0] or 0)
        first_seen = str(row[1] or "")
        last_seen = str(row[2] or "")

        new_first = first_seen or pub_utc
        new_last = last_seen or pub_utc
        if pub_utc:
            if first_seen and pub_utc < first_seen:
                new_first = pub_utc
            if last_seen and pub_utc > last_seen:
                new_last = pub_utc

        conn.execute(
            """
            UPDATE campaigns
            SET label=?, first_seen_utc=?, last_seen_utc=?, story_count=?
            WHERE tenant_id=? AND campaign_id=?
            """,
            (label, new_first or "", new_last or "", story_count + 1, tenant_id, cid),
        )
        conn.commit()
    finally:
        conn.close()


def record_campaign_event(
    *,
    tenant_id: str,
    campaign_id: str,
    story_id: str,
    actor_user_id: str,
    actor_email: str,
    event: str,
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    ensure_campaign_tables()
    ts = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    conn = _db_conn()
    try:
        conn.execute(
            """
            INSERT INTO story_campaign_events(ts_utc,tenant_id,campaign_id,story_id,actor_user_id,actor_email,event,meta_json)
            VALUES(?,?,?,?,?,?,?,?)
            """,
            (
                ts,
                (tenant_id or "")[:80],
                (campaign_id or "")[:40],
                (story_id or "")[:120],
                (actor_user_id or "")[:80],
                (actor_email or "")[:254],
                (event or "")[:60],
                json.dumps(meta or {}, separators=(",", ":"), default=str),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def build_campaign_graph(stories: List[Dict[str, Any]], campaign_label: str) -> Dict[str, Any]:
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []

    root_id = "campaign"
    nodes.append({"id": root_id, "label": campaign_label, "type": "campaign"})

    def add_node(nid: str, label: str, ntype: str):
        if not nid:
            return
        for n in nodes:
            if n["id"] == nid:
                return
        nodes.append({"id": nid, "label": label, "type": ntype})

    def add_edge(src: str, tgt: str, label: str):
        edges.append({"source": src, "target": tgt, "label": label})

    cves: Dict[str, int] = {}
    domains: Dict[str, int] = {}
    ips: Dict[str, int] = {}
    urls: Dict[str, int] = {}
    hashes: Dict[str, int] = {}
    cats: Dict[str, int] = {}
    sources: Dict[str, int] = {}

    for s in stories:
        ind = s.get("indicators") or {}
        for x in (ind.get("cves") or [])[:50]:
            k = str(x).upper()
            cves[k] = cves.get(k, 0) + 1
        for x in (ind.get("domains") or [])[:50]:
            k = str(x).lower()
            domains[k] = domains.get(k, 0) + 1
        for x in (ind.get("ips") or [])[:50]:
            k = str(x)
            ips[k] = ips.get(k, 0) + 1
        for x in (ind.get("urls") or [])[:50]:
            k = str(x)
            urls[k] = urls.get(k, 0) + 1
        for klist in ["md5", "sha1", "sha256"]:
            for x in (ind.get(klist) or [])[:50]:
                k = str(x).lower()
                hashes[k] = hashes.get(k, 0) + 1
        for c in (s.get("categories") or [])[:20]:
            cats[str(c)] = cats.get(str(c), 0) + 1
        ls = (s.get("lead_source") or "").strip()
        if ls:
            sources[ls] = sources.get(ls, 0) + 1

    def top_items(m: Dict[str, int], n: int) -> List[Tuple[str, int]]:
        return sorted(m.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)[:n]

    for v, cnt in top_items(cves, 10):
        nid = f"cve:{v}"
        add_node(nid, v, "cve")
        add_edge(root_id, nid, f"{cnt}×")
    for v, cnt in top_items(domains, 10):
        nid = f"dom:{v}"
        add_node(nid, v, "domain")
        add_edge(root_id, nid, f"{cnt}×")
    for v, cnt in top_items(ips, 8):
        nid = f"ip:{v}"
        add_node(nid, v, "ip")
        add_edge(root_id, nid, f"{cnt}×")
    for v, cnt in top_items(urls, 6):
        nid = f"url:{hashlib.sha1(v.encode('utf-8', errors='ignore')).hexdigest()[:10]}"
        add_node(nid, v[:60] + ("…" if len(v) > 60 else ""), "url")
        add_edge(root_id, nid, f"{cnt}×")
    for v, cnt in top_items(hashes, 8):
        nid = f"hash:{v[:12]}"
        add_node(nid, v[:12] + "…", "hash")
        add_edge(root_id, nid, f"{cnt}×")
    for v, cnt in top_items(cats, 10):
        nid = f"cat:{v}"
        add_node(nid, v, "category")
        add_edge(root_id, nid, f"{cnt}×")
    for v, cnt in top_items(sources, 10):
        nid = f"src:{v}"
        add_node(nid, v, "source")
        add_edge(root_id, nid, f"{cnt}×")

    if len(nodes) > 60:
        nodes = nodes[:60]
    if len(edges) > 100:
        edges = edges[:100]

    return {"nodes": nodes, "edges": edges}


# =============================
# FEATURE 3: STORY LIFECYCLE TIMELINE (append-only)
# =============================
def ensure_story_lifecycle_tables() -> None:
    conn = _db_conn()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS story_lifecycle_events(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              ts_utc TEXT NOT NULL,
              tenant_id TEXT NOT NULL,
              story_id TEXT NOT NULL,
              actor_user_id TEXT,
              actor_email TEXT,
              event_type TEXT NOT NULL,   -- reviewed_toggle, reviewed_open, status_changed, owner_changed, notes_updated, assigned_to_me
              field TEXT NOT NULL,        -- seen/status/owner/notes
              old_value TEXT NOT NULL,
              new_value TEXT NOT NULL,
              meta_json TEXT NOT NULL DEFAULT '{}'
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sle_story_ts ON story_lifecycle_events(story_id, ts_utc)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sle_tenant_story_ts ON story_lifecycle_events(tenant_id, story_id, ts_utc)")
        conn.commit()
    finally:
        conn.close()


def _log_story_lifecycle_event(
    *,
    tenant_id: str,
    story_id: str,
    actor_user_id: str,
    actor_email: str,
    event_type: str,
    field: str,
    old_value: str = "",
    new_value: str = "",
    meta: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Append-only audit trail.

    Hard rule: do NOT log no-op changes (old == new), even if called repeatedly
    (e.g., page refreshes, idempotent review operations).
    """
    def _norm(v: Any) -> str:
        s = "" if v is None else str(v)
        # Normalize whitespace + case to avoid "same value" looking different
        s = s.replace("\r\n", "\n").replace("\r", "\n")
        s = re.sub(r"\s+", " ", s).strip()
        return s

    try:
        f = (field or "").strip().lower()

        o = _norm(old_value)
        n = _norm(new_value)

        # Special-case: "seen" often comes through as 0/1, True/False, etc.
        if f in {"seen", "reviewed"}:
            truthy = {"1", "true", "yes", "y", "on"}
            falsy = {"0", "false", "no", "n", "off", ""}
            o2 = "1" if o.lower() in truthy else ("0" if o.lower() in falsy else o)
            n2 = "1" if n.lower() in truthy else ("0" if n.lower() in falsy else n)
            o, n = o2, n2

        # ✅ NO-OP guard: if nothing changed, do not log anything
        if o == n:
            return

        ts = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        conn = _db_conn()
        try:
            conn.execute(
                """
                INSERT INTO story_lifecycle_events(
                  ts_utc, tenant_id, story_id,
                  actor_user_id, actor_email,
                  event_type, field, old_value, new_value, meta_json
                )
                VALUES(?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    (ts or "")[:32],
                    (tenant_id or "")[:80],
                    (story_id or "")[:120],
                    (actor_user_id or "")[:80],
                    (actor_email or "")[:254],
                    (event_type or "")[:60],
                    (field or "")[:60],
                    str(o or "")[:2000],
                    str(n or "")[:2000],
                    json.dumps(meta or {}, separators=(",", ":"), default=str),
                ),
            )
            conn.commit()
        finally:
            conn.close()
    except Exception:
        # Never break user workflows because a log insert failed
        log.exception("lifecycle log degraded")



def get_story_lifecycle_events(*, tenant_id: str, story_id: str, limit: int = 120) -> List[Dict[str, Any]]:
    conn = _db_conn()
    try:
        cur = conn.execute(
            """
            SELECT ts_utc, actor_email, event_type, field, old_value, new_value, meta_json
            FROM story_lifecycle_events
            WHERE tenant_id=? AND story_id=?
            ORDER BY ts_utc DESC
            LIMIT ?
            """,
            ((tenant_id or "")[:80], (story_id or "")[:120], int(limit)),
        )
        rows = cur.fetchall()
    finally:
        conn.close()

    out: List[Dict[str, Any]] = []
    for r in rows:
        ts_utc = str(r[0] or "")
        actor_email = str(r[1] or "")
        event_type = str(r[2] or "")
        field = str(r[3] or "")
        old_value = str(r[4] or "")
        new_value = str(r[5] or "")
        meta_json = str(r[6] or "{}")
        try:
            meta = json.loads(meta_json) if meta_json else {}
        except Exception:
            meta = {}
        out.append(
            {
                "ts_utc": ts_utc,
                "actor_email": actor_email,
                "event_type": event_type,
                "field": field,
                "old_value": old_value,
                "new_value": new_value,
                "meta": meta,
            }
        )
    return out


_LIFECYCLE_SNIPPET = r"""
<style>
  .audit-wrap{ max-width:1100px; margin:18px auto 34px; padding:0 14px; }
  .audit-card{
    border:1px solid rgba(255,255,255,.10);
    border-radius:14px;
    background: rgba(24,24,27,.55);
    box-shadow: 0 10px 25px rgba(0,0,0,.40);
    overflow:hidden;
  }
  .audit-head{
    display:flex; justify-content:space-between; align-items:center; gap:12px;
    padding:14px 16px;
    border-bottom:1px solid rgba(255,255,255,.07);
    background: rgba(0,0,0,.18);
  }
  .audit-title{
    display:flex; align-items:center; gap:10px;
    font-weight:950; letter-spacing:-.2px; font-size:16px;
    color: rgba(250,250,250,.96);
  }
  .audit-sub{ color: rgba(250,250,250,.60); font-weight:900; font-size:12px; }
  .audit-badge{
    display:inline-flex; align-items:center; gap:8px;
    padding:6px 10px; border-radius:999px;
    border:1px solid rgba(255,255,255,.10);
    background: rgba(255,255,255,.03);
    color: rgba(250,250,250,.78);
    font-weight:900; font-size:12px;
  }
  .audit-table{ width:100%; border-collapse:collapse; }
  .audit-table th{
    text-align:left;
    font-size:12px; letter-spacing:.18em; text-transform:uppercase;
    color: rgba(250,250,250,.55);
    font-weight:950;
    padding:12px 16px;
    border-bottom:1px solid rgba(255,255,255,.07);
  }
  .audit-table td{
    padding:12px 16px;
    border-bottom:1px solid rgba(255,255,255,.06);
    vertical-align:top;
    color: rgba(250,250,250,.86);
    font-weight:850;
  }
  .audit-table tr:hover td{ background: rgba(255,255,255,.02); }

  .aud-when{ color: rgba(250,250,250,.72); font-weight:900; white-space:nowrap; }
  .aud-who{ color: rgba(250,250,250,.90); font-weight:950; white-space:nowrap; }
  .aud-pill{
    display:inline-flex; align-items:center; gap:8px;
    padding:6px 10px; border-radius:999px;
    border:1px solid rgba(255,255,255,.10);
    background: rgba(255,255,255,.03);
    color: rgba(250,250,250,.88);
    font-weight:950; font-size:12px; white-space:nowrap;
  }
  .aud-pill.warn{ border-color: rgba(245,158,11,.35); background: rgba(245,158,11,.12); }
  .aud-pill.good{ border-color: rgba(34,197,94,.35); background: rgba(34,197,94,.12); }
  .aud-field{
    display:inline-flex; align-items:center;
    padding:5px 9px; border-radius:999px;
    border:1px solid rgba(255,255,255,.08);
    background: rgba(255,255,255,.02);
    color: rgba(250,250,250,.70);
    font-weight:900; font-size:12px;
    margin-left:8px; white-space:nowrap;
  }
  details.aud-details{
    margin-top:8px;
    border:1px solid rgba(255,255,255,.08);
    background: rgba(0,0,0,.18);
    border-radius:10px;
    padding:10px 12px;
  }
  details.aud-details > summary{
    cursor:pointer;
    color: rgba(250,250,250,.70);
    font-weight:900;
    list-style:none;
  }
  details.aud-details > summary::-webkit-details-marker{ display:none; }
  .aud-change{
    margin-top:10px;
    display:grid;
    grid-template-columns:64px 1fr;
    gap:10px 12px;
    align-items:start;
    font-weight:850;
    color: rgba(250,250,250,.88);
  }
  .aud-k{ color: rgba(161,161,170,.95); font-weight:950; }
  .aud-mono{
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono","Courier New", monospace;
    font-weight:900;
    white-space: pre-wrap;   /* wrap normally, preserve newlines */
    word-break: break-word;  /* break long tokens without letter-stacking */
    overflow-wrap: normal;   /* NOT anywhere */
}

</style>

<div class="audit-wrap">
  <div class="audit-card">
    <div class="audit-head">
      <div class="audit-title">
        <span style="opacity:.85;">🧾</span>
        Lifecycle
        <span class="audit-badge">{{ (lifecycle|length) if lifecycle else 0 }} events</span>
      </div>
      <div class="audit-sub">Audit trail (append-only)</div>
    </div>

    {% if lifecycle and lifecycle|length %}
      <table class="audit-table">
        <thead>
          <tr>
            <th style="width:120px;">WHEN</th>
            <th style="width:140px;">WHO</th>
            <th style="width:220px;">ACTION</th>
            <th style="min-width:420px;">DETAILS</th>

          </tr>
        </thead>
        <tbody>
          {% for ev in lifecycle %}
            {% set actor = (ev.actor_email or "system").split("@",1)[0] %}
            {% set action = (ev.event_type or '')|replace('_',' ')|title %}
            {% set field = (ev.field or '') %}
            {% set oldv = (ev.old_value or '') %}
            {% set newv = (ev.new_value or '') %}
            <tr>
              <td>
                <div class="aud-when" title="{{ ev.ts_utc }}">{{ rel_time(ev.ts_utc) }}</div>
              </td>
              <td><div class="aud-who">{{ actor }}</div></td>
              <td>
                {% if field == "seen" %}
                  <span class="aud-pill good">{{ action }}</span>
                {% elif field in ["status","owner"] %}
                  <span class="aud-pill warn">{{ action }}</span>
                {% else %}
                  <span class="aud-pill">{{ action }}</span>
                {% endif %}
                <span class="aud-field">{{ field }}</span>
              </td>
              <td>
                {% if oldv or newv %}
                  <details class="aud-details">
                    <summary>View change</summary>
                    <div class="aud-change">
                      <div class="aud-k">From</div>
                      <div class="aud-mono">{{ oldv if oldv else "—" }}</div>
                      <div class="aud-k">To</div>
                      <div class="aud-mono">{{ newv if newv else "—" }}</div>
                    </div>
                  </details>
                {% else %}
                  <span style="color: rgba(250,250,250,.55); font-weight:900;">—</span>
                {% endif %}
              </td>
            </tr>
          {% endfor %}
        </tbody>
      </table>
    {% else %}
      <div style="padding:14px 16px; color: rgba(250,250,250,.65); font-weight:900;">
        No lifecycle events yet. Reviewed, Status, Owner, and Notes changes will appear here.
      </div>
    {% endif %}
  </div>
</div>
"""




def cluster_into_stories(
    items: List[Dict[str, Any]], similarity_threshold: float
) -> List[Dict[str, Any]]:
    buckets: Dict[str, List[Dict[str, Any]]] = {}
    for it in items:
        buckets.setdefault(story_key(it), []).append(it)

    stories: List[Dict[str, Any]] = []
    for k, bucket_items in buckets.items():
        is_cve = k.startswith("CVE-")
        clusters: List[List[Dict[str, Any]]] = []

        if is_cve:
            clusters = [bucket_items]
        else:
            reps: List[List[str]] = []
            for it in bucket_items:
                toks = normalize_title(it.get("title", ""))
                placed = False
                for idx, rep in enumerate(reps):
                    if jaccard(toks, rep) >= similarity_threshold:
                        clusters[idx].append(it)
                        reps[idx] = list(set(rep) | set(toks))
                        placed = True
                        break
                if not placed:
                    clusters.append([it])
                    reps.append(toks)

        for cluster in clusters:
            cluster.sort(
                key=lambda x: x.get("published_dt") or datetime.min, reverse=True
            )
            lead = choose_story_lead(cluster)

            story_title = lead.get("title") or "Untitled"
            story_summary = ""
            for a in cluster:
                s = (a.get("summary") or "").strip()
                if s:
                    story_summary = s
                    break

            kw_set = set()
            for a in cluster:
                for kw in a.get("matched_keywords", []):
                    kw_set.add(kw)

            merged_text = " ".join(
                f"{a.get('title','')} {a.get('summary_full') or a.get('summary','')}"
                for a in cluster
            )
            indicators = extract_indicators(merged_text)
            # ===== Threat Actor Profiling (story-level) =====
            # Keep actor logic in feeds.py; app.py just calls it.
            actor_label, actor_id = feeds.derive_actor_label_and_id(story_title, merged_text)


            sid = _stable_story_id(k, lead.get("link", ""), story_title)

            lead_src = lead.get("source", "")
            trust = _trust_for_source(lead_src)

            story = {
                "story_id": sid,
                "key": k,
                "title": story_title,
                "summary": story_summary,
                "published_dt": cluster[0].get("published_dt"),
                "published": cluster[0].get("published") or "",
                "thumbnail": lead.get("thumbnail", ""),
                "matched_keywords": sorted(kw_set),
                "articles": cluster,
                "sources_count": len({a.get("source") for a in cluster}),
                "indicators": indicators,
                "lead_source": lead_src,
                "trust": trust,
                "summary_full": merged_text,
                "actor_label": actor_label,
                "actor_id": actor_id,

            }

            story["kev"] = story_is_kev(story)
            story["categories"] = categorize_story(
                story["title"], story["summary"], story.get("matched_keywords", [])
            )
            story["severity"] = compute_severity(story)
            story["memory_fp"] = _memory_fingerprint(story)

            story["campaign_id"] = compute_campaign_id(story)
            story["campaign_label"] = compute_campaign_label(story)

            stories.append(story)

    stories.sort(key=lambda s: s.get("published_dt") or datetime.min, reverse=True)
    return stories


# =============================
# QUERY PARAMS + QS
# =============================
ALLOWED_PARAMS = {
    "q",
    "sources",
    "sort",
    "days",
    "min_sources",
    "exclude",
    "kw",
    "view",
    "story_id",
    "sev_min",
    "kev",
    "has_iocs",
    "cat",
    "seen",
    "status",
    "stack",
    "delta",
    "actor",
    "mine",
    "kpi",
}

SEV_ORDER = {"Low": 0, "Medium": 1, "High": 2, "Critical": 3}


def get_params_dict() -> Dict[str, Any]:
    q = (request.args.get("q") or "").strip()
    sort = (request.args.get("sort") or "newest").strip()
    view = (request.args.get("view") or "cards").strip()
    exclude = (request.args.get("exclude") or "").strip()
    kw = (request.args.get("kw") or "").strip()
    mine = (request.args.get("mine", "").strip() == "1")
    kpi = (request.args.get("kpi", "").strip())


    sources_raw = (request.args.get("sources") or "").strip()
    sources = parse_sources_param(sources_raw)

    legacy_source = (request.args.get("source") or "").strip()
    if legacy_source and not sources and legacy_source != "All":
        sources = [legacy_source]

    try:
        days = int(request.args.get("days") or 7)
    except Exception:
        days = 7

    try:
        min_sources = int(request.args.get("min_sources") or 1)
    except Exception:
        min_sources = 1

    sev_min = (request.args.get("sev_min") or "").strip()
    kev = (request.args.get("kev") or "").strip()
    has_iocs = (request.args.get("has_iocs") or "").strip()
    cat = (request.args.get("cat") or "").strip()

    seen = (request.args.get("seen") or "").strip()
    status = (request.args.get("status") or "").strip()
    stack = (request.args.get("stack") or "").strip()
    delta = (request.args.get("delta") or "").strip()

    days = days if days in (1, 7, 30) else 7
    min_sources = min_sources if min_sources in (1, 2, 3) else 1
    sort = sort if sort in ("newest", "oldest", "severity") else "newest"
    view = view if view in ("cards", "list") else "cards"
    sev_min = sev_min if sev_min in ("", "High", "Critical") else ""
    seen = seen if seen in ("", "hide", "only") else ""
    status = status if status in ([""] + STATUS_VALUES) else ""
    stack = stack if stack in ("", "1") else ""
    delta = delta if delta in ("", "1") else ""

    # ✅ If the user explicitly set a time range (7/30), delta must not keep forcing 24h.
    # This prevents "days dropdown does nothing" when delta=1 is still in the URL.
    if delta == "1" and "days" in request.args and days != 1:
        delta = ""

    actor = (request.args.get("actor") or "").strip()
    actor = actor[:40]  # safety cap



    categories = parse_csv_param(cat)

    q = q[:200]
    exclude = exclude[:300]

    return {
        "q": q,
        "sources": sources,
        "sort": sort,
        "days": days,
        "min_sources": min_sources,
        "exclude": exclude,
        "kw": kw,
        "view": view,
        "sev_min": sev_min,
        "kev": kev,
        "has_iocs": has_iocs,
        "cat": categories,
        "seen": seen,
        "status": status,
        "stack": stack,
        "delta": delta,
        "actor": actor,
        "mine": mine,
        "kpi": kpi,
    }



def clean_params(params: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k, v in params.items():
        if k not in ALLOWED_PARAMS:
            continue
        if v is None:
            continue
        if k in ("sources", "cat"):
            if isinstance(v, list) and v:
                out[k] = ",".join(v)
            continue
        if isinstance(v, str) and v.strip() == "":
            continue
        out[k] = v
    return out


def make_qs(params: Dict[str, Any], overrides: Optional[Dict[str, Any]] = None) -> str:
    merged = dict(params)
    if overrides:
        merged.update(overrides)
    merged = clean_params(merged)
    return urlencode(merged, doseq=True)


# =============================
# BUILD PIPELINE
# =============================
def build_stories_from_items(
    items: List[Dict[str, Any]],
    q: str,
    sources_filter: List[str],
    sort: str,
    days: int,
    min_sources: int,
    include_kw: str,
    exclude: str,
    sev_min: str,
    kev_only: bool,
    has_iocs_only: bool,
    categories: List[str],
) -> List[Dict[str, Any]]:
    cutoff = now_utc() - timedelta(days=days)

    items_time_filtered = []
    for it in items:
        dt = it.get("published_dt")
        if dt is None or dt >= cutoff:
            items_time_filtered.append(it)

    ql = (q or "").strip().lower()
    if ql:
        items_time_filtered = [
            it
            for it in items_time_filtered
            if ql in (it.get("title", "").lower() + " " + it.get("summary", "").lower())
        ]

    if sources_filter:
        src_set = set(sources_filter)
        items_time_filtered = [
            it for it in items_time_filtered if it.get("source") in src_set
        ]

    ex_terms = [t.strip().lower() for t in (exclude or "").split(",") if t.strip()]

    if ex_terms:

        def ok(it: Dict[str, Any]) -> bool:
            t = (it.get("title", "") + " " + it.get("summary", "")).lower()
            return not any(term in t for term in ex_terms)

        items_time_filtered = [it for it in items_time_filtered if ok(it)]

    stories = cluster_into_stories(items_time_filtered, STORY_SIMILARITY_THRESHOLD)

    if include_kw:
        inc = include_kw.strip().lower()
        stories = [
            s
            for s in stories
            if any(inc == k.lower() for k in s.get("matched_keywords", []))
        ]

    if min_sources > 1:
        stories = [s for s in stories if s.get("sources_count", 1) >= min_sources]

    if sev_min:
        min_rank = SEV_ORDER.get(sev_min, 0)
        stories = [
            s
            for s in stories
            if SEV_ORDER.get((s.get("severity") or {}).get("level", "Low"), 0) >= min_rank
        ]

    if kev_only:
        stories = [s for s in stories if bool(s.get("kev", False))]

    if has_iocs_only:
        stories = [
            s
            for s in stories
            if int((s.get("severity") or {}).get("ioc_count", 0) or 0) > 0
        ]

    if categories:
        want = set(categories)
        stories = [
            s for s in stories if want.intersection(set(s.get("categories") or []))
        ]

    if sort == "oldest":
        stories.sort(key=lambda s: s.get("published_dt") or datetime.min, reverse=False)
    elif sort == "severity":
        stories.sort(
            key=lambda s: (
                (s.get("severity") or {}).get("score", 0),
                s.get("published_dt") or datetime.min,
            ),
            reverse=True,
        )
    else:
        stories.sort(key=lambda s: s.get("published_dt") or datetime.min, reverse=True)

    return stories


def find_story(stories: List[Dict[str, Any]], story_id: str) -> Optional[Dict[str, Any]]:
    for s in stories:
        if s.get("story_id") == story_id:
            return s
    return None


def _delta_filter(stories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

    def updated_recent(s: Dict[str, Any]) -> bool:
        u = (s.get("updated_utc") or "").strip()
        if not u:
            return False
        dt = parse_dt(u)
        return bool(dt and dt >= cutoff)

    def published_recent(s: Dict[str, Any]) -> bool:
        dt = s.get("published_dt")
        return bool(dt and dt >= cutoff)

    return [s for s in stories if published_recent(s) or updated_recent(s)]


def _is_story_new_since(dt_start: datetime, story: Dict[str, Any]) -> bool:
    """
    A story is "new" if:
      - published_dt exists and >= window start
      - AND user has NOT reviewed it (seen=False)
    """
    try:
        pub: Optional[datetime] = story.get("published_dt")
        if not pub:
            return False
        if pub < dt_start:
            return False
        if bool(story.get("seen", False)):
            return False
        return True
    except Exception:
        return False


def build_for_request() -> Tuple[
    List[Dict[str, Any]],
    List[str],
    Dict[str, Any],
    List[str],
    Dict[str, int],
    List[Dict[str, Any]],
    List[str],
    List[str],
    str,
    Dict[str, List[str]],
    int,
    str,
    str,
]:
    params = get_params_dict()
    tenant_id = current_tenant_id()

    snap_items, snap_errors = feeds.get_snapshot_items()

    all_stories = build_stories_from_items(
        items=snap_items,
        q="",
        sources_filter=[],
        sort="newest",
        days=params["days"],
        min_sources=1,
        include_kw="",
        exclude="",
        sev_min="",
        kev_only=False,
        has_iocs_only=False,
        categories=[],
    )

    stories = build_stories_from_items(
        items=snap_items,
        q=params["q"],
        sources_filter=params["sources"],
        sort=params["sort"],
        days=params["days"],
        min_sources=params["min_sources"],
        include_kw=params["kw"],
        exclude=params["exclude"],
        sev_min=params["sev_min"],
        kev_only=(params["kev"] == "1"),
        has_iocs_only=(params["has_iocs"] == "1"),
        categories=params["cat"],
    )

    # ✅ Campaign upsert (best-effort; does not break feed if degraded)
    try:
        for s in all_stories:
            upsert_campaign_from_story(tenant_id=tenant_id, story=s)
    except Exception as ex:
        log.warning("campaign upsert degraded: %s", ex)

    uid = current_user_id()

    # Seen map for current view
    story_ids = [s["story_id"] for s in stories]
    seen_map = get_seen_map(story_ids, uid, tenant_id=tenant_id) if uid else {}

    for s in stories:
        s["seen"] = bool(seen_map.get(s["story_id"], False))
        s["last_seen_utc"] = ""
        if uid and s["seen"]:
            try:
                info = get_seen_info(s["story_id"], uid, tenant_id=tenant_id) or {}
                s["last_seen_utc"] = str(info.get("last_seen_utc") or "")
            except Exception:
                s["last_seen_utc"] = ""


    # Seen map for all stories (so "X new since ..." counts are global, not filter-only)
    all_ids = [s["story_id"] for s in all_stories]
    seen_map_all = get_seen_map(all_ids, uid, tenant_id=tenant_id) if uid else {}
    for s in all_stories:
        s["seen"] = bool(seen_map_all.get(s["story_id"], False))

    # Meta for current view
    meta_map = get_meta_map([s["story_id"] for s in stories], tenant_id=tenant_id)
    for s in stories:
        m = meta_map.get(s["story_id"], {})
        s["status"] = _sanitize_status(m.get("status", "New"))
        s["owner"] = m.get("owner", "")
        s["notes"] = m.get("notes", "")
        s["updated_utc"] = m.get("updated_utc", "")
        s["updated_by_email"] = m.get("updated_by_email", "")
        s["not_assessed"] = (
            s["status"] == "New"
            and not (s["owner"] or "").strip()
            and not (s["notes"] or "").strip()
        )

    if params["status"]:
        stories = [s for s in stories if s.get("status") == params["status"]]

    wl = load_watchlist()
    for s in stories:
        hits = watchlist_matches_for_story(s, wl)
        s["watchlist_matches"] = hits
        s["matches_stack"] = bool(hits)

    if params["stack"] == "1":
        stories = [s for s in stories if s.get("matches_stack")]

    if params["seen"] == "hide":
        stories = [s for s in stories if not s.get("seen")]
    elif params["seen"] == "only":
        stories = [s for s in stories if s.get("seen")]


    # ✅ Delta view is strictly "last 24h" and should not override explicit multi-day ranges.
    if params["delta"] == "1" and params["days"] == 1:
        stories = _delta_filter(stories)


    # =============================
    # ✅ NEW SINCE LAST LOGIN (per-user)
    # =============================
    new_since_dt, new_since_label = current_user_new_since_dt()
    new_since_utc = iso_utc_z(new_since_dt)

    # mark "is_new" on the currently displayed stories
    for s in stories:
        s["is_new"] = bool(uid) and _is_story_new_since(new_since_dt, s)

    # global count across all stories (within params["days"] window)
    new_count = 0
    if uid:
        for s in all_stories:
            # all_stories already got seen assigned above
            if _is_story_new_since(new_since_dt, s):
                new_count += 1

    # =============================
    # MEMORY write/read (existing)
    # =============================
    try:
        if os.getenv("MEMORY_WRITE", "1").strip() != "0":
            for s in all_stories:
                fp = (s.get("memory_fp") or "").strip()
                if fp:
                    record_story_fingerprint(
                        fp,
                        story_id=s.get("story_id", ""),
                        title_sample=s.get("title", ""),
                        tenant_id=tenant_id,
                    )
    except Exception as ex:
        log.warning("memory record degraded: %s", ex)

    fps = [
        str(s.get("memory_fp") or "")
        for s in stories
        if (s.get("memory_fp") or "").strip()
    ]
    try:
        mem_map = get_memory_map(fps, tenant_id=tenant_id) if fps else {}
    except Exception as ex:
        log.warning("memory read degraded: %s", ex)
        mem_map = {}

    for s in stories:
        fp = (s.get("memory_fp") or "").strip()
        mm = mem_map.get(fp, {}) if fp else {}
        s["seen_before_count"] = int(mm.get("seen_count", 0) or 0)
        s["seen_before_first_utc"] = str(mm.get("first_seen_utc", "") or "")
        s["seen_before"] = bool(s["seen_before_count"] >= 2)

    counts: Dict[str, int] = {"All": len(all_stories)}
    for src in [x["name"] for x in SOURCES]:
        counts[src] = sum(
            1
            for st in all_stories
            if any(a.get("source") == src for a in st["articles"])
        )

    source_names = ["All"] + [x["name"] for x in SOURCES]
    valid = set(source_names)
    params["sources"] = [s for s in params["sources"] if s in valid and s != "All"]

    kw_union = sorted({k for st in all_stories for k in st.get("matched_keywords", [])})
    cat_union = sorted({c for st in all_stories for c in (st.get("categories") or [])})

    health_rows = feeds.get_health_rows(human_dt)

    _kev_set, kev_err = get_kev_cves()
    kev_status = "OK" if not kev_err else "DEGRADED"

    try:
        ensure_daily_report_written(all_stories)
    except Exception as ex:
        log.warning("Daily report write error: %s", ex)

    errors = list(snap_errors)
    wl = load_watchlist()
    return (
        stories,
        errors,
        params,
        source_names,
        counts,
        health_rows,
        kw_union,
        cat_union,
        kev_status,
        wl,
        new_count,
        new_since_label,
        new_since_utc,
    )


# =============================
# REPORTS
# =============================
def ensure_reports_dir() -> None:
    os.makedirs(REPORT_DIR, exist_ok=True)


def write_daily_report(all_stories: List[Dict[str, Any]], report_date: str) -> str:
    ensure_reports_dir()
    tenant_id = current_tenant_id()

    ids = [s["story_id"] for s in all_stories]
    seen_map: Dict[str, bool] = {}  # daily report is cross-user

    meta_map = get_meta_map(ids, tenant_id=tenant_id)
    wl = load_watchlist()

    for s in all_stories:
        s["seen"] = bool(seen_map.get(s["story_id"], False))
        m = meta_map.get(s["story_id"], {})
        s["status"] = _sanitize_status(m.get("status", "New"))
        hits = watchlist_matches_for_story(s, wl)
        s["watchlist_matches"] = hits
        s["matches_stack"] = bool(hits)

    stories = sorted(
        all_stories,
        key=lambda s: (
            s.get("severity", {}).get("score", 0),
            s.get("published_dt") or datetime.min,
        ),
        reverse=True,
    )[:40]

    base_url = (os.environ.get("PUBLIC_BASE_URL") or "").rstrip("/")
    app_url = base_url if base_url else ""

    html = render_template_string(
        TEMPLATES["daily"],
        report_date=report_date,
        generated_utc=now_utc().strftime("%Y-%m-%d %H:%M UTC"),
        stories=stories,
        app_url=app_url,
        json_url=(app_url + "/daily.json") if app_url else "/daily.json",
    )

    daily_path = os.path.join(REPORT_DIR, f"{report_date}.html")
    latest_path = os.path.join(REPORT_DIR, "latest.html")

    with open(daily_path, "w", encoding="utf-8") as f:
        f.write(html)
    with open(latest_path, "w", encoding="utf-8") as f:
        f.write(html)

    return daily_path


def ensure_daily_report_written(all_stories: List[Dict[str, Any]]) -> None:
    report_date = today_utc_str()
    now_ts = time.time()
    last = _last_daily_write.get(report_date, 0)
    if now_ts - last < 300:
        return
    write_daily_report(all_stories, report_date)
    _last_daily_write[report_date] = now_ts


# =============================
# AUTH ROUTES
# =============================
@app.get("/login")
def login_get():
    if current_user_id():
        return redirect("/")
    next_url = (request.args.get("next") or "").strip()
    return render_template_string(
        TEMPLATES["login"], mode="login", error="", next_url=next_url, email=""
    )


@app.post("/logout")
def logout_post():
    # Optional CSRF check (recommended)
    expected = (session.get("csrf") or "").strip()
    sent = (request.form.get("csrf") or "").strip() or (request.headers.get("X-CSRF-Token") or "").strip()
    if expected and sent != expected:
        return Response("CSRF failed", status=403)


    session.clear()
    resp = redirect("/login")
    # Hard cache-bust just in case the browser caches redirects oddly
    resp.headers["Cache-Control"] = "no-store"
    return resp


@app.get("/logout")
def logout_get_fallback():
    return Response("Use POST /logout", status=405)




@app.post("/login")
def login_post():
    ip = _client_ip()

    email = (request.form.get("email") or "").strip().lower()
    password = (request.form.get("password") or "")
    next_url = (request.form.get("next") or "").strip()

    if not email or not password:
        audit_auth_event("login_attempt", ok=False, email=email, reason="missing_fields")
        return render_template_string(
            TEMPLATES["login"],
            mode="login",
            error="Invalid credentials.",
            next_url=next_url,
            email=email,
        )

    locked, retry_after = _check_lockout(ip, email)
    if locked:
        audit_auth_event(
            "login_attempt",
            ok=False,
            email=email,
            reason="rate_limited",
            extra={"retry_after_s": int(retry_after)},
        )
        return render_template_string(
            TEMPLATES["login"],
            mode="login",
            error="Too many attempts. Try again later.",
            next_url=next_url,
            email=email,
        )

    u = verify_user(email, password)

    if not u:
        now_locked, _ra, fail_count = _record_login_failure(ip, email)
        audit_auth_event(
            "login_attempt",
            ok=False,
            email=email,
            reason="invalid_or_disabled",
            extra={"fail_count_pair": int(fail_count), "locked": bool(now_locked)},
        )
        return render_template_string(
            TEMPLATES["login"],
            mode="login",
            error="Too many attempts. Try again later."
            if now_locked
            else "Invalid credentials or account disabled.",
            next_url=next_url,
            email=email,
        )

    _clear_login_failures(ip, email)

    session["uid"] = u["user_id"]
    session["email"] = u.get("email", "")

    # ✅ Store timestamps for "new since last login"
    session["last_login_utc"] = str(u.get("last_login_utc", "") or "")
    session["prev_login_utc"] = str(u.get("prev_login_utc", "") or "")

    _ensure_csrf_token()

    audit_auth_event(
        "login_success",
        ok=True,
        email=u.get("email", email),
        user_id=u.get("user_id", ""),
        reason="ok",
    )

    if next_url.startswith("/") and not next_url.startswith("//"):
        return redirect(next_url)
    return redirect("/")


@app.get("/signup")
def signup_get():
    if current_user_id():
        return redirect("/")
    if not SIGNUP_ENABLED:
        abort(404)
    return render_template_string(TEMPLATES["login"], mode="signup", error="", next_url="", email="")


@app.post("/signup")
def signup_post():
    if not SIGNUP_ENABLED:
        abort(404)

    email = (request.form.get("email") or "").strip().lower()
    password = (request.form.get("password") or "")

    if not email or "@" not in email:
        return render_template_string(
            TEMPLATES["login"],
            mode="signup",
            error="Please use a valid email address.",
            next_url="",
            email=email,
        )

    if len(password) < 10:
        return render_template_string(
            TEMPLATES["login"],
            mode="signup",
            error="Password must be at least 10 characters.",
            next_url="",
            email=email,
        )

    if get_user_by_email(email):
        return render_template_string(
            TEMPLATES["login"],
            mode="signup",
            error="An account with that email already exists.",
            next_url="",
            email=email,
        )

    default_role = (os.getenv("DEFAULT_SIGNUP_ROLE") or "analyst").strip().lower()
    user = create_user(email=email, password=password, role=default_role)

    session["uid"] = user["user_id"]
    session["email"] = email
    session["last_login_utc"] = ""
    session["prev_login_utc"] = ""
    _ensure_csrf_token()

    return redirect("/")


# =============================
# ROUTES
# =============================
@app.get("/")
def index():
    gate = enforce_login_if_configured()
    if gate:
        return gate

    (
        stories,
        errors,
        params,
        source_names,
        counts,
        _health_rows,
        _kw_union,
        cat_union,
        kev_status,
        _wl,
        new_count,
        new_since_label,
        new_since_utc,
    ) = build_for_request()
    tenant_id = current_tenant_id()
    uid = current_user_id()
    email = current_user_email()


    actor = (params.get("actor") or "").strip()

    if actor:
        stories = [s for s in stories if str(s.get("actor_id") or "") == actor]

    # ---- UI filter state (so dropdowns don't "reset") ----
    q = params.get("q") or ""
    sort = params.get("sort") or "newest"
    min_sources = int(params.get("min_sources") or 1)
    view = params.get("view") or "cards"
    status_filter = params.get("status") or ""
    sev_min = params.get("sev_min") or ""
    kev = params.get("kev") or ""
    has_iocs = params.get("has_iocs") or ""
    reviewed_filter = params.get("seen") or ""
    stack_filter = params.get("stack") or ""
    exclude = params.get("exclude") or ""
    include_kw = params.get("kw") or ""
    delta = params.get("delta") or ""
    selected_sources = list(params.get("sources") or [])
    selected_cats = list(params.get("cat") or [])



    def qs(overrides: Dict[str, Any]) -> str:
        return make_qs(params, overrides)

    def qs_toggle_source(src: str) -> str:
        selected = list(params["sources"])
        if src in selected:
            selected = [s for s in selected if s != src]
        else:
            selected.append(src)
        return make_qs(params, {"sources": selected})

    def qs_toggle_cat(cat: str) -> str:
        selected = list(params["cat"])
        if cat in selected:
            selected = [c for c in selected if c != cat]
        else:
            selected.append(cat)
        return make_qs(params, {"cat": selected})

    def qs_clear_all() -> str:
        return make_qs(
            params,
            {
                "q": "",
                "sources": [],
                "sev_min": "",
                "kev": "",
                "has_iocs": "",
                "cat": [],
                "seen": "",
                "status": "",
                "stack": "",
                "exclude": "",
                "kw": "",
                "min_sources": 1,
                "sort": "newest",
                "delta": "",
                "days": params["days"],
                "actor": "",

            },
        )

    active_filters: List[Dict[str, str]] = []
    if params["delta"] == "1":
        active_filters.append({"key": "delta", "value": "1", "label": "Delta view (last 24h)"})
    if params["q"]:
        active_filters.append({"key": "q", "value": params["q"], "label": f"Search: {params['q']}"})
    if params["exclude"]:
        active_filters.append({"key": "exclude", "value": params["exclude"], "label": f"Exclude: {params['exclude']}"})
    if params["sev_min"]:
        active_filters.append({"key": "sev_min", "value": params["sev_min"], "label": f"Severity: {params['sev_min']}+"})
    if params["kev"] == "1":
        active_filters.append({"key": "kev", "value": "1", "label": "KEV only"})
    if params["has_iocs"] == "1":
        active_filters.append({"key": "has_iocs", "value": "1", "label": "Has IOCs"})
    if params["status"]:
        active_filters.append({"key": "status", "value": params["status"], "label": f"Status: {params['status']}"})
    if params["stack"] == "1":
        active_filters.append({"key": "stack", "value": "1", "label": "Relevant to our environment"})
    if params["seen"] == "hide":
        active_filters.append({"key": "seen", "value": "hide", "label": "Hide reviewed"})
    if params["seen"] == "only":
        active_filters.append({"key": "seen", "value": "only", "label": "Reviewed only"})

    for s in params["sources"]:
        active_filters.append({"key": "sources", "value": s, "label": f"Source: {s}"})
    for c in params["cat"]:
        active_filters.append({"key": "cat", "value": c, "label": f"Category: {c}"})

    def _truthy(v) -> bool:
        return str(v or "").strip().lower() in {"1", "true", "yes", "y", "on"}

    def _sev_level(st) -> str:
        sev = (st.get("severity") or {}) if isinstance(st, dict) else getattr(st, "severity", {}) or {}
        lvl = (sev.get("level") or "Low")
        return str(lvl)

    def _ioc_count(st) -> int:
        sev = (st.get("severity") or {}) if isinstance(st, dict) else getattr(st, "severity", {}) or {}
        return int(sev.get("ioc_count") or 0)

    def _is_seen(st) -> bool:
        if isinstance(st, dict):
            return bool(st.get("seen"))
        return bool(getattr(st, "seen", False))

    def _matches_stack(st) -> bool:
        if isinstance(st, dict):
            return bool(st.get("matches_stack"))
        return bool(getattr(st, "matches_stack", False))

    def _is_kev(st) -> bool:
        if isinstance(st, dict):
            return bool(st.get("kev"))
        return bool(getattr(st, "kev", False))

    def _is_delta_new(st) -> bool:
        if isinstance(st, dict):
            return bool(st.get("delta_new"))
        return bool(getattr(st, "delta_new", False))

    base = list(stories)
   
    delta_new_count = int(new_count or 0)
    delta_since_label = str(new_since_label or "")


    filter_counts = {
        "total": len(base),
        "kev": sum(1 for s in base if _is_kev(s)),
        "has_iocs": sum(1 for s in base if _ioc_count(s) > 0),
        "high_plus": sum(1 for s in base if _sev_level(s) in {"High", "Critical"}),
        "critical": sum(1 for s in base if _sev_level(s) == "Critical"),
        "relevant": sum(1 for s in base if _matches_stack(s)),
        "reviewed_only": sum(1 for s in base if _is_seen(s)),
        "reviewed_hide": sum(1 for s in base if not _is_seen(s)),
    }

    # Delta count (keep simple for now)
    filter_counts["delta"] = int(delta_new_count or 0)

    user_kpis: Dict[str, Any] = {}
    if uid and email:
        now_dt = now_utc()
        cutoff_24h = iso_utc_z(now_dt - timedelta(hours=24))
        cutoff_7d = iso_utc_z(now_dt - timedelta(days=7))


        user_kpis = {
            "assigned_open": user_assigned_open_count(tenant_id=tenant_id, owner_email=email),
            "assigned_done": user_assigned_done_count(tenant_id=tenant_id, owner_email=email),
            "unreviewed_assigned": user_unreviewed_assigned_open_count(
                tenant_id=tenant_id, user_id=str(uid), owner_email=email
            ),
            "reviewed_total": user_reviewed_total(tenant_id=tenant_id, user_id=str(uid)),
            "reviewed_24h": user_reviewed_since(tenant_id=tenant_id, user_id=str(uid), cutoff_utc_iso=cutoff_24h),
            "reviewed_7d": user_reviewed_since(tenant_id=tenant_id, user_id=str(uid), cutoff_utc_iso=cutoff_7d),
        }

    # ===== Phase 2: user KPI drilldowns =====
    mine = bool(params.get("mine"))
    kpi = str(params.get("kpi") or "").strip()
    is_authed = bool(uid)

    if mine and is_authed:
        me = (email or "").strip().lower()
        stories = [st for st in stories if (st.get("owner", "") or "").strip().lower() == me]

    # Define "done" statuses conservatively; everything else counts as "open"
    

    _DONE = {s.strip().lower() for s in (DONE_STATUS_VALUES or [])}

    def _is_done(status: str) -> bool:
        return (status or "").strip().lower() in _DONE


    if is_authed and kpi:
        if kpi == "assigned_open":
            stories = [st for st in stories if not _is_done(st.get("status", ""))]

        elif kpi == "assigned_done":
            stories = [st for st in stories if _is_done(st.get("status", ""))]

        elif kpi == "unreviewed_assigned":
            stories = [
                st for st in stories
                if (not bool(st.get("seen", False)))
                and (not _is_done(st.get("status", "")))
            ]

        elif kpi == "reviewed_total":
            stories = [st for st in stories if bool(st.get("seen", False))]

        elif kpi == "reviewed_24h":
            cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
            out = []
            for st in stories:
                if not bool(st.get("seen", False)):
                    continue

                dt = parse_dt(str(st.get("last_seen_utc") or ""))
                if not dt:
                    continue

                # normalize dt to UTC-aware so comparisons are valid
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                else:
                    dt = dt.astimezone(timezone.utc)

                if dt >= cutoff:
                    out.append(st)

            stories = out







    return render_template_string(
        TEMPLATES["base"],
        items=stories,
        errors=errors,
        params=params,
                # --- core filter/UI state ---
        q=q,
        days=params["days"],
        sort=sort,
        min_sources=min_sources,
        view=view,
        status_filter=status_filter,

        sev_min=sev_min,
        kev=kev,
        has_iocs=has_iocs,
        reviewed_filter=reviewed_filter,
        stack_filter=stack_filter,
        exclude=exclude,
        include_kw=include_kw,
        delta=delta,

        selected_sources=selected_sources,
        selected_cats=selected_cats,

        # --- delta counters used by template badges/subline ---
        delta_new_count=delta_new_count,
        delta_since_label=delta_since_label,

        is_authed=bool(current_user_id()),
        source_names=source_names,
        source_counts=counts,
        counts=counts,
        cat_union=cat_union,
        kev_status=kev_status,
        qs=qs,
        qs_toggle_source=qs_toggle_source,
        qs_toggle_cat=qs_toggle_cat,
        qs_clear_all=qs_clear_all,
        active_filters=active_filters,
        filter_counts=filter_counts,
        new_count=new_count,
        new_since_label=new_since_label,
        new_since_utc=new_since_utc,
        current_user_email=current_user_email(),
        current_user_initials=current_user_email().split("@", 1)[0][:2].upper(),
        csrf_token=_ensure_csrf_token() if current_user_id() else "",
        can_mark_seen=has_perm("mark_seen"),
        can_case_edit=has_perm("case_edit"),
        can_view_admin=has_perm("view_admin"),
        rel_time=_rel_time_from_any,   # ✅ THIS FIX
        user_kpis=user_kpis,


    
    )

   


@app.get("/shortcuts")
def shortcuts():
    gate = enforce_login_if_configured()
    if gate:
        return gate
    return render_template_string(TEMPLATES["shortcuts"])


@app.get("/campaign/<campaign_id>")
def campaign_view(campaign_id: str):
    gate = enforce_login_if_configured()
    if gate:
        return gate

    tenant_id = current_tenant_id()
    campaign_id = (campaign_id or "").strip()[:40]
    if not campaign_id:
        abort(404)

    snap_items, _snap_err = _get_snapshot_items()
    all_stories = build_stories_from_items(
        items=snap_items,
        q="",
        sources_filter=[],
        sort="newest",
        days=30,
        min_sources=1,
        include_kw="",
        exclude="",
        sev_min="",
        kev_only=False,
        has_iocs_only=False,
        categories=[],
    )

    hits = [s for s in all_stories if (s.get("campaign_id") == campaign_id)]
    if not hits:
        abort(404)

    label = (hits[0].get("campaign_label") or "Campaign").strip()
    graph = build_campaign_graph(hits, label)

    return render_template_string(
    TEMPLATES["campaign"],
    campaign_id=campaign_id,
    tenant_id=tenant_id,
    campaign_label=label,
    stories=hits,
    graph=graph,
    rel_time=_rel_time_from_any,
    current_user_email=current_user_email(),
    csrf_token=_ensure_csrf_token() if current_user_id() else "",
)



@app.get("/story/<story_id>")
def story(story_id: str):
    gate = enforce_login_if_configured()
    if gate:
        return gate

    tenant_id = current_tenant_id()
    uid = current_user_id()
    email = current_user_email()

    # If authed, mark seen (best effort) and log lifecycle ONLY on first transition 0->1
    if uid and has_perm("mark_seen"):
        was_seen = False
        try:
            si0 = get_seen_info(story_id, uid, tenant_id=tenant_id)
            was_seen = bool(int(si0.get("seen_count", 0) or 0) > 0)
        except Exception:
            was_seen = False

        # Always keep seen_count/last_seen fresh for the user experience
        try:
            mark_seen(story_id, uid, tenant_id=tenant_id)
        except Exception:
            pass

        # Optional legacy hook (leave as-is if you still want it)
        try:
            _record_seen_event(
                story_id=story_id,
                user_id=str(uid),
                email=email,
                tenant_id=tenant_id,
            )
        except Exception:
            pass


        # Only log the FIRST open for this user/story to avoid refresh spam
        if not was_seen:
            try:
                _log_story_lifecycle_event(
                    tenant_id=tenant_id,
                    story_id=story_id,
                    actor_user_id=str(uid),
                    actor_email=email,
                    event_type="reviewed_open",
                    field="seen",
                    old_value="Not reviewed",
                    new_value="Reviewed",
                    meta={"path": "/story/<id>"},
                )
            except Exception:
                pass




    (
        stories,
        _errors,
        params,
        _source_names,
        _counts,
        _health_rows,
        _kw_union,
        _cat_union,
        _kev_status,
        wl,
        _new_count,
        _new_since_label,
        _new_since_utc,
    ) = build_for_request()

    st = find_story(stories, story_id)
    if not st:
        snap_items, _snap_err = _get_snapshot_items()
        all_stories = build_stories_from_items(
            items=snap_items,
            q="",
            sources_filter=[],
            sort="newest",
            days=params["days"],
            min_sources=1,
            include_kw="",
            exclude="",
            sev_min="",
            kev_only=False,
            has_iocs_only=False,
            categories=[],
        )
        st = find_story(all_stories, story_id)
        if not st:
            abort(404)

        meta_map = get_meta_map([story_id], tenant_id=tenant_id)
        m = meta_map.get(story_id, {})
        st["status"] = _sanitize_status(m.get("status", "New"))
        st["owner"] = m.get("owner", "")
        st["notes"] = m.get("notes", "")
        st["updated_utc"] = m.get("updated_utc", "")
        st["updated_by_email"] = m.get("updated_by_email", "")
        hits = watchlist_matches_for_story(st, wl)
        st["watchlist_matches"] = hits
        st["matches_stack"] = bool(hits)

    if not st.get("campaign_id"):
        st["campaign_id"] = compute_campaign_id(st)
    if not st.get("campaign_label"):
        st["campaign_label"] = compute_campaign_label(st)


    if uid and has_perm("mark_seen"):
        # Only write campaign "reviewed_open" on first open to avoid refresh spam
        if not locals().get("was_seen", False):
            try:
                record_campaign_event(
                    tenant_id=tenant_id,
                    campaign_id=str(st.get("campaign_id") or ""),
                    story_id=story_id,
                    actor_user_id=str(uid),
                    actor_email=email,
                    event="reviewed_open",
                    meta={"path": "/story/<id>"},
                )
            except Exception:
                pass


    if uid:
        si = get_seen_info(story_id, uid, tenant_id=tenant_id)
        st["seen"] = True
        st["first_seen_utc"] = si.get("first_seen_utc", "")
        st["last_seen_utc"] = si.get("last_seen_utc", "")
        st["seen_count"] = si.get("seen_count", 0)
    else:
        st["seen"] = False
        st["first_seen_utc"] = ""
        st["last_seen_utc"] = ""
        st["seen_count"] = 0

    try:
        enrich_story_cves(st)
    except Exception as ex:
        st["cve_enrichment"] = {
            "cves": [],
            "cvss_max": None,
            "epss_max": None,
            "errors": [str(ex)],
        }

    def qs(overrides: Dict[str, Any]) -> str:
        return make_qs(params, overrides)

    # Pull lifecycle events (append-only timeline)
    try:
        lifecycle = get_story_lifecycle_events(tenant_id=tenant_id, story_id=story_id, limit=120)
    except Exception:
        lifecycle = []



    html = render_template_string(
        TEMPLATES["story"],
        story=st,
        qs=qs,
        status_values=STATUS_VALUES,
        rel_time=_rel_time_from_any,
        current_user_email=email,
        can_case_edit=has_perm("case_edit"),
        can_view_admin=has_perm("view_admin"),
        csrf_token=_ensure_csrf_token() if current_user_id() else "",
        lifecycle=lifecycle,  # ✅ render lifecycle natively in template
    )

    return html


# =============================
# API (RBAC-enforced writes) + AUDIT
# =============================
def _record_seen_event(*, story_id: str, user_id: str, email: str, tenant_id: str) -> None:
    ensure_admin_tables()

    conn = _db_conn()
    try:
        cur = conn.execute("PRAGMA table_info(story_seen_events)")
        cols = [str(r[1]) for r in cur.fetchall()]
        colset = set(cols)

        ts = datetime.utcnow().isoformat(timespec="seconds") + "Z"

        if "user_email" in colset:
            email_col = "user_email"
        elif "email" in colset:
            email_col = "email"
        else:
            email_col = None

        fields: List[str] = []
        values: List[Any] = []

        if "ts_utc" in colset:
            fields.append("ts_utc")
            values.append(ts)

        if "tenant_id" in colset:
            fields.append("tenant_id")
            values.append((tenant_id or "")[:80])

        if "story_id" in colset:
            fields.append("story_id")
            values.append((story_id or "")[:120])

        if "user_id" in colset:
            fields.append("user_id")
            values.append((user_id or "")[:80])

        if email_col:
            fields.append(email_col)
            values.append((email or "")[:254])

        if not fields:
            return

        placeholders = ",".join(["?"] * len(fields))
        sql = f"INSERT INTO story_seen_events({','.join(fields)}) VALUES({placeholders})"
        conn.execute(sql, tuple(values))
        conn.commit()
    finally:
        conn.close()


@app.post("/api/seen/toggle")
@require_perm("mark_seen")
def api_seen_toggle():
    tenant_id = current_tenant_id()
    uid = current_user_id()
    assert uid is not None
    email = current_user_email()

    data = request.get_json(silent=True) or {}
    story_id = str(data.get("story_id") or "").strip()
    if not story_id:
        return Response(
            json.dumps({"ok": False, "error": "missing story_id"}),
            status=400,
            mimetype="application/json",
        )

    new_state = toggle_seen(story_id, uid, tenant_id=tenant_id)

    # Lifecycle (append-only)
    try:
        _log_story_lifecycle_event(
            tenant_id=tenant_id,
            story_id=story_id,
            actor_user_id=str(uid),
            actor_email=email,
            event_type="reviewed_toggle",
            field="seen",
            old_value=("0" if bool(new_state) else "1"),
            new_value=("1" if bool(new_state) else "0"),
            meta={},
        )
    except Exception:
        pass

    if bool(new_state):
        try:
            _record_seen_event(story_id=story_id, user_id=uid, email=email, tenant_id=tenant_id)
        except Exception:
            pass

        try:
            snap_items, _ = _get_snapshot_items()
            all_stories = build_stories_from_items(
                items=snap_items,
                q="",
                sources_filter=[],
                sort="newest",
                days=30,
                min_sources=1,
                include_kw="",
                exclude="",
                sev_min="",
                kev_only=False,
                has_iocs_only=False,
                categories=[],
            )
            st = find_story(all_stories, story_id)
            if st:
                record_campaign_event(
                    tenant_id=tenant_id,
                    campaign_id=str(st.get("campaign_id") or ""),
                    story_id=story_id,
                    actor_user_id=str(uid),
                    actor_email=email,
                    event="reviewed_toggle",
                    meta={"seen": True},
                )
        except Exception:
            pass

    try:
        write_audit_event(
            event="seen_toggle",
            ok=True,
            actor_user_id=uid,
            actor_email=email,
            ip=_client_ip(),
            user_agent=_user_agent(),
            target_type="story",
            target_id=story_id,
            meta={"tenant_id": tenant_id, "seen": bool(new_state)},
        )
    except Exception:
        pass

    return Response(json.dumps({"ok": True, "seen": new_state}), mimetype="application/json")


@app.post("/api/meta/set")
@require_perm("case_edit")
def api_meta_set():
    tenant_id = current_tenant_id()
    uid = current_user_id()
    assert uid is not None
    email = current_user_email()

    data = request.get_json(silent=True) or {}
    story_id = str(data.get("story_id") or "").strip()
    if not story_id:
        return Response(
            json.dumps({"ok": False, "error": "missing story_id"}),
            status=400,
            mimetype="application/json",
        )

    status = str(data.get("status") or "").strip()
    owner = str(data.get("owner") or "").strip()
    notes = str(data.get("notes") or "").strip()

   
    # Capture old meta for lifecycle diffs
    old_status = "New"
    old_owner = ""
    old_notes = ""

    try:
        meta_map0 = get_meta_map([story_id], tenant_id=tenant_id)
        cur0 = meta_map0.get(story_id, {}) or {}
        old_status = _sanitize_status(cur0.get("status", "New"))
        old_owner = str(cur0.get("owner", "") or "")
        old_notes = str(cur0.get("notes", "") or "")
    except Exception:
        cur0 = {}

    # Fallback: if meta_map didn't return notes, pull from meta history.
    # This makes "From: testing 123 -> trail 2" work even when meta_map is flaky.
    if not old_notes:
        try:
            hist = get_meta_history(story_id, tenant_id=tenant_id, limit=50) or []
            for ev in hist:
                if isinstance(ev, dict):
                    n = str(ev.get("notes") or "").strip()
                    if n:
                        old_notes = n
                        break
        except Exception:
            pass









    rec = upsert_story_meta(
        story_id,
        status=status,
        owner=owner,
        notes=notes,
        actor_user_id=uid,
        actor_email=email,
        ip=_client_ip(),
        user_agent=_user_agent(),
        tenant_id=tenant_id,
    )

    # Lifecycle logging (field-level diffs)
    try:
        new_status = _sanitize_status((rec or {}).get("status", status) or "New")
        new_owner = str((rec or {}).get("owner", owner) or "")
        new_notes = str((rec or {}).get("notes", notes) or "")

        if str(old_status) != str(new_status):
            _log_story_lifecycle_event(
                tenant_id=tenant_id,
                story_id=story_id,
                actor_user_id=str(uid),
                actor_email=email,
                event_type="status_changed",
                field="status",
                old_value=str(old_status),
                new_value=str(new_status),
                meta={},
            )

        if str(old_owner) != str(new_owner):
            _log_story_lifecycle_event(
                tenant_id=tenant_id,
                story_id=story_id,
                actor_user_id=str(uid),
                actor_email=email,
                event_type="owner_changed",
                field="owner",
                old_value=str(old_owner),
                new_value=str(new_owner),
                meta={},
            )


        if str(old_notes) != str(new_notes):
            _log_story_lifecycle_event(
                tenant_id=tenant_id,
                story_id=story_id,
                actor_user_id=str(uid),
                actor_email=email,
                event_type="notes_updated",
                field="notes",
                old_value=str(old_notes),
                new_value=str(new_notes),
                meta={"notes_len": int(len(new_notes or ""))},
            )



    except Exception:
        pass

    try:
        write_audit_event(
            event="meta_set",
            ok=True,
            actor_user_id=uid,
            actor_email=email,
            ip=_client_ip(),
            user_agent=_user_agent(),
            target_type="story",
            target_id=story_id,
            meta={
                "tenant_id": tenant_id,
                "status": status,
                "owner": owner,
                "notes_len": len(notes or ""),
            },
        )
    except Exception:
        pass

    return Response(json.dumps({"ok": True, "meta": rec}, indent=2), mimetype="application/json")


@app.post("/api/meta/assign_to_me")
@require_perm("case_edit")
def api_assign_to_me():
    tenant_id = current_tenant_id()
    uid = current_user_id()
    assert uid is not None
    email = current_user_email()

    data = request.get_json(silent=True) or {}
    story_id = str(data.get("story_id") or "").strip()
    if not story_id:
        return Response(
            json.dumps({"ok": False, "error": "missing story_id"}),
            status=400,
            mimetype="application/json",
        )

    meta_map = get_meta_map([story_id], tenant_id=tenant_id)
    cur = meta_map.get(story_id, {})
    old_owner = str(cur.get("owner", "") or "")
    status = _sanitize_status(cur.get("status", "New"))
    notes = str(cur.get("notes", "") or "")

    rec = upsert_story_meta(
        story_id,
        status=status,
        owner=email,
        notes=notes,
        actor_user_id=uid,
        actor_email=email,
        ip=_client_ip(),
        user_agent=_user_agent(),
        tenant_id=tenant_id,
    )

    # Lifecycle logging
    try:
        _log_story_lifecycle_event(
            tenant_id=tenant_id,
            story_id=story_id,
            actor_user_id=str(uid),
            actor_email=email,
            event_type="assigned_to_me",
            field="owner",
            old_value=str(old_owner),
            new_value=str(email),
            meta={},
        )
    except Exception:
        pass

    try:
        write_audit_event(
            event="assign_to_me",
            ok=True,
            actor_user_id=uid,
            actor_email=email,
            ip=_client_ip(),
            user_agent=_user_agent(),
            target_type="story",
            target_id=story_id,
            meta={"tenant_id": tenant_id},
        )
    except Exception:
        pass

    return Response(json.dumps({"ok": True, "meta": rec}, indent=2), mimetype="application/json")


@app.get("/api/meta/history")
def api_meta_history():
    auth = require_auth_or_401()
    if auth:
        return auth

    tenant_id = current_tenant_id()
    story_id = (request.args.get("story_id") or "").strip()
    if not story_id:
        return Response(
            json.dumps({"ok": False, "error": "missing story_id"}),
            status=400,
            mimetype="application/json",
        )

    try:
        limit = int(request.args.get("limit") or 50)
    except Exception:
        limit = 50

    rows = get_meta_history(story_id, tenant_id=tenant_id, limit=limit)
    return Response(
        json.dumps({"ok": True, "story_id": story_id, "events": rows}, indent=2),
        mimetype="application/json",
    )


@app.get("/api/story/lifecycle")
def api_story_lifecycle():
    auth = require_auth_or_401()
    if auth:
        return auth

    tenant_id = current_tenant_id()
    story_id = (request.args.get("story_id") or "").strip()
    if not story_id:
        return Response(
            json.dumps({"ok": False, "error": "missing story_id"}),
            status=400,
            mimetype="application/json",
        )

    try:
        limit = int(request.args.get("limit") or 120)
    except Exception:
        limit = 120

    events = get_story_lifecycle_events(tenant_id=tenant_id, story_id=story_id, limit=limit)
    return Response(
        json.dumps({"ok": True, "story_id": story_id, "events": events}, indent=2, default=str),
        mimetype="application/json",
    )


# =============================
# REPORTS / EXPORTS (RBAC)
# =============================
@app.get("/daily")
@require_perm("export_reports")
def daily_latest():
    ensure_reports_dir()
    latest_path = os.path.join(REPORT_DIR, "latest.html")
    if not os.path.exists(latest_path):
        snap_items, _snap_err = _get_snapshot_items()
        all_stories = build_stories_from_items(
            items=snap_items,
            q="",
            sources_filter=[],
            sort="newest",
            days=1,
            min_sources=1,
            include_kw="",
            exclude="",
            sev_min="",
            kev_only=False,
            has_iocs_only=False,
            categories=[],
        )
        write_daily_report(all_stories, today_utc_str())
    return send_file(latest_path, mimetype="text/html")


@app.get("/daily/<report_date>")
@require_perm("export_reports")
def daily_by_date(report_date: str):
    try:
        datetime.strptime(report_date, "%Y-%m-%d")
    except Exception:
        abort(400)

    ensure_reports_dir()
    path = os.path.join(REPORT_DIR, f"{report_date}.html")
    if not os.path.exists(path):
        abort(404)
    return send_file(path, mimetype="text/html")


@app.get("/daily.json")
@require_perm("export_reports")
def daily_json():
    tenant_id = current_tenant_id()

    snap_items, _snap_err = _get_snapshot_items()
    stories = build_stories_from_items(
        items=snap_items,
        q="",
        sources_filter=[],
        sort="severity",
        days=1,
        min_sources=1,
        include_kw="",
        exclude="",
        sev_min="",
        kev_only=False,
        has_iocs_only=False,
        categories=[],
    )

    ids = [s["story_id"] for s in stories]
    meta_map = get_meta_map(ids, tenant_id=tenant_id)
    wl = load_watchlist()

    for s in stories:
        m = meta_map.get(s["story_id"], {})
        s["status"] = _sanitize_status(m.get("status", "New"))
        s["owner"] = m.get("owner", "")
        s["notes"] = m.get("notes", "")
        s["updated_utc"] = m.get("updated_utc", "")
        s["updated_by_email"] = m.get("updated_by_email", "")
        hits = watchlist_matches_for_story(s, wl)
        s["watchlist_matches"] = hits
        s["matches_stack"] = bool(hits)

        try:
            enrich_story_cves(s)
            if s.get("cve_enrichment"):
                for row in s["cve_enrichment"].get("cves", []):
                    row["references"] = (row.get("references") or [])[:0]
        except Exception:
            s["cve_enrichment"] = {
                "cves": [],
                "cvss_max": None,
                "epss_max": None,
                "errors": ["enrichment failed"],
            }

    payload = {
        "generated_utc": now_utc().isoformat(),
        "report_date": today_utc_str(),
        "count": len(stories),
        "top": stories[:50],
    }
    return Response(json.dumps(payload, indent=2, default=str), mimetype="application/json")


@app.get("/export.csv")
@require_perm("export_reports")
def export_csv():
    tenant_id = current_tenant_id()
    params = get_params_dict()

    snap_items, _snap_err = _get_snapshot_items()
    stories = build_stories_from_items(
        items=snap_items,
        q=params["q"],
        sources_filter=params["sources"],
        sort=params["sort"],
        days=params["days"],
        min_sources=params["min_sources"],
        include_kw=params["kw"],
        exclude=params["exclude"],
        sev_min=params["sev_min"],
        kev_only=(params["kev"] == "1"),
        has_iocs_only=(params["has_iocs"] == "1"),
        categories=params["cat"],
    )

    meta_map = get_meta_map([s["story_id"] for s in stories], tenant_id=tenant_id)
    wl = load_watchlist()

    for s in stories:
        m = meta_map.get(s["story_id"], {})
        s["status"] = _sanitize_status(m.get("status", "New"))
        s["owner"] = m.get("owner", "")
        s["notes"] = m.get("notes", "")
        s["updated_utc"] = m.get("updated_utc", "")
        s["updated_by_email"] = m.get("updated_by_email", "")
        hits = watchlist_matches_for_story(s, wl)
        s["watchlist_matches"] = hits
        s["matches_stack"] = bool(hits)

        try:
            enrich_story_cves(s)
        except Exception:
            s["cve_enrichment"] = {
                "cves": [],
                "cvss_max": None,
                "epss_max": None,
                "errors": ["enrichment failed"],
            }

    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(
        [
            "story_id",
            "campaign_id",
            "campaign_label",
            "status",
            "owner",
            "updated_utc",
            "updated_by",
            "matches_stack",
            "watchlist_matches",
            "severity",
            "severity_score",
            "kev",
            "trust",
            "categories",
            "title",
            "sources_count",
            "published",
            "cves",
            "ioc_count",
            "cvss_max",
            "epss_max_percent",
            "newest_link",
        ]
    )

    for st in stories:
        sev = (st.get("severity") or {})
        enr = st.get("cve_enrichment") or {}
        cvss_max = enr.get("cvss_max")
        epss_max = enr.get("epss_max")
        w.writerow(
            [
                st.get("story_id", ""),
                st.get("campaign_id", ""),
                st.get("campaign_label", ""),
                st.get("status", "New"),
                st.get("owner", ""),
                st.get("updated_utc", ""),
                st.get("updated_by_email", ""),
                "1" if st.get("matches_stack") else "0",
                " | ".join(st.get("watchlist_matches") or []),
                sev.get("level", ""),
                sev.get("score", 0),
                "1" if st.get("kev") else "0",
                st.get("trust", ""),
                " | ".join(st.get("categories") or []),
                st.get("title", ""),
                st.get("sources_count", 0),
                (st.get("published", "")[:19].replace("T", " ") + " UTC")
                if st.get("published")
                else "",
                " ".join(st.get("indicators", {}).get("cves", [])),
                sev.get("ioc_count", 0),
                (f"{float(cvss_max):.1f}" if cvss_max is not None else ""),
                (f"{float(epss_max) * 100:.2f}" if epss_max is not None else ""),
                (st.get("articles", [{}])[0].get("link", "") if st.get("articles") else ""),
            ]
        )

    return Response(
        out.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=threatly_export.csv"},
    )


@app.get("/health")
def health():
    gate = enforce_login_if_configured()
    if gate:
        return gate

    rows = feeds.get_health_rows(human_dt) or []
    normalized: List[Dict[str, Any]] = []
    for r in rows:
        if isinstance(r, dict):
            source = (r.get("source") or r.get("name") or r.get("source_name") or "").strip()
            last_fetch_utc = (r.get("last_fetch_utc") or r.get("last_fetch") or r.get("fetched_utc") or "").strip()
            last_fetch_human = (r.get("last_fetch_human") or r.get("last_fetch_human_str") or r.get("fetched_human") or "").strip()
            status = (r.get("status") or "").strip().upper() or "UNKNOWN"
            error = (r.get("error") or r.get("detail") or r.get("err") or r.get("last_error") or "").strip()
        else:
            source = (getattr(r, "source", "") or getattr(r, "name", "") or "").strip()
            last_fetch_utc = (getattr(r, "last_fetch_utc", "") or getattr(r, "last_fetch", "") or "").strip()
            last_fetch_human = (getattr(r, "last_fetch_human", "") or getattr(r, "fetched_human", "") or "").strip()
            status = (getattr(r, "status", "") or "").strip().upper() or "UNKNOWN"
            error = (getattr(r, "error", "") or getattr(r, "detail", "") or "").strip()

        normalized.append(
            {
                "source": source,
                "last_fetch_utc": last_fetch_utc,
                "last_fetch_human": last_fetch_human,
                "status": status,
                "error": error,
            }
        )

    params = get_params_dict()

    def qs(overrides: Dict[str, Any]) -> str:
        return make_qs(params, overrides)

    return render_template_string(
        TEMPLATES["health"],
        health_rows=normalized,
        refreshed_utc=now_utc().strftime("%Y-%m-%d %H:%M UTC"),
        qs=qs,
    )


# =============================
# BOOT
# =============================
init_state_db()
ensure_users_table()
ensure_watchlist_file()
bootstrap_first_admin_if_empty()
ensure_admin_tables()

# ✅ Campaign tables
try:
    ensure_campaign_tables()
except Exception as ex:
    log.warning("Campaign tables degraded: %s", ex)

# ✅ Lifecycle tables (Feature 3)
try:
    ensure_story_lifecycle_tables()
except Exception as ex:
    log.warning("Lifecycle tables degraded: %s", ex)

try:
    feeds.refresh_snapshot_if_stale(force=True)
except Exception as ex:
    log.warning("Initial snapshot refresh failed: %s", ex)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "7860"))
    app.run(host="0.0.0.0", port=port, debug=False)
