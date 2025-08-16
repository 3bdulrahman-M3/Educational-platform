# P2P Session System API Documentation

## Overview

This document provides comprehensive API documentation for integrating the React/Next.js frontend with the Django backend P2P Session system. The backend is built using Django REST Framework with JWT authentication.

## Base URL

```
http://localhost:8000/api/
```

## Authentication

All API endpoints require JWT authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## API Endpoints

### 1. Session Management

#### Get All Sessions

```http
GET /api/sessions/
```

**Query Parameters:**

- `status` (optional): Filter by status (pending_approval, approved, scheduled, ongoing, completed, cancelled, expired)
- `subject` (optional): Filter by subject (case-insensitive search)
- `level` (optional): Filter by level (beginner, intermediate, advanced)
- `date_from` (optional): Filter sessions from this date
- `date_to` (optional): Filter sessions until this date
- `creator` (optional): Filter by creator ID

**Response:**

```json
{
  "count": 10,
  "next": "http://localhost:8000/api/sessions/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Advanced Python Programming",
      "description": "Learn advanced Python concepts",
      "subject": "Programming",
      "level": "advanced",
      "date": "2024-01-15T14:00:00Z",
      "duration": 90,
      "max_participants": 15,
      "creator": {
        "id": 1,
        "username": "john_doe",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "date_joined": "2024-01-01T00:00:00Z"
      },
      "status": "scheduled",
      "created_at": "2024-01-10T10:00:00Z",
      "updated_at": "2024-01-10T10:00:00Z",
      "participant_count": 5,
      "is_full": false,
      "available_spots": 10,
      "can_join": true
    }
  ]
}
```

#### Get Session Details

```http
GET /api/sessions/{id}/
```

**Response:**

```json
{
  "id": 1,
  "title": "Advanced Python Programming",
  "description": "Learn advanced Python concepts",
  "subject": "Programming",
  "level": "advanced",
  "date": "2024-01-15T14:00:00Z",
  "duration": 90,
  "max_participants": 15,
  "creator": {
    "id": 1,
    "username": "john_doe",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "date_joined": "2024-01-01T00:00:00Z"
  },
  "status": "scheduled",
  "created_at": "2024-01-10T10:00:00Z",
  "updated_at": "2024-01-10T10:00:00Z",
  "participants": [
    {
      "id": 1,
      "user": {
        "id": 2,
        "username": "jane_smith",
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane@example.com",
        "date_joined": "2024-01-02T00:00:00Z"
      },
      "role": "student",
      "status": "approved",
      "joined_at": "2024-01-11T09:00:00Z"
    }
  ],
  "materials": [
    {
      "id": 1,
      "title": "Python Basics PDF",
      "type": "file",
      "url": "",
      "file": "https://res.cloudinary.com/...",
      "file_name": "python_basics.pdf",
      "uploaded_by": {
        "id": 1,
        "username": "john_doe",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "date_joined": "2024-01-01T00:00:00Z"
      },
      "uploaded_at": "2024-01-12T10:00:00Z"
    }
  ],
  "booking_requests": [
    {
      "id": 1,
      "user": {
        "id": 3,
        "username": "bob_wilson",
        "first_name": "Bob",
        "last_name": "Wilson",
        "email": "bob@example.com",
        "date_joined": "2024-01-03T00:00:00Z"
      },
      "message": "I'm interested in learning Python",
      "status": "pending",
      "requested_at": "2024-01-13T11:00:00Z"
    }
  ],
  "is_full": false,
  "available_spots": 10,
  "participant_count": 5,
  "can_join": true
}
```

#### Create Session

```http
POST /api/sessions/
```

**Request Body:**

```json
{
  "title": "Advanced Python Programming",
  "description": "Learn advanced Python concepts",
  "subject": "Programming",
  "level": "advanced",
  "date": "2024-01-15T14:00:00-05:00",
  "duration": 90,
  "max_participants": 15,
  "timezone_offset": -300
}
```

**Response:**

```json
{
  "id": 1,
  "title": "Advanced Python Programming",
  "description": "Learn advanced Python concepts",
  "subject": "Programming",
  "level": "advanced",
  "date": "2024-01-15T19:00:00Z",
  "duration": 90,
  "max_participants": 15,
  "creator": {
    "id": 1,
    "username": "john_doe",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "date_joined": "2024-01-01T00:00:00Z"
  },
  "status": "pending_approval",
  "created_at": "2024-01-10T10:00:00Z",
  "updated_at": "2024-01-10T10:00:00Z"
}
```

#### Update Session

```http
PUT /api/sessions/{id}/
```

**Request Body:**

```json
{
  "title": "Updated Python Programming",
  "description": "Updated description",
  "subject": "Programming",
  "level": "intermediate",
  "date": "2024-01-16T14:00:00-05:00",
  "duration": 120,
  "max_participants": 20,
  "status": "approved"
}
```

#### Delete Session

```http
DELETE /api/sessions/{id}/
```

#### Join Session (Create Booking Request)

```http
POST /api/sessions/{id}/join/
```

**Request Body:**

```json
{
  "message": "I'm interested in joining this session"
}
```

**Response:**

```json
{
  "id": 1,
  "user": {
    "id": 3,
    "username": "bob_wilson",
    "first_name": "Bob",
    "last_name": "Wilson",
    "email": "bob@example.com",
    "date_joined": "2024-01-03T00:00:00Z"
  },
  "message": "I'm interested in joining this session",
  "status": "pending",
  "requested_at": "2024-01-13T11:00:00Z"
}
```

#### Approve Booking Request

```http
POST /api/sessions/{id}/approve_request/
```

**Request Body:**

```json
{
  "user_id": 3
}
```

#### Reject Booking Request

```http
POST /api/sessions/{id}/reject_request/
```

**Request Body:**

```json
{
  "user_id": 3
}
```

#### Cancel Session

```http
POST /api/sessions/{id}/cancel/
```

#### Get My Sessions

```http
GET /api/sessions/my_sessions/
```

**Response:**

```json
{
  "created": [
    {
      "id": 1,
      "title": "Advanced Python Programming",
      "description": "Learn advanced Python concepts",
      "subject": "Programming",
      "level": "advanced",
      "date": "2024-01-15T19:00:00Z",
      "duration": 90,
      "max_participants": 15,
      "creator": {
        "id": 1,
        "username": "john_doe",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "date_joined": "2024-01-01T00:00:00Z"
      },
      "status": "scheduled",
      "created_at": "2024-01-10T10:00:00Z",
      "updated_at": "2024-01-10T10:00:00Z",
      "participants": [...],
      "materials": [...],
      "booking_requests": [...],
      "is_full": false,
      "available_spots": 10,
      "participant_count": 5,
      "can_join": true
    }
  ],
  "joined": [
    {
      "id": 2,
      "title": "JavaScript Fundamentals",
      "description": "Learn JavaScript basics",
      "subject": "Web Development",
      "level": "beginner",
      "date": "2024-01-20T15:00:00Z",
      "duration": 60,
      "max_participants": 10,
      "creator": {
        "id": 4,
        "username": "alice_jones",
        "first_name": "Alice",
        "last_name": "Jones",
        "email": "alice@example.com",
        "date_joined": "2024-01-04T00:00:00Z"
      },
      "status": "approved",
      "created_at": "2024-01-11T09:00:00Z",
      "updated_at": "2024-01-11T09:00:00Z",
      "participants": [...],
      "materials": [...],
      "booking_requests": [...],
      "is_full": false,
      "available_spots": 5,
      "participant_count": 5,
      "can_join": false
    }
  ]
}
```

### 2. Notification Management

#### Get Notifications

```http
GET /api/notifications/
```

**Response:**

```json
[
  {
    "id": 1,
    "user": 1,
    "title": "New booking request for Advanced Python Programming",
    "message": "Bob Wilson wants to join your session.",
    "type": "booking_request",
    "session": 1,
    "read": false,
    "created_at": "2024-01-13T11:00:00Z"
  },
  {
    "id": 2,
    "user": 1,
    "title": "Booking request approved for JavaScript Fundamentals",
    "message": "Your request to join JavaScript Fundamentals has been approved.",
    "type": "session_update",
    "session": 2,
    "read": true,
    "created_at": "2024-01-12T10:00:00Z"
  }
]
```

#### Mark Notification as Read

```http
POST /api/notifications/{id}/mark_as_read/
```

#### Mark All Notifications as Read

```http
POST /api/notifications/mark_all_as_read/
```

### 3. Session Materials

#### Get Session Materials

```http
GET /api/sessions/{session_id}/materials/
```

**Response:**

```json
[
  {
    "id": 1,
    "title": "Python Basics PDF",
    "type": "file",
    "url": "",
    "file": "https://res.cloudinary.com/...",
    "file_name": "python_basics.pdf",
    "uploaded_by": {
      "id": 1,
      "username": "john_doe",
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "date_joined": "2024-01-01T00:00:00Z"
    },
    "uploaded_at": "2024-01-12T10:00:00Z"
  },
  {
    "id": 2,
    "title": "Python Documentation",
    "type": "link",
    "url": "https://docs.python.org/3/",
    "file": "",
    "file_name": "",
    "uploaded_by": {
      "id": 1,
      "username": "john_doe",
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com",
      "date_joined": "2024-01-01T00:00:00Z"
    },
    "uploaded_at": "2024-01-12T11:00:00Z"
  }
]
```

#### Upload Material

```http
POST /api/sessions/{session_id}/materials/
```

**Request Body (multipart/form-data):**

```
title: Python Basics PDF
type: file
file: [file upload]
```

**OR**

**Request Body (JSON for links):**

```json
{
  "title": "Python Documentation",
  "type": "link",
  "url": "https://docs.python.org/3/"
}
```

#### Update Material

```http
PUT /api/sessions/{session_id}/materials/{id}/
```

#### Delete Material

```http
DELETE /api/sessions/{session_id}/materials/{id}/
```

## Frontend Integration Guide

### 1. API Configuration

Create an API configuration file:

```typescript
// src/lib/apiConfig.ts
import axios from "axios";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export const apiConfig = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add request interceptor to include auth token
apiConfig.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle token refresh
apiConfig.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      const refreshToken = localStorage.getItem("refresh_token");
      if (refreshToken) {
        try {
          const response = await axios.post(
            `${API_BASE_URL}/auth/token/refresh/`,
            {
              refresh: refreshToken,
            }
          );

          localStorage.setItem("access_token", response.data.access);
          originalRequest.headers.Authorization = `Bearer ${response.data.access}`;

          return apiConfig(originalRequest);
        } catch (refreshError) {
          // Redirect to login
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          window.location.href = "/login";
        }
      }
    }

    return Promise.reject(error);
  }
);
```

### 2. Session API Service

```typescript
// src/lib/sessionAPI.ts
import { apiConfig } from "./apiConfig";

export interface Session {
  id: number;
  title: string;
  description: string;
  subject: string;
  level: "beginner" | "intermediate" | "advanced";
  date: string;
  duration: number;
  max_participants: number;
  creator: User;
  status: string;
  created_at: string;
  updated_at: string;
  participants: Participant[];
  materials: SessionMaterial[];
  booking_requests: BookingRequest[];
  is_full: boolean;
  available_spots: number;
  participant_count: number;
  can_join: boolean;
}

export interface User {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  email: string;
  date_joined: string;
}

export interface Participant {
  id: number;
  user: User;
  role: "student" | "tutor";
  status: "pending" | "approved" | "rejected";
  joined_at: string;
}

export interface BookingRequest {
  id: number;
  user: User;
  message: string;
  status: "pending" | "approved" | "rejected";
  requested_at: string;
}

export interface SessionMaterial {
  id: number;
  title: string;
  type: "file" | "link" | "note";
  url: string;
  file: string;
  file_name: string;
  uploaded_by: User;
  uploaded_at: string;
}

export interface Notification {
  id: number;
  user: number;
  title: string;
  message: string;
  type: "reminder" | "booking_request" | "session_update" | "general";
  session: number | null;
  read: boolean;
  created_at: string;
}

export const sessionAPI = {
  // Get all sessions
  getSessions: async (
    filters?: any
  ): Promise<{
    count: number;
    next: string | null;
    previous: string | null;
    results: Session[];
  }> => {
    const params = new URLSearchParams();
    if (filters?.status) params.append("status", filters.status);
    if (filters?.subject) params.append("subject", filters.subject);
    if (filters?.level) params.append("level", filters.level);
    if (filters?.date_from) params.append("date_from", filters.date_from);
    if (filters?.date_to) params.append("date_to", filters.date_to);
    if (filters?.creator) params.append("creator", filters.creator);

    const response = await apiConfig.get(`/sessions/?${params}`);
    return response.data;
  },

  // Get session details
  getSessionDetails: async (id: number): Promise<Session> => {
    const response = await apiConfig.get(`/sessions/${id}/`);
    return response.data;
  },

  // Create session
  createSession: async (data: Partial<Session>): Promise<Session> => {
    const payload = {
      ...data,
      timezone_offset: new Date().getTimezoneOffset(),
    };
    const response = await apiConfig.post("/sessions/", payload);
    return response.data;
  },

  // Update session
  updateSession: async (
    id: number,
    data: Partial<Session>
  ): Promise<Session> => {
    const payload = {
      ...data,
      timezone_offset: new Date().getTimezoneOffset(),
    };
    const response = await apiConfig.put(`/sessions/${id}/`, payload);
    return response.data;
  },

  // Delete session
  deleteSession: async (id: number): Promise<void> => {
    await apiConfig.delete(`/sessions/${id}/`);
  },

  // Join session
  joinSession: async (
    sessionId: number,
    message?: string
  ): Promise<BookingRequest> => {
    const response = await apiConfig.post(`/sessions/${sessionId}/join/`, {
      message,
    });
    return response.data;
  },

  // Approve request
  approveRequest: async (sessionId: number, userId: number): Promise<void> => {
    await apiConfig.post(`/sessions/${sessionId}/approve_request/`, {
      user_id: userId,
    });
  },

  // Reject request
  rejectRequest: async (sessionId: number, userId: number): Promise<void> => {
    await apiConfig.post(`/sessions/${sessionId}/reject_request/`, {
      user_id: userId,
    });
  },

  // Cancel session
  cancelSession: async (sessionId: number): Promise<void> => {
    await apiConfig.post(`/sessions/${sessionId}/cancel/`);
  },

  // Get my sessions
  getMySessions: async (): Promise<{
    created: Session[];
    joined: Session[];
  }> => {
    const response = await apiConfig.get("/sessions/my_sessions/");
    return response.data;
  },

  // Get notifications
  getNotifications: async (): Promise<Notification[]> => {
    const response = await apiConfig.get("/notifications/");
    return response.data;
  },

  // Mark notification as read
  markNotificationAsRead: async (notificationId: number): Promise<void> => {
    await apiConfig.post(`/notifications/${notificationId}/mark_as_read/`);
  },

  // Mark all notifications as read
  markAllNotificationsAsRead: async (): Promise<void> => {
    await apiConfig.post("/notifications/mark_all_as_read/");
  },

  // Get session materials
  getSessionMaterials: async (
    sessionId: number
  ): Promise<SessionMaterial[]> => {
    const response = await apiConfig.get(`/sessions/${sessionId}/materials/`);
    return response.data;
  },

  // Upload material
  uploadMaterial: async (
    sessionId: number,
    material: FormData
  ): Promise<SessionMaterial> => {
    const response = await apiConfig.post(
      `/sessions/${sessionId}/materials/`,
      material,
      {
        headers: { "Content-Type": "multipart/form-data" },
      }
    );
    return response.data;
  },

  // Update material
  updateMaterial: async (
    sessionId: number,
    materialId: number,
    data: Partial<SessionMaterial>
  ): Promise<SessionMaterial> => {
    const response = await apiConfig.put(
      `/sessions/${sessionId}/materials/${materialId}/`,
      data
    );
    return response.data;
  },

  // Delete material
  deleteMaterial: async (
    sessionId: number,
    materialId: number
  ): Promise<void> => {
    await apiConfig.delete(`/sessions/${sessionId}/materials/${materialId}/`);
  },
};
```

### 3. React Hook for Sessions

```typescript
// src/hooks/useSessions.ts
import { useState, useEffect } from "react";
import { sessionAPI, Session } from "@/lib/sessionAPI";

export const useSessions = (filters?: any) => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pagination, setPagination] = useState({
    count: 0,
    next: null,
    previous: null,
  });

  const fetchSessions = async () => {
    try {
      setLoading(true);
      const response = await sessionAPI.getSessions(filters);
      setSessions(response.results);
      setPagination({
        count: response.count,
        next: response.next,
        previous: response.previous,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch sessions");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, [filters]);

  return {
    sessions,
    loading,
    error,
    pagination,
    refetch: fetchSessions,
  };
};
```

### 4. Session Form Component

```typescript
// src/components/SessionForm.tsx
import React, { useState } from "react";
import { sessionAPI, Session } from "@/lib/sessionAPI";

interface SessionFormProps {
  session?: Session;
  onSubmit: (session: Session) => void;
  onCancel: () => void;
}

export const SessionForm: React.FC<SessionFormProps> = ({
  session,
  onSubmit,
  onCancel,
}) => {
  const [formData, setFormData] = useState({
    title: session?.title || "",
    description: session?.description || "",
    subject: session?.subject || "",
    level: session?.level || "beginner",
    date: session?.date
      ? new Date(session.date).toISOString().slice(0, 16)
      : "",
    duration: session?.duration || 60,
    max_participants: session?.max_participants || 10,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      let result: Session;

      if (session) {
        result = await sessionAPI.updateSession(session.id, formData);
      } else {
        result = await sessionAPI.createSession(formData);
      }

      onSubmit(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save session");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700">Title</label>
        <input
          type="text"
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Description
        </label>
        <textarea
          value={formData.description}
          onChange={(e) =>
            setFormData({ ...formData, description: e.target.value })
          }
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          rows={3}
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Subject
        </label>
        <input
          type="text"
          value={formData.subject}
          onChange={(e) =>
            setFormData({ ...formData, subject: e.target.value })
          }
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">Level</label>
        <select
          value={formData.level}
          onChange={(e) =>
            setFormData({ ...formData, level: e.target.value as any })
          }
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        >
          <option value="beginner">Beginner</option>
          <option value="intermediate">Intermediate</option>
          <option value="advanced">Advanced</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Date & Time
        </label>
        <input
          type="datetime-local"
          value={formData.date}
          onChange={(e) => setFormData({ ...formData, date: e.target.value })}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Duration (minutes)
        </label>
        <input
          type="number"
          value={formData.duration}
          onChange={(e) =>
            setFormData({ ...formData, duration: parseInt(e.target.value) })
          }
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          min="15"
          max="480"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Max Participants
        </label>
        <input
          type="number"
          value={formData.max_participants}
          onChange={(e) =>
            setFormData({
              ...formData,
              max_participants: parseInt(e.target.value),
            })
          }
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          min="2"
          max="50"
          required
        />
      </div>

      <div className="flex justify-end space-x-3">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50"
        >
          {loading
            ? "Saving..."
            : session
            ? "Update Session"
            : "Create Session"}
        </button>
      </div>
    </form>
  );
};
```

## Error Handling

The API returns standard HTTP status codes:

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error responses include a message:

```json
{
  "error": "Session date must be in the future"
}
```

## Timezone Handling

The backend stores all dates in UTC. When creating or updating sessions:

1. Send the date with timezone offset: `"date": "2024-01-15T14:00:00-05:00"`
2. Include timezone offset: `"timezone_offset": -300`
3. The backend will convert to UTC before storing

When displaying dates, convert from UTC to local timezone on the frontend.

## File Upload

For file uploads:

1. Use `FormData` for multipart requests
2. Set `Content-Type: multipart/form-data`
3. Files are stored in Cloudinary and return a URL

## Testing

Test the API endpoints using tools like Postman or curl:

```bash
# Get all sessions
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/sessions/

# Create a session
curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
  -d '{"title":"Test Session","description":"Test","subject":"Test","level":"beginner","date":"2024-01-15T14:00:00-05:00","duration":60,"max_participants":10,"timezone_offset":-300}' \
  http://localhost:8000/api/sessions/
```

## Next Steps

1. Replace the mock service in your frontend with the real API calls
2. Update components to use the new data structure
3. Implement error handling and loading states
4. Add real-time notifications using WebSockets (optional)
5. Test thoroughly with different scenarios
6. Deploy and monitor for issues
