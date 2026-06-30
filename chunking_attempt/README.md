# Chunking Experiment (not part of the final pipeline)

This folder contains an experiment in **chunked extraction** that was tried to
improve recall, evaluated, and ultimately rejected in favour of the single-pass
approach in `src/`. It is kept here as documented evidence of the comparison.

## Motivation

The single-pass extraction captured the dense, frequently-repeated
Scrooge–Marley relationships well but underweighted minor characters (the clerk,
the nephew, the charity gentlemen) mentioned only once. The hypothesis was that
splitting the text into smaller chunks would give each passage the model's full
attention, so minor entities would no longer be drowned out by the dominant
cluster.

## Approach

- `chunk_text.py` splits the cleaned excerpt into overlapping, sentence-aligned
  chunks of roughly 800–1500 tokens, snapping each cut to the nearest sentence
  boundary and carrying a small overlap into the next chunk to avoid splitting
  facts across a boundary.
- `extract_triples_chunked.py` runs the same extraction prompt on each chunk
  independently, then merges and deduplicates the results.
- `triples_chunked.json` is the resulting output, kept as evidence.

## Result: rejected

Chunking raised recall but caused a large drop in precision. With less
surrounding context, the model lost its sense of what was significant and began
transcribing the plot rather than extracting durable relationships. The output
ballooned to roughly 190 triples dominated by transient actions
(`Scrooge -- saw_poker --> poker`), individual lines of dialogue as objects, and
placeholder values (`true`, `none`) where no real object existed.

This illustrates a precision/recall trade-off central to LLM-based extraction:
smaller chunks improve coverage of underweighted entities but degrade the
model's ability to judge relevance, because that judgement depends on seeing the
text as a whole. The single-pass extraction sits at a better operating point and
is the one used in the final pipeline.

See the main report for the full comparison and discussion.

## Files

| File                          | Purpose                                      |
|-------------------------------|----------------------------------------------|
| `chunk_text.py`               | Sentence-aligned chunker with overlap        |
| `extract_triples_chunked.py`  | Per-chunk extraction, merge, and dedup       |
| `triples_chunked.json`        | Output of the chunked run (rejected)         |