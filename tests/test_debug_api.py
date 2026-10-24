from fastapi.testclient import TestClient

from app.main import app
from app.api.routes import debug as debug_route


client = TestClient(app)


def test_debug_endpoint_returns_analysis(monkeypatch):
    # Mock AI so the test doesn't call Gemini.
    def mock_debug_with_ai(
        evidence,
        code="",
        logs="",
        root_cause=None
    ):
        return {
            "status": "success",
            "analysis": {
                "root_cause": "Type mismatch",
                "why_it_happened": (
                    "An integer and a string are being added."
                ),
                "evidence": [
                    "Static analysis detected a type mismatch."
                ],
                "suggested_fix": (
                    "Convert the operands to compatible types."
                ),
                "confidence": "High"
            }
        }

    monkeypatch.setattr(
        debug_route,
        "debug_with_ai",
        mock_debug_with_ai
    )

    response = client.post(
        "/api/v1/debug",
        json={
            "error": (
                "Traceback (most recent call last):\n"
                '  File "app.py", line 3, in calculate\n'
                "TypeError: unsupported operand type(s) "
                "for +: 'int' and 'str'"
            ),
            "code": (
                'age = 22\n'
                'name = "Vivek"\n'
                'result = age + name'
            ),
            "logs": (
                "2026-10-24 10:00:00 INFO Application started"
            )
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Debug request analyzed"
    assert data["error_analysis"]["exception_type"] == "TypeError"
    assert data["code_analysis"]["valid_python"] is True
    assert data["root_cause"]["root_cause"] == "Type mismatch"
    assert data["ai_analysis"]["status"] == "success"


def test_debug_endpoint_handles_empty_input(monkeypatch):
    def mock_debug_with_ai(
        evidence,
        code="",
        logs="",
        root_cause=None
    ):
        return {
            "status": "fallback",
            "analysis": {
                "root_cause": "Unknown",
                "confidence": "Low"
            }
        }

    monkeypatch.setattr(
        debug_route,
        "debug_with_ai",
        mock_debug_with_ai
    )

    response = client.post(
        "/api/v1/debug",
        json={
            "error": "",
            "code": "",
            "logs": ""
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["error_analysis"]["exception_type"] is None
    assert data["code_analysis"]["valid_python"] is True
    assert data["log_analysis"]["total_entries"] == 0