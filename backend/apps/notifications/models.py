import uuid

from django.conf import settings
from django.db import models


class Notification(models.Model):
    """In-app notification for a user."""

    class NotificationType(models.TextChoices):
        ENROLLMENT = "enrollment", "New Enrollment"
        REVIEW = "review", "New Review"
        DISCUSSION = "discussion", "New Discussion"
        REPLY = "reply", "New Reply"
        CERTIFICATE = "certificate", "Certificate Issued"
        PAYMENT = "payment", "Payment Received"
        PAYOUT = "payout", "Payout Processed"
        COURSE_UPDATE = "course_update", "Course Updated"
        ACHIEVEMENT = "achievement", "Achievement Earned"
        SYSTEM = "system", "System Notification"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    notification_type = models.CharField(max_length=20, choices=NotificationType.choices)
    title = models.CharField(max_length=300)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    action_url = models.URLField(blank=True, help_text="Link to the relevant page")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read", "-created_at"]),
        ]

    def __str__(self):
        return f"[{self.notification_type}] {self.title} -> {self.recipient.email}"


class EmailLog(models.Model):
    """Tracks emails sent from the platform."""

    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient_email = models.EmailField()
    subject = models.CharField(max_length=500)
    body = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.QUEUED)
    error_message = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "email_logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Email to {self.recipient_email}: {self.subject} ({self.status})"
