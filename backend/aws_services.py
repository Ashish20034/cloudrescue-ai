import boto3
from datetime import datetime, timedelta, timezone


AWS_REGION = "us-east-1"


def get_ec2_instances():
    ec2 = boto3.client(
        "ec2",
        region_name=AWS_REGION
    )

    response = ec2.describe_instances()

    instances = []

    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instances.append({
                "id": instance["InstanceId"],
                "state": instance["State"]["Name"],
                "type": instance["InstanceType"]
            })

    return instances


def get_cpu_utilization(instance_id):
    cloudwatch = boto3.client(
        "cloudwatch",
        region_name=AWS_REGION
    )

    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(minutes=30)

    response = cloudwatch.get_metric_statistics(
        Namespace="AWS/EC2",
        MetricName="CPUUtilization",
        Dimensions=[
            {
                "Name": "InstanceId",
                "Value": instance_id
            }
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=300,
        Statistics=["Average"]
    )

    datapoints = response["Datapoints"]

    if not datapoints:
        return {
            "instance_id": instance_id,
            "cpu_utilization": None,
            "message": "No CPU data available"
        }

    latest = max(
        datapoints,
        key=lambda x: x["Timestamp"]
    )

    return {
        "instance_id": instance_id,
        "cpu_utilization": round(
            latest["Average"],
            2
        ),
        "timestamp": latest["Timestamp"].isoformat()
    }


def get_ec2_health():

    instances = get_ec2_instances()

    health = []

    for instance in instances:

        state = instance["state"]

        if state == "running":
            status = "healthy"

        elif state == "stopped":
            status = "stopped"

        else:
            status = "attention"

        health.append({
            "id": instance["id"],
            "state": state,
            "type": instance["type"],
            "status": status
        })

    return health


def get_high_cpu_instances(threshold=80):

    instances = get_ec2_instances()

    high_cpu = []

    for instance in instances:

        if instance["state"] != "running":
            continue

        cpu_data = get_cpu_utilization(
            instance["id"]
        )

        cpu = cpu_data.get(
            "cpu_utilization"
        )

        if cpu is not None and cpu >= threshold:

            high_cpu.append({
                "id": instance["id"],
                "type": instance["type"],
                "cpu_utilization": cpu,
                "threshold": threshold
            })

    return high_cpu