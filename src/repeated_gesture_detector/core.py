from __future__ import annotations

import json
import re
from bisect import bisect_right
from collections import Counter
from typing import Any

PROJECT = "repeated-gesture-detector"


def _require(data: dict[str, Any], key: str) -> Any:
    value = data.get(key)
    if value is None or value == "" or value == []:
        raise ValueError(f"{key} is required")
    return value


def _gestures(data: dict[str, Any]) -> dict[str, Any]:
    text = str(_require(data, "text"))
    include_spans = data.get("include_occurrence_spans", False)
    if not isinstance(include_spans, bool):
        raise TypeError("include_occurrence_spans must be a boolean")
    window = data.get("word_window")
    if window is not None and (
        isinstance(window, bool) or not isinstance(window, int) or window < 0
    ):
        raise ValueError("word_window must be a nonnegative integer")
    word_ends = [match.end() for match in re.finditer(r"\b\w+\b", text)]
    minimum = data.get("minimum", 2)
    if not isinstance(minimum, int) or minimum < 1:
        raise ValueError("minimum must be a positive integer")
    gestures = data.get("gestures") or {
        "sigh": ["sighed", "sighs", "sighing"],
        "nod": ["nodded", "nods", "nodding"],
        "shrug": ["shrugged", "shrugs", "shrugging"],
        "crossed arms": ["crossed his arms", "crossed her arms", "crossed their arms"],
    }
    if not isinstance(gestures, dict) or not gestures:
        raise ValueError("gestures must be a non-empty object")
    phrase_categories: dict[str, list[str]] = {}
    normalized: dict[str, list[str]] = {}
    for raw_gesture, raw_patterns in gestures.items():
        gesture = str(raw_gesture).strip()
        if not gesture or not isinstance(raw_patterns, list) or not raw_patterns:
            raise ValueError("each gesture must have a non-empty phrase list")
        patterns: list[str] = []
        for raw_pattern in raw_patterns:
            pattern = str(raw_pattern).strip()
            if not pattern:
                raise ValueError("gesture phrases cannot be empty")
            if pattern.casefold() not in {item.casefold() for item in patterns}:
                patterns.append(pattern)
            phrase_categories.setdefault(pattern.casefold(), []).append(gesture)
        normalized[gesture] = patterns
    catalog_warnings = [
        {"phrase": phrase, "categories": sorted(set(categories))}
        for phrase, categories in phrase_categories.items()
        if len(set(categories)) > 1
    ]
    headings: list[tuple[int, str]] = [(1, "(document)")]
    source_lines = text.splitlines()
    for line_number, line_text in enumerate(source_lines, start=1):
        heading = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", line_text)
        if heading:
            headings.append((line_number, heading.group(1)))

    def section_at(line: int) -> str:
        return next(name for start, name in reversed(headings) if start <= line)

    occurrences = []
    located: list[dict[str, Any]] = []
    for gesture, patterns in normalized.items():
        for pattern in patterns:
            for match in re.finditer(f"(?<!\\w){re.escape(pattern)}(?!\\w)", text, re.IGNORECASE):
                line = text.count("\n", 0, match.start()) + 1
                context = source_lines[line - 1].strip() if source_lines else ""
                occurrences.append(
                    {
                        "gesture": gesture,
                        "phrase": match.group(0),
                        "line": line,
                        "section": section_at(line),
                        "context": context[:157] + "..." if len(context) > 160 else context,
                    }
                )
                if include_spans or window is not None:
                    span = {"start": match.start(), "end": match.end()}
                    if include_spans:
                        occurrences[-1]["span"] = span
                    located.append(
                        {
                            **occurrences[-1],
                            "span": span,
                            "word_index": bisect_right(word_ends, match.start()),
                            "section_start_line": next(
                                start for start, _ in reversed(headings) if start <= line
                            ),
                        }
                    )
    counts = Counter(item["gesture"] for item in occurrences)
    flagged = {key: value for key, value in counts.items() if value >= minimum}
    section_counts: dict[str, Counter[str]] = {}
    for item in occurrences:
        section_counts.setdefault(str(item["section"]), Counter())[str(item["gesture"])] += 1
    report = {
        "minimum": minimum,
        "flagged": dict(sorted(flagged.items(), key=lambda pair: (-pair[1], pair[0]))),
        "sections": {section: dict(counts) for section, counts in section_counts.items()},
        "catalog_warnings": catalog_warnings,
        "occurrences": [item for item in occurrences if item["gesture"] in flagged],
    }

    if window is not None:
        clusters: list[dict[str, Any]] = []
        for gesture in normalized:
            candidates = sorted(
                (item for item in located if item["gesture"] == gesture),
                key=lambda item: (item["span"]["start"], item["span"]["end"]),
            )
            # Connected runs use the distance between adjacent occurrence starts.
            runs: list[list[dict[str, Any]]] = []
            for item in candidates:
                if (
                    not runs
                    or item["section_start_line"] != runs[-1][-1]["section_start_line"]
                    or item["word_index"] - runs[-1][-1]["word_index"] > window
                ):
                    runs.append([])
                runs[-1].append(item)
            for run in runs:
                if len(run) >= minimum:
                    clusters.append({"gesture": gesture, "count": len(run), "occurrences": run})
        clusters.sort(
            key=lambda cluster: (cluster["occurrences"][0]["span"]["start"], cluster["gesture"])
        )
        report["word_window"] = window
        report["proximity_clusters"] = clusters
    return report


def analyze(data: dict[str, Any]) -> dict[str, Any]:
    return {"version": 1, "project": PROJECT, **_gestures(data)}


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False) + "\n"


def render_markdown(report: dict[str, Any]) -> str:
    lines = [f"# {report['project'].replace('-', ' ').title()} report", ""]
    for key, value in report.items():
        if key not in {"version", "project"}:
            lines.append(f"## {key.replace('_', ' ').title()}")
            lines.append("")
            lines.append(f"```json\n{json.dumps(value, indent=2, ensure_ascii=False)}\n```")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"
