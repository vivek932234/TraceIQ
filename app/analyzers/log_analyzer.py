import re


LOG_PATTERN = re.compile(
    r"(?P<timestamp>\S+\s+\S+)\s+"
    r"(?P<level>DEBUG|INFO|WARNING|ERROR|CRITICAL)\s+"
    r"(?P<message>.*)"
)

def classify_log_message(message: str) -> str:
    """
    Classify an error message into a broad category.
    """

    message_lower = message.lower()

    if any(word in message_lower for word in [
        "database",
        "sql",
        "postgres",
        "mysql",
        "connection refused"
    ]):
        return "database"

    if any(word in message_lower for word in [
        "timeout",
        "timed out"
    ]):
        return "timeout"

    if any(word in message_lower for word in [
        "authentication",
        "unauthorized",
        "invalid credentials"
    ]):
        return "authentication"

    if any(word in message_lower for word in [
        "permission denied",
        "forbidden"
    ]):
        return "permission"

    if any(word in message_lower for word in [
        "network",
        "connection"
    ]):
        return "network"

    if "500" in message_lower:
        return "server_error"

    return "general"

def analyze_logs(logs: str) -> dict:
    """
    Analyze application logs and extract
    structured debugging information.
    """

    result = {
        "total_entries": 0,
        "levels": {
            "DEBUG": 0,
            "INFO": 0,
            "WARNING": 0,
            "ERROR": 0,
            "CRITICAL": 0
        },
        "entries": [],
        "errors": [],
        "warnings": []
    }

    if not logs:
        return result

    for line in logs.splitlines():

        line = line.strip()

        if not line:
            continue

        match = LOG_PATTERN.match(line)

        if not match:
            continue

        timestamp = match.group("timestamp")
        level = match.group("level")
        message = match.group("message")

        category = classify_log_message(message)

        entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message,
            "category": category
        }

        result["entries"].append(entry)

        result["total_entries"] += 1

        result["levels"][level] += 1

        if level in ["ERROR", "CRITICAL"]:
            result["errors"].append(entry)

        elif level == "WARNING":
            result["warnings"].append(entry)

    return result