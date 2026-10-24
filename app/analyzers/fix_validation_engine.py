
import ast


def validate_fix(
    original_code: str,
    suggested_code: str,
    root_cause: dict
) -> dict:
    """
    Perform conservative static validation of a proposed Python fix.

    This function checks syntax and compares simple integer-plus-string
    operations. It does not execute code or guarantee correctness.
    """

    result = {
        "valid_syntax": False,
        "issue_resolved": False,
        "validation_status": "not_validated",
        "checks": [],
        "warnings": [],
    }

    if not suggested_code or not suggested_code.strip():
        result["validation_status"] = "rejected"
        result["warnings"].append(
            "No suggested code was provided."
        )
        return result

    # Check 1: Validate suggested Python syntax.
    try:
        suggested_tree = ast.parse(suggested_code)
        result["valid_syntax"] = True

        result["checks"].append({
            "name": "python_syntax",
            "passed": True,
            "message": "Suggested code has valid Python syntax."
        })

    except SyntaxError as error:
        result["validation_status"] = "rejected"

        result["checks"].append({
            "name": "python_syntax",
            "passed": False,
            "message": error.msg,
            "line": error.lineno
        })

        result["warnings"].append(
            "Fix the syntax error before considering this suggestion."
        )
        return result

    # Check 2: Determine whether this root-cause type is supported.
    cause = root_cause.get("root_cause", "Unknown")

    if cause != "Type mismatch":
        result["validation_status"] = "inconclusive"
        result["warnings"].append(
            "Automatic validation is not implemented for this root-cause category."
        )
        result["warnings"].append(
            "Static checks do not prove runtime correctness. "
            "Review and test the proposed fix."
        )
        return result

    # Check 3: Analyze the original source.
    try:
        original_tree = ast.parse(original_code or "")
    except SyntaxError:
        result["validation_status"] = "inconclusive"
        result["warnings"].append(
            "Original code has invalid syntax, so the issue could not "
            "be compared reliably."
        )
        return result

    original_has_mismatch = _has_int_string_addition(
        original_tree
    )

    if not original_has_mismatch:
        result["validation_status"] = "inconclusive"
        result["warnings"].append(
            "The original code does not contain the supported "
            "integer-plus-string pattern. Additional analysis is required."
        )
        return result

    # Check 4: Recognize only supported, explicit corrections.
    #
    # A replacement statement such as:
    #     result = str(age) + name
    # can be checked against the original source's variable types.
    #
    # We do not execute the suggested code.
    original_types = _get_variable_types(original_tree)

    if _suggestion_fixes_mismatch(
        suggested_tree,
        original_types
    ):
        result["issue_resolved"] = True
        result["validation_status"] = "passed"

        result["checks"].append({
            "name": "type_mismatch_check",
            "passed": True,
            "message": (
                "The suggestion uses an explicit conversion for the "
                "detected integer-plus-string pattern."
            )
        })
    else:
        result["issue_resolved"] = False
        result["validation_status"] = "inconclusive"

        result["checks"].append({
            "name": "type_mismatch_check",
            "passed": False,
            "message": (
                "The validator could not confirm that the suggestion "
                "corrects the detected integer-plus-string pattern."
            )
        })

        result["warnings"].append(
            "The suggested code may still be appropriate, but it needs "
            "manual review because the supported static checks could not "
            "verify the correction."
        )

    result["warnings"].append(
        "Static validation does not prove runtime correctness or "
        "preserve intended behavior. Review and test the fix."
    )

    return result


def _get_variable_types(tree: ast.AST) -> dict:
    """Collect basic types from simple literal assignments."""

    variable_types = {}

    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue

        if not isinstance(node.value, ast.Constant):
            continue

        value = node.value.value

        if isinstance(value, bool):
            value_type = "bool"
        elif isinstance(value, int):
            value_type = "int"
        elif isinstance(value, str):
            value_type = "str"
        else:
            continue

        for target in node.targets:
            if isinstance(target, ast.Name):
                variable_types[target.id] = value_type

    return variable_types


def _has_int_string_addition(tree: ast.AST) -> bool:
    """Detect simple additions between variables assigned int and str."""

    variable_types = _get_variable_types(tree)

    for node in ast.walk(tree):
        if not isinstance(node, ast.BinOp):
            continue

        if not isinstance(node.op, ast.Add):
            continue

        if not isinstance(node.left, ast.Name):
            continue

        if not isinstance(node.right, ast.Name):
            continue

        left_type = variable_types.get(node.left.id)
        right_type = variable_types.get(node.right.id)

        if {left_type, right_type} == {"int", "str"}:
            return True

    return False


def _suggestion_fixes_mismatch(
    suggested_tree: ast.AST,
    original_types: dict
) -> bool:
    """
    Confirm a narrow set of explicit fixes for a known int + str issue.

    Examples:
        str(age) + name
        name + str(age)

    This is a limited syntax-pattern check, not proof of correctness.
    """

    for node in ast.walk(suggested_tree):
        if not isinstance(node, ast.BinOp):
            continue

        if not isinstance(node.op, ast.Add):
            continue

        left = node.left
        right = node.right

        # str(age) + name
        if (
            isinstance(left, ast.Call)
            and isinstance(left.func, ast.Name)
            and left.func.id == "str"
            and len(left.args) == 1
            and isinstance(left.args[0], ast.Name)
            and isinstance(right, ast.Name)
        ):
            converted_variable = left.args[0].id
            other_variable = right.id

            if (
                original_types.get(converted_variable) == "int"
                and original_types.get(other_variable) == "str"
            ):
                return True

        # name + str(age)
        if (
            isinstance(right, ast.Call)
            and isinstance(right.func, ast.Name)
            and right.func.id == "str"
            and len(right.args) == 1
            and isinstance(right.args[0], ast.Name)
            and isinstance(left, ast.Name)
        ):
            converted_variable = right.args[0].id
            other_variable = left.id

            if (
                original_types.get(converted_variable) == "int"
                and original_types.get(other_variable) == "str"
            ):
                return True

    return False