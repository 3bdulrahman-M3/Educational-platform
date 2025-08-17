import os
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.conf import settings
from django.core.exceptions import ValidationError


def verify_google_token(token):
    """
    Verify Google ID token and return user info
    """
    try:
        # Get Google Client ID from environment
        google_client_id = os.getenv('GOOGLE_CLIENT_ID')
        if not google_client_id:
            raise ValidationError("Google Client ID not configured")

        # Verify the token with clock skew tolerance
        idinfo = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            google_client_id,
            clock_skew_in_seconds=10  # Allow 10 seconds of clock skew
        )

        # Extract user information
        google_id = idinfo['sub']
        email = idinfo['email']
        first_name = idinfo.get('given_name', '')
        last_name = idinfo.get('family_name', '')

        return {
            'google_id': google_id,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'email_verified': idinfo.get('email_verified', False)
        }

    except ValueError as e:
        raise ValidationError(f"Invalid Google token: {str(e)}")
    except Exception as e:
        raise ValidationError(f"Error verifying Google token: {str(e)}")


def get_google_user_info(access_token):
    """
    Get user info from Google using access token (alternative method)
    """
    try:
        url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        user_info = response.json()

        return {
            'google_id': user_info['id'],
            'email': user_info['email'],
            'first_name': user_info.get('given_name', ''),
            'last_name': user_info.get('family_name', ''),
            'email_verified': user_info.get('verified_email', False)
        }

    except requests.RequestException as e:
        raise ValidationError(
            f"Error fetching user info from Google: {str(e)}")
    except Exception as e:
        raise ValidationError(f"Error processing Google user info: {str(e)}")
