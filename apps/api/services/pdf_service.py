import fitz  # PyMuPDF
import os
import re
import logging
logger = logging.getLogger("services.pdf_service")

MAX_PAGES = 200


def _detect_section(text: str) -> str:
    """Detect section header using word-boundary matching on the first 200 chars."""
    prefix = text[:200].lower()
    patterns = {
        "abstract": r'\babstract\b',
        "introduction": r'\bintroduction\b',
        "references": r'\b(?:references|bibliography)\b',
        "methods": r'\b(?:methods?|methodology)\b',
    }
    for section, pattern in patterns.items():
        if re.search(pattern, prefix):
            return section
    return "body"


class PDFService:
    @staticmethod
    def extract_text_by_page(file_path: str) -> list[dict]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found at path: {file_path}")
        doc = fitz.open(file_path)
        if doc.page_count > MAX_PAGES:
            doc.close()
            raise ValueError(f"PDF has {doc.page_count} pages (max {MAX_PAGES}). Refusing to process.")
        pages = []
        for page_idx, page in enumerate(doc):
            text = page.get_text()
            if page_idx == 0 and len(text.strip()) < 20:
                logger.info(f"[PDFService] Warning: page 1 has only {len(text.strip())} characters — scanned PDF likely")
            pages.append({
                "page_number": page_idx + 1,
                "text": text
            })
        doc.close()
        return pages

    @staticmethod
    def chunk_text(pages: list[dict], chunk_size: int = 512, overlap: int = 50) -> list[dict]:
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
        step = max(chunk_size - overlap, 1)
        while idx < total_words:
            end_idx = min(idx + chunk_size, total_words)
            raw_slice = all_words[idx:end_idx]
            content = " ".join(item["word"] for item in raw_slice)
            # Try to break at a sentence boundary within the last 30% of the chunk
            if end_idx < total_words:
                cut_candidates = [m.start() for m in re.finditer(r'\. (?=[A-Z])', content)]
                if cut_candidates and cut_candidates[-1] > len(content) * 0.7:
                    boundary = cut_candidates[-1] + 2  # after ". "
                    content = content[:boundary]
            chunk_pages = list(set(item["page_number"] for item in raw_slice))
            primary_page = chunk_pages[0] if chunk_pages else 1
            section = _detect_section(content)
            chunks.append({
                "content": content,
                "chunk_index": chunk_idx,
                "page_number": primary_page,
                "section": section,
                "token_count": len(raw_slice),
            })
            chunk_idx += 1
            idx += step
        return chunks
