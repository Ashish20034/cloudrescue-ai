def analyze_incident(incident):

    problem = incident.get(
        "problem",
        ""
    ).lower()

    service = incident.get(
        "service",
        ""
    )

    if "cpu utilization" in problem:

        return {
            "analysis_status": "fallback",

            "root_cause": (
                "Possible CPU saturation caused "
                "by a resource-intensive workload."
            ),

            "evidence": [
                incident.get("problem")
            ],

            "recommendation": [
                "Inspect running processes on the EC2 instance.",
                "Check application and system logs.",
                "Review CloudWatch CPU metrics over a longer period.",
                "Scale the workload if high CPU usage persists."
            ],

            "risk": "medium"
        }

    if (
        service == "EC2"
        and "stopped" in problem
    ):

        return {
            "analysis_status": "fallback",

            "root_cause": (
                "The EC2 instance is currently stopped."
            ),

            "evidence": [
                incident.get("problem")
            ],

            "recommendation": [
                "Check whether the instance was intentionally stopped.",
                "Review CloudTrail events for recent stop actions.",
                "Start the instance only after confirming it is required."
            ],

            "risk": "high"
        }

    return {
        "analysis_status": "fallback",

        "root_cause": (
            "The incident requires additional investigation."
        ),

        "evidence": [
            incident.get("problem")
        ],

        "recommendation": [
            "Review CloudWatch metrics.",
            "Inspect application and system logs.",
            "Check recent infrastructure changes."
        ],

        "risk": "medium"
    }