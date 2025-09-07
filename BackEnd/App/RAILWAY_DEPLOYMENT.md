# Railway Deployment Guide

## Current Issue: 502 Error

The 502 error indicates that Railway cannot reach your Django application. Here are the fixes implemented:

## Changes Made

### 1. Fixed ASGI Configuration

- Updated `App/asgi.py` with better error handling and Django setup
- Added fallback to HTTP-only mode if WebSocket routing fails

### 2. Enhanced Procfile Options

- **Main Procfile**: Uses Daphne for ASGI (WebSocket support)
- **Procfile.wsgi**: Uses Gunicorn for HTTP-only (more stable)
- **Procfile.uvicorn**: Alternative ASGI server

### 3. Added Health Check Endpoints

- Root endpoint: `https://your-app.railway.app/`
- API health check: `https://your-app.railway.app/api/health/`

### 4. Added Railway Configuration

- `railway.json` with deployment settings
- Added Gunicorn to requirements.txt

## Deployment Steps

### Option 1: Try Different Procfile (Recommended)

1. In Railway dashboard, go to your project
2. Go to Settings → Environment
3. Add a new variable:
   - **Name**: `PROCFILE_PATH`
   - **Value**: `Procfile.wsgi`
4. Redeploy your application

### Option 2: Manual Procfile Switch

1. Rename current `Procfile` to `Procfile.daphne`
2. Rename `Procfile.wsgi` to `Procfile`
3. Push changes to your repository

### Option 3: Environment Variables Check

Ensure these environment variables are set in Railway:

```
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
DEBUG=False
REDIS_URL=redis://... (if using Redis)
```

## Testing Deployment

### 1. Check Health Endpoint

Visit: `https://educational-platform-production.up.railway.app/`
Should return: `{"status": "ok", "message": "Educational Platform API is running"}`

### 2. Check API Health

Visit: `https://educational-platform-production.up.railway.app/api/health/`

### 3. Test CORS

From your frontend console:

```javascript
fetch("https://educational-platform-production.up.railway.app/api/health/")
  .then((r) => r.json())
  .then(console.log);
```

## Troubleshooting

### If still getting 502:

1. Check Railway logs for specific error messages
2. Try the Gunicorn Procfile (more stable than Daphne)
3. Ensure all environment variables are properly set
4. Check if your database connection is working

### If CORS issues persist:

Your CORS settings are already correctly configured for:

- `https://eduplatformiti.netlify.app`
- All Netlify deploy previews

### Railway Logs

Check Railway deployment logs for:

- Import errors
- Database connection issues
- Missing environment variables
- Port binding issues

## Next Steps

1. Try Option 1 (change to Gunicorn via environment variable)
2. Check the health endpoints
3. Test your OAuth flow again
4. If issues persist, check Railway logs for specific error messages

## Backup WSGI-Only Configuration

If WebSocket features aren't critical, you can use the simpler WSGI setup which is more stable on Railway.
