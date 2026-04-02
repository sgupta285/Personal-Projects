from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.models import LoginRequest, TokenResponse
from app.security.auth import authenticate_user, create_access_token, get_user_by_username
from app.security.totp import totp

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=TokenResponse)
def token(payload: LoginRequest) -> TokenResponse:
    user = authenticate_user(payload.username, payload.password, payload.mfa_code)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials or missing mfa")
    return TokenResponse(
        access_token=create_access_token(user),
        expires_in_seconds=30 * 60,
    )


@router.get("/mfa-demo/{username}")
def mfa_demo(username: str) -> dict[str, str]:
    row = get_user_by_username(username)
    if not row:
        raise HTTPException(status_code=404, detail="user not found")
    return {"username": username, "demo_totp_code": totp(row["mfa_secret"])}
