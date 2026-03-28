"""Certificate generation service using WeasyPrint for PDF creation."""

import logging
import uuid
from datetime import datetime
from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
from django.template import Template, Context
from django.utils import timezone

logger = logging.getLogger(__name__)


def generate_certificate_number():
    """Generate a unique certificate number in format CC-YYYYMMDD-XXXX."""
    date_part = datetime.now().strftime("%Y%m%d")
    unique_part = uuid.uuid4().hex[:8].upper()
    return f"CC-{date_part}-{unique_part}"


def render_certificate_html(template, student, course, certificate):
    """Render the certificate HTML template with actual data."""
    context = Context({
        "student_name": student.display_name,
        "student_email": student.email,
        "course_title": course.title,
        "course_description": course.subtitle or course.description[:200],
        "instructor_name": course.instructor.display_name,
        "certificate_id": certificate.certificate_number,
        "issue_date": certificate.issued_at.strftime("%B %d, %Y") if certificate.issued_at else "",
        "verification_url": certificate.verification_url,
    })

    html_template = Template(template.html_template)
    return html_template.render(context)


def generate_certificate_pdf(certificate):
    """Generate a PDF file for the given certificate."""
    from .models import CertificateTemplate

    try:
        import weasyprint
    except ImportError:
        logger.error("WeasyPrint is not installed. Cannot generate PDF certificates.")
        return None

    template = certificate.template
    if not template:
        template = CertificateTemplate.objects.filter(is_default=True, is_active=True).first()
        if not template:
            logger.error("No certificate template available for certificate %s", certificate.id)
            return None

    html_content = render_certificate_html(
        template, certificate.student, certificate.course, certificate
    )

    try:
        pdf_bytes = weasyprint.HTML(string=html_content).write_pdf()
        filename = f"certificate_{certificate.certificate_number}.pdf"
        certificate.pdf_file.save(filename, ContentFile(pdf_bytes), save=False)
        certificate.status = "generated"
        certificate.save(update_fields=["pdf_file", "status"])
        logger.info("Generated PDF for certificate %s", certificate.certificate_number)
        return certificate
    except Exception as e:
        logger.exception("Failed to generate PDF for certificate %s: %s", certificate.id, e)
        return None


def issue_certificate(student, course):
    """Issue a new certificate for a student who completed a course."""
    from .models import Certificate, CertificateTemplate

    existing = Certificate.objects.filter(student=student, course=course).first()
    if existing and existing.status != Certificate.Status.REVOKED:
        logger.info("Certificate already exists for %s in %s", student.email, course.title)
        return existing

    template = CertificateTemplate.objects.filter(is_default=True, is_active=True).first()

    cert_number = generate_certificate_number()
    certificate = Certificate.objects.create(
        certificate_number=cert_number,
        student=student,
        course=course,
        template=template,
        status=Certificate.Status.PENDING,
        issued_at=timezone.now(),
        verification_url=f"{settings.ALLOWED_HOSTS[0]}/verify/{cert_number}",
        metadata={
            "course_instructor": course.instructor.display_name,
            "course_duration": str(course.total_duration) if course.total_duration else "N/A",
            "total_lessons": course.total_lessons,
        },
    )

    generate_certificate_pdf(certificate)
    logger.info("Issued certificate %s to %s for course %s",
                cert_number, student.email, course.title)

    return certificate


def revoke_certificate(certificate, reason=""):
    """Revoke an issued certificate."""
    certificate.status = "revoked"
    certificate.revoked_at = timezone.now()
    certificate.revoke_reason = reason
    certificate.save(update_fields=["status", "revoked_at", "revoke_reason"])
    logger.info("Revoked certificate %s. Reason: %s", certificate.certificate_number, reason)
    return certificate
