from flask import Flask, jsonify, send_from_directory

from aws_services import (
    get_ec2_instances,
    get_cpu_utilization,
    get_ec2_health,
    get_high_cpu_instances
)

from incidents import create_incident
from ai_analyzer import analyze_incident


app = Flask(__name__)

# Stores simulated incidents while Flask is running
demo_incidents = []


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():
    return send_from_directory("../frontend", "index.html")


# =========================================================
# EC2 INSTANCES
# =========================================================

@app.route("/api/ec2")
def ec2_instances():
    try:
        instances = get_ec2_instances()

        return jsonify({
            "status": "success",
            "instances": instances
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# =========================================================
# EC2 CPU
# =========================================================

@app.route("/api/ec2/<instance_id>/cpu")
def ec2_cpu(instance_id):
    try:
        cpu = get_cpu_utilization(instance_id)

        return jsonify({
            "status": "success",
            "data": cpu
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# =========================================================
# AWS HEALTH
# =========================================================

@app.route("/api/health")
def health():
    try:
        health_data = get_ec2_health()

        return jsonify({
            "status": "success",
            "data": health_data
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# =========================================================
# INCIDENT DETECTION
# =========================================================

@app.route("/api/incidents")
def incidents():

    try:

        # Get real AWS data
        health_data = get_ec2_health()
        high_cpu_instances = get_high_cpu_instances()

        incidents = []


        # -------------------------------------------------
        # Detect EC2 state problems
        # -------------------------------------------------

        for instance in health_data:

            if instance["status"] != "healthy":

                incident = create_incident(
                    service="EC2",
                    resource_id=instance["id"],
                    problem=f"EC2 instance is {instance['state']}",
                    severity="high"
                )

                incidents.append(incident)


        # -------------------------------------------------
        # Detect high CPU problems
        # -------------------------------------------------

        for instance in high_cpu_instances:

            incident = create_incident(
                service="CloudWatch",
                resource_id=instance["id"],
                problem=f"CPU utilization is {instance['cpu_utilization']}%",
                severity="high"
            )

            incident["evidence"] = {
                "cpu_utilization": instance["cpu_utilization"],
                "threshold": instance["threshold"]
            }

            incidents.append(incident)


        # -------------------------------------------------
        # Add simulated incidents
        # -------------------------------------------------

        incidents.extend(demo_incidents)


        # -------------------------------------------------
        # AI analysis
        # -------------------------------------------------

        for incident in incidents:

            if "ai_analysis" not in incident:

                incident["ai_analysis"] = analyze_incident(
                    incident
                )


        # -------------------------------------------------
        # Response
        # -------------------------------------------------

        return jsonify({

            "status": "success",

            "count": len(incidents),

            "incidents": incidents

        })


    except Exception as e:

        return jsonify({

            "status": "error",

            "message": str(e)

        }), 500


# =========================================================
# SIMULATE INCIDENT
# =========================================================

@app.route("/api/test-incident")
def test_incident():

    try:

        # Create simulated incident
        incident = create_incident(

            service="CloudWatch",

            resource_id="i-demo-cloudrescue",

            problem="CPU utilization is 94%",

            severity="high"

        )


        # Add monitoring evidence
        incident["evidence"] = {

            "cpu_utilization": 94,

            "threshold": 80,

            "source": "simulated CloudWatch event"

        }


        # Run AI analysis
        incident["ai_analysis"] = analyze_incident(
            incident
        )


        # Store the incident
        demo_incidents.append(incident)


        return jsonify({

            "status": "success",

            "incident": incident

        })


    except Exception as e:

        return jsonify({

            "status": "error",

            "message": str(e)

        }), 500


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(debug=True)