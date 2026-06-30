"""
extract_triples_chunked.py

Chunked version of the extraction. Splits the cleaned excerpt into
overlapping, sentence-aligned chunks, runs the LLM on each chunk separately,
then merges and deduplicates the triples into triples_chunked.json.

Run from the same folder as chunk_text.py and excerpt_clean.txt:
    python extract_triples_chunked.py

Prerequisites:
    ollama pull llama3.1:8b
    pip install ollama
"""

import json
import logging
import sys

import ollama
from chunk_text import chunk_text   # reuses your standalone chunker

MODEL = "llama3.1:8b"
INPUT_FILE = "excerpt_clean.txt"
OUTPUT_FILE = "triples_chunked.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# Same system prompt as the single-pass script. Keeping it identical means
# chunking is the only variable that changed between the two runs.
SYSTEM_PROMPT = """You are an information extraction system.
Extract entities and the relationships between them from the given text.

Output format:
- Return ONLY a JSON object with a single key "triples".
- "triples" is a list of objects, each with "subject", "relation", "object".
- Use short snake_case relations, for example: partner_of, executor_of,
  nephew_of, employed_by, died, visited, has_state, located_in.

Rules:
- Every triple must have a non-empty subject, relation, AND object.
  Never leave the object null or empty.
- If a fact is a state, condition, or property of an entity, express it as a
  relation to that state. For example, write
  {"subject": "John", "relation": "has_state", "object": "dead"}
  rather than leaving the object empty.
- Objects and subjects must be single entities: one person, place, or thing.
  They must NOT be sentences, clauses, or descriptive phrases.
- If a fact is expressed as a phrase, break it into multiple triples that
  connect single entities, introducing the intermediate entity as its own node.
- Extract relationships for EVERY character mentioned, including minor ones
  who appear only once (for example employees, family members, or visitors).
  Do not extract only the most frequently mentioned characters.
- Use proper names where the text gives them. If a character is only
  described (for example "the clerk"), use that description as the entity.
- Extract only facts stated in the text. Do not invent or infer beyond it.
- Ignore metaphors and figures of speech (for example "dead as a door-nail").

Example text:
"Old Hooper was dead. The shop passed to young Pip, who lived in rooms that
had once belonged to Hooper. Pip's clerk, a man named Tom, earned ten
shillings a week and lived in Dover."

Example output:
{"triples": [
  {"subject": "Old Hooper", "relation": "has_state", "object": "dead"},
  {"subject": "Pip", "relation": "inherited", "object": "shop"},
  {"subject": "Pip", "relation": "lived_in", "object": "rooms"},
  {"subject": "rooms", "relation": "formerly_belonged_to", "object": "Old Hooper"},
  {"subject": "Tom", "relation": "employed_by", "object": "Pip"},
  {"subject": "Tom", "relation": "earns", "object": "ten shillings a week"},
  {"subject": "Tom", "relation": "lived_in", "object": "Dover"}
]}"""


def extract(text):
    """Run the model on one chunk and return a list of well-formed triples."""

    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f'Text:\n"""{text}"""'},
        ],
        format="json",
        options={"temperature": 0, "num_ctx": 16384, "num_thread": 8},
    )

    content = response["message"]["content"]

    try:
        data = json.loads(content)
        triples = data.get("triples", [])
    except (json.JSONDecodeError, AttributeError):
        log.warning("Could not parse a chunk's output as JSON; skipping it.")
        log.warning(content)
        return []

    # Keep only triples that have all three fields with non-empty values.
    clean = [
        t for t in triples
        if isinstance(t, dict)
        and {"subject", "relation", "object"} <= t.keys()
        and t["subject"] and t["relation"] and t["object"]
    ]
    return clean


def merge(all_triples):
    """Deduplicate triples by case-insensitive (subject, relation, object)."""

    seen = set()
    merged = []
    for t in all_triples:
        key = (
            str(t["subject"]).lower().strip(),
            str(t["relation"]).lower().strip(),
            str(t["object"]).lower().strip(),
        )
        if key not in seen:
            seen.add(key)
            merged.append(t)
    return merged


def main():
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        log.error(f"{INPUT_FILE} not found. Run clean_excerpt.py first.")
        sys.exit(1)

    chunks = chunk_text(text)
    log.info(f"Split text into {len(chunks)} chunks.")

    all_triples = []
    for i, chunk in enumerate(chunks, 1):
        log.info(f"Extracting chunk {i}/{len(chunks)} (~{len(chunk)} chars) ...")
        triples = extract(chunk)
        log.info(f"  chunk {i}: {len(triples)} triples")
        all_triples.extend(triples)

    merged = merge(all_triples)
    log.info(f"Total: {len(all_triples)} raw triples, "
             f"{len(merged)} after dedup ({len(all_triples) - len(merged)} duplicates removed).")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump({"triples": merged}, f, indent=2)

    log.info(f"Saved to {OUTPUT_FILE}")
    print()
    for t in merged:
        print(f"  {t['subject']}  --{t['relation']}-->  {t['object']}")


if __name__ == "__main__":
    main()