"""Notification creation and delivery services."""

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from .models import EmailLog, Notification

logger = logging.getLogger(__name__)


def create_notification(recipient, notification_type, title, message, action_url="", metadata=None):
    """Create an in-app notification for a user."""
    notification = Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        message=message,
        action_url=action_url,
        metadata=metadata or {},
    )
    logger.info("Created notification '%s' for user %s", title, recipient.email)
    return notification


def send_notification_email(recipient_email, subject, body):
    """Send an email notification and log the result."""
    log = EmailLog.objects.create(
        recipient_email=recipient_email,
        subject=subject,
        body=body,
    )

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
        log.status = EmailLog.Status.SENT
        log.sent_at = timezone.now()
        log.save(update_fields=["status", "sent_at"])
        logger.info("Email sent to %s: %s", recipient_email, subject)
        return True
    except Exception as e:
        log.status = EmailLog.Status.FAILED
        log.error_message = str(e)
        log.save(update_fields=["status", "error_message"])
        logger.exception("Failed to send email to %s: %s", recipient_email, e)
        return False


def notify_new_enrollment(enrollment):
    """Notify the instructor about a new enrollment."""
    instructor = enrollment.course.instructor
    student = enrollment.student

    create_notification(
        recipient=instructor,
        notification_type=Notification.NotificationType.ENROLLMENT,
        title="New Student Enrolled",
        message=f"{student.display_name} enrolled in your course '{enrollment.course.title}'.",
        action_url=f"/instructor/courses/{enrollment.course.slug}/students",
        metadata={
            "student_id": str(student.id),
            "course_id": str(enrollment.course.id),
        },
    )

    create_notification(
        recipient=student,
        notification_type=Notification.NotificationType.ENROLLMENT,
        title=f"Welcome to {enrollment.course.title}!",
        message=f"You've successfully enrolled in '{enrollment.course.title}'. Start learning now!",
        action_url=f"/learn/{enrollment.course.slug}",
    )


def notify_new_review(review):
    """Notify the instructor about a new review."""
    instructor = review.course.instructor

    create_notification(
        recipient=instructor,
        notification_type=Notification.NotificationType.REVIEW,
        title=f"New {review.rating}-star Review",
        message=f"{review.student.display_name} left a {review.rating}-star review on '{review.course.title}'.",
        action_url=f"/instructor/courses/{review.course.slug}/reviews",
        metadata={
            "review_id": str(review.id),
            "rating": review.rating,
        },
    )


def notify_certificate_issued(certificate):
    """Notify a student that their certificate is ready."""
    create_notification(
        recipient=certificate.student,
        notification_type=Notification.NotificationType.CERTIFICATE,
        title="Certificate Ready!",
        message=f"Your certificate for '{certificate.course.title}' is ready to download.",
        action_url=f"/certificates/{certificate.id}",
        metadata={
            "certificate_id": str(certificate.id),
            "certificate_number": certificate.certificate_number,
        },
    )

    send_notification_email(
        recipient_email=certificate.student.email,
        subject=f"Your CourseCraft Certificate for {certificate.course.title}",
        body=(
            f"Congratulations {certificate.student.display_name}!\n\n"
            f"You have successfully completed '{certificate.course.title}' "
            f"and your certificate is ready.\n\n"
            f"Certificate Number: {certificate.certificate_number}\n\n"
            f"Download your certificate at: {certificate.verification_url}\n\n"
            f"Best regards,\nThe CourseCraft Team"
        ),
    )


def notify_payment_received(payment):
    """Notify instructor about a payment."""
    instructor = payment.course.instructor

    create_notification(
        recipient=instructor,
        notification_type=Notification.NotificationType.PAYMENT,
        title="Payment Received",
        message=f"You earned ${payment.instructor_share} from a sale of '{payment.course.title}'.",
        action_url="/instructor/earnings",
        metadata={
            "payment_id": str(payment.id),
            "amount": str(payment.instructor_share),
        },
    )


def mark_notifications_read(user, notification_ids=None):
    """Mark notifications as read for a user."""
    qs = Notification.objects.filter(recipient=user, is_read=False)
    if notification_ids:
        qs = qs.filter(id__in=notification_ids)
    count = qs.update(is_read=True)
    return count
