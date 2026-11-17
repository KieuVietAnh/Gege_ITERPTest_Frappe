# Order Management — bài test ERP/CRM

App **Frappe v15** quản lý đơn hàng một mặt hàng, dùng giao diện Desk có sẵn.
Đề gốc: [JD-IT-ERP-bai-test.md](JD-IT-ERP-bai-test.md).
Tài khoản và luồng test từng bước: [HUONG-DAN-TEST.md](HUONG-DAN-TEST.md).
CI khi push/PR lên GitHub: [docs/github-actions.md](docs/github-actions.md).

## Chức năng

- Khách hàng, mặt hàng, số lượng, đơn giá; server tự tính thành tiền và kiểm tra dữ liệu > 0.
- Đơn mới luôn là **Mới**, kể cả khi request truyền trạng thái khác.
- Đơn Mới được sửa và chuyển sang **Đã giao** hoặc **Hủy** bằng nút trên form.
- Đơn kết thúc bị khóa sửa / đổi trạng thái tại server và trên form.
- **Daily Revenue**: mỗi ngày một dòng, số đơn và tổng tiền của đơn Đã giao, theo **ngày tạo đơn**.
  Ví dụ tạo ngày 16, giao ngày 17 thì tính vào ngày 16.
- Chặn tab cũ ghi đè bằng kiểm tra phiên bản và khóa Document sẵn có của Frappe.

## Chạy trên máy hiện tại

Đã cài Ubuntu WSL: Frappe 15.126.1, Python 3.12, Node.js 22, MariaDB 10.11, Redis.

```powershell
.\start.ps1
```

- Đơn hàng: **http://localhost:8000/app/simple-order**.
- Báo cáo: **http://localhost:8000/app/query-report/Daily%20Revenue**.
- Tài khoản `Administrator`; mật khẩu trong `.cache/local-login.txt` (không đưa vào Git/ZIP).
- Bench: `/home/vietanh/frappe-bench`; mã app liên kết với thư mục Windows hiện tại.
- Log: `.cache/bench.log`, `.cache/bench.error.log`. Sửa JS xong dùng Ctrl + Shift + R.
- Sửa JSON xong chạy `bench --site orders.localhost migrate` từ thư mục Bench.

## Cài trên máy khác

Chuẩn bị [môi trường Frappe v15](https://docs.frappe.io/framework/user/en/installation), Bench và dịch vụ MariaDB/Redis trước.
Các lệnh sau chạy trong Linux/WSL tại thư mục Bench:

```bash
bench get-app <URL_REPOSITORY_CUA_APP>
bench new-site orders.localhost
bench --site orders.localhost install-app order_management
bench build
bench start --procfile apps/order_management/Procfile.dev
```

Nếu site đã có, bỏ `new-site`. Tự đặt mật khẩu Administrator khi được hỏi.
Hoàn thành setup wizard, chọn Vietnam, VND và Asia/Ho_Chi_Minh. Mở các URL localhost phía trên.
Không cần ERPNext. `get-app` không tự cài toàn bộ hạ tầng.

Nếu nhận ZIP, giải nén vào thư mục riêng, tạo local Git repo trước khi lấy app:

```bash
cd /duong-dan/toi/thu-muc-da-giai-nen
git init
git add .
git -c user.name="Local Demo" -c user.email="demo@example.invalid" commit -m "Initial app"
cd ~/frappe-bench
bench get-app --soft-link /duong-dan/toi/thu-muc-da-giai-nen
```

Sau đó dùng `new-site`, `install-app`, `build`, `start` như trên.
`Procfile.dev` chọn site `orders.localhost`; đổi tên trong file nếu chọn site khác.
`start.ps1` là tiện ích cho WSL trên máy hiện tại, không phải bộ cài đa nền tảng.

## Test

Trên site phát triển riêng, giữ Bench/Redis đang chạy:

```bash
cd ~/frappe-bench
bench --site orders.localhost set-config allow_tests true
bench --site orders.localhost run-tests --app order_management
node apps/order_management/tests/simple-order-form.test.cjs
```

**14 test server đã qua:** kiểm tra/tính tiền, chuyển trạng thái, khóa sửa/xóa, tab cũ, báo cáo theo ngày tạo và quyền xem báo cáo.
Test Node kiểm tra tính nháp, khóa form, nút thao tác và khôi phục trạng thái khi lưu lỗi.
Đã kiểm tra cài app trên site sạch và build wheel thành công; site thử nghiệm đã được dọn sau kiểm tra.

Test trình duyệt từ Windows (tạo thêm 2 đơn demo mỗi lần chạy):

```powershell
npm install --prefix .cache/ui --no-save --no-package-lock playwright@1.65.1
node .cache/ui/node_modules/playwright/cli.js install chromium --only-shell
$env:NODE_PATH = Join-Path $PWD '.cache/ui/node_modules'
node tests/e2e.cjs
```

Dùng mật khẩu trong `.cache/local-login.txt` và browser headless có profile riêng.
Đã qua luồng tạo đơn → giao/hủy → khóa form → chặn sửa qua API → báo cáo.

## Ảnh minh họa

1. [Tạo đơn, tính tiền nháp](docs/screenshots/01-create-order.png).
2. [Đã giao, khóa sửa](docs/screenshots/02-delivered-order.png).
3. [Đã hủy, khóa sửa](docs/screenshots/03-cancelled-order.png).
4. [Doanh thu theo ngày](docs/screenshots/04-daily-revenue.png).

## Giả định và giới hạn

- Khách hàng/mặt hàng nhập tên, mỗi đơn một mặt hàng; chưa tách danh mục riêng.
- Số lượng 3 chữ số thập phân, đơn giá/thành tiền 2 chữ số; dùng cách làm tròn của Frappe.
- Ngày báo cáo theo `creation` và múi giờ site. Chỉ hiện ngày có đơn Đã giao.
- Quyền dành cho System Manager/Administrator; không cấp quyền xóa cho System Manager.
  Kể cả Administrator cũng không được xóa đơn kết thúc qua thao tác Document thông thường.
- Cho phép sửa dữ liệu và kết thúc đơn trong cùng lần lưu khi trạng thái cũ vẫn là Mới.
- Cấu hình chạy hiện tại dành cho phát triển cục bộ; hosting/production chưa thuộc bản bàn giao này.
- Metadata tác giả còn là `ERP Test` / `dev@example.com` trong `hooks.py` và `pyproject.toml`; thay trước khi nộp.

## Đọc code từ .NET

- `simple_order.json`: Entity + mapping + metadata form.
- `simple_order.py`: nghiệp vụ/validation trước khi lưu Document.
- `simple_order.js`: hành vi form; `simple_order_list.js`: nút/nhãn ở danh sách.
- `report/daily_revenue/`: khai báo báo cáo và truy vấn tổng hợp.
- [Hướng dẫn FE từng bước](docs/frappe-frontend.md).
