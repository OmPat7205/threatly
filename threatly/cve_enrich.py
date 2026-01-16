from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

import requests

from threatly.config import (
    NVD_CVE_API,
    EPSS_API,
    REQUEST_TIMEOUT_SECONDS,
    NVD_CACHE_TTL_SECONDS,
    EPSS_CACHE_TTL_SECONDS,
    MAX_CVES_ENRICH_PER_STORY,
    MAX_VENDOR_LINKS_PER_CVE,
)

# Module-level caches (same behavior as before)
_nvd_cache: Dict[str, Dict[str, Any]] = {}   # cve -> {ts, data, error}
_epss_cache: Dict[str, Dict[str, Any]] = {}  # cve -> {ts, data, error}


def _http_headers(tag: str) -> Dict[str, str]:
    # Use a non-placeholder UA for production credibility.
    return {
        "User-Agent": f"Threatly/{tag}",
        "Accept": "application/json,*/*;q=0.8",
    }


def _safe_float(x: Any) -> Optional[float]:
    try:
        if x is None:
            return None
        return float(x)
    except Exception:
        return None


def _pick_cvss_from_nvd(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    NVD v2 schema: metrics may include cvssMetricV31, cvssMetricV30, cvssMetricV2.
    We pick the "Primary" record if present, else first item.
    """
    for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        arr = metrics.get(key)
        if isinstance(arr, list) and arr:
            chosen = None
            for m in arr:
                if isinstance(m, dict) and (m.get("type") or "").lower() == "primary":
                    chosen = m
                    break
            if chosen is None:
                chosen = arr[0]
            if not isinstance(chosen, dict):
                continue

            cvss = chosen.get("cvssData") or {}
            base_score = _safe_float(cvss.get("baseScore"))
            base_sev = (cvss.get("baseSeverity") or chosen.get("baseSeverity") or "").strip()
            vector = (cvss.get("vectorString") or "").strip()

            if not base_sev and isinstance(chosen.get("baseSeverity"), str):
                base_sev = chosen.get("baseSeverity")

            return {
                "version": str(
                    cvss.get("version")
                    or ("3.1" if key == "cvssMetricV31" else ("3.0" if key == "cvssMetricV30" else "2.0"))
                ),
                "base_score": base_score,
                "base_severity": base_sev,
                "vector": vector,
            }

    return {"version": "", "base_score": None, "base_severity": "", "vector": ""}


def fetch_nvd_cve(cve: str) -> Dict[str, Any]:
    c = (cve or "").strip().upper()
    if not c.startswith("CVE-"):
        return {"ok": False, "cve": c, "cvss": {}, "vendor_advisories": [], "references": [], "error": "invalid cve"}

    now = time.time()
    ent = _nvd_cache.get(c)
    if ent and (now - float(ent.get("ts") or 0.0)) < NVD_CACHE_TTL_SECONDS and ent.get("data"):
        return ent["data"]  # type: ignore

    url = f"{NVD_CVE_API}?cveId={c}"
    try:
        resp = requests.get(url, headers=_http_headers("NVD"), timeout=REQUEST_TIMEOUT_SECONDS)
        resp.raise_for_status()
        data = resp.json()

        vulns = data.get("vulnerabilities") or []
        if not vulns:
            out = {"ok": False, "cve": c, "cvss": {}, "vendor_advisories": [], "references": [], "error": "not found"}
            _nvd_cache[c] = {"ts": now, "data": out, "error": out["error"]}
            return out

        cve_obj = (vulns[0] or {}).get("cve") or {}
        metrics = cve_obj.get("metrics") or {}
        cvss = _pick_cvss_from_nvd(metrics)

        refs: List[Dict[str, Any]] = []
        raw_refs = cve_obj.get("references") or []
        if isinstance(raw_refs, list):
            for r in raw_refs:
                if not isinstance(r, dict):
                    continue
                u = (r.get("url") or "").strip()
                if not u:
                    continue
                tags = r.get("tags") or []
                tags2 = [str(t) for t in tags] if isinstance(tags, list) else []
                refs.append({"url": u, "tags": tags2})

        vendor = [r for r in refs if any(str(t).lower() == "vendor advisory" for t in (r.get("tags") or []))]
        if not vendor:
            vendor = [
                r for r in refs
                if any(str(t).lower() in ("release notes", "patch", "third party advisory", "product") for t in (r.get("tags") or []))
            ]

        vendor = vendor[:MAX_VENDOR_LINKS_PER_CVE]
        refs = refs[:max(MAX_VENDOR_LINKS_PER_CVE, 10)]

        out = {
            "ok": True,
            "cve": c,
            "cvss": cvss,
            "vendor_advisories": vendor,
            "references": refs,
            "error": "",
        }
        _nvd_cache[c] = {"ts": now, "data": out, "error": ""}
        return out

    except Exception as ex:
        out = {"ok": False, "cve": c, "cvss": {}, "vendor_advisories": [], "references": [], "error": str(ex)}
        _nvd_cache[c] = {"ts": now, "data": out, "error": str(ex)}
        return out


def fetch_epss(cve: str) -> Dict[str, Any]:
    c = (cve or "").strip().upper()
    if not c.startswith("CVE-"):
        return {"ok": False, "cve": c, "epss": None, "percentile": None, "error": "invalid cve"}

    now = time.time()
    ent = _epss_cache.get(c)
    if ent and (now - float(ent.get("ts") or 0.0)) < EPSS_CACHE_TTL_SECONDS and ent.get("data") is not None:
        return ent["data"]  # type: ignore

    url = f"{EPSS_API}?cve={c}"
    try:
        resp = requests.get(url, headers=_http_headers("EPSS"), timeout=REQUEST_TIMEOUT_SECONDS)
        resp.raise_for_status()
        data = resp.json()

        arr = data.get("data") or []
        epss = None
        pct = None
        if isinstance(arr, list) and arr:
            row = arr[0] if isinstance(arr[0], dict) else {}
            epss = _safe_float(row.get("epss"))
            pct = _safe_float(row.get("percentile"))

        out = {"ok": True, "cve": c, "epss": epss, "percentile": pct, "error": ""}
        _epss_cache[c] = {"ts": now, "data": out, "error": ""}
        return out

    except Exception as ex:
        out = {"ok": False, "cve": c, "epss": None, "percentile": None, "error": str(ex)}
        _epss_cache[c] = {"ts": now, "data": out, "error": str(ex)}
        return out


def enrich_story_cves(story: Dict[str, Any]) -> Dict[str, Any]:
    ind = story.get("indicators") or {}
    cves = (ind.get("cves") or [])[:MAX_CVES_ENRICH_PER_STORY]

    out_rows: List[Dict[str, Any]] = []
    errors: List[str] = []

    cvss_max: Optional[float] = None
    epss_max: Optional[float] = None

    for c in cves:
        c = (c or "").strip().upper()
        if not c.startswith("CVE-"):
            continue

        nvd = fetch_nvd_cve(c)
        epss = fetch_epss(c)

        row_errs: List[str] = []
        if not nvd.get("ok"):
            if nvd.get("error"):
                row_errs.append(f"NVD: {nvd.get('error')}")
        if not epss.get("ok"):
            if epss.get("error"):
                row_errs.append(f"EPSS: {epss.get('error')}")

        cvss = nvd.get("cvss") or {}
        base_score = _safe_float(cvss.get("base_score"))
        if base_score is not None:
            cvss_max = base_score if cvss_max is None else max(cvss_max, base_score)

        epss_val = _safe_float(epss.get("epss"))
        if epss_val is not None:
            epss_max = epss_val if epss_max is None else max(epss_max, epss_val)

        out_rows.append(
            {
                "cve": c,
                "cvss": cvss,
                "epss": {"epss": epss_val, "percentile": _safe_float(epss.get("percentile"))},
                "vendor_advisories": nvd.get("vendor_advisories") or [],
                "references": nvd.get("references") or [],
                "errors": row_errs,
            }
        )

    for r in out_rows:
        for e in r.get("errors") or []:
            if e and e not in errors:
                errors.append(e)

    enrichment = {"cves": out_rows, "cvss_max": cvss_max, "epss_max": epss_max, "errors": errors}
    story["cve_enrichment"] = enrichment
    return enrichment
