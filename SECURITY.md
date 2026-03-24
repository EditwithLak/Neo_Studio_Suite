# Security Policy

## Supported Versions

Neo Studio Suite is currently in its early public release stage.

Security updates are provided for the latest maintained release branch only.

| Version | Supported |
| ------- | --------- |
| 1.x     | :white_check_mark: |
| < 1.0   | :x: |

If a serious security issue is found, fixes will be made in the current supported version. Older versions, archived builds, forks, and modified local installs may not receive patches.

---

## Reporting a Vulnerability

Please **do not report security vulnerabilities through public GitHub issues, discussions, or pull requests**.

Instead, report them privately using one of the following methods:

1. **GitHub Private Vulnerability Reporting** for this repository, if enabled.
2. If private reporting is not available, contact the maintainer directly at: **[replace-with-your-security-contact-email]**

---

## What to include in a report

To help reproduce and verify the issue, please include as much of the following as possible:

- affected version
- affected component or file
- steps to reproduce
- proof of concept, if safe to share
- expected behavior
- actual behavior
- screenshots or logs, if relevant
- whether the issue depends on a specific OS, Python version, backend, model, or optional dependency

Please keep reports focused and practical. The clearer the report, the faster it can be reviewed.

---

## What to expect after reporting

Once a valid report is received:

- acknowledgment will usually be sent within **5 business days**
- status updates will usually be provided within **7 business days** when there is meaningful progress
- the report will be reviewed, reproduced, and assessed for severity and impact
- if accepted, a fix or mitigation will be prepared for the current supported version
- if declined, a reason will be shared when possible

Not every bug is a security vulnerability. Reports may be declined if they are:

- not reproducible
- already known
- configuration mistakes
- dependency issues outside the project scope with no practical project-side fix
- low-risk behavior that does not create a real security impact

---

## Scope notes

Neo Studio Suite is a **local-first workflow system**, so security issues are typically most relevant when they involve things like:

- unsafe file handling
- path traversal
- unintended file overwrite or data exposure
- insecure import/export behavior
- unsafe backend communication
- execution of untrusted input
- dependency-related vulnerabilities with real impact on supported workflows

Model quality issues, bad generations, prompt failures, or normal application bugs are usually **not** security issues unless they create a real security risk.

---

## Disclosure policy

Please allow reasonable time for investigation and remediation before making any vulnerability public.

Once an issue is confirmed and fixed, the maintainer may choose to publish a summary, patch note, or advisory.

---

## Final note

Good-faith security research is appreciated.

Please report responsibly, avoid public disclosure before review, and do not access, modify, or destroy data that does not belong to you.
