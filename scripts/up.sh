#!/bin/bash

set -e

echo "[INFO] Starting up the project"

if ! $( pixi --version | grep -q "0.73" ); then
    echo "[WARNING] Pixi version is not 0.73, the repository is written assuming 0.73"
    echo "[WARNING] Most likely this won't affect you, but stability is not guaranteed"
    echo "[WARNING] Current Pixi version is $(pixi --version)"
fi

if [ ! -d $PIXI_PROJECT_ROOT/.pixi/envs/default/pgdata ]; then
    mkdir -p $PIXI_PROJECT_ROOT/.pixi/envs/default/pgdata
    chmod 700 $PIXI_PROJECT_ROOT/.pixi/envs/default/pgdata
fi

if [ ! -f $PIXI_PROJECT_ROOT/.pixi/envs/default/pgdata/postgresql.conf ]; then
    initdb -D $PIXI_PROJECT_ROOT/.pixi/envs/default/pgdata \
     -c listen_addresses='localhost' \
     -c port=5432 \
     -c log_timezone='UTC' \
     -c timezone='UTC' \
     -c datestyle='iso, ymd'
fi

PGDATA=$PIXI_PROJECT_ROOT/.pixi/envs/default/pgdata postgres