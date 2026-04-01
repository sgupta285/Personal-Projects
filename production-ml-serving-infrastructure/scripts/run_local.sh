#!/usr/bin/env bash
set -euo pipefail
cp -n .env.example .env || true
python scripts/train_model.py
python scripts/seed_feature_store.py
uvicorn app.main:app --reload
