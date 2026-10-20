import pytest

from repeated_gesture_detector.core import analyze


@pytest.mark.parametrize("text", [None, "", [], {}, 3, True])
def test_invalid_text(text):
    with pytest.raises((ValueError, TypeError), match="text"):
        analyze({"text": text})


@pytest.mark.parametrize("minimum", [True, False, 0, -1, 1.5, "2", None])
def test_invalid_minimum(minimum):
    with pytest.raises((ValueError, TypeError), match="minimum"):
        analyze({"text": "sighed", "minimum": minimum})


@pytest.mark.parametrize(
    "gestures",
    [
        None,
        {},
        [],
        "nod",
        {"": ["nod"]},
        {"nod": []},
        {"nod": "nod"},
        {"nod": [None]},
        {"nod": [""]},
        {"nod": [" "]},
        {1: ["nod"]},
        {"nod": ["nod"], " nod ": ["nodded"]},
    ],
)
def test_invalid_gesture_catalog(gestures):
    with pytest.raises((ValueError, TypeError)):
        analyze({"text": "nod nodded", "gestures": gestures})


@pytest.mark.parametrize("separator", ["\n", "\r\n", "\r", "\u2028", "\u0085", "\v"])
def test_source_lines_and_sections_share_newline_rules(separator):
    text = separator.join(["# One", "sighed", "# Two", "sighed"])
    report = analyze({"text": text, "word_window": 99, "include_occurrence_spans": True})
    assert [(item["line"], item["section"], item["context"]) for item in report["occurrences"]] == [
        (2, "One", "sighed"),
        (4, "Two", "sighed"),
    ]
    assert report["proximity_clusters"] == []
    for item in report["occurrences"]:
        assert text[item["span"]["start"] : item["span"]["end"]] == "sighed"


def test_phrase_deduplication_and_long_context():
    report = analyze(
        {
            "text": "x " * 100 + "sighed sighed",
            "gestures": {"breath": ["sighed", "SIGHED"]},
            "minimum": 1,
        }
    )
    assert report["flagged"] == {"breath": 2}
    assert all(len(item["context"]) == 160 for item in report["occurrences"])
