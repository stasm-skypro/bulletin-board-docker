# bulletin/serializers.py
from rest_framework import serializers

from .models import Bulletin, Review


class BulletinListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для краткого представления объявлений (список).

    Используется при отображении списка объявлений. Не включает описание и отзывы.
    """

    class Meta:
        model = Bulletin
        fields = ["id", "title", "price", "created_at"]
        read_only_fields = ["id", "created_at"]


class BulletinDetailSerializer(serializers.ModelSerializer):
    """
    Сериализатор для детального представления объявления.

    Используется при отображении одного объявления. Не включает описание и отзывы.
    """

    class Meta:
        model = Bulletin
        fields = ["id", "title", "price", "description", "author", "created_at"]
        read_only_fields = ["id", "author", "created_at"]


class BulletinCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания нового объявления.

    Поля 'id', 'author' и 'created_at' устанавливаются автоматически и доступны только для чтения.
    """

    class Meta:
        model = Bulletin
        fields = ["id", "title", "price", "description", "author", "created_at"]
        read_only_fields = ["id", "author", "created_at"]

    def create(self, validated_data):
        """
        Создаёт новый объект объявления и автоматически присваивает текущего пользователя как автора.

        :validated_data (dict): Валидированные данные для создания объявления
        :returns: Bulletin: Созданный объект объявления
        """
        # автоматически назначаем автора на текущего пользователя
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Review.

    Используется для преобразования объектов отзыва в JSON и обратно.
    Поля 'id', 'author' и 'created_at' доступны только для чтения.
    """

    class Meta:
        model = Review
        fields = ["id", "text", "author", "bulletin", "created_at"]
        read_only_fields = ["id", "author", "bulletin", "created_at"]
