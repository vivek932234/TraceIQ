import json
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.ai import debugging_agent


def sample_evidence():
    return {
        "primary_error": {
            "type": "TypeError",
            "message": "unsupported operand type(s) for +: 'int' and 'str'",
            "file": "app.py",
            "line": 3,
            "function": "calculate",
        },
        "supporting_evidence": [
            {
                "source": "static_code_analysis",
                "type": "TypeMismatch",
                "line": 3,
                "message": "Integer and string are being added.",
            }
        ],
        "related_logs": [],
        "unrelated_logs": [],
        "observations": [],
    }


def sample_root_cause():
    return {
        "root_cause": "Type mismatch",
        "score": 90,
        "confidence": "High",
        "evidence": ["Runtime TypeError detected."],
    }


def test_gemini_success(monkeypatch):
    expected_analysis = {
        "root_cause": "Type mismatch",
        "why_it_happened": "An integer and string were added.",
        "evidence": ["TypeError detected."],
        "suggested_fix": "Convert operands to compatible types.",
        "confidence": "High",
    }

    mock_client = MagicMock()

    mock_client.models.generate_content.return_value = (
        SimpleNamespace(text=json.dumps(expected_analysis))
    )

    monkeypatch.setattr(
        debugging_agent,
        "client",
        mock_client,
    )

    result = debugging_agent.debug_with_ai(
        evidence=sample_evidence(),
        code='age = 22\nname = "Vivek"\nresult = age + name',
        root_cause=sample_root_cause(),
    )

    assert result["status"] == "success"
    assert result["analysis"]["root_cause"] == "Type mismatch"

    mock_client.models.generate_content.assert_called_once()


def test_gemini_failure_uses_fallback(monkeypatch):
    mock_client = MagicMock()

    mock_client.models.generate_content.side_effect = (
        RuntimeError("Simulated API failure")
    )

    monkeypatch.setattr(
        debugging_agent,
        "client",
        mock_client,
    )

    result = debugging_agent.debug_with_ai(
        evidence=sample_evidence(),
        root_cause=sample_root_cause(),
    )

    assert result["status"] == "fallback"
    assert result["analysis"]["root_cause"] == "Type mismatch"
    assert "llm_error" in result


def test_missing_client_uses_fallback(monkeypatch):
    monkeypatch.setattr(
        debugging_agent,
        "client",
        None,
    )

    result = debugging_agent.debug_with_ai(
        evidence=sample_evidence(),
        root_cause=sample_root_cause(),
    )

    assert result["status"] == "fallback"
    assert result["analysis"]["confidence"] == "High"