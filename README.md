# dimatech-test

REST API (Sanic + SQLAlchemy + PostgreSQL) for the Dimatech take-home assignment.

## Seed credentials

Created by Alembic migrations:

| Role  | Email               | Password   |
|-------|---------------------|------------|
| user  | `user@example.com`  | `password1` |
| admin | `admin@example.com` | `password1` |

Webhook example secret (also in `.env.example`): `gfdmhghif38yrf9ew0jkf32`.

## Run with Docker Compose (local build)

1. Clone and enter the repo:
```sh
git clone https://github.com/isbur/dimatech-test.git
cd dimatech-test
```

2. Create `.env` (Compose still needs JWT/webhook secrets from it):
```sh
cp .env.example .env
# edit JWT_SECRET / WEBHOOK_SECRET if you want
```

3. Build and start Postgres + migrate + app:
```sh
docker compose up --build -d
```

The app image is a two-stage build: Pixi installs the **`dist`** environment
(runtime deps only, no PostgreSQL/dev tools), then that prefix is copied into a
distroless runtime.
4. Open:
- API: http://localhost:8000
- OpenAPI / Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/health

Stop:
```sh
docker compose down
```

### Optional: pull image from GHCR (no local build)

If the image is published to GitHub Container Registry:

```sh
docker compose -f compose.yaml -f compose.ghcr.yaml pull
docker compose -f compose.yaml -f compose.ghcr.yaml up -d
```

Publish (maintainer):
```sh
docker build -t ghcr.io/isbur/dimatech-test:latest .
echo "$GHCR_TOKEN" | docker login ghcr.io -u USERNAME --password-stdin
docker push ghcr.io/isbur/dimatech-test:latest
```

## Run without Docker (pixi)

The project uses `pixi` for the local toolchain (Python, PostgreSQL, deps).

1. Clone the repository:
```sh
git clone https://github.com/isbur/dimatech-test.git
```

2. Install `pixi`:
```sh
curl -fsSL https://pixi.sh/install.sh | sh
```

3. Enter the repository:
```sh
cd dimatech-test
```

4. Install dependencies:
```sh
pixi install
```

5. Generate secrets, create and edit `.env`:
```sh
openssl rand -hex 32
python -c "import secrets,string; a=string.ascii_lowercase+string.digits; print(''.join(secrets.choice(a) for _ in range(23)))"
cp .env.example .env
nano .env
```

6. Start local Postgres, run migrations, and launch the app:
```sh
pixi run up
```

Stop Postgres:
```sh
pixi run down
```

## Техническое задание

Необходимо реализовать асинхронное веб приложение в парадигме REST API.

Время выполнения задачи 5 дней.


Стек:
- База данных - postgresql
- sqlalchemy - для работы с базой данных
- sanic - веб фреймворк(рекомендуемый, допускается альтернативный веб фрейморк НО НЕ DJANGO)
- docker compose


Необходимо реализовать работу со следующими сущностями:
1. Пользователь
2. Администратор
3. Счет - имеет баланс, привязан к пользователю
4. Платеж(пополнение баланса) - хранит уникальный идентификатор и сумму пополнения счета пользователя

Пользователь должен иметь следующие возможности:
1. Авторизоваться по email/password
2. Получить данные о себе(id, email, full_name)
3. Получить список своих счетов и балансов
4. Получить список своих платежей

Администратор должен иметь следующие возможности:
1. Авторизоваться по email/password
2. Получить данные о себе (id, email, full_name)
3. Создать/Удалить/Обновить пользователя
4. Получить список пользователей и список его счетов с балансами

Для работы с платежами должен быть реализован роут эмулирующий обработку вебхука от сторонней платежной системы.
Структура json-объекта для обработки вебхука должна состоять из следующих полей:
- `transaction_id` - уникальный идентификатор транзакции в “сторонней системе”
- `account_id` - уникальный идентификатор счета пользователя
- `user_id` - уникальный идентификатор счета пользователя
- `amount` - сумма пополнения счета пользователя
- `signature` - подпись объекта

signature должна формироваться через SHA256 хеш, для строки состоящей из конкатенации значений объекта в алфавитном порядке ключей и “секретного ключа” хранящегося в конфигурации проекта (`{account_id}{amount}{transaction_id}{user_id}{secret_key}`). 

Пример, для secret_key `gfdmhghif38yrf9ew0jkf32`:
```json
{
  "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
  "user_id": 1,
  "account_id": 1,
  "amount": 100,
  "signature": "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"
}
```

При обработке вебхука необходимо:
1. Проверить подпись объекта
2. Проверить существует ли у пользователя такой счет - если нет, его необходимо создать
3. Сохранить транзакцию в базе данных
4. Начислить сумму транзакции на счет пользователя

Транзакции являются уникальными, начисление суммы с одним transaction_id должно производиться только один раз.

Для тестирования приложения в миграции должен быть создан:
1. Тестовый пользователь
2. Счет тестового пользователя
3. Тестовый администратор

Для развертывания проекта необходимо реализовать docker compose конфигурацию состоящую из сервиса postgresql и сервиса приложения.
К реализованному заданию должна прилагаться краткая инструкция по запуску проекта в двух вариантах - с использованием docker compose и без него. В инструкции также должны быть предоставлены email/password для пользователя и администратора по умолчанию созданных в миграции.
