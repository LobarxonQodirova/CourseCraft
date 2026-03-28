"""Payment processing services using Stripe."""

import logging
from decimal import Decimal

import stripe
from django.conf import settings

from apps.courses.models import CourseEnrollment

from .models import Coupon, InstructorPayout, Payment

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(user, course, coupon_code=None):
    """Create a Stripe Checkout session for a course purchase."""
    original_price = course.effective_price
    discount_amount = Decimal("0")
    coupon = None

    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon.is_valid and (not coupon.course or coupon.course == course):
                discount_amount = Decimal(str(coupon.calculate_discount(float(original_price))))
        except Coupon.DoesNotExist:
            pass

    final_amount = max(original_price - discount_amount, Decimal("0"))

    if final_amount == 0:
        payment = Payment.objects.create(
            student=user,
            course=course,
            amount=0,
            original_amount=original_price,
            discount_amount=discount_amount,
            coupon=coupon,
            status=Payment.Status.COMPLETED,
            payment_method=Payment.PaymentMethod.FREE,
        )
        CourseEnrollment.objects.get_or_create(course=course, student=user)
        if coupon:
            coupon.times_used += 1
            coupon.save(update_fields=["times_used"])
        return {"payment_id": str(payment.id), "free": True}

    commission_rate = Decimal("85.00")
    if hasattr(course.instructor, "creator_profile"):
        commission_rate = course.instructor.creator_profile.commission_rate

    instructor_share = final_amount * (commission_rate / 100)
    platform_share = final_amount - instructor_share

    payment = Payment.objects.create(
        student=user,
        course=course,
        amount=final_amount,
        original_amount=original_price,
        discount_amount=discount_amount,
        coupon=coupon,
        instructor_share=instructor_share,
        platform_share=platform_share,
        status=Payment.Status.PENDING,
    )

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": course.currency.lower(),
                    "unit_amount": int(final_amount * 100),
                    "product_data": {
                        "name": course.title,
                        "description": course.subtitle or course.description[:200],
                    },
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{settings.CORS_ALLOWED_ORIGINS[0]}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{settings.CORS_ALLOWED_ORIGINS[0]}/payment/cancel",
            customer_email=user.email,
            metadata={
                "payment_id": str(payment.id),
                "course_id": str(course.id),
                "user_id": str(user.id),
            },
        )

        payment.stripe_checkout_session_id = session.id
        payment.save(update_fields=["stripe_checkout_session_id"])

        return {
            "checkout_url": session.url,
            "session_id": session.id,
            "payment_id": str(payment.id),
        }

    except stripe.error.StripeError as e:
        payment.status = Payment.Status.FAILED
        payment.metadata = {"stripe_error": str(e)}
        payment.save(update_fields=["status", "metadata"])
        logger.exception("Stripe checkout session creation failed: %s", e)
        raise


def handle_checkout_completed(session):
    """Handle Stripe webhook for checkout.session.completed."""
    payment_id = session.metadata.get("payment_id")
    if not payment_id:
        logger.error("No payment_id in session metadata: %s", session.id)
        return

    try:
        payment = Payment.objects.get(id=payment_id)
    except Payment.DoesNotExist:
        logger.error("Payment %s not found for session %s", payment_id, session.id)
        return

    payment.status = Payment.Status.COMPLETED
    payment.stripe_payment_intent_id = session.payment_intent
    payment.receipt_url = session.get("receipt_url", "")
    payment.save(update_fields=["status", "stripe_payment_intent_id", "receipt_url"])

    CourseEnrollment.objects.get_or_create(course=payment.course, student=payment.student)

    course = payment.course
    course.total_enrollments += 1
    course.save(update_fields=["total_enrollments"])

    if payment.coupon:
        payment.coupon.times_used += 1
        payment.coupon.save(update_fields=["times_used"])

    logger.info("Payment %s completed for course %s by %s",
                payment_id, course.title, payment.student.email)


def process_refund(refund):
    """Process a refund through Stripe."""
    payment = refund.payment

    if not payment.stripe_payment_intent_id:
        logger.error("No stripe_payment_intent_id for payment %s", payment.id)
        return False

    try:
        stripe_refund = stripe.Refund.create(
            payment_intent=payment.stripe_payment_intent_id,
            amount=int(refund.amount * 100),
        )
        refund.stripe_refund_id = stripe_refund.id
        refund.status = "processed"
        refund.save(update_fields=["stripe_refund_id", "status"])

        if refund.amount >= payment.amount:
            payment.status = Payment.Status.REFUNDED
            enrollment = CourseEnrollment.objects.filter(
                course=payment.course, student=payment.student
            ).first()
            if enrollment:
                enrollment.is_active = False
                enrollment.save(update_fields=["is_active"])
        else:
            payment.status = Payment.Status.PARTIALLY_REFUNDED

        payment.save(update_fields=["status"])
        logger.info("Refund %s processed for payment %s", refund.id, payment.id)
        return True

    except stripe.error.StripeError as e:
        refund.status = "denied"
        refund.admin_notes = f"Stripe error: {str(e)}"
        refund.save(update_fields=["status", "admin_notes"])
        logger.exception("Refund failed: %s", e)
        return False
