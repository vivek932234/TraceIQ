from app.analyzers.error_analyzer import analyze_error


def test_detects_type_error():
    error = """
    Traceback (most recent call last):
      File "app.py", line 3, in calculate
        result = age + name
    TypeError: unsupported operand type(s) for +: 'int' and 'str'
    """

    result = analyze_error(error)

    assert result["exception_type"] == "TypeError"
    assert result["file"] == "app.py"
    assert result["line"] == 3
    assert result["function"] == "calculate"


def test_detects_name_error():
    error = """
    Traceback (most recent call last):
      File "app.py", line 10, in main
    NameError: name 'username' is not defined
    """

    result = analyze_error(error)

    assert result["exception_type"] == "NameError"
    assert result["message"] == "name 'username' is not defined"


def test_empty_error():
    result = analyze_error("")

    assert result["exception_type"] is None
    assert result["message"] is None
    assert result["file"] is None


def test_error_without_traceback_location():
    result = analyze_error("ValueError: invalid value")

    assert result["exception_type"] == "ValueError"
    assert result["message"] == "invalid value"
    assert result["file"] is None