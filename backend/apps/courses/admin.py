from django.contrib import admin

from .models import (
    Course,
    CourseCategory,
    CourseEnrollment,
    CourseReview,
    CourseSection,
    Lesson,
    LessonContent,
)


class CourseSectionInline(admin.TabularInline):
    model = CourseSection
    extra = 0
    ordering = ["order"]


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    ordering = ["order"]


@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent", "is_active", "order")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "title", "instructor", "category", "level", "status",
        "price", "is_free", "is_featured", "average_rating",
        "total_enrollments", "created_at",
    )
    list_filter = ("status", "level", "is_free", "is_featured", "category")
    search_fields = ("title", "subtitle", "description", "instructor__email")
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ("instructor", "category")
    readonly_fields = (
        "total_enrollments", "average_rating", "total_reviews",
        "total_lessons", "total_duration", "created_at", "updated_at",
    )
    inlines = [CourseSectionInline]
    date_hierarchy = "created_at"


@admin.register(CourseSection)
class CourseSectionAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order", "is_preview")
    list_filter = ("is_preview",)
    raw_id_fields = ("course",)
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "section", "content_type", "order", "is_preview", "is_mandatory", "duration")
    list_filter = ("content_type", "is_preview", "is_mandatory")
    search_fields = ("title",)
    raw_id_fields = ("section",)


@admin.register(LessonContent)
class LessonContentAdmin(admin.ModelAdmin):
    list_display = ("lesson", "video_duration_seconds")
    raw_id_fields = ("lesson",)


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "enrolled_at", "is_active", "progress_percent", "completed_at")
    list_filter = ("is_active",)
    search_fields = ("student__email", "course__title")
    raw_id_fields = ("student", "course")
    date_hierarchy = "enrolled_at"


@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "rating", "is_approved", "helpful_count", "created_at")
    list_filter = ("rating", "is_approved")
    search_fields = ("student__email", "course__title", "comment")
    raw_id_fields = ("student", "course")
