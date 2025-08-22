# Google OAuth2 Implementation

This OAuth2 app provides Google authentication for your Django backend without requiring any new database models. It works with your existing User model.

## Setup

1. **Environment Variables**: Add these to your `.env` file:
   ```
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   ```

2. **Google Console Setup**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google+ API
   - Create OAuth 2.0 credentials
   - Add authorized redirect URIs:
     - `http://localhost:5173/auth/callback` (for development)
     - `http://localhost:8000/api/oauth2/google/callback/` (for testing)

## API Endpoints

### 1. Get Google Auth URL
**GET** `/api/oauth2/google/auth-url/`

**Query Parameters**:
- `redirect_uri` (optional): Custom redirect URI (defaults to `http://localhost:5173/auth/callback`)

**Response**:
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?..."
}
```

### 2. Google Auth Callback
**POST** `/api/oauth2/google/callback/`

**Request Body**:
```json
{
  "code": "authorization_code_from_google",
  "redirect_uri": "http://localhost:5173/auth/callback"
}
```

**Response**:
```json
{
  "access_token": "jwt_access_token",
  "refresh_token": "jwt_refresh_token",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student",
    "date_joined": "2024-01-01T00:00:00Z",
    "is_active": true
  },
  "google_id": "google_user_id",
  "picture": "https://lh3.googleusercontent.com/...",
  "locale": "en",
  "verified_email": true
}
```

## Frontend Integration (Vite/React)

1. **Redirect to Google**:
```javascript
const getGoogleAuthUrl = async () => {
  const response = await fetch('/api/oauth2/google/auth-url/?redirect_uri=http://localhost:5173/auth/callback');
  const data = await response.json();
  window.location.href = data.auth_url;
};
```

2. **Handle Callback**:
```javascript
const handleGoogleCallback = async (code) => {
  const response = await fetch('/api/oauth2/google/callback/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      code: code,
      redirect_uri: 'http://localhost:5173/auth/callback'
    })
  });
  
  const data = await response.json();
  // Store tokens and user data
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
  localStorage.setItem('user', JSON.stringify(data.user));
};
```

## Features

- ✅ No new database models required
- ✅ Uses existing User model
- ✅ JWT token authentication
- ✅ Automatic user creation/update
- ✅ Google profile information included
- ✅ CORS enabled for frontend integration
- ✅ Works with Vite development server (port 5173)

## Error Handling

The API returns appropriate HTTP status codes and error messages:
- `400 Bad Request`: Invalid request data
- `500 Internal Server Error`: Google API errors or configuration issues
