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


@pytest.mark.parametrize("prefix", ["", "é ", "a\r\n"])
def test_punctuation_leading_phrases_have_distinct_word_coordinates(prefix):
    text = prefix + "(nod) (nod)"
    data = {"text": text, "gestures": {"nod": ["(nod)"]}, "minimum": 2}
    baseline = analyze(data)
    assert analyze({**data, "word_window": 0})["proximity_clusters"] == []
    result = analyze({**data, "word_window": 1})
    cluster = result.pop("proximity_clusters")[0]
    assert [item["word_index"] for item in cluster["occurrences"]] == (
        [0, 1] if not prefix else [1, 2]
    )
    for item in cluster["occurrences"]:
        span = item["span"]
        assert text[span["start"] : span["end"]] == "(nod)"
    result.pop("word_window")
    assert result == baseline


@pytest.mark.parametrize(
    "text,indices",
    [
        ("! a ! b !", [0, 1, 2]),
        ("! !", [0, 0]),
        ("a ! !", [1, 1]),
        ("! é ! b !", [0, 1, 2]),
    ],
)
def test_punctuation_only_gap_coordinates_and_zero_window_boundary(text, indices):
    data = {"text": text, "gestures": {"mark": ["!"]}, "minimum": 2}
    cluster = analyze({**data, "word_window": 1})["proximity_clusters"][0]
    assert [item["word_index"] for item in cluster["occurrences"]] == indices
    zero_clusters = analyze({**data, "word_window": 0})["proximity_clusters"]
    assert [item["count"] for item in zero_clusters] == ([2] if len(set(indices)) == 1 else [])


def test_punctuation_catalog_retains_literal_word_boundaries():
    data = {"text": "a! !b", "gestures": {"mark": ["!"]}, "minimum": 1}
    report = analyze({**data, "word_window": 0})
    assert report["flagged"] == {}
    assert report["proximity_clusters"] == []
