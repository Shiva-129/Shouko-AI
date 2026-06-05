import hashlib
from openai import AsyncOpenAI
from core.config import settings

EMBEDDING_DIM = 2048
EMBEDDING_MODEL = "nvidia/llama-nemotron-embed-vl-1b-v2"

class EmbeddingService:
    def __init__(self):
        self.client = None
        if settings.OPENROUTER_API_KEY and settings.OPENROUTER_API_KEY != "mock-key-for-now":
            self.client = AsyncOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=settings.OPENROUTER_API_KEY,
            )

    async def get_embeddings(self, texts: list[str]) -> list[list[float]]:
        if self.client:
            try:
                response = await self.client.embeddings.create(
                    model=EMBEDDING_MODEL,
                    input=texts
                )
                return [data.embedding for data in response.data]
            except Exception as e:
                print(f"[EmbeddingService] OpenRouter embedding error: {e}. Falling back to mock vectors.")

        return [self._generate_mock_vector(text) for text in texts]

    def _generate_mock_vector(self, text: str) -> list[float]:
        hasher = hashlib.sha256(text.encode("utf-8"))
        digest = hasher.digest()

        vector = []
        for i in range(EMBEDDING_DIM):
            val = (digest[i % 32] * (i + 1) + 17) % 256
            float_val = (val / 128.0) - 1.0
            vector.append(float_val)

        magnitude = sum(x * x for x in vector) ** 0.5
        if magnitude > 0:
            vector = [x / magnitude for x in vector]

        return vector
