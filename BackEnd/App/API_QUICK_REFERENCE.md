# API Quick Reference Guide

## 🔐 Authentication
```bash
# Login
POST /api/auth/login/
Body: {"email": "...", "password": "..."}

# Register  
POST /api/auth/register/
Body: {"email": "...", "password": "...", "confirm_password": "...", "first_name": "...", "last_name": "...", "username": "...", "role": "..."}

# Get Profile
GET /api/auth/profile/
Headers: Authorization: Bearer <token>
```

## 📚 Courses
```bash
# Get All Courses
GET /api/courses/

# Get Course by ID
GET /api/courses/?id=1

# Create Course (Instructor Only)
POST /api/courses/create/
Headers: Authorization: Bearer <token>, Content-Type: multipart/form-data
Body: FormData with title, description, image

# Update Course (Instructor Only)
PUT /api/courses/{id}/update/
Headers: Authorization: Bearer <token>, Content-Type: multipart/form-data

# Delete Course (Instructor Only)
DELETE /api/courses/{id}/delete/
Headers: Authorization: Bearer <token>
```

## 👨‍🏫 Instructor Endpoints
```bash
# Get My Courses
GET /api/courses/instructor/courses/
Headers: Authorization: Bearer <token>

# Get Course Students
GET /api/courses/instructor/courses/{course_id}/students/
Headers: Authorization: Bearer <token>

# Get Withdrawn Students
GET /api/courses/instructor/courses/{course_id}/withdrawn/
Headers: Authorization: Bearer <token>
```

## 👨‍🎓 Student Endpoints
```bash
# Get My Enrolled Courses
GET /api/courses/student/courses/
Headers: Authorization: Bearer <token>

# Enroll in Course
POST /api/courses/{course_id}/enroll/
Headers: Authorization: Bearer <token>

# Withdraw from Course
POST /api/courses/{course_id}/withdraw/
Headers: Authorization: Bearer <token>
```

## 📝 Common Request Headers
```bash
# For authenticated endpoints
Authorization: Bearer <your_jwt_token>

# For file uploads
Content-Type: multipart/form-data
```

## 🚨 Common HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Server Error

## 💡 Frontend Integration Tips

### 1. Setup Axios Interceptors
```typescript
// Add auth token to all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

### 2. File Upload Pattern
```typescript
const formData = new FormData();
formData.append('title', title);
formData.append('description', description);
if (image) {
  formData.append('image', image);
}

const response = await api.post('/courses/create/', formData, {
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});
```

### 3. Error Handling Pattern
```typescript
try {
  const response = await api.post('/endpoint/', data);
  // Handle success
} catch (error: any) {
  const errorMessage = error.response?.data?.error || 'An error occurred';
  // Handle error
  console.error(errorMessage);
}
```

## 🔍 Testing Endpoints

### Test with cURL
```bash
# Test authentication
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Test course creation (with token)
curl -X POST http://localhost:8000/api/courses/create/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "title=Test Course" \
  -F "description=Test Description"
```

### Test with Postman
1. Set base URL: `http://localhost:8000/api`
2. Add auth header: `Authorization: Bearer <token>`
3. For file uploads: Use `form-data` body type

## 📋 Required Fields

### Course Creation
- `title` (required)
- `description` (required)
- `image` (optional)

### User Registration
- `email` (required)
- `username` (required)
- `password` (required)
- `confirm_password` (required)
- `first_name` (required)
- `last_name` (required)
- `role` (required: "instructor" or "student")

## ⚠️ Important Notes
1. **Authentication**: Most endpoints require valid JWT token
2. **Role-based Access**: Some endpoints are restricted by user role
3. **File Uploads**: Always use `multipart/form-data` for file uploads
4. **Error Handling**: Always check response status and handle errors
5. **Token Expiry**: JWT tokens expire after 60 minutes (refresh needed)
