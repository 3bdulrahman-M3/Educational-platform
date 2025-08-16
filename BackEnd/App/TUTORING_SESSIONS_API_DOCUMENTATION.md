# Tutoring Sessions API Documentation

## 🎓 **Overview**

This documentation covers the complete tutoring sessions system for the educational platform. Users can create, join, manage, and participate in tutoring sessions with comprehensive security and validation.

## 🔐 **Authentication**

All endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## 📚 **Session Management APIs**

### 1. Get All Sessions

**GET** `/api/sessions/`

**Description:** Get all available tutoring sessions with pagination and filtering

**Headers:**

```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Query Parameters:**

- `page` (optional): Page number for pagination
- `page_size` (optional): Number of items per page (max 100)
- `status` (optional): Filter by status (upcoming, ongoing, completed, cancelled)
- `date_from` (optional): Filter sessions from this date (ISO format)
- `date_to` (optional): Filter sessions until this date (ISO format)
- `creator` (optional): Filter by creator ID

**Request Example:**

```javascript
// Get all sessions
const getAllSessions = async () => {
  try {
    const response = await fetch("/api/sessions/", {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    });

    if (response.ok) {
      const data = await response.json();
      return data;
    } else {
      throw new Error("Failed to fetch sessions");
    }
  } catch (error) {
    console.error("Error:", error);
    throw error;
  }
};

// Get sessions with filters
const getFilteredSessions = async (filters = {}) => {
  const params = new URLSearchParams(filters);
  const response = await fetch(`/api/sessions/?${params}`, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
    },
  });
  return response.json();
};

// Usage examples
getFilteredSessions({ status: "upcoming", page_size: 5 });
getFilteredSessions({ date_from: "2024-01-01T00:00:00Z" });
```

**Success Response (200 OK):**

```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Advanced JavaScript Concepts",
      "description": "Deep dive into closures, promises, and async/await patterns",
      "date": "2024-01-15T14:00:00Z",
      "max_participants": 8,
      "creator": {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "role": "instructor"
      },
      "status": "upcoming",
      "created_at": "2024-01-05T09:00:00Z",
      "updated_at": "2024-01-05T09:00:00Z",
      "participant_count": 3,
      "is_full": false,
      "available_spots": 5,
      "can_join": true
    }
  ]
}
```

### 2. Get Session Details

**GET** `/api/sessions/{id}/`

**Description:** Get detailed information about a specific session

**Headers:**

```
Authorization: Bearer <jwt_token>
```

**URL Parameters:**

- `id` (integer): Session ID

**Request Example:**

```javascript
const getSessionDetails = async (sessionId) => {
  try {
    const response = await fetch(`/api/sessions/${sessionId}/`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    });

    if (response.ok) {
      const data = await response.json();
      return data;
    } else {
      throw new Error("Session not found");
    }
  } catch (error) {
    console.error("Error:", error);
    throw error;
  }
};
```

**Success Response (200 OK):**

```json
{
  "id": 1,
  "title": "Advanced JavaScript Concepts",
  "description": "Deep dive into closures, promises, and async/await patterns",
  "date": "2024-01-15T14:00:00Z",
  "max_participants": 8,
  "creator": {
    "id": 1,
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "role": "instructor"
  },
  "participants": [
    {
      "id": 1,
      "user": {
        "id": 2,
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice@example.com",
        "role": "student"
      },
      "joined_at": "2024-01-10T10:00:00Z",
      "role": "student"
    }
  ],
  "status": "upcoming",
  "created_at": "2024-01-05T09:00:00Z",
  "updated_at": "2024-01-05T09:00:00Z",
  "is_full": false,
  "available_spots": 7,
  "can_join": true
}
```

### 3. Create Session

**POST** `/api/sessions/`

**Description:** Create a new tutoring session (Instructors only)

**Headers:**

```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**Request Body:**

```json
{
  "title": "React Hooks Workshop",
  "description": "Learn useState, useEffect, and custom hooks",
  "date": "2024-01-20T16:00:00Z",
  "max_participants": 6
}
```

**Request Example:**

```javascript
const createSession = async (sessionData) => {
  try {
    const response = await fetch("/api/sessions/", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(sessionData),
    });

    if (response.ok) {
      const data = await response.json();
      return data;
    } else {
      const error = await response.json();
      throw new Error(error.error || "Failed to create session");
    }
  } catch (error) {
    console.error("Error:", error);
    throw error;
  }
};

// Usage
const newSession = {
  title: "React Hooks Workshop",
  description: "Learn useState, useEffect, and custom hooks",
  date: "2024-01-20T16:00:00Z",
  max_participants: 6,
};

createSession(newSession);
```

**Success Response (201 Created):**

```json
{
  "id": 4,
  "title": "React Hooks Workshop",
  "description": "Learn useState, useEffect, and custom hooks",
  "date": "2024-01-20T16:00:00Z",
  "max_participants": 6,
  "creator": {
    "id": 1,
    "first_name": "Current",
    "last_name": "User",
    "email": "current@example.com",
    "role": "instructor"
  },
  "participants": [],
  "status": "upcoming",
  "created_at": "2024-01-12T10:00:00Z",
  "updated_at": "2024-01-12T10:00:00Z",
  "is_full": false,
  "available_spots": 6,
  "can_join": true
}
```

**Error Responses:**

- `400 Bad Request`: Invalid data (past date, invalid participant count, etc.)
- `403 Forbidden`: User is not an instructor
- `401 Unauthorized`: Invalid or missing token

### 4. Update Session

**PUT** `/api/sessions/{id}/`

**Description:** Update an existing session (Creator only)

**Headers:**

```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**URL Parameters:**

- `id` (integer): Session ID

**Request Body:**

```json
{
  "title": "Updated React Hooks Workshop",
  "description": "Updated description with more details",
  "date": "2024-01-25T16:00:00Z",
  "max_participants": 8
}
```

**Request Example:**

```javascript
const updateSession = async (sessionId, updateData) => {
  try {
    const response = await fetch(`/api/sessions/${sessionId}/`, {
      method: "PUT",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(updateData),
    });

    if (response.ok) {
      const data = await response.json();
      return data;
    } else {
      const error = await response.json();
      throw new Error(error.error || "Failed to update session");
    }
  } catch (error) {
    console.error("Error:", error);
    throw error;
  }
};
```

**Error Responses:**

- `400 Bad Request`: Invalid data or cannot update completed/cancelled sessions
- `403 Forbidden`: User is not the creator
- `404 Not Found`: Session not found

### 5. Delete Session

**DELETE** `/api/sessions/{id}/`

**Description:** Delete a session (Creator only, cannot delete ongoing/completed sessions)

**Headers:**

```
Authorization: Bearer <jwt_token>
```

**URL Parameters:**

- `id` (integer): Session ID

**Request Example:**

```javascript
const deleteSession = async (sessionId) => {
  try {
    const response = await fetch(`/api/sessions/${sessionId}/`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    });

    if (response.ok) {
      return { message: "Session deleted successfully" };
    } else {
      const error = await response.json();
      throw new Error(error.error || "Failed to delete session");
    }
  } catch (error) {
    console.error("Error:", error);
    throw error;
  }
};
```

## 🎯 **Session Participation APIs**

### 6. Join Session

**POST** `/api/sessions/{id}/join/`

**Description:** Join a tutoring session

**Headers:**

```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**URL Parameters:**

- `id` (integer): Session ID

**Request Body:** No body required

**Request Example:**

```javascript
const joinSession = async (sessionId) => {
  try {
    const response = await fetch(`/api/sessions/${sessionId}/join/`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
        "Content-Type": "application/json",
      },
    });

    if (response.ok) {
      const data = await response.json();
      return data;
    } else {
      const error = await response.json();
      throw new Error(error.error || "Failed to join session");
    }
  } catch (error) {
    console.error("Error:", error);
    throw error;
  }
};
```

**Success Response (201 Created):**

```json
{
  "message": "Successfully joined the session",
  "session": {
    "id": 1,
    "title": "Advanced JavaScript Concepts",
    "description": "Deep dive into closures, promises, and async/await patterns",
    "date": "2024-01-15T14:00:00Z",
    "max_participants": 8,
    "creator": {
      "id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "role": "instructor"
    },
    "participants": [
      {
        "id": 1,
        "user": {
          "id": 2,
          "first_name": "Alice",
          "last_name": "Smith",
          "email": "alice@example.com",
          "role": "student"
        },
        "joined_at": "2024-01-10T10:00:00Z",
        "role": "student"
      },
      {
        "id": 2,
        "user": {
          "id": 3,
          "first_name": "Current",
          "last_name": "User",
          "email": "current@example.com",
          "role": "student"
        },
        "joined_at": "2024-01-12T15:30:00Z",
        "role": "student"
      }
    ],
    "status": "upcoming",
    "created_at": "2024-01-05T09:00:00Z",
    "updated_at": "2024-01-05T09:00:00Z",
    "is_full": false,
    "available_spots": 6,
    "can_join": true
  }
}
```

**Error Responses:**

- `400 Bad Request`: Already joined, session is full, or cannot join
- `404 Not Found`: Session not found

### 7. Leave Session

**POST** `/api/sessions/{id}/leave/`

**Description:** Leave a tutoring session

**Headers:**

```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**URL Parameters:**

- `id` (integer): Session ID

**Request Body:** No body required

**Request Example:**

```javascript
const leaveSession = async (sessionId) => {
  try {
    const response = await fetch(`/api/sessions/${sessionId}/leave/`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
        "Content-Type": "application/json",
      },
    });

    if (response.ok) {
      const data = await response.json();
      return data;
    } else {
      const error = await response.json();
      throw new Error(error.error || "Failed to leave session");
    }
  } catch (error) {
    console.error("Error:", error);
    throw error;
  }
};
```

**Success Response (200 OK):**

```json
{
  "message": "Successfully left the session",
  "session": {
    // Updated session object without the participant
  }
}
```

**Error Responses:**

- `400 Bad Request`: Not joined to session or cannot leave ongoing/completed session
- `404 Not Found`: Session not found

## 👨‍🏫 **Session Management APIs (Creator Only)**

### 8. Cancel Session

**POST** `/api/sessions/{id}/cancel/`

**Description:** Cancel a session (Creator only)

**Headers:**

```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**URL Parameters:**

- `id` (integer): Session ID

**Request Body:** No body required

**Request Example:**

```javascript
const cancelSession = async (sessionId) => {
  try {
    const response = await fetch(`/api/sessions/${sessionId}/cancel/`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
        "Content-Type": "application/json",
      },
    });

    if (response.ok) {
      const data = await response.json();
      return data;
    } else {
      const error = await response.json();
      throw new Error(error.error || "Failed to cancel session");
    }
  } catch (error) {
    console.error("Error:", error);
    throw error;
  }
};
```

**Success Response (200 OK):**

```json
{
  "message": "Session cancelled successfully",
  "session": {
    "id": 1,
    "title": "Advanced JavaScript Concepts",
    "description": "Deep dive into closures, promises, and async/await patterns",
    "date": "2024-01-15T14:00:00Z",
    "max_participants": 8,
    "creator": {
      "id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "role": "instructor"
    },
    "participants": [],
    "status": "cancelled",
    "created_at": "2024-01-05T09:00:00Z",
    "updated_at": "2024-01-12T16:00:00Z",
    "is_full": false,
    "available_spots": 8,
    "can_join": false
  }
}
```

**Error Responses:**

- `400 Bad Request`: Cannot cancel completed or cancelled session
- `403 Forbidden`: User is not the creator
- `404 Not Found`: Session not found

### 9. Start Session

**POST** `/api/sessions/{id}/start/`

**Description:** Start a session (Creator only)

**Headers:**

```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**URL Parameters:**

- `id` (integer): Session ID

**Request Example:**

```javascript
const startSession = async (sessionId) => {
  try {
    const response = await fetch(`/api/sessions/${sessionId}/start/`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
        "Content-Type": "application/json",
      },
    });

    if (response.ok) {
      const data = await response.json();
      return data;
    } else {
      const error = await response.json();
      throw new Error(error.error || "Failed to start session");
    }
  } catch (error) {
    console.error("Error:", error);
    throw error;
  }
};
```

**Success Response (200 OK):**

```json
{
  "message": "Session started successfully",
  "session": {
    "id": 1,
    "title": "Advanced JavaScript Concepts",
    "description": "Deep dive into closures, promises, and async/await patterns",
    "date": "2024-01-15T14:00:00Z",
    "max_participants": 8,
    "creator": {
      "id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "role": "instructor"
    },
    "participants": [],
    "status": "ongoing",
    "created_at": "2024-01-05T09:00:00Z",
    "updated_at": "2024-01-15T14:00:00Z",
    "is_full": false,
    "available_spots": 8,
    "can_join": false
  }
}
```

### 10. Complete Session

**POST** `/api/sessions/{id}/complete/`

**Description:** Complete a session (Creator only)

**Headers:**

```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

**URL Parameters:**

- `id` (integer): Session ID

**Request Example:**

```javascript
const completeSession = async (sessionId) => {
  try {
    const response = await fetch(`/api/sessions/${sessionId}/complete/`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
        "Content-Type": "application/json",
      },
    });

    if (response.ok) {
      const data = await response.json();
      return data;
    } else {
      const error = await response.json();
      throw new Error(error.error || "Failed to complete session");
    }
  } catch (error) {
    console.error("Error:", error);
    throw error;
  }
};
```

**Success Response (200 OK):**

```json
{
  "message": "Session completed successfully",
  "session": {
    "id": 1,
    "title": "Advanced JavaScript Concepts",
    "description": "Deep dive into closures, promises, and async/await patterns",
    "date": "2024-01-15T14:00:00Z",
    "max_participants": 8,
    "creator": {
      "id": 1,
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "role": "instructor"
    },
    "participants": [],
    "status": "completed",
    "created_at": "2024-01-05T09:00:00Z",
    "updated_at": "2024-01-15T16:00:00Z",
    "is_full": false,
    "available_spots": 8,
    "can_join": false
  }
}
```

## 👤 **User-Specific APIs**

### 11. Get My Sessions

**GET** `/api/sessions/my_sessions/`

**Description:** Get all sessions where user is creator or participant

**Headers:**

```
Authorization: Bearer <jwt_token>
```

**Query Parameters:**

- `page` (optional): Page number for pagination
- `page_size` (optional): Number of items per page

**Request Example:**

```javascript
const getMySessions = async () => {
  try {
    const response = await fetch("/api/sessions/my_sessions/", {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    });

    if (response.ok) {
      const data = await response.json();
      return data;
    } else {
      throw new Error("Failed to fetch my sessions");
    }
  } catch (error) {
    console.error("Error:", error);
    throw error;
  }
};
```

**Success Response (200 OK):**

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Advanced JavaScript Concepts",
      "description": "Deep dive into closures, promises, and async/await patterns",
      "date": "2024-01-15T14:00:00Z",
      "max_participants": 8,
      "creator": {
        "id": 1,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "role": "instructor"
      },
      "status": "upcoming",
      "created_at": "2024-01-05T09:00:00Z",
      "updated_at": "2024-01-05T09:00:00Z",
      "participant_count": 3,
      "is_full": false,
      "available_spots": 5,
      "can_join": true
    }
  ]
}
```

### 12. Get Created Sessions

**GET** `/api/sessions/created_sessions/`

**Description:** Get sessions created by the current user

**Headers:**

```
Authorization: Bearer <jwt_token>
```

**Request Example:**

```javascript
const getCreatedSessions = async () => {
  try {
    const response = await fetch("/api/sessions/created_sessions/", {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    });

    if (response.ok) {
      const data = await response.json();
      return data;
    } else {
      throw new Error("Failed to fetch created sessions");
    }
  } catch (error) {
    console.error("Error:", error);
    throw error;
  }
};
```

### 13. Get Joined Sessions

**GET** `/api/sessions/joined_sessions/`

**Description:** Get sessions where user is a participant

**Headers:**

```
Authorization: Bearer <jwt_token>
```

**Request Example:**

```javascript
const getJoinedSessions = async () => {
  try {
    const response = await fetch("/api/sessions/joined_sessions/", {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    });

    if (response.ok) {
      const data = await response.json();
      return data;
    } else {
      throw new Error("Failed to fetch joined sessions");
    }
  } catch (error) {
    console.error("Error:", error);
    throw error;
  }
};
```

### 14. Get Session Participants

**GET** `/api/sessions/{id}/participants/`

**Description:** Get all participants of a specific session

**Headers:**

```
Authorization: Bearer <jwt_token>
```

**URL Parameters:**

- `id` (integer): Session ID

**Request Example:**

```javascript
const getSessionParticipants = async (sessionId) => {
  try {
    const response = await fetch(`/api/sessions/${sessionId}/participants/`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
    });

    if (response.ok) {
      const data = await response.json();
      return data;
    } else {
      throw new Error("Failed to fetch participants");
    }
  } catch (error) {
    console.error("Error:", error);
    throw error;
  }
};
```

**Success Response (200 OK):**

```json
[
  {
    "id": 1,
    "user": {
      "id": 2,
      "first_name": "Alice",
      "last_name": "Smith",
      "email": "alice@example.com",
      "role": "student"
    },
    "joined_at": "2024-01-10T10:00:00Z",
    "role": "student"
  },
  {
    "id": 2,
    "user": {
      "id": 3,
      "first_name": "Bob",
      "last_name": "Johnson",
      "email": "bob@example.com",
      "role": "student"
    },
    "joined_at": "2024-01-11T14:30:00Z",
    "role": "student"
  }
]
```

## 📊 **Data Models**

### Session Model

```json
{
  "id": "integer (read-only)",
  "title": "string (max 200 characters)",
  "description": "text",
  "date": "datetime (future date required)",
  "max_participants": "integer (2-20)",
  "creator": "User object (read-only)",
  "participants": "Participant array (read-only)",
  "status": "string (upcoming, ongoing, completed, cancelled) (read-only)",
  "created_at": "datetime (read-only)",
  "updated_at": "datetime (read-only)",
  "is_full": "boolean (read-only)",
  "available_spots": "integer (read-only)",
  "can_join": "boolean (read-only)"
}
```

### Participant Model

```json
{
  "id": "integer (read-only)",
  "user": "User object (read-only)",
  "joined_at": "datetime (read-only)",
  "role": "string (student, tutor) (read-only)"
}
```

## 🔄 **Session Status Flow**

1. **Created**: Session is created with status "upcoming"
2. **Started**: Creator can start session → status becomes "ongoing"
3. **Completed**: Creator can complete session → status becomes "completed"
4. **Cancelled**: Creator can cancel session → status becomes "cancelled"

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

**Get All Sessions:**

```bash
curl -X GET \
  http://localhost:8000/api/sessions/ \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN'
```

**Create Session:**

```bash
curl -X POST \
  http://localhost:8000/api/sessions/ \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "React Hooks Workshop",
    "description": "Learn useState, useEffect, and custom hooks",
    "date": "2024-01-20T16:00:00Z",
    "max_participants": 6
  }'
```

**Join Session:**

```bash
curl -X POST \
  http://localhost:8000/api/sessions/1/join/ \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json'
```

**Cancel Session:**

```bash
curl -X POST \
  http://localhost:8000/api/sessions/1/cancel/ \
  -H 'Authorization: Bearer YOUR_JWT_TOKEN' \
  -H 'Content-Type: application/json'
```

## 🛡️ **Security Features**

1. **JWT Authentication**: All endpoints require valid JWT tokens
2. **Role-Based Access**: Only instructors can create sessions
3. **Creator Permissions**: Only creators can update, delete, start, complete, or cancel sessions
4. **Data Validation**: Comprehensive validation for dates, participant limits, and session states
5. **State Management**: Proper session state transitions with validation
6. **SQL Injection Protection**: Django ORM prevents SQL injection
7. **XSS Protection**: Input sanitization and output encoding
8. **CSRF Protection**: Django's built-in CSRF protection

## 🎯 **Best Practices**

1. **Always validate session state** before allowing actions
2. **Check user permissions** before sensitive operations
3. **Use proper error messages** for different scenarios
4. **Implement confirmation dialogs** for destructive actions
5. **Update UI immediately** after successful operations
6. **Handle edge cases** (full sessions, past dates, etc.)
7. **Use pagination** for large datasets
8. **Implement proper logging** for debugging

This documentation provides everything needed for frontend integration of the tutoring sessions system! 🎉
