.PHONY: backend-install frontend-install seed refresh test lint api frontend

backend-install:
	cd backend && python -m pip install -r requirements.txt

frontend-install:
	cd frontend && npm install

seed:
	cd backend && python scripts/seed_usage_data.py

refresh:
	cd backend && python scripts/refresh_rollups.py

api:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

test:
	cd backend && pytest
