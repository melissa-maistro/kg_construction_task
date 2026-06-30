"""
chunk_text.py

Splits a cleaned text into overlapping, sentence-aligned chunks sized by an
approximate token budget. Designed to feed each chunk to the LLM separately
so minor characters are not drowned out by the dense opening.

Token counts are approximated from characters. The ratio below is measured
from a real run: the full excerpt was 36312 chars and 8792 tokens
(36312 / 8792 = 4.13 chars per token). Chunking does not need exact token
counts, so this estimate is good enough and needs no tokenizer.
"""

import re

CHARS_PER_TOKEN = 4.13      # measured from the actual extraction run
TARGET_TOKENS = 1000        # aim for ~1000 tokens per chunk (in the 800-1500 range)
OVERLAP_TOKENS = 100        # carry ~100 tokens of context into the next chunk


def chunk_text(text, target_tokens=TARGET_TOKENS, overlap_tokens=OVERLAP_TOKENS):
    """Split text into overlapping chunks that end on sentence boundaries."""

    char_budget = int(target_tokens * CHARS_PER_TOKEN)
    overlap_chars = int(overlap_tokens * CHARS_PER_TOKEN)
    n = len(text)

    # Sentence boundaries: the position right after any . ! ? plus whitespace.
    # Include the very start (0) and end (n) so snapping always has a target.
    boundaries = [0] + [m.end() for m in re.finditer(r"[.!?]+\s+", text)] + [n]

    def snap(pos):
        """Return the sentence boundary nearest to a character position."""
        return min(boundaries, key=lambda b: abs(b - pos))

    chunks = []
    start = 0
    while start < n:
        target_end = start + char_budget

        if target_end >= n:
            end = n                      # last chunk runs to the end
        else:
            end = snap(target_end)       # snap the cut to a sentence boundary

        # Safety: guarantee forward progress if snapping lands at/before start.
        if end <= start:
            later = [b for b in boundaries if b > start]
            end = later[0] if later else n

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= n:
            break

        # Start the next chunk overlap_chars earlier, snapped to a boundary,
        # so a fact straddling the cut appears whole in at least one chunk.
        start = snap(end - overlap_chars)

    return chunks


if __name__ == "__main__":
    with open("excerpt_clean.txt", "r", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_text(text)

    print(f"Produced {len(chunks)} chunks\n")
    for i, c in enumerate(chunks, 1):
        approx_tokens = int(len(c) / CHARS_PER_TOKEN)
        preview = c[:70].replace("\n", " ")
        print(f"Chunk {i:>2}: ~{approx_tokens:>4} tokens, {len(c):>5} chars | {preview}...")