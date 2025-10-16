# 🛡️ SECURITY POLICY

**Security Contact:** [Mustapha Fonsau](https://www.linkedin.com/in/mustapha-fonsau/) | [GitHub](https://github.com/Monsau)

## 🔒 Supported Versions

We release patches for security vulnerabilities for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

---

## 🚨 Reporting a Vulnerability

**Please DO NOT report security vulnerabilities through public GitHub issues.**

### Preferred Method

Please report security vulnerabilities by emailing:

**mfonsau@talentys.eu** or contact via [LinkedIn](https://www.linkedin.com/in/mustapha-fonsau/)

### What to Include

Please include the following information in your report:

1. **Description** of the vulnerability
2. **Steps to reproduce** the issue
3. **Potential impact** of the vulnerability
4. **Suggested fix** (if you have one)
5. **Your contact information** for follow-up

### Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 7 days
- **Patch Development**: Depends on severity (High: 7-14 days, Medium: 14-30 days, Low: 30-60 days)
- **Public Disclosure**: After patch is released and users have had time to update

---

## 🔐 Security Best Practices

### For Users

#### 1. Credentials Management

**❌ NEVER do this:**
```bash
# DON'T commit credentials to git
POSTGRES_PASSWORD=mypassword123
DREMIO_ADMIN_PASSWORD=admin123
```

**✅ DO this instead:**
```bash
# Use .env file (which is gitignored)
POSTGRES_PASSWORD=${SECURE_POSTGRES_PASSWORD}
DREMIO_ADMIN_PASSWORD=${SECURE_DREMIO_PASSWORD}
```

#### 2. Generate Strong Passwords

```bash
# Generate secure password (32 characters)
openssl rand -base64 32

# Generate secret key for JWT
openssl rand -base64 42
```

#### 3. Environment Variables

Always use `.env` file for sensitive configuration:

```bash
# Copy example and customize
cp .env.example .env

# Edit with strong passwords
nano .env

# Verify .env is in .gitignore
git check-ignore .env
```

#### 4. Docker Security

```yaml
# Use secrets instead of environment variables
services:
  postgres:
    secrets:
      - postgres_password
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/postgres_password

secrets:
  postgres_password:
    file: ./secrets/postgres_password.txt
```

#### 5. Network Security

```yaml
# Expose only necessary ports
ports:
  - "127.0.0.1:9047:9047"  # Bind to localhost only
  # NOT: - "9047:9047"      # Exposed to all interfaces
```

---

## 🔍 Known Security Considerations

### PostgreSQL Wire Protocol (Port 31010)

**Issue**: Dremio's PostgreSQL Wire Protocol uses PostgreSQL authentication.

**Mitigation**:
- Use strong passwords
- Restrict network access
- Enable SSL/TLS in production
- Use firewall rules

### Arrow Flight (Port 32010)

**Issue**: Arrow Flight endpoint requires authentication.

**Mitigation**:
- Use Dremio authentication tokens
- Enable TLS for Flight
- Restrict to trusted networks

### OpenMetadata JWT Token

**Issue**: JWT tokens have long expiration times.

**Mitigation**:
- Rotate tokens regularly
- Use short-lived tokens
- Store tokens securely (never commit to git)

### MinIO Access Keys

**Issue**: S3-compatible storage requires access keys.

**Mitigation**:
- Use IAM policies
- Rotate keys regularly
- Use temporary credentials when possible

---

## 🛠️ Security Scanning

### Pre-commit Checks

```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Scan for secrets
pip install detect-secrets
detect-secrets scan > .secrets.baseline

# Scan for vulnerabilities
pip install safety
safety check
```

### Docker Image Scanning

```bash
# Scan Docker images
docker scan dremio:latest
docker scan openmetadata:latest

# Use Trivy
trivy image dremio:latest
```

### Dependency Scanning

```bash
# Python dependencies
pip install pip-audit
pip-audit

# Check for outdated packages
pip list --outdated
```

---

## 📋 Security Checklist

### Before Deployment

- [ ] All passwords changed from defaults
- [ ] `.env` file contains no real credentials
- [ ] SSL/TLS enabled for all services
- [ ] Network ports restricted (firewall rules)
- [ ] Docker images from trusted sources
- [ ] Dependencies updated to latest secure versions
- [ ] Backup strategy in place
- [ ] Monitoring and alerting configured
- [ ] Secrets stored in secure vault (not in git)
- [ ] Access logs enabled

### Production Hardening

- [ ] Use Docker secrets instead of environment variables
- [ ] Enable audit logging
- [ ] Implement rate limiting
- [ ] Use reverse proxy (Nginx/Traefik)
- [ ] Enable HTTPS only
- [ ] Disable unnecessary ports
- [ ] Regular security updates
- [ ] Backup encryption
- [ ] Network segmentation
- [ ] Least privilege access

---

## 🔗 Resources

### Official Documentation

- [Dremio Security](https://docs.dremio.com/security/)
- [OpenMetadata Security](https://docs.open-metadata.org/deployment/security)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html)
- [MinIO Security](https://min.io/docs/minio/linux/administration/identity-access-management.html)

### Security Tools

- [OWASP ZAP](https://www.zaproxy.org/) - Web application security scanner
- [Trivy](https://github.com/aquasecurity/trivy) - Container vulnerability scanner
- [detect-secrets](https://github.com/Yelp/detect-secrets) - Secret detection
- [git-secrets](https://github.com/awslabs/git-secrets) - Prevent committing secrets

### Standards

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

---

## 📞 Contact

For security concerns, please contact:

- **Email**: security@yourproject.com (**⚠️ REMPLACER**)
- **PGP Key**: [Link to public key] (**⚠️ AJOUTER SI DISPONIBLE**)

---

## 📜 Disclosure Policy

We follow **Responsible Disclosure**:

1. Reporter contacts us privately
2. We confirm and assess the vulnerability
3. We develop and test a fix
4. We release a patch
5. We publicly disclose the vulnerability (after users have time to update)

**Timeline**: Typically 90 days from initial report to public disclosure.

---

**Last Updated**: October 16, 2025  
**Version**: 1.0
