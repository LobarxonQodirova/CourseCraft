"""Analytics computation services."""

import logging
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Sum, Q

from apps.courses.models import Course, CourseEnrollment, CourseReview
from apps.payments.models import Payment
from apps.progress.models import CourseProgress, LessonProgress

from .models import DailyCourseStat, DailyPlatformStat, InstructorDailyStat

logger = logging.getLogger(__name__)
User = get_user_model()


def calculate_course_stats(course, stat_date=None):
    """Calculate daily statistics for a single course."""
    stat_date = stat_date or date.today() - timedelta(days=1)

    enrollments = CourseEnrollment.objects.filter(
        course=course, enrolled_at__date=stat_date
    ).count()

    completions = CourseProgress.objects.filter(
        course=course, is_completed=True, completed_at__date=stat_date
    ).count()

    revenue = Payment.objects.filter(
        course=course, status="completed", created_at__date=stat_date
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

    watch_time = LessonProgress.objects.filter(
        lesson__section__course=course, updated_at__date=stat_date
    ).aggregate(total=Sum("watch_time_seconds"))["total"] or 0

    review_stats = CourseReview.objects.filter(
        course=course, created_at__date=stat_date
    ).aggregate(avg=Avg("rating"), count=Count("id"))

    stat, _ = DailyCourseStat.objects.update_or_create(
        course=course,
        date=stat_date,
        defaults={
            "enrollments": enrollments,
            "completions": completions,
            "revenue": revenue,
            "watch_time_minutes": watch_time // 60,
            "avg_rating": review_stats["avg"] or 0,
            "reviews_count": review_stats["count"] or 0,
        },
    )
    return stat


def calculate_instructor_stats(instructor, stat_date=None):
    """Calculate daily statistics for an instructor."""
    stat_date = stat_date or date.today() - timedelta(days=1)
    courses = Course.objects.filter(instructor=instructor)

    total_students = CourseEnrollment.objects.filter(
        course__in=courses, is_active=True
    ).values("student").distinct().count()

    new_enrollments = CourseEnrollment.objects.filter(
        course__in=courses, enrolled_at__date=stat_date
    ).count()

    daily_revenue = Payment.objects.filter(
        course__in=courses, status="completed", created_at__date=stat_date
    ).aggregate(total=Sum("instructor_share"))["total"] or Decimal("0")

    total_revenue = Payment.objects.filter(
        course__in=courses, status="completed"
    ).aggregate(total=Sum("instructor_share"))["total"] or Decimal("0")

    review_stats = CourseReview.objects.filter(
        course__in=courses, is_approved=True
    ).aggregate(avg=Avg("rating"), count=Count("id"))

    watch_time = LessonProgress.objects.filter(
        lesson__section__course__in=courses, updated_at__date=stat_date
    ).aggregate(total=Sum("watch_time_seconds"))["total"] or 0

    stat, _ = InstructorDailyStat.objects.update_or_create(
        instructor=instructor,
        date=stat_date,
        defaults={
            "total_students": total_students,
            "new_enrollments": new_enrollments,
            "daily_revenue": daily_revenue,
            "total_revenue": total_revenue,
            "avg_rating": review_stats["avg"] or 0,
            "total_reviews": review_stats["count"] or 0,
            "total_watch_time_minutes": watch_time // 60,
        },
    )
    return stat


def calculate_platform_stats(stat_date=None):
    """Calculate daily platform-wide statistics."""
    stat_date = stat_date or date.today() - timedelta(days=1)

    total_users = User.objects.filter(is_active=True).count()
    new_users = User.objects.filter(created_at__date=stat_date).count()

    total_courses = Course.objects.filter(status="published").count()
    new_courses = Course.objects.filter(published_at__date=stat_date).count()

    total_enrollments = CourseEnrollment.objects.filter(is_active=True).count()
    new_enrollments = CourseEnrollment.objects.filter(enrolled_at__date=stat_date).count()

    total_revenue = Payment.objects.filter(
        status="completed"
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

    daily_revenue = Payment.objects.filter(
        status="completed", created_at__date=stat_date
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0")

    watch_time = LessonProgress.objects.filter(
        updated_at__date=stat_date
    ).aggregate(total=Sum("watch_time_seconds"))["total"] or 0

    stat, _ = DailyPlatformStat.objects.update_or_create(
        date=stat_date,
        defaults={
            "total_users": total_users,
            "new_users": new_users,
            "total_courses": total_courses,
            "new_courses": new_courses,
            "total_enrollments": total_enrollments,
            "new_enrollments": new_enrollments,
            "total_revenue": total_revenue,
            "daily_revenue": daily_revenue,
            "total_watch_time_minutes": watch_time // 60,
        },
    )
    return stat


def get_instructor_dashboard_summary(instructor):
    """Get summary data for the instructor dashboard."""
    courses = Course.objects.filter(instructor=instructor)

    total_students = CourseEnrollment.objects.filter(
        course__in=courses, is_active=True
    ).values("student").distinct().count()

    total_revenue = Payment.objects.filter(
        course__in=courses, status="completed"
    ).aggregate(total=Sum("instructor_share"))["total"] or Decimal("0")

    avg_rating = CourseReview.objects.filter(
        course__in=courses, is_approved=True
    ).aggregate(avg=Avg("rating"))["avg"] or 0

    return {
        "total_courses": courses.count(),
        "published_courses": courses.filter(status="published").count(),
        "total_students": total_students,
        "total_revenue": str(total_revenue),
        "average_rating": round(float(avg_rating), 2),
        "total_reviews": CourseReview.objects.filter(course__in=courses).count(),
    }
