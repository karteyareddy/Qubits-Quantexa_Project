.PHONY: install backend frontend test lint build smoke docker-up docker-down

install:
	python -m pip install -r requirements.txt
	cd frontend && npm ci

backend:
	python -m uvicorn app.api.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

test:
	python -m pytest -q

lint:
	python -m ruff check backend
	python -m mypy backend/app
	cd frontend && npm run lint

build:
	cd frontend && npm run build

smoke:
	python scripts/smoke_test.py

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down
