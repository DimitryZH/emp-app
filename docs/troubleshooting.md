# Troubleshooting Guide

This guide documents real issues encountered while implementing the **Enterprise Application Migration** project across:

- GCP Compute Engine – see [`GCP/deployment_gce.md`](../GCP/deployment_gce.md)
- GCP Cloud Run (containers, Terraform, GitHub Actions) – see [`GCP-Cloud-Run/deployment_cloud_run.md`](../GCP-Cloud-Run/deployment_cloud_run.md)

It serves both as **hands-on troubleshooting work** (supported by GitHub Actions logs and screenshots under [`docs/assets`](../docs/assets)) and as a **professional runbook** to fix these issues.

Each issue is structured with:

- **Symptom** – how the problem surfaces (pipeline failure, HTTP error, etc.)
- **Root Cause** – what was actually wrong
- **Resolution** – the concrete fix that resolved it
- **Prevention / Best Practices** – how to avoid it in future environments



---

## A. Workload Identity Federation (WIF) Misconfiguration

> A and B are issues occurred while wiring CI/CD for Cloud Run in [`.github/workflows/cloud-run-deploy.yml`](../.github/workflows/cloud-run-deploy.yml).


**Symptom**  
The workflow fails in the **Configure GCP authentication** step. Logs in the GitHub Actions UI show messages such as:

- `Failed to exchange token for service account`
- `Workload Identity Provider not found`
- `invalid audience` or `audience does not match`

**Root Cause**  
Workload Identity Federation between GitHub and GCP was not configured consistently with the values used in the workflow:

- `GCP_WORKLOAD_IDENTITY_PROVIDER` did not exactly match the provider resource name created in GCP.
- Provider attribute conditions did not match the actual GitHub repository.
- `GCP_WORKLOAD_IDENTITY_SA` did not point to the correct CI service account.

[GitHub Actions Settings:](../docs/assets/repository_secrets.png)

**Resolution**

1. In GCP Console → **IAM & Admin → Workload Identity Federation**, copy the exact provider resource name:
   - `projects/<PROJECT_NUMBER>/locations/global/workloadIdentityPools/<POOL_ID>/providers/<PROVIDER_ID>`
2. Update the GitHub repository secret `GCP_WORKLOAD_IDENTITY_PROVIDER` with that exact value.
3. Adjust provider attribute conditions so they reference the correct repository, for example:
   - `attribute.repository == "<github-owner>/<repo-name>"`
4. Set `GCP_WORKLOAD_IDENTITY_SA` to the CI service account email (for example `enterprise-app-github-sa@1234567890.iam.gserviceaccount.com`).
5. Add a diagnostic step (`gcloud auth list`) in the workflow and confirm authentication succeeds.

**Prevention / Best Practices**

- Keep the WIF provider resource name and attribute conditions documented in [`GCP-Cloud-Run/deployment_cloud_run.md`](../GCP-Cloud-Run/deployment_cloud_run.md).
- Validate WIF with a minimal auth-only workflow before adding build and deploy jobs.
- Use dedicated, narrowly-scoped service accounts for CI.

---

## B.  Cloud Build / Artifact Registry – `PERMISSION_DENIED`

**Symptom**  
The **Build and push container image with Cloud Build** step fails. Logs show error such as:

- `PERMISSION_DENIED: The caller does not have permission to act as service account...`


[GitHub Actions logs:](../docs/assets/build_push_perm_denied.png)

**Root Cause**  
The GitHub CI service account (for example `enterprise-app-github-sa@enterprise-app-migration.iam.gserviceaccount.com`) lacked the IAM roles required to:

- Run Cloud Build in the `enterprise-app-migration` project.
- Push images to the Artifact Registry repository created by Terraform in [`GCP-Cloud-Run/terraform/main.tf`](../GCP-Cloud-Run/terraform/main.tf).

**Resolution**

1. Grant the CI service account on the project:
   - `roles/artifactregistry.writer` – to push images to Artifact Registry.
   - `roles/cloudbuild.builds.editor` – to run Cloud Build builds.
2. If Cloud Build uses a dedicated build service account via `--service-account`, grant the CI account:
   - `roles/iam.serviceAccountUser` on that build service account.
3. Re-run the workflow and confirm that it:
   - Builds the Docker image from [`GCP/app`](../GCP/app).
   - Pushes it successfully to the Terraform-managed repository (for example `enterprise-app-repo` in `us-central1`).

**Prevention / Best Practices**

- Define a dedicated **CI IAM policy** and document it in [`GCP-Cloud-Run/deployment_cloud_run.md`](../GCP-Cloud-Run/deployment_cloud_run.md).
- Manage CI IAM bindings via Terraform or repeatable scripts.
- Periodically review IAM audit logs for the CI service account.

---

## C. 403 Forbidden when accessing Cloud Run URL

**Symptom**  
Opening the Cloud Run URL (from Terraform output or `gcloud run services describe`) returns:

```text
Error: Forbidden
The user does not have permission to access this resource.
```
**Root Cause**  
The Cloud Run service `enterprise-app` was deployed as **private** (default), and `allUsers` did not have the `roles/run.invoker` role.

**Resolution**

1. For public demo or external access, grant invoker to all users:

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

2. Refresh the URL and confirm it is now accessible.

This step is illustrated in [`GCP-Cloud-Run/assets/grant_access.gif`](../GCP-Cloud-Run/assets/grant_access.gif).

**Prevention / Best Practices**

- Decide early whether the service is public or private.
- For non-public systems, grant `roles/run.invoker` only to the identities that require access.



## D. GCP Compute Engine – application not accessible after deployment

**Symptom**  
After a successful `terraform apply` for the Managed Instance Group stack, opening the HTTP Load Balancer IP from the outputs of [`GCP/deployment_gce.md`](../GCP/deployment_gce.md) returns `502` or times out instead of showing the Enterprise App UI.

**Root Cause**  
The HTTP Load Balancer marks all instances in the Managed Instance Group as **unhealthy**, most often due to one of the following:

- Health check configuration (path/port) does not match the Flask app endpoint exposed by the startup script.
- Firewall rules do not allow Google health check IP ranges to reach the instance group on the health check port.

**Resolution**

1. **Validate the app on a VM instance directly**
   - SSH into one of the MIG instances.
   - Run: `curl http://localhost:8080/` and confirm the HTML for the Enterprise App is returned.

2. **Verify health check configuration** in the load balancer:
   - Ensure the health check is probing the correct port (for this project, `8080`).
   - Use path `/` unless the app exposes a different dedicated health endpoint.

3. **Confirm firewall rules** for health checks:
   - Ensure there is a firewall rule that allows traffic from the Google health check ranges to the instance group on the health check port.

4. **Wait for instances to become healthy**
   - In the MIG and backend service views, confirm instance status turns to `HEALTHY`.
   - Re-test the external load balancer IP in a browser and verify the Enterprise App UI loads.

**Prevention / Best Practices**

- Keep the health check path and port documented alongside the app configuration in [`GCP/deployment_gce.md`](../GCP/deployment_gce.md).
- When modifying the Flask app or startup script, re-validate the local endpoint (`curl http://localhost:8080/`) and ensure the health check still matches.

## E. Quick Reference – Diagnostic Commands (GCP & Terraform)

```bash
# Describe Cloud Run service and get URL
gcloud run services describe enterprise-app \
  --region=us-central1 \
  --platform=managed

# Tail recent application requests from Cloud Run (Cloud Logging)
gcloud logs tail "run.googleapis.com%2Frequests" \
  --project=enterprise-app-migration \
  --limit=100

# Validate Terraform state and detect drift for Cloud Run stack
cd ../GCP-Cloud-Run/terraform
terraform plan

# List recent Cloud Build executions
gcloud builds list --project=enterprise-app-migration

# Show IAM policy for Cloud Run service (to verify 'run.invoker' bindings)
gcloud run services get-iam-policy enterprise-app \
  --region=us-central1 \
  --platform=managed
```

---

By systematically capturing CI/CD, IAM, Terraform, and runtime issues in this guide, the project demonstrates a **production-grade troubleshooting discipline**. These patterns can be reused when onboarding new environments (dev, stage, prod) or extending the architecture beyond the current AWS, GCE, and Cloud Run solutions.

