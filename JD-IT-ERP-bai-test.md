# Bài test tại nhà — Lập trình viên ERP/CRM

- **Hạn nộp:** 48 giờ kể từ khi nhận đề.
- **Công nghệ:** Frappe (ưu tiên) hoặc framework bạn quen (Django, Laravel, Express…).
- **AI:** được dùng, nhưng ở vòng phỏng vấn bạn cần giải thích được mã mình nộp.

## Đề bài: app nhỏ quản lý đơn hàng

1. **Đơn hàng** gồm khách hàng, mặt hàng, số lượng, đơn giá, thành tiền. Mỗi đơn một mặt hàng là đủ.
2. **Thành tiền** = số lượng × đơn giá, do server tự tính. Số lượng và đơn giá phải lớn hơn 0.
3. **Trạng thái:** đơn mới tạo ở trạng thái **Mới**, từ Mới chuyển sang **Đã giao** hoặc **Hủy**. Đơn đã giao hay đã hủy thì không sửa, không đổi trạng thái được nữa.
4. **Báo cáo doanh thu theo ngày:** mỗi ngày một dòng gồm số đơn và tổng thành tiền, chỉ tính đơn **Đã giao**, theo ngày tạo đơn.
5. **Giao diện** chỉ cần đủ dùng. Với Frappe, màn hình Desk có sẵn là được.

## Cần nộp

- **Mã nguồn:** link repo (GitHub, GitLab…) hoặc tệp nén. Nếu dùng Frappe: một app cài được bằng `bench get-app`.
- **README ngắn:** cách cài và chạy, các giả định bạn đã đặt, phần nào chưa làm xong. Chưa xong hết vẫn nộp được.
- **Ảnh chụp màn hình** (hoặc video ngắn) cho thấy: tạo đơn, đổi trạng thái, xem báo cáo.
- Có test tự động là điểm cộng.

Trả lời email đã nhận đề, tiêu đề `[IT-ERP] Bài test – Họ tên`.

## Tiêu chí đánh giá

- Làm đúng các yêu cầu trên, nhất là phần kiểm tra ở server.
- Mã dễ đọc; README đủ để người khác chạy lại.
- Ở vòng phỏng vấn: giải thích được mã và sửa được khi yêu cầu thay đổi.
