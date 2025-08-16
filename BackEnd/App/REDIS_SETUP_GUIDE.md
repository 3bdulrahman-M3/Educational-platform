# Redis Setup Guide for Live Sessions

## Overview
Redis is required for the WebSocket functionality in live sessions. It acts as a channel layer for Django Channels, enabling real-time communication between participants.

## Option 1: Local Redis Installation (Recommended for Development)

### Windows Installation

1. **Download Redis for Windows:**
   - Visit: https://github.com/microsoftarchive/redis/releases
   - Download the latest MSI installer (e.g., `Redis-x64-3.0.504.msi`)
   - Run the installer and follow the setup wizard

2. **Start Redis Service:**
   ```powershell
   # Start Redis service
   net start Redis
   
   # Or start manually
   redis-server
   ```

3. **Test Redis Connection:**
   ```powershell
   redis-cli ping
   # Should return: PONG
   ```

### macOS Installation

1. **Using Homebrew:**
   ```bash
   brew install redis
   brew services start redis
   ```

2. **Test Connection:**
   ```bash
   redis-cli ping
   # Should return: PONG
   ```

### Linux Installation

1. **Ubuntu/Debian:**
   ```bash
   sudo apt update
   sudo apt install redis-server
   sudo systemctl start redis-server
   sudo systemctl enable redis-server
   ```

2. **Test Connection:**
   ```bash
   redis-cli ping
   # Should return: PONG
   ```

## Option 2: Cloud Redis Service (Recommended for Production)

### Redis Cloud (Redis Labs)
1. Sign up at: https://redis.com/try-free/
2. Create a new database
3. Get your connection details
4. Set environment variable:
   ```bash
   REDIS_URL=redis://username:password@host:port/database
   ```

### Upstash Redis
1. Sign up at: https://upstash.com/
2. Create a new Redis database
3. Get your connection URL
4. Set environment variable:
   ```bash
   REDIS_URL=redis://username:password@host:port/database
   ```

## Environment Configuration

Create or update your `.env` file in the Django project root:

```env
# Local Redis (default)
REDIS_URL=redis://127.0.0.1:6379/0

# Or for cloud Redis
# REDIS_URL=redis://username:password@host:port/database
```

## Testing Redis Connection

### 1. Test Redis CLI
```bash
redis-cli ping
# Should return: PONG
```

### 2. Test Django Redis Connection
```python
# In Django shell
python manage.py shell

# Test Redis connection
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

channel_layer = get_channel_layer()
async_to_sync(channel_layer.group_add)("test_group", "test_channel")
print("Redis connection successful!")
```

### 3. Test WebSocket Connection
1. Start Django server: `python manage.py runserver`
2. Open browser console and test WebSocket:
   ```javascript
   const ws = new WebSocket('ws://localhost:8000/ws/sessions/1/');
   ws.onopen = () => console.log('WebSocket connected!');
   ws.onmessage = (event) => console.log('Message:', event.data);
   ```

## Troubleshooting

### Common Issues

1. **Redis Connection Refused:**
   - Make sure Redis is running: `redis-cli ping`
   - Check if Redis service is started
   - Verify port 6379 is not blocked by firewall

2. **Django Channels Error:**
   - Install required packages: `pip install channels-redis redis`
   - Check Redis URL format in settings
   - Verify Redis is accessible from Django

3. **WebSocket Connection Failed:**
   - Check if Django server is running with ASGI
   - Verify WebSocket URL format
   - Check browser console for errors

### Debug Commands

```bash
# Check Redis status
redis-cli ping

# Check Redis info
redis-cli info

# Monitor Redis commands
redis-cli monitor

# Check Django channels
python manage.py shell
from channels.layers import get_channel_layer
channel_layer = get_channel_layer()
print(channel_layer)
```

## Production Considerations

1. **Security:**
   - Use strong Redis passwords
   - Enable Redis authentication
   - Use SSL/TLS for cloud Redis

2. **Performance:**
   - Configure Redis memory limits
   - Set appropriate TTL for keys
   - Monitor Redis memory usage

3. **Scalability:**
   - Consider Redis Cluster for high traffic
   - Use Redis Sentinel for high availability
   - Implement proper connection pooling

## Quick Start for Development

1. **Install Redis locally**
2. **Start Redis service**
3. **Set environment variable:**
   ```bash
   export REDIS_URL=redis://127.0.0.1:6379/0
   ```
4. **Start Django server:**
   ```bash
   python manage.py runserver
   ```
5. **Test live session functionality**

## Support

If you encounter issues:
1. Check Redis logs: `redis-cli monitor`
2. Check Django logs for channel layer errors
3. Verify Redis connection in Django shell
4. Test WebSocket connection manually
