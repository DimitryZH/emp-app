# Cost Optimization Guide  
## Cloud Run vs Compute Engine

This document describes cost optimization considerations for two Google Cloud deployment models used in this project:

- **Google Compute Engine (VM-based deployment)**
- **Google Cloud Run (serverless container deployment)**

The goal is to evaluate cost efficiency, scalability, and operational overhead for each model, and provide guidance on when to choose one over another.

---

## Cost Model Overview

### Google Compute Engine

**Billing model:**
- Pay for provisioned VM resources (CPU, memory)
- Billed per second while VM is running
- Additional costs for:
  - Persistent disks
  - Load balancer
  - External IPs
  - Cloud SQL
  - Network egress

**Key characteristic:**
Costs are incurred **even when application is idle**.

---

### Google Cloud Run

**Billing model:**
- Pay only for:
  - Request execution time
  - Allocated CPU and memory during request processing
- No cost when service is idle
- Built-in HTTPS load balancing included

**Key characteristic:**
Costs scale **to zero** when no traffic exists.

---

## Baseline Cost Comparison

| Category                    | Compute Engine                | Cloud Run                     |
|----------------------------|-------------------------------|-------------------------------|
| Idle cost                  | Yes (VM always running)       | No (scales to zero)           |
| Auto-scaling               | Manual / autoscaler           | Native request-based scaling |
| Load balancer              | Separate paid service         | Included                      |
| Operations overhead        | VM maintenance required       | Fully managed                 |
| Startup latency            | Always warm                   | Cold start possible           |
| Best for                  | Steady workloads              | Variable / burst workloads   |

---

## Example Scenario

**Enterprise application with:**
- Business hours traffic
- Low night/weekend usage
- Occasional peak loads

### Compute Engine
- VM must run 24/7
- Fixed monthly baseline cost
- Underutilized resources during off-hours

### Cloud Run
- Scales down to zero at night
- Scales automatically during peak
- No cost during idle periods

**Result:**  
Cloud Run significantly reduces cost for non-constant workloads.

---

## Quick Cost Optimization Wins

### For Compute Engine
- Use autoscaling instance groups  
- Apply committed use discounts  
- Right-size VM instance types  
- Schedule non-production shutdown  
- Use preemptible VMs for dev/test  

### For Cloud Run
- Optimize container startup time  
- Reduce allocated CPU/memory per request  
- Set concurrency appropriately  
- Use minimum instances = 0 for non-prod  

---

## Long-term Optimization Strategy

- Migrate suitable services from VM to Cloud Run  
- Refactor monolithic services into smaller containers  
- Implement request-level monitoring  
- Measure cost per request / per user  
- Automate rightsizing recommendations  

---

## Observability for Cost Control

- Enable Cloud Billing export  
- Set budget alerts  
- Monitor:
  - Cost per environment
  - Cost per service
  - Request volume vs spend

---

## Decision Matrix

| Workload Type                  | Recommended Platform |
|--------------------------------|----------------------|
| Constant steady load           | Compute Engine       |
| Variable or bursty load        | Cloud Run            |
| Event-driven workloads         | Cloud Run            |
| Legacy VM-based application    | Compute Engine       |
| Modern containerized services  | Cloud Run            |

---

## FinOps Takeaways

- Cloud Run shifts cost from **capacity-based** to **usage-based**
- Compute Engine provides predictable fixed baseline cost
- Combining both models enables optimal hybrid architecture

---

## Future Enhancements

- Automated cost anomaly detection  
- Policy-as-code for resource limits  
- Scheduled environment shutdown  
- Monthly FinOps review reports  
- Continuous rightsizing recommendations

---

## Author

**Dmitry Zhuravlev**  
Cloud & DevOps Engineer

---

## License

MIT License — free to reuse with attribution.

---