# Educational Platform API Documentation

## Overview
This document provides comprehensive documentation for the Educational Platform API endpoints, including authentication, courses, enrollments, and exams management.

**Base URL:** `http://localhost:8000/api`

## Table of Contents
1. [Authentication](#authentication)
2. [Courses](#courses)
3. [Enrollments](#enrollments)
4. [Exams](#exams)
5. [Error Handling](#error-handling)
6. [Frontend Integration Examples](#frontend-integration-examples)

---

## Authentication

### Login
**Endpoint:** `POST /api/auth/login/`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "username": "johndoe",
    "role": "instructor",
    "date_joined": "2025-08-14T19:00:00Z"
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

### Register
**Endpoint:** `POST /api/auth/register/`

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "username": "newuser",
  "password": "password123",
  "confirm_password": "password123",
  "first_name": "Jane",
  "last_name": "Smith",
  "role": "student"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 2,
    "email": "newuser@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "username": "newuser",
    "role": "student",
    "date_joined": "2025-08-14T19:00:00Z"
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }
}
```

### Get Current User Profile
**Endpoint:** `GET /api/auth/profile/`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "username": "johndoe",
  "role": "instructor",
  "date_joined": "2025-08-14T19:00:00Z"
}
```

---

## Courses

### Get All Courses
**Endpoint:** `GET /api/courses/`

**Headers:** `Authorization: Bearer <access_token>` (optional)

**Response:**
```json
[
  {
    "id": 1,
    "title": "Python Programming Basics",
    "description": "Learn the fundamentals of Python programming",
    "image": "https://res.cloudinary.com/.../image/upload/...",
    "instructor": {
      "id": 1,
      "email": "instructor@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "username": "johndoe",
      "role": "instructor"
    },
    "student_count": 15,
    "enrollment_count": 20,
    "created_at": "2025-08-14T19:00:00Z",
    "updated_at": "2025-08-14T19:00:00Z"
  }
]
```

### Get Course by ID
**Endpoint:** `GET /api/courses/?id=1`

**Headers:** `Authorization: Bearer <access_token>` (optional)

**Response:** Same as single course object above

### Create Course (Instructor Only)
**Endpoint:** `POST /api/courses/create/`

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body (FormData):**
```
title: "Advanced JavaScript"
description: "Master modern JavaScript concepts"
image: [File object] (optional)
```

**Response:**
```json
{
  "id": 2,
  "title": "Advanced JavaScript",
  "description": "Master modern JavaScript concepts",
  "image": "https://res.cloudinary.com/.../image/upload/...",
  "instructor": {
    "id": 1,
    "email": "instructor@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "username": "johndoe",
    "role": "instructor"
  },
  "student_count": 0,
  "enrollment_count": 0,
  "created_at": "2025-08-14T19:00:00Z",
  "updated_at": "2025-08-14T19:00:00Z"
}
```

### Update Course (Instructor Only)
**Endpoint:** `PUT /api/courses/{id}/update/`

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Request Body (FormData):**
```
title: "Updated Course Title" (optional)
description: "Updated description" (optional)
image: [File object] (optional)
```

**Response:** Updated course object

### Delete Course (Instructor Only)
**Endpoint:** `DELETE /api/courses/{id}/delete/`

**Headers:** `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "message": "Course deleted successfully"
}
```

### Get Instructor's Courses
**Endpoint:** `GET /api/courses/instructor/courses/`

**Headers:** `Authorization: Bearer <access_token>`

**Response:** Array of courses created by the authenticated instructor

### Get Course Students (Instructor Only)
**Endpoint:** `GET /api/courses/instructor/courses/{course_id}/students/`

**Headers:** `Authorization: Bearer <access_token>`

**Response:**
```json
[
  {
    "id": 1,
    "student": {
      "id": 2,
      "email": "student@example.com",
      "first_name": "Jane",
      "last_name": "Smith",
      "username": "janesmith",
      "role": "student"
    },
    "course": {
      "id": 1,
      "title": "Python Programming Basics"
    },
    "enrolled_at": "2025-08-14T19:00:00Z",
    "withdrawn_at": null,
    "is_active": true
  }
]
```

### Get Withdrawn Students (Instructor Only)
**Endpoint:** `GET /api/courses/instructor/courses/{course_id}/withdrawn/`

**Headers:** `Authorization: Bearer <access_token>`

**Response:** Array of withdrawn enrollments

---

## Enrollments

### Get Student's Enrolled Courses
**Endpoint:** `GET /api/courses/student/courses/`

**Headers:** `Authorization: Bearer <access_token>`

**Response:** Array of enrollments for the authenticated student

### Enroll in Course (Student Only)
**Endpoint:** `POST /api/courses/{course_id}/enroll/`

**Headers:** `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "id": 1,
  "student": {
    "id": 2,
    "email": "student@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "username": "janesmith",
    "role": "student"
  },
  "course": {
    "id": 1,
    "title": "Python Programming Basics"
  },
  "enrolled_at": "2025-08-14T19:00:00Z",
  "withdrawn_at": null,
  "is_active": true
}
```

### Withdraw from Course (Student Only)
**Endpoint:** `POST /api/courses/{course_id}/withdraw/`

**Headers:** `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "message": "Successfully withdrawn from course"
}
```

### Get Course Enrollments
**Endpoint:** `GET /api/courses/{course_id}/enrollments/`

**Headers:** `Authorization: Bearer <access_token>`

**Response:** Array of student profiles enrolled in the course

### Get Student Enrollments by Student ID
**Endpoint:** `GET /api/courses/student/{student_id}/enrollments/`

**Headers:** `Authorization: Bearer <access_token>`

**Response:** Array of courses the student is enrolled in

---

## Exams

### Get Course Exam
**Endpoint:** `GET /api/courses/{course_id}/exam/`

**Headers:** `Authorization: Bearer <access_token>` (optional)

**Response:**
```json
{
  "id": 1,
  "name": "Python Basics Final Exam",
  "course": 1,
  "questions": [
    {
      "id": 1,
      "text": "What is Python?",
      "question_type": "multiple_choice",
      "points": 5,
      "choices": [
        {
          "id": 1,
          "text": "A programming language",
          "is_correct": true,
          "order": 1
        }
      ]
    }
  ]
}
```

---

## Error Handling

### Common HTTP Status Codes
- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

### Error Response Format
```json
{
  "error": "Error message description",
  "details": "Additional error details (optional)"
}
```

### Common Error Scenarios

#### Authentication Errors
```json
{
  "error": "Authentication credentials were not provided"
}
```

#### Permission Errors
```json
{
  "error": "Only instructors can create courses"
}
```

#### Validation Errors
```json
{
  "title": ["This field is required."],
  "description": ["This field is required."]
}
```

---

## Frontend Integration Examples

### Setting up Axios with Authentication

```typescript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

### Authentication Functions

```typescript
export const authAPI = {
  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login/', { email, password });
    const { tokens, user } = response.data;
    
    localStorage.setItem('authToken', tokens.access);
    localStorage.setItem('user', JSON.stringify(user));
    
    return response.data;
  },

  register: async (userData: RegisterData) => {
    const response = await api.post('/auth/register/', userData);
    const { tokens, user } = response.data;
    
    localStorage.setItem('authToken', tokens.access);
    localStorage.setItem('user', JSON.stringify(user));
    
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
  },

  getCurrentUser: () => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }
};
```

### Course Management Functions

```typescript
export const instructorAPI = {
  createCourse: async (courseData: {
    title: string;
    description: string;
    image?: File;
  }) => {
    const formData = new FormData();
    formData.append('title', courseData.title);
    formData.append('description', courseData.description);
    
    if (courseData.image) {
      formData.append('image', courseData.image);
    }

    const response = await api.post('/courses/create/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  getMyCourses: async () => {
    const response = await api.get('/courses/instructor/courses/');
    return response.data;
  },

  updateCourse: async (courseId: number, courseData: any) => {
    const formData = new FormData();
    
    if (courseData.title) formData.append('title', courseData.title);
    if (courseData.description) formData.append('description', courseData.description);
    if (courseData.image) formData.append('image', courseData.image);

    const response = await api.put(`/courses/${courseId}/update/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  deleteCourse: async (courseId: number) => {
    const response = await api.delete(`/courses/${courseId}/delete/`);
    return response.data;
  },

  getCourseStudents: async (courseId: number) => {
    const response = await api.get(`/courses/instructor/courses/${courseId}/students/`);
    return response.data;
  }
};
```

### Student Functions

```typescript
export const studentAPI = {
  getAvailableCourses: async () => {
    const response = await api.get('/courses/');
    return response.data;
  },

  enrollInCourse: async (courseId: number) => {
    const response = await api.post(`/courses/${courseId}/enroll/`);
    return response.data;
  },

  withdrawFromCourse: async (courseId: number) => {
    const response = await api.post(`/courses/${courseId}/withdraw/`);
    return response.data;
  },

  getMyEnrolledCourses: async () => {
    const response = await api.get('/courses/student/courses/');
    return response.data;
  }
};
```

### React Component Example

```tsx
import React, { useState, useEffect } from 'react';
import { instructorAPI } from '../lib/api';

const CreateCourseForm: React.FC = () => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    image: null as File | null
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const course = await instructorAPI.createCourse(formData);
      console.log('Course created:', course);
      // Handle success (redirect, show message, etc.)
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to create course');
    } finally {
      setLoading(false);
    }
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setFormData(prev => ({ ...prev, image: file }));
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="title">Course Title</label>
        <input
          type="text"
          id="title"
          value={formData.title}
          onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
          required
        />
      </div>

      <div>
        <label htmlFor="description">Description</label>
        <textarea
          id="description"
          value={formData.description}
          onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
          required
        />
      </div>

      <div>
        <label htmlFor="image">Course Image</label>
        <input
          type="file"
          id="image"
          accept="image/*"
          onChange={handleImageChange}
        />
      </div>

      {error && <div className="error">{error}</div>}

      <button type="submit" disabled={loading}>
        {loading ? 'Creating...' : 'Create Course'}
      </button>
    </form>
  );
};

export default CreateCourseForm;
```

---

## Testing the API

### Using Postman/Insomnia
1. Set base URL to `http://localhost:8000/api`
2. For authenticated endpoints, add header: `Authorization: Bearer <your_token>`
3. For file uploads, use `form-data` body type

### Using cURL
```bash
# Get all courses
curl -X GET http://localhost:8000/api/courses/

# Create course (with auth token)
curl -X POST http://localhost:8000/api/courses/create/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "title=Test Course" \
  -F "description=Test Description" \
  -F "image=@/path/to/image.jpg"
```

---

## Notes

1. **File Uploads**: All file uploads use `multipart/form-data` format
2. **Authentication**: Most endpoints require JWT authentication via Bearer token
3. **Role-based Access**: Some endpoints are restricted to specific user roles
4. **Error Handling**: Always check response status and handle errors appropriately
5. **Image Storage**: Images are stored using Cloudinary and return URLs
6. **Database**: The API uses PostgreSQL with Django ORM

---

## Support

For API issues or questions:
1. Check the Django server logs for detailed error messages
2. Verify authentication tokens are valid and not expired
3. Ensure all required fields are provided in requests
4. Check user permissions for role-restricted endpoints
