# threatly/rbac.py
from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Dict, Optional, Set

from flask import abort, g

ROLE_VIEWER = "viewer"
ROLE_ANALYST = "analyst"
ROLE_ADMIN = "admin"
ALL_ROLES = {ROLE_VIEWER, ROLE_ANALYST, ROLE_ADMIN}

PERM_VIEW_APP = "view_app"
PERM_MARK_SEEN = "mark_seen"
PERM_CASE_EDIT = "case_edit"
PERM_EXPORT_REPORTS = "export_reports"
PERM_VIEW_ADMIN = "view_admin"
PERM_MANAGE_USERS = "manage_users"
PERM_MANAGE_ACTORS = "manage_actors"


ROLE_PERMS: Dict[str, Set[str]] = {
    ROLE_VIEWER: {PERM_VIEW_APP, PERM_MARK_SEEN},
    ROLE_ANALYST: {PERM_VIEW_APP, PERM_MARK_SEEN, PERM_CASE_EDIT},
    ROLE_ADMIN: {
        PERM_VIEW_APP,
        PERM_MARK_SEEN,
        PERM_CASE_EDIT,
        PERM_EXPORT_REPORTS,
        PERM_VIEW_ADMIN,
        PERM_MANAGE_USERS,
        PERM_MANAGE_ACTORS,
    },
}

def _user() -> Optional[Dict[str, Any]]:
    return getattr(g, "user", None)

def has_perm(perm: str) -> bool:
    u = _user()
    if not u:
        return False    
    active_val = u.get("is_active", None)
    if active_val is None:
        active_val = u.get("active", 0)
    if int(active_val or 0) != 1:
        return False

    role = (u.get("role") or "").strip().lower()
    if role not in ALL_ROLES:
        return False
    return perm in ROLE_PERMS.get(role, set())

def require_perm(perm: str) -> Callable:
    def deco(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapped(*args: Any, **kwargs: Any):
            if not _user():
                abort(401)
            if not has_perm(perm):
                abort(403)
            return fn(*args, **kwargs)
        return wrapped
    return deco
