# Changelog

## 1.2.1 - 2026-10-20

- Consistent newline evidence and checked input.
- Return friendly diagnostics for malformed input and refuse existing or linked report targets with exclusive file creation.
- Added regression tests and documented the exact supported input and source-safety boundaries.

## 1.2.0 - 2026-10-16

- Added nearby gesture clusters.
- Count completed word tokens for occurrence coordinates, including punctuation-leading and punctuation-only phrases.
- Preserved legacy defaults and added synthetic boundary and compatibility tests.

## 1.1.0 - 2026-07-27

- Added short source-line context and Markdown-section names to occurrence evidence.
- Added per-section gesture counts.
- Added warnings when one literal phrase belongs to multiple gesture categories.
- Added stricter editable-catalog validation and phrase deduplication.

## 1.0.0 - 2026-07-26

- Released the first complete Repeated Gesture Detector command-line workflow.
- Added deterministic JSON and Markdown reporting, representative examples, and cross-platform tests.
