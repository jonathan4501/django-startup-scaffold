from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, RegisterView, LoginView, LogoutView, CurrentUserView, VerifyEmailView,  SendVerificationEmailView, PasswordResetRequestView, PasswordResetConfirmView
from django.urls import path

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='user')

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
    path('auth/me/', CurrentUserView.as_view(), name='auth-me'),
    path('auth/email-verify/', VerifyEmailView.as_view(), name='email-verify'),
    path('auth/send-verification-email/', SendVerificationEmailView.as_view(), name='send-verification-email'),
    path('auth/password-reset-request/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('auth/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]

urlpatterns += router.urls
