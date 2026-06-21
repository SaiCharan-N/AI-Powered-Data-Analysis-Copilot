import logging

from langchain_groq import ChatGroq

from app.config import settings

logger = logging.getLogger(__name__)


class LLMConfigurationError(RuntimeError):
    """Raised when the LLM provider is not configured."""


def is_groq_configured() -> bool:
    return bool(settings.groq_api_key)


def get_groq_llm() -> ChatGroq:
    if not settings.groq_api_key:
        logger.error("GROQ_API_KEY is not configured.")
        raise LLMConfigurationError("GROQ_API_KEY is not configured.")

    return ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.groq_model,
        temperature=0,
    )
