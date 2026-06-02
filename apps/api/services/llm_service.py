import asyncio
import json
from typing import AsyncGenerator
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from core.config import settings

class LLMService:
    def __init__(self):
        self.provider = None
        self.client = None
        self.model = None

        # 1. Prioritize Gemini API Key
        gemini_key = settings.GEMINI_API_KEY
        if gemini_key and gemini_key != "mock-key-for-now":
            self.provider = "gemini"
            self.client = AsyncOpenAI(
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
                api_key=gemini_key
            )
            self.model = "gemini-1.5-flash"
            print("[LLMService] Initialized Google Gemini API Provider via OpenAI compatibility layer.")
            return

        # 2. Fallback to OpenRouter API Key
        openrouter_key = settings.OPENROUTER_API_KEY
        if openrouter_key and openrouter_key != "mock-key-for-now":
            self.provider = "openrouter"
            self.client = AsyncOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=openrouter_key
            )
            self.model = "openrouter/auto"
            print("[LLMService] Initialized OpenRouter API Provider with openrouter/auto.")
            return

        # 3. Fallback to Anthropic API Key
        anthropic_key = settings.ANTHROPIC_API_KEY
        if anthropic_key and anthropic_key != "mock-key-for-now":
            self.provider = "anthropic"
            self.client = AsyncAnthropic(api_key=anthropic_key)
            self.model = "claude-3-5-sonnet-20241022"
            print("[LLMService] Initialized Anthropic Claude API Provider.")
            return

        print("[LLMService] Running in sandbox mode. Deterministic mock generator enabled.")

    async def stream_chat_response(self, system_prompt: str, prompt: str, context_chunks: list[dict]) -> AsyncGenerator[str, None]:
        """
        Streams a chat response token-by-token using the active provider.
        Falls back to a context-aware mock generator if no keys are configured.
        """
        if self.client and self.provider in ("gemini", "openrouter"):
            try:
                # Call OpenAI-compatible chat completion stream
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
                print(f"[LLMService] {self.provider.upper()} API streaming error: {e}. Falling back to mock generator.")

        elif self.client and self.provider == "anthropic":
            try:
                async with self.client.messages.stream(
                    model=self.model,
                    max_tokens=1024,
                    temperature=0.3,
                    system=system_prompt,
                    messages=[{"role": "user", "content": prompt}]
                ) as stream:
                    async for text in stream.text_stream:
                        yield text
                return
            except Exception as e:
                print(f"[LLMService] Anthropic API streaming error: {e}. Falling back to mock generator.")

        # Context-aware mock RAG stream generator
        async for token in self._generate_mock_rag_stream(prompt, context_chunks):
            yield token

    async def _generate_mock_rag_stream(self, prompt: str, context_chunks: list[dict]) -> AsyncGenerator[str, None]:
        """
        Generates a token-by-token simulated response, incorporating the actual parsed
        text contents of the retrieved database chunks for high-fidelity offline verification.
        """
        snippets = []
        for i, c in enumerate(context_chunks[:2]):
            content_preview = c.get("content", "")
            # Grab first 2 sentences
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
        if self.client and self.provider in ("gemini", "openrouter"):
            try:
                response = await self.client.chat.completions.create(
                    model=model_override or self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content or ""
            except Exception as e:
                print(f"[LLMService] {self.provider.upper()} completion error: {e}")

        elif self.client and self.provider == "anthropic":
            try:
                response = await self.client.messages.create(
                    model=model_override or self.model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    system=system_prompt,
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.content[0].text
            except Exception as e:
                print(f"[LLMService] Anthropic completion error: {e}")

        print("[LLMService] No LLM configured, using mock completion.")
        return json.dumps([
            {"paper_id": "mock-1", "score": 75, "reason": "Sample scoring (mock mode)"}
        ])
