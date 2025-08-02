import requests
import json

# Base URL for your Django server
BASE_URL = "http://localhost:8000/api"

# Test data
test_users = {
    "instructor": {
        "email": "instructor@test.com",
        "username": "instructor1",
        "password": "testpass123",
        "role": "instructor",
        "first_name": "John",
        "last_name": "Doe"
    },
    "student": {
        "email": "student@test.com",
        "username": "student1",
        "password": "testpass123",
        "role": "student",
        "first_name": "Jane",
        "last_name": "Smith"
    }
}

test_questions = [
    {
        "text": "What is the capital of France?",
        "question_type": "multiple_choice",
        "points": 5
    },
    {
        "text": "Is Python a programming language?",
        "question_type": "true_false",
        "points": 3
    },
    {
        "text": "Explain the concept of object-oriented programming.",
        "question_type": "essay",
        "points": 10
    },
    {
        "text": "What is the output of 2 + 2?",
        "question_type": "short_answer",
        "points": 2
    }
]

test_exams = [
    {
        "name": "Python Basics Exam"
    },
    {
        "name": "Web Development Quiz"
    }
]


def test_api():
    print("🚀 Testing Educational Platform API with Function-Based Views")
    print("=" * 60)

    # 1. Register users
    print("\n1. Registering test users...")
    for role, user_data in test_users.items():
        response = requests.post(f"{BASE_URL}/auth/register/", json=user_data)
        if response.status_code == 201:
            print(f"✅ {role.capitalize()} registered successfully")
        else:
            print(f"❌ Failed to register {role}: {response.text}")

    # 2. Login as instructor
    print("\n2. Logging in as instructor...")
    login_data = {
        "email": test_users["instructor"]["email"],
        "password": test_users["instructor"]["password"]
    }
    response = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
    if response.status_code == 200:
        token = response.json().get("access")
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Instructor logged in successfully")
    else:
        print(f"❌ Login failed: {response.text}")
        return

    # 3. Create questions
    print("\n3. Creating test questions...")
    question_ids = []
    for question_data in test_questions:
        response = requests.post(f"{BASE_URL}/exams/questions/",
                                 json=question_data, headers=headers)
        if response.status_code == 201:
            question_id = response.json()["id"]
            question_ids.append(question_id)
            print(f"✅ Question created: {question_data['text'][:30]}...")
        else:
            print(f"❌ Failed to create question: {response.text}")

    # 4. Create exams
    print("\n4. Creating test exams...")
    exam_ids = []
    for exam_data in test_exams:
        response = requests.post(f"{BASE_URL}/exams/exams/",
                                 json=exam_data, headers=headers)
        if response.status_code == 201:
            exam_id = response.json()["id"]
            exam_ids.append(exam_id)
            print(f"✅ Exam created: {exam_data['name']}")
        else:
            print(f"❌ Failed to create exam: {response.text}")

    # 5. Add questions to exams
    print("\n5. Adding questions to exams...")
    for i, exam_id in enumerate(exam_ids):
        for j, question_id in enumerate(question_ids):
            if i == 0:  # Add all questions to first exam
                add_data = {"question_id": question_id, "order": j}
                response = requests.post(f"{BASE_URL}/exams/exams/{exam_id}/add_question/",
                                         json=add_data, headers=headers)
                if response.status_code == 201:
                    print(f"✅ Question {question_id} added to exam {exam_id}")
                else:
                    print(f"❌ Failed to add question: {response.text}")

    # 6. Test API endpoints
    print("\n6. Testing API endpoints...")

    # Get all questions
    response = requests.get(f"{BASE_URL}/exams/questions/", headers=headers)
    if response.status_code == 200:
        questions = response.json()
        print(f"✅ Retrieved {len(questions)} questions")

    # Get questions by type
    response = requests.get(
        f"{BASE_URL}/exams/questions/by_type/?type=multiple_choice", headers=headers)
    if response.status_code == 200:
        mc_questions = response.json()
        print(f"✅ Retrieved {len(mc_questions)} multiple choice questions")

    # Search questions
    response = requests.get(
        f"{BASE_URL}/exams/questions/search/?q=Python", headers=headers)
    if response.status_code == 200:
        search_results = response.json()
        print(f"✅ Found {len(search_results)} questions containing 'Python'")

    # Get all exams
    response = requests.get(f"{BASE_URL}/exams/exams/", headers=headers)
    if response.status_code == 200:
        exams = response.json()
        print(f"✅ Retrieved {len(exams)} exams")

    # Get exam questions
    if exam_ids:
        response = requests.get(
            f"{BASE_URL}/exams/exams/{exam_ids[0]}/questions/", headers=headers)
        if response.status_code == 200:
            exam_questions = response.json()
            print(
                f"✅ Retrieved {len(exam_questions)} questions for exam {exam_ids[0]}")

    print("\n🎉 API testing completed!")
    print("\n📋 Available endpoints:")
    print("GET    /api/exams/questions/                    - List all questions")
    print("POST   /api/exams/questions/                    - Create new question")
    print(
        "GET    /api/exams/questions/{id}/               - Get question details")
    print("PUT    /api/exams/questions/{id}/               - Update question")
    print("DELETE /api/exams/questions/{id}/               - Delete question")
    print("GET    /api/exams/questions/by_type/?type=     - Get questions by type")
    print("GET    /api/exams/questions/search/?q=          - Search questions")
    print("GET    /api/exams/exams/                        - List all exams")
    print("POST   /api/exams/exams/                        - Create new exam")
    print("GET    /api/exams/exams/{id}/                   - Get exam details")
    print("PUT    /api/exams/exams/{id}/                   - Update exam")
    print("DELETE /api/exams/exams/{id}/                   - Delete exam")
    print(
        "GET    /api/exams/exams/{id}/questions/         - Get exam questions")
    print(
        "POST   /api/exams/exams/{id}/add_question/      - Add question to exam")
    print(
        "DELETE /api/exams/exams/{id}/remove_question/   - Remove question from exam")
    print("GET    /api/exams/exam-questions/               - List exam-question relationships")
    print("POST   /api/exams/exam-questions/               - Create exam-question relationship")
    print(
        "GET    /api/exams/exam-questions/{id}/          - Get relationship details")
    print(
        "PUT    /api/exams/exam-questions/{id}/          - Update relationship")
    print(
        "DELETE /api/exams/exam-questions/{id}/          - Delete relationship")


if __name__ == "__main__":
    test_api()
