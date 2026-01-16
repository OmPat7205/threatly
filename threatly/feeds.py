# threatly/feeds.py
from __future__ import annotations

import time
import threading
import logging
import re
import hashlib
from collections import Counter
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote


import feedparser
import requests

from threatly.config import (
    KEYWORDS,
    SOURCES,
    MAX_ITEMS_PER_SOURCE,
    CACHE_TTL_SECONDS,
    MAX_FEED_BYTES,
    REQUEST_TIMEOUT_SECONDS,
    REFRESH_TTL_SECONDS,
    SNAPSHOT_MAX_DAYS,
)
from threatly.utils import (
    now_utc,
    keyword_hits,
    canonicalize_url,
    pick_thumbnail,
    strip_html,
    parse_dt,
)

log = logging.getLogger("threatly")


# ============================================================
# THREAT ACTOR PROFILING (single source of truth)
# ============================================================
# This is NOT true attribution. It's deterministic clustering to group related stories.
_STOP = {
    "the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "with", "at", "by", "from",
    "is", "are", "was", "were", "be", "been", "as", "that", "this", "it", "its", "their",
    "into", "over", "via", "per", "new", "more", "less", "after", "before", "than",
    # common security boilerplate words (kept conservative)
    "security", "research", "report", "blog", "update", "advisory", "analysis", "alerts",
    "vulnerability", "vulnerabilities", "patch", "patched", "mitigation", "mitigations",
}


def _actor_tokens(text: str) -> List[str]:
    text = (text or "").lower()
    text = re.sub(r"[^a-z0-9\s\-_/\.]", " ", text)
    parts = [p for p in text.split() if p and p not in _STOP and len(p) > 2]
    return parts[:600]


def derive_actor_label_and_id(title: str, summary_full: str) -> Tuple[str, str]:
    """
    Deterministic clustering ID/label from title+full text.
    Great for grouping "campaign-shaped" story clusters.
    """
    blob = f"{title or ''}\n{summary_full or ''}".strip()
    if not blob:
        return ("Unattributed Cluster", "unattributed")

    toks = _actor_tokens(blob)
    top = [w for w, _ in Counter(toks).most_common(10)]

    # Stable-ish key: top tokens; fallback to hash of blob
    key = "|".join(top[:10]) if top else hashlib.sha1(blob.encode("utf-8", errors="ignore")).hexdigest()

    actor_id = hashlib.sha1(key.encode("utf-8", errors="ignore")).hexdigest()[:12]
    actor_label = " / ".join(top[:3]) if top else "Unattributed Cluster"
    return actor_label, actor_id


# ============================================================
# HEALTH MODEL (single source of truth)
# ============================================================
_FEED_HEALTH: Dict[str, Dict[str, Any]] = {}  # source_name -> record


def _now_utc_iso() -> str:
    return datetime.utcnow().isoformat()


def _touch_health(
    source_name: str,
    *,
    status: str,
    items: int = 0,
    error: str = "",
    last_fetch_utc: Optional[str] = None,
) -> None:
    """
    Update health for a source. last_fetch_utc should be set when an actual HTTP fetch occurs.
    """
    prev = _FEED_HEALTH.get(source_name, {})
    rec = dict(prev)

    rec["source"] = source_name
    rec["name"] = source_name  # compatibility
    rec["status"] = status
    rec["items"] = int(items or 0)
    rec["error"] = (error or "")[:800]
    rec["detail"] = rec["error"]  # compatibility

    # last_fetch_utc: only overwrite when a real fetch occurred
    if last_fetch_utc:
        rec["last_fetch_utc"] = last_fetch_utc
    else:
        rec.setdefault("last_fetch_utc", "")

    # updated_utc: "last time we updated health record" (can be cache hit too)
    rec["updated_utc"] = _now_utc_iso()

    _FEED_HEALTH[source_name] = rec


def _iso_to_dt(iso_str: str) -> Optional[datetime]:
    if not iso_str:
        return None
    try:
        return datetime.fromisoformat(iso_str)
    except Exception:
        return None


# =============================
# GLOBAL IN-MEMORY CACHE / SNAPSHOT
# =============================
_feed_cache: Dict[str, Dict[str, Any]] = {}   # rss_url -> {ts, items}

_snapshot_lock = threading.Lock()
_snapshot: Dict[str, Any] = {
    "ts": 0.0,
    "items": [],    # keyword-matched, time-trimmed feed items (articles)
    "errors": [],   # fetch errors
}


# =============================
# TEXT NORMALIZATION (enterprise-friendly summaries)
# =============================
_RE_WS = re.compile(r"\s+")
_RE_HARD_BREAKS = re.compile(r"(?:\r\n|\r|\n){2,}")
_RE_URL = re.compile(r"https?://\S+", re.IGNORECASE)

_BOILERPLATE_PREFIXES = (
    "view csaf",
    "view cve",
    "legal notice",
    "terms of use",
    "privacy policy",
    "recommended practices",
    "revision history",
    "initial release date",
)

_BOILERPLATE_MARKERS = (
    "cisa legal notice",
    "this product is provided subject to",
    "for more information, contact",
    "terms of use",
    "privacy policy",
    "revision history",
)


def _clean_text(s: str) -> str:
    """Strip HTML already done upstream; this just normalizes whitespace safely."""
    if not s:
        return ""
    s2 = s.replace("\u00a0", " ")
    s2 = _RE_WS.sub(" ", s2).strip()
    return s2


def _split_paragraphs(s: str) -> List[str]:
    if not s:
        return []
    raw = s.strip()
    parts = [p.strip() for p in _RE_HARD_BREAKS.split(raw) if p.strip()]
    return parts if parts else [raw]


def _strip_leading_boilerplate(paras: List[str]) -> List[str]:
    if not paras:
        return paras
    first = paras[0].lower().strip()
    for pref in _BOILERPLATE_PREFIXES:
        if first.startswith(pref):
            return paras[1:]
    return paras


def _truncate(s: str, max_chars: int) -> str:
    s = (s or "").strip()
    if len(s) <= max_chars:
        return s
    cut = s[:max_chars].rstrip()
    for sep in (". ", "; ", " — ", " - ", ", "):
        idx = cut.rfind(sep)
        if idx >= int(max_chars * 0.65):
            cut = cut[:idx].rstrip()
            break
    return cut.rstrip(" ,;-—") + "…"


def _smart_summary(full_text: str, *, max_chars: int = 520) -> str:
    """
    Enterprise summary policy:
    - Prefer the first “real” paragraph (after boilerplate)
    - If it’s still huge, truncate hard
    - If it’s basically all URLs/metadata, fallback to cleaned version
    """
    ft = (full_text or "").strip()
    if not ft:
        return ""

    paras = _strip_leading_boilerplate(_split_paragraphs(ft))

    pick = ""
    for p in paras[:5]:
        p_clean = _clean_text(p)
        if not p_clean:
            continue
        url_count = len(_RE_URL.findall(p_clean))
        if url_count >= 3 and len(p_clean) < 220:
            continue
        pick = p_clean
        break

    if not pick:
        pick = _clean_text(paras[0] if paras else ft)

    low = pick.lower()
    for m in _BOILERPLATE_MARKERS:
        idx = low.find(m)
        if idx != -1 and idx > 60:
            pick = pick[:idx].strip()
            break

    return _truncate(pick, max_chars=max_chars)


# =============================
# CACHE
# =============================
def _cache_get(url: str) -> Optional[List[Dict[str, Any]]]:
    entry = _feed_cache.get(url)
    if not entry:
        return None
    if time.time() - float(entry.get("ts", 0.0)) > CACHE_TTL_SECONDS:
        return None
    return entry.get("items")  # type: ignore


def _cache_set(url: str, items: List[Dict[str, Any]]) -> None:
    _feed_cache[url] = {"ts": time.time(), "items": items}


# =============================
# FEED FETCH
# =============================
def fetch_feed(source: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Fetch a single RSS feed. Uses in-memory caching.
    Updates health status and last_fetch time when a real HTTP fetch happens.

    Enterprise behavior:
      - Store both summary (short) and summary_full (full cleaned text)
      - UI uses summary; matching/IOCs can use summary_full
    """
    name = source["name"]
    url = source["rss"]

    cached = _cache_get(url)
    if cached is not None:
        _touch_health(name, status="OK", items=len(cached), error="")
        return cached

    headers = {
        "User-Agent": "Threatly/FeedFetch",
        "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.8",
    }

    fetch_iso = _now_utc_iso()
    try:
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
        resp.raise_for_status()

        content = resp.content
        if len(content) > MAX_FEED_BYTES:
            raise RuntimeError(f"Feed too large ({len(content)} bytes)")

        feed = feedparser.parse(content)
        if getattr(feed, "bozo", 0):
            log.debug("[%s] bozo_exception: %s", name, getattr(feed, "bozo_exception", None))

        items: List[Dict[str, Any]] = []
        for e in (feed.entries or [])[:MAX_ITEMS_PER_SOURCE]:
            title = (e.get("title") or "").strip()
            link = canonicalize_url((e.get("link") or "").strip())

            full_raw = strip_html(e.get("summary") or e.get("description") or "")
            summary_full = _clean_text(full_raw)
            summary = _smart_summary(summary_full, max_chars=520)

            published_dt = parse_dt(e)
            published = published_dt.isoformat() if published_dt else ""
            thumb = pick_thumbnail(e)

            actor_label, actor_id = derive_actor_label_and_id(title, summary_full)

            items.append(
                {
                    "source": name,
                    "title": title,
                    "link": link,
                    "summary": summary,
                    "summary_full": summary_full,
                    "published": published,
                    "published_dt": published_dt,
                    "thumbnail": thumb,
                    "actor_label": actor_label,
                    "actor_id": actor_id,
                }
            )

        _cache_set(url, items)
        _touch_health(name, status="OK", items=len(items), error="", last_fetch_utc=fetch_iso)
        return items

    except Exception as ex:
        _touch_health(name, status="ERROR", items=0, error=str(ex), last_fetch_utc=fetch_iso)
        raise


# =============================
# SNAPSHOT REFRESH PIPELINE
# =============================
def refresh_snapshot_if_stale(force: bool = False) -> None:
    """
    Refresh keyword-matched feed items once every REFRESH_TTL_SECONDS.

    Enterprise behavior:
      - Keyword matching uses full text (summary_full) so we don’t lose signal.
      - Actor clustering uses title + summary_full (deterministic).
    """
    now = time.time()
    with _snapshot_lock:
        ts = float(_snapshot.get("ts") or 0.0)
        if (
            not force
            and (now - ts) < REFRESH_TTL_SECONDS
            and isinstance(_snapshot.get("items"), list)
            and _snapshot["items"]
        ):
            return

        errors: List[str] = []
        all_items: List[Dict[str, Any]] = []

        for s in SOURCES:
            try:
                all_items.extend(fetch_feed(s))
            except Exception as ex:
                errors.append(f"{s['name']}: {ex}")

        cutoff = now_utc() - timedelta(days=SNAPSHOT_MAX_DAYS)
        time_trimmed: List[Dict[str, Any]] = []
        for it in all_items:
            dt = it.get("published_dt")
            if dt is None or dt >= cutoff:
                time_trimmed.append(it)

        matched: List[Dict[str, Any]] = []
        for it in time_trimmed:
            full_text = (it.get("summary_full") or it.get("summary") or "")
            title = (it.get("title") or "")
            text = f"{title} {full_text}"

            hits = keyword_hits(text, KEYWORDS)
            if hits:
                actor_label, actor_id = derive_actor_label_and_id(title, full_text)
                it2 = dict(it)
                it2["matched_keywords"] = hits
                it2["actor_label"] = actor_label
                it2["actor_id"] = actor_id
                matched.append(it2)

        _snapshot["ts"] = now
        _snapshot["items"] = matched
        _snapshot["errors"] = errors

        log.info("Snapshot refreshed: %d items (errors=%d)", len(matched), len(errors))


def get_snapshot_items() -> Tuple[List[Dict[str, Any]], List[str]]:
    refresh_snapshot_if_stale(force=False)
    with _snapshot_lock:
        items = list(_snapshot.get("items") or [])
        errors = list(_snapshot.get("errors") or [])
    return items, errors


# =============================
# ACTOR PROFILE ENRICHMENT FOR UI
# =============================
_RE_CVE = re.compile(r"\bCVE-\d{4}-\d{4,7}\b", re.IGNORECASE)
_RE_IPV4 = re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b")
_RE_SHA256 = re.compile(r"\b[a-f0-9]{64}\b", re.IGNORECASE)
_RE_SHA1 = re.compile(r"\b[a-f0-9]{40}\b", re.IGNORECASE)
_RE_MD5 = re.compile(r"\b[a-f0-9]{32}\b", re.IGNORECASE)

_RE_DOMAIN = re.compile(
    r"\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+(?:[a-z]{2,24})\b",
    re.IGNORECASE,
)


def _extract_cves(text: str, limit: int = 5) -> List[str]:
    if not text:
        return []
    cves = [c.upper() for c in _RE_CVE.findall(text)]
    seen = set()
    out: List[str] = []
    for c in cves:
        if c in seen:
            continue
        seen.add(c)
        out.append(c)
        if len(out) >= limit:
            break
    return out


def _extract_iocs(text: str, limit: int = 5) -> List[str]:
    """
    Lightweight IOC extraction:
      - IPv4
      - domains
      - md5/sha1/sha256
    (Deliberately conservative; you can expand later.)
    """
    if not text:
        return []

    found: List[str] = []
    found.extend(_RE_IPV4.findall(text))
    found.extend([d.lower() for d in _RE_DOMAIN.findall(text)])
    found.extend([h.lower() for h in _RE_SHA256.findall(text)])
    found.extend([h.lower() for h in _RE_SHA1.findall(text)])
    found.extend([h.lower() for h in _RE_MD5.findall(text)])

    seen = set()
    out: List[str] = []
    for x in found:
        if x in seen:
            continue
        seen.add(x)
        out.append(x)
        if len(out) >= limit:
            break
    return out


def get_actor_profiles(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Group matched items into lightweight "Threat Actor" profiles.

    Returns EXACT keys your BASE_TEMPLATE expects:
      ap.href
      ap.label
      ap.story_count
      ap.last_seen
      ap.top_cves
      ap.top_iocs
      ap.campaign_id
    """
    buckets: Dict[str, Dict[str, Any]] = {}

    for it in (items or []):
        actor_id = str(it.get("actor_id") or "unattributed").strip() or "unattributed"
        actor_label = str(it.get("actor_label") or "Unattributed").strip() or "Unattributed"

        b = buckets.get(actor_id)
        if not b:
            b = {
                "actor_id": actor_id,
                "actor_label": actor_label,
                "items": [],
                "latest_published": None,   # datetime|None
            }
            buckets[actor_id] = b

        b["items"].append(it)

        dt = it.get("published_dt")
        if isinstance(dt, datetime):
            cur = b.get("latest_published")
            if cur is None or dt > cur:
                b["latest_published"] = dt

    profiles: List[Dict[str, Any]] = []
    for b in buckets.values():
        b["items"].sort(key=lambda x: x.get("published_dt") or datetime.min, reverse=True)

        story_count = len(b["items"])
        latest_dt: Optional[datetime] = b.get("latest_published")

        corpus_parts: List[str] = []
        for it in b["items"][:12]:  # cap for speed
            title = it.get("title") or ""
            body = it.get("summary_full") or it.get("summary") or ""
            corpus_parts.append(f"{title}\n{body}")
        corpus = "\n".join(corpus_parts)

        top_cves = _extract_cves(corpus, limit=4)
        top_iocs = _extract_iocs(corpus, limit=4)

        last_seen = ""
        if isinstance(latest_dt, datetime):
            last_seen = latest_dt.strftime("%Y-%m-%d %H:%M UTC")

        # Make it clickable now (even if you haven’t wired actor filtering yet)
        href = f"/?actor={b['actor_id']}"

        ap = {
            "campaign_id": b["actor_id"],
            "label": b["actor_label"],
            "story_count": story_count,
            "last_seen": last_seen,
            "top_cves": top_cves,
            "top_iocs": top_iocs,
            "href": f"/?actor={quote(b['actor_id'])}",


            # optional compatibility keys (safe to keep)
            "actor_id": b["actor_id"],
            "actor_label": b["actor_label"],
            "count": story_count,
            "latest_published": latest_dt,
            "items": b["items"],
        }

        profiles.append(ap)

    profiles.sort(
        key=lambda p: (p.get("latest_published") or datetime.min, int(p.get("story_count") or 0)),
        reverse=True,
    )
    return profiles


# =============================
# HEALTH ROWS FOR UI
# =============================
def get_health_rows(human_dt_func) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    for s in SOURCES:
        name = s["name"]

        rec = _FEED_HEALTH.get(
            name,
            {
                "source": name,
                "name": name,
                "status": "UNKNOWN",
                "items": 0,
                "last_fetch_utc": "",
                "error": "",
                "detail": "",
                "updated_utc": "",
            },
        )

        last_fetch_utc = str(rec.get("last_fetch_utc") or "")
        last_fetch_dt = _iso_to_dt(last_fetch_utc)

        last_fetch_human = ""
        if last_fetch_dt:
            try:
                last_fetch_human = human_dt_func(last_fetch_dt)
            except Exception:
                last_fetch_human = ""

        updated_utc = str(rec.get("updated_utc") or "")
        updated_dt = _iso_to_dt(updated_utc)
        updated_human = ""
        if updated_dt:
            try:
                updated_human = human_dt_func(updated_dt)
            except Exception:
                updated_human = ""

        rows.append(
            {
                "source": name,
                "status": str(rec.get("status") or "UNKNOWN"),
                "last_fetch_utc": last_fetch_utc,
                "last_fetch_human": last_fetch_human,
                "error": str(rec.get("error") or ""),
                "name": name,
                "detail": str(rec.get("detail") or rec.get("error") or ""),
                "items": int(rec.get("items", 0) or 0),
                "updated": updated_human,
                "updated_utc": updated_utc,
                "last_ok": last_fetch_human,
            }
        )

    return rows
