from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    full_name: str
    password: str
    role: str = "operator"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
