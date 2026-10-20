import json
from pathlib import Path

import pytest

from repeated_gesture_detector.cli import main
from repeated_gesture_detector.core import analyze


@pytest.mark.parametrize("data", [None, [], 1, "text", True])
def test_top_level_input_requires_object(data):
    with pytest.raises((ValueError, TypeError), match="JSON object"):
        analyze(data)


def test_cli_rejects_malformed_shapes_without_traceback(tmp_path, capsys):
    source = tmp_path / "bad.json"
    source.write_text("[]", encoding="utf-8")
    assert main([str(source)]) == 2
    output = capsys.readouterr()
    assert output.out == "" and "JSON object" in output.err
    assert "Traceback" not in output.err


def test_cli_invalid_boolean_option_is_friendly(tmp_path, capsys):
    source = tmp_path / "bad-option.json"
    source.write_text(
        json.dumps({"text": "sighed", "include_occurrence_spans": 1}), encoding="utf-8"
    )
    assert main([str(source)]) == 2
    assert "boolean" in capsys.readouterr().err


def test_cli_writes_new_file_and_preserves_existing_input(tmp_path, capsys):
    source = Path(__file__).parents[1] / "examples" / "sample.json"
    original = source.read_bytes()
    output = tmp_path / "report.json"
    assert main([str(source), "--format", "json", "--output", str(output)]) == 0
    assert json.loads(output.read_text(encoding="utf-8"))["project"] == "repeated-gesture-detector"
    assert main([str(source), "--output", str(source)]) == 2
    assert source.read_bytes() == original
    assert "error:" in capsys.readouterr().err


def test_cli_never_follows_dangling_output_symlink(tmp_path, capsys):
    source = Path(__file__).parents[1] / "examples" / "sample.json"
    target = tmp_path / "uncreated-target"
    output = tmp_path / "report-link"
    try:
        output.symlink_to(target)
    except OSError as exc:
        if __import__("sys").platform == "win32" and getattr(exc, "winerror", None) == 1314:
            pytest.skip("Windows runner does not grant symbolic-link creation")
        raise
    assert main([str(source), "--output", str(output)]) == 2
    assert output.is_symlink() and not target.exists()
    assert "error:" in capsys.readouterr().err


@pytest.mark.parametrize("content", [b"{", b"\xff"])
def test_cli_reports_bad_encoding_and_json(tmp_path, capsys, content):
    source = tmp_path / "invalid.json"
    source.write_bytes(content)
    assert main([str(source)]) == 2
    assert "error:" in capsys.readouterr().err


def test_cli_missing_input_and_missing_output_parent(tmp_path, capsys):
    assert main([str(tmp_path / "absent")]) == 2
    source = Path(__file__).parents[1] / "examples" / "sample.json"
    assert main([str(source), "--output", str(tmp_path / "missing" / "report")]) == 2
    assert capsys.readouterr().err.count("error:") == 2
