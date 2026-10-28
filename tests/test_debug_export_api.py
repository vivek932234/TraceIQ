
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.debug_history import DebugHistory


test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)

Base.metadata.create_all(bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

client = TestClient(app)


@pytest.fixture(autouse=True)
def isolate_history_database():
    previous_override = app.dependency_overrides.get(get_db)

    app.dependency_overrides[get_db] = override_get_db

    try:
        yield
    finally:
        if previous_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous_override


def setup_function():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)




def test_export_debug_history_as_json():
    db = TestingSessionLocal()
    try:
        record = DebugHistory(
            error_message="Example TypeError",
            exception_type="TypeError",
            root_cause="Type mismatch",
            confidence="High",
            fix_recommendation={"suggested_code": "result = str(age) + name"},
            fix_validation={"validation_status": "passed"},
            ai_analysis={"status": "success"},
            created_at=datetime.now(timezone.utc),
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        record_id = record.id
    finally:
        db.close()

    response = client.get(
        f"/api/v1/debug/history/{record_id}/export"
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "application/json"
    )
    assert f"traceiq_report_{record_id}.json" in response.headers[
        "content-disposition"
    ]

    report = response.json()
    assert report["id"] == record_id
    assert report["error_message"] == "Example TypeError"
    assert report["fix_recommendation"]["suggested_code"] == (
        "result = str(age) + name"
    )


def test_export_missing_debug_history_returns_404():
    response = client.get(
        "/api/v1/debug/history/999999/export"
    )

    assert response.status_code == 404
