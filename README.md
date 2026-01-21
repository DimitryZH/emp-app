# Enterprise App Migration to Google Cloud (GCP)

This repository is a **migration case study** for a Python/Flask "Enterprise App" that moves from a legacy-style AWS deployment to modern architectures on Google Cloud.

It focuses on:
- Showing a realistic AWS baseline
- Re‑platforming the app to GCP Compute Engine
- Modernizing further to serverless Cloud Run with CI/CD

All detailed design and runbooks are moved into the `docs/` folder and per-platform deployment guides.

---

## Quick Overview

The same Flask application is deployed in three ways:

1. **AWS Baseline** – EC2 + Application Load Balancer + DynamoDB + S3
2. **GCP Option 1** – Compute Engine Managed Instance Group + HTTPS Load Balancer + Firestore + Cloud Storage
3. **GCP Option 2** – Cloud Run (serverless containers) + Artifact Registry + CI/CD with GitHub Actions

Each option is fully described in architecture and deployment docs under `docs/` and in the `deployment_*.md` files in each platform folder.

---

## High-Level Architecture (At a Glance)

- **Web tier**: Flask app served via EC2, Compute Engine, or Cloud Run
- **Data tier**: DynamoDB (AWS) or Firestore (GCP)
- **Object storage**: S3 (AWS) or Cloud Storage (GCP)
- **Identity**: IAM roles (AWS) or service accounts with IAM (GCP)

Detailed diagrams and flows are in [`docs/architecture.md`](docs/architecture.md).

---

## Technology Stack (Summary)

- **Language & Framework**: Python, Flask, Jinja2
- **AWS**: EC2, Auto Scaling, ALB, DynamoDB, S3, IAM
- **GCP (Compute Engine)**: Compute Engine, MIG, HTTPS Load Balancer, Firestore (Datastore mode), Cloud Storage, VPC, Cloud NAT, service accounts
- **GCP (Cloud Run)**: Cloud Run, Artifact Registry, Firestore, Cloud Storage, Secret Manager
- **Automation & Tooling**: Terraform, Google Cloud SDK, AWS CLI, Docker, GitHub Actions

---

## How to Use This Repository

1. **Understand the architecture**  
   Read the full architecture and migration story:
   - [`docs/architecture.md`](docs/architecture.md)

2. **Understand the deployment model**  
   Review common deployment principles (Terraform, environments, CI/CD):
   - [`docs/deployment.md`](docs/deployment.md)

3. **Pick a deployment path and follow its guide**
   - AWS baseline (EC2): `AWS/deployment_aws.md`
   - GCP Compute Engine (Option 1): `GCP/deployment_gce.md`
   - GCP Cloud Run (Option 2): `GCP-Cloud-Run/deployment_cloud_run.md`

4. **Operate and optimize**
   - Troubleshooting tips and common errors:
     - [`docs/troubleshooting.md`](docs/troubleshooting.md)
   - Cost guidance and efficiency tuning:
     - [`docs/cost-optimization.md`](docs/cost-optimization.md)

---

## Repository Layout (Short)

```text
/
├── AWS/                # AWS baseline app + Terraform + deployment_aws.md
├── GCP/                # GCE (Option 1) app + Terraform + deployment_gce.md
├── GCP-Cloud-Run/      # Cloud Run (Option 2) Terraform + deployment_cloud_run.md
├── docs/               # Architecture, deployment model, troubleshooting, cost
└── .github/workflows/  # cloud-run-deploy.yml (Cloud Run CI/CD)
```

For all implementation details and diagrams, start in:
- [`docs/architecture.md`](docs/architecture.md)
- [`docs/deployment.md`](docs/deployment.md)

