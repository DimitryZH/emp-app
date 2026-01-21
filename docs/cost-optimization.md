# Cost Optimization Guide

## Cloud Run vs Compute Engine

This document describes cost optimization considerations for two Google
Cloud deployment models used in this project:

-   **Google Compute Engine (VM-based deployment)**
-   **Google Cloud Run (serverless container deployment)**

The goal is to evaluate cost efficiency, scalability, and operational
overhead for each model, and provide guidance on when to choose one over
another.

------------------------------------------------------------------------

## Cost Model Overview

### Google Compute Engine

**Billing model:** - Pay for provisioned VM resources (CPU, memory) -
Billed per second while VM is running - Additional costs for: -
Persistent disks - Load balancer - External IPs - Cloud SQL - Network
egress

**Key characteristic:**\
Costs are incurred **even when application is idle**.

------------------------------------------------------------------------

### Google Cloud Run

**Billing model:** - Pay only for: - Request execution time - Allocated
CPU and memory during request processing - No cost when service is
idle - Built-in HTTPS load balancing included

**Key characteristic:**\
Costs scale **to zero** when no traffic exists.

------------------------------------------------------------------------

## Baseline Cost Comparison

  ------------------------------------------------------------------------
  Category               Compute Engine           Cloud Run
  ---------------------- ------------------------ ------------------------
  Idle cost              Yes (VM always running)  No (scales to zero)

  Auto-scaling           Manual / autoscaler      Native request-based
                                                  scaling

  Load balancer          Separate paid service    Included

  Operations overhead    VM maintenance required  Fully managed

  Startup latency        Always warm              Cold start possible

  Best for               Steady workloads         Variable / burst
                                                  workloads
  ------------------------------------------------------------------------

------------------------------------------------------------------------

## Example Workload Scenario

**Enterprise application profile:** - Average traffic: 2 requests/sec
during business hours\
- Low or no traffic at night\
- Peak bursts: up to 20 requests/sec\
- Container execution time per request: \~400ms\
- Application container: 1 vCPU, 512MB RAM

------------------------------------------------------------------------

## Cost Estimation Example

> Prices are approximate and based on public GCP pricing at the time of
> writing.\
> This example is for demonstration and FinOps comparison only.

### Option 1 --- Compute Engine

**Configuration:** - e2-medium VM (2 vCPU, 4GB RAM) - Runs 24/7

**Monthly cost:** - VM instance: \~\$27\
- Persistent disk: \~\$4\
- Load balancer: \~\$18\
- External IP: \~\$3

**Total monthly baseline:**\
➡️ **\~\$52 / month**

**Key note:**\
Cost is constant, regardless of traffic.

------------------------------------------------------------------------

### Option 2 --- Cloud Run

**Configuration:** - 1 vCPU, 512MB RAM - Concurrency: 10 - Scales to
zero when idle

**Estimated usage:** - 2 req/sec × 8 hours/day × 22 days\
- Execution time: 0.4 sec/request

**Compute usage:**\
≈ 506,880 vCPU-seconds/month

**Estimated monthly cost:** - Cloud Run compute: \~\$6 -- \$8\
- Requests: negligible at this scale\
- Load balancing: included

**Total monthly cost:**\
➡️ **\~\$7 / month**

------------------------------------------------------------------------

## Cost Result Summary

  -------------------------------------------------------------------------
  Platform            Monthly Cost   Idle Cost   Scaling Cost Efficiency
  ------------------- -------------- ----------- --------------------------
  Compute Engine      \~\$52         Yes         Low

  Cloud Run           \~\$7          No          High
  -------------------------------------------------------------------------

**Savings:**\
➡️ **\~85% lower cost** using Cloud Run for this workload pattern.

------------------------------------------------------------------------

## Quick Cost Optimization Wins

### For Compute Engine

-   Use autoscaling instance groups\
-   Apply committed-use discounts\
-   Right-size VM instance types\
-   Schedule non-production shutdown\
-   Use preemptible VMs for dev/test

### For Cloud Run

-   Optimize container startup time\
-   Reduce allocated CPU/memory\
-   Tune concurrency settings\
-   Keep minimum instances = 0 for non-prod

------------------------------------------------------------------------

## Long-term Optimization Strategy

-   Migrate suitable services from VM to Cloud Run\
-   Refactor monolith into microservices\
-   Measure cost per request\
-   Implement automated rightsizing\
-   Introduce scheduled environment shutdown

------------------------------------------------------------------------

## Observability for Cost Control

-   Enable Cloud Billing export\
-   Define monthly budgets\
-   Set anomaly alerts\
-   Track:
    -   Cost per environment\
    -   Cost per service\
    -   Cost per request

------------------------------------------------------------------------

## Decision Flow --- Which Platform to Choose?

``` mermaid
flowchart TD
    A[New Workload] --> B{Traffic Pattern?}
    B -->|Steady 24/7| C[Compute Engine]
    B -->|Variable / Bursty| D[Cloud Run]
    C --> E{Legacy VM Required?}
    E -->|Yes| C
    E -->|No| D
    D --> F[Cloud Run]
```

------------------------------------------------------------------------

## Decision Matrix

  Workload Type                   Recommended Platform
  ------------------------------- ----------------------
  Constant steady load            Compute Engine
  Variable or bursty load         Cloud Run
  Event-driven workloads          Cloud Run
  Legacy VM-based application     Compute Engine
  Modern containerized services   Cloud Run

------------------------------------------------------------------------

## FinOps Takeaways

-   Cloud Run shifts cost from **capacity-based** to **usage-based**
-   Compute Engine provides predictable fixed baseline cost
-   Combining both models enables optimal hybrid architecture

------------------------------------------------------------------------

## GCP Pricing Calculator Reference

To validate and adjust cost assumptions used in this document, you can
use the official Google Cloud Pricing Calculator:

**Google Cloud Pricing Calculator:**\
https://cloud.google.com/products/calculator

Recommended approach: - Select **Cloud Run** or **Compute Engine** -
Configure region, vCPU, memory, and expected usage - Compare monthly
estimates for both deployment models

This ensures cost projections remain accurate as pricing or workload
patterns change.

------------------------------------------------------------------------

## Future Enhancements

-   Automated cost anomaly detection\
-   Policy-as-code for cost governance\
-   Scheduled environment shutdown\
-   Monthly FinOps optimization reports
