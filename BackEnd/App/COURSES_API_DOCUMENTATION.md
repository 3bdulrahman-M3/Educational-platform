# Courses API Documentation

## 🔐 **Authentication**

All endpoints require JWT authentication except where noted. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## 📚 **Course Management APIs**

### 1. Create Course

**POST** `/api/courses/create/`

**Description:** Create a new course (Instructors only)

**Headers:**

```
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data
```

**Request Body (Form Data):**

```javascript
// JavaScript/Frontend Example
const formData = new FormData();
formData.append("title", "Introduction to Python Programming");
formData.append(
  "description",
  "Learn the basics of Python programming language"
);
formData.append("image", imageFile); // Optional: image file

// Using fetch
fetch("/api/courses/create/", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${token}`,
  },
  body: formData,
})
  .then((response) => response.json())
  .then((data) => console.log(data));
```

**Request Body (JSON - without image):**

```json
{
  "title": "Introduction to Python Programming",
  "description": "Learn the basics of Python programming language including variables, loops, functions, and object-oriented programming concepts."
}
```

**Success Response (201 Created):**

```json
{
  "id": 1,
  "title": "Introduction to Python Programming",
  "description": "Learn the basics of Python programming language",
  "image": "https://res.cloudinary.com/ddtp8tqvv/image/upload/v1234567890/course_image.jpg",
  "instructor": {
    "id": 1,
    "email": "instructor@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "instructor"
  },
  "student_count": 0,
  "enrollment_count": 0,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Error Responses:**

- `400 Bad Request`: Invalid data
- `403 Forbidden`: User is not an instructor
- `401 Unauthorized`: Invalid or missing token

**Frontend Integration Examples:**

**React with Axios:**

```javascript
import axios from "axios";

const createCourse = async (courseData, imageFile) => {
  const formData = new FormData();
  formData.append("title", courseData.title);
  formData.append("description", courseData.description);

  if (imageFile) {
    formData.append("image", imageFile);
  }

  try {
    const response = await axios.post("/api/courses/create/", formData, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  } catch (error) {
    throw error.response?.data || error.message;
  }
};
```

**Vue.js with Axios:**

```javascript
// In your Vue component
async createCourse() {
    const formData = new FormData();
    formData.append('title', this.course.title);
    formData.append('description', this.course.description);

    if (this.course.image) {
        formData.append('image', this.course.image);
    }

    try {
        const response = await this.$axios.post('/api/courses/create/', formData, {
            headers: {
                'Authorization': `Bearer ${this.$store.state.token}`,
                'Content-Type': 'multipart/form-data'
            }
        });
        this.$toast.success('Course created successfully!');
        this.$router.push('/courses');
    } catch (error) {
        this.$toast.error(error.response?.data?.error || 'Failed to create course');
    }
}
```

**Angular with HttpClient:**

```typescript
// In your Angular service
createCourse(courseData: any, imageFile?: File): Observable<any> {
    const formData = new FormData();
    formData.append('title', courseData.title);
    formData.append('description', courseData.description);

    if (imageFile) {
        formData.append('image', imageFile);
    }

    return this.http.post<any>('/api/courses/create/', formData, {
        headers: {
            'Authorization': `Bearer ${this.authService.getToken()}`
        }
    });
}

// In your component
async onSubmit() {
    try {
        const result = await this.courseService.createCourse(this.courseForm.value, this.selectedImage).toPromise();
        this.snackBar.open('Course created successfully!', 'Close', { duration: 3000 });
        this.router.navigate(['/courses']);
    } catch (error) {
        this.snackBar.open(error.error?.error || 'Failed to create course', 'Close', { duration: 3000 });
    }
}
```

### 2. Get All Courses

**GET** `/api/courses/`

**Description:** Get all available courses (Public endpoint)

**Headers:**

```
Content-Type: application/json
```

**Query Parameters:**

- `id` (optional): Get specific course by ID

**Request Examples:**

```javascript
// Get all courses
fetch("/api/courses/")
  .then((response) => response.json())
  .then((data) => console.log(data));

// Get specific course
fetch("/api/courses/?id=1")
  .then((response) => response.json())
  .then((data) => console.log(data));
```

**Success Response (200 OK):**

```json
[
  {
    "id": 1,
    "title": "Introduction to Python Programming",
    "description": "Learn the basics of Python programming language",
    "image": "https://res.cloudinary.com/ddtp8tqvv/image/upload/v1234567890/course_image.jpg",
    "instructor": {
      "id": 1,
      "email": "instructor@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "instructor"
    },
    "student_count": 15,
    "enrollment_count": 18,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
```

### 3. Update Course

**PUT** `/api/courses/{id}/update/`

**Description:** Update an existing course (Instructors only - can only update their own courses)

**Headers:**

```
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data
```

**Request Body:**

```javascript
const formData = new FormData();
formData.append("title", "Updated Course Title");
formData.append("description", "Updated course description");
formData.append("image", newImageFile); // Optional

fetch("/api/courses/1/update/", {
  method: "PUT",
  headers: {
    Authorization: `Bearer ${token}`,
  },
  body: formData,
})
  .then((response) => response.json())
  .then((data) => console.log(data));
```

**Success Response (200 OK):**

```json
{
  "id": 1,
  "title": "Updated Course Title",
  "description": "Updated course description",
  "image": "https://res.cloudinary.com/ddtp8tqvv/image/upload/v1234567890/new_image.jpg",
  "instructor": {
    "id": 1,
    "email": "instructor@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "instructor"
  },
  "student_count": 15,
  "enrollment_count": 18,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T11:45:00Z"
}
```

### 4. Delete Course

**DELETE** `/api/courses/{id}/delete/`

**Description:** Delete a course (Instructors only - can only delete their own courses)

**Headers:**

```
Authorization: Bearer <jwt_token>
```

**Request Example:**

```javascript
fetch("/api/courses/1/delete/", {
  method: "DELETE",
  headers: {
    Authorization: `Bearer ${token}`,
  },
})
  .then((response) => response.json())
  .then((data) => console.log(data));
```

**Success Response (200 OK):**

```json
{
  "message": "Course deleted successfully"
}
```

## 🎓 **Enrollment Management APIs**

### 5. Enroll in Course

**POST** `/api/courses/{id}/enroll/`

**Description:** Student enrolls in a course

**Headers:**

```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Example:**

```javascript
fetch("/api/courses/1/enroll/", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
})
  .then((response) => response.json())
  .then((data) => console.log(data));
```

**Success Response (201 Created):**

```json
{
  "id": 1,
  "student": {
    "id": 2,
    "email": "student@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "role": "student"
  },
  "course": {
    "id": 1,
    "title": "Introduction to Python Programming",
    "description": "Learn the basics of Python programming language",
    "image": "https://res.cloudinary.com/ddtp8tqvv/image/upload/v1234567890/course_image.jpg",
    "instructor": {
      "id": 1,
      "email": "instructor@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "role": "instructor"
    },
    "student_count": 16,
    "enrollment_count": 19,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "enrolled_at": "2024-01-15T12:00:00Z",
  "withdrawn_at": null,
  "is_active": true
}
```

### 6. Withdraw from Course

**POST** `/api/courses/{id}/withdraw/`

**Description:** Student withdraws from a course

**Headers:**

```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Example:**

```javascript
fetch("/api/courses/1/withdraw/", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  },
})
  .then((response) => response.json())
  .then((data) => console.log(data));
```

**Success Response (200 OK):**

```json
{
  "message": "Successfully withdrawn from course"
}
```

## 👨‍🏫 **Instructor-Specific APIs**

### 7. Get Instructor's Courses

**GET** `/api/courses/instructor/courses/`

**Description:** Get all courses created by the authenticated instructor

**Headers:**

```
Authorization: Bearer <jwt_token>
```

**Request Example:**

```javascript
fetch("/api/courses/instructor/courses/", {
  headers: {
    Authorization: `Bearer ${token}`,
  },
})
  .then((response) => response.json())
  .then((data) => console.log(data));
```

### 8. Get Course Students

**GET** `/api/courses/instructor/courses/{course_id}/students/`

**Description:** Get all active students enrolled in a specific course

**Headers:**

```
Authorization: Bearer <jwt_token>
```

**Request Example:**

```javascript
fetch("/api/courses/instructor/courses/1/students/", {
  headers: {
    Authorization: `Bearer ${token}`,
  },
})
  .then((response) => response.json())
  .then((data) => console.log(data));
```

## 👨‍🎓 **Student-Specific APIs**

### 9. Get Student's Enrolled Courses

**GET** `/api/courses/student/courses/`

**Description:** Get all courses the authenticated student is enrolled in

**Headers:**

```
Authorization: Bearer <jwt_token>
```

**Request Example:**

```javascript
fetch("/api/courses/student/courses/", {
  headers: {
    Authorization: `Bearer ${token}`,
  },
})
  .then((response) => response.json())
  .then((data) => console.log(data));
```

## 📊 **Data Models**

### Course Model

```json
{
  "id": "integer",
  "title": "string (max 255 characters)",
  "description": "text",
  "image": "Cloudinary URL (optional)",
  "instructor": "User object (read-only)",
  "student_count": "integer (read-only)",
  "enrollment_count": "integer (read-only)",
  "created_at": "datetime (read-only)",
  "updated_at": "datetime (read-only)"
}
```

### Enrollment Model

```json
{
  "id": "integer",
  "student": "User object (read-only)",
  "course": "Course object (read-only)",
  "enrolled_at": "datetime (read-only)",
  "withdrawn_at": "datetime (read-only, null if active)",
  "is_active": "boolean (read-only)"
}
```

## 🚨 **Error Handling**

All endpoints return appropriate HTTP status codes:

- `200 OK`: Success
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

**Error Response Format:**

```json
{
  "error": "Error message description"
}
```

## 🔧 **Testing with cURL**

**Create Course:**

```bash
curl -X POST \
  http://localhost:8000/api/courses/create/ \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -F 'title=Test Course' \
  -F 'description=This is a test course' \
  -F 'image=@/path/to/image.jpg'
```

**Get All Courses:**

```bash
curl -X GET \
  http://localhost:8000/api/courses/
```

**Enroll in Course:**

```bash
curl -X POST \
  http://localhost:8000/api/courses/1/enroll/ \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'
```

This documentation provides everything needed for frontend integration. The APIs are RESTful and follow standard conventions for easy integration with any frontend framework.
