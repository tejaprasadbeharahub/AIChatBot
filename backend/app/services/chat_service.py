from app.ai.chains.chat_chain import generate_reply
from app.ai.llm import DEFAULT_MODEL
from app.core.config import settings
from app.schemas.chat import ChatRequest, ChatResponse


def create_chat_response(request: ChatRequest) -> ChatResponse:
    reply = generate_reply(request)
    return ChatResponse(reply=reply, model=settings.llm_model or DEFAULT_MODEL)
