# user/views.py
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import (  # type: ignore[reportUnusedImport]
    EmailTokenObtainPairSerializer,
    RegisterSerializer,
    UserSerializer,
)
from .utils import send_password_reset_email, send_welcome_email


class RegisterAPIView(CreateAPIView):
    """
    Регистрация нового пользователя.
    Параметры запроса:
    - email (str): Email пользователя;
    - password (str): Пароль не менее 8 символов;

    Клиент (например, фронтенд) отправляет POST-запрос на эндпоинт регистрации (например, /api/register/),
    передавая JSON:
    {
        "email": "user@example.com",
        "password": "secure1234"
    }

    API возвращает успешный ответ, например:
    {
        "message": "Регистрация пользователя user@example.com прошла успешно."
    }
    """

    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        """
        Сохраняет новый объект, используя переданный сериализатор.

        Этот метод вызывается после успешной валидации данных.
        Здесь можно переопределить или расширить логику создания объекта,
        например, установить текущего пользователя в качестве владельца
        или выполнить дополнительные действия (логирование, отправка писем и т.п.).

        :param serializer: Валидированный сериализатор, содержащий данные для создания объекта.
        :type serializer: rest_framework.serializers.Serializer
        """
        user = serializer.save()
        send_welcome_email.delay(user.email)  # type: ignore

    def create(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запрос на создание нового объекта.

        Метод вызывается при отправке POST-запроса к API-представлению,
        основанному на CreateAPIView. Валидирует входные данные, сохраняет
        новый объект и возвращает ответ с данными или сообщением.

        :param request: HTTP-запрос, содержащий входные данные (обычно JSON).
        :type request: rest_framework.request.Request
        :param args: Дополнительные позиционные аргументы.
        :param kwargs: Дополнительные именованные аргументы.
        :return: HTTP-ответ с сообщением об успешном создании объекта или ошибками валидации.
        :rtype: rest_framework.response.Response
        """
        response = super().create(request, *args, **kwargs)
        email = request.data.get("email")
        response.data = {"message": f"Регистрация пользователя {email} прошла успешно."}
        return response


class EmailTokenObtainPairView(TokenObtainPairView):
    """
    Представляет сериализатор для получения пары токенов.
    """

    serializer_class = EmailTokenObtainPairSerializer  # type: ignore[assignment]


class PasswordResetRequestView(APIView):
    """
    Получает email, генерирует uid/token и отправляет ссылку для сброса пароля.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Пользователь такого email не найден"}, status=status.HTTP_400_BAD_REQUEST)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        reset_url = f"{request.scheme}://{request.get_host()}/users/reset_password_confirm/?uid={uid}&token={token}"
        send_password_reset_email(user.email, reset_url)

        return Response({"message": "Письмо для сброса пароля отправлено"}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """
    Подтверждает токен и устанавливает новый пароль.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        uid = request.data.get("uid")
        token = request.data.get("token")
        new_password = request.data.get("new_password")

        try:
            uid_decoded = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=uid_decoded)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({"error": "Неверный uid."}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Неверный или просроченный токен."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"message": "Пароль успешно изменен"}, status=status.HTTP_200_OK)


class UserMeAPIView(RetrieveUpdateDestroyAPIView):
    """
    Управление текущим пользователем:
    - GET: Получить данные
    - PUT/PATCH: Обновить данные
    - DELETE: Деактивировать пользователя
    """

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):  # type: ignore
        return self.request.user

    def perform_destroy(self, instance):
        instance.is_active = False  # вместо удаления
        instance.save()
