from django.urls import path

from . import views

app_name = "analytics"

urlpatterns = [
    path("instructor/dashboard/", views.InstructorDashboardView.as_view(), name="instructor-dashboard"),
    path("instructor/", views.InstructorAnalyticsView.as_view(), name="instructor-analytics"),
    path("course/<slug:course_slug>/", views.CourseAnalyticsView.as_view(), name="course-analytics"),
    path("platform/", views.PlatformAnalyticsView.as_view(), name="platform-analytics"),
]
