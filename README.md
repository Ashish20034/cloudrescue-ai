# 🚨 CloudRescue AI

### AI-Powered AWS Cloud Incident Response Platform

CloudRescue AI is an AWS-based cloud incident response platform that monitors cloud infrastructure, detects abnormal conditions, analyzes probable root causes, and provides recommended recovery actions through a web dashboard.

The project is designed to reduce the time required to identify and respond to cloud infrastructure incidents.

---

## 🎯 Problem

Cloud infrastructure incidents can be difficult to troubleshoot quickly.

For example:

- EC2 CPU utilization becomes extremely high
- An EC2 instance becomes unhealthy
- Infrastructure resources experience abnormal behavior
- Engineers need to manually inspect CloudWatch metrics and logs

CloudRescue AI aims to bring these investigation steps into a single dashboard.

---

## 💡 Solution

CloudRescue AI connects AWS infrastructure monitoring with an incident analysis layer.

The platform:

1. Monitors AWS infrastructure
2. Retrieves EC2 and CloudWatch metrics
3. Detects abnormal conditions
4. Creates incidents
5. Determines incident severity
6. Analyzes probable root causes
7. Provides recommended actions
8. Displays the incident through a web dashboard

---

## 🏗️ Architecture

```text
                    AWS Infrastructure
                           │
                           ▼
                         EC2
                           │
                           ▼
                      CloudWatch
                           │
                           ▼
                    CloudRescue Lambda
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
       Incident Detection          AI Analysis
              │                         │
              └────────────┬────────────┘
                           ▼
                      API Gateway
                           │
                           ▼
                 CloudRescue Dashboard
