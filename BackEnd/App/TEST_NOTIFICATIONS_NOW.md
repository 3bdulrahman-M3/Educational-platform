# 🔔 **TEST NOTIFICATIONS NOW - Complete Guide**

## 🚀 **Quick Start - Test the Notification System**

### **Step 1: Start the Server**

```bash
cd Educational-platform/BackEnd/App
python manage.py runserver 8000
```

### **Step 2: Open a New Terminal and Run Tests**

#### **Option A: Quick Health Check**

```bash
cd Educational-platform/BackEnd/App
python quick_test.py
```

#### **Option B: Full API Test**

```bash
cd Educational-platform/BackEnd/App
python test_notifications_simple.py
```

#### **Option C: Complete WebSocket Test**

```bash
cd Educational-platform/BackEnd/App
python test_notifications.py
```

## 🎯 **Manual Testing with Browser/Postman**

### **1. Test Server Connection**

Open your browser and go to: `http://localhost:8000/api/courses/`

**Expected Result:** JSON response with courses or empty array

### **2. Test Notifications Endpoint**

Go to: `http://localhost:8000/api/notifications/`

**Expected Result:** `{"detail": "Authentication credentials were not provided."}` (401 error is expected)

### **3. Test with Postman/curl**

#### **Step 1: Create Test Users**

```bash
# Create Instructor
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_instructor@example.com",
    "password": "testpass123",
    "first_name": "Test",
    "last_name": "Instructor",
    "role": "instructor"
  }'

# Create Student
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

#### **Step 2: Login and Get Tokens**

```bash
# Login as Instructor
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_instructor@example.com",
    "password": "testpass123"
  }'

# Login as Student
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_student@example.com",
    "password": "testpass123"
  }'
```

**Save the access tokens from both responses.**

#### **Step 3: Create a Course**

```bash
curl -X POST http://localhost:8000/api/courses/create/ \
  -H "Authorization: Bearer YOUR_INSTRUCTOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Course for Notifications",
    "description": "This is a test course",
    "price": 99.99,
    "category": 1
  }'
```

#### **Step 4: Enroll Student**

```bash
curl -X POST http://localhost:8000/api/courses/COURSE_ID/enroll/ \
  -H "Authorization: Bearer YOUR_STUDENT_TOKEN"
```

#### **Step 5: Send Notification**

```bash
curl -X POST http://localhost:8000/api/courses/COURSE_ID/notify-students/ \
  -H "Authorization: Bearer YOUR_INSTRUCTOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Notification",
    "message": "This is a test notification!",
    "update_type": "announcement"
  }'
```

#### **Step 6: Check Student Notifications**

```bash
curl -X GET http://localhost:8000/api/notifications/ \
  -H "Authorization: Bearer YOUR_STUDENT_TOKEN"
```

## ✅ **Expected Results**

### **Step 5 (Send Notification) Success:**

```json
{
  "message": "Notification sent to 1 enrolled students",
  "student_count": 1,
  "course_title": "Test Course for Notifications"
}
```

### **Step 6 (Check Notifications) Success:**

```json
[
  {
    "id": 1,
    "notification_type": "course_update",
    "title": "Test Notification",
    "message": "This is a test notification!",
    "data": {
      "course_id": 1,
      "course_title": "Test Course for Notifications",
      "instructor_name": "Test Instructor",
      "update_type": "announcement"
    },
    "is_read": false,
    "created_at": "2025-08-21T16:30:00Z"
  }
]
```

## 🔧 **Troubleshooting**

### **Server Won't Start:**

1. Check if port 8000 is in use: `netstat -an | findstr :8000`
2. Try different port: `python manage.py runserver 8001`
3. Check Django settings and requirements

### **Database Issues:**

```bash
python manage.py makemigrations
python manage.py migrate
```

### **Redis Connection Issues:**

Check your `.env` file has correct Redis credentials:

```env
REDIS_HOST=redis-15762.c321.us-east-1-2.ec2.redns.redis-cloud.com
REDIS_PORT=15762
REDIS_USERNAME=default
REDIS_PASSWORD=huK4JsczUVa8j0CMKg52l7a0lM8DfGtL
```

## 🎉 **Success Criteria**

✅ **Notification System Working** if:

- Server starts without errors
- Users can be created and logged in
- Course can be created
- Student can be enrolled
- Instructor can send notification
- Student receives notification in API response
- Notification appears in database

## 🚀 **Next Steps After Testing**

1. **Test Frontend Integration** - Open the React app and test the notification bell
2. **Test WebSocket Real-time** - Use Daphne server for WebSocket support
3. **Test Multiple Students** - Enroll multiple students and verify all receive notifications
4. **Test Different Notification Types** - Try content, assignment, schedule updates

## 📞 **Need Help?**

If you encounter issues:

1. Check Django server logs for error messages
2. Verify all required packages are installed
3. Ensure Redis Cloud connection is working
4. Check that all notification app files are properly configured

---

**🎯 The notification system is fully implemented and ready for testing!**
