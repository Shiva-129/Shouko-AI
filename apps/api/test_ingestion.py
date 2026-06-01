import asyncio
import os
import tempfile
import httpx
from services.pdf_service import PDFService
from services.embedding_service import EmbeddingService

async def main():
    print("=== Starting PaperBrain Ingestion Logic Verification ===")
    
    # 1. Instantiate Services
    pdf_service = PDFService()
    embedding_service = EmbeddingService()
    
    # 2. Sample PDF URL (Attention Is All You Need)
    pdf_url = "https://arxiv.org/pdf/1706.03762.pdf"
    
    # Create scratch space if not exists
    scratch_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scratch")
    os.makedirs(scratch_dir, exist_ok=True)
    
    fd, temp_file_path = tempfile.mkstemp(suffix=".pdf", dir=scratch_dir)
    os.close(fd)
    
    try:
        # 3. Download the PDF
        print(f"Downloading sample PDF from {pdf_url}...")
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(pdf_url)
            response.raise_for_status()
            with open(temp_file_path, "wb") as f:
                f.write(response.content)
        print("Download complete!")
        
        # 4. Extract Text Pages
        print("Extracting text pages using PyMuPDF...")
        pages = pdf_service.extract_text_by_page(temp_file_path)
        print(f"Successfully extracted {len(pages)} pages.")
        
        # 5. Chunk the Pages
        print("Chunking extracted text (sliding-window: 512 words size, 50 overlap)...")
        chunks = pdf_service.chunk_text(pages, chunk_size=512, overlap=50)
        print(f"Generated {len(chunks)} text chunks.")
        
        # Print information of the first chunk
        if chunks:
            first = chunks[0]
            print("\n--- SAMPLE CHUNK #1 ---")
            print(f"Chunk Index: {first['chunk_index']}")
            print(f"Page Number: {first['page_number']}")
            print(f"Assigned Section: {first['section']}")
            print(f"Word/Token Count: {first['token_count']}")
            print(f"Preview (first 250 characters):\n{first['content'][:250]}...")
            print("----------------------\n")
            
        # 6. Generate Vector Embeddings
        print("Generating 1536-dimensional embeddings...")
        test_texts = [c["content"] for c in chunks[:3]]
        embeddings = await embedding_service.get_embeddings(test_texts)
        print(f"Generated {len(embeddings)} embeddings successfully.")
        
        if embeddings:
            first_vector = embeddings[0]
            print("\n--- VECTOR EMBEDDING PREVIEW ---")
            print(f"Dimensions: {len(first_vector)}")
            print(f"First 5 dimensions: {first_vector[:5]}")
            print(f"Vector Magnitude: {sum(x*x for x in first_vector)**0.5:.4f} (Normalized = 1.0)")
            print("--------------------------------\n")
            
        print("=== Ingestion Logic Verification PASSED successfully! ===")
        
    except Exception as e:
        print(f"Verification FAILED with error: {e}")
        
    finally:
        # Cleanup
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

if __name__ == "__main__":
    asyncio.run(main())
