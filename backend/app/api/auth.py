from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth.jwt import create_access_token
from app.db.session import get_db
from app.repositories.user_repo import create_user, get_user_by_email, verify_password
from app.schemas.user import RegisterResponse, Token, UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> RegisterResponse:
    try:
        email = payload.email.lower().strip()
        if not email.endswith("@amzur.com"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Use your @amzur.com email")

        existing = get_user_by_email(db, email=email)
        if existing is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

        user = create_user(db, email=email, password=payload.password)
        token = Token(access_token=create_access_token(subject=user.email), token_type="bearer")
        return RegisterResponse(user=UserRead.model_validate(user), token=token)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable") from exc


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    """Authenticate an Amzur employee and return a JWT access token."""
    try:
        user = get_user_by_email(db, email=form_data.username.lower().strip())
        if user is None or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")

        access_token = create_access_token(subject=user.email)
        return Token(access_token=access_token, token_type="bearer")
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable") from exc
