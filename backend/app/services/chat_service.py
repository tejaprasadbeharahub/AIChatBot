from app.ai.chains.chat_chain import generate_reply
from app.ai.llm import resolve_model_name
from app.schemas.chat import ChatRequest, ChatResponse


def create_chat_response(request: ChatRequest) -> ChatResponse:
    reply = generate_reply(request)
    return ChatResponse(reply=reply, model=resolve_model_name())
