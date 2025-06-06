# tests/test_review_viewset.py
"""
Что покрыто:
list — получение списка отзывов
retrieve — получение одного отзыва
create — создание отзыва
update — полное обновление отзыва
partial_update — частичное обновление отзыва
destroy — удаление отзыва
"""

from django.urls import reverse

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from bulletin.models import Bulletin, Review
from user.models import User


@pytest.fixture
def api_client():
    """
    Возвращает экземпляр APIClient для тестирования DRF.

    :return: Экземпляр APIClient
    :rtype: APIClient
    """
    return APIClient()


@pytest.fixture
def user(db):
    """
    Создаёт тестового пользователя.

    :param db: Фикстура для доступа к тестовой БД
    :return: Тестовый пользователь
    :rtype: User
    """
    return User.objects.create_user(email="reviewer@example.com", password="password")


@pytest.fixture
def user2(db):
    return User.objects.create_user(email="user2@example.com", password="password")


@pytest.fixture
def auth_client(api_client, user):
    """
    Возвращает клиента, аутентифицированного от имени тестового пользователя.

    :param api_client: API клиент
    :param user: Тестовый пользователь
    :return: Аутентифицированный клиент
    :rtype: APIClient
    """
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def bulletin(user):
    """
    Создаёт тестовое объявление, связанное с пользователем.

    :param user: Автор объявления
    :return: Объект Bulletin
    :rtype: Bulletin
    """
    return Bulletin.objects.create(
        title="Объявление для отзыва",
        price=10000,
        description="Описание объявления",
        author=user,
    )


@pytest.fixture
def review(user2, bulletin):
    """
    Создаёт тестовый отзыв для объявления.

    :param user2: Автор отзыва
    :param bulletin: Объявление, к которому привязан отзыв
    :return: Объект Review
    :rtype: Review
    """
    return Review.objects.create(
        text="Отличное объявление!",
        author=user2,
        bulletin=bulletin,
    )


def test_list_reviews(auth_client, bulletin, review):
    """
    Тестирует получение списка отзывов.

    - Отправляет GET-запрос на /reviews/
    - Проверяет, что статус ответа — 200 OK
    - Проверяет, что созданный отзыв присутствует в ответе
    :param api_client: Неавторизованный клиент
    :param review: Существующий отзыв
    """
    url = reverse("bulletin:bulletin-reviews-list", args=[bulletin.id])
    response = auth_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data["results"], list)
    assert any(r["id"] == review.id for r in response.data["results"])


def test_create_review(auth_client, bulletin):
    """
    Тестирует создание нового отзыва.

    - Отправляет POST-запрос на /reviews/
    - Проверяет, что статус ответа — 201 CREATED
    - Проверяет, что отзыв создан в базе данных

    :param auth_client: Аутентифицированный клиент
    :param bulletin: Объявление, к которому оставляется отзыв
    """
    url = reverse("bulletin:bulletin-reviews-list", args=[bulletin.id])
    data = {"text": "Хорошее объявление"}

    response = auth_client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED
    assert Review.objects.filter(text="Хорошее объявление").exists()


def test_update_review(auth_client, bulletin, review, user2):
    """
    Тестирует полное обновление отзыва (PUT).

    - Отправляет PUT-запрос на /reviews/<id>/
    - Проверяет статус ответа и изменение данных

    :param auth_client: Аутентифицированный клиент
    :param review: Объект отзыва
    """
    auth_client.force_authenticate(user=user2)
    url = reverse("bulletin:bulletin-reviews-detail", args=[bulletin.id, review.id])
    data = {"text": "Обновлённый отзыв"}

    response = auth_client.put(url, data)

    assert response.status_code == status.HTTP_200_OK
    review.refresh_from_db()
    assert review.text == "Обновлённый отзыв"


def test_partial_update_review(auth_client, bulletin, review, user2):
    """
    Тестирует частичное обновление отзыва (PATCH).

    - Отправляет PATCH-запрос на /reviews/<id>/
    - Проверяет, что изменилось только указанное поле

    :param auth_client: Аутентифицированный клиент
    :param review: Объект отзыва
    """
    auth_client.force_authenticate(user=user2)
    url = reverse("bulletin:bulletin-reviews-detail", args=[bulletin.id, review.id])
    data = {"text": "Частично обновлённый"}

    response = auth_client.patch(url, data)

    assert response.status_code == status.HTTP_200_OK
    review.refresh_from_db()
    assert review.text == "Частично обновлённый"


def test_delete_review(auth_client, bulletin, review, user2):
    """
    Тестирует удаление отзыва.

    - Отправляет DELETE-запрос на /reviews/<id>/
    - Проверяет, что отзыв удалён из базы данных

    :param auth_client: Аутентифицированный клиент
    :param review: Объект отзыва
    """
    auth_client.force_authenticate(user=user2)
    url = reverse("bulletin:bulletin-reviews-detail", args=[bulletin.id, review.id])

    response = auth_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Review.objects.filter(id=review.id).exists()


def test_cannot_update_foreign_review(auth_client, bulletin, review):
    """
    Текущий пользователь не может редактировать чужой отзыв.
    """
    url = reverse("bulletin:bulletin-reviews-detail", args=[bulletin.id, review.id])
    data = {"text": "Попытка изменить чужой отзыв"}

    response = auth_client.put(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_cannot_delete_foreign_review(auth_client, bulletin, review):
    """
    Текущий пользователь не может удалить чужой отзыв.
    """
    url = reverse("bulletin:bulletin-reviews-detail", args=[bulletin.id, review.id])

    response = auth_client.delete(url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Review.objects.filter(id=review.id).exists()


def test_bulletin_me_returns_user_bulletins(auth_client, user):
    """
    Тест экшена 'me' — должен возвращать только объявления текущего пользователя.
    """
    # Объявления текущего пользователя
    Bulletin.objects.create(title="Моё 1", price=1000, description="...", author=user)
    Bulletin.objects.create(title="Моё 2", price=2000, description="...", author=user)

    # Объявление другого пользователя
    other_user = User.objects.create_user(email="other@example.com", password="password")
    Bulletin.objects.create(title="Чужое", price=9999, description="...", author=other_user)

    url = reverse("bulletin:bulletins-me")
    response = auth_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    titles = [item["title"] for item in response.data["results"]]
    assert "Моё 1" in titles
    assert "Моё 2" in titles
    assert "Чужое" not in titles
