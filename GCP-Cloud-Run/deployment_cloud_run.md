# GCP Cloud Run Deployment Guide

This document provides a step-by-step guide to deploy the Enterprise App on **Google Cloud Platform using Cloud Run (serverless containers)**. This is the **Option 2** migration path, complementing the **Compute Engine + Managed Instance Group** deployment described in [`GCP/deployment_gce.md`](../GCP/deployment_gce.md).

The Cloud Run deployment is implemented using:

- Containerized Flask app under [`GCP/app`](../GCP/app)
- Infrastructure as Code via Terraform under [`GCP-Cloud-Run/terraform`](terraform/main.tf)
- CI/CD with GitHub Actions and Workload Identity Federation in [`.github/workflows/cloud-run-deploy.yml`](../.github/workflows/cloud-run-deploy.yml)
- Architecture and design details in [`README.md`](../README.md)

---

## Prerequisites

Before starting, ensure you have:

- A Google Cloud project **`enterprise-app-migration`** with **Billing enabled**
- **Google Cloud SDK (gcloud)** installed
- **Terraform** installed (v1.6+ recommended)
- **Docker** installed (for local build and test)
- A GitHub repository containing this codebase
- Permissions on the GCP project to:
  - Create Cloud Run services
  - Create Artifact Registry repositories
  - Create and manage service accounts and IAM bindings
  - Create Firestore (Datastore mode) databases
  - Create Cloud Storage buckets
  - Configure Workload Identity Federation (for CI/CD)

---

## Step 1 – Authenticate with GCP

Initialize gcloud and authenticate on your workstation or Cloud Shell:

```bash
gcloud init
gcloud auth application-default login
```

Set your active project to the Cloud Run project used in this solution:

```bash
gcloud config set project enterprise-app-migration
```

This ensures both `gcloud` commands and Terraform (via Application Default Credentials) operate against the correct project.

---

## Step 2 – Enable Required APIs

Enable all APIs used by the Cloud Run solution (some may already be enabled from earlier phases):

```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  iam.googleapis.com \
  cloudresourcemanager.googleapis.com \
  secretmanager.googleapis.com \
  firestore.googleapis.com \
  storage.googleapis.com \
  cloudbuild.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com
```

These APIs are referenced directly or indirectly by Terraform in [`GCP-Cloud-Run/terraform/main.tf`](terraform/main.tf) and by the CI/CD workflow in [`.github/workflows/cloud-run-deploy.yml`](../.github/workflows/cloud-run-deploy.yml).

---

## Step 3 – Prepare the Containerized Application

The Cloud Run deployment uses the GCP-optimized Enterprise App under [`GCP/app`](GCP/app:1).

### 3.1 Review the Dockerfile

The production Dockerfile for Cloud Run resides at:

- [`GCP/app/Dockerfile`](../GCP/app/Dockerfile)

Key characteristics (as implemented during this migration):

- Base image: `python:3.11-slim`
- Working directory: `/app`
- Dependencies installed from [`GCP/app/requirements.txt`](../GCP/app/requirements.txt)
- Application code copied: `application.py`, `config.py`, `database_datastore.py`, and the `templates/` directory
- Entrypoint uses **Gunicorn** to serve the Flask app, listening on `0.0.0.0:$PORT` where `PORT` is injected by Cloud Run
- Logs are written to stdout/stderr for integration with Cloud Logging

### 3.2 Local Build and Smoke Test

From the `GCP/app` directory:

```bash
cd GCP/app

docker build -t enterprise-app:test .

docker run --rm -p 8080:8080 \
  -e PHOTOS_BUCKET=local-photos-bucket \
  -e GCP_PROJECT=enterprise-app-migration \
  -e DATASTORE_MODE=on \
  enterprise-app:test
```

Open `http://localhost:8080/` in your browser and verify:

- Employee list loads
- You can add a new employee
- You can upload and view an employee photo

Note: In Cloud Run, GCP credentials are provided via the service account. Locally you may need ADC (`gcloud auth application-default login`) for full functionality.

---

## Step 4 – Configure Terraform Variables (Cloud Run Stack)

The Cloud Run infrastructure is defined under:

- [`GCP-Cloud-Run/terraform/main.tf`](terraform/main.tf)
- [`GCP-Cloud-Run/terraform/variables.tf`](terraform/variables.tf)
- [`GCP-Cloud-Run/terraform/outputs.tf`](terraform/outputs.tf)
- [`GCP-Cloud-Run/terraform/terraform.tfvars`](terraform/terraform.tfvars)

Update `terraform.tfvars` with your project and environment values. For the `enterprise-app-migration` baseline, the file was created with values similar to:

```hcl
project_id         = "enterprise-app-migration"
region             = "us-central1"
environment        = "dev"          # or "stage" / "prod" for additional environments
photos_bucket_name = "enterprise-app-photos-784001prod"
```

These variables are consumed in [`GCP-Cloud-Run/terraform/main.tf`](terraform/main.tf) to parameterize the Cloud Run service, Artifact Registry repository, runtime service account, and Cloud Storage bucket.

---

## Step 5 – Initialize Terraform (Cloud Run)

From the repository root:

```bash
cd GCP-Cloud-Run/terraform

terraform init
```

Initialization will:

- Download the Google provider
- Configure the backend (if a remote GCS state bucket is defined)
- Prepare the working directory for `plan` and `apply`

---

## Step 6 – Deploy Cloud Run Infrastructure

Review the execution plan:

```bash
terraform plan
```

Apply the deployment:

```bash
terraform apply
```

Terraform will provision, in the `enterprise-app-migration` project:

1. **Artifact Registry repository**
   - Docker repository for application images (for example `enterprise-app-repo`), located in `us-central1`.

2. **Runtime service account for Cloud Run**
   - A dedicated service account (for example `enterprise-app-sa@enterprise-app-migration.iam.gserviceaccount.com`).
   - IAM roles assigned during this migration:
     - `roles/datastore.user` – read/write access to Firestore (Datastore mode)
     - `roles/storage.objectAdmin` – manage objects in the photos bucket
     - `roles/secretmanager.secretAccessor` – read secrets if Secret Manager is used for config

3. **Firestore (Datastore mode) database**
   - Database `(default)` in Datastore mode for employee records.

4. **Cloud Storage bucket for photos**
   - Bucket with the name provided in `photos_bucket_name` (e.g. `enterprise-app-photos-784001prod`).
   - Used by the application via the `PHOTOS_BUCKET` environment variable.

5. **Cloud Run service**
   - Service name: `enterprise-app`.
   - Region: `us-central1`.
   - Uses the runtime service account above.
   - Configured with environment variables such as:
     - `ENVIRONMENT` (e.g. `dev`)
     - `PHOTOS_BUCKET` (e.g. `enterprise-app-photos-784001prod`)
     - `GCP_PROJECT=enterprise-app-migration`
     - `DATASTORE_MODE=on`
   - Image field initialized with a placeholder container image; the actual production image is set later by CI/CD.

After `terraform apply` completes, inspect outputs:

```bash
terraform output
```

You should see values such as the Cloud Run service name, region, and URL (for example, `cloud_run_service_uri`).

---

## Step 7 – Configure CI/CD with GitHub Actions

Continuous delivery for the Cloud Run option is defined in:

- [`.github/workflows/cloud-run-deploy.yml`](../.github/workflows/cloud-run-deploy.yml)

This workflow builds the container image from [`GCP/app`](../GCP/app), pushes it to Artifact Registry, and then updates the Cloud Run service.

### 7.1 Workload Identity Federation (GitHub → GCP)

During this migration, **Workload Identity Federation (OIDC)** was configured instead of JSON key files. The key steps were:

1. **Create a Workload Identity Pool and Provider** in the `enterprise-app-migration` project, tied to the GitHub repository.
2. **Create a GitHub CI service account**, for example:
   - `enterprise-app-github-sa@enterprise-app-migration.iam.gserviceaccount.com`
3. **Grant IAM roles to the CI service account**:
   - `roles/artifactregistry.writer` – push images to Artifact Registry
   - `roles/cloudbuild.builds.editor` (or a more scoped role) – run Cloud Build jobs
   - `roles/run.admin` – update the Cloud Run service image and configuration
4. **Configure GitHub repository secrets** used by the workflow:
   - `GCP_WORKLOAD_IDENTITY_PROVIDER` – full resource name of the Workload Identity Provider
   - `GCP_WORKLOAD_IDENTITY_SA` – email of the CI service account

These are consumed in the "Configure GCP authentication" step inside [`.github/workflows/cloud-run-deploy.yml`](../.github/workflows/cloud-run-deploy.yml).

### 7.2 Build and Deploy Flow

On push to the main branch, the workflow:

1. Authenticates to GCP using the Workload Identity Provider and CI service account.
2. Uses **Cloud Build** to build and push the container image from [`GCP/app`](../GCP/app) to the Artifact Registry repository created by Terraform.
3. Runs `gcloud run services update` to point the `enterprise-app` Cloud Run service to the newly built image (tagged, for example, with `${GITHUB_SHA}`).


Github Actions workflow run showing successful Cloud Run deployment:

[`GCP-Cloud-Run/assets/workflow_succeeded.png`](assets/workflow_succeeded.png)


This pattern decouples **infrastructure provisioning** (Terraform, run by an operator) from **application rollout** (GitHub Actions, triggered by commits).

---

## Step 8 – Grant Public Access (Optional)

By default, newly created Cloud Run services are **private**. If you want the Enterprise App to be publicly accessible over HTTPS without authentication, grant the `roles/run.invoker` role to `allUsers`:




```bash
PROJECT_ID="enterprise-app-migration"
REGION="us-central1"
SERVICE="enterprise-app"

gcloud run services add-iam-policy-binding "$SERVICE" \
  --project="$PROJECT_ID" \
  --region="$REGION" \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --platform=managed
```

Granting public access to Cloud Run service via IAM:

[`GCP-Cloud-Run/assets/grant-access.gif`](assets/grant-access.gif)


This IAM binding change is part of the operational setup performed during this migration. For private deployments, instead grant `roles/run.invoker` to specific identities (users, groups, or service accounts).

---

## Step 9 – Verify Cloud Run Deployment

After Terraform has provisioned infrastructure and the CI/CD workflow has run at least once:

1. Retrieve the Cloud Run service URL:

   ```bash
   gcloud run services describe enterprise-app \
     --region=us-central1 \
     --platform=managed \
     --format='value(status.url)'
   ```

2. Open the URL in your browser.

3. Validate application functionality:
   - View employee list
   - Add a new employee
   - Upload an employee photo
   - Confirm records are stored in Firestore (Datastore mode) for the `enterprise-app-migration` project
   - Confirm images appear in the `photos_bucket_name` bucket (e.g. `enterprise-app-photos-784001prod`)

4. Optionally, verify scaling behavior by generating concurrent requests and observing Cloud Run instance scaling in the GCP console.

---

## Step 10 – Cleanup

To destroy all Cloud Run–related resources provisioned by Terraform in this solution:

```bash
cd GCP-Cloud-Run/terraform

terraform destroy
```

This command will remove:

- Cloud Run service `enterprise-app`
- Runtime service account and its IAM bindings
- Artifact Registry repository for the app images
- Cloud Storage photos bucket (`photos_bucket_name`)
- (If managed in this stack) the Firestore database

If you granted public access using `allUsers` and `roles/run.invoker`, those bindings are removed automatically when the Cloud Run service is deleted.

---

## Deployment Summary

By following this guide, you have deployed:

- A fully serverless Flask web application on **Cloud Run**
- Backed by **Firestore (Datastore mode)** and **Cloud Storage** for photos
- Using a **dedicated runtime service account** with minimal IAM roles:
  - `roles/datastore.user`
  - `roles/storage.objectAdmin`
  - `roles/secretmanager.secretAccessor`
- A **GitHub Actions** pipeline using **Workload Identity Federation** to:
  - Build and push container images via Cloud Build
  - Update the Cloud Run service to new revisions
- Infrastructure provisioned and managed by **Terraform** under [`GCP-Cloud-Run/terraform`](terraform/main.tf)

This Cloud Run deployment realizes the **Option 2** migration path described in [`README.md`](../README.md), standing alongside the Compute Engine deployment in [`GCP/deployment_gce.md`](../GCP/deployment_gce.md) as a complete, production-ready solution.

---

## Author

**Dmitry Zhuravlev**  
Cloud & DevOps Engineer

