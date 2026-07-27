from __future__ import annotations

import json
import re
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
    counts = Counter(item["gesture"] for item in occurrences)
    flagged = {key: value for key, value in counts.items() if value >= minimum}
    section_counts: dict[str, Counter[str]] = {}
    for item in occurrences:
        section_counts.setdefault(str(item["section"]), Counter())[str(item["gesture"])] += 1
    return {
        "minimum": minimum,
        "flagged": dict(sorted(flagged.items(), key=lambda pair: (-pair[1], pair[0]))),
        "sections": {section: dict(counts) for section, counts in section_counts.items()},
        "catalog_warnings": catalog_warnings,
        "occurrences": [item for item in occurrences if item["gesture"] in flagged],
    }


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
