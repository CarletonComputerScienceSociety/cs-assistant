.PHONY: setup cli migrate ingest test cov lint check format

setup:
	uv sync
	uv run pre-commit install

cli:
	uv run python -m src.apps.dev_cli

discord:
	uv run python -m src.apps.discord_bot

migrate:
	uv run alembic -c src/infrastructure/db/alembic.ini upgrade head

ingest:
	uv run python -m scripts.ingest

test:
	uv run pytest

cov:
	uv run pytest --cov-report=html
	@echo "HTML coverage report: htmlcov/index.html"

lint:
	uv run pre-commit run --all-files

check:
	uv run ruff check .

format:
	uv run black .
