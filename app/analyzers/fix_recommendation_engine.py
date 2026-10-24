def generate_fix_recommendation(
    root_cause: dict,
    error_analysis: dict,
    code_analysis: dict
) -> dict:
    """
    Generate fix recommendations based on the diagnosed root cause.

    This function recommends code changes but does not execute them.
    """

    diagnosis = root_cause.get("root_cause", "Unknown")
    exception_type = error_analysis.get("exception_type")
    error_message = (
        error_analysis.get("message") or ""
    ).lower()

    result = {
        "problem": diagnosis,
        "suggested_code": None,
        "alternative_code": None,
        "explanation": None,
        "requires_manual_review": True,
        "status": "no_recommendation"
    }

    # ---------------------------------
    # Type Mismatch
    # ---------------------------------
    if diagnosis == "Type mismatch" or exception_type == "TypeError":
        variables = code_analysis.get("variables", {})

        has_type_mismatch = any(
            issue.get("type") == "TypeMismatch"
            for issue in code_analysis.get("potential_issues", [])
        )

        if (
            has_type_mismatch
            or "unsupported operand type(s)" in error_message
        ):
            result.update({
                "problem": (
                    "Incompatible types are used in an operation."
                ),
                "suggested_code": (
                    "# Convert values according to the intended operation."
                ),
                "alternative_code": None,
                "explanation": (
                    "The available evidence indicates a possible type "
                    "mismatch. Choose a correction based on the intended "
                    "result; converting to a string is appropriate only "
                    "when text concatenation is intended."
                ),
                "status": "review_required"
            })

            # Provide concrete examples only when the analyzed variables
            # match the known integer-plus-string pattern.
            if (
                variables.get("age") == "int"
                and variables.get("name") == "str"
            ):
                result["suggested_code"] = (
                    "result = str(age) + name"
                )
                result["alternative_code"] = (
                    'result = f"{name} is {age} years old."'
                )
                result["explanation"] = (
                    "Use str(age) + name if you want to concatenate "
                    "the values as text. Use an f-string if you want "
                    "to create a readable sentence. Select the fix "
                    "that matches the program's intended behavior."
                )

    # ---------------------------------
    # Syntax Error
    # ---------------------------------
    elif exception_type == "SyntaxError":
        result.update({
            "problem": "Invalid Python syntax.",
            "suggested_code": None,
            "alternative_code": None,
            "explanation": (
                "Inspect the reported line and syntax error message. "
                "The exact correction cannot be determined reliably "
                "without examining the source code and error location."
            ),
            "status": "review_required"
        })

    # ---------------------------------
    # Database Failure
    # ---------------------------------
    elif diagnosis == "Database failure":
        result.update({
            "problem": "Possible database connectivity failure.",
            "suggested_code": None,
            "alternative_code": None,
            "explanation": (
                "Check database availability, connection settings, "
                "network access, authentication, and database logs. "
                "The available evidence is insufficient to safely "
                "recommend a specific code change."
            ),
            "status": "review_required"
        })

    # ---------------------------------
    # Unknown Root Cause
    # ---------------------------------
    elif diagnosis == "Unknown":
        result.update({
            "problem": "Root cause could not be determined.",
            "explanation": (
                "Collect the full traceback, relevant source code, "
                "and logs before recommending a code change."
            ),
            "status": "insufficient_evidence"
        })

    return result