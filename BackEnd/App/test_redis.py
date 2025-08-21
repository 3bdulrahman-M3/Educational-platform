#!/usr/bin/env python
"""
Test Redis Cloud connection for WebSocket support
"""
import redis
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_redis_connection():
    try:
        # Get Redis credentials from environment variables
        redis_host = os.environ.get(
            'REDIS_HOST', 'redis-15762.c321.us-east-1-2.ec2.redns.redis-cloud.com')
        redis_port = int(os.environ.get('REDIS_PORT', 15762))
        redis_username = os.environ.get('REDIS_USERNAME', 'default')
        redis_password = os.environ.get('REDIS_PASSWORD', '')

        if not redis_password:
            print("❌ REDIS_PASSWORD environment variable is not set!")
            print("Please add REDIS_PASSWORD to your .env file")
            return False

        # Try to connect to Redis Cloud
        r = redis.Redis(
            host=redis_host,
            port=redis_port,
            decode_responses=True,
            username=redis_username,
            password=redis_password,
        )

        # Test basic operations
        r.set('test_key', 'test_value')
        value = r.get('test_key')
        r.delete('test_key')

        if value == 'test_value':
            print("✅ Redis Cloud connection successful!")
            print("✅ Basic operations working correctly")
            print(f"✅ Connected to: {redis_host}:{redis_port}")
            return True
        else:
            print("❌ Redis test failed - value mismatch")
            return False

    except redis.ConnectionError:
        print("❌ Redis Cloud connection failed!")
        print("Please check your Redis Cloud credentials and network connection")
        return False
    except Exception as e:
        print(f"❌ Redis test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_redis_connection()
    sys.exit(0 if success else 1)
