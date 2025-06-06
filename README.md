# SB1: Доска объявлений

## Описание проекта

Backend-часть для сайта объявлений. Платформа позволяет пользователям публиковать объявления, оставлять отзывы, а администраторам — управлять контентом и пользователями.

## Основные возможности

-   **Аутентификация и Авторизация:** Регистрация, вход пользователей, управление сессиями с использованием JWT токенов.
-   **Управление пользователями:** Разделение ролей (пользователь, администратор), управление профилем.
-   **Восстановление пароля:** Возможность сброса и восстановления пароля через электронную почту.
-   **Управление объявлениями (CRUD):**
    -   Пользователи могут создавать, читать, обновлять и удалять свои объявления.
    -   Администраторы могут управлять всеми объявлениями.
-   **Отзывы:** Пользователи могут оставлять отзывы к объявлениям. Администраторы могут управлять всеми отзывами.
-   **Поиск:** Поиск объявлений по названию.
-   **Пагинация:** Для списков объявлений.

## Технологический стек

-   **Backend:** Python, Django, Django REST framework
-   **База данных:** PostgreSQL
-   **Аутентификация:** djangorestframework-simplejwt
-   **Фильтрация/Поиск:** django-filter
-   **API документация:** drf-yasg (Swagger/OpenAPI/Redoc)
-   **Обработка изображений:** Pillow
-   **Контейнеризация:** Docker, Docker Compose
-   **Тестирование:** Pytest, pytest-django
-   **CORS:** django-cors-headers

## Начало работы

### Предварительные требования

-   Python 3.10+
-   Docker
-   Docker Compose

### Установка и запуск

1.  **Клонируйте репозиторий:**
    ```bash
    git clone https://github.com/stasm-skypro/diploma-sb1-docker.git
    ```

2.  **Настройка переменных окружения:**
    Создайте файл `.env` в корневой директории проекта (рядом с `compose.yml`). Вы можете скопировать `env.example` (если он есть) или создать новый со следующим содержимым:

    ```env
    # Django settings
    SECRET_KEY=your_very_secret_django_key_here
    DEBUG=True
    ALLOWED_HOSTS=localhost,127.0.0.1

    # Database settings (PostgreSQL)
    POSTGRES_DB=bulletin
    POSTGRES_USER=user
    POSTGRES_PASSWORD=password
    POSTGRES_HOST=db # Имя сервиса БД в docker compose.yaml
    POSTGRES_PORT=5432

    # Email settings (для восстановления пароля)
    EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
    EMAIL_HOST=smtp.example.com
    EMAIL_PORT=587
    EMAIL_USE_TLS=True
    EMAIL_USE_SSL=False
    EMAIL_HOST_USER=email@example.com
    EMAIL_HOST_PASSWORD=email_app_password

    REDIS_HOST=redis_host
    REDIS_PORT=redis_port

    CELERY_BROKER_URL=redis://${REDIS_HOST}:${REDIS_PORT}/0
    CELERY_RESULT_BACKEND=redis://${REDIS_HOST}:${REDIS_PORT}/0
    ```

3.  **Сборка и запуск Docker контейнеров:**
    ```bash
    docker compose up --build -d
    ```
    Эта команда соберет образы (если они еще не собраны) и запустит сервисы в фоновом режиме.

4.  **Применение миграций базы данных:**
    ```bash
    docker compose exec web python manage.py migrate
    ```
    По умолчанию все необходимые для функционирования приложения миграции уже включены и применяются автоматически на этапе `docker compose up`.

5.  **Создание суперпользователя (администратора):**
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```
    Следуйте инструкциям в консоли для создания администратора.

Приложение будет доступно по адресу `http://localhost:8000` (или порт, указанный в `compose.yaml`).
Документация API (Swagger/OpenAPI) будет доступна по адресу `http://localhost:8000/api/swagger/` или `http://localhost:8000/api/redoc/`. Также по адресу `http://localhost:8000/api/swaggerjson/` доступна версия документации в формате JSON без Swagger-UI.

## Модели данных

### Пользователь (`User`)

-   `id` (IntegerField, Primary Key, Auto-increment): Уникальный идентификатор.
-   `first_name` (CharField): Имя пользователя.
-   `last_name` (CharField): Фамилия пользователя.
-   `phone` (CharField): Телефон для связи.
-   `email` (EmailField, Unique): Электронная почта, используется в качестве логина.
-   `password` (CharField): Пароль пользователя (хранится в хэшированном виде).
-   `role` (CharField): Роль пользователя (например, `user`, `admin`). По умолчанию `user`.
-   `image` (ImageField, опционально): Аватар пользователя.
-   `is_active` (BooleanField): Активен ли пользователь. По умолчанию `True`.
-   `is_staff` (BooleanField): Является ли пользователь персоналом. По умолчанию `False`.
-   `is_superuser` (BooleanField): Является ли пользователь суперпользователем. По умолчанию `False`.
-   `last_login` (DateTimeField, auto_now_add=True): Время последнего входа.
-   `date_joined` (DateTimeField, auto_now_add=True): Дата регистрации.

### Объявление (`Bulletin`)

-   `id` (IntegerField, Primary Key, Auto-increment): Уникальный идентификатор.
-   `title` (CharField): Название товара/объявления.
-   `price` (PositiveIntegerField): Цена товара (целое положительное число).
-   `description` (TextField, опционально): Описание товара.
-   `author` (ForeignKey to `User`): Пользователь, создавший объявление.
-   `created_at` (DateTimeField, auto_now_add=True): Дата и время создания объявления.
-   *Сортировка по умолчанию: по `created_at` в порядке убывания (новые выше).*

### Отзыв (`Review`)

-   `id` (IntegerField, Primary Key, Auto-increment): Уникальный идентификатор.
-   `text` (TextField): Текст отзыва.
-   `author` (ForeignKey to `User`): Пользователь, оставивший отзыв.
-   `bulletin` (ForeignKey to `Bulletin`): Объявление, к которому оставлен отзыв.
-   `created_at` (DateTimeField, auto_now_add=True): Дата и время создания отзыва.

## API Эндпоинты

Префикс для всех API эндпоинтов: `/api/`

### Аутентификация и Пользователи

#### 1. Регистрация пользователя
-   **POST** `/api/user/users/`
-   **Request body:**
    ```json
    {
        "first_name": "Имя",
        "last_name": "Фамилия",
        "phone": "+71234567890",
        "email": "user@example.com",
        "password": "password123",
        "password_confirmation": "password123"
    }
    ```

#### 2. Получение JWT токенов (Вход)
-   **POST** `/api/login/`
-   **Request body:**
    ```json
    {
        "email": "user@example.com",
        "password": "password123"
    }
    ```
-   **Response (200 OK):**
    ```json
    {
        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    ```

#### 3. Обновление Access токена
-   **POST** `/api/token/refresh/`
-   **Request body:**
    ```json
    {
        "refresh": "your_refresh_token"
    }
    ```
-   **Response (200 OK):**
    ```json
    {
        "access": "new_access_token"
    }
    ```

#### 4. Управление текущим пользователем (Профиль)
-   **GET** `/api/user/users/me/`: Получить данные текущего пользователя.
-   **PUT/PATCH** `/api/user/users/me/`: Обновить данные текущего пользователя.
-   **DELETE** `/api/user/users/me/`: Удалить (деактивировать) текущего пользователя.

#### 5. Сброс пароля (Запрос на сброс)
-   **POST** `/api/user/reset_password/`
-   **Request body:**
    ```json
    {
        "email": "user@example.com"
    }
    ```
-   **Действие:** Сервер отправляет на указанную почту ссылку для сброса пароля. Ссылка формируется на основе `PASSWORD_RESET_CONFIRM_URL` из настроек (например, `http://localhost:8000/reset_password_confirm/?uid={uid}&token={token}/`).

#### 6. Сброс пароля (Подтверждение нового пароля)
-   **POST** `/api/user/reset_password_confirm/`
-   **Request body:**
    ```json
    {
        "uid": "base64_encoded_user_id",
        "token": "password_reset_token",
        "new_password": "YourNewP4$$W0RD"
    }
    ```

### Объявления (`/api/bulletin/bulletins/`)

-   **GET** `/api/bulletin/bulletins/`: Получение списка всех объявлений.
    -   Доступ: Анонимные пользователи, Авторизованные пользователи, Администраторы.
    -   Поддерживает пагинацию (по умолчанию 4 объекта на странице).
    -   Поддерживает поиск по названию (`title`) через query-параметр: `/api/bulletins/?title=искомое_слово`. (Реализовано с `django-filter`).
-   **POST** `/api/bulletin/bulletins/`: Создание нового объявления.
    -   Доступ: Авторизованные пользователи.
-   **GET** `/api/bulletin/bulletins/{id}/`: Получение конкретного объявления.
    -   Доступ: Авторизованные пользователи, Администраторы.
-   **PUT/PATCH** `/api/bulletin/bulletins/{id}/`: Обновление объявления.
    -   Доступ: Владелец объявления или Администратор.
-   **DELETE** `/api/bulletin/bulletins/{id}/`: Удаление объявления.
    -   Доступ: Владелец объявления или Администратор.
-   **GET** `/api/bulletin/bulletins/me/`: Получение списка объявлений текущего авторизованного пользователя.
    -   Доступ: Авторизованные пользователи.

### Отзывы (`/api/bulletins/{ad_pk}/reviews/`)

-   **GET** `/api/bulletins/{ad_pk}/reviews/`: Получение списка всех отзывов для объявления с ID=`ad_pk`.
    -   Доступ: Авторизованные пользователи, Администраторы.
-   **POST** `/api/bulletins/{ad_pk}/reviews/`: Создание нового отзыва для объявления с ID=`ad_pk`.
    -   Доступ: Авторизованные пользователи.
-   **GET** `/api/bulletins/{ad_pk}/reviews/{review_pk}/`: Получение конкретного отзыва с ID=`review_pk` для объявления с ID=`ad_pk`.
    -   Доступ: Авторизованные пользователи, Администраторы.
-   **PUT/PATCH** `/api/bulletins/{ad_pk}/reviews/{review_pk}/`: Обновление отзыва.
    -   Доступ: Владелец отзыва или Администратор.
-   **DELETE** `/api/bulletins/{ad_pk}/reviews/{review_pk}/`: Удаление отзыва.
    -   Доступ: Владелец отзыва или Администратор.

## Права доступа (Permissions)

-   **Анонимный пользователь:**
    -   Может получать список объявлений (`GET /api/bulletin/bulletins/`).
-   **Авторизованный пользователь (`user`):**
    -   Все права анонимного пользователя.
    -   Получать одно объявление (`GET /api/bulletin/bulletins/{id}/`).
    -   Создавать объявление (`POST /api/bulletin/bulletins/`).
    -   Редактировать и удалять **свои** объявления.
    -   Получать список своих объявлений (`GET /api/bulletin/bulletins/me/`).
    -   Получать список отзывов к объявлению (`GET /api/bulletin/bulletins/{ad_pk}/reviews/`).
    -   Получать один отзыв (`GET /api/bulletin/bulletins/{ad_pk}/reviews/{review_pk}/`).
    -   Создавать отзывы (`POST /api/bulletin/bulletins/{ad_pk}/reviews/`).
    -   Редактировать и удалять **свои** отзывы.
    -   Управлять своим профилем (`GET/PUT/PATCH/DELETE /api/user/users/`).
-   **Администратор (`admin`):**
    -   Все права авторизованного пользователя.
    -   Редактировать и удалять **любые** объявления.
    -   Редактировать и удалять **любые** отзывы.
    -   Управлять всеми пользователями (просмотр списка, создание, редактирование, удаление через `/api/user/users/`, `/api/user/users/{id}/`).

## Тестирование

-   Тесты написаны с использованием библиотеки `pytest` и `pytest-django`.
-   Для запуска тестов выполните команду в контейнере `web` (убедитесь, что контейнеры запущены):
    ```bash
    docker compose exec web pytest .
    ```
-   Тесты покрывают основные функции платформы, включая CRUD операции для моделей, аутентификацию, права доступа и логику API эндпоинтов.

## Docker

-   Проект полностью контейнеризирован с использованием Docker и Docker Compose.
-   `Dockerfile` (в директории сервиса `web`) описывает сборку образа Django-приложения.
-   `compose.yml` (в корне проекта) оркестрирует запуск сервисов приложения:
    -   `web`: Django-приложение Gunicorn/Daphne.
    -   `db`: База данных PostgreSQL.
    -   (Опционально) `nginx`: Веб-сервер для раздачи статики и проксирования запросов к `web`.
-   Для сборки и запуска см. раздел Установка и запуск.
