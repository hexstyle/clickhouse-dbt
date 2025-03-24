import jwt
import datetime
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Загрузка приватного ключа
with open("private_key.der", "rb") as key_file:
    private_key = serialization.load_der_private_key(
        key_file.read(),
        password=None,
        backend=default_backend()
    )

# Создание payload
payload = {
    "iss": "localhost",
    "sub": "airflow",
    "aud": "localhost",
    "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=9999),
    "iat": datetime.datetime.now(datetime.UTC)
}

# Генерация JWT-токена
token = jwt.encode(payload, private_key, algorithm="RS256", headers={"kid": "gb389a-9f76-gdjs-a92j-0242bk94356"})

print(f"Сгенерированный JWT-токен: {token}")
