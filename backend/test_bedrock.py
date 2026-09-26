import boto3

client = boto3.client(
    "bedrock-runtime",
    region_name="us-east-1"
)

response = client.converse(
    modelId="us.amazon.nova-lite-v1:0",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "text": "Explain in one sentence what high CPU utilization on an AWS EC2 instance could mean."
                }
            ]
        }
    ]
)

print(response["output"]["message"]["content"][0]["text"])