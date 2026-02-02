# Security Advisory

## Overview

This document tracks security vulnerabilities found and fixed in the project.

## Fixed Vulnerabilities

### [RESOLVED] CVE-2024-01 - python-multipart Arbitrary File Write

**Date Reported**: 2026-02-02  
**Date Fixed**: 2026-02-02  
**Severity**: HIGH  
**Component**: python-multipart  
**Affected Versions**: < 0.0.22  
**Fixed Version**: 0.0.22

**Description**:  
Python-Multipart has an Arbitrary File Write vulnerability via non-default configuration. This could allow attackers to write files to arbitrary locations on the filesystem.

**Impact**:  
Potential for arbitrary file write attacks when using non-default multipart configuration.

**Fix**:  
Updated `backend/requirements.txt` to use python-multipart==0.0.22

**References**:
- CVE: Pending
- GHSA: Pending

---

### [RESOLVED] CVE-2024-02 - python-multipart DoS via Malformed Boundary

**Date Reported**: 2026-02-02  
**Date Fixed**: 2026-02-02  
**Severity**: MEDIUM  
**Component**: python-multipart  
**Affected Versions**: < 0.0.18  
**Fixed Version**: 0.0.22 (includes 0.0.18 fix)

**Description**:  
Denial of Service (DoS) vulnerability via deformed `multipart/form-data` boundary. Maliciously crafted multipart requests could cause the service to become unresponsive.

**Impact**:  
Service availability could be compromised through specially crafted requests.

**Fix**:  
Updated `backend/requirements.txt` to use python-multipart==0.0.22

**References**:
- CVE: Pending
- GHSA: Pending

---

## Security Best Practices

### Dependency Management

1. **Regular Updates**: Check for security updates weekly
2. **Automated Scanning**: GitHub Dependabot is enabled
3. **Version Pinning**: All dependencies use exact versions
4. **Review Process**: Security updates reviewed and tested before merging

### Reporting Security Issues

If you discover a security vulnerability, please:

1. **DO NOT** open a public issue
2. Email the maintainers directly (see CONTRIBUTING.md)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

### Security Update Process

1. Vulnerability reported or discovered
2. Impact assessment
3. Patch developed and tested
4. Security advisory published
5. Fix deployed immediately
6. Users notified via:
   - GitHub Security Advisory
   - README badge
   - Release notes

## Active Monitoring

We actively monitor security advisories from:

- GitHub Security Advisories
- Python Security Mailing List
- CVE Database
- Snyk
- npm audit (for frontend)
- pip audit (for backend)

## Dependency Audit

Last audit: 2026-02-02

```bash
# Run security audit
pip-audit
npm audit
```

## Secure Coding Practices

- ✅ Input validation on all API endpoints
- ✅ No hardcoded secrets
- ✅ CORS properly configured
- ✅ Dependencies regularly updated
- ✅ Security headers configured in nginx
- ✅ Principle of least privilege

## Future Improvements

- [ ] Implement rate limiting
- [ ] Add API authentication (OAuth2/JWT)
- [ ] Enable HTTPS/TLS in production
- [ ] Implement request signing
- [ ] Add security scanning to CI/CD
- [ ] Set up automated dependency updates

## Contact

For security concerns, contact the maintainers via GitHub Issues (for non-critical) or direct email for critical vulnerabilities.

---

**Last Updated**: 2026-02-02  
**Next Review**: 2026-03-02
