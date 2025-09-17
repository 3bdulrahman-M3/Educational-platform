from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Sum

from courses.models import Course, Enrollment
from django.db.models import Q
from transactions.models import Transaction


def _forbidden_if_not_instructor(request, instructor_id: int):
    user = getattr(request, "user", None)
    if not user or user.role != "instructor" or user.id != int(instructor_id):
        return Response({"error": "Forbidden"}, status=403)
    return None


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard(request, instructor_id: int):
    forbidden = _forbidden_if_not_instructor(request, instructor_id)
    if forbidden:
        return forbidden

    # Courses by this instructor
    courses_qs = Course.objects.filter(instructor_id=instructor_id)

    # Enrollments per course and completion counts
    enrollments_qs = (
        Enrollment.objects.filter(course__in=courses_qs)
        .values("course_id", "course__title")
        .annotate(
            students=Count("id"),
            completed=Count("id", filter=Q(completed_at__isnull=False))
        )
    )

    # Transactions-based revenue (successful only)
    tx_qs = (
        Transaction.objects.filter(
            course__in=courses_qs,
            payment_status="completed",
        )
        .values("course_id", "course__title")
        .annotate(
            sales=Count("id"),
            revenue=Sum("amount")
        )
    )

    # Aggregate totals
    total_students = 0
    course_map = {}
    for row in enrollments_qs:
        cid = row["course_id"]
        course_map[cid] = {
            "course_id": cid,
            "course": row["course__title"],
            "students": int(row.get("students") or 0),
            "completed": int(row.get("completed") or 0),
            "sales": 0,
            "revenue": 0.0,
        }
        total_students += course_map[cid]["students"]

    total_revenue = 0.0
    total_balance = 0.0
    for row in tx_qs:
        cid = row["course_id"]
        info = course_map.setdefault(
            cid,
            {
                "course_id": cid,
                "course": row["course__title"],
                "students": 0,
                "completed": 0,
                "sales": 0,
                "revenue": 0.0,
            },
        )
        info["sales"] = int(row.get("sales") or 0)
        revenue_val = float(row.get("revenue") or 0)
        info["revenue"] = revenue_val
        total_revenue += revenue_val
        total_balance += revenue_val  # assuming 100% to instructor; adjust if needed

    # Return normalized list
    per_course = list(course_map.values())
    per_course.sort(key=lambda r: r.get("sales", 0), reverse=True)

    return Response(
        {
            "summary": {
                "balance": float(round(total_balance, 2)),
                "total_revenue": float(round(total_revenue, 2)),
                "total_students": int(total_students),
            },
            "by_course": per_course,
        }
    )


urlpatterns = [
    path("<int:instructor_id>/dashboard/",
         dashboard, name="instructor_dashboard"),
]
