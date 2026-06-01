import fitz  # PyMuPDF
import os

class PDFService:
    @staticmethod
    def extract_text_by_page(file_path: str) -> list[dict]:
        """
        Extracts text from each page of a PDF using PyMuPDF.
        Returns a list of dicts: [{"page_number": int, "text": str}]
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found at path: {file_path}")

        pages = []
        doc = fitz.open(file_path)
        for page_idx, page in enumerate(doc):
            text = page.get_text()
            pages.append({
                "page_number": page_idx + 1,
                "text": text
            })
        doc.close()
        return pages

    @staticmethod
    def chunk_text(pages: list[dict], chunk_size: int = 512, overlap: int = 50) -> list[dict]:
        """
        Chunks the page texts into overlaps of `chunk_size` words with an `overlap` of words.
        Attaches the page number, section metadata, and sequence chunk_index.
        """
        all_words = []
        for p in pages:
            words = p["text"].split()
            for w in words:
                all_words.append({
                    "word": w,
                    "page_number": p["page_number"]
                })

        chunks = []
        idx = 0
        chunk_idx = 0
        total_words = len(all_words)

        if total_words == 0:
            return []

        while idx < total_words:
            end_idx = min(idx + chunk_size, total_words)
            chunk_slice = all_words[idx:end_idx]
            
            # Reconstruct string content
            content = " ".join([item["word"] for item in chunk_slice])
            
            # Determine pages spanned by this chunk
            chunk_pages = list(set([item["page_number"] for item in chunk_slice]))
            primary_page = chunk_pages[0] if chunk_pages else 1
            
            # Simple section-header detection heuristic
            section = "body"
            lower_content = content.lower()
            if "abstract" in lower_content[:150]:
                section = "abstract"
            elif "introduction" in lower_content[:150]:
                section = "introduction"
            elif "references" in lower_content or "bibliography" in lower_content:
                section = "references"
            elif "methods" in lower_content[:150] or "methodology" in lower_content[:150]:
                section = "methods"
            
            chunks.append({
                "content": content,
                "chunk_index": chunk_idx,
                "page_number": primary_page,
                "section": section,
                "token_count": len(chunk_slice)  # Approximation using word count
            })
            
            chunk_idx += 1
            # Slide window forward by step size
            step = chunk_size - overlap
            if step <= 0:
                step = 1  # Guard against infinite loop
            idx += step
            
        return chunks
