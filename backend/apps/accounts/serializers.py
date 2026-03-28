from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import CreatorProfile, StudentProfile

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "email", "full_name", "password", "password_confirm", "role",
        )

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        if user.role == User.Role.CREATOR:
            CreatorProfile.objects.create(user=user)
        StudentProfile.objects.create(user=user)
        return user


class UserSerializer(serializers.ModelSerializer):
    display_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = (
            "id", "email", "full_name", "display_name", "role",
            "avatar", "bio", "phone", "email_verified",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "email", "email_verified", "created_at", "updated_at")


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("full_name", "avatar", "bio", "phone")


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value


class CreatorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = CreatorProfile
        fields = (
            "id", "user", "headline", "website", "twitter", "linkedin",
            "youtube", "stripe_onboarding_complete", "commission_rate",
            "total_earnings", "total_students", "is_verified",
            "verified_at", "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "stripe_onboarding_complete", "commission_rate",
            "total_earnings", "total_students", "is_verified",
            "verified_at", "created_at", "updated_at",
        )


class CreatorProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreatorProfile
        fields = ("headline", "website", "twitter", "linkedin", "youtube")


class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = StudentProfile
        fields = (
            "id", "user", "interests", "preferred_language",
            "learning_goals", "completed_courses_count",
            "total_learning_hours", "streak_days", "last_active_at",
            "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "completed_courses_count", "total_learning_hours",
            "streak_days", "last_active_at", "created_at", "updated_at",
        )


class StudentProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ("interests", "preferred_language", "learning_goals")
