from rest_framework import serializers

from .models import Certificate, CertificateTemplate


class CertificateTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateTemplate
        fields = (
            "id", "name", "description", "html_template",
            "background_image", "is_default", "is_active",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class CertificateSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.display_name", read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)
    template_name = serializers.CharField(source="template.name", read_only=True, default="")

    class Meta:
        model = Certificate
        fields = (
            "id", "certificate_number", "student_name", "course_title",
            "template_name", "status", "pdf_file", "verification_url",
            "issued_at", "created_at",
        )
        read_only_fields = (
            "id", "certificate_number", "status", "pdf_file",
            "verification_url", "issued_at", "created_at",
        )


class CertificateVerifySerializer(serializers.Serializer):
    """Serializer for public certificate verification."""

    certificate_number = serializers.CharField()

    def validate_certificate_number(self, value):
        try:
            cert = Certificate.objects.select_related("student", "course").get(
                certificate_number=value, status=Certificate.Status.GENERATED
            )
        except Certificate.DoesNotExist:
            raise serializers.ValidationError("Certificate not found or has been revoked.")
        return value
