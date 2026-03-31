.PHONY: test smoke seed backend

test:
	cd backend && python -m unittest discover -s tests -v

smoke:
	python scripts/smoke_test.py

seed:
	cd backend && python seed.py

backend:
	cd backend && uvicorn app.main:app --reload --port 8000
