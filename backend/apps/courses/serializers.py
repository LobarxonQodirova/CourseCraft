from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import (
    Course,
    CourseCategory,
    CourseEnrollment,
    CourseReview,
    CourseSection,
    Lesson,
    LessonContent,
)

User = get_user_model()


class CourseCategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    course_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = CourseCategory
        fields = ("id", "name", "slug", "description", "icon", "parent", "children", "course_count")

    def get_children(self, obj):
        children = obj.children.filter(is_active=True)
        return CourseCategorySerializer(children, many=True).data


class InstructorSummarySerializer(serializers.ModelSerializer):
    display_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ("id", "display_name", "avatar", "bio")


class LessonContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonContent
        fields = (
            "id", "video_url", "video_duration_seconds", "text_content",
            "attachment", "resources",
        )


class LessonSerializer(serializers.ModelSerializer):
    content = LessonContentSerializer(read_only=True)

    class Meta:
        model = Lesson
        fields = (
            "id", "title", "slug", "content_type", "order",
            "is_preview", "is_mandatory", "duration", "content",
        )


class LessonCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ("id", "section", "title", "content_type", "order", "is_preview", "is_mandatory", "duration")
        read_only_fields = ("id",)


class CourseSectionSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    lesson_count = serializers.SerializerMethodField()

    class Meta:
        model = CourseSection
        fields = ("id", "title", "description", "order", "is_preview", "lessons", "lesson_count")

    def get_lesson_count(self, obj):
        return obj.lessons.count()


class CourseSectionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseSection
        fields = ("id", "course", "title", "description", "order", "is_preview")
        read_only_fields = ("id",)


class CourseListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing courses."""

    instructor = InstructorSummarySerializer(read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)
    effective_price = serializers.ReadOnlyField()

    class Meta:
        model = Course
        fields = (
            "id", "title", "slug", "subtitle", "thumbnail",
            "instructor", "category_name", "level", "price",
            "discount_price", "effective_price", "is_free",
            "average_rating", "total_reviews", "total_enrollments",
            "total_duration", "total_lessons", "created_at",
        )


class CourseDetailSerializer(serializers.ModelSerializer):
    """Full serializer with sections and lessons for course detail page."""

    instructor = InstructorSummarySerializer(read_only=True)
    category = CourseCategorySerializer(read_only=True)
    sections = CourseSectionSerializer(many=True, read_only=True)
    effective_price = serializers.ReadOnlyField()
    is_enrolled = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            "id", "title", "slug", "subtitle", "description",
            "thumbnail", "promo_video", "instructor", "category",
            "level", "language", "price", "discount_price",
            "effective_price", "currency", "is_free", "is_featured",
            "requirements", "what_you_learn", "tags",
            "total_duration", "total_lessons", "total_enrollments",
            "average_rating", "total_reviews", "status",
            "sections", "is_enrolled", "published_at", "created_at",
        )

    def get_is_enrolled(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.enrollments.filter(student=request.user, is_active=True).exists()
        return False


class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            "id", "title", "subtitle", "description", "thumbnail",
            "promo_video", "category", "level", "language",
            "price", "discount_price", "currency", "is_free",
            "requirements", "what_you_learn", "tags",
        )
        read_only_fields = ("id",)

    def create(self, validated_data):
        validated_data["instructor"] = self.context["request"].user
        return super().create(validated_data)


class CourseEnrollmentSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)

    class Meta:
        model = CourseEnrollment
        fields = (
            "id", "course", "enrolled_at", "is_active",
            "completed_at", "last_accessed_at", "progress_percent",
        )


class CourseReviewSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.display_name", read_only=True)
    student_avatar = serializers.ImageField(source="student.avatar", read_only=True)

    class Meta:
        model = CourseReview
        fields = (
            "id", "course", "student_name", "student_avatar",
            "rating", "title", "comment", "helpful_count", "created_at",
        )
        read_only_fields = ("id", "helpful_count", "created_at")

    def create(self, validated_data):
        validated_data["student"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, attrs):
        course = attrs.get("course")
        user = self.context["request"].user
        if not CourseEnrollment.objects.filter(course=course, student=user, is_active=True).exists():
            raise serializers.ValidationError("You must be enrolled in this course to leave a review.")
        if CourseReview.objects.filter(course=course, student=user).exists():
            raise serializers.ValidationError("You have already reviewed this course.")
        return attrs
