# AWS to GCP Migration: Employee Directory Application

##  Project Overview

This project demonstrates a comprehensive cloud migration strategy, moving a legacy 3-tier web application from **Amazon Web Services (AWS)** to **Google Cloud Platform (GCP)**. The application is a Python Flask-based Employee Directory that allows users to view, add, and manage employee records, including photo uploads.

The goal was to modernize the infrastructure using **Infrastructure as Code (Terraform)** and leverage GCP's cloud-native services to improve scalability, reliability, and maintainability.

---


##  Project Structure

```
GCP/
├── app/                 # Python Flask Application Code
│   ├── templates/       # HTML Templates
│   ├── application.py   # Main App Logic
│   ├── database_datastore.py # GCP Datastore Adapter
│   └── ...
├── terraform/           # Infrastructure as Code
│   ├── main.tf          # Provider Config
│   ├── compute.tf       # MIG, Autoscaler, Templates
│   ├── database.tf      # Firestore Config
│   ├── storage.tf       # GCS Bucket Config
│   ├── vpc.tf           # Networking & Firewalls
│   ├── lb .tf           # Cloud HTTP(S) Load Balancer
│   ├── iam.tf           # Service Accounts & Permissions
│   ├── variables.tf     # Variables
│   └── startup.sh       # Instance Boot Script
└── README.md            # Project Documentation
```

##  Architecture Evolution

The migration followed a "Re-platform" strategy, replacing AWS-specific services with their GCP managed equivalents while keeping the core application logic intact.

| Component | AWS Architecture | GCP Architecture | Improvement/Benefit |
|-----------|------------------|------------------|---------------------|
| **Compute** | EC2 Auto Scaling Group | **Managed Instance Group (MIG)** | Automated scaling, self-healing, and rolling updates. |
| **Load Balancing** | Application Load Balancer (ALB) | **Cloud HTTP(S) Load Balancer** | Global anycast IP, integrated health checks, and DDoS protection. |
| **Database** | DynamoDB (NoSQL) | **Firestore (Datastore mode)** | Serverless, highly scalable NoSQL document database. |
| **Object Storage** | S3 Bucket | **Google Cloud Storage (GCS)** | Durable, secure object storage for employee photos. |
| **Networking** | VPC + Public Subnets | **VPC + Cloud NAT** | Enhanced security by keeping instances private (no public IPs). |
| **Identity** | IAM Roles | **Service Accounts + IAM** | Granular permission control using the Principle of Least Privilege. |

---

##  Technical Implementation

### 1. Infrastructure as Code (Terraform)
The entire GCP infrastructure is provisioned using Terraform, ensuring reproducibility and version control.
- **Modular Design:** Resources are organized into logical files (`compute.tf`, `database.tf`, `storage.tf`, `vpc.tf`).
- **Simplified Networking:** Unlike AWS where subnets are zonal, GCP subnets are **regional**. This allowed us to use a single subnet (`employee-web-app-subnet`) to host instances across multiple zones, simplifying the network topology while maintaining high availability.
- **Security:**
  - Instances run in private subnets with no public IP addresses.
The entire GCP infrastructure is provisioned using Terraform, ensuring reproducibility and version control.
- **Modular Design:** Resources are organized into logical files (`compute.tf`, `database.tf`, `storage.tf`, `vpc.tf`).
- **Security:** 
  - Instances run in private subnets with no public IP addresses.
  - **Cloud NAT** provides secure outbound internet access for updates and package installation.
  - **Firewall rules** strictly limit access to HTTP traffic from the Load Balancer and SSH via Identity-Aware Proxy (IAP).

### 2. Application Modernization
The Python Flask application was refactored to decouple it from AWS SDKs (`boto3`) and integrate with GCP client libraries.
- **Storage Adapter:** Replaced S3 logic with `google-cloud-storage` for uploading and generating Signed URLs for secure image access.
- **Database Adapter:** Implemented a new data layer using `google-cloud-datastore` to interact with Firestore in Datastore mode.
- **Metadata Service:** Updated instance metadata retrieval logic to query the GCP Metadata Server.

### 3. Automated Deployment
- **Startup Scripts:** A robust `startup.sh` script handles the bootstrapping of new instances. It installs dependencies, downloads the latest application code from GCS, and configures the environment variables dynamically.
- **Rolling Updates:** Changes to the application or infrastructure trigger a zero-downtime rolling update of the Managed Instance Group.

---

##  Challenges & Solutions

During the migration, several technical challenges were encountered and resolved:

*   **Challenge:** Application startup failures due to missing system dependencies for Python packages.
    *   **Solution:** Debugged using `journalctl` via SSH and updated the startup script to include `default-libmysqlclient-dev` and other prerequisites.
*   **Challenge:** "502 Bad Gateway" errors from the Load Balancer.
    *   **Solution:** Identified that the application health checks were failing because the startup script was downloading an outdated version of the code. Implemented a deployment pipeline where the latest code is zipped and uploaded to GCS, which the instances then download on boot.
*   **Challenge:** Secure SSH access to private instances.
    *   **Solution:** Configured **Identity-Aware Proxy (IAP)** and firewall rules to allow secure SSH tunneling without exposing port 22 to the public internet.
*   **Challenge:** Images not loading in the application.
    *   **Solution:** Diagnosed an IAM permission issue. The Service Account lacked the `iam.serviceAccountTokenCreator` role required to sign blobs. Updated the Terraform IAM configuration to grant the necessary permissions.

---

##  How to Deploy

### Prerequisites
*   Google Cloud SDK (`gcloud`) installed and authenticated.
*   Terraform installed.
*   A GCP Project with billing enabled.

### Steps

1.  **Clone the Repository:**
    ```bash
    git clone <repository-url>
    cd emp-app/GCP
    ```

2.  **Package the Application:**
    Zip the application code and upload it to a GCS bucket (or let the CI/CD pipeline handle this).
    ```bash
    # Example manual packaging
    cd app
    zip -r ../FlaskApp.zip .
    gsutil cp ../FlaskApp.zip gs://<your-bucket-name>/
    ```

3.  **Configure Terraform:**
    Create a `terraform.tfvars` file in `terraform/`:
    ```hcl
    project_id   = "your-gcp-project-id"
    region       = "us-central1"
    flask_secret = "your-secure-secret"
    ```

4.  **Deploy Infrastructure:**
    ```bash
    cd terraform
    terraform init
    terraform apply
    ```

5.  **Access the Application:**
    Terraform will output the **Load Balancer IP**. Visit this IP in your browser to see the running application.

---
