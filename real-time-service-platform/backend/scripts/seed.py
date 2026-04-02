from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.security import hash_password
from app.db.database import Base, SessionLocal, engine
from app.db.models import User

Base.metadata.create_all(bind=engine)

db = SessionLocal()
users = [
    ("admin", "Platform Admin", "admin", "adminpass"),
    ("operator", "Default Operator", "operator", "operatorpass"),
]
for username, full_name, role, password in users:
    if not db.query(User).filter(User.username == username).first():
        db.add(User(username=username, full_name=full_name, role=role, hashed_password=hash_password(password)))
db.commit()
print("Seed complete. Users: admin/adminpass, operator/operatorpass")
