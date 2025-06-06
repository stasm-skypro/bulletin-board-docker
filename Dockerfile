# Используем Python-образ
FROM python:3.12-slim

# Создаем группу и пользователя, чтобы комнды не выполнялись от имени root.
RUN groupadd -r groupdjango && useradd -r -g groupdjango userdj

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем переменные окружения
# Отключает создание .pyc файлов (байткода) при запуске Python-приложения.
# Обычно Python создаёт .pyc файлы в __pycache__, чтобы ускорить последующие загрузки модулей.
# В Docker это не нужно:
# Контейнеры часто одноразовые — кэш бесполезен.
# .pyc файлы могут 'засорять' тома и слои образа.
# Плюс: меньший размер образа, чище дерево файлов.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Установим netcat для ожидания сервисов
# nc нужен в entypont_*.sh, ждать база когда будет доступна, чтобы применить миграции.
RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*

# Устанавливаем curl для healthcheck-ов в docker compose
RUN apt update && apt install -y curl

# Копируем и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем все файлы проекта в контейнер
COPY . .

# Копируем скрипты и даём права на исполнение
COPY entrypoint-web.sh /entrypoint-web.sh
COPY entrypoint-celery.sh /entrypoint-celery.sh
RUN chmod +x /entrypoint-*.sh

# Создаем директорию для статики от имени root и назначаем права
RUN mkdir -p /app/staticfiles /app/static && chown -R userdj:groupdjango /app/staticfiles /app/static

# Возвращаем пользователя на userdj
USER userdj

# Указываем команду  по умолчанию для запуска проекта в контейнере при старте
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
