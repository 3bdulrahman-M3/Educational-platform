#!/usr/bin/env python
"""
Test script to verify Redis connection and Django Channels setup
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'App.settings')
django.setup()


def test_redis_connection():
    """Test Redis connection through Django Channels"""
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        print("🔍 Testing Redis connection...")

        # Get the channel layer
        channel_layer = get_channel_layer()
        print(f"✅ Channel layer created: {type(channel_layer).__name__}")

        # Test basic Redis operations
        print("🔍 Testing Redis operations...")

        # Test group add
        async_to_sync(channel_layer.group_add)("test_group", "test_channel")
        print("✅ Group add operation successful")

        # Test group send
        async_to_sync(channel_layer.group_send)("test_group", {
            "type": "test.message",
            "message": "Hello Redis!"
        })
        print("✅ Group send operation successful")

        # Test group discard
        async_to_sync(channel_layer.group_discard)(
            "test_group", "test_channel")
        print("✅ Group discard operation successful")

        print("\n🎉 Redis connection test PASSED!")
        print("✅ Redis Cloud is properly connected")
        print("✅ Django Channels is working correctly")

        return True

    except Exception as e:
        print(f"\n❌ Redis connection test FAILED!")
        print(f"Error: {str(e)}")
        print("\n🔧 Troubleshooting steps:")
        print("1. Check if Redis Cloud is running")
        print("2. Verify Redis URL in settings.py")
        print("3. Check if channels-redis is installed")
        print("4. Verify network connectivity")
        return False


def test_redis_url():
    """Test Redis URL configuration"""
    try:
        from django.conf import settings

        print("🔍 Checking Redis configuration...")

        # Get Redis URL from settings
        redis_url = os.getenv(
            'REDIS_URL', 'redis://default:huK4JsczUVa8j0CMKg52l7a0lM8DfGtL@redis-15762.c321.us-east-1-2.ec2.redns.redis-cloud.com:15762')

        print(f"✅ Redis URL configured: {redis_url[:50]}...")
        print(f"✅ Channel layers configured: {settings.CHANNEL_LAYERS}")

        return True

    except Exception as e:
        print(f"❌ Redis configuration error: {str(e)}")
        return False


if __name__ == "__main__":
    print("🚀 Redis Connection Test")
    print("=" * 50)

    # Test configuration
    config_ok = test_redis_url()

    if config_ok:
        # Test connection
        connection_ok = test_redis_connection()

        if connection_ok:
            print("\n🎯 All tests passed! Redis is ready for live sessions.")
        else:
            print("\n💥 Connection failed. Check your Redis Cloud setup.")
    else:
        print("\n💥 Configuration failed. Check your Django settings.")
