# Development contract

Flag frequently repeated physical actions using an editable gesture-pattern catalog.

Preserve deterministic, source-safe behavior and the interpretation boundary documented in the README. Every feature release must update tests, version metadata, `CHANGELOG.md`, README claims and limitations, repository metadata, release assets, and the Forge catalog together.

## Version 1.2.0

Set `include_occurrence_spans` to `true` to add half-open character `span` coordinates in the original text to reported occurrences. Set `word_window` to a nonnegative integer to add `proximity_clusters`: connected runs of the same gesture whose adjacent occurrence starts are at most that many word tokens apart. A cluster must meet the existing `minimum`; global `flagged` counts retain their original meaning. Clusters never cross Markdown heading boundaries, even when heading labels repeat. Cluster occurrences include source spans, word-coordinate `word_index`, and one-based `section_start_line`. Word tokens use Unicode word boundaries; headings also count as tokens. Different overlapping catalog phrases remain separate literal matches. Clusters sort by first source position then gesture, with occurrence ties ordered by end position. Default counts, occurrence ordering and literal matching are unchanged.

`word_index` counts word tokens whose half-open end is at or before the occurrence start. A phrase beginning inside a token uses that token's index; leading punctuation uses the following token's coordinate. A punctuation-only match uses the gap coordinate (zero before the first word, or the total word count after the last). Matches separated only by punctuation or whitespace share a coordinate and may form a zero-window cluster. Thus `(nod) (nod)` has coordinates 0 and 1 and does not cluster with `word_window: 0`.

## Version 1.2.1: consistent newline evidence and checked input

The required `text` must be a non-empty string. `minimum` must be a positive integer (booleans are rejected). Omit `gestures` to use the built-in catalog; an explicitly supplied catalog must be a non-empty object with non-empty string labels and non-empty lists of string phrases. Labels that become identical after trimming are rejected. Source lines, contexts, heading boundaries and occurrence coordinates now use the same Python `splitlines` rules, including CRLF, lone CR and Unicode line separators. Character spans continue to refer to the original unmodified string.

Invalid JSON shapes and option types produce a concise `error:` diagnostic and exit status 2. A report is created exclusively: existing files, directories and symbolic links (including dangling links) are refused, and the input is never overwritten. Output parent directories must already exist. This prevents replacing an existing output leaf; it does not promise protection against hostile concurrent replacement of parent directories.
