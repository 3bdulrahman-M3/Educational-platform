# Educational Platform - Backend API

This is a Django REST API for an educational platform with JWT authentication supporting two user roles: Instructor and Student.

## Features

- JWT Authentication with access and refresh tokens
- User registration and login
- Role-based access (Instructor/Student)
- User profile management
- PostgreSQL database integration
- RESTful API endpoints

## Setup Instructions

### Prerequisites

- Python 3.8+
- PostgreSQL
- pip

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure PostgreSQL database:
   - Create a database named `edu-app`
   - Set password for postgres user to `abdo`

4. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Authentication Endpoints

#### Register User
- **URL**: `POST /api/auth/register/`
- **Description**: Register a new user (instructor or student)
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "username": "username",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student",  // or "instructor"
    "password": "password123",
    "confirm_password": "password123"
  }
  ```
- **Response**:
  ```json
  {
    "message": "User registered successfully",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "username": "username",
      "first_name": "John",
      "last_name": "Doe",
      "role": "student",
      "date_joined": "2024-01-01T00:00:00Z"
    },
    "tokens": {
      "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
  }
  ```

#### Login User
- **URL**: `POST /api/auth/login/`
- **Description**: Login user and get JWT tokens
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "password123"
  }
  ```
- **Response**: Same as register response

#### Get User Profile
- **URL**: `GET /api/auth/profile/`
- **Description**: Get current user profile
- **Headers**: `Authorization: Bearer <access_token>`
- **Response**:
  ```json
  {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "first_name": "John",
    "last_name": "Doe",
    "role": "student",
    "date_joined": "2024-01-01T00:00:00Z"
  }
  ```

#### Update User Profile
- **URL**: `PUT /api/auth/profile/update/`
- **Description**: Update current user profile
- **Headers**: `Authorization: Bearer <access_token>`
- **Request Body**:
  ```json
  {
    "first_name": "Updated Name",
    "last_name": "Updated Last Name"
  }
  ```

#### Refresh Token
- **URL**: `POST /api/auth/token/refresh/`
- **Description**: Get new access token using refresh token
- **Request Body**:
  ```json
  {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
  ```

#### Logout
- **URL**: `POST /api/auth/logout/`
- **Description**: Logout user (blacklist refresh token)
- **Headers**: `Authorization: Bearer <access_token>`
- **Request Body**:
  ```json
  {
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
  ```

## User Roles

### Student
- Can register and login
- Can view and update their profile
- Access to student-specific features (to be implemented)

### Instructor
- Can register and login
- Can view and update their profile
- Access to instructor-specific features (to be implemented)

## Database Schema

### User Model
- `id`: Primary key
- `email`: Unique email address (used for login)
- `username`: Unique username
- `first_name`: User's first name
- `last_name`: User's last name
- `role`: User role (instructor/student)
- `date_joined`: Account creation date
- `is_active`: Account status
- `password`: Hashed password

## Testing

Run the test script to verify API functionality:
```bash
python test_api.py
```

## Admin Panel

Access the Django admin panel at `http://localhost:8000/admin/` to manage users and view the database.

## Security Features

- JWT token-based authentication
- Password hashing
- Token blacklisting for logout
- CORS configuration for frontend integration
- Role-based access control

## Environment Variables

For production, consider setting these environment variables:
- `SECRET_KEY`
- `DEBUG`
- `DATABASE_URL`
- `ALLOWED_HOSTS` 
