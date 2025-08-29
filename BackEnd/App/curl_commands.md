# API Testing with cURL Commands - Function-Based Views

## Prerequisites

1. Start your Django server: `python manage.py runserver`
2. Run migrations: `python manage.py makemigrations && python manage.py migrate`

## Authentication

### Register Instructor

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "instructor@test.com",
    "username": "instructor1",
    "password": "testpass123",
    "role": "instructor",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "instructor@test.com",
    "password": "testpass123"
  }'
```

## Questions API

### Create Question

```bash
curl -X POST http://localhost:8000/api/exams/questions/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "text": "What is the capital of France?",
    "question_type": "multiple_choice",
    "points": 5
  }'
```

### Get All Questions

```bash
curl -X GET http://localhost:8000/api/exams/questions/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Get Question Details

```bash
curl -X GET http://localhost:8000/api/exams/questions/1/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Update Question

```bash
curl -X PUT http://localhost:8000/api/exams/questions/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "text": "What is the capital of France? (Updated)",
    "question_type": "multiple_choice",
    "points": 10
  }'
```

### Delete Question

```bash
curl -X DELETE http://localhost:8000/api/exams/questions/1/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Get Questions by Type

```bash
curl -X GET "http://localhost:8000/api/exams/questions/by_type/?type=multiple_choice" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Search Questions

```bash
curl -X GET "http://localhost:8000/api/exams/questions/search/?q=Python" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Exams API

### Create Exam

```bash
curl -X POST http://localhost:8000/api/exams/exams/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "name": "Python Basics Exam"
  }'
```

### Get All Exams

```bash
curl -X GET http://localhost:8000/api/exams/exams/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Get Exam Details

```bash
curl -X GET http://localhost:8000/api/exams/exams/1/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Update Exam

```bash
curl -X PUT http://localhost:8000/api/exams/exams/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "name": "Python Basics Exam (Updated)"
  }'
```

### Delete Exam

```bash
curl -X DELETE http://localhost:8000/api/exams/exams/1/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Exam Questions Management

### Get Exam Questions

```bash
curl -X GET http://localhost:8000/api/exams/exams/1/questions/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Add Question to Exam

```bash
curl -X POST http://localhost:8000/api/exams/exams/1/add_question/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "question_id": 1,
    "order": 1
  }'
```

### Remove Question from Exam

```bash
curl -X DELETE http://localhost:8000/api/exams/exams/1/remove_question/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "question_id": 1
  }'
```

## Exam-Question Relationships

### Get All Relationships

```bash
curl -X GET http://localhost:8000/api/exams/exam-questions/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Get Relationships by Exam

```bash
curl -X GET "http://localhost:8000/api/exams/exam-questions/?exam_id=1" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Create Relationship

```bash
curl -X POST http://localhost:8000/api/exams/exam-questions/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "exam": 1,
    "question": 1,
    "order": 1
  }'
```

### Update Relationship

```bash
curl -X PUT http://localhost:8000/api/exams/exam-questions/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "exam": 1,
    "question": 1,
    "order": 2
  }'
```

### Delete Relationship

```bash
curl -X DELETE http://localhost:8000/api/exams/exam-questions/1/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Complete Test Flow

1. **Register and Login:**

```bash
# Register instructor
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email": "instructor@test.com", "username": "instructor1", "password": "testpass123", "role": "instructor", "first_name": "John", "last_name": "Doe"}'

# Login and get token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "instructor@test.com", "password": "testpass123"}'
```

2. **Create Questions:**

```bash
# Create multiple choice question
curl -X POST http://localhost:8000/api/exams/questions/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"text": "What is the capital of France?", "question_type": "multiple_choice", "points": 5}'

# Create true/false question
curl -X POST http://localhost:8000/api/exams/questions/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"text": "Is Python a programming language?", "question_type": "true_false", "points": 3}'
```

3. **Create Exam:**

```bash
curl -X POST http://localhost:8000/api/exams/exams/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"name": "Python Basics Exam"}'
```

4. **Add Questions to Exam:**

```bash
curl -X POST http://localhost:8000/api/exams/exams/1/add_question/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"question_id": 1, "order": 1}'

curl -X POST http://localhost:8000/api/exams/exams/1/add_question/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"question_id": 2, "order": 2}'
```

5. **Test Retrieval:**

```bash
# Get all questions
curl -X GET http://localhost:8000/api/exams/questions/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Get exam with questions
curl -X GET http://localhost:8000/api/exams/exams/1/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Get exam questions
curl -X GET http://localhost:8000/api/exams/exams/1/questions/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Search questions
curl -X GET "http://localhost:8000/api/exams/questions/search/?q=Python" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Get questions by type
curl -X GET "http://localhost:8000/api/exams/questions/by_type/?type=multiple_choice" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## URL Pattern Summary

### Questions:

- `GET    /api/exams/questions/` - List all questions
- `POST   /api/exams/questions/` - Create question
- `GET    /api/exams/questions/{id}/` - Get question details
- `PUT    /api/exams/questions/{id}/` - Update question
- `DELETE /api/exams/questions/{id}/` - Delete question
- `GET    /api/exams/questions/by_type/?type=` - Filter by type
- `GET    /api/exams/questions/search/?q=` - Search questions

### Exams:

- `GET    /api/exams/exams/` - List all exams
- `POST   /api/exams/exams/` - Create exam
- `GET    /api/exams/exams/{id}/` - Get exam details
- `PUT    /api/exams/exams/{id}/` - Update exam
- `DELETE /api/exams/exams/{id}/` - Delete exam
- `GET    /api/exams/exams/{id}/questions/` - Get exam questions
- `POST   /api/exams/exams/{id}/add_question/` - Add question to exam
- `DELETE /api/exams/exams/{id}/remove_question/` - Remove question from exam

### Exam-Question Relationships:

- `GET    /api/exams/exam-questions/` - List relationships
- `POST   /api/exams/exam-questions/` - Create relationship
- `GET    /api/exams/exam-questions/{id}/` - Get relationship details
- `PUT    /api/exams/exam-questions/{id}/` - Update relationship
- `DELETE /api/exams/exam-questions/{id}/` - Delete relationship

## Notes

- Replace `YOUR_TOKEN_HERE` with the actual JWT token from login
- Replace IDs (1, 2, etc.) with actual IDs from your database
- All endpoints require authentication except registration and login
- Only instructors can create questions and exams
- Students can view all questions and exams
- Function-based views provide better control and readability
