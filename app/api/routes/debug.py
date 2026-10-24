from fastapi import APIRouter

from app.models.schemas import DebugRequest
from app.analyzers.error_analyzer import analyze_error
from app.analyzers.code_analyzer import analyze_code
from app.analyzers.log_analyzer import analyze_logs
from app.analyzers.evidence_engine import build_evidence
from app.ai.debugging_agent import debug_with_ai
from app.analyzers.root_cause_engine import calculate_root_cause

router = APIRouter(
    prefix="/api/v1",
    tags=["Debugging"]
)


@router.post("/debug")
def debug_application(request: DebugRequest):

    error_analysis = analyze_error(
        request.error
    )

    code_analysis = analyze_code(
        request.code or ""
    )

    log_analysis = analyze_logs(
        request.logs or ""
    )
    evidence = build_evidence(
    error_analysis,
    code_analysis,
    log_analysis
)
    root_cause = calculate_root_cause(evidence)
    
    ai_analysis = debug_with_ai(
    evidence=evidence,
    code=request.code or "",
    logs=request.logs or "",
    root_cause=root_cause
)

    return {
    "message": "Debug request analyzed",
    "error_analysis": error_analysis,
    "code_analysis": code_analysis,
    "log_analysis": log_analysis,
    "evidence": evidence,
    "root_cause": root_cause,
    "ai_analysis": ai_analysis
}