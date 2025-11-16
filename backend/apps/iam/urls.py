from django.urls import path

from .views import MeView, ChangePasswordView

urlpatterns = [
    # existing auth endpoints go here (e.g. login, refresh, register)

    path("me", MeView.as_view(), name="auth-me"),
    path("change-password", ChangePasswordView.as_view(), name="auth-change-password"),
]
