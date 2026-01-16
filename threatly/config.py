# threatly/config.py
import os


def _env_bool(name: str, default: str = "0") -> bool:
    v = os.environ.get(name, default)
    return str(v).strip().lower() in ("1", "true", "yes", "y", "on")


# =============================
# AUTH / SECURITY
# =============================
# REQUIRED for login sessions. In Docker/prod you should set this to a long random value.
# Example: SECRET_KEY="a-very-long-random-string"
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-insecure-change-me")

# If True, users must log in to view the dashboard. If False, viewing is allowed but write actions require login.
AUTH_REQUIRE_LOGIN = _env_bool("AUTH_REQUIRE_LOGIN", "0")

# Bootstrap admin user (created automatically on boot if no users exist)
ADMIN_EMAIL = (os.environ.get("ADMIN_EMAIL") or "").strip().lower()
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD") or ""

# Cookie/session hardening (works best behind HTTPS)
SESSION_COOKIE_SECURE = _env_bool("SESSION_COOKIE_SECURE", "0")   # set to 1 behind HTTPS
SESSION_COOKIE_HTTPONLY = _env_bool("SESSION_COOKIE_HTTPONLY", "1")
SESSION_COOKIE_SAMESITE = os.environ.get("SESSION_COOKIE_SAMESITE", "Lax")  # Lax or Strict


# =============================
# KEYWORDS
# =============================
KEYWORDS = [
    "cve", "zero-day", "0day", "n-day",
    "remote code execution", "rce",
    "privilege escalation", "elevation of privilege",
    "authentication bypass", "sandbox escape",
    "deserialization", "memory corruption",
    "buffer overflow", "heap overflow", "use-after-free",
    "command injection", "sql injection",
    "path traversal", "directory traversal",
    "arbitrary file upload",

    "ransomware", "wiper",
    "data exfiltration", "double extortion",
    "initial access", "payload", "dropper", "loader",
    "botnet", "backdoor",
    "c2", "command and control", "beaconing",
    "lateral movement", "persistence", "living off the land", "lolbins",
    "credential harvesting", "credential dumping", "mimikatz",

    "apt", "advanced persistent threat",
    "threat actor", "nation-state",
    "espionage", "cyber espionage",
    "campaign", "operation", "intrusion set", "cluster",

    "supply chain", "dependency confusion", "typosquatting",
    "malicious package", "open source compromise",
    "ci/cd", "pipeline compromise",
    "cloud misconfiguration", "iam misconfiguration",
    "credential exposure", "api abuse", "oauth abuse", "token theft",

    "phishing", "spear phishing", "business email compromise", "bec",
    "malicious attachment", "malicious link",
    "smishing", "vishing", "qr phishing",
    "impersonation", "account takeover", "ato",

    "actively exploited", "in the wild",
    "mass exploitation", "exploitation observed",
    "proof of concept", "poc",
    "exploit kit", "weaponized",
    "patch bypass", "public exploit", "metasploit",
]

# =============================
# SOURCES
# =============================
SOURCES = [
    {"name": "CISA Advisories", "rss": "https://www.cisa.gov/cybersecurity-advisories/all.xml"},
    {"name": "Microsoft Security Blog", "rss": "https://www.microsoft.com/en-us/security/blog/feed/"},
    {"name": "Google Security Blog", "rss": "https://security.googleblog.com/feeds/posts/default?alt=rss"},
    {"name": "Krebs on Security", "rss": "https://krebsonsecurity.com/feed/"},
    {"name": "Google Cloud - Threat Intelligence (Mandiant/GTIG)", "rss": "https://feeds.feedburner.com/threatintelligence/pvexyqv7v0v"},
    {"name": "Google Threat Analysis Group (TAG)", "rss": "https://blog.google/threat-analysis-group/rss/"},
    {"name": "Palo Alto Unit 42", "rss": "http://feeds.feedburner.com/Unit42"},
    {"name": "SANS Internet Storm Center (Full)", "rss": "https://isc.sans.edu/rssfeed_full.xml"},
    {"name": "Kaspersky Securelist", "rss": "https://securelist.com/feed/"},
    {"name": "Sophos - Threat Research", "rss": "https://news.sophos.com/en-us/category/threat-research/feed/"},
    {"name": "Sophos - Security Operations", "rss": "https://news.sophos.com/en-us/category/security-operations/feed/"},
    {"name": "Proofpoint (main RSS)", "rss": "https://www.proofpoint.com/us/rss.xml"},
    {"name": "Cisco Security - Event Responses", "rss": "https://sec.cloudapps.cisco.com/security/center/eventResponses_20.xml"},
    {"name": "JPCERT/CC (English RSS)", "rss": "https://www.jpcert.or.jp/english/rss/jpcert-en.rdf"},
    {"name": "JPCERT/CC Blog (Atom)", "rss": "https://blogs.jpcert.or.jp/en/atom.xml"},
    {"name": "GovCERT.HK - Security Alerts", "rss": "https://www.govcert.gov.hk/en/rss_security_alerts.xml"},
    {"name": "GovCERT.HK - Security Blogs", "rss": "https://www.govcert.gov.hk/en/rss_security_blogs.xml"},
]

# =============================
# GENERAL SETTINGS
# =============================
MAX_ITEMS_PER_SOURCE = 50
STORY_SIMILARITY_THRESHOLD = 0.55

CACHE_TTL_SECONDS = 8 * 60
MAX_FEED_BYTES = 2_000_000
REQUEST_TIMEOUT_SECONDS = 15

REPORT_DIR = os.environ.get("REPORT_DIR", "reports")

# =============================
# SOURCE WEIGHTS
# =============================
SOURCE_WEIGHT = {
    "CISA Advisories": 100,
    "Google Cloud - Threat Intelligence (Mandiant/GTIG)": 90,
    "Google Threat Analysis Group (TAG)": 90,
    "Microsoft Security Blog": 85,
    "Google Security Blog": 80,
    "Cisco Security - Event Responses": 80,
    "JPCERT/CC (English RSS)": 85,
    "Palo Alto Unit 42": 80,
    "SANS Internet Storm Center (Full)": 75,
    "Proofpoint (main RSS)": 75,
    "Kaspersky Securelist": 75,
    "Sophos - Threat Research": 75,
    "Sophos - Security Operations": 70,
    "JPCERT/CC Blog (Atom)": 70,
    "GovCERT.HK - Security Alerts": 80,
    "GovCERT.HK - Security Blogs": 70,
    "Krebs on Security": 60,
}

# =============================
# KEV
# =============================
KEV_CATALOG_URL = os.environ.get(
    "KEV_CATALOG_URL",
    "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
)
KEV_CACHE_TTL_SECONDS = 12 * 60 * 60

# =============================
# STATE / META
# =============================
STATE_DB_PATH = os.environ.get("STATE_DB_PATH", "state/state.db")

STATUS_VALUES = ["New", "Investigating", "Not Relevant", "Mitigated"]

WATCHLIST_PATH = os.environ.get("WATCHLIST_PATH", os.path.join("state", "watchlist.json"))

# =============================
# CVE ENRICHMENT
# =============================
NVD_CVE_API = os.environ.get("NVD_CVE_API", "https://services.nvd.nist.gov/rest/json/cves/2.0")
EPSS_API = os.environ.get("EPSS_API", "https://api.first.org/data/v1/epss")

NVD_CACHE_TTL_SECONDS = int(os.environ.get("NVD_CACHE_TTL_SECONDS", str(24 * 60 * 60)))
EPSS_CACHE_TTL_SECONDS = int(os.environ.get("EPSS_CACHE_TTL_SECONDS", str(6 * 60 * 60)))

MAX_CVES_ENRICH_PER_STORY = int(os.environ.get("MAX_CVES_ENRICH_PER_STORY", "8"))
MAX_VENDOR_LINKS_PER_CVE = int(os.environ.get("MAX_VENDOR_LINKS_PER_CVE", "5"))

# =============================
# SNAPSHOT
# =============================
REFRESH_TTL_SECONDS = int(os.environ.get("REFRESH_TTL_SECONDS", "180"))
SNAPSHOT_MAX_DAYS = int(os.environ.get("SNAPSHOT_MAX_DAYS", "30"))

