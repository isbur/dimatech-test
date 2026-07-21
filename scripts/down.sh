#!/bin/bash

echo "[INFO] Stopping the project"

pg_ctl -D "$PIXI_PROJECT_ROOT/.local/pgdata" stop

echo "[INFO] Postgres is stopped"