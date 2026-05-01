import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.chat_repo import get_chat_by_id, get_chats_for_user
from app.repositories.message_repo import get_messages_for_chat
from app.schemas.chat import ChatRead
from app.schemas.message import MessageRead

router = APIRouter(prefix="/chats", tags=["chats"])


@router.get("", response_model=list[ChatRead])
def list_chats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ChatRead]:
    """Return all chats belonging to the authenticated user."""
    return get_chats_for_user(db, user_id=current_user.id)  # type: ignore[return-value]


@router.get("/{chat_id}/messages", response_model=list[MessageRead])
def list_messages(
    chat_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MessageRead]:
    """Return all messages for a specific chat (must belong to the current user)."""
    chat = get_chat_by_id(db, chat_id=chat_id)
    if chat is None or chat.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    return get_messages_for_chat(db, chat_id=chat_id)  # type: ignore[return-value]
