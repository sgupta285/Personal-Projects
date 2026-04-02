from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.security import RoleChecker, get_current_user
from app.db.database import get_db

DbSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[object, Depends(get_current_user)]
AdminUser = Annotated[object, Depends(RoleChecker("admin"))]
