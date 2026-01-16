from __future__ import annotations

import time
from typing import Any, Dict, Tuple

import requests

from .config import (
    KEV_CATALOG_URL,
    KEV_CACHE_TTL_SECONDS,
    REQUEST_TIMEOUT_SECONDS,
)

# Module-level cache (keeps app.py clean, behavior stays identical)
_kev_cache: Dict[str, Any] = {"ts": 0.0, "cves": set(), "error": ""}  # type: ignore


def get_kev_cves() -> Tuple[set, str]:
    """
    Returns (kev_set, error_string). kev_set is a set of CVE IDs (uppercase).
    Uses a TTL cache to avoid hammering CISA.
    """
    now = time.time()
    ts = float(_kev_cache.get("ts") or 0.0)

    if (now - ts) < KEV_CACHE_TTL_SECONDS and _kev_cache.get("cves"):
        return _kev_cache["cves"], (_kev_cache.get("error") or "")  # type: ignore

    headers = {
        "User-Agent": "Mozilla/5.0 (ThreatlyFeed/0.9; KEVCache)",
        "Accept": "application/json,*/*;q=0.8",
    }

    try:
        resp = requests.get(KEV_CATALOG_URL, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
        resp.raise_for_status()
        data = resp.json()

        vulns = data.get("vulnerabilities") or []
        cves = set()

        for v in vulns:
            c = (v.get("cveID") or v.get("cveId") or v.get("cve") or "").strip().upper()
            if c.startswith("CVE-"):
                cves.add(c)

        _kev_cache["ts"] = now
        _kev_cache["cves"] = cves
        _kev_cache["error"] = ""
        return cves, ""

    except Exception as ex:
        _kev_cache["ts"] = now
        _kev_cache["error"] = str(ex)
        return (_kev_cache.get("cves") or set()), str(ex)


def story_is_kev(story: Dict[str, Any]) -> bool:
    cves = (story.get("indicators") or {}).get("cves", []) or []
    if not cves:
        return False
    kev_set, _err = get_kev_cves()
    return any(c.upper() in kev_set for c in cves)
