"""Celery tasks for notifications."""

import logging
from datetime import timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task(name="apps.notifications.tasks.send_progress_reminders")
def send_progress_reminders():
    """Send reminder emails to students who haven't engaged in 3+ days."""
    from apps.courses.models import CourseEnrollment
    from apps.progress.models import CourseProgress
    from .services import create_notification, send_notification_email

    cutoff = timezone.now() - timedelta(days=3)

    stale_enrollments = CourseEnrollment.objects.filter(
        is_active=True,
        completed_at__isnull=True,
        last_accessed_at__lt=cutoff,
    ).select_related("student", "course")[:100]

    sent_count = 0
    for enrollment in stale_enrollments:
        student = enrollment.student
        course = enrollment.course

        progress = CourseProgress.objects.filter(
            student=student, course=course
        ).first()
        progress_pct = progress.progress_percent if progress else 0

        create_notification(
            recipient=student,
            notification_type="system",
            title=f"Continue learning: {course.title}",
            message=f"You're {progress_pct}% through '{course.title}'. Keep going!",
            action_url=f"/learn/{course.slug}",
        )

        send_notification_email(
            recipient_email=student.email,
            subject=f"Continue your journey in {course.title}",
            body=(
                f"Hi {student.display_name},\n\n"
                f"You're {progress_pct}% through '{course.title}' - "
                f"don't lose your momentum!\n\n"
                f"Continue learning now at CourseCraft.\n\n"
                f"Happy learning,\nThe CourseCraft Team"
            ),
        )
        sent_count += 1

    logger.info("Sent %d progress reminder notifications.", sent_count)


@shared_task(name="apps.notifications.tasks.send_new_lesson_notification")
def send_new_lesson_notification(lesson_id):
    """Notify enrolled students when a new lesson is published."""
    from apps.courses.models import CourseEnrollment, Lesson
    from .services import create_notification

    try:
        lesson = Lesson.objects.select_related("section__course").get(id=lesson_id)
    except Lesson.DoesNotExist:
        logger.warning("Lesson %s not found for notification.", lesson_id)
        return

    course = lesson.section.course
    if course.status != "published":
        return

    enrollments = CourseEnrollment.objects.filter(
        course=course, is_active=True
    ).select_related("student")

    for enrollment in enrollments:
        create_notification(
            recipient=enrollment.student,
            notification_type="course_update",
            title=f"New lesson in {course.title}",
            message=f"A new lesson '{lesson.title}' has been added to '{course.title}'.",
            action_url=f"/learn/{course.slug}/lesson/{lesson.id}",
        )

    logger.info("Notified %d students about new lesson '%s'.", enrollments.count(), lesson.title)


@shared_task(name="apps.notifications.tasks.cleanup_old_notifications")
def cleanup_old_notifications():
    """Delete read notifications older than 90 days."""
    from .models import Notification

    cutoff = timezone.now() - timedelta(days=90)
    count, _ = Notification.objects.filter(is_read=True, created_at__lt=cutoff).delete()
    logger.info("Cleaned up %d old notifications.", count)
