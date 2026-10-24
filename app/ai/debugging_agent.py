import os
import json

from dotenv import load_dotenv
from google import genai


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key) if api_key else None


def build_debugging_prompt(
    evidence: dict,
    code: str = "",
    logs: str = "",
    root_cause: dict | None = None
) -> str:

    return f"""
You are TraceIQ, an AI-powered debugging and root-cause analysis agent.

Analyze the supplied evidence carefully.

PRIMARY EVIDENCE:
{json.dumps(evidence, indent=2)}

ROOT-CAUSE SCORES:
{json.dumps(root_cause or {}, indent=2)}

SOURCE CODE:
{code}

APPLICATION LOGS:
{logs}

Requirements:
1. Identify the most likely root cause.
2. Explain why it occurred.
3. Cite evidence from the supplied information.
4. Recommend a practical fix.
5. Do not treat unrelated logs as proof of the root cause.
6. Do not invent information that is not provided.
7. If the evidence is insufficient, say so.

Return valid JSON with these keys:
{{
    "root_cause": "",
    "why_it_happened": "",
    "evidence": [],
    "suggested_fix": "",
    "confidence": "High, Medium, or Low"
}}
"""


def build_fallback_analysis(
    evidence: dict,
    root_cause: dict
) -> dict:

    primary_error = evidence.get("primary_error", {})

    exception_type = primary_error.get("type")
    error_message = primary_error.get("message")

    root_cause_name = root_cause.get("root_cause", "Unknown")

    evidence_items = []

    if exception_type:
        evidence_items.append(
            f"Runtime exception detected: {exception_type}."
        )

    for item in evidence.get("supporting_evidence", []):
        message = item.get("message")

        if message:
            evidence_items.append(message)

    for item in root_cause.get("evidence", []):
        if item not in evidence_items:
            evidence_items.append(item)

    if root_cause_name == "Type mismatch":
        explanation = (
            "The code appears to perform an operation using "
            "incompatible data types."
        )

        suggested_fix = (
            "Inspect the reported operation and convert the operands "
            "to compatible types if appropriate."
        )

    elif root_cause_name == "Database failure":
        explanation = (
            "Application logs indicate a database-related failure. "
            "The logs alone may not establish its exact underlying cause."
        )

        suggested_fix = (
            "Verify database availability, connection settings, "
            "credentials, and network connectivity."
        )

    else:
        explanation = (
            f"TraceIQ identified '{root_cause_name}' as the leading "
            "candidate based on the available evidence."
        )

        suggested_fix = (
            "Inspect the relevant source code, error details, "
            "and runtime logs to verify the suspected cause."
        )

    if error_message:
        evidence_items.append(f"Runtime error message: {error_message}")

    return {
        "root_cause": root_cause_name,
        "why_it_happened": explanation,
        "evidence": evidence_items,
        "suggested_fix": suggested_fix,
        "confidence": root_cause.get("confidence", "Low")
    }


def debug_with_ai(
    evidence: dict,
    code: str = "",
    logs: str = "",
    root_cause: dict | None = None
) -> dict:

    root_cause = root_cause or {}

    if client is None:
        return {
            "status": "fallback",
            "analysis": build_fallback_analysis(
                evidence=evidence,
                root_cause=root_cause
            ),
            "llm_error": "GEMINI_API_KEY is not configured."
        }

    prompt = build_debugging_prompt(
        evidence=evidence,
        code=code,
        logs=logs,
        root_cause=root_cause
    )

    try:
        response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents=prompt,
    config={
        "response_mime_type": "application/json"
    }
)

        analysis_text = response.text

        if not analysis_text:
            raise ValueError("Gemini returned an empty response.")

        analysis = json.loads(analysis_text)

        return {
            "status": "success",
            "analysis": analysis
        }

    except Exception as error:
        return {
            "status": "fallback",
            "analysis": build_fallback_analysis(
                evidence=evidence,
                root_cause=root_cause
            ),
            "llm_error": str(error)
        }