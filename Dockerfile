FROM python:3.12-slim

# Install uv (binary release, no Python deps needed). Pinned by digest
# in addition to tag — the tag is mutable; the digest gives a stable
# guarantee that every build pulls the same uv layer.
COPY --from=ghcr.io/astral-sh/uv:0.11.15@sha256:e590846f4776907b254ac0f44b5b380347af5d90d668138ca7938d1b0c2f98d3 /uv /uvx /usr/local/bin/

ENV UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv \
    UV_COMPILE_BYTECODE=1

WORKDIR /app

# Lockfile + manifest first so the install layer is reused on source-only edits.
# README intentionally excluded: with `[tool.uv].package = false`, uv doesn't
# read it at sync time, and copying it here would bust the dep cache on
# README-only edits.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-default-groups

# Application source (.dockerignore keeps host venv / .git / caches out).
COPY . .

EXPOSE 80

# `--frozen --no-sync` keeps the container hermetic at start: don't
# re-resolve, don't fetch from PyPI.
CMD ["sh", "-c", "sleep 20 && uv run --frozen --no-sync uvicorn app.main:app --host 0.0.0.0 --port 80 --reload"]
