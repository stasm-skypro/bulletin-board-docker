from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from user.models import User


class RegisterSerializer(serializers.ModelSerializer):
    """
    Представляет сериализатор для регистрации пользователя.
    Attributes:
        email (str): Электронная почта пользователя
        password (str): Пароль пользователя
    """

    # Чтобы не было попыток зарегистрировать одного и того же пользователя дважды
    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])

    # Добавляем подтверждение пароля
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirmation = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """
        Проверяет, что пароли совпадают.
        """
        data = super().validate(attrs)
        if data["password"] != data["password_confirmation"]:
            raise serializers.ValidationError("Пароли не совпадают!")
        return data

    def create(self, validated_data):
        """
        Создает новый объект пользователя.
        """
        # password_confirmation не является полем модели User, и его нельзя передавать в create_user()
        validated_data.pop("password_confirmation")
        # статический анализатор не знает о существовании метода create_user в менеджере модели User, поэтому
        user = User.objects.create_user(**validated_data)  # type: ignore
        return user

    class Meta:
        """
        Говорит сериализатору, что он работает с моделью User, и обрабатывает поля, которые нужны при регистрации:
        'first_name', 'last_name', 'phone', 'email', 'password', 'password_confirmation'.
        """

        model = User
        fields = ("first_name", "last_name", "phone", "email", "password", "password_confirmation")
        extra_kwargs = {
            "password": {"write_only": True},
            "password_confirmation": {"write_only": True},
        }


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "email"


class UserSerializer(serializers.ModelSerializer):
    """
    Представляет собой универсальный сериализатор пользователя.
    """

    class Meta:
        """
        Говорит сериализатору, что он работает с моделью User, и определяет список полей,
        которые он должен обрабатывать.
        """

        model = User
        fields = ["id", "email", "first_name", "last_name", "role", "is_active", "is_staff", "is_superuser"]
        read_only_fields = ["id", "email"]
