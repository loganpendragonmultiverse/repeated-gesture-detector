# Development contract

Flag frequently repeated physical actions using an editable gesture-pattern catalog.

Preserve deterministic, source-safe behavior and the interpretation boundary documented in the README. Every feature release must update tests, version metadata, `CHANGELOG.md`, README claims and limitations, repository metadata, release assets, and the Forge catalog together.

## Version 1.2.0

Set `include_occurrence_spans` to `true` to add half-open character `span` coordinates in the original text to reported occurrences. Set `word_window` to a nonnegative integer to add `proximity_clusters`: connected runs of the same gesture whose adjacent occurrence starts are at most that many word tokens apart. A cluster must meet the existing `minimum`; global `flagged` counts retain their original meaning. Clusters never cross Markdown heading boundaries, even when heading labels repeat. Cluster occurrences include source spans, zero-based `word_index`, and one-based `section_start_line`. Word tokens use Unicode word boundaries; headings also count as tokens. Different overlapping catalog phrases remain separate literal matches. Clusters sort by first source position then gesture, with occurrence ties ordered by end position. Default counts, occurrence ordering and literal matching are unchanged.
