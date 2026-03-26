# Reference Architecture: Data Platform

## Pattern: Modern Data Platform (Lambda Architecture)

### Mô tả
Nền tảng dữ liệu tổng hợp cho doanh nghiệp vừa và lớn, hỗ trợ batch và real-time processing.

### Khi nào áp dụng
- Công ty có > 200 nhân viên
- Dữ liệu từ nhiều nguồn khác nhau (ERP, CRM, IoT, web logs)
- Cần báo cáo và analytics gần real-time
- Pain point: dữ liệu phân tán, không có "single source of truth"

### Kiến trúc Mermaid
```mermaid
graph TD
    subgraph Sources["Data Sources"]
        A1[ERP System]
        A2[CRM System]
        A3[Database]
        A4[APIs / Files]
    end

    subgraph Ingestion["Ingestion Layer"]
        B1[Batch ETL - Apache Airflow]
        B2[Stream - Apache Kafka]
    end

    subgraph Storage["Storage Layer"]
        C1[Data Lake - MinIO / S3]
        C2[Data Warehouse - PostgreSQL / Redshift]
        C3[OLAP - ClickHouse]
    end

    subgraph Processing["Processing Layer"]
        D1[Spark / dbt]
        D2[Data Quality - Great Expectations]
    end

    subgraph Serving["Serving Layer"]
        E1[BI Tool - Metabase / Superset]
        E2[API Layer]
        E3[ML Feature Store]
    end

    A1 --> B1
    A2 --> B1
    A3 --> B1
    A4 --> B2
    B1 --> C1
    B2 --> C1
    C1 --> D1
    D1 --> C2
    D1 --> C3
    D2 --> C2
    C2 --> E1
    C3 --> E1
    C2 --> E2
    C2 --> E3
```

### Technology Stack

| Component | Open Source (< $100K) | Cloud Managed ($100K-$500K) | Enterprise (> $500K) |
|-----------|----------------------|------------------------------|----------------------|
| Orchestration | Apache Airflow | AWS MWAA / Azure Data Factory | Databricks Workflows |
| Data Lake | MinIO | AWS S3 / Azure ADLS | Databricks Delta Lake |
| Data Warehouse | PostgreSQL + dbt | AWS Redshift / Google BigQuery | Snowflake |
| Stream Processing | Apache Kafka + Flink | AWS Kinesis / Azure Event Hubs | Confluent Platform |
| BI / Reporting | Apache Superset | Power BI / Tableau | Tableau Enterprise |
| Data Quality | Great Expectations | AWS Deequ | Monte Carlo |

### Lộ trình Triển khai Gợi ý
- **Phase 1** (3-4 tháng): Data Lake + ETL cơ bản + BI Dashboard
- **Phase 2** (2-3 tháng): Data Quality + Data Catalog + Self-serve Analytics
- **Phase 3** (3-6 tháng): Real-time streaming + Advanced Analytics

### Chi phí Tham khảo
- Infrastructure (cloud): $2,000 - $15,000/tháng tùy quy mô
- Implementation: $30,000 - $150,000 (tùy phức tạp)
- Training & Change Management: $10,000 - $30,000

### Rủi ro Chính
1. Data quality từ hệ thống nguồn (High) — Mitigation: Data quality gates
2. Adoption của người dùng cuối (Medium) — Mitigation: Training + champions
3. Cost overrun khi data volume tăng (Medium) — Mitigation: Lifecycle policies
