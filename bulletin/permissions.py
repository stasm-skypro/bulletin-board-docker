# bulletin/permissions.py
"""
| Действие                    | Аноним  | Пользователь | Администратор |
| --------------------------- | ------- | ------------ | ------------- |
| Получить список объявлений  | ✅      | ✅          | ✅            |
| Получить одно объявление    | ❌      | ✅          | ✅            |
| Создать объявление          | ❌      | ✅          | ✅            |
| Редактировать/удалить своё  | ❌      | ✅          | ✅            |
| Редактировать/удалить чужое | ❌      | ❌          | ✅            |
| Получить список отзывов     | ❌      | ✅          | ✅            |
| Создать отзыв               | ❌      | ✅          | ✅            |
| Редактировать/удалить свой  | ❌      | ✅          | ✅            |
| Редактировать/удалить чужой | ❌      | ❌          | ✅            |

"""

from rest_framework import permissions


class IsAuthorOrAdminOrReadOnlyForBulletins(permissions.BasePermission):
    """
    - Аноним может только смотреть список.
    - Подробный просмотр, создание, изменение, удаление — только авторизованным.
    - Изменение/удаление — только автору или админу.
    """

    def has_permission(self, request, view):
        """
        Определяет уровень доступа на уровне запроса (до получения объекта).

        Разрешает доступ к списку объявлений (`list`) для всех пользователей, включая анонимных.
        Для остальных действий (создание, детальный просмотр, редактирование и удаление)
        требуется аутентификация.

        :param request: объект запроса
        :param view: текущий view (ручка)
        :return: True, если доступ разрешён, иначе False
        """
        # Только список объявлений доступен анонимам
        if view.action == "list":
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Определяет уровень доступа на уровне конкретного объекта объявления.

        Анонимным пользователям запрещён просмотр отдельных объявлений (только список).
        Безопасные методы (GET, HEAD, OPTIONS) разрешены только аутентифицированным пользователям.
        Изменение и удаление разрешено только автору объявления или участнику группы 'Администраторы'.

        :param request: объект запроса
        :param view: текущий view
        :param obj: объект Bulletin, к которому осуществляется доступ
        :return: True, если доступ разрешён, иначе False
        """
        # Просмотр конкретного объявления запрещён анонимам
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return obj.author == request.user or request.user.groups.filter(name="Администраторы").exists()


class IsAuthenticatedOrReadOnlyForReviews(permissions.BasePermission):
    """
    - Только авторизованные могут видеть и создавать отзывы.
    - Изменять и удалять — только автор или админ.
    """

    def has_permission(self, request, view):
        """
        Определяет уровень доступа на уровне запроса (до получения объекта).

        Разрешает доступ к списку отзывов (`list`) для всех пользователей, включая анонимных.
        Для остальных действий (создание, детальный просмотр, редактирование и удаление)
        требуется аутентификация.

        :param request: объект запроса
        :param view: текущий view (ручка)
        :return: True, если доступ разрешён, иначе False
        """
        # Даже список — только авторизованным
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Определяет уровень доступа на уровне конкретного объекта отзыва.

        Анонимным пользователям запрещён просмотр отдельных запросов (только список).
        Безопасные методы (GET, HEAD, OPTIONS) разрешены только аутентифицированным пользователям.
        Изменение и удаление разрешено только автору запроса или участнику группы 'Администраторы'.

        :param request: объект запроса
        :param view: текущий view
        :param obj: объект Review, к которому осуществляется доступ
        :return: True, если доступ разрешён, иначе False
        """
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return obj.author == request.user or request.user.groups.filter(name="Администраторы").exists()
