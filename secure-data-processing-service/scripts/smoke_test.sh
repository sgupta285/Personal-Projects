#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
USERNAME="${USERNAME:-admin}"
PASSWORD="${PASSWORD:-ChangeMe123!}"

MFA_CODE=$(curl -s "$BASE_URL/auth/mfa-demo/$USERNAME" | python -c 'import json,sys; print(json.load(sys.stdin)["demo_totp_code"])')
TOKEN=$(curl -s -X POST "$BASE_URL/auth/token" -H "Content-Type: application/json" -d "{"username": "$USERNAME", "password": "$PASSWORD", "mfa_code": "$MFA_CODE"}" | python -c 'import json,sys; print(json.load(sys.stdin)["access_token"])')

curl -s -X POST "$BASE_URL/records"   -H "Authorization: Bearer $TOKEN"   -H "Content-Type: application/json"   -d '{"subject_id":"SMOKE-001","org_id":"north","classification":"restricted","region":"midwest","department":"finance","payload":{"name":"Smoke User","email":"smoke@example.com","record_type":"payment","status":"open","priority":"high","notes":"smoke"}}'   | tee /tmp/secure_service_record.json

RECORD_ID=$(python -c 'import json; print(json.load(open("/tmp/secure_service_record.json"))["record_id"])')
curl -s "$BASE_URL/records/$RECORD_ID" -H "Authorization: Bearer $TOKEN"
curl -s "$BASE_URL/audit/verify" -H "Authorization: Bearer $TOKEN"
