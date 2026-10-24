from app.analyzers.fix_validation_engine import validate_fix


def test_validates_type_mismatch_fix():
    original_code = (
        'age = 22\n'
        'name = "Vivek"\n'
        'result = age + name'
    )

    suggested_code = (
        'age = 22\n'
        'name = "Vivek"\n'
        'result = str(age) + name'
    )

    result = validate_fix(
        original_code=original_code,
        suggested_code=suggested_code,
        root_cause={"root_cause": "Type mismatch"},
    )

    assert result["valid_syntax"] is True
    assert result["issue_resolved"] is True
    assert result["validation_status"] == "passed"


def test_rejects_invalid_python_syntax():
    result = validate_fix(
        original_code='age = 22\nname = "Vivek"\nresult = age + name',
        suggested_code="if True\n    print('Hello')",
        root_cause={"root_cause": "Type mismatch"},
    )

    assert result["valid_syntax"] is False
    assert result["validation_status"] == "rejected"


def test_detects_unresolved_type_mismatch():
    original_code = (
        'age = 22\n'
        'name = "Vivek"\n'
        'result = age + name'
    )

    result = validate_fix(
        original_code=original_code,
        suggested_code=original_code,
        root_cause={"root_cause": "Type mismatch"},
    )

    assert result["valid_syntax"] is True
    assert result["issue_resolved"] is False
    assert result["validation_status"] == "inconclusive"


def test_unknown_root_cause_is_inconclusive():
    result = validate_fix(
        original_code="x = 10",
        suggested_code="x = 20",
        root_cause={"root_cause": "Unknown"},
    )

    assert result["valid_syntax"] is True
    assert result["validation_status"] == "inconclusive"


def test_empty_suggestion_is_rejected():
    result = validate_fix(
        original_code="x = 10",
        suggested_code="",
        root_cause={"root_cause": "Type mismatch"},
    )

    assert result["validation_status"] == "rejected"