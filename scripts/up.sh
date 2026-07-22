#!/bin/bash

set -e

echo "[INFO] Starting up the project"

if ! pixi --version | grep -q "0.73"; then
    echo "[WARNING] Pixi version is not 0.73, the repository is written assuming 0.73"
    echo "[WARNING] Most likely this won't affect you, but stability is not guaranteed"
    echo "[WARNING] Current Pixi version is $(pixi --version)"
fi

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
     PGDATA="$PIXI_PROJECT_ROOT/.local/pgdata" postgres &> /dev/null &

    echo "[INFO] Starting Postgres"

    while ! pg_isready -h localhost -p 5432; do
        sleep 1
    done

    echo "[INFO] Creating database redcoon"

    createdb -h localhost -p 5432   # создать базу redcoon

    echo "[INFO] Postgres is ready"
else
    echo "[INFO] Starting Postgres"

    PGDATA="$PIXI_PROJECT_ROOT/.local/pgdata" postgres &> /dev/null &

    while ! pg_isready -h localhost -p 5432; do
        sleep 1
    done

    echo "[INFO] Postgres is ready"
fi



if ! psql -h localhost -p 5432 -lqt | cut -d \| -f 1 | grep -qw dimatech; then
  echo "[INFO] Creating database dimatech"
  psql -h localhost -p 5432 -c "CREATE DATABASE dimatech"
fi

pixi run dev