# * URL for user *

from django.urls import path

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .apps import UserConfig
from .views import PasswordResetConfirmView, PasswordResetRequestView, RegisterAPIView, UserMeAPIView

app_name = UserConfig.name


urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),  # регистрация пользователя
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),  # логин
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),  # обновление токена
    #
    path("reset_password/", PasswordResetRequestView.as_view(), name="password_reset"),  # сброс пароля
    path("reset_password_confirm/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    #
    path("users/me/", UserMeAPIView.as_view(), name="user-me"),
]
