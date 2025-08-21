# 🔔 Manual Notification System Test Guide

This guide provides step-by-step instructions to manually test the notification system using curl commands.

## Prerequisites

1. **Start the Django server:**

   ```bash
   cd Educational-platform/BackEnd/App
   python manage.py runserver 8000
   ```

2. **Make sure you have test users or create them first**

## Step-by-Step Test

### Step 1: Create Test Users (if needed)

```bash
# Create instructor
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_instructor@example.com",
    "password": "testpass123",
    "first_name": "Test",
    "last_name": "Instructor",
    "role": "instructor"
  }'

# Create student
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_student@example.com",
    "password": "testpass123",
    "first_name": "Test",
    "last_name": "Student",
    "role": "student"
  }'
```

### Step 2: Login as Instructor

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_instructor@example.com",
    "password": "testpass123"
  }'
```

**Save the access token from the response for the next steps.**

### Step 3: Login as Student

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_student@example.com",
    "password": "testpass123"
  }'
```

**Save the access token from the response for the next steps.**

### Step 4: Get Available Courses

```bash
curl -X GET http://localhost:8000/api/courses/ \
  -H "Authorization: Bearer YOUR_INSTRUCTOR_TOKEN"
```

**Note the course ID from the response.**

### Step 5: Enroll Student in Course

```bash
curl -X POST http://localhost:8000/api/courses/COURSE_ID/enroll/ \
  -H "Authorization: Bearer YOUR_STUDENT_TOKEN"
```

### Step 6: Send Notification (as Instructor)

```bash
curl -X POST http://localhost:8000/api/courses/COURSE_ID/notify-students/ \
  -H "Authorization: Bearer YOUR_INSTRUCTOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Notification",
    "message": "This is a test notification from the manual test.",
    "update_type": "announcement"
  }'
```

### Step 7: Check Student Notifications

```bash
curl -X GET http://localhost:8000/api/notifications/ \
  -H "Authorization: Bearer YOUR_STUDENT_TOKEN"
```

### Step 8: Mark Notification as Read

```bash
curl -X PATCH http://localhost:8000/api/notifications/NOTIFICATION_ID/mark_read/ \
  -H "Authorization: Bearer YOUR_STUDENT_TOKEN"
```

### Step 9: Check Unread Count

```bash
curl -X GET http://localhost:8000/api/notifications/unread_count/ \
  -H "Authorization: Bearer YOUR_STUDENT_TOKEN"
```

## Expected Results

### Step 6 (Send Notification):

```json
{
  "message": "Notification sent to 1 enrolled students",
  "student_count": 1,
  "course_title": "Your Course Title"
}
```

### Step 7 (Check Notifications):

```json
[
  {
    "id": 1,
    "notification_type": "course_update",
    "title": "Test Notification",
    "message": "This is a test notification from the manual test.",
    "data": {
      "course_id": 1,
      "course_title": "Your Course Title",
      "instructor_name": "Test Instructor",
      "update_type": "announcement"
    },
    "is_read": false,
    "created_at": "2025-08-21T16:30:00Z"
  }
]
```

## Troubleshooting

### Common Issues:

1. **401 Unauthorized**: Check that your access token is valid and properly formatted
2. **403 Forbidden**: Make sure the instructor is the course owner
3. **404 Not Found**: Verify the course ID exists
4. **500 Internal Server Error**: Check Django server logs for details

### WebSocket Testing:

For real-time WebSocket testing, you can use a WebSocket client like:

- Browser Developer Tools
- Postman
- WebSocket King

Connect to: `ws://localhost:8000/ws/notifications/`

Send authentication message:

```json
{
  "type": "auth",
  "token": "YOUR_STUDENT_TOKEN"
}
```

## Success Criteria

✅ **API Test Passed** if:

- Notification is sent successfully (Step 6 returns 200)
- Student receives notification (Step 7 shows the notification)
- Mark as read works (Step 8 returns 200)

✅ **WebSocket Test Passed** if:

- Connection established successfully
- Authentication accepted
- Real-time notification received when sent

## Next Steps

After manual testing:

1. Test the frontend integration
2. Test with multiple students
3. Test different notification types
4. Test error scenarios
