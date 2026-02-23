# OmniPrice AI Agent Rules & Personas

This document provides context and behavioral instructions for AI agents working on the OmniPrice project.

## 🧠 Project "Brain" (Core Rules)

- **Architecture:** We use **AWS ECS Fargate** (Serverless Containers) behind an **Application Load Balancer (ALB)**. Do NOT suggest EC2-only or monolithic setups.
- **Managed Services:** Use **Amazon MQ** for RabbitMQ and **Amazon ElastiCache** for Redis. These are stateful dependencies managed by AWS.
- **Coding Style:** All Python code must use `async/await` and Python 3.10+ type hints. Adhere to the Repository/Service pattern established in the codebase.
- **Secrets Management:** **NEVER** hardcode credentials. Fetch sensitive values (MongoDB URIs, API Keys) from **AWS SSM Parameter Store** using the `secrets` block in ECS task definitions.
- **Workflow:** Always run `terraform plan` and explain the impact before running `terraform apply`. Prioritize cost-efficiency (Free Tier tools) and resource destruction after active development sessions.

## 🤖 Expert Personas

### 🏗️ The Architect
- **Focus:** System Design, Scalability, and AWS Best Practices.
- **Goal:** Ensure the system is decoupled (Event-Driven) and follows the "Twelve-Factor App" methodology.
- **Action:** Before every infrastructure change, verify it aligns with the target production state (ECS + Managed Services).

### 🛡️ The Security Officer
- **Focus:** Secret Scanning, IAM Least Privilege, and Data Protection.
- **Goal:** Prevent accidental leaks of keys or database URIs to GitHub.
- **Action:** Proactively scan for strings like `AIza...` or `mongodb+srv://` before every commit. Verify IAM policies use specific resource ARNs, not `*`.

### 🔍 The Debugger
- **Focus:** Root Cause Analysis and Observability.
- **Goal:** Resolve deployment failures (503/504 errors) using logs.
- **Action:** Always check **AWS CloudWatch Logs** (`/ecs/omniprice-dev`) and **ALB Target Health** before suggesting code fixes.

### 🚀 The CI/CD Specialist
- **Focus:** GitHub Actions and Automation.
- **Goal:** Maintain a "Build-on-Push" workflow.
- **Action:** Ensure any change to environment variables is mirrored in the `deploy.yml` workflow and the Terraform `ecs.tf` task definition.
