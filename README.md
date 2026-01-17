# Threatly

Threatly is a threat intelligence triage and accountability system.
It helps security teams turn noisy threat feeds into structured decisions that can be tracked, reviewed, and audited over time.

Threatly is not a SIEM, SOAR, alerting platform, or detection engine.
It sits between raw threat intelligence and human decision-making.

---

## Why Threatly Exists

Most threat intelligence tools focus on collecting more data.
Threatly focuses on deciding what matters — and proving what was done about it.

Threatly is designed to answer the questions security teams and auditors actually ask:
- What did we see?
- When did we see it?
- Who reviewed it?
- What decision was made?
- Why was that decision made?

This makes Threatly a system of record for threat intelligence decisions.

---

## Core Capabilities

Threat Intelligence Triage
- Aggregates multiple security feeds into a single view
- De-duplicates related items into unified stories
- Transparent severity scoring (no black boxes)
- Extracts and tracks CVEs, domains, IPs, and hashes

Analyst Workflow
- Mark stories as reviewed
- Assign status, owner, and notes
- Track “new since last login”
- Filter by severity, source, category, KEV, and indicators

Campaign and Actor Tracking
- Groups related stories into campaigns
- Links infrastructure, CVEs, and sources
- Maintains campaign-level history and relationships

Auditability and Accountability
- Append-only lifecycle events for every story
- Full audit trail of analyst actions
- Exportable history for reviews and compliance
- Built to answer “who knew what, and when”

Administration and RBAC
- Role-based access control
- Permission-gated actions
- Admin dashboards
- Safe defaults for enterprise environments

---

## Architecture Overview

- Backend: Python + Flask
- Database: SQLite (default)
- Deployment: Docker-friendly, single-instance by default
- Authentication: Built-in authentication with RBAC
- Storage model: Append-only, no hard deletes

Threatly is intentionally boring to operate and easy to reason about.

---

## What Threatly Is Not

Threatly explicitly does not:
- Generate alerts or notifications
- Replace a SIEM or EDR
- Perform detections or automated response
- Depend on opaque AI decision-making

Threatly complements existing security tools — it does not replace them.

---

## Getting Started

Requirements
- Python 3.11+
- SQLite (bundled)
- Docker (recommended)

Threatly is designed to run as a single service with persistent storage.

---

## Configuration

Common environment variables:
- AUTH_REQUIRE_LOGIN=1 — enforce authentication
- SECRET_KEY — required for stable sessions
- COOKIE_SECURE=1 — enable secure cookies (HTTPS)
- SIGNUP_ENABLED=0 — disable public signup
- BOOTSTRAP_ADMIN_EMAIL / BOOTSTRAP_ADMIN_PASSWORD — create first admin user
- PUBLIC_BASE_URL — used for report links
- READ_ONLY_MODE=1 — disable all write operations

---

## Persistence and Data Safety

Threatly uses SQLite by default.
A persistent volume must be mounted to retain data across restarts.

The data model favors:
- Append-only logs
- Soft deletes
- Historical traceability

PostgreSQL support is planned for multi-instance deployments.

---

## Exports and Reporting

Threatly supports:
- Daily HTML reports
- CSV exports
- JSON APIs
- Lifecycle and audit history retrieval

Designed for analyst review, management reporting, and audits.

---

## Security and Design Principles

- Deterministic behavior
- Explainable logic
- Least-privilege permissions
- Append-only audit logs
- Explicit feature scope
- No hidden automation

Threatly is built to reduce operational risk, not increase it.

---

## Summary

Threatly helps teams:
- Reduce threat noise
- Preserve context
- Track decisions
- Prove diligence

It is a quiet but critical layer in modern security operations.

