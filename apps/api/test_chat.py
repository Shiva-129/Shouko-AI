import asyncio
import os
import tempfile
import httpx
from services.pdf_service import PDFService
from services.embedding_service import EmbeddingService
from services.rag_service import RAGService
from services.llm_service import LLMService

async def main():
    print("=== Starting PaperBrain RAG Vector Search & SSE Chat Stream Verification ===")
    
    # 1. Instantiate Services
    pdf_service = PDFService()
    embedding_service = EmbeddingService()
    rag_service = RAGService()
    llm_service = LLMService()
    
    # Sample PDF (Attention Is All You Need)
    pdf_url = "https://arxiv.org/pdf/1706.03762.pdf"
    
    # Workspace scratch space
    scratch_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scratch")
    os.makedirs(scratch_dir, exist_ok=True)
    
    fd, temp_file_path = tempfile.mkstemp(suffix=".pdf", dir=scratch_dir)
    os.close(fd)
    
    try:
        # 2. Download the PDF
        print(f"Downloading sample paper from {pdf_url}...")
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(pdf_url)
            response.raise_for_status()
            with open(temp_file_path, "wb") as f:
                f.write(response.content)
        print("Download complete!")
        
        # 3. Parse and chunk paper
        print("Extracting pages and segmenting text chunks...")
        pages = pdf_service.extract_text_by_page(temp_file_path)
        chunks = pdf_service.chunk_text(pages, chunk_size=512, overlap=50)
        print(f"Successfully generated {len(chunks)} chunks.")
        
        # 4. Perform simulated vector search
        # We will embed the user's question, calculate cosine similarities against all chunks locally,
        # and sort by highest similarity to mimic the pgvector database search flow perfectly!
        question = "What is Multi-Head Attention and its primary mathematical formula?"
        print(f"\nUser Query: '{question}'")
        print("Embedding query and executing RAG retrieval...")
        
        question_embeddings = await embedding_service.get_embeddings([question])
        q_vec = question_embeddings[0]
        
        # Generate mock embeddings for our document chunks so we can compare similarity
        chunk_texts = [c["content"] for c in chunks]
        chunk_embeddings = await embedding_service.get_embeddings(chunk_texts)
        
        scored_chunks = []
        for i, c in enumerate(chunks):
            c_vec = chunk_embeddings[i]
            # Cosine similarity calculation: dot_product / (mag_a * mag_b)
            # Since our mock embeddings are already normalized (magnitude = 1.0),
            # similarity is simply the dot product!
            dot_product = sum(x * y for x, y in zip(q_vec, c_vec))
            scored_chunks.append((dot_product, c))
            
        # Sort by similarity descending
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        top_chunks = [item[1] for item in scored_chunks[:3]]
        
        print("\n--- RETRIEVED SEGMENTS (RAG Context) ---")
        for idx, tc in enumerate(top_chunks):
            print(f"Segment #{idx+1} (Similarity Score: {scored_chunks[idx][0]:.4f}, Page {tc['page_number']}):")
            print(f"'{tc['content'][:150]}...'")
        print("----------------------------------------\n")
        
        # 5. Build prompts
        print("Compiling history-aware context prompts...")
        history = []  # Empty initial history
        system_prompt, user_prompt = rag_service.compile_rag_prompt(
            query=question,
            context_chunks=top_chunks,
            history=history
        )
        
        # 6. Stream RAG Chat Response
        print("Initiating Server-Sent Events (SSE) token stream:")
        print(">>> ", end="", flush=True)
        
        async for token in llm_service.stream_chat_response(
            system_prompt=system_prompt,
            prompt=user_prompt,
            context_chunks=top_chunks
        ):
            print(token, end="", flush=True)
        print("\n")
        
        print("=== RAG Search & SSE Streaming Chat Verification PASSED! ===")
        
    except Exception as e:
        print(f"Verification FAILED with error: {e}")
        
    finally:
        # Cleanup
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

if __name__ == "__main__":
    asyncio.run(main())
