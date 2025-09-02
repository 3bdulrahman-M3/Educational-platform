# views.py
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import requests
import os
from courses.models import Course

HF_TOKEN = os.getenv("HF_API_KEY")  # store your HF token in .env
MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.3"
PROVIDER = "together"
API_URL = f"https://router.huggingface.co/{PROVIDER}/v1/chat/completions"
MAX_HISTORY = 10

# Optional: store conversation history per user (simplest: in memory)
conversation_history = []

@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def chatbot(request):
    user_message = request.data.get("message")
    if not user_message:
        return Response({"error": "Message is required"}, status=400)

    try:
        global conversation_history

        # Get courses from your DB and build context
        courses = Course.objects.select_related("category", "instructor").all()
        course_text = "\n".join([
            f"Course: {c.title}\n"
            f"Description: {c.description}\n"
            f"Category: {c.category.name if c.category else 'Uncategorized'}\n"
            f"Instructor: {c.instructor.first_name} {c.instructor.last_name if c.instructor else 'Unknown'}\n"
            f"Level: {c.level}\n"
            f"Language: {c.language}\n"
            for c in courses
        ])

        # FAQs
        FAQS = {
            "how do i become an instructor": (
                "To become an instructor, go to your profile and apply for an instructor account. "
                "An admin will review your request and inform you of the results."
            ),
            "refund policy": "We currently do not offer refunds after a course has been purchased.",
            "payment methods": "We currently support credit cards and PayPal for payments.",
        }

        # Add user message to conversation history
        conversation_history.append({"role": "user", "content": f"{user_message}\n\nCourses:\n{course_text}\n\nFAQs:\n" + "\n".join([f"- {q}: {a}" for q, a in FAQS.items()])})

        # Limit conversation history
        if len(conversation_history) > MAX_HISTORY:
            conversation_history = conversation_history[-MAX_HISTORY:]

        payload = {
            "model": MODEL_ID,
            "messages": conversation_history,
            "temperature": 0.7,
            "max_tokens": 1000
        }

        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {HF_TOKEN}",
                "Content-Type": "application/json"
            },
            json=payload
        )

        if not response.ok:
            return Response({"error": f"HF API returned {response.status_code}: {response.text}"}, status=500)

        data = response.json()
        assistant_message = data["choices"][0]["message"]["content"]

        # Add assistant reply to history
        conversation_history.append({"role": "assistant", "content": assistant_message})

        return Response({"response": assistant_message})

    except Exception as e:
        return Response({"error": str(e)}, status=500)
