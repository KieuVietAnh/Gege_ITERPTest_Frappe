# Order Management — bài test ERP/CRM

App **`order_management` cho Frappe v15**, dùng giao diện Desk, không cần ERPNext.
Đáp ứng [đề bài](JD-IT-ERP-bai-test.md): server tính tiền, kiểm tra số lượng/đơn giá > 0;
đơn **Mới → Đã giao hoặc Hủy**, đơn kết thúc không sửa; doanh thu chỉ tính Đã giao theo **ngày tạo đơn**.
Có thêm phân quyền Admin/Sale/Kho, danh mục hàng và lịch sử nhập/xuất kho.

## Cách 1: cài bằng `bench get-app`

Cần môi trường **Frappe v15 / Bench**, MariaDB và Redis trên Linux/WSL. Tại thư mục Bench:

```bash
bench get-app https://github.com/KieuVietAnh/Gege_ITERPTest_Frappe.git
bench new-site orders.localhost
bench --site orders.localhost install-app order_management
bench build
bench start --procfile apps/order_management/Procfile.dev
```

Bỏ `new-site` nếu site đã có. Đăng nhập **Administrator** bằng mật khẩu đặt khi tạo site;
hoàn thành setup wizard với Vietnam / VND / Asia/Ho_Chi_Minh.
Mở **http://localhost:8000/app/order-management**.
Nếu dùng tên site khác, thay `orders.localhost` trong lệnh và `Procfile.dev`.

## Cách 2: chạy bằng Docker

Cài và mở **Docker Desktop** (Linux containers), tải/clone repo, chạy tại thư mục repo:

```bash
docker compose up -d --build --wait
```

Compose tự dựng database, Redis, Frappe và cài app. Lần đầu cần tải/build image.
Mở **http://localhost:8080/app/order-management**, đăng nhập **Administrator / admin**.
Dừng bằng `docker compose down`; không thêm `--volumes` nếu muốn giữ dữ liệu.

## Tài khoản, dữ liệu và hướng dẫn test

**[HUONG-DAN-TEST.md](HUONG-DAN-TEST.md)**: tài khoản/mật khẩu từng role, sáu đơn có sẵn,
mặt hàng/tồn kho, các bước thao tác và kết quả mong đợi, kiểm tra phân quyền và chạy test tự động.

Seed tự chạy khi install/migrate: **4 nhân viên, 3 mặt hàng, 6 đơn (3 đơn mỗi Sale)**.
Chạy lại không reset mật khẩu, đơn hoặc cộng lại tồn. Đổi mật khẩu demo trước khi mở web công khai.

```bash
docker compose exec -T backend bash apps/order_management/docker/test.sh
```

## Giả định và giới hạn

- Mỗi đơn một mặt hàng, một kho chung. Sale quản lý đơn mình tạo; Kho xử lý đơn được giao; Admin xem mọi đơn/doanh thu.
- Xác nhận Đã giao đồng thời xuất kho; mỗi lần nhập/xuất lưu chứng từ, người thực hiện và tồn trước/sau. Khóa DB và transaction chống xuất trùng/vượt tồn.
- Chưa giữ chỗ tồn, giao từng phần, hoàn hàng hoặc nhiều kho. Đơn Mới chưa trừ tồn nên Hủy không hoàn kho.
- Lịch sử kho không dựng lại giao dịch cũ; seed giữ dữ liệu đã có. Các chức năng bắt buộc của đề đã hoàn thành.

Chi tiết: [Luồng trạng thái và kho](docs/stock-flow.md).
Ảnh: [Tạo đơn](docs/screenshots/01-create-order.png) · [Đã giao](docs/screenshots/02-delivered-order.png) ·
[Hủy](docs/screenshots/03-cancelled-order.png) · [Báo cáo](docs/screenshots/04-daily-revenue.png).
