import re


def analyze_error(error_text: str) -> dict:
    """
    Analyze a Python error or stack trace
    and extract useful debugging information.
    """

    result = {
        "exception_type": None,
        "message": None,
        "file": None,
        "line": None,
        "function": None
    }

    if not error_text:
        return result

    # Extract exception type and message
    exception_pattern = (
        r"([A-Za-z_][A-Za-z0-9_]*Error|"
        r"[A-Za-z_][A-Za-z0-9_]*Exception):\s*(.*)"
    )

    exception_match = re.search(
        exception_pattern,
        error_text
    )

    if exception_match:
        result["exception_type"] = exception_match.group(1)
        result["message"] = exception_match.group(2).strip()

    # Extract file and line number
    file_pattern = r'File ["\'](.+?)["\'], line (\d+)'

    file_match = re.search(
        file_pattern,
        error_text
    )

    if file_match:
        result["file"] = file_match.group(1)
        result["line"] = int(file_match.group(2))

    # Extract function name
    function_pattern = r'File ["\'].+?["\'], line \d+, in (\w+)'

    function_match = re.search(
        function_pattern,
        error_text
    )

    if function_match:
        result["function"] = function_match.group(1)

    return result