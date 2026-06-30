"""
extract_triples.py

Uses a local LLM (via Ollama) to extract (subject, relation, object)
triples from the cleaned excerpt, and saves them to triples.json.

Prerequisites:
    ollama pull llama3.1:8b
    pip install ollama
"""

import json
import sys
import ollama
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

MODEL = "llama3.1:8b"
INPUT_FILE = "excerpt_clean.txt"
OUTPUT_FILE = "triples.json"

# Few-shot examples steer a small model toward the format and the kind of
# relations we want. They are illustrative, not from the actual excerpt.
SYSTEM_PROMPT1 = """You are an information extraction system.
Extract entities and the relationships between them from the given text.

Rules:
- Return ONLY a JSON object with a single key "triples".
- "triples" is a list of objects, each with "subject", "relation", "object".
- Use short snake_case relations, for example: partner_of, executor_of,
  nephew_of, employed_by, died, visited_by, located_in.
- Use proper names where the text gives them. If a character is only
  described (for example "the clerk"), use that description as the entity.
- Extract only facts stated in the text. Do not invent or infer beyond it.
- Ignore metaphors and figures of speech (for example "dead as a door-nail").

Example text:
"Anna was the daughter of Mr. Bennet. She worked for Mr. Gardiner in London."

Example output:
{"triples": [
  {"subject": "Anna", "relation": "daughter_of", "object": "Mr. Bennet"},
  {"subject": "Anna", "relation": "employed_by", "object": "Mr. Gardiner"},
  {"subject": "Mr. Gardiner", "relation": "located_in", "object": "London"}
]}"""

# --------------------------------------------------------------------------------------------
SYSTEM_PROMPT2 = """You are an information extraction system.
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

# --------------------------------------------------------------------------------------------

def extract(text: str) -> list:
    """Send the text to the model and return a list of triple dicts."""

    log.info(f"Sending {len(text)} chars to {MODEL} ...")

    chunks = []
    for part in ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT2},
            {"role": "user", "content": f'Text:\n"""{text}"""'},
        ],
        format="json",
        options={"temperature": 0, "num_ctx": 16384, "num_thread": 8},
        stream=True,                       # yield tokens as they are generated
    ):
        token = part["message"]["content"]
        chunks.append(token)
        print(token, end="", flush=True)   # live view of the raw output

    print()                                # newline after the stream ends
    content = "".join(chunks)
    log.info(f"Received {len(content)} chars from model.")

    try:
        data = json.loads(content)
        triples = data.get("triples", [])
    except (json.JSONDecodeError, AttributeError):
        log.warning("Could not parse model output as JSON.")
        log.warning(content)
        return []

    clean = [
        t for t in triples
        if isinstance(t, dict) and {"subject", "relation", "object"} <= t.keys()
    ]
    log.info(f"Parsed {len(clean)} well-formed triples.")
    return clean


def main() -> None:
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"Error: {INPUT_FILE} not found. Run clean_excerpt.py first.",
              file=sys.stderr)
        sys.exit(1)

    triples = extract(text)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump({"triples": triples}, f, indent=2)

    print(f"Extracted {len(triples)} triples, saved to {OUTPUT_FILE}\n")
    for t in triples:
        print(f"  {t['subject']}  --{t['relation']}-->  {t['object']}")


if __name__ == "__main__":
    main()