from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "certificates"

router = DefaultRouter()
router.register(r"templates", views.CertificateTemplateViewSet, basename="certificate-template")
router.register(r"", views.CertificateViewSet, basename="certificate")

urlpatterns = [
    path("verify/", views.CertificateVerifyView.as_view(), name="certificate-verify"),
    path("", include(router.urls)),
]
