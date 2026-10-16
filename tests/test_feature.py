from copy import deepcopy

import pytest

from repeated_gesture_detector.core import analyze


@pytest.mark.parametrize("window,counts", [(0, []), (1, []), (2, [2]), (3, [3])])
def test_window_start_boundaries_and_global_compatibility(window, counts):
    data = {"text": "sighed then sighed one two sighed", "minimum": 2}
    original = deepcopy(data)
    baseline = analyze(data)
    result = analyze({**data, "word_window": window})
    assert data == original
    assert [item["count"] for item in result.pop("proximity_clusters")] == counts
    assert result.pop("word_window") == window
    assert result == baseline


def test_repeated_headings_overlapping_phrases_and_stable_order():
    text = "# Beat\r\né nodded twice nodded\r\n# Beat\r\nnodded nodded"
    data = {
        "text": text,
        "gestures": {"z": ["nodded", "nodded twice"], "a": ["nodded"]},
        "minimum": 2,
    }
    baseline = analyze(data)
    result = analyze({**data, "include_occurrence_spans": True, "word_window": 3})
    assert result["flagged"] == baseline["flagged"]
    clusters = result["proximity_clusters"]
    assert [(c["gesture"], c["count"]) for c in clusters] == [
        ("a", 2),
        ("z", 3),
        ("a", 2),
        ("z", 2),
    ]
    assert [c["occurrences"][0]["section_start_line"] for c in clusters] == [1, 1, 3, 3]
    for item in result["occurrences"]:
        span = item["span"]
        assert text[span["start"] : span["end"]] == item["phrase"]
    for cluster in clusters:
        starts = [item["span"]["start"] for item in cluster["occurrences"]]
        assert starts == sorted(starts)
    assert result == analyze({**data, "include_occurrence_spans": True, "word_window": 3})
    spans_only = analyze({**data, "include_occurrence_spans": True})
    for item in spans_only["occurrences"]:
        item.pop("span")
    assert spans_only == baseline


@pytest.mark.parametrize("window", [-1, True, 1.5, "3"])
def test_invalid_window(window):
    with pytest.raises(ValueError, match="word_window"):
        analyze({"text": "sighed", "word_window": window})


def test_invalid_spans_and_no_clusters():
    with pytest.raises(TypeError, match="boolean"):
        analyze({"text": "sighed", "include_occurrence_spans": 1})
    assert analyze({"text": "quiet day", "word_window": 0})["proximity_clusters"] == []
