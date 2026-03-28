from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import CreatorProfile, StudentProfile
from .serializers import (
    ChangePasswordSerializer,
    CreatorProfileSerializer,
    CreatorProfileUpdateSerializer,
    StudentProfileSerializer,
    StudentProfileUpdateSerializer,
    UserProfileUpdateSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """Register a new user account."""

    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    """Obtain JWT token pair via email and password."""

    permission_classes = (permissions.AllowAny,)


class TokenRefreshAPIView(TokenRefreshView):
    """Refresh an access token using a refresh token."""

    permission_classes = (permissions.AllowAny,)


class LogoutView(APIView):
    """Blacklist the refresh token to log the user out."""

    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"detail": "Refresh token is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"detail": "Successfully logged out."},
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"detail": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Retrieve or update the current user's profile."""

    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UserProfileUpdateSerializer
        return UserSerializer

    def get_object(self):
        return self.request.user


class ChangePasswordView(generics.UpdateAPIView):
    """Change the current user's password."""

    serializer_class = ChangePasswordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()
        return Response(
            {"detail": "Password updated successfully."},
            status=status.HTTP_200_OK,
        )


class CreatorProfileView(generics.RetrieveUpdateAPIView):
    """Retrieve or update the current creator's profile."""

    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return CreatorProfileUpdateSerializer
        return CreatorProfileSerializer

    def get_object(self):
        profile, _ = CreatorProfile.objects.get_or_create(user=self.request.user)
        return profile


class StudentProfileView(generics.RetrieveUpdateAPIView):
    """Retrieve or update the current student's profile."""

    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return StudentProfileUpdateSerializer
        return StudentProfileSerializer

    def get_object(self):
        profile, _ = StudentProfile.objects.get_or_create(user=self.request.user)
        return profile


class CreatorPublicProfileView(generics.RetrieveAPIView):
    """Retrieve a creator's public profile by user ID."""

    serializer_class = CreatorProfileSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = CreatorProfile.objects.select_related("user").all()
    lookup_field = "user__id"
    lookup_url_kwarg = "user_id"
