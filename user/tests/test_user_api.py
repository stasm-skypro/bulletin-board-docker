from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from user.models import User


@pytest.mark.django_db
class TestUserRegistration:
    """
    Тесты для регистрации пользователя.
    """

    def setup_method(self):
        """
        Создание клиента и URL для регистрации пользователя.
        :return:
        """
        self.client = APIClient()
        self.url = reverse("user:register")

    def test_successful_registration(self):
        """
        Тест успешной регистрации пользователя.
        :return:
        """
        data = {
            "first_name": "Иван",
            "last_name": "Иванов",
            "phone": "79999999999",
            "email": "test@example.com",
            "password": "secure1234",
            "password_confirmation": "secure1234",
        }
        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert "message" in response.data
        assert User.objects.filter(email="test@example.com").exists()

    def test_duplicate_email(self):
        """
        Тест на дублирование email.
        :return:
        """
        User.objects.create_user(
            email="test@example.com", password="secure1234", first_name="Иван", last_name="Иванов", phone="79999999999"
        )
        data = {
            "first_name": "Петр",
            "last_name": "Петров",
            "phone": "79999999998",
            "email": "test@example.com",
            "password": "secure1234",
            "password_confirmation": "secure1234",
        }
        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_mismatch(self):
        """
        Тест на несовпадение паролей.
        :return:
        """
        data = {
            "first_name": "Мария",
            "last_name": "Сидорова",
            "phone": "79999999997",
            "email": "mismatch@example.com",
            "password": "secure1234",
            "password_confirmation": "wrong1234",
        }
        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Пароли не совпадают!" in str(response.data)


@pytest.mark.django_db
class TestUserLogin:
    """
    Тесты для логина пользователя.
    """

    def setup_method(self):
        """
        Создание клиента и URL для логина пользователя.
        :return:
        """
        self.client = APIClient()
        self.url = reverse("user:token_obtain_pair")
        self.user = User.objects.create_user(
            email="user@example.com", password="secure1234", first_name="Имя", last_name="Фамилия", phone="70000000000"
        )

    def test_successful_login(self):
        """
        Тест успешного логина пользователя.
        :return:
        """
        data = {
            "email": "user@example.com",
            "password": "secure1234",
        }
        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_invalid_credentials(self):
        """
        Тест неверных учетных данных.
        :return:
        """
        data = {
            "email": "user@example.com",
            "password": "wrongpassword",
        }
        response = self.client.post(self.url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestPasswordReset:
    """
    Тесты для сброса пароля.
    """

    def setup_method(self):
        """
        Создание клиента и пользователя для сброса пароля.
        :return:
        """
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="reset@example.com",
            password="oldpassword123",
            first_name="Reset",
            last_name="User",
            phone="71111111111",
        )

    def test_password_reset_request(self):
        """
        Тест запроса на сброс пароля.
        :return:
        """
        url = reverse("user:password_reset")
        response = self.client.post(url, {"email": "reset@example.com"})
        assert response.status_code == status.HTTP_200_OK
        assert "Письмо для сброса пароля отправлено" in response.data["message"]

    def test_password_reset_confirm_success(self):
        """
        Тест успешного сброса пароля.
        :return:
        """
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        url = reverse("user:password_reset_confirm")
        data = {
            "uid": uid,
            "token": token,
            "new_password": "newsecure123",
        }
        response = self.client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        self.user.refresh_from_db()
        assert self.user.check_password("newsecure123")

    def test_password_reset_confirm_invalid_token(self):
        """
        Тест неверного токена.
        :return:
        """
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        url = reverse("user:password_reset_confirm")
        data = {
            "uid": uid,
            "token": "invalid-token",
            "new_password": "newsecure123",
        }
        response = self.client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Неверный или просроченный токен" in response.data["error"]


@pytest.mark.django_db
class TestUserMe:
    """
    Тесты для эндпоинта /me/ — просмотр, обновление и деактивация текущего пользователя.
    """

    def setup_method(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="me@example.com",
            password="secure1234",
            first_name="Тест",
            last_name="Пользователь",
            phone="79991234567",
        )
        token_url = reverse("user:token_obtain_pair")
        response = self.client.post(token_url, {"email": self.user.email, "password": "secure1234"})
        access_token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        self.url = reverse("user:user-me")

    def test_get_user_info(self):
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == self.user.email
        assert response.data["first_name"] == self.user.first_name

    def test_update_user_info(self):
        response = self.client.patch(self.url, {"first_name": "Новый"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "Новый"

    def test_deactivate_user(self):
        response = self.client.delete(self.url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        self.user.refresh_from_db()
        assert self.user.is_active is False
