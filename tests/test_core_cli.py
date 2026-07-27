import json
from pathlib import Path

import pytest

from repeated_gesture_detector.cli import main
from repeated_gesture_detector.core import PROJECT, analyze, render_json, render_markdown


def test_representative_sample_has_expected_result():
    data = json.loads(
        (Path(__file__).parents[1] / "examples" / "sample.json").read_text(encoding="utf-8")
    )
    report = analyze(data)
    assert report["version"] == 1
    assert report["project"] == PROJECT
    assert report["flagged"] == {"sigh": 3}
    assert report["sections"] == {
        "One": {"sigh": 2, "nod": 1},
        "Two": {"sigh": 1},
    }
    assert report["occurrences"][0]["context"].startswith("Mara sighed")
    assert f'"project": "{PROJECT}"' in render_json(report)
    assert PROJECT.replace("-", " ").title() in render_markdown(report)


def test_missing_required_input_is_rejected():
    with pytest.raises(ValueError):
        analyze({})


def test_catalog_overlap_warning_and_validation():
    report = analyze(
        {
            "text": "# Beat\nMara sighed. Mara sighed.",
            "gestures": {"breath": ["sighed"], "fatigue": ["sighed"]},
        }
    )
    assert report["catalog_warnings"] == [{"phrase": "sighed", "categories": ["breath", "fatigue"]}]
    assert report["occurrences"][0]["section"] == "Beat"
    with pytest.raises(ValueError):
        analyze({"text": "hello", "gestures": {"nod": []}})


def test_cli_json_and_output_safety(tmp_path, capsys):
    source = Path(__file__).parents[1] / "examples" / "sample.json"
    assert main([str(source), "--format", "json"]) == 0
    assert json.loads(capsys.readouterr().out)["project"] == PROJECT
    output = tmp_path / "report.md"
    output.write_text("keep", encoding="utf-8")
    assert main([str(source), "--output", str(output)]) == 2
