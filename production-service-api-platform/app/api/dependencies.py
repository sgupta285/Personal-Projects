import uuid
from dataclasses import dataclass
from jose import JWTError, jwt
from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.db import get_db
from app.models import ApiClient
from app.services.rate_limit import limiter
from app.services.tokens import verify_api_key


@dataclass
class AuthContext:
    client_id: str
    scopes: list[str]
    token_type: str
    rate_limit_per_minute: int
    daily_quota: int


def _error(code: str, message: str, status_code: int = status.HTTP_401_UNAUTHORIZED) -> HTTPException:
    return HTTPException(status_code=status_code, detail={'code': code, 'message': message})


def get_request_id(request: Request) -> str:
    request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
    request.state.request_id = request_id
    return request_id


def require_auth(
    request: Request,
    db: Session = Depends(get_db),
    x_api_key: str | None = Header(default=None, alias='X-API-Key'),
    authorization: str | None = Header(default=None),
) -> AuthContext:
    settings = get_settings()
    context = None

    if x_api_key:
        clients = db.query(ApiClient).filter(ApiClient.api_key_hash.is_not(None)).all()
        matched = None
        for client in clients:
            if verify_api_key(x_api_key, client.api_key_hash):
                matched = client
                break
        if matched and matched.is_active:
            context = AuthContext(
                client_id=matched.client_id,
                scopes=matched.scopes.split(),
                token_type='api_key',
                rate_limit_per_minute=matched.rate_limit_per_minute,
                daily_quota=matched.daily_quota,
            )

    elif authorization and authorization.lower().startswith('bearer '):
        token = authorization.split(' ', 1)[1]
        try:
            payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        except JWTError as exc:
            raise _error('invalid_token', 'Bearer token could not be verified') from exc
        scopes = (payload.get('scope') or '').split()
        context = AuthContext(
            client_id=payload.get('sub', 'unknown'),
            scopes=scopes,
            token_type=payload.get('token_type', 'oauth'),
            rate_limit_per_minute=settings.default_rate_limit_per_minute,
            daily_quota=settings.default_daily_quota,
        )

    if context is None:
        raise _error('authentication_required', 'Provide X-API-Key or a valid Bearer token')

    limiter.enforce(context.client_id, context.rate_limit_per_minute, context.daily_quota)
    request.state.auth = context
    return context


def require_scope(scope: str):
    def dependency(context: AuthContext = Depends(require_auth)) -> AuthContext:
        if scope not in context.scopes:
            raise _error('forbidden', f'Missing required scope: {scope}', status.HTTP_403_FORBIDDEN)
        return context

    return dependency
