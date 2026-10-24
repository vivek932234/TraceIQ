def build_evidence(
    error_analysis: dict,
    code_analysis: dict,
    log_analysis: dict
) -> dict:

    evidence = {
        "primary_error": {},
        "supporting_evidence": [],
        "related_logs": [],
        "unrelated_logs": [],
        "observations": []
    }

    # -----------------------------
    # Primary Error
    # -----------------------------
    evidence["primary_error"] = {
        "type": error_analysis.get("exception_type"),
        "message": error_analysis.get("message"),
        "file": error_analysis.get("file"),
        "line": error_analysis.get("line"),
        "function": error_analysis.get("function")
    }

    exception_type = error_analysis.get("exception_type")

    # -----------------------------
    # Code Evidence
    # -----------------------------
    for issue in code_analysis.get("potential_issues", []):

        if exception_type == "TypeError" and issue.get("type") == "TypeMismatch":

            evidence["supporting_evidence"].append({
                "source": "static_code_analysis",
                "type": issue.get("type"),
                "line": issue.get("line"),
                "message": issue.get("message")
            })

    # -----------------------------
    # Log Evidence
    # -----------------------------
    for log in log_analysis.get("errors", []):

        category = log.get("category")

        # Logs that directly support the current error
        if exception_type == "TypeError":
            if category == "server_error":
                evidence["related_logs"].append({
                    "source": "application_logs",
                    "timestamp": log.get("timestamp"),
                    "level": log.get("level"),
                    "message": log.get("message"),
                    "category": category
                })
            else:
                evidence["unrelated_logs"].append({
                    "source": "application_logs",
                    "timestamp": log.get("timestamp"),
                    "level": log.get("level"),
                    "message": log.get("message"),
                    "category": category
                })

        else:
            evidence["related_logs"].append({
                "source": "application_logs",
                "timestamp": log.get("timestamp"),
                "level": log.get("level"),
                "message": log.get("message"),
                "category": category
            })

    # -----------------------------
    # Observations
    # -----------------------------
    if exception_type:
        evidence["observations"].append(
            f"Application raised {exception_type}."
        )

    if evidence["supporting_evidence"]:
        evidence["observations"].append(
            "Static analysis found evidence supporting the primary error."
        )

    if evidence["related_logs"]:
        evidence["observations"].append(
            "Application logs contain entries related to the failure."
        )

    if evidence["unrelated_logs"]:
        evidence["observations"].append(
            "Some log entries were detected but do not directly support "
            "the identified root cause."
        )

    return evidence