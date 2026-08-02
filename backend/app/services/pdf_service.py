"""Safe text extraction and deterministic chunking for text-based PDF files."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import fitz


@dataclass(slots=True, frozen=True)
class TextChunk:
    page_number: int
    chunk_index: int
    content: str
    token_count: int


class PDFService:
    """Extract text chunks while preserving page-level citation metadata."""

    def extract_chunks(
        self,
        path: str,
        chunk_words: int = 220,
        overlap_words: int = 40,
    ) -> tuple[int, list[TextChunk]]:
        if chunk_words < 20:
            raise ValueError("chunk_words must be at least 20")
        if overlap_words < 0 or overlap_words >= chunk_words:
            raise ValueError("overlap_words must be between 0 and chunk_words - 1")

        pdf_path = Path(path).resolve()
        if not pdf_path.is_file():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        with fitz.open(pdf_path) as document:
            page_count = document.page_count
            raw_pages = [page.get_text("text") for page in document]

        cleaned_pages = self._remove_repeated_margins(raw_pages)
        chunks: list[TextChunk] = []
        chunk_index = 0
        step = chunk_words - overlap_words
        for page_index, raw_text in enumerate(cleaned_pages):
            text = self.clean_text(raw_text)
            if not text:
                continue
            words = text.split()
            for start in range(0, len(words), step):
                selected = words[start : start + chunk_words]
                # Very small tails add retrieval noise and weak citations.
                if len(selected) < 20:
                    continue
                chunks.append(
                    TextChunk(
                        page_number=page_index + 1,
                        chunk_index=chunk_index,
                        content=" ".join(selected),
                        token_count=len(selected),
                    )
                )
                chunk_index += 1
        return page_count, chunks

    @staticmethod
    def _remove_repeated_margins(pages: list[str]) -> list[str]:
        """Remove probable repeated headers/footers without altering page order."""
        if len(pages) < 3:
            return pages

        split_pages = [[line.strip() for line in page.splitlines() if line.strip()] for page in pages]
        first_lines = Counter(lines[0] for lines in split_pages if lines)
        last_lines = Counter(lines[-1] for lines in split_pages if lines)
        threshold = max(3, int(len(pages) * 0.6 + 0.5))
        repeated = {
            line
            for line, count in (*first_lines.items(), *last_lines.items())
            if count >= threshold and 2 <= len(line) <= 200
        }
        if not repeated:
            return pages
        return [
            "\n".join(line for line in lines if line not in repeated)
            for lines in split_pages
        ]

    @staticmethod
    def clean_text(text: str) -> str:
        """Normalize whitespace and neutralize obvious instruction-like PDF content."""
        text = re.sub(
            r"(?i)ignore\s+(?:all\s+)?previous\s+instructions|system\s+prompt|developer\s+message",
            "[filtered]",
            text,
        )
        text = re.sub(r"[\u0000-\u0008\u000b\u000c\u000e-\u001f]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()
