import uuid

from django.conf import settings
from django.db import models


class DailyCourseStat(models.Model):
    """Daily aggregated statistics for a course."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(
        "courses.Course", on_delete=models.CASCADE, related_name="daily_stats"
    )
    date = models.DateField(db_index=True)
    views = models.PositiveIntegerField(default=0)
    unique_visitors = models.PositiveIntegerField(default=0)
    enrollments = models.PositiveIntegerField(default=0)
    completions = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    watch_time_minutes = models.PositiveIntegerField(default=0)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    reviews_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "daily_course_stats"
        unique_together = ["course", "date"]
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["course", "-date"]),
        ]

    def __str__(self):
        return f"{self.course.title} - {self.date}"


class DailyPlatformStat(models.Model):
    """Daily platform-wide statistics."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(unique=True, db_index=True)
    total_users = models.PositiveIntegerField(default=0)
    new_users = models.PositiveIntegerField(default=0)
    active_users = models.PositiveIntegerField(default=0)
    total_courses = models.PositiveIntegerField(default=0)
    new_courses = models.PositiveIntegerField(default=0)
    total_enrollments = models.PositiveIntegerField(default=0)
    new_enrollments = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    daily_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_watch_time_minutes = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "daily_platform_stats"
        ordering = ["-date"]

    def __str__(self):
        return f"Platform Stats - {self.date}"


class InstructorDailyStat(models.Model):
    """Daily statistics for an instructor across all their courses."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="daily_stats"
    )
    date = models.DateField(db_index=True)
    total_students = models.PositiveIntegerField(default=0)
    new_enrollments = models.PositiveIntegerField(default=0)
    daily_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_revenue = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    total_watch_time_minutes = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "instructor_daily_stats"
        unique_together = ["instructor", "date"]
        ordering = ["-date"]

    def __str__(self):
        return f"{self.instructor.email} - {self.date}"
