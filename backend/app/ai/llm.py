from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings


DEFAULT_MODEL = "gemini-2.0-flash"


def get_chat_model(temperature: float = 0.2) -> ChatGoogleGenerativeAI:
	api_key = settings.gemini_api_key or settings.litellm_api_key
	if not api_key:
		raise ValueError("Missing Gemini API key. Set GEMINI_API_KEY in .env")

	model_name = settings.llm_model or DEFAULT_MODEL
	return ChatGoogleGenerativeAI(
		model=model_name,
		google_api_key=api_key,
		temperature=temperature,
	)
