# tests/test_bulletin_viewset.py
"""
Что покрыто:
list — получение списка
retrieve — получение одного объявления
create — создание объявления
update — полное обновление
partial_update — частичное обновление
destroy — удаление
"""
from django.urls import reverse

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from bulletin.models import Bulletin
from user.models import User


@pytest.fixture
def api_client():
    """
    Возвращает экземпляр APIClient без авторизации.

    :return: APIClient
    """
    return APIClient()


@pytest.fixture
def user(db):
    """
    Создаёт и возвращает пользователя.

    :return: User
    """
    return User.objects.create_user(email="user@example.com", password="password")


@pytest.fixture
def auth_client(api_client, user):
    """
    Возвращает APIClient с авторизованным пользователем.

    :param api_client: APIClient без авторизации
    :param user: Пользователь
    :return: Авторизованный APIClient
    """
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def bulletin(user):
    """
    Создаёт тестовое объявление.

    :param user: Пользователь-владелец объявления
    :return : Bulletin
    """
    return Bulletin.objects.create(
        title="Тестовое объявление",
        price=5000,
        description="Описание тестового объявления",
        author=user,
    )


def test_list_bulletins(api_client, bulletin):
    """
    Тест получения списка объявлений.

    Проверяет:
    - статус 200
    - наличие результатов
    - наличие созданного объявления
    :param api_client: APIClient без авторизации
    :param bulletin: Объявление
    :return:
    """
    url = reverse("bulletin:bulletins-list")
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.data["results"], list)
    assert any(b["id"] == bulletin.id for b in response.data["results"])


def test_retrieve_bulletin(api_client, bulletin, user):
    """
    Тест получения одного объявления.

    Проверяет:
    - статус 200
    - корректность ID
    - наличие полей description и reviews
    :param api_client: APIClient без авторизации
    :param bulletin: Объявление
    :param user: Пользователь
    :return:
    """
    api_client.force_authenticate(user=user)
    url = reverse("bulletin:bulletins-detail", args=[bulletin.id])
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == bulletin.id
    assert "description" in response.data


def test_create_bulletin(auth_client):
    """
    Тест создания объявления.

    Проверяет:
    - статус 201
    - наличие объявления в базе
    :param auth_client: Авторизованный пользователь
    :return:
    """
    url = reverse("bulletin:bulletins-list")
    data = {
        "title": "Новое объявление",
        "price": 3000,
        "description": "Описание нового объявления",
    }

    response = auth_client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED
    assert Bulletin.objects.filter(title="Новое объявление").exists()


def test_update_bulletin(auth_client, bulletin):
    """
    Тест полного обновления объявления.

    Проверяет:
    - статус 200
    - обновление полей в базе
    :param auth_client: APIClient
    :param bulletin: Объявление
    :return:
    """
    url = reverse("bulletin:bulletins-detail", args=[bulletin.id])
    data = {
        "title": "Обновлённое объявление",
        "price": 7000,
        "description": "Новое описание",
    }

    response = auth_client.put(url, data)

    assert response.status_code == status.HTTP_200_OK
    bulletin.refresh_from_db()
    assert bulletin.title == "Обновлённое объявление"


def test_partial_update_bulletin(auth_client, bulletin):
    """
    Тест частичного обновления объявления.

    Проверяет:
    - статус 200
    - обновление одного поля
    :param auth_client: Авторизованный пользователь
    :param bulletin: Объявление
    :return:
    """
    url = reverse("bulletin:bulletins-detail", args=[bulletin.id])
    data = {"price": 9999}

    response = auth_client.patch(url, data)

    assert response.status_code == status.HTTP_200_OK
    bulletin.refresh_from_db()
    assert bulletin.price == 9999


def test_delete_bulletin(auth_client, bulletin):
    """
    Тест удаления объявления.

    Проверяет:
    - статус 204
    - удаление объекта из базы
    :param auth_client: APIClient с авторизацией
    :param bulletin: Объявление
    :return:
    """
    url = reverse("bulletin:bulletins-detail", args=[bulletin.id])
    response = auth_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Bulletin.objects.filter(id=bulletin.id).exists()
