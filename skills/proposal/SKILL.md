---
name: proposal
description: Sinh proposal kiến trúc giải pháp chuyên nghiệp từ dữ liệu khảo sát khách hàng.
version: 1.0.0
author: DeerFlow Multi-Agent POC
---

# Proposal Skill — Thiết kế Kiến trúc & Sinh Proposal

## Mục tiêu
Phân tích dữ liệu khảo sát từ Survey Agent và sinh ra proposal kiến trúc giải pháp Data & AI chuyên nghiệp, có cơ sở dữ liệu thực tế.

## Cấu trúc Output Bắt buộc

### 1. Executive Summary (1 đoạn, 3-5 câu)
- Tóm tắt bài toán và giải pháp đề xuất
- Nhấn mạnh business value và ROI

### 2. Phân tích Hiện trạng
- Tóm tắt tình hình từ survey data (KHÔNG bịa thêm)
- Liệt kê rõ các điểm mạnh / điểm yếu / cơ hội

### 3. Kiến trúc Giải pháp Đề xuất
- **Architecture Diagram**: BẮT BUỘC dùng Mermaid syntax
  - Diagram phải hiển thị rõ các component chính và luồng dữ liệu
  - Dùng `graph TD` hoặc `graph LR` tùy độ phức tạp
- **Technology Stack**: Bảng component → technology → mục đích
- **Integration Points**: Danh sách điểm tích hợp với hệ thống hiện tại

### 4. Lộ trình Triển khai (Phased Approach)
- Chia thành 2-4 phase
- Mỗi phase: tên, mục tiêu, thời gian, danh sách công việc chính, deliverables

### 5. Ước tính Chi phí & ROI
- Chi phí theo phase (setup, licensing, implementation, training)
- Ước tính ROI và payback period
- Ghi rõ assumptions

### 6. Rủi ro & Mitigation
- Liệt kê top 3-5 rủi ro chính
- Mỗi rủi ro: mức độ (Low/Med/High), xác suất, kế hoạch giảm thiểu

## Quy tắc Sinh Proposal
1. **Data-driven**: Chỉ đề xuất giải pháp dựa trên survey data thực tế
2. **Pain-point mapping**: Mỗi pain point phải được address bởi ít nhất 1 giải pháp cụ thể
3. **Phù hợp ngân sách**: Technology stack phải phù hợp với budget_range đã khảo sát
4. **Phù hợp quy mô**: Giải pháp phải scale với quy mô công ty
5. **Timeline thực tế**: Lộ trình phải khả thi với timeline mong muốn của khách hàng
6. **Tone**: Chuyên nghiệp, data-driven, tập trung vào business value

## Reference Architecture Patterns
Sử dụng knowledge base để tham khảo các pattern phù hợp:
- `data_platform.md`: Nền tảng dữ liệu (Data Lake, Data Warehouse, ETL)
- `ai_ml_pipeline.md`: Pipeline AI/ML (MLOps, Feature Store, Inference)
- `cloud_migration.md`: Cloud migration và hybrid architecture

## Technology Mapping theo Ngân sách
- **< $100K**: Open-source stack (Apache Airflow, MinIO, PostgreSQL, MLflow)
- **$100K - $500K**: Managed cloud services (AWS/Azure/GCP PaaS)
- **> $500K**: Enterprise solutions (Databricks, Snowflake, SageMaker Enterprise)
