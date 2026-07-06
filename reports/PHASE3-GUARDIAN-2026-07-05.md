# Phase 3 GUARDIAN — SentryView Security Review

**Date:** 2026-07-05
**Analyst:** J1-PIPELINE GUARDIAN

---

## Security Posture Summary

| Category | Score | Status |
|----------|-------|--------|
| Authentication | 50/100 | DEGRADED |
| Authorization | 60/100 | DEGRADED |
| HTTPS/TLS | 0/100 | CRITICAL |
| CSP/Headers | 20/100 | CRITICAL |
| Docker Hardening | 50/100 | DEGRADED |
| Secrets Management | 30/100 | CRITICAL |
| Input Validation | 70/100 | OPERATIONAL |
| Rate Limiting | 40/100 | DEGRADED |
| Supply Chain | 50/100 | DEGRADED |
| Logging & Monitoring | 60/100 | OPERATIONAL |

**Overall Security Score: 43/100 — CRITICAL**

---

## 1. Authentication & Authorization

### JWT Implementation

| Issue | Severity | Details |
|-------|----------|---------|
| JWT stored in localStorage | **CRITICAL** | The frontend stores JWT tokens in `localStorage` (App.js:13, Login.js:21). This is vulnerable to XSS attacks — any injected script can steal the token. Should use httpOnly cookies instead. |
| JWTManager not initialized | **CRITICAL** | `flask-jwt-extended` requires `JWTManager(app)` to be called, but this is missing from `app.py`. JWT features will not work. |
| Weak JWT secret default | **HIGH** | `docker-compose.yml:35` has default `JWT_SECRET_KEY: change-this-jwt-secret`. If not overridden, tokens can be forged. |
| 24-hour token expiry | **MEDIUM** | `app.py:48` sets `JWT_ACCESS_TOKEN_EXPIRES` to 24 hours. Long-lived tokens increase the window of compromise. 1-4 hours is recommended. |
| No refresh tokens | **MEDIUM** | The system issues only access tokens with no refresh mechanism. Users must re-authenticate after 24 hours. |
| No token revocation | **MEDIUM** | There is no token blacklist or revocation mechanism. A leaked token is valid until expiry. |

### Password Security

| Issue | Severity | Details |
|-------|----------|---------|
| PBKDF2-SHA256 instead of bcrypt/argon2 | **MEDIUM** | `app.py:63-65` uses PBKDF2-SHA256 with 100,000 iterations. While not insecure, bcrypt or argon2id would provide better resistance to GPU-based attacks. |
| SECRET_KEY used as salt | **MEDIUM** | `app.py:64` uses `app.config["SECRET_KEY"]` as the password salt. If the SECRET_KEY is compromised, all password hashes are effectively unsalted. |
| Default admin credentials | **CRITICAL** | `init-db.sql:121-131` creates a default admin user. The password hash is a placeholder. The install.sh script and README both reference "admin/admin" as default credentials. |
| No account lockout | **MEDIUM** | Rate limiting on login (10/min) provides some protection, but there's no account lockout after N failed attempts. |

### Authorization

| Issue | Severity | Details |
|-------|----------|---------|
| Role-based access not enforced | **HIGH** | The database has roles (admin, user, viewer) but the backend never checks role permissions. Any authenticated user can access any endpoint. |
| No admin-only endpoints | **HIGH** | Routes like backup creation, schedule management, and user registration are accessible to any authenticated user. |
| User-scoped data only | **MEDIUM** | Streams, recordings, and events are filtered by `user_id`, so users can only see their own data. This is correct but incomplete without role enforcement. |

---

## 2. HTTPS/TLS

| Issue | Severity | Details |
|-------|----------|---------|
| No HTTPS anywhere | **CRITICAL** | The Nginx config (`nginx.conf`) listens on port 80 with no TLS configuration. All traffic is plain HTTP. |
| No TLS certificates | **CRITICAL** | No certbot, Let's Encrypt, or self-signed certificate setup. No TLS volume mounts in docker-compose.yml. |
| No HSTS header | **CRITICAL** | No `Strict-Transport-Security` header configured. |
| Credentials sent in plaintext | **CRITICAL** | Login credentials, JWT tokens, and all API data are transmitted over unencrypted HTTP. On any network (including LAN), an attacker with packet capture can steal credentials. |

**Recommendation:** Add TLS termination at the Nginx level. For self-hosted deployments, use Tailscale (which provides encrypted tunnels) or set up Let's Encrypt with certbot.

---

## 3. HTTP Security Headers

| Header | Present | Notes |
|--------|---------|-------|
| Content-Security-Policy | ❌ | Not configured. No XSS protection at the header level. |
| X-Content-Type-Options | ❌ | Not configured. |
| X-Frame-Options | ❌ | Not configured. |
| X-XSS-Protection | ❌ | Not configured. |
| Strict-Transport-Security | ❌ | Not configured (no HTTPS anyway). |
| Referrer-Policy | ❌ | Not configured. |
| Permissions-Policy | ❌ | Not configured. |

The Nginx config (`nginx.conf`) has no security headers at all. This is a significant gap for a web application.

---

## 4. Docker Hardening

| Issue | Severity | Details |
|-------|----------|---------|
| Containers run as root | **HIGH** | None of the Dockerfiles use `USER` directives. All containers run as root by default. |
| No read-only root filesystem | **HIGH** | No container uses `read_only: true` in docker-compose.yml. |
| No capability dropping | **HIGH** | No `cap_drop` directives in docker-compose.yml. Containers have full default capabilities. |
| No security_opt | **MEDIUM** | No `no-new-privileges:true` or AppArmor/SELinux profiles. |
| No resource limits | **MEDIUM** | No `mem_limit` or `cpus` constraints in docker-compose.yml. A runaway FFmpeg process could exhaust system resources. |
| No .dockerignore | **LOW** | No `.dockerignore` files, potentially sending unnecessary files to the Docker daemon. |
| Exposed ports | **MEDIUM** | Ports 3000 and 5000 are exposed to the host. In a production deployment, these should be behind a reverse proxy or Tailscale. |

---

## 5. Secrets Management

| Issue | Severity | Details |
|-------|----------|---------|
| Hardcoded secrets in source | **CRITICAL** | `Settings.js:6` contains `tailscaleApiKey: ***` — literal `***` in source code. |
| Default secrets in compose | **HIGH** | `docker-compose.yml` has default values for SECRET_KEY, JWT_SECRET_KEY, POSTGRES_PASSWORD. |
| RTSP credentials in code | **HIGH** | `ffmpeg/processor.py:16` has hardcoded `rtsp://admin:admin@192.168.1.10:554/stream`. |
| .env.sample has placeholder secrets | **MEDIUM** | `.env.sample` contains `your-secret-key-here-change-in-production` and `your-jwt-secret-key-here`. |
| No secrets scanning in CI | **MEDIUM** | CodeQL workflow does not include secret scanning. No gitleaks/trufflehog configuration. |
| Email in SECURITY.md | **LOW** | `j1admin@onebyjorah.com` is exposed in a public file. While legitimate, it may attract spam. |

---

## 6. Input Validation & Injection

| Issue | Severity | Details |
|-------|----------|---------|
| SQL injection risk | **LOW** | All database queries use parameterized queries (`%s` placeholders). Good practice. |
| No input sanitization on stream URLs | **MEDIUM** | Stream URLs are validated to start with `rtsp://` but not sanitized for injection. An attacker could inject special characters. |
| No file upload validation | **MEDIUM** | The backup endpoint writes files to disk. While it uses `pg_dump` output, the filename is constructed from user-controlled timestamp. |
| JSON parsing | **LOW** | All request bodies are parsed via `request.get_json()` which is safe. |
| No SSRF protection | **MEDIUM** | The FFmpeg processor connects to arbitrary RTSP URLs. An attacker who can add streams could use the server to probe internal networks. |

---

## 7. Rate Limiting

| Issue | Severity | Details |
|-------|----------|---------|
| Rate limiter not initialized | **CRITICAL** | `@limiter.limit()` decorators are used on all routes but `Limiter` is never instantiated. Rate limiting is completely non-functional. |
| No global rate limit | **MEDIUM** | Each endpoint has per-route limits, but there's no global rate limit per IP. |
| Health endpoint unprotected | **LOW** | `/health` has no rate limiting. |

---

## 8. Supply Chain Security

| Issue | Severity | Details |
|-------|----------|---------|
| Dependabot configured but broken | **HIGH** | Dependabot points all ecosystems to `/` directory, but requirements.txt files are in `/backend/` and `/ffmpeg/`. Dependabot will never find updates. |
| No lock files | **MEDIUM** | No `package-lock.json` or `requirements.txt` hash pins. Dependencies are not pinned to specific hashes. |
| No SBOM | **MEDIUM** | No Software Bill of Materials generated. |
| CodeQL present | ✅ | CodeQL analysis runs on push/PR to main. Covers Python, JavaScript, TypeScript. |
| No image signing | **MEDIUM** | Docker images are not signed or verified. |

---

## 9. Logging & Monitoring

| Issue | Severity | Details |
|-------|----------|---------|
| Audit logging configured | ✅ | `config.py:82` has `AUDIT_LOG_ENABLED` setting. |
| Health check endpoint | ✅ | `/health` checks both PostgreSQL and Redis. |
| No centralized logging | **MEDIUM** | Logs go to stdout and a file. No log aggregation (ELK, Loki, etc.). |
| No alerting | **MEDIUM** | No alerting on failed health checks, backup failures, or security events. |
| No failed auth tracking | **MEDIUM** | Login failures are logged but not tracked for brute force detection. |

---

## 10. Security Score Calculation

| Category | Weight | Score | Weighted |
|----------|--------|-------|----------|
| Authentication | 15% | 50 | 7.5 |
| Authorization | 10% | 60 | 6.0 |
| HTTPS/TLS | 15% | 0 | 0.0 |
| CSP/Headers | 10% | 20 | 2.0 |
| Docker Hardening | 15% | 50 | 7.5 |
| Secrets Management | 15% | 30 | 4.5 |
| Input Validation | 10% | 70 | 7.0 |
| Rate Limiting | 5% | 40 | 2.0 |
| Supply Chain | 5% | 50 | 2.5 |
| **Total** | **100%** | | **39.0** |

**Security Score: 39/100 — CRITICAL**

---

## Critical Findings (Must Fix)

| # | Finding | Location |
|---|---------|----------|
| S1 | No HTTPS/TLS — all traffic in plaintext | `nginx.conf`, `docker-compose.yml` |
| S2 | No HTTP security headers (CSP, HSTS, etc.) | `nginx.conf` |
| S3 | JWT stored in localStorage (XSS vulnerability) | `App.js`, `Login.js` |
| S4 | Rate limiter not initialized — all rate limiting is non-functional | `backend/app.py` |
| S5 | Hardcoded secrets in source code (`***` in Settings.js) | `Settings.js:6` |
| S6 | Default admin credentials with placeholder hash | `init-db.sql:121-131` |
| S7 | Containers run as root with full capabilities | All Dockerfiles, `docker-compose.yml` |
| S8 | Dependabot misconfigured — will never find updates | `.github/dependabot.yml` |

---

## Recommendations

1. **Immediate:** Add TLS termination at Nginx with Let's Encrypt or Tailscale
2. **Immediate:** Add security headers to Nginx config (CSP, HSTS, X-Frame-Options, etc.)
3. **Immediate:** Fix the missing imports in app.py (limiter, socketio, get_db, JWTManager)
4. **High priority:** Move JWT to httpOnly cookies instead of localStorage
5. **High priority:** Add `USER` directives to all Dockerfiles
6. **High priority:** Add `cap_drop: ALL` and `read_only: true` to docker-compose.yml
7. **High priority:** Fix Dependabot directory paths
8. **Medium priority:** Implement role-based access control
9. **Medium priority:** Add account lockout after failed login attempts
10. **Medium priority:** Add token revocation mechanism
