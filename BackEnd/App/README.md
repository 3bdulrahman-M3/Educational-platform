# Educational Platform API

A Django REST API for an educational platform with Google OAuth authentication, exam management, and course enrollment features.

## Features

- **Authentication System**

  - Traditional email/password registration and login
  - Google OAuth 2.0 authentication
  - JWT token-based authentication
  - Role-based access control (Student, Instructor, Admin)

- **Exam Management**

  - Create and manage exams
  - Add questions to exams
  - Multiple question types (Multiple Choice, True/False, Essay, Short Answer)
  - Question search and filtering

- **Course Management**
  - Course creation and enrollment
  - Student-instructor relationships

## Setup Instructions

### Prerequisites

- Python 3.8+
- PostgreSQL database
- Google OAuth 2.0 credentials

### 1. Environment Setup

Create a virtual environment and install dependencies:

```bash
# Create virtual environment
python -m venv myenv

# Activate virtual environment
# Windows:
myenv\Scripts\activate
# macOS/Linux:
source myenv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

1. Create a PostgreSQL database
2. Update database settings in `App/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_database_name',
        'USER': 'your_database_user',
        'PASSWORD': 'your_database_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 3. Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
5. Configure OAuth consent screen
6. Add authorized JavaScript origins:
   - `http://localhost:3000` (for development)
   - Your production domain
7. Add authorized redirect URIs:
   - `http://localhost:3000/auth/google/callback`
   - Your production callback URL
8. Copy the Client ID

### 4. Environment Variables

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your_django_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id

# JWT Settings
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ACCESS_TOKEN_LIFETIME=5
JWT_REFRESH_TOKEN_LIFETIME=1
```

### 5. Database Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

### 6. Run the Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication Endpoints

#### Traditional Authentication

- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/user/` - Get current user info
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/update/` - Update user profile
- `PUT /api/auth/role/update/` - Update user role

#### Google OAuth Authentication

- `POST /api/auth/google/` - Google OAuth login
- `POST /api/auth/google/complete/` - Complete Google OAuth registration

#### Token Management

- `POST /api/auth/token/refresh/` - Refresh JWT token

### Exam Endpoints

#### Questions

- `GET /api/exams/questions/` - List all questions
- `POST /api/exams/questions/` - Create new question
- `GET /api/exams/questions/<id>/` - Get question details
- `PUT /api/exams/questions/<id>/` - Update question
- `DELETE /api/exams/questions/<id>/` - Delete question
- `GET /api/exams/questions/by_type/` - Filter questions by type
- `GET /api/exams/questions/search/` - Search questions

#### Exams

- `GET /api/exams/exams/` - List all exams
- `POST /api/exams/exams/` - Create new exam
- `GET /api/exams/exams/<id>/` - Get exam details
- `PUT /api/exams/exams/<id>/` - Update exam
- `DELETE /api/exams/exams/<id>/` - Delete exam
- `GET /api/exams/exams/<id>/questions/` - Get exam questions
- `POST /api/exams/exams/<id>/add_question/` - Add question to exam
- `POST /api/exams/exams/<id>/remove_question/` - Remove question from exam

## Google OAuth Flow

### 1. Initial Google Login

**Request:**

```bash
POST /api/auth/google/
Content-Type: application/json

{
  "token": "google_id_token_from_frontend"
}
```

**Response (New User):**

```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student",
    "google_id": "google_user_id"
  },
  "tokens": {
    "access": "access_token",
    "refresh": "refresh_token"
  },
  "isNewUser": true
}
```

**Response (Existing User):**

```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "instructor",
    "google_id": "google_user_id"
  },
  "tokens": {
    "access": "access_token",
    "refresh": "refresh_token"
  },
  "isNewUser": false
}
```

### 2. Complete Registration (for new users)

**Request:**

```bash
POST /api/auth/google/complete/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "google_id": "google_user_id",
  "role": "student"
}
```

**Response:**

```json
{
  "message": "Profile completed successfully",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student",
    "google_id": "google_user_id"
  },
  "tokens": {
    "access": "new_access_token",
    "refresh": "new_refresh_token"
  }
}
```

## Role Management

### Updating User Roles

Users can update their roles after registration using two methods:

#### 1. Dedicated Role Update Endpoint

```bash
PUT /api/auth/role/update/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "role": "instructor"
}
```

**Response:**

```json
{
  "message": "Role updated successfully from student to instructor",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "instructor",
    "google_id": null,
    "date_joined": "2024-01-01T00:00:00Z"
  },
  "tokens": {
    "access": "new_access_token",
    "refresh": "new_refresh_token"
  }
}
```

#### 2. Profile Update with Role Change

```bash
PUT /api/auth/profile/update/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "first_name": "Updated",
  "last_name": "Name",
  "role": "admin"
}
```

**Features:**

- New JWT tokens are generated when role changes
- Role validation ensures only valid roles are accepted
- Authentication is required for role updates
- Role changes are logged in the response message

**Valid Roles:**

- `student` - Default role for new users
- `instructor` - For teachers and course creators
- `admin` - For system administrators

## Testing the API

### Using cURL

1. **Register a new user:**

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpass123",
    "confirm_password": "testpass123",
    "first_name": "Test",
    "last_name": "User",
    "role": "student"
  }'
```

2. **Login:**

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

3. **Create a question (requires authentication):**

```bash
curl -X POST http://localhost:8000/api/exams/questions/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_access_token>" \
  -d '{
    "text": "What is the capital of France?",
    "question_type": "multiple_choice",
    "points": 5
  }'
```

### Using Postman

Import the provided `postman_collection.json` file for a complete set of API requests.

## Security Considerations

1. **HTTPS in Production**: Always use HTTPS in production environments
2. **Environment Variables**: Never commit sensitive information to version control
3. **Token Expiration**: Configure appropriate JWT token lifetimes
4. **CORS Configuration**: Configure CORS settings for your frontend domain
5. **Input Validation**: All inputs are validated using DRF serializers
6. **Error Handling**: Sensitive information is not leaked in error responses

## File Structure

```
BackEnd/App/
├── authentication/
│   ├── models.py          # User model with Google OAuth support
│   ├── serializers.py     # Authentication serializers
│   ├── views.py          # Authentication views
│   ├── urls.py           # Authentication URLs
│   └── services.py       # Google OAuth verification
├── exams/
│   ├── models.py         # Exam and Question models
│   ├── serializers.py    # Exam serializers
│   ├── views.py         # Exam views
│   └── urls.py          # Exam URLs
├── courses/
│   ├── models.py        # Course and Enrollment models
│   └── ...
├── App/
│   ├── settings.py      # Django settings
│   └── urls.py         # Main URL configuration
├── manage.py
├── requirements.txt
└── README.md
```

## Troubleshooting

### Common Issues

1. **Google OAuth Error**: Ensure `GOOGLE_CLIENT_ID` is set correctly
2. **Database Connection**: Check database credentials and connection
3. **Migration Errors**: Run `python manage.py migrate` to apply pending migrations
4. **Import Errors**: Ensure all dependencies are installed with `pip install -r requirements.txt`

### Getting Help

If you encounter issues:

1. Check the Django debug logs
2. Verify environment variables are set correctly
3. Ensure all migrations are applied
4. Check Google OAuth configuration in Google Cloud Console

## License

This project is licensed under the MIT License.
