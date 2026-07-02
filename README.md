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
       |  build_graph.py        (build directed multigraph, export GraphML)
       v
    christmas_carol_stave_one_kg.graphml
       |  visualize_pyvis.py    (render interactive HTML)
       v
    christmas_carol_stave_one_kg.html  ->  screenshot -> .png

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
    python src/visualize_pyvis.py     # graphml                 -> output/christmas_carol_stave_one_kg.html

Open the resulting HTML file in a browser for the interactive graph. The static
image in output/ (christmas_carol_stave_one_kg.png) is a screenshot of that view.

Note on cleanup: extract_triples.py writes the raw model output. The final
triples.json reflects light manual cleanup of that output (fixing null objects,
splitting phrase-shaped nodes, removing a leaked metaphor). The specific edits
and the reasoning are documented in the report.

## Repository structure

    .
    ├── README.md
    ├── requirements.txt
    ├── report.pdf                  # 1-2 page writeup: approach, challenges, improvements
    │
    ├── data/
    │   ├── excerpt.txt             # raw source excerpt
    │   └── excerpt_clean.txt       # cleaned text
    │
    ├── src/
    │   ├── clean_excerpt.py        # step 1: text cleaning
    │   ├── extract_triples.py      # step 2: LLM-based extraction (final prompt)
    │   ├── build_graph.py          # step 3: graph construction + GraphML export
    │   └── visualize_pyvis.py      # step 4: interactive HTML visualization
    │
    ├── output/
    │   ├── triples_raw.json        # raw model output
    │   ├── triples.json            # final triples (after manual cleanup)
    │   ├── christmas_carol_stave_one_kg.graphml
    │   ├── christmas_carol_stave_one_kg.html
    │   └── christmas_carol_stave_one_kg.png
    │
    └── experiments/                # extraction approaches that were tried and rejected
        ├── README.md
        ├── prompt_1_baseline/      # first simple prompt (13 triples)
        ├── prompt_3_selective/     # over-strict prompt (18 triples)
        └── chunking_attempt/       # chunked extraction (~190 triples, noisy)

## Approach in brief

- Model: Llama 3.1 8B (4-bit), run locally via Ollama. No fine-tuning; the model
  is steered entirely through prompt design and few-shot examples.
- Extraction: a single pass over the full excerpt, forcing valid JSON output and
  using temperature=0 for determinism. The prompt was refined across four
  versions to balance recall against precision; the final one is in src/.
- Graph: triples become a directed multigraph in NetworkX, exported as GraphML
  and rendered as an interactive HTML page with pyvis, where node size scales
  with degree

The rejected approaches, including a chunking strategy tried to improve recall,
are kept in experiments/ as documented evidence. See report.pdf for the full
discussion of challenges, evaluation, and possible improvements.

## Reproducibility

All steps are deterministic (temperature=0, fixed extraction settings). The
scripts read and write fixed paths relative to the project root, so run them from
there. The one manual step is the cleanup between triples_raw.json and
triples.json, which is documented in the report.