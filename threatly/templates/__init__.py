# threatly/templates/__init__.py

from .base import BASE_TEMPLATE
from .story import STORY_TEMPLATE
from .daily import DAILY_TEMPLATE
from .health import HEALTH_TEMPLATE
from .login import LOGIN_TEMPLATE
from .shortcuts import SHORTCUTS_TEMPLATE
from .campaign import CAMPAIGN_TEMPLATE

from .admin.base import ADMIN_BASE_TEMPLATE
from .admin.dashboard import ADMIN_DASHBOARD_TEMPLATE
from .admin.users import ADMIN_USERS_TEMPLATE
from .admin.roles import ADMIN_ROLES_TEMPLATE
from .admin.audit import ADMIN_AUDIT_TEMPLATE
from .admin.settings import ADMIN_SETTINGS_TEMPLATE

__all__ = [
    "BASE_TEMPLATE",
    "STORY_TEMPLATE",
    "DAILY_TEMPLATE",
    "HEALTH_TEMPLATE",
    "LOGIN_TEMPLATE",
    "SHORTCUTS_TEMPLATE",
    "CAMPAIGN_TEMPLATE",
    "ADMIN_BASE_TEMPLATE",
    "ADMIN_DASHBOARD_TEMPLATE",
    "ADMIN_USERS_TEMPLATE",
    "ADMIN_ROLES_TEMPLATE",
    "ADMIN_AUDIT_TEMPLATE",
    "ADMIN_SETTINGS_TEMPLATE",
    "TEMPLATES"
]


# Optional clean access layer (does NOT break existing variable imports)
TEMPLATES = {
    # core
    "base": BASE_TEMPLATE,
    "story": STORY_TEMPLATE,
    "daily": DAILY_TEMPLATE,
    "health": HEALTH_TEMPLATE,
    "login": LOGIN_TEMPLATE,
    "shortcuts": SHORTCUTS_TEMPLATE,
    "campaign": CAMPAIGN_TEMPLATE,

    # admin
    "admin_base": ADMIN_BASE_TEMPLATE,
    "admin_dashboard": ADMIN_DASHBOARD_TEMPLATE,
    "admin_users": ADMIN_USERS_TEMPLATE,
    "admin_roles": ADMIN_ROLES_TEMPLATE,
    "admin_audit": ADMIN_AUDIT_TEMPLATE,
    "admin_settings": ADMIN_SETTINGS_TEMPLATE,
}
