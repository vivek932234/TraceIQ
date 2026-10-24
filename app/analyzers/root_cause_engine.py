def calculate_root_cause(evidence: dict) -> dict:

    candidates = []

    # -----------------------------
    # Type Mismatch
    # -----------------------------
    type_score = 0
    type_evidence = []

    primary_error = evidence.get("primary_error", {})

    if primary_error.get("type") == "TypeError":
        type_score += 40
        type_evidence.append(
            "Runtime TypeError detected."
        )

    for item in evidence.get("supporting_evidence", []):

        if item.get("type") == "TypeMismatch":
            type_score += 35

            type_evidence.append(
                "Static code analysis detected a type mismatch."
            )

    if type_evidence:
        type_score += 15
        type_evidence.append(
            "Static analysis supports the runtime error."
        )

    candidates.append({
        "root_cause": "Type mismatch",
        "score": type_score,
        "evidence": type_evidence
    })

    # -----------------------------
    # Database / Network Failure
    # -----------------------------
    database_score = 0
    database_evidence = []

    for log in evidence.get("unrelated_logs", []):

        if log.get("category") == "database":
            database_score += 20

            database_evidence.append(
                f"Database error detected: {log.get('message')}"
            )

    candidates.append({
        "root_cause": "Database failure",
        "score": database_score,
        "evidence": database_evidence
    })

    # -----------------------------
    # Rank Candidates
    # -----------------------------
    candidates.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    best = candidates[0]

    if best["score"] >= 70:
        confidence = "High"
    elif best["score"] >= 40:
        confidence = "Medium"
    else:
        confidence = "Low"

    return {
        "root_cause": best["root_cause"],
        "score": best["score"],
        "confidence": confidence,
        "evidence_count": len(best["evidence"]),
        "evidence": best["evidence"],
        "candidates": candidates
    }