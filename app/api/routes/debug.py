import json

from fastapi.encoders import jsonable_encoder
from fastapi.responses import Response


from app.models.schemas import DebugRequest
from fastapi import APIRouter, Depends, HTTPException

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
from sqlalchemy.orm import Session


from app.database import get_db
from app.models.debug_history import DebugHistory


router = APIRouter(
    prefix="/api/v1",
    tags=["Debugging"]
)


@router.post("/debug")
def debug_application(
    request: DebugRequest,
    db: Session = Depends(get_db),
):

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
    history_record = DebugHistory(
        error_message=(
            error_analysis.get("message")
            or request.error
            or "Unknown error"
        ),
        exception_type=error_analysis.get("exception_type"),
        root_cause=root_cause.get("root_cause", "Unknown"),
        confidence=root_cause.get("confidence"),
        fix_recommendation=fix_recommendation,
        fix_validation=fix_validation,
        ai_analysis=ai_analysis,
    )

    try:
        db.add(history_record)
        db.commit()
        db.refresh(history_record)
    except Exception:
        db.rollback()
        raise

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
        "history_id": history_record.id,
    }



@router.get("/debug/history")
def get_debug_history(
    db: Session = Depends(get_db),
):
    records = (
        db.query(DebugHistory)
        .order_by(
            DebugHistory.created_at.desc(),
            DebugHistory.id.desc(),
        )
        .limit(100)
        .all()
    )

    return {
        "total": len(records),
        "history": [
            {
                "id": record.id,
                "error_message": record.error_message,
                "exception_type": record.exception_type,
                "root_cause": record.root_cause,
                "confidence": record.confidence,
                "created_at": record.created_at,
            }
            for record in records
        ],
    }


@router.get("/debug/history/{history_id}")
def get_debug_history_by_id(
    history_id: int,
    db: Session = Depends(get_db),
):
    record = (
        db.query(DebugHistory)
        .filter(DebugHistory.id == history_id)
        .first()
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"Debug history record {history_id} not found",
        )

    return {
        "id": record.id,
        "error_message": record.error_message,
        "exception_type": record.exception_type,
        "root_cause": record.root_cause,
        "confidence": record.confidence,
        "fix_recommendation": record.fix_recommendation,
        "fix_validation": record.fix_validation,
        "ai_analysis": record.ai_analysis,
        "created_at": record.created_at,
    }


@router.get("/debug/history/{history_id}/export")
def export_debug_history(
    history_id: int,
    db: Session = Depends(get_db),
):
    record = (
        db.query(DebugHistory)
        .filter(DebugHistory.id == history_id)
        .first()
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail=f"Debug history record {history_id} not found",
        )

    report = {
        "id": record.id,
        "error_message": record.error_message,
        "exception_type": record.exception_type,
        "root_cause": record.root_cause,
        "confidence": record.confidence,
        "fix_recommendation": record.fix_recommendation,
        "fix_validation": record.fix_validation,
        "ai_analysis": record.ai_analysis,
        "created_at": record.created_at,
    }

    json_content = json.dumps(
        jsonable_encoder(report),
        indent=2,
        ensure_ascii=False,
    )

    return Response(
        content=json_content,
        media_type="application/json",
        headers={
            "Content-Disposition": (
                f'attachment; filename="traceiq_report_{record.id}.json"'
            )
        },
    )
