from __future__ import annotations

import json
import os
import re
import time
from typing import Any, Dict, List, Tuple, Optional

from .config import WATCHLIST_PATH

# =============================
# PHASE 4: WATCHLIST (GLOBAL STACK)
# =============================
DEFAULT_WATCHLIST: Dict[str, List[str]] = {
    "Okta": ["okta"],
    "Microsoft Exchange": ["exchange", "outlook web access", "owa"],
    "Microsoft 365": ["microsoft 365", "office 365", "o365"],
    "Azure AD / Entra": ["azure ad", "entra", "microsoft entra"],
    "Fortinet": ["fortinet", "fortigate", "fortios"],
    "Citrix / NetScaler": ["citrix", "netscaler", "adc"],
    "Palo Alto Networks": ["palo alto", "pan-os", "prisma"],
    "VMware": ["vmware", "esxi", "vcenter", "vsphere"],
    "Kubernetes": ["kubernetes", "k8s"],
    "AWS": ["aws", "amazon web services"],
    "GCP": ["gcp", "google cloud platform"],
    "Azure": ["azure"],
}

# Light in-module caches so app.py doesn't carry extra globals
_watchlist_cache: Dict[str, Any] = {"ts": 0.0, "data": {}}  # raw watchlist dict
_compiled_cache: Dict[str, Any] = {"ts": 0.0, "compiled": {}}  # compiled matchers


# -----------------------------
# Helpers
# -----------------------------
def _now() -> float:
    return time.time()


def _normalize_term(t: str) -> str:
    # Keep regex terms as-is after trimming
    tt = (t or "").strip()
    if tt.lower().startswith("re:"):
        return "re:" + tt[3:].strip()
    # normalize whitespace and lowercase for matching
    tt = re.sub(r"\s+", " ", tt).strip().lower()
    return tt


def _normalize_watchlist(wl: Dict[str, List[str]]) -> Dict[str, List[str]]:
    out: Dict[str, List[str]] = {}
    for k, v in (wl or {}).items():
        if not isinstance(k, str) or not isinstance(v, list):
            continue
        name = k.strip()
        if not name:
            continue
        terms: List[str] = []
        for x in v:
            nx = _normalize_term(str(x))
            if nx:
                terms.append(nx)
        # dedupe while preserving order
        seen = set()
        uniq: List[str] = []
        for t in terms:
            if t in seen:
                continue
            seen.add(t)
            uniq.append(t)
        if uniq:
            out[name] = uniq
    return out


def _broad_terms(wl: Dict[str, List[str]]) -> List[Tuple[str, str]]:
    """
    Returns (label, term) pairs that are *likely* too broad/noisy.
    This is informational; we do NOT block matching at runtime.
    """
    broad: List[Tuple[str, str]] = []
    for name, terms in (wl or {}).items():
        for t in terms:
            if t.startswith("re:"):
                continue
            # very short or very generic single words are high-noise
            if len(t) <= 2:
                broad.append((name, t))
                continue
            if " " not in t and t in {"azure", "amazon", "google", "windows", "linux", "microsoft"}:
                broad.append((name, t))
    return broad


def _compile_watchlist(wl: Dict[str, List[str]]) -> Dict[str, Dict[str, Any]]:
    """
    Builds per-label matchers:
      - regex patterns for 're:' terms
      - word-boundary regex for normal terms (reduces substring noise)
    """
    compiled: Dict[str, Dict[str, Any]] = {}
    for name, terms in (wl or {}).items():
        regexes: List[re.Pattern[str]] = []
        boundary: List[re.Pattern[str]] = []
        for t in terms:
            if t.startswith("re:"):
                pat = t[3:].strip()
                if not pat:
                    continue
                try:
                    regexes.append(re.compile(pat, flags=re.IGNORECASE))
                except Exception:
                    # ignore invalid regex patterns
                    continue
            else:
                # word-ish boundary matching:
                # - if term contains non-word chars like '-' or '.', still works
                # - we allow term inside boundaries so "pan-os" matches "PAN-OS"
                # - we avoid matching inside larger words ("azure" won't match "lazured" etc.)
                escaped = re.escape(t)
                boundary.append(re.compile(rf"(?<!\w){escaped}(?!\w)", flags=re.IGNORECASE))
        compiled[name] = {"regex": regexes, "boundary": boundary, "terms": terms}
    return compiled


def _dedupe_overlapping_hits(hits: List[str], wl: Dict[str, List[str]]) -> List[str]:
    """
    Prefer more specific labels over generic ones when terms overlap.

    Heuristic:
      If label A's term-set is a strict subset of label B's term-set,
      then B is more specific than A. If both hit, drop A.
    """
    if not hits:
        return []
    hitset = set(hits)

    # Build normalized term sets for labels that hit (ignore regex terms for specificity math)
    termsets: Dict[str, set] = {}
    for name in hitset:
        ts = set()
        for t in wl.get(name, []):
            if t.startswith("re:"):
                continue
            ts.add(t)
        termsets[name] = ts

    # Decide which to drop
    drop: set = set()
    names = list(hitset)
    for i in range(len(names)):
        a = names[i]
        for j in range(len(names)):
            if i == j:
                continue
            b = names[j]
            sa = termsets.get(a, set())
            sb = termsets.get(b, set())
            if not sa or not sb:
                continue
            # if a is strictly more generic than b, drop a
            if sa.issubset(sb) and sa != sb:
                drop.add(a)

    kept = [h for h in hits if h not in drop]
    return kept


# -----------------------------
# Public API
# -----------------------------
def ensure_watchlist_file() -> None:
    d = os.path.dirname(WATCHLIST_PATH)
    if d:
        os.makedirs(d, exist_ok=True)
    if os.path.exists(WATCHLIST_PATH):
        return
    try:
        with open(WATCHLIST_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_WATCHLIST, f, indent=2)
    except Exception:
        # If the FS is read-only, we just fall back to defaults.
        pass


def load_watchlist() -> Dict[str, List[str]]:
    """
    Flat JSON mapping of { "Product/Vendor": ["term1","term2", ...] }.

    Terms are matched case-insensitively. If a term starts with 're:', it's treated as a regex.
    Normal terms are matched using word-boundary rules to reduce false positives.
    """
    # light cache (60s) to avoid re-reading on every request
    now = _now()
    ts = float(_watchlist_cache.get("ts") or 0.0)
    if (now - ts) < 60 and isinstance(_watchlist_cache.get("data"), dict) and _watchlist_cache["data"]:
        return _watchlist_cache["data"]  # type: ignore

    wl: Dict[str, List[str]] = {}
    try:
        if os.path.exists(WATCHLIST_PATH):
            with open(WATCHLIST_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                wl = _normalize_watchlist(data)  # normalize on load
    except Exception:
        wl = {}

    if not wl:
        wl = _normalize_watchlist(dict(DEFAULT_WATCHLIST))

    _watchlist_cache["ts"] = now
    _watchlist_cache["data"] = wl

    # bust compiled cache when watchlist refreshes
    _compiled_cache["ts"] = 0.0
    _compiled_cache["compiled"] = {}

    return wl


def get_watchlist_warnings() -> List[Tuple[str, str]]:
    """
    Optional helper for admin UI: shows terms that are likely too broad/noisy.
    """
    wl = load_watchlist()
    return _broad_terms(wl)


def _get_compiled(wl: Dict[str, List[str]]) -> Dict[str, Dict[str, Any]]:
    # cache compiled matchers for 60s
    now = _now()
    ts = float(_compiled_cache.get("ts") or 0.0)
    if (now - ts) < 60 and isinstance(_compiled_cache.get("compiled"), dict) and _compiled_cache["compiled"]:
        return _compiled_cache["compiled"]  # type: ignore

    compiled = _compile_watchlist(wl)
    _compiled_cache["ts"] = now
    _compiled_cache["compiled"] = compiled
    return compiled


def invalidate_watchlist_cache() -> None:
    _watchlist_cache["ts"] = 0.0
    _watchlist_cache["data"] = {}
    _compiled_cache["ts"] = 0.0
    _compiled_cache["compiled"] = {}


def watchlist_matches_for_story(story: Dict[str, Any], wl: Dict[str, List[str]]) -> List[str]:
    """
    Returns stable-sorted list of matching watchlist labels.
    """
    title = (story.get("title") or "")
    summary = (story.get("summary") or "")
    kws = " ".join(story.get("matched_keywords") or [])
    cves = " ".join((story.get("indicators") or {}).get("cves", []) or [])

    # normalize text: lowercase, normalize whitespace
    raw = f"{title}\n{summary}\n{kws}\n{cves}"
    text = re.sub(r"\s+", " ", raw).strip().lower()

    compiled = _get_compiled(wl)

    hits: List[str] = []
    for name, pack in compiled.items():
        # regex terms
        for rgx in pack.get("regex", []):
            try:
                if rgx.search(text):
                    hits.append(name)
                    break
            except Exception:
                continue
        else:
            # boundary terms
            for b in pack.get("boundary", []):
                try:
                    if b.search(text):
                        hits.append(name)
                        break
                except Exception:
                    continue

    # prefer specific over generic when overlaps occur
    hits = _dedupe_overlapping_hits(hits, wl)

    # stable ordering
    hits = sorted(set(hits), key=lambda x: x.lower())
    return hits
