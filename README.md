# Enterprise App Migration to Google Cloud (GCP)

This repository demonstrates a **real-world cloud migration project**, where a legacy 3-tier web application is deployed on AWS and then re-platformed to Google Cloud Platform using modern Infrastructure as Code and cloud-native services.

The project is designed both as:
- A **completed technical migration case study**
- A **reusable blueprint** for client cloud-migration projects

It showcases multi-cloud architecture, Terraform automation, scalable infrastructure, and application modernization.

---

## Project Goal

Migrate a production-style web application from AWS to GCP while:

- Preserving application functionality
- Replacing cloud-specific services with GCP equivalents
- Improving security and scalability
- Automating everything with Terraform
- Documenting the migration process end-to-end

---

## Repository Structure

```text
/
├── AWS/                      # Original AWS deployment (EC2 + ALB + DynamoDB + S3)
│   ├── README.md             # AWS Employee Directory app overview & usage
│   ├── app/                  # Application source code (Flask on AWS)
│   ├── assets/               # AWS architecture & app diagrams
│   └── terraform/            # AWS Infrastructure as Code
│       └── README.md         # AWS Terraform project documentation
│
├── GCP/                      # GCP migration using Compute Engine + MIG
│   ├── app/                  # Refactored Flask application for GCP
│   ├── assets/               # GCP diagrams
│   ├── terraform/            # GCP Infrastructure as Code
│   ├── migration.md          # AWS → GCP migration design & architecture
│   └── deployment_gce.md     # Step-by-step GCE deployment guide
│
├── FlaskApp.zip              # Packaged Flask app archive (used by some guides)
│
└── README.md                 # This file
```

> Note: A second phase of this project targets a **GCP Cloud Run** (serverless) migration. That implementation is referenced in the docs as `/GCP-Cloud-Run/` and is planned as a future extension of this repository.

---

## Documentation Overview

This repository includes several focused documentation files to guide you through both the AWS baseline and the GCP migration.

### AWS Documentation

- **AWS Application Overview & Usage**  
  See [AWS/README.md](AWS/README.md) for:
  - High-level description of the AWS Employee Directory App
  - Features and architecture of the original AWS deployment
  - Screenshots of the running application
  - Basic setup and usage instructions on AWS

- **AWS Terraform Infrastructure**  
  See [AWS/terraform/README.md](AWS/terraform/README.md) for:
  - Detailed description of the AWS Terraform project
  - Infrastructure components (VPC, EC2, ALB, Auto Scaling, DynamoDB, S3, IAM, etc.)
  - Steps to initialize, plan, apply, and destroy the AWS environment
  - Notes on security, modular structure, and cost optimization

### GCP (Compute Engine) Migration Documentation

- **AWS → GCP Migration Design**  
  See [GCP/migration.md](GCP/migration.md) for:
  - Overall migration strategy (**Re-platform / Lift & Optimize**)
  - Detailed AWS → GCP service mapping (ALB → HTTPS LB, EC2 → GCE, DynamoDB → Firestore, S3 → Cloud Storage, IAM Roles → Service Accounts, etc.)
  - Network and security redesign (private subnets, Cloud NAT, IAP)
  - Architectural comparison and key design decisions (compute, database, storage, identity)

- **GCP Compute Engine Deployment Guide**  
  See [GCP/deployment_gce.md](GCP/deployment_gce.md) for:
  - Prerequisites for deploying on GCP using Compute Engine + Managed Instance Groups
  - Commands to authenticate with GCP and enable required APIs
  - How to package and upload the Flask app and configure Terraform variables
  - Step-by-step Terraform workflow to provision the full GCP stack
  - Post-deployment validation, scaling tests, and cleanup

These documents together provide:

- A complete picture of the original AWS implementation
- A detailed design of the target GCP architecture
- Hands-on deployment instructions for reproducing the migration

---

## Architecture Comparison

### AWS – Original Deployment

```mermaid
flowchart TB
    U[User Browser] --> ALB[AWS Application Load Balancer]
    ALB --> ASG[Auto Scaling Group]
    ASG --> EC21[EC2 Instance]
    ASG --> EC22[EC2 Instance]

    subgraph LT["Launch Template"]
        EC21
        EC22
        UD[UserData Script]
    end

    UD --> EC21
    UD --> EC22

    EC21 --> APP1[Flask App]
    EC22 --> APP2[Flask App]

    APP1 --> S3[(S3 Bucket)]
    APP2 --> S3

    APP1 --> DDB[(DynamoDB)]
    APP2 --> DDB

    subgraph VPC["AWS VPC"]
        PUBSUB1[Public Subnet AZ1]
        PUBSUB2[Public Subnet AZ2]
        ASG
    end

    EC21 --- PUBSUB1
    EC22 --- PUBSUB2

    PUBSUB1 --> IGW[Internet Gateway] --> Internet[(Internet)]
    PUBSUB2 --> IGW

    IAM[IAM Role]
    IAM --> EC21
    IAM --> EC22
    IAM --> S3
    IAM --> DDB

    ALB --> HC[Target Group Health Check]
    HC --> ASG
```

---

### GCP – Compute Engine Migration

```mermaid
flowchart TB
    U[User Browser] --> LB[Cloud HTTPS Load Balancer]

    LB --> MIG[Managed Instance Group]

    MIG --> VM1[Compute Engine VM]
    MIG --> VM2[Compute Engine VM]

    subgraph IT["Instance Template"]
        VM1
        VM2
        SS[Startup Script]
    end

    SS --> VM1
    SS --> VM2

    VM1 --> APP1[Flask App]
    VM2 --> APP2[Flask App]

    APP1 --> GCS[(Cloud Storage Bucket)]
    APP2 --> GCS

    APP1 --> FS[(Firestore Datastore Mode)]
    APP2 --> FS

    subgraph VPC["Custom VPC"]
        SUBNET[Regional Private Subnet]
        MIG
    end

    VM1 --- SUBNET
    VM2 --- SUBNET

    SUBNET --> NAT[Cloud NAT] --> Internet[(Internet)]

    SA[Service Account]
    SA --> VM1
    SA --> VM2
    SA --> GCS
    SA --> FS

    LB --> HC[Health Checks]
    HC --> MIG
```

---

## Why This Project Matters

This repository demonstrates:

- **Terraform Infrastructure as Code**
- **Cloud networking & security design**
- **Scalable compute architectures**
- **Application refactoring for cloud services**
- **Real migration problem-solving**

The AWS and GCP documentation referenced above shows not only *what* was built, but *how* and *why* each design decision was made.

---

## Author

**Dmitry Zhuravlev**  
Cloud DevOps Engineer

---

## License

MIT License — free to reuse with attribution.
