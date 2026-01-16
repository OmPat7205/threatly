from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


RE_CVE = re.compile(r"\bCVE-\d{4}-\d{4,7}\b", re.IGNORECASE)

RE_IPV4 = re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b")
RE_DOMAIN = re.compile(r"\b(?:[a-z0-9-]+\.)+(?:com|net|org|io|gov|edu|co|uk|de|fr|ru|cn|jp|au|br|in|us)\b", re.IGNORECASE)
RE_SHA256 = re.compile(r"\b[a-f0-9]{64}\b", re.IGNORECASE)
RE_SHA1 = re.compile(r"\b[a-f0-9]{40}\b", re.IGNORECASE)
RE_MD5 = re.compile(r"\b[a-f0-9]{32}\b", re.IGNORECASE)
RE_URL = re.compile(r"\bhttps?://[^\s<>\")]+", re.IGNORECASE)
TRACKING_PREFIXES = ("utm_",)
TRACKING_KEYS = {"fbclid", "gclid", "mc_cid", "mc_eid", "ref", "source", "spm"}

from typing import List

def parse_sources_param(value: str) -> List[str]:
    if not value:
        return []
    parts = [p.strip() for p in value.split(",") if p.strip()]
    seen = set()
    out = []
    for p in parts:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out

def parse_csv_param(value: str) -> List[str]:
    if not value:
        return []
    parts = [p.strip() for p in value.split(",") if p.strip()]
    seen = set()
    out = []
    for p in parts:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def now_utc() -> datetime:
    return datetime.utcnow()


def strip_html(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s or "").strip()


# in threatly/utils.py
from datetime import datetime, timezone

def parse_dt(entry):
    if not entry:
        return None

    # ✅ NEW: allow ISO strings
    if isinstance(entry, str):
        s = entry.strip()
        if not s:
            return None
        try:
            # handles "2025-12-30T23:20:23.199707" (no timezone)
            return datetime.fromisoformat(s.replace("Z", "+00:00"))
        except Exception:
            return None

    # existing logic (dict-like feedparser entry)
    for k in ("published_parsed", "updated_parsed"):
        if entry.get(k):
            try:
                return datetime(*entry[k][:6], tzinfo=timezone.utc).replace(tzinfo=None)
            except Exception:
                pass
    for k in ("published", "updated"):
        if entry.get(k):
            try:
                return datetime.fromisoformat(entry.get(k).replace("Z", "+00:00"))
            except Exception:
                pass
    return None



def canonicalize_url(url: str) -> str:
    if not url:
        return ""
    try:
        p = urlparse(url)
        q = parse_qsl(p.query, keep_blank_values=True)
        q2 = []
        for k, v in q:
            kl = k.lower()
            if kl.startswith(TRACKING_PREFIXES):
                continue
            if kl in TRACKING_KEYS:
                continue
            q2.append((k, v))
        new_query = urlencode(q2, doseq=True)
        p2 = p._replace(
            scheme=(p.scheme or "https").lower(),
            netloc=(p.netloc or "").lower(),
            query=new_query,
            fragment="",
        )
        return urlunparse(p2)
    except Exception:
        return url


def pick_thumbnail(entry: Dict[str, Any]) -> str:
    for key in ("media_thumbnail", "media_content"):
        if entry.get(key):
            try:
                if isinstance(entry[key], list) and entry[key]:
                    url = entry[key][0].get("url") or ""
                    return url
            except Exception:
                pass

    try:
        links = entry.get("links") or []
        for l in links:
            if (l.get("type") or "").startswith("image/") and l.get("href"):
                return l["href"]
    except Exception:
        pass

    summary = entry.get("summary") or entry.get("description") or ""
    m = re.search(r'<img[^>]+src="([^"]+)"', summary, flags=re.IGNORECASE)
    if m:
        return m.group(1)

    return ""


def keyword_hits(text: str, keywords: List[str]) -> List[str]:
    t = (text or "").lower()
    hits = []
    for kw in keywords:
        k = kw.lower().strip()
        if k and k in t:
            hits.append(kw)
    return hits

def extract_indicators(text: str) -> Dict[str, List[str]]:
    text = text or ""
    cves = sorted({m.group(0).upper() for m in RE_CVE.finditer(text)})
    ips = sorted(set(RE_IPV4.findall(text)))
    domains = sorted({d.lower() for d in RE_DOMAIN.findall(text)})
    sha256 = sorted({h.lower() for h in RE_SHA256.findall(text)})
    sha1 = sorted({h.lower() for h in RE_SHA1.findall(text)})
    md5 = sorted({h.lower() for h in RE_MD5.findall(text)})
    urls = sorted({canonicalize_url(u) for u in RE_URL.findall(text)})

    return {
        "cves": cves[:50],
        "ips": ips[:50],
        "domains": domains[:50],
        "sha256": sha256[:50],
        "sha1": sha1[:50],
        "md5": md5[:50],
        "urls": urls[:50],
    }


from typing import List

def parse_sources_param(value: str) -> List[str]:
    if not value:
        return []
    parts = [p.strip() for p in value.split(",") if p.strip()]
    seen = set()
    out: List[str] = []
    for p in parts:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


def parse_csv_param(value: str) -> List[str]:
    # same behavior, but keep it separate for readability
    if not value:
        return []
    parts = [p.strip() for p in value.split(",") if p.strip()]
    seen = set()
    out: List[str] = []
    for p in parts:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out




def human_dt(dt: Optional[datetime]) -> str:
    if not dt:
        return ""
    return dt.strftime("%Y-%m-%d %H:%M UTC")



def today_utc_str() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d")
