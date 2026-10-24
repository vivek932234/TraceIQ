from fastapi import FastAPI

from app.api.routes.debug import router as debug_router


app = FastAPI(
    title="TraceIQ",
    description="AI-Powered Debugging & Root-Cause Analysis Agent",
    version="0.1.0"
)


app.include_router(debug_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to TraceIQ",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }