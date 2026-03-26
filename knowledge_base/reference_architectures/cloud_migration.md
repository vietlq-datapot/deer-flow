# Reference Architecture: Cloud Migration & Hybrid

## Pattern: Lift-and-Shift + Modernization

### Mô tả
Chiến lược di chuyển hạ tầng on-premise lên cloud theo phương pháp phân giai đoạn, giảm thiểu rủi ro.

### Khi nào áp dụng
- Công ty đang chạy on-premise hoặc datacenter riêng
- Chi phí vận hành hạ tầng cao
- Cần scale linh hoạt theo mùa vụ / tăng trưởng
- Pain point: hệ thống cũ khó mở rộng, CAPEX cao, khó DR/HA

### Kiến trúc Mermaid
```mermaid
graph TD
    subgraph OnPrem["On-Premise (Hiện tại)"]
        A1[Legacy Apps]
        A2[Databases]
        A3[File Servers]
        A4[Network / Security]
    end

    subgraph Hybrid["Hybrid Connectivity"]
        B1[VPN / Direct Connect]
        B2[Identity Federation - SSO]
        B3[API Gateway]
    end

    subgraph Cloud["Cloud Platform"]
        subgraph IaaS["IaaS - Lift and Shift"]
            C1[VMs - EC2 / Azure VM]
            C2[Block Storage]
            C3[Load Balancer]
        end
        subgraph PaaS["PaaS - Modernization"]
            D1[Containers - EKS / AKS]
            D2[Serverless - Lambda]
            D3[Managed DB - RDS / CosmosDB]
            D4[Object Storage - S3 / Blob]
        end
        subgraph Security["Security & Compliance"]
            E1[IAM / RBAC]
            E2[WAF / DDoS Protection]
            E3[Audit Logging]
        end
    end

    A1 --> B1
    A2 --> B1
    A3 --> B1
    B1 --> C1
    B1 --> D3
    B2 --> E1
    B3 --> D1
    C1 --> D1
    C2 --> D4
    D1 --> D3
    D2 --> D3
    E1 --> D1
    E2 --> C3
    C3 --> D1
```

### Chiến lược 6R
1. **Rehost** (Lift & Shift): Di chuyển nhanh, không thay đổi code
2. **Replatform**: Minor optimization (e.g., managed DB thay self-managed)
3. **Repurchase**: Chuyển sang SaaS (e.g., Salesforce, Workday)
4. **Refactor**: Tái kiến trúc cho cloud-native
5. **Retire**: Tắt hệ thống không còn dùng
6. **Retain**: Giữ on-premise (compliance, latency requirements)

### Technology Stack

| Workload | AWS | Azure | GCP |
|----------|-----|-------|-----|
| Compute | EC2 / ECS / Lambda | Azure VM / AKS / Functions | GCE / GKE / Cloud Run |
| Database | RDS / Aurora / DynamoDB | Azure SQL / CosmosDB | Cloud SQL / Spanner |
| Storage | S3 / EFS / EBS | Blob / Files / Disk | GCS / Filestore |
| Networking | VPC / VPN / Direct Connect | VNet / VPN / ExpressRoute | VPC / VPN / Cloud Interconnect |
| Security | IAM / WAF / Shield | Azure AD / WAF / DDoS | Cloud IAM / Armor |
| Monitoring | CloudWatch / X-Ray | Azure Monitor / App Insights | Cloud Monitoring / Trace |

### Lộ trình Triển khai Gợi ý
- **Phase 1** (2-3 tháng): Assessment + Connectivity + Non-critical apps (Lift & Shift)
- **Phase 2** (3-4 tháng): Core business apps + Database migration + Security hardening
- **Phase 3** (4-6 tháng): Modernization + DR setup + Optimization + Training

### Chi phí Tham khảo
- Cloud infrastructure: $5,000 - $50,000/tháng (tùy workload)
- Migration services: $30,000 - $200,000
- Tools (migration, monitoring): $1,000 - $5,000/tháng
- Training: $5,000 - $20,000

### Rủi ro Chính
1. Downtime trong quá trình migration (High) — Mitigation: Blue/green deployment
2. Cost overrun nếu không optimize (High) — Mitigation: FinOps từ đầu
3. Security & compliance gaps (High) — Mitigation: Security review trước khi migrate
4. Network latency với on-premise (Medium) — Mitigation: Hybrid connectivity cẩn thận
