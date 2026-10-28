
from datetime import datetime, timezone

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


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)


def teardown_module():
    app.dependency_overrides.pop(get_db, None)


def test_get_debug_history_empty():
    response = client.get("/api/v1/debug/history")

    assert response.status_code == 200
    assert response.json()["total"] == 0
    assert response.json()["history"] == []


def test_get_debug_history_returns_saved_record():
    db = TestingSessionLocal()
    try:
        record = DebugHistory(
            error_message="Example TypeError",
            exception_type="TypeError",
            root_cause="Type mismatch",
            confidence="High",
            fix_recommendation={"suggested_code": "str(age)"},
            fix_validation={"validation_status": "passed"},
            ai_analysis={"status": "success"},
            created_at=datetime.now(timezone.utc),
        )
        db.add(record)
        db.commit()
    finally:
        db.close()

    response = client.get("/api/v1/debug/history")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["history"][0]["error_message"] == "Example TypeError"


def test_get_debug_history_by_id():
    db = TestingSessionLocal()
    try:
        record = DebugHistory(
            error_message="Example TypeError",
            exception_type="TypeError",
            root_cause="Type mismatch",
            confidence="High",
            created_at=datetime.now(timezone.utc),
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        record_id = record.id
    finally:
        db.close()

    response = client.get(f"/api/v1/debug/history/{record_id}")

    assert response.status_code == 200
    assert response.json()["id"] == record_id
    assert response.json()["root_cause"] == "Type mismatch"


def test_get_missing_debug_history_returns_404():
    response = client.get("/api/v1/debug/history/999999")

    assert response.status_code == 404
