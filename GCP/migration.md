# AWS → GCP Migration Design

This document describes the architectural migration of the Employee Directory application from Amazon Web Services (AWS) to Google Cloud Platform (GCP). It focuses on service mapping, infrastructure redesign, and key technical decisions made during the re-platforming process.

---

## Migration Strategy

The migration follows a **Re-platform (Lift & Optimize)** approach:

- Core application logic remains unchanged (Python Flask)
- AWS-managed services are replaced with GCP-native equivalents
- Infrastructure is rebuilt using Terraform
- Security and networking are redesigned following GCP best practices

This approach allows rapid migration while improving scalability, maintainability, and security.

---

## Service Mapping (AWS → GCP)

```mermaid
flowchart LR

    %% ===== ENVIRONMENTS =====
    subgraph AWS["AWS ENVIRONMENT"]
        ALB[Application Load Balancer]
        ASG[EC2 Auto Scaling Group]
        EC2[EC2 Instances]
        VPC_AWS[AWS VPC + Public Subnets]
        IAM_AWS[IAM Roles]
        DDB[DynamoDB]
        S3[S3 Bucket]
    end

    subgraph GCP["GOOGLE CLOUD"]
        GLB[Cloud HTTPS Load Balancer]
        MIG[Managed Instance Group]
        GCE[Compute Engine Instances]
        VPC_GCP[VPC + Private Subnet]
        IAM_GCP[Service Accounts + IAM]
        FS[Firestore Datastore mode]
        GCS[Cloud Storage Bucket]     
    end

    %% ===== SERVICE MAPPING =====
    ALB --> GLB
    ASG --> MIG
    EC2 --> GCE
   
    IAM_AWS --> IAM_GCP
    DDB --> FS
    S3 --> GCS
    
 %% Highlighted Security Re-Architecture
    VPC_AWS ==> |"KEY IMPROVEMENT<br/><br/>"| VPC_GCP

    %% ===== KEY IMPROVEMENT BOX =====
    NOTE["🔒 Security Perimeter Redesign:<br/><br/>Private Subnets + Zero Public IP<br/>Controlled Egress (Cloud NAT)<br/>Secure Access (Firewall + IAP)"]

    VPC_GCP ==> NOTE
    
        %% ===== STYLES =====

    %% Base cloud colors
    classDef aws fill:#FFF3E0,stroke:#FF9900,stroke-width:1.5px,font-weight:bold,color:#222,font-size:14px;
    classDef gcp fill:#E8F0FE,stroke:#1A73E8,stroke-width:1.5px,font-weight:bold,color:#222,font-size:14px;

    %% Highlighted VPC blocks
    classDef highlight stroke:#D93025,stroke-width:3px,font-weight:bold,font-size:20px;

    %% Environment titles
    classDef envTitle font-size:22px,font-weight:bold,color:#000;

    %% Key improvement emphasis
    classDef noteStyle fill:#FFF0F0,stroke:#D93025,stroke-width:3px,font-weight:bold,font-size:18px,color:#000;


%% ===== AUTHOR WATERMARK =====
    AUTHOR["Designed by Dmitry Z."]

    GCP  -.- AUTHOR


    %% Author watermark
    classDef authorStyle font-size:12px,font-style:italic,color:#666;

    %% Apply classes
    class ALB,ASG,EC2,DDB,S3,VPC_AWS,IAM_AWS aws;
    class GLB,MIG,GCE,FS,GCS,VPC_GCP,IAM_GCP gcp;
    class VPC_AWS,VPC_GCP highlight;
    class NOTE highlight;
    class AUTHOR envTitle;

    %% Apply title styles
    class AWS envTitle;
    class GCP envTitle;

```

---

## Architectural Evolution

### Original AWS Design

- EC2 Auto Scaling Group running Flask application
- Application Load Balancer distributing HTTP traffic
- DynamoDB for employee records
- S3 bucket for employee photos
- Public subnets with direct internet access
- IAM roles attached to EC2 instances

### Target GCP Design

- Managed Instance Group running Flask application on Compute Engine
- Global HTTP(S) Load Balancer
- Firestore (Datastore mode) for employee records
- Cloud Storage bucket for employee photos
- Private regional subnet with Cloud NAT for outbound access
- Service Accounts with fine-grained IAM permissions

---

## Key Design Decisions

### Networking
- AWS public subnets were replaced by **private subnets** in GCP
- **Cloud NAT** provides secure outbound internet access
- No public IPs assigned to application instances
- Load Balancer is the only public entry point

### Compute
- EC2 Auto Scaling Group replaced with **Managed Instance Group**
- Instance Template with startup script automates application bootstrapping
- Built-in health checks enable self-healing
- Autoscaler adjusts capacity based on CPU utilization

### Database
- DynamoDB replaced with **Firestore (Datastore mode)**
- NoSQL document model preserved
- Fully managed and serverless

### Object Storage
- S3 replaced with **Cloud Storage**
- Signed URLs used for secure image access

### Identity & Security
- IAM Roles replaced with **Service Accounts**
- Principle of Least Privilege enforced
- Secure SSH access via Identity-Aware Proxy (IAP)

---

## Migration Outcome

- Application successfully redeployed on GCP
- Full functional parity with AWS version
- Improved network security posture
- Automated infrastructure provisioning
- Scalable and self-healing compute layer

---

## Next Phase: Serverless Modernization

A second migration phase will introduce a **Cloud Run** deployment model:

```
/GCP-Cloud-Run/
```

This phase will demonstrate containerization, serverless scaling, and further cost optimization.

---

## Author

**Dmitry Zhuravlev**  
Cloud & DevOps Engineer

