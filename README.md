# Order Management — bài test ERP/CRM

Repo này là mã nguồn app **`order_management` cho Frappe v15**, cài được bằng `bench get-app` để nộp theo đề.
Docker Compose đi kèm giúp chạy thử toàn bộ môi trường local bằng một lệnh. App dùng giao diện Desk có sẵn.
Đề bài: [JD-IT-ERP-bai-test.md](JD-IT-ERP-bai-test.md).

## Chạy local bằng một lệnh

Cài và mở **Docker Desktop**, chọn Linux containers. Trong thư mục repo, chạy:

```bash
docker compose up -d --build --wait
```

Lần đầu cần tải image và build Frappe, có thể mất vài phút. Compose tự tạo database,
site `orders.localhost`, cài app và hoàn thành setup; không cần cài Python, Node.js hay Bench trên máy.

- Đơn hàng: **http://localhost:8080/app/simple-order**.
- Báo cáo: **http://localhost:8080/app/query-report/Daily%20Revenue**.
- Đăng nhập: **Administrator** / **admin** (tài khoản demo local).

MariaDB, Redis, backend, worker, scheduler, WebSocket và Nginx đều chạy trong Docker.
Cổng web chỉ mở trên máy local. Dữ liệu nằm trong Docker volumes; `docker compose down`
dừng app và giữ dữ liệu. Không thêm `--volumes` nếu muốn giữ dữ liệu.
Bản Docker tạo database riêng, không tự nhập dữ liệu từ bản WSL cũ ở cổng 8000.
Sau khi sửa code, chạy lại lệnh trên để build và cập nhật app rồi Ctrl + Shift + R.

## Cài app bằng `bench get-app` theo đề bài

Nếu đã có môi trường **Frappe v15 / Bench**, MariaDB và Redis trong Linux/WSL,
chạy tại thư mục Bench:

```bash
bench get-app https://github.com/KieuVietAnh/Gege_ITERPTest_Frappe.git
bench new-site orders.localhost
bench --site orders.localhost install-app order_management
bench build
bench start --procfile apps/order_management/Procfile.dev
```

Bỏ `new-site` nếu site đã có. Tự đặt mật khẩu Administrator khi tạo site, hoàn thành
setup wizard với Vietnam / VND / Asia/Ho_Chi_Minh. Bản Bench này dùng **http://localhost:8000/app/simple-order**.
`Procfile.dev` chọn site `orders.localhost`; sửa tên nếu dùng site khác. Không cần ERPNext.

## Chức năng và giả định

- Một đơn có tên khách hàng, tên mặt hàng, số lượng, đơn giá. Server kiểm tra số lượng/đơn giá > 0 và tính thành tiền.
- Đơn mới luôn là **Mới**; được sửa và chuyển sang **Đã giao** hoặc **Hủy**. Đơn kết thúc bị khóa sửa, đổi trạng thái và xóa ở server.
- **Daily Revenue** đếm đơn và cộng tiền **Đã giao**, nhóm theo **ngày tạo đơn**; bỏ qua Mới/Hủy.
- Khách hàng/mặt hàng nhập tên, chưa tách danh mục. Số lượng 3 chữ số thập phân, tiền 2 chữ số, làm tròn theo Frappe.
- Báo cáo theo múi giờ site, chỉ hiện ngày có đơn Đã giao. Quyền dành cho System Manager/Administrator.
- Các chức năng bắt buộc đã có. Metadata tác giả hiện là `ERP Test` / `dev@example.com` trong `hooks.py` và `pyproject.toml`.

## Kiểm tra và đọc code

Sau khi app Docker chạy:

```bash
docker compose exec -T backend bash apps/order_management/docker/test.sh
```

Gồm test server cho nghiệp vụ/báo cáo, test JavaScript của form và test khởi tạo Docker.
Luồng test thủ công và browser test: [HUONG-DAN-TEST.md](HUONG-DAN-TEST.md).

- `simple_order.json`: schema, quyền và metadata form.
- `simple_order.py`: validation và quy tắc lưu đơn.
- `simple_order.js` / `simple_order_list.js`: hành vi form và danh sách.
- `report/daily_revenue/`: báo cáo tổng hợp.

[Giải thích Frappe cho người làm .NET](GIAI-THICH-FRAPPE.md) · [Hướng dẫn code FE](docs/frappe-frontend.md).

Ảnh minh họa: [Tạo đơn](docs/screenshots/01-create-order.png),
[Đã giao](docs/screenshots/02-delivered-order.png),
[Hủy](docs/screenshots/03-cancelled-order.png),
[Báo cáo](docs/screenshots/04-daily-revenue.png).
