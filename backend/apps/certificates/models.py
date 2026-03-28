import uuid

from django.conf import settings
from django.db import models


class CertificateTemplate(models.Model):
    """Template used to generate course completion certificates."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    html_template = models.TextField(
        help_text="HTML/CSS template with placeholders: {{student_name}}, {{course_title}}, {{date}}, {{certificate_id}}"
    )
    background_image = models.ImageField(
        upload_to="certificates/templates/%Y/%m/", blank=True
    )
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "certificate_templates"
        ordering = ["-is_default", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_default:
            CertificateTemplate.objects.filter(is_default=True).exclude(pk=self.pk).update(
                is_default=False
            )
        super().save(*args, **kwargs)


class Certificate(models.Model):
    """Issued certificate for a student who completed a course."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending Generation"
        GENERATED = "generated", "Generated"
        REVOKED = "revoked", "Revoked"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    certificate_number = models.CharField(max_length=50, unique=True, db_index=True)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="certificates"
    )
    course = models.ForeignKey(
        "courses.Course", on_delete=models.CASCADE, related_name="certificates"
    )
    template = models.ForeignKey(
        CertificateTemplate, on_delete=models.SET_NULL, null=True, related_name="certificates"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    pdf_file = models.FileField(upload_to="certificates/pdf/%Y/%m/", blank=True)
    verification_url = models.URLField(blank=True)
    issued_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    revoke_reason = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True, help_text="Extra data embedded in cert")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "certificates"
        unique_together = ["student", "course"]
        ordering = ["-issued_at"]

    def __str__(self):
        return f"Certificate {self.certificate_number} - {self.student.email}"
