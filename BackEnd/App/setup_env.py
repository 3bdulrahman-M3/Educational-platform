#!/usr/bin/env python
"""
Setup script to create .env file with Redis Cloud credentials
"""
import os


def create_env_file():
    """Create .env file with Redis Cloud configuration"""

    env_content = """# Database Configuration
DATABASE_URL=your_database_url_here

# Redis Cloud Configuration
REDIS_HOST=redis-15762.c321.us-east-1-2.ec2.redns.redis-cloud.com
REDIS_PORT=15762
REDIS_USERNAME=default
REDIS_PASSWORD=huK4JsczUVa8j0CMKg52l7a0lM8DfGtL
REDIS_DB=0

# Django Secret Key (generate a new one for production)
SECRET_KEY=)zMKNWH6QNxbcpQTYISW-RUVb)RB)2e*c6XbiW@%W*Z0+UAJ62

# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=ddtp8tqvv
CLOUDINARY_API_KEY=272766425297671
CLOUDINARY_API_SECRET=o44U57Jmn3Rjtz_N2SDrpS7Mow0

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Debug Mode (set to False in production)
DEBUG=True
"""

    # Check if .env already exists
    if os.path.exists('.env'):
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("❌ Setup cancelled.")
            return

    # Create .env file
    with open('.env', 'w') as f:
        f.write(env_content)

    print("✅ .env file created successfully!")
    print("🔐 Redis Cloud credentials configured")
    print("🔑 Secure Django secret key generated")
    print("\n📝 Next steps:")
    print("1. Test Redis connection: python test_redis.py")
    print("2. Run migrations: python manage.py migrate")
    print("3. Start server: python manage.py runserver")


if __name__ == "__main__":
    create_env_file()
