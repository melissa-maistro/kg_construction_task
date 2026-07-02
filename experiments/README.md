# Experiments

This folder documents the extraction approaches that were tried and rejected
before settling on the final pipeline in `src/`. Each subfolder holds the prompt
(or code) that was used and the output it produced, kept as evidence for the
comparison discussed in the report.

The final approach (a single-pass prompt, version 2) lives in `src/`, not here.

## Summary

| Experiment          | Triples | Result                                             |
|---------------------|---------|----------------------------------------------------|
| `prompt_1_baseline` | 13      | High precision, low recall. Rejected.              |
| Version 2 (final)   | 23      | Best balance. Used in `src/`.                      |
| `chunking_attempt`  | ~190    | Recall up, precision collapsed. Rejected.          |
| `prompt_3_selective`| 18      | Over-corrected, dropped real facts. Rejected.      |

The four versions trace a precision and recall trade-off: the baseline was
precise but narrow, version 2 struck the best balance, chunking pushed recall too
far into noise, and the selective prompt pushed too far into omission. Version 2
was chosen because further changes made the results oscillate rather than
improve, which suggested the 8B model had reached its limit on this text. See
`report.pdf` for the full discussion.

## Contents

### `prompt_1_baseline/`
The first, simplest prompt. It returned 13 triples with high precision but only
captured the dense Scrooge-Marley cluster, missing almost every minor character.
It also produced one broken triple (`Marley -- dead --> null`) because it had no
way to express a one-place fact.

### `prompt_3_selective/`
A single-pass prompt with strict rules to exclude transient actions, dialogue,
and scene description. It over-corrected: 18 triples, with real facts lost (the
clerk disappeared) and new errors introduced (`Scrooge -- employed --> himself`).

### `chunking_attempt/`
An attempt to improve recall by splitting the text into overlapping,
sentence-aligned chunks and extracting from each separately. It made things
worse: about 190 triples, but precision collapsed because with less surrounding
context the model started transcribing the plot (`Scrooge -- saw_poker -->
poker`, lines of dialogue as objects, placeholder values like `true`). This
folder has its own README with more detail.

## Note

These experiments are supporting evidence, not part of the runnable pipeline. To
reproduce the final result, use the scripts in `src/` as described in the
top-level README.