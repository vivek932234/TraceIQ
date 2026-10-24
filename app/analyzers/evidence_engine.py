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

    # ---------------------------------
    # Primary Error
    # ---------------------------------
    evidence["primary_error"] = {
        "type": error_analysis.get("exception_type"),
        "message": error_analysis.get("message"),
        "file": error_analysis.get("file"),
        "line": error_analysis.get("line"),
        "function": error_analysis.get("function")
    }

    exception_type = error_analysis.get("exception_type")

    # ---------------------------------
    # Static Code Evidence
    # ---------------------------------
    for issue in code_analysis.get("potential_issues", []):
        issue_type = issue.get("type")

        if exception_type == "TypeError" and issue_type == "TypeMismatch":
            evidence["supporting_evidence"].append({
                "source": "static_code_analysis",
                "type": issue_type,
                "line": issue.get("line"),
                "message": issue.get("message")
            })

    # ---------------------------------
    # Log Evidence
    # ---------------------------------
    for log in log_analysis.get("errors", []):
        category = log.get("category")

        entry = {
            "source": "application_logs",
            "timestamp": log.get("timestamp"),
            "level": log.get("level"),
            "message": log.get("message"),
            "category": category
        }

        # A generic HTTP 500 is not proof of a TypeError.
        # Without trace-ID or timestamp correlation, classify it
        # as unconfirmed rather than causally related.
        if exception_type == "TypeError":
            if category == "server_error":
                entry["relationship"] = "unconfirmed"
                evidence["unrelated_logs"].append(entry)
            else:
                entry["relationship"] = "unconfirmed"
                evidence["unrelated_logs"].append(entry)

        elif exception_type is None:
            # No primary exception exists to correlate against.
            entry["relationship"] = "unconfirmed"
            evidence["unrelated_logs"].append(entry)

        else:
            # The log is a possible lead, not confirmed causal evidence.
            entry["relationship"] = "unconfirmed"
            evidence["related_logs"].append(entry)

    # ---------------------------------
    # Observations
    # ---------------------------------
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
            "Application logs contain potential leads requiring correlation."
        )

    if evidence["unrelated_logs"]:
        evidence["observations"].append(
            "Log entries were found, but their causal relationship "
            "to the primary error has not been established."
        )

    return evidence