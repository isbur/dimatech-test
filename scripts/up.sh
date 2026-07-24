#!/bin/bash

set -e

echo "[INFO] Starting up the project"

if ! pixi --version | grep -q "0.73"; then
    echo "[WARNING] Pixi version is not 0.73, the repository is written assuming 0.73"
    echo "[WARNING] Most likely this won't affect you, but stability is not guaranteed"
    echo "[WARNING] Current Pixi version is $(pixi --version)"
fi

if [ ! -f "$PIXI_PROJECT_ROOT/.env" ]; then
    echo "[ERROR] Missing $PIXI_PROJECT_ROOT/.env — copy .env.example and fill in secrets"
    exit 1
fi

set -a
# shellcheck disable=SC1091
source "$PIXI_PROJECT_ROOT/.env"
set +a

: "${POSTGRES_USER:?POSTGRES_USER is required in .env}"
: "${POSTGRES_PASSWORD:?POSTGRES_PASSWORD is required in .env}"
: "${POSTGRES_DB:?POSTGRES_DB is required in .env}"
POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"

PSQL=(psql -d postgres -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -v ON_ERROR_STOP=1)

# Identifiers from .env must be simple names (no SQL injection / quoting issues).
for _ident in "$POSTGRES_USER" "$POSTGRES_DB"; do
    if [[ ! "$_ident" =~ ^[a-zA-Z_][a-zA-Z0-9_]*$ ]]; then
        echo "[ERROR] Invalid SQL identifier in .env: ${_ident}"
        exit 1
    fi
done

# Dollar-quote the password so special characters are safe in SQL.
sql_password_literal() {
    local raw="$1"
    local tag="pw"
    while [[ "$raw" == *"\$${tag}\$"* ]]; do
        tag="${tag}x"
    done
    printf '$%s$%s$%s$' "$tag" "$raw" "$tag"
}

PASSWORD_SQL=$(sql_password_literal "$POSTGRES_PASSWORD")

if [ ! -d "$PIXI_PROJECT_ROOT/.local/pgdata" ]; then
    mkdir -p "$PIXI_PROJECT_ROOT/.local/pgdata"
    chmod 700 "$PIXI_PROJECT_ROOT/.local/pgdata"
fi

if [ ! -f "$PIXI_PROJECT_ROOT/.local/pgdata/postgresql.conf" ]; then
    echo "[INFO] Initializing PGDATA folder"

    initdb -D "$PIXI_PROJECT_ROOT/.local/pgdata" \
     -c listen_addresses='localhost' \
     -c port=5432 \
     -c log_timezone='UTC' \
     -c timezone='UTC' \
     -c datestyle='iso, ymd'
fi


echo "[INFO] Starting Postgres"

PGDATA="$PIXI_PROJECT_ROOT/.local/pgdata" postgres &> /dev/null &

while ! pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT"; do
    sleep 1
done

echo "[INFO] Postgres is ready"

if ! "${PSQL[@]}" -tAc "SELECT 1 FROM pg_roles WHERE rolname = '${POSTGRES_USER}'" | grep -q 1; then
    echo "[INFO] Creating role ${POSTGRES_USER}"
    "${PSQL[@]}" -c "CREATE ROLE ${POSTGRES_USER} LOGIN CREATEDB PASSWORD ${PASSWORD_SQL}"
else
    echo "[INFO] Updating password for role ${POSTGRES_USER}"
    "${PSQL[@]}" -c "ALTER ROLE ${POSTGRES_USER} WITH LOGIN CREATEDB PASSWORD ${PASSWORD_SQL}"
fi

if ! "${PSQL[@]}" -tAc "SELECT 1 FROM pg_database WHERE datname = '${POSTGRES_DB}'" | grep -q 1; then
    echo "[INFO] Creating database ${POSTGRES_DB}"
    "${PSQL[@]}" -c "CREATE DATABASE ${POSTGRES_DB} OWNER ${POSTGRES_USER}"
else
    echo "[INFO] Ensuring ${POSTGRES_USER} owns database ${POSTGRES_DB}"
    "${PSQL[@]}" -c "ALTER DATABASE ${POSTGRES_DB} OWNER TO ${POSTGRES_USER}"
fi

echo "[INFO] Granting privileges on ${POSTGRES_DB} to ${POSTGRES_USER}"
"${PSQL[@]}" -c "GRANT ALL PRIVILEGES ON DATABASE ${POSTGRES_DB} TO ${POSTGRES_USER}"
psql -d "$POSTGRES_DB" -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -v ON_ERROR_STOP=1 \
    -c "GRANT ALL ON SCHEMA public TO ${POSTGRES_USER}" \
    -c "ALTER SCHEMA public OWNER TO ${POSTGRES_USER}"

alembic upgrade head

pixi run dev
