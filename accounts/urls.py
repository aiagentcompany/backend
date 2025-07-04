from django.urls import path
from .views import RegisterView, ActivateView, ResetRequestView, ResetPasswordView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("signup/", RegisterView.as_view()),
    path("activate/", ActivateView.as_view()),
    path("login/", TokenObtainPairView.as_view()),
    path("refresh/", TokenRefreshView.as_view()),
    path("reset/", ResetRequestView.as_view()),
    path("reset/confirm/", ResetPasswordView.as_view()),
]
