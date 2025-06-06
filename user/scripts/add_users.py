# user/scripts/add_user.py
"""
Начальная инициализация базы данных - скрипт для добавления пользователей.
В отличие от фикстур добавляет пользователей с исходными паролями, а не хэшами.
"""
from user.models import User

users = [
    ("Johny", "Walker", "johny.walker@example.com"),
    ("Jack", "Daniels", "jack.daniels@example.com"),
    ("Jim", "Beam", "jim.beam@example.com"),
    ("Jameson", "Irish", "jameson.irish@example.com"),
    ("Glen", "Fiddich", "glen.fiddich@example.com"),
    ("Chivas", "Regal", "chivas.regal@example.com"),
    ("Veuve", "Clicquot", "veuve.clicquot@example.com"),
    ("Remy", "Martin", "remy.martin@example.com"),
    ("Hennessy", "XO", "hennessy.xo@example.com"),
    ("Don", "Julio", "don.julio@example.com"),
]

for first_name, last_name, email in users:
    User.objects.create_user(  # type: ignore
        first_name=first_name, last_name=last_name, email=email, phone="+1234567890", password="P4$$w0rd"
    )
print("Users added")
