# 🔒 Security Guide for Educational Platform

## 🚨 **CRITICAL: Immediate Security Actions Required**

### 1. **Move Sensitive Data to Environment Variables**

Create a `.env` file in your Django project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Database Settings
DB_NAME=edu
DB_USER=postgres
DB_PASSWORD=your-database-password
DB_HOST=localhost
DB_PORT=5432

# Redis Cloud Settings
REDIS_URL=redis://default:huK4JsczUVa8j0CMKg52l7a0lM8DfGtL@redis-15762.c321.us-east-1-2.ec2.redns.redis-cloud.com:15762

# Cloudinary Settings
CLOUDINARY_CLOUD_NAME=ddtp8tqvv
CLOUDINARY_API_KEY=272766425297671
CLOUDINARY_API_SECRET=o44U57Jmn3Rjtz_N2SDrpS7Mow0

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id

# Security Settings
CSRF_TRUSTED_ORIGINS=https://your-domain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### 2. **Update settings.py for Security**

```python
# Security Settings
SECRET_KEY = os.getenv('SECRET_KEY', 'your-fallback-secret-key')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Database with environment variables
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'edu'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Cloudinary with environment variables
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

# Security Headers
SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'False').lower() == 'true'
SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'False').lower() == 'true'
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')

# CORS Settings (more restrictive)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://your-frontend-domain.com",
]
CORS_ALLOW_CREDENTIALS = True
```

## 🛡️ **Security Best Practices**

### 1. **Environment Variables**

- ✅ Never commit `.env` files to version control
- ✅ Use different credentials for development/production
- ✅ Rotate secrets regularly

### 2. **Database Security**

- ✅ Use strong passwords
- ✅ Enable SSL connections
- ✅ Restrict database access by IP

### 3. **Redis Security**

- ✅ Use Redis Cloud (already implemented)
- ✅ Enable Redis authentication
- ✅ Use SSL connections

### 4. **WebSocket Security**

- ✅ Validate authentication tokens
- ✅ Rate limiting on WebSocket connections
- ✅ Sanitize all incoming messages

### 5. **Frontend Security**

- ✅ HTTPS only in production
- ✅ Secure cookie settings
- ✅ Content Security Policy (CSP)

## 🔐 **Production Security Checklist**

### Before Deployment:

- [ ] Move all secrets to environment variables
- [ ] Set `DEBUG = False`
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Enable HTTPS
- [ ] Set secure cookie flags
- [ ] Configure CORS properly
- [ ] Set up proper logging
- [ ] Enable rate limiting
- [ ] Configure backup strategy

### Ongoing Security:

- [ ] Regular security updates
- [ ] Monitor for suspicious activity
- [ ] Regular secret rotation
- [ ] Security audits
- [ ] Penetration testing

## 🚨 **Current Vulnerabilities to Fix**

1. **Exposed Credentials:**

   - Redis password in settings.py
   - Cloudinary credentials in settings.py
   - Database password in settings.py

2. **Development Settings in Production:**

   - `DEBUG = True`
   - `CORS_ALLOW_ALL_ORIGINS = True`

3. **Missing Security Headers:**
   - No HTTPS enforcement
   - No secure cookie settings

## 🔧 **Quick Security Fixes**

### Immediate Actions:

1. Create `.env` file with all secrets
2. Update `settings.py` to use environment variables
3. Set `DEBUG = False` for production
4. Configure proper CORS settings
5. Enable security headers

### For Production:

1. Use HTTPS everywhere
2. Set up proper domain names
3. Configure SSL certificates
4. Set up monitoring and logging
5. Implement rate limiting

## 📞 **Security Contact**

If you discover any security vulnerabilities:

1. Don't post them publicly
2. Contact your security team
3. Follow responsible disclosure practices

---

**Remember: Security is an ongoing process, not a one-time setup!**
