# PaperBrain — AI Architecture

> All prompts, agent designs, RAG setup, cost optimization, and evaluation strategy.

---

## Model Selection

| Task | Model | Max Tokens | Reason |
|---|---|---|---|
| Artifact generation | claude-sonnet-4-20250514 | 2000 | Quality matters, complex structured output |
| RAG Q&A (chat) | claude-sonnet-4-20250514 | 1000 | Reasoning quality for user-facing answers |
| Relevance scoring | claude-haiku-4-5-20251001 | 300 | Runs on 100s of papers/day, cheap |
| Section classification | claude-haiku-4-5-20251001 | 100 | Simple classification |
| Embeddings | text-embedding-3-small | — | 1536 dims, $0.02/1M tokens |

**Never use Sonnet for batch classification tasks. Never use Haiku for artifact generation.**

---

## Prompt Registry

All prompts are versioned in `apps/api/prompts/`. Never hardcode prompts in router or service files.

Each prompt file exports:
- `SYSTEM_PROMPT` — the system message
- `build_user_prompt(...)` — function that constructs the user message
- `PROMPT_VERSION` — increment when changing prompts
- `OUTPUT_SCHEMA` — Pydantic model the output must conform to

---

## Prompt Designs

### 1. Discovery Agent Prompt (`prompts/discovery.py`)

```python
PROMPT_VERSION = "1.0"

SYSTEM_PROMPT = """
You are a research relevance scoring agent for an AI researcher.
Your job: evaluate academic papers and score how relevant they are to the researcher's interests.

RULES:
- Output ONLY valid JSON, no preamble, no explanation
- Score 0-100 (only recommend if score >= 70)
- Be strict — the researcher is busy, only surface truly relevant papers
- relevance_reasons should be specific, not generic ("uses transformer architecture" not "interesting paper")
"""

def build_user_prompt(papers: list[dict], interest_profile: dict) -> str:
    return f"""
Researcher interest profile:
- Topics: {', '.join(interest_profile.get('topics', []))}
- Keywords: {', '.join(interest_profile.get('keywords', []))}
- Favorite authors: {', '.join(interest_profile.get('authors', []))}
- ArXiv categories: {', '.join(interest_profile.get('categories', []))}

Papers to evaluate (batch of {len(papers)}):
{json.dumps(papers, indent=2)}

For each paper, output a JSON array:
[
  {{
    "arxiv_id": "...",
    "relevance_score": 0-100,
    "relevance_reasons": ["specific reason 1", "specific reason 2"],
    "recommended": true/false,
    "one_line_summary": "one sentence plain English description"
  }}
]
"""

class DiscoveryOutput(BaseModel):
    arxiv_id: str
    relevance_score: int = Field(ge=0, le=100)
    relevance_reasons: list[str] = Field(min_items=1, max_items=4)
    recommended: bool
    one_line_summary: str
```

---

### 2. Artifact Generation Prompt (`prompts/artifact_generation.py`)

```python
PROMPT_VERSION = "1.0"

SYSTEM_PROMPT = """
You are a research artifact generator. Your job is to transform academic paper content
into a structured, interactive knowledge artifact for a researcher.

The artifact should help the researcher:
1. Quickly understand the paper's contribution
2. Remember the key ideas months later
3. Know what experiments to run
4. Ask productive questions about the paper

RULES:
- Output ONLY valid JSON matching the schema below
- Write for a technical audience (PhD-level or senior engineer)
- Be specific, not generic — use actual numbers, method names, and findings from the paper
- key_insights should be things a researcher would highlight in a margin
- auto_qa questions should span easy comprehension to deep technical understanding
- suggested_experiments should be concrete and feasible
"""

def build_user_prompt(paper_title: str, paper_chunks: list[dict]) -> str:
    # Organize chunks by section for better context
    sections = {}
    for chunk in paper_chunks:
        section = chunk.get('section', 'other')
        if section not in sections:
            sections[section] = []
        sections[section].append(chunk['content'])

    context = ""
    for section, contents in sections.items():
        context += f"\n\n=== {section.upper()} ===\n"
        context += "\n".join(contents[:3])  # Max 3 chunks per section

    return f"""
Paper: {paper_title}

Content:
{context}

Generate a structured artifact with this exact JSON schema:
{{
  "one_line_summary": "one sentence, max 20 words, plain English",
  "summary": "300 word max plain English summary of contribution, method, and results",
  "key_insights": [
    {{
      "insight": "specific insight text",
      "importance_score": 0-100,
      "section": "which paper section this came from"
    }}
  ],
  "auto_qa": [
    {{
      "question": "question text",
      "answer": "answer text",
      "difficulty": "easy|medium|hard"
    }}
  ],
  "suggested_experiments": [
    {{
      "description": "specific experiment description",
      "feasibility": "low|medium|high",
      "expected_outcome": "what you'd expect to find"
    }}
  ]
}}

Requirements:
- 5-8 key_insights
- 10-15 auto_qa pairs (mix of easy, medium, hard)
- 3-5 suggested_experiments
- Everything grounded in the actual paper content
"""

class Insight(BaseModel):
    insight: str
    importance_score: int = Field(ge=0, le=100)
    section: str

class QAPair(BaseModel):
    question: str
    answer: str
    difficulty: Literal["easy", "medium", "hard"]

class SuggestedExperiment(BaseModel):
    description: str
    feasibility: Literal["low", "medium", "high"]
    expected_outcome: str

class ArtifactGenerationOutput(BaseModel):
    one_line_summary: str
    summary: str
    key_insights: list[Insight] = Field(min_items=3, max_items=10)
    auto_qa: list[QAPair] = Field(min_items=5, max_items=20)
    suggested_experiments: list[SuggestedExperiment] = Field(min_items=1, max_items=7)
```

---

### 3. RAG Q&A Prompt (`prompts/rag_qa.py`)

```python
PROMPT_VERSION = "1.0"

SYSTEM_PROMPT = """
You are a research assistant with deep knowledge of the paper provided in the context.
Answer questions about this paper accurately and specifically.

RULES:
- Only answer based on the provided paper context
- If the answer isn't in the context, say "I don't have enough context from this paper to answer that"
- Be specific — use exact numbers, method names, and findings from the paper
- For technical questions, provide enough depth for a senior researcher
- Cite which section your answer comes from when relevant
- Keep answers concise but complete — don't pad
"""

def build_user_prompt(
    question: str,
    chunks: list[dict],
    conversation_history: list[dict],
    paper_title: str
) -> str:
    context = "\n\n---\n\n".join([
        f"[{c['section'].upper()}, page {c.get('page_number', '?')}]\n{c['content']}"
        for c in chunks
    ])

    history = ""
    if conversation_history:
        history = "\n\nPrevious conversation:\n"
        for msg in conversation_history[-6:]:  # Last 3 turns
            history += f"{msg['role'].upper()}: {msg['content']}\n"

    return f"""
Paper: {paper_title}

Relevant paper context:
{context}
{history}

Current question: {question}
"""
```

---

## RAG Pipeline

### Full Flow

```
1. User sends question
2. Embed question → text-embedding-3-small → 1536-dim vector
3. Vector search in paper_chunks WHERE paper_id = artifact.paper_id
   → top_k = 8, cosine similarity threshold > 0.5
4. Rerank: score chunks by keyword overlap + semantic similarity → keep top 5
5. Build context: format chunks with section labels
6. Load conversation history (last 6 messages)
7. Call Claude Sonnet with streaming
8. Parse response, extract source references
9. Append to conversation history in DB
10. Stream tokens to frontend via SSE
```

### Chunking Strategy

```python
CHUNK_CONFIG = {
    "target_tokens": 512,
    "overlap_tokens": 50,
    "min_chunk_tokens": 100,    # discard tiny fragments
    "section_boundary_weight": 2.0,  # prefer splitting at section boundaries
}

SECTION_MARKERS = [
    "abstract", "introduction", "related work", "background",
    "method", "methodology", "approach", "model", "architecture",
    "experiment", "evaluation", "results", "discussion",
    "conclusion", "future work", "references", "appendix"
]
```

Always store section metadata per chunk — it makes RAG answers more precise.

### Semantic Cache

```python
# Before hitting Claude for a question:
# 1. Embed the question
# 2. Check semantic_cache table for similar query on same artifact
# 3. If cosine_similarity(cached_query_embedding, new_query_embedding) > 0.95
#    → return cached answer (skip LLM call)
# 4. Otherwise: call Claude, store result in cache

CREATE TABLE semantic_cache (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  artifact_id UUID REFERENCES artifacts(id) ON DELETE CASCADE,
  query_embedding VECTOR(1536),
  query_text TEXT,
  answer_text TEXT,
  hit_count INTEGER DEFAULT 1,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Cost Optimization

### Per-Artifact Cost Breakdown

| Operation | Model | Tokens | Cost |
|---|---|---|---|
| Chunk embeddings (100 chunks × 512 tokens) | text-embedding-3-small | ~51,200 | ~$0.001 |
| Artifact generation | claude-sonnet-4 | ~8,000 in + 2,000 out | ~$0.09 |
| **Total per artifact** | | | **~$0.09** |

### Per-Chat-Question Cost

| Operation | Tokens | Cost |
|---|---|---|
| Query embedding | 50 | ~$0.000001 |
| Context (5 chunks × 512) | ~2,560 in | |
| History (6 messages) | ~600 in | |
| Answer | ~300 out | |
| **Total per question** | ~3,460 tokens | **~$0.01** |

### Cost Control Rules

1. **Cache artifact generation** — same paper_id = never regenerate (save $0.09 per repeat)
2. **Cache embeddings** — store permanently, never re-embed same chunk
3. **Semantic cache** — similar questions = cached answers (save $0.01 per repeat)
4. **Batch embeddings** — 100 chunks per API call, not 100 separate calls
5. **Use Haiku for scoring** — 10x cheaper than Sonnet for classification
6. **Enforce limits** — free users capped at 5 artifacts/month

### Budget Alert System

```python
# Daily cost check (run at midnight)
# If daily_llm_cost > daily_revenue * 0.4 → send alert to founder Slack
# If daily_llm_cost > daily_revenue * 0.7 → auto-throttle free tier
```

---

## Guardrails

### Input Validation

```python
PROMPT_INJECTION_PATTERNS = [
    r"ignore (all |previous |above )?instructions",
    r"you are now",
    r"new system prompt",
    r"forget everything",
    r"act as",
    r"jailbreak",
    r"DAN mode",
]

def sanitize_user_input(text: str) -> str:
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            raise ValueError("Invalid input detected")
    # Strip any content that looks like XML/JSON injection
    return text.strip()[:2000]  # Hard cap on input length
```

### Output Validation

```python
# Every LLM response goes through Pydantic validation
# If validation fails → retry (up to 3 times)
# If still failing → log + return graceful error

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
async def generate_artifact_with_retry(chunks: list) -> ArtifactGenerationOutput:
    raw = await call_claude(ARTIFACT_SYSTEM_PROMPT, build_artifact_prompt(chunks))
    try:
        return ArtifactGenerationOutput.model_validate_json(raw)
    except ValidationError as e:
        logger.warning(f"Artifact validation failed: {e}, retrying...")
        raise
```

### Content Filtering

```python
# Reject uploads that are not academic papers
# Check: does abstract exist? Does it have references? Is it PDF?
# If content seems non-academic → reject with clear error message
```

---

## Evaluation Suite

Located at `apps/api/tests/evals/`.

### Gold Standard Dataset

50 papers hand-labeled by the founder with:
- Human-written summary
- 5 key insights
- 10 Q&A pairs
- Quality score per artifact (1-5)

### Automated Eval Metrics

```python
EVAL_METRICS = {
    "summary_rouge_l": 0.35,        # Minimum ROUGE-L score vs gold standard
    "insights_coverage": 0.70,      # % of gold insights covered
    "qa_accuracy": 0.75,            # LLM-as-judge accuracy on Q&A pairs
    "json_validity": 1.0,           # Must always be valid JSON
    "generation_time_s": 30,        # Max seconds for artifact generation
}
```

### Running Evals

```bash
# Full eval suite (takes ~10 min, costs ~$2 in API calls)
python tests/evals/run_evals.py --suite all

# Quick smoke test (5 papers only)
python tests/evals/run_evals.py --suite smoke

# Test specific prompt version
python tests/evals/run_evals.py --prompt-version 1.1 --compare-to 1.0
```

**Run evals before ANY prompt change is merged to main.**

### LLM-as-Judge

For Q&A accuracy, use Claude Sonnet as judge:

```python
JUDGE_PROMPT = """
You are evaluating the quality of an AI answer about a research paper.

Question: {question}
Gold answer: {gold_answer}
Generated answer: {generated_answer}

Score the generated answer 1-5:
5: Fully correct, complete, well-explained
4: Mostly correct, minor omissions
3: Partially correct, some errors
2: Mostly incorrect but some truth
1: Wrong or hallucinated

Output ONLY a JSON: {"score": N, "reason": "one sentence"}
"""
```
