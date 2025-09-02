from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count

from courses.models import Category, Course
from courses.serializers import CategorySerializer


def _forbidden_if_not_admin(request):
    if not getattr(request.user, "role", None) == "admin":
        return Response({"error": "Forbidden"}, status=403)
    return None


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_categories(request):
    forbidden = _forbidden_if_not_admin(request)
    if forbidden:
        return forbidden
    search = request.query_params.get("search", "").strip()
    qs = Category.objects.all().annotate(courses_count=Count("courses"))
    if search:
        qs = qs.filter(name__icontains=search)
    serializer = CategorySerializer(qs, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_category(request):
    forbidden = _forbidden_if_not_admin(request)
    if forbidden:
        return forbidden
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_category(request, pk: int):
    forbidden = _forbidden_if_not_admin(request)
    if forbidden:
        return forbidden
    cat = Category.objects.filter(pk=pk).first()
    if not cat:
        return Response({"error": "Not found"}, status=404)
    serializer = CategorySerializer(cat, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_category(request, pk: int):
    forbidden = _forbidden_if_not_admin(request)
    if forbidden:
        return forbidden
    cat = Category.objects.filter(pk=pk).first()
    if not cat:
        return Response({"error": "Not found"}, status=404)
    # optional: prevent delete if there are courses
    if Course.objects.filter(category=cat).exists():
        return Response({"error": "Cannot delete: category has courses"}, status=400)
    cat.delete()
    return Response(status=204)


urlpatterns = [
    path("", list_categories, name="admin_categories_list"),
    path("<int:pk>/", update_category, name="admin_categories_update"),
    path("<int:pk>/delete/", delete_category, name="admin_categories_delete"),
    path("create/", create_category, name="admin_categories_create"),
]
