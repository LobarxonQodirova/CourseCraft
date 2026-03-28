from django.db.models import Count, Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.permissions import IsEnrolledOrInstructor, IsInstructor, IsInstructorOfCourse

from .models import (
    Course,
    CourseCategory,
    CourseEnrollment,
    CourseReview,
    CourseSection,
    Lesson,
    LessonContent,
)
from .serializers import (
    CourseCategorySerializer,
    CourseCreateSerializer,
    CourseDetailSerializer,
    CourseEnrollmentSerializer,
    CourseListSerializer,
    CourseReviewSerializer,
    CourseSectionCreateSerializer,
    CourseSectionSerializer,
    LessonContentSerializer,
    LessonCreateSerializer,
    LessonSerializer,
)


class CourseCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve course categories."""

    queryset = CourseCategory.objects.filter(is_active=True, parent__isnull=True)
    serializer_class = CourseCategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.annotate(course_count=Count("courses", filter=Q(courses__status="published")))


class CourseViewSet(viewsets.ModelViewSet):
    """CRUD operations for courses with filtering and search."""

    lookup_field = "slug"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category__slug", "level", "is_free", "language"]
    search_fields = ["title", "subtitle", "description", "tags"]
    ordering_fields = ["created_at", "price", "average_rating", "total_enrollments"]
    ordering = ["-created_at"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        if self.action == "create":
            return [permissions.IsAuthenticated(), IsInstructor()]
        return [permissions.IsAuthenticated(), IsInstructorOfCourse()]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CourseDetailSerializer
        if self.action in ("create", "update", "partial_update"):
            return CourseCreateSerializer
        return CourseListSerializer

    def get_queryset(self):
        qs = Course.objects.select_related("instructor", "category")
        if self.action in ("list", "retrieve"):
            if not (self.request.user.is_authenticated and self.request.user.is_creator):
                qs = qs.filter(status="published")
        else:
            qs = qs.filter(instructor=self.request.user)
        return qs

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def enroll(self, request, slug=None):
        """Enroll the authenticated user in this course."""
        course = self.get_object()
        if CourseEnrollment.objects.filter(course=course, student=request.user).exists():
            return Response(
                {"detail": "Already enrolled in this course."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not course.is_free:
            return Response(
                {"detail": "Payment required. Use the payments API to purchase."},
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )
        enrollment = CourseEnrollment.objects.create(course=course, student=request.user)
        course.total_enrollments += 1
        course.save(update_fields=["total_enrollments"])
        return Response(
            CourseEnrollmentSerializer(enrollment).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def my_courses(self, request):
        """List courses the authenticated user is enrolled in."""
        enrollments = CourseEnrollment.objects.filter(
            student=request.user, is_active=True
        ).select_related("course__instructor", "course__category")
        page = self.paginate_queryset(enrollments)
        serializer = CourseEnrollmentSerializer(page or enrollments, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(
        detail=False, methods=["get"],
        permission_classes=[permissions.IsAuthenticated, IsInstructor],
        url_path="instructor-courses",
    )
    def instructor_courses(self, request):
        """List courses created by the authenticated instructor."""
        courses = Course.objects.filter(instructor=request.user).select_related("category")
        page = self.paginate_queryset(courses)
        serializer = CourseListSerializer(page or courses, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    @action(
        detail=True, methods=["post"],
        permission_classes=[permissions.IsAuthenticated, IsInstructorOfCourse],
    )
    def publish(self, request, slug=None):
        """Publish a draft course."""
        course = self.get_object()
        if course.sections.count() == 0:
            return Response(
                {"detail": "Course must have at least one section with lessons."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        course.status = Course.Status.PUBLISHED
        course.published_at = timezone.now()
        course.save(update_fields=["status", "published_at"])
        return Response({"detail": "Course published successfully."})


class CourseSectionViewSet(viewsets.ModelViewSet):
    """CRUD for course sections."""

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated(), IsEnrolledOrInstructor()]
        return [permissions.IsAuthenticated(), IsInstructor()]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return CourseSectionCreateSerializer
        return CourseSectionSerializer

    def get_queryset(self):
        return CourseSection.objects.filter(
            course__slug=self.kwargs.get("course_slug")
        ).prefetch_related("lessons__content")


class LessonViewSet(viewsets.ModelViewSet):
    """CRUD for lessons within a section."""

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsInstructor()]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return LessonCreateSerializer
        return LessonSerializer

    def get_queryset(self):
        return Lesson.objects.filter(
            section_id=self.kwargs.get("section_pk")
        ).select_related("content")


class CourseReviewViewSet(viewsets.ModelViewSet):
    """CRUD for course reviews."""

    serializer_class = CourseReviewSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        return CourseReview.objects.filter(
            course__slug=self.kwargs.get("course_slug"),
            is_approved=True,
        ).select_related("student")

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def helpful(self, request, **kwargs):
        """Mark a review as helpful."""
        review = self.get_object()
        review.helpful_count += 1
        review.save(update_fields=["helpful_count"])
        return Response({"helpful_count": review.helpful_count})
