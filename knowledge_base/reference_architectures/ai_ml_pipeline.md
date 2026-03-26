# Reference Architecture: AI/ML Pipeline

## Pattern: End-to-End MLOps Platform

### Mô tả
Nền tảng MLOps cho phép xây dựng, triển khai và vận hành mô hình AI/ML ở quy mô production.

### Khi nào áp dụng
- Công ty đã có data platform hoặc đang xây dựng
- Có use case AI cụ thể (prediction, classification, NLP, CV)
- Cần tái sử dụng models cho nhiều ứng dụng
- Pain point: model drift, không có process tái training, không monitor được

### Kiến trúc Mermaid
```mermaid
graph LR
    subgraph DataPrep["Data Preparation"]
        A1[Feature Engineering]
        A2[Feature Store]
        A3[Data Versioning - DVC]
    end

    subgraph Training["Model Training"]
        B1[Experiment Tracking - MLflow]
        B2[Training Pipeline]
        B3[Model Registry]
    end

    subgraph Deployment["Model Deployment"]
        C1[Model Serving - BentoML / TorchServe]
        C2[A/B Testing]
        C3[API Gateway]
    end

    subgraph Monitoring["Monitoring & Ops"]
        D1[Data Drift Detection]
        D2[Model Performance Monitor]
        D3[Retraining Trigger]
    end

    subgraph Apps["Applications"]
        E1[Web App]
        E2[Mobile App]
        E3[Internal Tools]
    end

    A1 --> A2
    A2 --> B2
    A3 --> B2
    B2 --> B1
    B1 --> B3
    B3 --> C1
    C1 --> C2
    C2 --> C3
    C3 --> E1
    C3 --> E2
    C3 --> E3
    C1 --> D1
    C1 --> D2
    D1 --> D3
    D2 --> D3
    D3 --> B2
```

### Technology Stack

| Component | Open Source | Cloud Managed | Enterprise |
|-----------|-------------|---------------|------------|
| Experiment Tracking | MLflow | AWS SageMaker Experiments | Weights & Biases |
| Feature Store | Feast | AWS SageMaker Feature Store | Tecton |
| Model Serving | BentoML / FastAPI | AWS SageMaker Endpoints | Seldon Core |
| Pipeline Orchestration | Kubeflow Pipelines | AWS SageMaker Pipelines | Databricks MLflow |
| Monitoring | Evidently AI | AWS SageMaker Clarify | Arize AI |
| Container Platform | Kubernetes | AWS EKS / Azure AKS | OpenShift |

### Use Cases Phổ biến
1. **Demand Forecasting**: Dự báo nhu cầu / tồn kho
2. **Customer Churn Prediction**: Dự báo khách hàng rời bỏ
3. **Document Intelligence**: OCR + classification tài liệu
4. **Recommendation System**: Gợi ý sản phẩm / nội dung
5. **Anomaly Detection**: Phát hiện gian lận / bất thường

### Lộ trình Triển khai Gợi ý
- **Phase 1** (2-3 tháng): MLflow + 1 use case pilot + basic serving
- **Phase 2** (3-4 tháng): Feature Store + CI/CD cho models + monitoring
- **Phase 3** (3-6 tháng): AutoML + multi-model serving + advanced MLOps

### Chi phí Tham khảo
- ML compute (training + inference): $3,000 - $20,000/tháng
- MLOps platform (cloud): $1,000 - $8,000/tháng
- Data science team: 2-5 FTEs (hoặc outsource)
- Implementation: $50,000 - $200,000

### Rủi ro Chính
1. Model accuracy không đạt kỳ vọng (High) — Mitigation: Pilot với baseline rõ ràng
2. Data pipeline không ổn định (High) — Mitigation: Data quality gates
3. Thiếu kỹ năng ML nội bộ (Medium) — Mitigation: Training + vendor support
4. Model drift trong production (Medium) — Mitigation: Monitoring + auto-retrain
