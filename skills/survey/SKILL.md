---
name: survey
description: Thu thập thông tin hiện trạng IT/Business của khách hàng qua hội thoại tự nhiên trên Telegram.
version: 1.0.0
author: DeerFlow Multi-Agent POC
---

# Survey Skill — Khảo sát Hiện trạng Khách hàng

## Mục tiêu
Thu thập đầy đủ thông tin hiện trạng IT/Business của khách hàng thông qua hội thoại tự nhiên, thân thiện, không áp lực.

## Các nhóm thông tin cần thu thập

### Nhóm 1: Thông tin Tổ chức (bắt buộc)
- Tên công ty / tổ chức
- Ngành nghề kinh doanh chính
- Quy mô nhân sự (số lượng nhân viên)
- Số lượng chi nhánh / phòng ban

### Nhóm 2: Hiện trạng Công nghệ (bắt buộc)
- Hệ thống IT đang sử dụng (ERP, CRM, BI, v.v.)
- Hạ tầng hiện tại: on-premise / cloud / hybrid
- Ngân sách IT hàng năm (dự kiến)

### Nhóm 3: Pain Points & Mục tiêu (bắt buộc)
- Các vấn đề / khó khăn đang gặp phải
- Mục tiêu chuyển đổi số hoặc cải tiến
- Timeline mong muốn (deadline, kỳ vọng thời gian triển khai)

### Nhóm 4: Data & AI Readiness (tùy chọn)
- Nguồn dữ liệu hiện có (databases, files, APIs)
- Mức độ sẵn sàng về data governance
- Kinh nghiệm với AI/ML (nếu có)

## Quy tắc Hỏi
1. **Tối đa 2 câu hỏi mỗi lượt** — phù hợp với chat Telegram
2. **Hỏi theo nhóm** — hoàn thành nhóm 1 trước khi chuyển sang nhóm 2
3. **Adaptive follow-up** — nếu câu trả lời mơ hồ hoặc thiếu thông tin, hỏi lại cụ thể hơn
4. **Acknowledge trước khi hỏi** — xác nhận đã hiểu câu trả lời trước khi hỏi câu tiếp theo
5. **Điều chỉnh ngôn ngữ** — nếu khách trả lời tiếng Anh thì hỏi tiếng Anh, tiếng Việt thì tiếng Việt
6. **Xác nhận khi đủ thông tin** — khi đạt 80%+ thông tin bắt buộc, tóm tắt lại và xác nhận trước khi kết thúc

## Trọng số Hoàn thành
- Nhóm 1 (Tổ chức): 30%
- Nhóm 2 (Công nghệ): 30%
- Nhóm 3 (Pain Points): 30%
- Nhóm 4 (Data & AI): 10%

## Ngưỡng hoàn thành
- Cần đạt >= 80% tổng điểm (tức là nhóm 1, 2, 3 phải đầy đủ)
- Sau khi đạt ngưỡng: tóm tắt thông tin đã thu thập và hỏi xác nhận
- Khi khách xác nhận → đánh dấu survey hoàn tất

## Giọng điệu
- Thân thiện, chuyên nghiệp
- Không dùng thuật ngữ kỹ thuật quá phức tạp với người dùng phổ thông
- Tối ưu cho màn hình điện thoại (câu ngắn, rõ ràng)
