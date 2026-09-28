import json

from aws_services import (
    get_ec2_instances,
    get_ec2_health,
    get_high_cpu_instances,
    get_cpu_utilization
)

from incidents import create_incident
from ai_analyzer import analyze_incident


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(
            body,
            default=str
        )
    }


def lambda_handler(event, context):

    path = event.get(
        "rawPath",
        "/"
    )

    try:

        # -------------------------
        # Health
        # -------------------------

        if path == "/api/health":

            data = get_ec2_health()

            return response(
                200,
                {
                    "status": "success",
                    "data": data
                }
            )

        # -------------------------
        # EC2 CPU
        # -------------------------

        if path.startswith("/api/ec2/") and path.endswith("/cpu"):

            parts = path.strip("/").split("/")

            instance_id = parts[2]

            cpu = get_cpu_utilization(
                instance_id
            )

            return response(
                200,
                {
                    "status": "success",
                    "instance_id": instance_id,
                    "cpu_utilization": cpu
                }
            )

        # -------------------------
        # EC2
        # -------------------------

        if path == "/api/ec2":

            data = get_ec2_instances()

            return response(
                200,
                {
                    "status": "success",
                    "instances": data
                }
            )

        # -------------------------
        # Test Incident
        # -------------------------

        if path == "/api/test-incident":

            incident = create_incident(
                service="CloudWatch",
                resource_id="i-demo-cloudrescue",
                problem="CPU utilization is 94%",
                severity="high"
            )

            incident["evidence"] = {
                "cpu_utilization": 94,
                "threshold": 80,
                "source": "simulated CloudWatch event"
            }

            incident["ai_analysis"] = analyze_incident(
                incident
            )

            return response(
                200,
                {
                    "status": "success",
                    "incident": incident
                }
            )

        # -------------------------
        # Incidents
        # -------------------------

        if path == "/api/incidents":

            health_data = get_ec2_health()

            high_cpu_instances = (
                get_high_cpu_instances()
            )

            incidents = []

            # -------------------------
            # EC2 State Incidents
            # -------------------------

            for instance in health_data:

                if (
                    instance["status"] != "healthy"
                    and instance["state"] != "terminated"
                ):

                    incident = create_incident(
                        service="EC2",
                        resource_id=instance["id"],
                        problem=(
                            f"EC2 instance is "
                            f"{instance['state']}"
                        ),
                        severity="high"
                    )

                    incidents.append(
                        incident
                    )

            # -------------------------
            # High CPU Incidents
            # -------------------------

            for instance in high_cpu_instances:

                incident = create_incident(
                    service="CloudWatch",
                    resource_id=instance["id"],
                    problem=(
                        f"CPU utilization is "
                        f"{instance['cpu_utilization']}%"
                    ),
                    severity="high"
                )

                incident["evidence"] = {
                    "cpu_utilization":
                        instance["cpu_utilization"],
                    "threshold":
                        instance["threshold"]
                }

                incidents.append(
                    incident
                )

            # -------------------------
            # AI Analysis
            # -------------------------

            for incident in incidents:

                incident["ai_analysis"] = (
                    analyze_incident(
                        incident
                    )
                )

            return response(
                200,
                {
                    "status": "success",
                    "count": len(incidents),
                    "incidents": incidents
                }
            )

        # -------------------------
        # Route Not Found
        # -------------------------

        return response(
            404,
            {
                "status": "error",
                "message": "Route not found"
            }
        )

    except Exception as e:

        return response(
            500,
            {
                "status": "error",
                "message": str(e)
            }
        )