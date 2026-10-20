# Repeated Gesture Detector

[![CI](https://github.com/loganpendragonmultiverse/repeated-gesture-detector/actions/workflows/ci.yml/badge.svg)](https://github.com/loganpendragonmultiverse/repeated-gesture-detector/actions/workflows/ci.yml)

Flag frequently repeated physical actions using an editable gesture-pattern catalog. The command runs locally, uses explicit UTF-8 JSON input, and produces deterministic JSON or Markdown reports without modifying the supplied source material.

## Three-minute start

```bash
python -m pip install .
repeated-gestures examples/sample.json
repeated-gestures examples/sample.json --format json --output report.json
```

The example documents the complete input shape. Reports now include short source-line context, counts grouped beneath Markdown headings, and a warning when the same literal phrase appears under multiple gesture categories. Markdown is intended for immediate review; JSON preserves structured evidence for scripts and later comparison. An existing output file is never overwritten.

## Privacy and platforms

All manuscript text and gesture patterns stay local.

Python 3.10 or newer is supported on Windows, macOS, and Linux. The package has no runtime dependencies, telemetry, account, or hosted service.

## Interpretation boundary

Pattern matches are literal review prompts. Repetition can be deliberate, and the tool does not infer body language, character intent, or semantic equivalents.

## Development

```bash
python -m pip install -e ".[dev]"
ruff format --check .
ruff check .
mypy src
pytest
python -m build
```

Version 1.1 adds contextual evidence, section-level totals, and overlapping-catalog diagnostics. Maintenance focuses on correctness, security, compatibility, and well-supported input improvements.

Part of the [Logan Pendragon Forge open-source collection](https://www.loganpendragonforge.com/open-source/). Licensed under the [MIT License](LICENSE).

## Version 1.2.0: nearby gesture clusters

Set `include_occurrence_spans` to `true` to add half-open character `span` coordinates in the original text to reported occurrences. Set `word_window` to a nonnegative integer to add `proximity_clusters`: connected runs of the same gesture whose adjacent occurrence starts are at most that many word tokens apart. A cluster must meet the existing `minimum`; global `flagged` counts retain their original meaning. Clusters never cross Markdown heading boundaries, even when heading labels repeat. Cluster occurrences include source spans, word-coordinate `word_index`, and one-based `section_start_line`. Word tokens use Unicode word boundaries; headings also count as tokens. Different overlapping catalog phrases remain separate literal matches. Clusters sort by first source position then gesture, with occurrence ties ordered by end position. Default counts, occurrence ordering and literal matching are unchanged.

Try the synthetic example:

```bash
repeated-gestures examples/feature.json --format json
```

`word_index` counts word tokens whose half-open end is at or before the occurrence start. A phrase beginning inside a token uses that token's index; leading punctuation uses the following token's coordinate. A punctuation-only match uses the gap coordinate (zero before the first word, or the total word count after the last). Matches separated only by punctuation or whitespace share a coordinate and may form a zero-window cluster. Thus `(nod) (nod)` has coordinates 0 and 1 and does not cluster with `word_window: 0`.

## Version 1.2.1: consistent newline evidence and checked input

The required `text` must be a non-empty string. `minimum` must be a positive integer (booleans are rejected). Omit `gestures` to use the built-in catalog; an explicitly supplied catalog must be a non-empty object with non-empty string labels and non-empty lists of string phrases. Labels that become identical after trimming are rejected. Source lines, contexts, heading boundaries and occurrence coordinates now use the same Python `splitlines` rules, including CRLF, lone CR and Unicode line separators. Character spans continue to refer to the original unmodified string.

Invalid JSON shapes and option types produce a concise `error:` diagnostic and exit status 2. A report is created exclusively: existing files, directories and symbolic links (including dangling links) are refused, and the input is never overwritten. Output parent directories must already exist. This prevents replacing an existing output leaf; it does not promise an atomic defense against hostile concurrent replacement of the output leaf or parent directories.
