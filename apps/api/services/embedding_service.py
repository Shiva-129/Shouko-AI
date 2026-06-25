from openai import AsyncOpenAI
from core.config import settings
import logging
logger = logging.getLogger("services.embedding_service")

EMBEDDING_MODEL = "nvidia/llama-nemotron-embed-vl-1b-v2:free"

class EmbeddingService:
    def __init__(self):
        self.client = None
        if settings.OPENROUTER_API_KEY:
            self.client = AsyncOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=settings.OPENROUTER_API_KEY,
            )
        else:
            logger.info("[EmbeddingService] WARNING: Embedding Service is not configured with a valid API key.")

    async def get_embeddings(self, texts: list[str], input_type: str = "passage") -> list[list[float]]:
        if not self.client:
            raise RuntimeError("Embedding Service is not configured. Please set a valid OPENROUTER_API_KEY.")

        response = await self.client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts,
            encoding_format="float",
            extra_body={"input_type": input_type}
        )
        return [data.embedding for data in response.data]
