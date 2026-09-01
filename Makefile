.PHONY: install test lint format dev clean

install:
	uv sync --all-groups

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

dev:
	uv run python run_map_wormbase_ids.py

clean:
	rm -rf .pytest_cache .ruff_cache dist build *.egg-info output
