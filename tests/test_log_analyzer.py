from app.analyzers.log_analyzer import analyze_logs


def test_detects_database_errors():
    logs = """
2026-10-24 10:00:00 INFO Application started
2026-10-24 10:01:00 ERROR Database connection failed
2026-10-24 10:01:01 ERROR Connection refused
"""

    result = analyze_logs(logs)

    assert result["total_entries"] == 3
    assert result["levels"]["INFO"] == 1
    assert result["levels"]["ERROR"] == 2

    assert any(
        entry["category"] == "database"
        for entry in result["errors"]
    )


def test_detects_warnings():
    logs = """
2026-10-24 10:00:00 WARNING Disk usage is high
"""

    result = analyze_logs(logs)

    assert result["levels"]["WARNING"] == 1
    assert len(result["warnings"]) == 1


def test_empty_logs():
    result = analyze_logs("")

    assert result["total_entries"] == 0
    assert result["errors"] == []
    assert result["warnings"] == []