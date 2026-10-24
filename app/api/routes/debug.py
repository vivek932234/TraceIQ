
from fastapi import APIRouter

from app.models.schemas import DebugRequest

from app.analyzers.error_analyzer import analyze_error
from app.analyzers.code_analyzer import analyze_code
from app.analyzers.log_analyzer import analyze_logs
from app.analyzers.evidence_engine import build_evidence
from app.analyzers.root_cause_engine import calculate_root_cause
from app.analyzers.fix_recommendation_engine import (
    generate_fix_recommendation,
)
from app.analyzers.fix_validation_engine import validate_fix

from app.ai.debugging_agent import debug_with_ai


router = APIRouter(
    prefix="/api/v1",
    tags=["Debugging"]
)


@router.post("/debug")
def debug_application(request: DebugRequest):

    # Step 1: Analyze the error
    error_analysis = analyze_error(
        request.error
    )

    # Step 2: Analyze the source code
    code_analysis = analyze_code(
        request.code or ""
    )

    # Step 3: Analyze application logs
    log_analysis = analyze_logs(
        request.logs or ""
    )

    # Step 4: Build supporting evidence
    evidence = build_evidence(
        error_analysis,
        code_analysis,
        log_analysis
    )

    # Step 5: Identify the likely root cause
    root_cause = calculate_root_cause(
        evidence
    )

    # Step 6: Recommend a possible fix
    fix_recommendation = generate_fix_recommendation(
        root_cause=root_cause,
        error_analysis=error_analysis,
        code_analysis=code_analysis,
    )

    # Step 7: Validate the proposed fix using static checks
    fix_validation = validate_fix(
        original_code=request.code or "",
        suggested_code=(
            fix_recommendation.get("suggested_code") or ""
        ),
        root_cause=root_cause,
    )

    # Step 8: Generate AI-assisted analysis
    ai_analysis = debug_with_ai(
        evidence=evidence,
        code=request.code or "",
        logs=request.logs or "",
        root_cause=root_cause
    )

    # Step 9: Return the complete debugging report
    return {
        "message": "Debug request analyzed",
        "error_analysis": error_analysis,
        "code_analysis": code_analysis,
        "log_analysis": log_analysis,
        "evidence": evidence,
        "root_cause": root_cause,
        "fix_recommendation": fix_recommendation,
        "fix_validation": fix_validation,
        "ai_analysis": ai_analysis,
    }
