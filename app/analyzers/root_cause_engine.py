def calculate_root_cause(evidence: dict) -> dict:
    candidates = []

    primary_error = evidence.get("primary_error") or {}
    supporting_evidence = evidence.get("supporting_evidence", [])
    related_logs = evidence.get("related_logs", [])
    unrelated_logs = evidence.get("unrelated_logs", [])

    exception_type = primary_error.get("type")
    error_message = (primary_error.get("message") or "").lower()

    # ---------------------------------
    # Candidate 1: Type Mismatch
    # ---------------------------------
    type_score = 0
    type_evidence = []

    if exception_type == "TypeError":
        type_score += 40
        type_evidence.append({
            "source": "traceback",
            "message": "Runtime TypeError detected."
        })

    matching_type_issues = [
        item
        for item in supporting_evidence
        if item.get("type") == "TypeMismatch"
    ]

    if matching_type_issues:
        type_score += 35

        for issue in matching_type_issues:
            type_evidence.append({
                "source": issue.get(
                    "source",
                    "static_code_analysis"
                ),
                "line": issue.get("line"),
                "message": issue.get("message")
                or "Static analysis detected a type mismatch."
            })

    # Award corroboration points only when both signals exist.
    if exception_type == "TypeError" and matching_type_issues:
        type_score += 15

        type_evidence.append({
            "source": "correlation",
            "message": (
                "Runtime TypeError and static type-mismatch "
                "evidence support the same candidate."
            )
        })

    # ---------------------------------
    # Candidate 2: Database Failure
    # ---------------------------------
    database_score = 0
    database_evidence = []

    for log in related_logs + unrelated_logs:
        if log.get("category") != "database":
            continue

        message = log.get("message") or ""

        database_score = max(database_score, 20)

        database_evidence.append({
            "source": log.get(
                "source",
                "application_logs"
            ),
            "timestamp": log.get("timestamp"),
            "message": message,
            "relationship": (
                "related"
                if log in related_logs
                else "unconfirmed"
            )
        })

    # Do not claim that a database log caused a TypeError.
    if exception_type == "TypeError" and database_evidence:
        for item in database_evidence:
            item["relationship"] = "unconfirmed"
            item["note"] = (
                "Database log detected, but no direct causal "
                "connection to the TypeError has been established."
            )

    candidates.append({
        "root_cause": "Type mismatch",
        "score": type_score,
        "evidence": type_evidence
    })

    candidates.append({
        "root_cause": "Database failure",
        "score": database_score,
        "evidence": database_evidence
    })

    # ---------------------------------
    # Rank Candidates
    # ---------------------------------
    candidates.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    best = candidates[0]

    # A zero-score candidate is not a confirmed diagnosis.
    if best["score"] == 0:
        root_cause = "Unknown"
        confidence = "Low"
    else:
        root_cause = best["root_cause"]

        if best["score"] >= 70:
            confidence = "High"
        elif best["score"] >= 40:
            confidence = "Medium"
        else:
            confidence = "Low"

    return {
        "root_cause": root_cause,
        "score": best["score"],
        "confidence": confidence,
        "evidence_count": len(best["evidence"]),
        "evidence": best["evidence"],
        "candidates": candidates
    }