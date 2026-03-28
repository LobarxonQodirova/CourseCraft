from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.permissions import IsAdmin, IsInstructor

from .models import Certificate, CertificateTemplate
from .serializers import (
    CertificateSerializer,
    CertificateTemplateSerializer,
    CertificateVerifySerializer,
)
from .services import issue_certificate, revoke_certificate


class CertificateTemplateViewSet(viewsets.ModelViewSet):
    """CRUD for certificate templates - admin only."""

    serializer_class = CertificateTemplateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    queryset = CertificateTemplate.objects.filter(is_active=True)


class CertificateViewSet(viewsets.ReadOnlyModelViewSet):
    """List and retrieve certificates for the authenticated user."""

    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return Certificate.objects.all().select_related("student", "course", "template")
        return Certificate.objects.filter(
            student=user
        ).select_related("student", "course", "template")

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        """Return the PDF file URL for a certificate."""
        certificate = self.get_object()
        if not certificate.pdf_file:
            return Response(
                {"detail": "Certificate PDF has not been generated yet."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({"pdf_url": request.build_absolute_uri(certificate.pdf_file.url)})

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsAdmin])
    def revoke(self, request, pk=None):
        """Revoke a certificate - admin only."""
        certificate = self.get_object()
        reason = request.data.get("reason", "")
        revoke_certificate(certificate, reason)
        return Response(
            {"detail": f"Certificate {certificate.certificate_number} has been revoked."}
        )


class CertificateVerifyView(generics.GenericAPIView):
    """Public endpoint to verify a certificate by its number."""

    serializer_class = CertificateVerifySerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cert_number = serializer.validated_data["certificate_number"]
        certificate = Certificate.objects.select_related("student", "course").get(
            certificate_number=cert_number
        )
        return Response({
            "valid": True,
            "certificate_number": certificate.certificate_number,
            "student_name": certificate.student.display_name,
            "course_title": certificate.course.title,
            "issued_at": certificate.issued_at,
        })
