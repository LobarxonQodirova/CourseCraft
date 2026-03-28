import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify


class CourseCategory(models.Model):
    """Top-level and sub-level categories for courses."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class name")
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "course_categories"
        ordering = ["order", "name"]
        verbose_name_plural = "Course Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Course(models.Model):
    """Main course model representing a complete course offering."""

    class Level(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"
        ALL_LEVELS = "all_levels", "All Levels"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        REVIEW = "review", "In Review"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="courses_created"
    )
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=320, unique=True, blank=True)
    subtitle = models.CharField(max_length=500, blank=True)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to="courses/thumbnails/%Y/%m/", blank=True)
    promo_video = models.URLField(blank=True, help_text="URL to promotional video")
    category = models.ForeignKey(
        CourseCategory, on_delete=models.SET_NULL, null=True, related_name="courses"
    )
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.ALL_LEVELS)
    language = models.CharField(max_length=20, default="en")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default="USD")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    is_featured = models.BooleanField(default=False)
    is_free = models.BooleanField(default=False)
    requirements = models.JSONField(default=list, blank=True, help_text="Prerequisites list")
    what_you_learn = models.JSONField(default=list, blank=True, help_text="Learning outcomes")
    tags = models.JSONField(default=list, blank=True)
    total_duration = models.DurationField(null=True, blank=True)
    total_lessons = models.PositiveIntegerField(default=0)
    total_enrollments = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "courses"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "is_featured"]),
            models.Index(fields=["category", "level"]),
            models.Index(fields=["-average_rating"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Course.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        if self.price == 0:
            self.is_free = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def effective_price(self):
        if self.is_free:
            return 0
        return self.discount_price if self.discount_price else self.price


class CourseSection(models.Model):
    """A section within a course, grouping related lessons."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="sections")
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_preview = models.BooleanField(default=False, help_text="Free preview section")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "course_sections"
        ordering = ["order"]
        unique_together = ["course", "order"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    """Individual lesson within a course section."""

    class ContentType(models.TextChoices):
        VIDEO = "video", "Video"
        ARTICLE = "article", "Article"
        QUIZ = "quiz", "Quiz"
        ASSIGNMENT = "assignment", "Assignment"
        DOWNLOAD = "download", "Downloadable Resource"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section = models.ForeignKey(CourseSection, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=320, blank=True)
    content_type = models.CharField(
        max_length=20, choices=ContentType.choices, default=ContentType.VIDEO
    )
    order = models.PositiveIntegerField(default=0)
    is_preview = models.BooleanField(default=False, help_text="Freely accessible preview lesson")
    is_mandatory = models.BooleanField(default=True)
    duration = models.DurationField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lessons"
        ordering = ["order"]
        unique_together = ["section", "order"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def course(self):
        return self.section.course


class LessonContent(models.Model):
    """Actual content attached to a lesson (video URL, text, files)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name="content")
    video_url = models.URLField(blank=True, help_text="Video hosting URL (Vimeo, S3, etc.)")
    video_duration_seconds = models.PositiveIntegerField(default=0)
    text_content = models.TextField(blank=True, help_text="Markdown-formatted article content")
    attachment = models.FileField(upload_to="lessons/attachments/%Y/%m/", blank=True)
    resources = models.JSONField(
        default=list, blank=True,
        help_text="List of supplementary resource links and files"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "lesson_contents"
        verbose_name = "Lesson Content"
        verbose_name_plural = "Lesson Contents"

    def __str__(self):
        return f"Content: {self.lesson.title}"


class CourseEnrollment(models.Model):
    """Tracks student enrollment in a course."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments"
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed_at = models.DateTimeField(null=True, blank=True)
    progress_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        db_table = "course_enrollments"
        unique_together = ["course", "student"]
        ordering = ["-enrolled_at"]

    def __str__(self):
        return f"{self.student.email} -> {self.course.title}"


class CourseReview(models.Model):
    """Student review and rating for a course."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="reviews")
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField(blank=True)
    is_approved = models.BooleanField(default=True)
    helpful_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "course_reviews"
        unique_together = ["course", "student"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.student.email} rated {self.course.title}: {self.rating}/5"
