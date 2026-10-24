from pydantic import BaseModel


class DebugRequest(BaseModel):
    error: str
    code: str | None = None
    logs: str | None = None