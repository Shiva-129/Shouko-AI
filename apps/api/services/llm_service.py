import asyncio
import json
from typing import AsyncGenerator
from openai import AsyncOpenAI
from core.config import settings

OPENROUTER_MODEL_MAP = {
    "gemini-1.5-flash": "moonshotai/kimi-k2.6",
    "claude-sonnet": "anthropic/claude-3.5-sonnet",
    "claude-haiku": "anthropic/claude-3-haiku",
}

class LLMService:
    def __init__(self):
        self.provider = None
        self.client = None
        self.model = None

        openrouter_key = settings.OPENROUTER_API_KEY
        if openrouter_key and openrouter_key != "mock-key-for-now":
            self.provider = "openrouter"
            self.client = AsyncOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=openrouter_key,
            )
            self.model = "moonshotai/kimi-k2.6"
            print("[LLMService] Initialized OpenRouter API Provider.")
            return

        print("[LLMService] Running in sandbox mode. Deterministic mock generator enabled.")

    async def stream_chat_response(self, system_prompt: str, prompt: str, context_chunks: list[dict]) -> AsyncGenerator[str, None]:
        if self.client and self.provider == "openrouter":
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
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
                print(f"[LLMService] OpenRouter streaming error: {e}. Falling back to mock generator.")

        async for token in self._generate_mock_rag_stream(prompt, context_chunks):
            yield token

    async def _generate_mock_rag_stream(self, prompt: str, context_chunks: list[dict]) -> AsyncGenerator[str, None]:
        snippets = []
        for i, c in enumerate(context_chunks[:2]):
            content_preview = c.get("content", "")
            sentences = [s.strip() + "." for s in content_preview.split(".") if len(s.strip()) > 10]
            snippets.append(" ".join(sentences[:2]))

        context_summary = " ".join(snippets) if snippets else "No context loaded."

        response = (
            f"Based on the ingested paper content: '{context_summary[:350]}...', "
            f"here is a technical breakdown relating to your query: '{prompt[:60]}...'\n\n"
            "1. Self-Attention Mechanisms rely on projecting queries, keys, and values to attend across token sequences without recurrence.\n"
            "2. By mapping relationships in a single operation, computing time decreases significantly and parallelization scales across modern GPU compute platforms.\n\n"
            "This synthesized response was streamed directly from the local RAG simulation engine."
        )

        words = response.split(" ")
        for w in words:
            yield w + " "
            await asyncio.sleep(0.04)

    async def generate_completion(
        self,
        system_prompt: str,
        prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 4096,
        model_override: str | None = None,
    ) -> str:
        actual_model = OPENROUTER_MODEL_MAP.get(model_override or "", self.model)

        if self.client and self.provider == "openrouter":
            try:
                response = await self.client.chat.completions.create(
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
                print(f"[LLMService] OpenRouter completion error: {e}")

        print("[LLMService] No LLM configured or call failed, using mock completion.")
        if "artifact" in system_prompt.lower() or "artifact_generation" in prompt.lower():
            return json.dumps({
                "one_line_summary": "A mock overview of the research paper highlighting key findings.",
                "summary": "This is a detailed mock summary of the paper's contribution, methodology, and results.",
                "key_insights": [
                    {"insight": "Mock insight 1 from introduction.", "importance_score": 8, "section": "introduction"},
                    {"insight": "Mock insight 2 on methodology.", "importance_score": 9, "section": "methods"},
                    {"insight": "Mock insight 3 on results.", "importance_score": 7, "section": "results"},
                ],
                "auto_qa": [
                    {"question": "What is the primary contribution?", "answer": "A simulated framework.", "difficulty": "EASY"},
                    {"question": "How does scaling behave?", "answer": "Logarithmically.", "difficulty": "MEDIUM"},
                ],
                "suggested_experiments": [
                    {"title": "Parameter tuning", "description": "Run grid search on learning rate.", "feasibility": "MEDIUM"},
                ],
            })
        return json.dumps([
            {"paper_id": "mock-1", "score": 75, "reason": "Sample scoring (mock mode)"}
        ])
