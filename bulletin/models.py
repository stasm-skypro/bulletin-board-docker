# bulletin/models.py
from django.db import models


class Bulletin(models.Model):
    """
    Определяет модель объявления.
    Attributes:
             title (str): Наименование товара;
             price (int): Цена товара;
       description (str): Описание товара;
                  author: Пользователь, который создал объявление;
              created_at: Время и дата создания объявления;
    """

    title = models.CharField(
        max_length=255,
        verbose_name="Наименование",
        help_text="Наименование товара",
    )  # type: ignore[var-annotated]

    price = models.PositiveIntegerField(
        verbose_name="Цена",
        help_text="Цена товара",
    )  # type: ignore[var-annotated]

    description = models.TextField(
        verbose_name="Описание",
        help_text=" ",
    )  # type: ignore[var-annotated]

    author = models.ForeignKey(
        "user.User",
        on_delete=models.CASCADE,
        verbose_name="Автор",
        help_text="Пользователь, который создал объявление",
    )  # type: ignore[var-annotated]

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания",
        help_text="Время и дата создания объявления",
    )  # type: ignore[var-annotated]

    def __str__(self):
        """
        Возвращает строковое представление объявления.
        :return: Строковое представление объявления
        """
        return self.title

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        ordering = ["-created_at"]


class Review(models.Model):
    """
    Определяет модель отзыва.
    Attributes:
              text (str): Текст отзыва;
                  author: Пользователь, который оставил отзыв;
                bulletin: Объявление, под которым оставлен отзыв;
              created_at: Время и дата создания отзыва;
    """

    text = models.TextField(
        verbose_name="Текст",
        help_text="Текст отзыва",
    )  # type: ignore[var-annotated]

    author = models.ForeignKey(
        "user.User",
        on_delete=models.CASCADE,
        verbose_name="Автор",
        help_text="Пользователь, который оставил отзыв",
    )  # type: ignore[var-annotated]

    bulletin = models.ForeignKey(
        "bulletin.Bulletin",
        related_name="reviews",
        on_delete=models.CASCADE,
        verbose_name="Объявление",
        help_text="Объявление, под которым оставлен отзыв",
    )  # type: ignore[var-annotated]

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Время и дата создания отзыва",
        help_text="Время и дата создания отзыва",
    )  # type: ignore[var-annotated]

    def __str__(self):
        """
        Возвращает строковое представление отзыва.
        :return: Строковое представление отзыва
        """
        return self.text[:30]

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-created_at"]
