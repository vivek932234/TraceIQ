from app.analyzers.fix_recommendation_engine import (
    generate_fix_recommendation,
)


def test_recommends_fix_for_integer_string_mismatch():
    root_cause = {
        "root_cause": "Type mismatch",
        "score": 90,
        "confidence": "High",
    }

    error_analysis = {
        "exception_type": "TypeError",
        "message": "unsupported operand type(s) for +: 'int' and 'str'",
    }

    code_analysis = {
        "variables": {
            "age": "int",
            "name": "str",
        },
        "potential_issues": [
            {
                "type": "TypeMismatch",
                "line": 3,
                "message": "Integer and string are being added.",
            }
        ],
    }

    result = generate_fix_recommendation(
        root_cause,
        error_analysis,
        code_analysis,
    )

    assert result["status"] == "review_required"
    assert result["suggested_code"] == "result = str(age) + name"
    assert result["alternative_code"] is not None
    assert result["requires_manual_review"] is True


def test_unknown_root_cause_does_not_invent_fix():
    root_cause = {"root_cause": "Unknown"}
    error_analysis = {"exception_type": None, "message": None}
    code_analysis = {"variables": {}, "potential_issues": []}

    result = generate_fix_recommendation(
        root_cause,
        error_analysis,
        code_analysis,
    )

    assert result["status"] == "insufficient_evidence"
    assert result["suggested_code"] is None
    assert result["requires_manual_review"] is True


def test_database_failure_recommends_investigation():
    root_cause = {"root_cause": "Database failure"}
    error_analysis = {"exception_type": None, "message": None}
    code_analysis = {"variables": {}, "potential_issues": []}

    result = generate_fix_recommendation(
        root_cause,
        error_analysis,
        code_analysis,
    )

    assert result["status"] == "review_required"
    assert result["suggested_code"] is None
    assert "database" in result["explanation"].lower()