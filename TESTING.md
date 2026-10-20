# Testing

Install development tools with `python -m pip install -e ".[dev]"`.

Run `ruff format --check .`, `ruff check .`, `mypy src`, `pytest`, and `python -m build`. Preserve the coverage gate and supported CI matrix.

## Version 1.2.0 acceptance

`tests/test_feature.py` covers the new option, boundary cases, and unchanged default reports using synthetic text only. Run `repeated-gestures examples/feature.json --format json` and the README sample commands against an installed wheel and an extracted source archive. Inspect packaged README, CHANGELOG, DEVELOPMENT and TESTING documents and confirm package version 1.2.0.

Punctuation regressions verify the reported `(nod) (nod)` zero-window case, literal word boundaries, leading and trailing punctuation-only gaps, and wordless input. The same word coordinate rule applies to every literal catalog phrase.

## Version 1.2.1 acceptance

Run the complete unchanged lint, strict typing and branch-coverage gates. Regression tests cover malformed top-level and nested shapes, option types, source preservation, exclusive output creation, invalid UTF-8/JSON, and a dangling output link. The link test runs on platforms with link creation; Windows privilege error 1314 alone is reported as unavailable. Package acceptance separately installs the wheel and source distribution, asserts imports resolve to the installed target, executes the complete test suite without source-path leakage, checks the packaged four documents and both examples, and runs the real console entry point for Markdown, JSON and new-file output.
