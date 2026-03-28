from datetime import date, timedelta

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdmin, IsInstructor

from .models import DailyCourseStat, DailyPlatformStat, InstructorDailyStat
from .services import get_instructor_dashboard_summary


class InstructorDashboardView(APIView):
    """Summary statistics for the instructor dashboard."""

    permission_classes = [permissions.IsAuthenticated, IsInstructor]

    def get(self, request):
        summary = get_instructor_dashboard_summary(request.user)
        return Response(summary)


class InstructorAnalyticsView(APIView):
    """Detailed time-series analytics for an instructor."""

    permission_classes = [permissions.IsAuthenticated, IsInstructor]

    def get(self, request):
        days = int(request.query_params.get("days", 30))
        days = min(days, 365)
        start_date = date.today() - timedelta(days=days)

        stats = InstructorDailyStat.objects.filter(
            instructor=request.user, date__gte=start_date
        ).order_by("date")

        data = [
            {
                "date": str(s.date),
                "total_students": s.total_students,
                "new_enrollments": s.new_enrollments,
                "daily_revenue": str(s.daily_revenue),
                "total_revenue": str(s.total_revenue),
                "avg_rating": str(s.avg_rating),
                "total_reviews": s.total_reviews,
                "watch_time_minutes": s.total_watch_time_minutes,
            }
            for s in stats
        ]

        return Response({"period_days": days, "data": data})


class CourseAnalyticsView(APIView):
    """Analytics for a specific course - instructor only."""

    permission_classes = [permissions.IsAuthenticated, IsInstructor]

    def get(self, request, course_slug):
        from apps.courses.models import Course

        try:
            course = Course.objects.get(slug=course_slug, instructor=request.user)
        except Course.DoesNotExist:
            return Response(
                {"detail": "Course not found."}, status=status.HTTP_404_NOT_FOUND
            )

        days = int(request.query_params.get("days", 30))
        start_date = date.today() - timedelta(days=days)

        stats = DailyCourseStat.objects.filter(
            course=course, date__gte=start_date
        ).order_by("date")

        data = [
            {
                "date": str(s.date),
                "views": s.views,
                "enrollments": s.enrollments,
                "completions": s.completions,
                "revenue": str(s.revenue),
                "watch_time_minutes": s.watch_time_minutes,
                "avg_rating": str(s.avg_rating),
                "reviews_count": s.reviews_count,
            }
            for s in stats
        ]

        return Response({
            "course": course.title,
            "period_days": days,
            "data": data,
        })


class PlatformAnalyticsView(APIView):
    """Platform-wide analytics - admin only."""

    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    def get(self, request):
        days = int(request.query_params.get("days", 30))
        start_date = date.today() - timedelta(days=days)

        stats = DailyPlatformStat.objects.filter(date__gte=start_date).order_by("date")

        data = [
            {
                "date": str(s.date),
                "total_users": s.total_users,
                "new_users": s.new_users,
                "active_users": s.active_users,
                "total_courses": s.total_courses,
                "new_courses": s.new_courses,
                "total_enrollments": s.total_enrollments,
                "new_enrollments": s.new_enrollments,
                "total_revenue": str(s.total_revenue),
                "daily_revenue": str(s.daily_revenue),
                "watch_time_minutes": s.total_watch_time_minutes,
            }
            for s in stats
        ]

        return Response({"period_days": days, "data": data})
