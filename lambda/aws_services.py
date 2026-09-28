import boto3
from datetime import datetime, timedelta, timezone


REGION = "us-east-1"


ec2 = boto3.client(
    "ec2",
    region_name=REGION
)

cloudwatch = boto3.client(
    "cloudwatch",
    region_name=REGION
)


# -------------------------------------------------
# Get active EC2 instances
# -------------------------------------------------

def get_ec2_instances():

    response = ec2.describe_instances(
        Filters=[
            {
                "Name": "instance-state-name",
                "Values": [
                    "pending",
                    "running",
                    "stopping",
                    "stopped",
                    "shutting-down"
                ]
            }
        ]
    )

    instances = []

    for reservation in response.get(
        "Reservations",
        []
    ):

        for instance in reservation.get(
            "Instances",
            []
        ):

            instances.append(
                {
                    "id": instance["InstanceId"],
                    "state": instance["State"]["Name"],
                    "type": instance["InstanceType"]
                }
            )

    return instances


# -------------------------------------------------
# Get EC2 health
# -------------------------------------------------

def get_ec2_health():

    instances = get_ec2_instances()

    health = []

    for instance in instances:

        if instance["state"] == "running":

            status = "healthy"

        else:

            status = "attention"

        health.append(
            {
                "id": instance["id"],
                "state": instance["state"],
                "type": instance["type"],
                "status": status
            }
        )

    return health


# -------------------------------------------------
# Get CPU utilization
# -------------------------------------------------

def get_cpu_utilization(
    instance_id
):

    end_time = datetime.now(
        timezone.utc
    )

    start_time = (
        end_time -
        timedelta(minutes=30)
    )

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

        Statistics=[
            "Average"
        ]
    )

    datapoints = response.get(
        "Datapoints",
        []
    )

    if not datapoints:

        return {
            "instance_id": instance_id,
            "cpu_utilization": 0,
            "timestamp": None
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
        "timestamp": latest["Timestamp"]
    }


# -------------------------------------------------
# Find high CPU instances
# -------------------------------------------------

def get_high_cpu_instances(
    threshold=80
):

    instances = get_ec2_instances()

    high_cpu = []

    for instance in instances:

        if instance["state"] != "running":
            continue

        cpu_data = get_cpu_utilization(
            instance["id"]
        )

        cpu = cpu_data.get(
            "cpu_utilization",
            0
        )

        if cpu >= threshold:

            high_cpu.append(
                {
                    "id": instance["id"],
                    "cpu_utilization": cpu,
                    "threshold": threshold
                }
            )

    return high_cpu