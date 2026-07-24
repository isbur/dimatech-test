# dimatech-test

REST API (Sanic + SQLAlchemy + PostgreSQL) для тестового задания Dimatech.

При конкурентных платежах на один счёт баланс обновляется под блокировкой SELECT FOR UPDATE, чтобы начисления не затирали друг друга. Идемпотентность по transaction_id обеспечивается уникальным ограничением и повторным чтением записи при гонке вставки. Если счёта ещё нет и его одновременно создают несколько вебхуков, INSERT выполняется в SAVEPOINT: при IntegrityError вложенная транзакция откатывается, после чего начисление идёт на уже созданный конкурентом счёт.

## Учётные данные из миграций

Создаются Alembic-миграциями:

| Роль  | Email               | Пароль     |
|-------|---------------------|------------|
| user  | `user@example.com`  | `password1` |
| admin | `admin@example.com` | `password1` |

Пример секрета вебхука (также в `.env.example`): `gfdmhghif38yrf9ew0jkf32`.


## Запуск через Docker Compose

1. Клонировать репозиторий и перейти в него:
```sh
git clone https://github.com/isbur/dimatech-test.git
cd dimatech-test
```

2. Создать `.env` (Compose читает из него секреты и параметры Postgres):
```sh
cp .env.example .env
# при необходимости отредактируйте JWT_SECRET / WEBHOOK_SECRET / POSTGRES_PASSWORD
openssl rand -hex 32  # Для JWT_SECRET
openssl rand -hex 16  # Для POSTGRES_PASSWORD
python -c "import secrets,string; a=string.ascii_lowercase+string.digits; print(''.join(secrets.choice(a) for _ in range(23)))" # Для WEBHOOK_SECRET
nano .env
```

3. Собрать образ и поднять Postgres + migrate + приложение:
```sh
docker compose up --build -d
```

Образ приложения — двухступенчатый Dockerfile: Pixi ставит окружение **`dist`**,
затем prefix копируется в distroless-runtime.

4. Открыть:
- API: http://localhost:8000
- OpenAPI / Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/health

Остановка:
```sh
docker compose down
```

## Запуск без Docker (pixi)

Проект использует `pixi` для локального окружения (Python, PostgreSQL, зависимости).

1. Клонировать репозиторий:
```sh
git clone https://github.com/isbur/dimatech-test.git
```

2. Установить `pixi`:
```sh
curl -fsSL https://pixi.sh/install.sh | sh
```

3. Перейти в репозиторий:
```sh
cd dimatech-test
```

4. Установить зависимости:
```sh
pixi install
```

5. Сгенерировать секреты, создать и отредактировать `.env`:
```sh
openssl rand -hex 32
openssl rand -hex 16
python -c "import secrets,string; a=string.ascii_lowercase+string.digits; print(''.join(secrets.choice(a) for _ in range(23)))"
cp .env.example .env
nano .env
```

6. Запустить локальный Postgres, миграции и приложение (происходит захват термиала):
```sh
pixi run up
```

Остановка Postgres:
```sh
pixi run down
```