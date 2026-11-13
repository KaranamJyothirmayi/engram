# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| 0.1.x (latest) | ✅ |

---

## Reporting a Vulnerability

**Please do NOT open a public GitHub issue for security vulnerabilities.** Doing so exposes all users to the risk before a fix is available.

### Option 1 — GitHub Private Vulnerability Reporting (Preferred)

Use GitHub's built-in private reporting:

1. Go to the [Security tab](https://github.com/KaranamJyothirmayi/engram/security) of this repository.
2. Click **"Report a vulnerability"**.
3. Fill in the advisory form — describe the issue, affected versions, and steps to reproduce.
4. Submit. Only the maintainers can see this report.

This is the fastest path: maintainers are notified immediately and can start a coordinated disclosure timeline.

### Option 2 — Email

If you prefer email, send details to the maintainer via the contact on their [GitHub profile](https://github.com/KaranamJyothirmayi). Include:

- A description of the vulnerability
- Steps to reproduce it
- The potential impact
- Any suggested fix (optional)

Please use the subject line: `[engram] Security Vulnerability Report`

---

## What to Include in Your Report

A good security report answers these questions:

- **What** is the vulnerability? (e.g. path traversal, arbitrary code execution, data leakage)
- **Where** in the code is it? (file, function, line number if possible)
- **How** can it be exploited? (minimal proof-of-concept steps)
- **Impact** — who is affected and under what conditions?
- **Version** — which version(s) are affected?

---

## Disclosure Process

1. You report the vulnerability privately.
2. Maintainers acknowledge within **72 hours**.
3. Maintainers investigate and develop a fix — target **14 days** for critical issues.
4. A patched release is published.
5. A GitHub Security Advisory is published crediting you (unless you prefer to remain anonymous).

---

## Out of Scope

The following are **not** considered security vulnerabilities for this project:

- Vulnerabilities in dependencies (report those to the upstream project; we track them with `pip-audit`)
- Issues that require physical access to the machine
- Social engineering attacks
- Denial-of-service via extremely large inputs (engram is a developer library, not a public service)

---

## Thank You

Responsible disclosure keeps the community safe. We appreciate reporters who follow this process and will credit you in the security advisory.
