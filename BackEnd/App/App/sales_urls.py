from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Sum
from django.db.models.functions import TruncDay, TruncWeek
from django.utils import timezone
from datetime import timedelta

from courses.models import Course, Enrollment


def _forbidden_if_not_admin(request):
    if not getattr(request.user, "role", None) == "admin":
        return Response({"error": "Forbidden"}, status=403)
    return None


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def sales_per_course(request):
    forbidden = _forbidden_if_not_admin(request)
    if forbidden:
        return forbidden

    # Count paid enrollments per course and sum revenue as sum of course.price over enrollments
    rows = (
        Enrollment.objects.select_related("course")
        .values("course_id", "course__title")
        .annotate(sales=Count("id"), revenue=Sum("course__price"))
        .order_by("-sales")[:200]
    )

    data = [
        {
            "course": r["course__title"] or "Unknown",
            "sales": int(r["sales"] or 0),
            "revenue": float(r["revenue"] or 0),
        }
        for r in rows
    ]
    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def sales_per_category(request):
    forbidden = _forbidden_if_not_admin(request)
    if forbidden:
        return forbidden

    rows = (
        Enrollment.objects.select_related("course", "course__category")
        .values("course__category__name")
        .annotate(sales=Count("id"), revenue=Sum("course__price"))
        .order_by("-sales")
    )

    data = [
        {
            "name": r["course__category__name"] or "Uncategorized",
            "value": int(r["sales"] or 0),  # primary for pie percentage
            "sales": int(r["sales"] or 0),
            "revenue": float(r["revenue"] or 0),
        }
        for r in rows
    ]
    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def revenue_trends(request):
    forbidden = _forbidden_if_not_admin(request)
    if forbidden:
        return forbidden

    range_param = request.query_params.get("range", "last_month")
    now = timezone.now()

    if range_param == "last_3_months":
        start = now - timedelta(days=90)
        qs = (
            Enrollment.objects.filter(enrolled_at__gte=start)
            .annotate(period=TruncWeek("enrolled_at"))
            .values("period")
            .annotate(revenue=Sum("course__price"))
            .order_by("period")
        )
        points = [
            {
                "date": (row["period"].date() if hasattr(row["period"], "date") else row["period"]).isoformat(),
                "revenue": float(row["revenue"] or 0),
            }
            for row in qs
        ]
        return Response(points)

    # Default: last month daily
    start = now - timedelta(days=30)
    qs = (
        Enrollment.objects.filter(enrolled_at__gte=start)
        .annotate(period=TruncDay("enrolled_at"))
        .values("period")
        .annotate(revenue=Sum("course__price"))
        .order_by("period")
    )
    points = [
        {
            "date": (row["period"].date() if hasattr(row["period"], "date") else row["period"]).isoformat(),
            "revenue": float(row["revenue"] or 0),
        }
        for row in qs
    ]
    return Response(points)


urlpatterns = [
    path("courses/", sales_per_course, name="admin_sales_courses"),
    path("categories/", sales_per_category, name="admin_sales_categories"),
    path("revenue/", revenue_trends, name="admin_sales_revenue"),
]
