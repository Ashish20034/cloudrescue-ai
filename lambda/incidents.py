from datetime import datetime


def create_incident(
    service,
    resource_id,
    problem,
    severity
):
    return {
        "id": (
            f"INC-"
            f"{datetime.now().strftime('%Y%m%d%H%M%S')}"
        ),
        "service": service,
        "resource_id": resource_id,
        "problem": problem,
        "severity": severity,
        "status": "open",
        "created_at": datetime.now().isoformat()
    }