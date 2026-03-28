from rest_framework import serializers

from .models import Coupon, InstructorPayout, Payment, Refund


class PaymentSerializer(serializers.ModelSerializer):
    student_email = serializers.CharField(source="student.email", read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)
    coupon_code = serializers.CharField(source="coupon.code", read_only=True, default="")

    class Meta:
        model = Payment
        fields = (
            "id", "student_email", "course_title", "amount", "currency",
            "status", "payment_method", "coupon_code", "discount_amount",
            "original_amount", "instructor_share", "platform_share",
            "receipt_url", "created_at",
        )
        read_only_fields = (
            "id", "status", "instructor_share", "platform_share",
            "receipt_url", "created_at",
        )


class CheckoutSerializer(serializers.Serializer):
    """Serializer for initiating a checkout session."""

    course_id = serializers.UUIDField()
    coupon_code = serializers.CharField(required=False, allow_blank=True)

    def validate_course_id(self, value):
        from apps.courses.models import Course
        try:
            course = Course.objects.get(id=value, status="published")
        except Course.DoesNotExist:
            raise serializers.ValidationError("Course not found or not available for purchase.")
        if course.is_free:
            raise serializers.ValidationError("This course is free. Use the enroll endpoint instead.")
        return value


class CouponSerializer(serializers.ModelSerializer):
    is_valid = serializers.ReadOnlyField()

    class Meta:
        model = Coupon
        fields = (
            "id", "code", "description", "discount_type", "discount_value",
            "min_purchase_amount", "max_discount_amount", "course",
            "max_uses", "times_used", "is_active", "is_valid",
            "valid_from", "valid_until", "created_at",
        )
        read_only_fields = ("id", "times_used", "created_at")


class CouponValidateSerializer(serializers.Serializer):
    """Validate a coupon code for a specific course."""

    code = serializers.CharField()
    course_id = serializers.UUIDField()

    def validate(self, attrs):
        try:
            coupon = Coupon.objects.get(code=attrs["code"])
        except Coupon.DoesNotExist:
            raise serializers.ValidationError({"code": "Invalid coupon code."})
        if not coupon.is_valid:
            raise serializers.ValidationError({"code": "This coupon has expired or is no longer valid."})
        if coupon.course and str(coupon.course_id) != str(attrs["course_id"]):
            raise serializers.ValidationError({"code": "This coupon is not valid for the selected course."})
        attrs["coupon"] = coupon
        return attrs


class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = (
            "id", "payment", "amount", "reason", "status",
            "admin_notes", "requested_at", "processed_at",
        )
        read_only_fields = ("id", "status", "admin_notes", "requested_at", "processed_at")


class InstructorPayoutSerializer(serializers.ModelSerializer):
    instructor_email = serializers.CharField(source="instructor.email", read_only=True)

    class Meta:
        model = InstructorPayout
        fields = (
            "id", "instructor_email", "amount", "currency", "status",
            "period_start", "period_end", "payment_count",
            "breakdown", "processed_at", "created_at",
        )
