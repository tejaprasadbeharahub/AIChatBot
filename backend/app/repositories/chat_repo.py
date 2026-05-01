import uuid

from sqlalchemy.orm import Session

from app.models.chat import Chat


def get_chats_for_user(db: Session, user_id: uuid.UUID) -> list[Chat]:
    return (
        db.query(Chat)
        .filter(Chat.user_id == user_id)
        .order_by(Chat.created_at.desc())
        .all()
    )


def get_chat_by_id(db: Session, chat_id: uuid.UUID) -> Chat | None:
    return db.query(Chat).filter(Chat.id == chat_id).first()


def get_chat_for_user(db: Session, chat_id: uuid.UUID, user_id: uuid.UUID) -> Chat | None:
    return db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user_id).first()


def create_chat(db: Session, user_id: uuid.UUID, title: str | None = None) -> Chat:
    chat = Chat(user_id=user_id, title=title)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat
