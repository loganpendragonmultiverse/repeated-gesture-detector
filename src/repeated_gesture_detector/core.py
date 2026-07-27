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
    occurrences = []
    for gesture, patterns in gestures.items():
        for pattern in patterns:
            for match in re.finditer(f"(?<!\\w){re.escape(pattern)}(?!\\w)", text, re.IGNORECASE):
                occurrences.append(
                    {
                        "gesture": gesture,
                        "phrase": match.group(0),
                        "line": text.count("\n", 0, match.start()) + 1,
                    }
                )
    counts = Counter(item["gesture"] for item in occurrences)
    flagged = {key: value for key, value in counts.items() if value >= minimum}
    return {
        "minimum": minimum,
        "flagged": dict(sorted(flagged.items(), key=lambda pair: (-pair[1], pair[0]))),
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
