from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("token/refresh/", views.TokenRefreshAPIView.as_view(), name="token-refresh"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("profile/", views.UserProfileView.as_view(), name="profile"),
    path("profile/password/", views.ChangePasswordView.as_view(), name="change-password"),
    path("profile/creator/", views.CreatorProfileView.as_view(), name="creator-profile"),
    path("profile/student/", views.StudentProfileView.as_view(), name="student-profile"),
    path(
        "creators/<uuid:user_id>/",
        views.CreatorPublicProfileView.as_view(),
        name="creator-public-profile",
    ),
]
