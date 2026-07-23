# syntax=docker/dockerfile:1

# ---------------------------------------------------------------------------
# Stage 1: install Pixi, resolve the `dist` environment from the lockfile
# ---------------------------------------------------------------------------
FROM debian:bookworm-slim AS deps

ARG PIXI_VERSION=v0.73.0

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -fsSL https://pixi.sh/install.sh | PIXI_VERSION=${PIXI_VERSION} bash

ENV PATH="/root/.pixi/bin:${PATH}"

WORKDIR /app

# Install deps before copying sources so dependency layers stay cached.
COPY pixi.toml pixi.lock ./
RUN --mount=type=cache,target=/root/.cache/rattler \
    pixi install --locked -e dist

# ---------------------------------------------------------------------------
# Stage 2: distroless runtime — conda env prefix + application sources
# Conda prefixes are not relocatable: path must match the builder (/app/...).
# ---------------------------------------------------------------------------
FROM gcr.io/distroless/cc-debian12:nonroot AS runtime

WORKDIR /app

COPY --from=deps --chown=nonroot:nonroot /app/.pixi/envs/dist /app/.pixi/envs/dist
COPY --from=deps /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/ca-certificates.crt

COPY --chown=nonroot:nonroot src /app/src
COPY --chown=nonroot:nonroot migrations /app/migrations
COPY --chown=nonroot:nonroot alembic.ini /app/alembic.ini

ENV PATH="/app/.pixi/envs/dist/bin" \
    CONDA_PREFIX="/app/.pixi/envs/dist" \
    PYTHONPATH=/app/src \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt

USER nonroot
EXPOSE 8000

# Distroless has no shell — invoke the env python directly.
ENTRYPOINT ["/app/.pixi/envs/dist/bin/python"]
CMD ["-m", "sanic", "dimatech.main:create_app", "--factory", "--host=0.0.0.0", "--port=8000"]
