# Knowledge Graph Construction from A Christmas Carol

A small knowledge graph built from an excerpt of Charles Dickens' A Christmas
Carol (Stave One) using a local open-source LLM with minimal human intervention.
Entities and relationships are extracted by the model, lightly cleaned, and
assembled into a directed graph.

## Pipeline

    excerpt.txt
       |  clean_excerpt.py      (remove page markers, duplicates, normalise whitespace)
       v
    excerpt_clean.txt
       |  extract_triples.py    (local LLM extracts subject-relation-object triples)
       v
    triples_raw.json
       |  manual cleanup        (see report; fixes structural extraction errors)
       v
    triples.json
       |  build_graph.py        (build directed graph, export GraphML)
       v
    christmas_carol_stave_one_kg.graphml  ->  visualised in Gephi

## Setup

1. Install Ollama (https://ollama.com) and pull the model:

       ollama pull llama3.1:8b

2. Install Python dependencies:

       pip install -r requirements.txt

## How to run

Run all scripts from the project root, in order:

    python src/clean_excerpt.py       # data/excerpt.txt        -> data/excerpt_clean.txt
    python src/extract_triples.py     # data/excerpt_clean.txt  -> output/triples_raw.json
    python src/build_graph.py         # output/triples.json     -> output/christmas_carol_stave_one_kg.graphml

The graph is then opened and laid out in Gephi to produce the final image
(output/christmas_carol_stave_one_kg.png).

Note on cleanup: extract_triples.py writes the raw model output. The final
triples.json reflects light manual cleanup of that output (splitting phrase-shaped nodes, removing a leaked metaphor). The specific edits
and the reasoning are documented in the report.

## Repository structure

    .
    ├── README.md
    ├── requirements.txt
    │
    ├── data/
    │   ├── excerpt.txt             # raw source excerpt
    │   └── excerpt_clean.txt       # cleaned text
    │
    ├── src/
    │   ├── clean_excerpt.py        # step 1: text cleaning
    │   ├── extract_triples.py      # step 2: LLM-based extraction
    │   └── build_graph.py          # step 3: graph construction + GraphML export
    │
    ├── output/
    │   ├── triples_raw.json        # raw model output
    │   ├── triples.json            # final triples (after manual cleanup)
    │   ├── christmas_carol_stave_one_kg.graphml
    │   └── christmas_carol_stave_one_kg.png
    │
    └── chunking_attempt/           # a rejected experiment, kept for reference
        └── README.md

## Approach in brief

- Model: Llama 3.1 8B (4-bit), run locally via Ollama. No fine-tuning; the model
  is steered entirely through prompt design and few-shot examples.
- Extraction: a single pass over the full excerpt, forcing valid JSON output and
  using temperature=0 for determinism. The prompt was refined across two
  iterations to balance recall against precision.
- Graph: triples become a directed graph in NetworkX, exported as GraphML and
  visualised in Gephi.

A chunked extraction strategy was also tried to improve recall of minor
entities. It was evaluated and rejected; see chunking_attempt/ and the report.