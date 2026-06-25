from typing import AsyncGenerator
from openai import AsyncOpenAI
from core.config import settings
import logging
logger = logging.getLogger("services.llm_service")

OPENROUTER_MODEL_MAP = {
    "gemini-1.5-flash": "moonshotai/kimi-k2.6",
    "claude-sonnet": "anthropic/claude-3.5-sonnet",
    "claude-haiku": "anthropic/claude-3-haiku",
}

class LLMService:
    def __init__(self):
        self.openrouter_client = None
        self.groq_client = None

        if settings.OPENROUTER_API_KEY:
            self.openrouter_client = AsyncOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=settings.OPENROUTER_API_KEY,
            )
            logger.info("[LLMService] Initialized OpenRouter client.")

        if settings.GROQ_API_KEY:
            self.groq_client = AsyncOpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=settings.GROQ_API_KEY,
            )
            logger.info("[LLMService] Initialized Groq client.")

    async def stream_chat_response(self, system_prompt: str, prompt: str) -> AsyncGenerator[str, None]:
        # Try OpenRouter first if configured
        if self.openrouter_client:
            try:
                response = await self.openrouter_client.chat.completions.create(
                    model="moonshotai/kimi-k2.6",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1024,
                    temperature=0.3,
                    stream=True
                )
                async for chunk in response:
                    token = chunk.choices[0].delta.content
                    if token:
                        yield token
                return
            except Exception as e:
                logger.info(f"[LLMService] OpenRouter streaming error: {e}")
                if not self.groq_client:
                    raise

        # Fallback to Groq
        if self.groq_client:
            logger.info("[LLMService] Falling back to Groq for streaming chat...")
            response = await self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1024,
                temperature=0.3,
                stream=True
            )
            async for chunk in response:
                token = chunk.choices[0].delta.content
                if token:
                    yield token
            return

        raise RuntimeError("No LLM provider configured or all calls failed.")

    async def generate_completion(
        self,
        system_prompt: str,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 4096,
        model_override: str | None = None,
    ) -> str:
        # Try OpenRouter first if configured
        if self.openrouter_client:
            try:
                actual_model = OPENROUTER_MODEL_MAP.get(model_override or "", "moonshotai/kimi-k2.6")
                response = await self.openrouter_client.chat.completions.create(
                    model=actual_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content or ""
            except Exception as e:
                logger.info(f"[LLMService] OpenRouter completion error: {e}")
                if not self.groq_client:
                    raise

        # Fallback to Groq
        if self.groq_client:
            logger.info("[LLMService] Falling back to Groq for completion...")
            response = await self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"} if "json" in system_prompt.lower() or "json" in prompt.lower() else None
            )
            return response.choices[0].message.content or ""

        raise RuntimeError("No LLM provider configured or all calls failed.")
