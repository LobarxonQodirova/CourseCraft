import logging
from datetime import timedelta

from celery import shared_task
from django.db.models import Avg, Count, Sum
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(name="apps.courses.tasks.update_course_stats")
def update_course_stats(course_id):
    """Recalculate aggregate stats for a course after enrollment or review changes."""
    from .models import Course

    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        logger.warning("Course %s not found for stats update.", course_id)
        return

    review_stats = course.reviews.filter(is_approved=True).aggregate(
        avg_rating=Avg("rating"),
        total_reviews=Count("id"),
    )
    course.average_rating = review_stats["avg_rating"] or 0
    course.total_reviews = review_stats["total_reviews"] or 0

    course.total_enrollments = course.enrollments.filter(is_active=True).count()

    lesson_stats = course.sections.aggregate(
        total_lessons=Count("lessons"),
        total_duration=Sum("lessons__duration"),
    )
    course.total_lessons = lesson_stats["total_lessons"] or 0
    course.total_duration = lesson_stats["total_duration"]

    course.save(update_fields=[
        "average_rating", "total_reviews", "total_enrollments",
        "total_lessons", "total_duration",
    ])

    logger.info("Updated stats for course %s: rating=%.2f, enrollments=%d",
                course.title, course.average_rating, course.total_enrollments)


@shared_task(name="apps.courses.tasks.process_video_upload")
def process_video_upload(lesson_content_id, video_url):
    """Process a newly uploaded video: extract duration metadata."""
    from .models import LessonContent

    try:
        content = LessonContent.objects.get(id=lesson_content_id)
    except LessonContent.DoesNotExist:
        logger.warning("LessonContent %s not found.", lesson_content_id)
        return

    content.video_url = video_url
    content.save(update_fields=["video_url"])
    logger.info("Processed video upload for lesson content %s", lesson_content_id)


@shared_task(name="apps.courses.tasks.send_new_lesson_notifications")
def send_new_lesson_notifications(lesson_id):
    """Notify enrolled students when a new lesson is added to a published course."""
    from .models import Lesson

    try:
        lesson = Lesson.objects.select_related("section__course").get(id=lesson_id)
    except Lesson.DoesNotExist:
        logger.warning("Lesson %s not found.", lesson_id)
        return

    course = lesson.section.course
    if course.status != "published":
        return

    enrolled_student_ids = list(
        course.enrollments.filter(is_active=True).values_list("student_id", flat=True)
    )

    logger.info(
        "Notifying %d students about new lesson '%s' in course '%s'",
        len(enrolled_student_ids), lesson.title, course.title,
    )


@shared_task(name="apps.courses.tasks.archive_stale_drafts")
def archive_stale_drafts():
    """Archive draft courses that haven't been updated in 6 months."""
    from .models import Course

    cutoff = timezone.now() - timedelta(days=180)
    stale_drafts = Course.objects.filter(status="draft", updated_at__lt=cutoff)
    count = stale_drafts.update(status="archived")
    logger.info("Archived %d stale draft courses.", count)
