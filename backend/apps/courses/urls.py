from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "courses"

router = DefaultRouter()
router.register(r"categories", views.CourseCategoryViewSet, basename="category")
router.register(r"", views.CourseViewSet, basename="course")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "<slug:course_slug>/sections/",
        views.CourseSectionViewSet.as_view({"get": "list", "post": "create"}),
        name="course-sections",
    ),
    path(
        "<slug:course_slug>/sections/<uuid:pk>/",
        views.CourseSectionViewSet.as_view({"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}),
        name="course-section-detail",
    ),
    path(
        "<slug:course_slug>/reviews/",
        views.CourseReviewViewSet.as_view({"get": "list", "post": "create"}),
        name="course-reviews",
    ),
    path(
        "<slug:course_slug>/reviews/<uuid:pk>/",
        views.CourseReviewViewSet.as_view({"get": "retrieve", "put": "update", "delete": "destroy"}),
        name="course-review-detail",
    ),
]
