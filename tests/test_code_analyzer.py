from app.analyzers.code_analyzer import analyze_code


def test_detects_integer_string_mismatch():
    code = """
age = 22
name = "Vivek"
result = age + name
"""

    result = analyze_code(code)

    assert result["valid_python"] is True
    assert result["variables"]["age"] == "int"
    assert result["variables"]["name"] == "str"

    assert any(
        issue["type"] == "TypeMismatch"
        for issue in result["potential_issues"]
    )


def test_valid_string_concatenation():
    code = """
first_name = "Vivek"
last_name = "Sawwalakhe"
full_name = first_name + last_name
"""

    result = analyze_code(code)

    assert result["valid_python"] is True

    assert not any(
        issue["type"] == "TypeMismatch"
        for issue in result["potential_issues"]
    )


def test_detects_syntax_error():
    code = """
if True
    print("Hello")
"""

    result = analyze_code(code)

    assert result["valid_python"] is False
    assert "syntax_error" in result
    assert result["syntax_error"]["line"] == 2


def test_empty_source_code():
    result = analyze_code("")

    assert result["valid_python"] is True
    assert result["potential_issues"] == []