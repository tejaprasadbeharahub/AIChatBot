import uuid
import hashlib
import hmac
import secrets

from sqlalchemy.orm import Session

from app.models.user import User

_PBKDF2_ROUNDS = 390000


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, email: str, password: str) -> User:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), _PBKDF2_ROUNDS)
    hashed = f"pbkdf2_sha256${_PBKDF2_ROUNDS}${salt}${digest.hex()}"
    user = User(email=email, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        algorithm, rounds_str, salt, digest_hex = hashed_password.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        rounds = int(rounds_str)
        computed = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt.encode("utf-8"),
            rounds,
        ).hex()
        return hmac.compare_digest(computed, digest_hex)
    except Exception:
        return False
