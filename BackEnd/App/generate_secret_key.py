#!/usr/bin/env python
"""
Generate a secure Django secret key for production use
"""
import secrets
import string


def generate_secret_key(length=50):
    """Generate a secure secret key"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"
    return ''.join(secrets.choice(alphabet) for _ in range(length))


if __name__ == "__main__":
    secret_key = generate_secret_key()
    print("🔐 Generated Secure Django Secret Key:")
    print(f"SECRET_KEY={secret_key}")
    print("\n📝 Copy this to your .env file:")
    print(f"SECRET_KEY={secret_key}")
    print("\n⚠️  Keep this secret and never commit it to version control!")
