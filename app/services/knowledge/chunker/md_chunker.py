import hashlib
import re


class MarkdownChunker:
    """
    This class represents a markdown content chunker that splits text into sections based on ## headers.
    The structure of returned chunks is defined as follows:
        - `slug`: A unique identifier for the chunk, generated from the title and section headers.
        - `section_text`: The text content of the chunk.
        - `embed_text`: The text content of the chunk, formatted for embedding.
    """

    def __init__(self):
        pass

    def build_chunks(self, text: str) -> list[dict]:
        """
        Split the input text into chunks based on ## headers, with slugs generated from the title and section headers.

        Args:
            text (str): The input text to be chunked.

        Returns:
            list[dict]: A list of chunk dictionaries, each containing a slug and embed text.
        """
        title = self._extract_title(text)
        sections = self._split_by_sections(text)

        chunks = []

        for idx, section in enumerate(sections):
            header_match = re.match(r"^##\s+(.+)$", section, re.MULTILINE)
            section_heading = header_match.group(1).strip() if header_match else None
            slug = header_match.group(1).strip() if header_match else f"section_{idx}"
            # Replace non-alphanumeric characters with underscores, strip leading/trailing underscores, and convert to lowercase
            slug = re.sub(r"[^a-zA-Z0-9:]+", "_", slug).strip("_").lower()

            embed_text = f"{title}\n\n{section}" if title else section

            chunks.append(
                {
                    "slug": slug,
                    "source_heading": title,
                    "section_heading": section_heading,
                    "chunk_index": idx,
                    "section_text": section,
                    "embed_text": embed_text,
                    "embed_hash": hashlib.sha256(embed_text.encode("utf-8")).hexdigest(),
                }
            )

        return chunks

    def _extract_title(self, text: str) -> str | None:
        """Return the first level-1 header (# ...) or None."""
        match = re.search(r"^# (.+)$", text, re.MULTILINE)
        return match.group(1).strip() if match else None

    def _split_by_sections(self, text: str) -> list[str]:
        """Split markdown into chunks delimited by ## headers.

        Each chunk contains the header and all content until the next header
        (or end of file).  If the file has no ## headers the whole text is
        returned as a single chunk.
        """
        # Split by ## headers, preserving the delimiter (so chunks include the header)
        parts = re.split(r"(?=^## )", text, flags=re.MULTILINE)

        ## Filter out empty parts and strip whitespace, keeping only those starting with "## "
        chunks = [p.strip() for p in parts if p.strip() and p.strip().startswith("## ")]

        return chunks if chunks else [text.strip()]
