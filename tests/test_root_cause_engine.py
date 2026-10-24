from app.analyzers.root_cause_engine import calculate_root_cause


def test_type_mismatch_ranks_first():
    evidence = {
        "primary_error": {
            "type": "TypeError",
            "message": "unsupported operand type(s) for +"
        },
        "supporting_evidence": [
            {
                "source": "static_code_analysis",
                "type": "TypeMismatch",
                "line": 3,
                "message": "Integer and string are being added."
            }
        ],
        "related_logs": [],
        "unrelated_logs": [
            {
                "category": "database",
                "message": "Database connection failed"
            }
        ],
        "observations": []
    }

    result = calculate_root_cause(evidence)

    assert result["root_cause"] == "Type mismatch"
    assert result["score"] == 90
    assert result["confidence"] == "High"


def test_database_failure_candidate():
    evidence = {
        "primary_error": {
            "type": "OperationalError",
            "message": "Database connection failed"
        },
        "supporting_evidence": [],
        "related_logs": [],
        "unrelated_logs": [
            {
                "category": "database",
                "message": "Database connection failed"
            }
        ],
        "observations": []
    }

    result = calculate_root_cause(evidence)

    assert result["root_cause"] == "Database failure"
    assert result["score"] == 20