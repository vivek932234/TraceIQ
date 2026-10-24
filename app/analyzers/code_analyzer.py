import ast


def get_value_type(value):
    """
    Identify the basic Python type of a literal value.
    """

    if isinstance(value, ast.Constant):
        return type(value.value).__name__

    if isinstance(value, ast.List):
        return "list"

    if isinstance(value, ast.Tuple):
        return "tuple"

    if isinstance(value, ast.Set):
        return "set"

    if isinstance(value, ast.Dict):
        return "dict"

    return "unknown"


def infer_expression_type(node, variables):
    """
    Infer the resulting type of a Python expression.
    """

    # Literal value
    if isinstance(node, ast.Constant):
        return type(node.value).__name__

    # Variable reference
    if isinstance(node, ast.Name):
        return variables.get(node.id, "unknown")

    # List
    if isinstance(node, ast.List):
        return "list"

    # Tuple
    if isinstance(node, ast.Tuple):
        return "tuple"

    # Dictionary
    if isinstance(node, ast.Dict):
        return "dict"

    # Binary operation
    if isinstance(node, ast.BinOp):

        left_type = infer_expression_type(
            node.left,
            variables
        )

        right_type = infer_expression_type(
            node.right,
            variables
        )

        # Addition
        if isinstance(node.op, ast.Add):

            if left_type == "int" and right_type == "int":
                return "int"

            if left_type == "float" and right_type == "float":
                return "float"

            if left_type == "str" and right_type == "str":
                return "str"

        # Subtraction
        if isinstance(node.op, ast.Sub):

            if left_type in ["int", "float"] and right_type in ["int", "float"]:
                return "float" if "float" in [left_type, right_type] else "int"

        # Multiplication
        if isinstance(node.op, ast.Mult):

            if left_type == "int" and right_type == "int":
                return "int"

            if left_type == "str" and right_type == "int":
                return "str"

            if left_type == "int" and right_type == "str":
                return "str"

        return "unknown"

    return "unknown"


def analyze_code(code: str) -> dict:
    """
    Analyze Python source code using the AST module.
    """

    result = {
        "valid_python": True,
        "variables": {},
        "functions": [],
        "imports": [],
        "operations": [],
        "potential_issues": []
    }

    if not code:
        return result

    # --------------------------------
    # Parse Python source code
    # --------------------------------

    try:
        tree = ast.parse(code)

    except SyntaxError as error:

        result["valid_python"] = False

        result["syntax_error"] = {
            "message": error.msg,
            "line": error.lineno,
            "offset": error.offset
        }

        return result

    # --------------------------------
    # First pass:
    # Collect variables, functions,
    # and imports
    # --------------------------------

    for node in ast.walk(tree):

        # Variables
        if isinstance(node, ast.Assign):

            value_type = infer_expression_type(
                node.value,
                result["variables"]
            )

            for target in node.targets:

                if isinstance(target, ast.Name):

                    result["variables"][target.id] = value_type

        # Functions
        elif isinstance(node, ast.FunctionDef):

            result["functions"].append(node.name)

        # Imports
        elif isinstance(node, ast.Import):

            for alias in node.names:
                result["imports"].append(alias.name)

        elif isinstance(node, ast.ImportFrom):

            for alias in node.names:

                result["imports"].append(
                    f"{node.module}.{alias.name}"
                )

    # --------------------------------
    # Second pass:
    # Analyze binary operations
    # --------------------------------

    for node in ast.walk(tree):

        if isinstance(node, ast.BinOp):

            operation = type(node.op).__name__

            left_type = infer_expression_type(
                node.left,
                result["variables"]
            )

            right_type = infer_expression_type(
                node.right,
                result["variables"]
            )

            operation_data = {
                "operation": operation,
                "line": node.lineno,
                "left_type": left_type,
                "right_type": right_type
            }

            result["operations"].append(
                operation_data
            )

            # Detect int + str
            if operation == "Add":

                if {
                    left_type,
                    right_type
                } == {"int", "str"}:

                    result["potential_issues"].append(
                        {
                            "type": "TypeMismatch",
                            "line": node.lineno,
                            "message": (
                                "Possible TypeError: "
                                "integer and string are being added."
                            )
                        }
                    )

    return result