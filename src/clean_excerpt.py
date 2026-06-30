"""
clean_excerpt.py

Reads a raw text excerpt, removes mechanical noise, and writes a cleaned
version to a new file for use in the LLM extraction step.

Cleaning performed:
  1. Strips inline page-number markers like [12], [13] that appear glued
     to words (e.g. "sole[12]" -> "sole").
  2. Collapses runs of whitespace and newlines into single spaces.
  3. Removes consecutive duplicate sentences (paste artifacts where a line
     appears repeated back to back).

Archaic spelling and original punctuation are left untouched on purpose.
The model reads them fine and they are part of the source text.

Usage:
    python clean_excerpt.py
    python clean_excerpt.py --input excerpt.txt --output excerpt_clean.txt
"""

import argparse
import re
import sys


def clean(text: str) -> str:
    """Apply all cleaning steps to a raw text string and return the result."""

    # 1. Remove inline page-number markers like [12] or [134].
    text = re.sub(r"\[\d+\]", "", text)

    # 2. Normalize all whitespace (newlines, tabs, multiple spaces) to one space.
    text = re.sub(r"\s+", " ", text).strip()

    # 3. Drop consecutive duplicate sentences.
    #    Split on sentence-ending punctuation followed by a space, keeping the
    #    punctuation attached to each sentence.
    sentences = re.split(r"(?<=[.!?]) ", text)
    deduped = [
        s for i, s in enumerate(sentences)
        if i == 0 or s.strip() != sentences[i - 1].strip()
    ]

    return " ".join(deduped)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clean a raw text excerpt for LLM-based extraction."
    )
    parser.add_argument(
        "--input", default="data/excerpt.txt",
        help="Path to the raw input file (default: excerpt.txt)"
    )
    parser.add_argument(
        "--output", default="data/excerpt_clean.txt",
        help="Path to write the cleaned file (default: excerpt_clean.txt)"
    )
    args = parser.parse_args()

    # Read the raw text. Exit with a clear message if the file is missing.
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            raw = f.read()
    except FileNotFoundError:
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    cleaned = clean(raw)

    # Write the cleaned text.
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(cleaned)

    # Print a short summary so you can sanity-check the result.
    raw_sentences = len(re.split(r"(?<=[.!?]) ", re.sub(r"\s+", " ", raw).strip()))
    clean_sentences = len(re.split(r"(?<=[.!?]) ", cleaned))
    print(f"Read:    {args.input} ({len(raw)} chars)")
    print(f"Wrote:   {args.output} ({len(cleaned)} chars)")
    print(f"Sentences: {raw_sentences} -> {clean_sentences} "
          f"({raw_sentences - clean_sentences} removed as duplicates)")


if __name__ == "__main__":
    main()