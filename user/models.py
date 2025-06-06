from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """
    Определяет менеджера пользователей. Нужен для правильного создания пользователей и суперпользователей в кастомной
    модели пользователя.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Создаёт обычного пользователя.
        :param email: Электронная почта пользователя
        :param password: Пароль пользователя
        :param extra_fields: Дополнительные поля пользователя
        :return: Объект пользователя
        """
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Создаёт суперпользователя.
        :param email: Электронная почта суперпользователя
        :param password: Пароль суперпользователя
        :param extra_fields: Дополнительные поля суперпользователя
        :return: Объект суперпользователя
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        # Проверка, чтобы избежать ситуаций, когда суперпользователь создаётся без нужных прав
        if not extra_fields["is_staff"]:
            raise ValueError("У суперпользователя должно быть is_staff=True.")
        if not extra_fields["is_superuser"]:
            raise ValueError("У суперпользователя должно быть is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Определяет модель пользователя.
    Attributes:
        first_name (str): Имя пользователя;
         last_name (str): Фамилия пользователя;
             phone (str): Телефон для связи;
             email (str): Электронная почта пользователя;
                    role: Роль пользователя, доступные значения: user, admin. Роли: user, admin;
                   image: Аватарка пользователя;
          password (str): Пароль пользователя;
    """

    ROLE_CHOICES = [
        ("user", "Пользователь"),
        ("admin", "Администратор"),
    ]

    # Комменты '# type: ignore[var-annotated]' для mypy - чтобы не требовал аннотаций типов
    first_name = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Имя",
        help_text="Имя пользователя",
    )  # type: ignore[var-annotated]

    last_name = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Фамилия",
        help_text="ФамилияФамилия пользователя",
    )  # type: ignore[var-annotated]

    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Номер телефона",
        help_text="Укажите ваш номер телефона",
    )  # type: ignore[var-annotated]

    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        help_text="Электронная почта пользователя",
        error_messages={"unique": "Пользователь с таким email уже существует."},
    )  # type: ignore[var-annotated]

    role = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Роль",
        help_text="Укажите вашу роль",
        choices=ROLE_CHOICES,
        default="user",
    )  # type: ignore[var-annotated]

    image = models.ImageField(
        upload_to="avatars/",
        verbose_name="Аватар",
        help_text="Загрузите ваш аватар",
        blank=True,
        null=True,
    )  # type: ignore[var-annotated]

    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
    )  # type: ignore[var-annotated]

    is_staff = models.BooleanField(
        default=False,
        verbose_name="Сотрудник",
    )  # type: ignore[var-annotated]

    is_superuser = models.BooleanField(
        default=False,
        verbose_name="Суперпользователь",
    )  # type: ignore[var-annotated]

    last_login = models.DateTimeField(
        auto_now=True,
        verbose_name="Последний вход",
    )  # type: ignore[var-annotated]

    date_joined = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата регистрации",
    )  # type: ignore[var-annotated]

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
        "phone",
    ]  # поля, требуемые при создании пользователя (кроме email и пароля)

    id: int  # Для mypy

    def __str__(self):
        """
        Возвращает строковое представление пользователя.
        :return: Строковое представление пользователя
        """
        return self.email

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
