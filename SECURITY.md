# Security Guide for Toolbox.io

## 🛡️ Security Features Implemented

### 1. **Authentication & Authorization**
- ✅ JWT-based authentication with bcrypt password hashing
- ✅ Strong password policy (min 10 chars, complexity requirements)
- ✅ Rate limiting on login/register endpoints
- ✅ Input validation and sanitization
- ✅ CORS protection

### 2. **Transport Security**
- ✅ HTTPS enforcement via Caddy
- ✅ Security headers (HSTS, CSP, X-Frame-Options, etc.)
- ✅ Certificate management

### 3. **Application Security**
- ✅ Input validation on all endpoints
- ✅ SQL injection protection via SQLAlchemy ORM
- ✅ XSS protection via Content Security Policy
- ✅ CSRF protection via CORS restrictions

### 4. **Infrastructure Security**
- ✅ Non-root user in Docker container
- ✅ Minimal package installation
- ✅ Security updates in Dockerfile
- ✅ Proper file permissions

## 🔧 Security Configuration

### Environment Variables (Required)
```bash
# Generate a strong secret key
SECRET_KEY=your-super-secure-256-bit-random-key-change-this-in-production

# Database configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=toolbox_db
DB_USER=toolbox_user
DB_PASSWORD=strong-database-password

# Server configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

### Rate Limiting
- Login: 5 attempts per minute per IP
- Register: 3 attempts per minute per IP
- Password change: 3 attempts per minute per user

### Password Policy
- Minimum length: 10 characters
- Maximum length: 128 characters
- Must contain: uppercase, lowercase, digit, special character
- No repeated characters (more than 2 in a row)
- No sequential characters
- No common passwords

### CORS Configuration
- Allowed origins: `https://server.toolbox-io.ru`, `http://server.toolbox-io.ru`
- Development: `http://localhost:3000`, `http://localhost:8000`

## 🚨 Critical Security Checklist

### Before Production Deployment
- [ ] Set strong `SECRET_KEY` environment variable
- [ ] Change default database passwords
- [ ] Enable HTTPS with valid certificates
- [ ] Configure firewall rules
- [ ] Set up monitoring and logging
- [ ] Test all security features
- [ ] Review and update dependencies

### Ongoing Security
- [ ] Regular security updates
- [ ] Monitor logs for suspicious activity
- [ ] Regular backup testing
- [ ] Security audits
- [ ] Dependency vulnerability scanning

## 🔍 Security Monitoring

### Logs to Monitor
- Failed login attempts
- Rate limit violations
- Password change attempts
- Account deletion requests
- Unusual API usage patterns

### Alerts to Set Up
- Multiple failed login attempts from same IP
- Unusual traffic patterns
- Database connection errors
- Certificate expiration warnings

## 🛠️ Security Tools

### Recommended Tools
- **Dependency Scanning**: `safety check` (Python)
- **Container Scanning**: `trivy` or `snyk`
- **SSL Testing**: `testssl.sh`
- **Security Headers**: `securityheaders.com`

### Commands
```bash
# Check Python dependencies
pip install safety
safety check

# Test SSL configuration
curl -sSfL https://testssl.sh/testssl.sh | bash -s -- server.toolbox-io.ru

# Check security headers
curl -I https://server.toolbox-io.ru
```

## 🚨 Incident Response

### If Compromised
1. **Immediate Actions**
   - Disconnect from network
   - Preserve evidence
   - Change all passwords
   - Revoke all tokens

2. **Investigation**
   - Review logs
   - Identify attack vector
   - Assess damage
   - Document findings

3. **Recovery**
   - Patch vulnerabilities
   - Restore from clean backup
   - Implement additional security
   - Monitor for re-compromise

## 📞 Security Contact

For security issues, please contact:
- Email: security@toolbox-io.ru
- Response time: 24 hours
- Please include detailed information about the vulnerability

## 📚 Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Caddy Security](https://caddy.community/t/security-headers/1080)
- [Docker Security](https://docs.docker.com/engine/security/)
