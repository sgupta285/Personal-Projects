.PHONY: backend frontend test seed

backend:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm install && npm run dev

test:
	cd backend && PYTHONPATH=. python -m unittest discover -s tests -v

seed:
	cd backend && python scripts/seed_demo.py
