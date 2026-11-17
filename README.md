# Order Management — bước đầu học Frappe từ .NET

Đây là **bản khởi tạo để học cấu trúc**, chưa phải bản hoàn thành bài test.
Mục tiêu: đọc được một DocType, hiểu server xử lý lúc lưu, sau đó mới thêm nghiệp vụ.

## Đã có / chưa có

- App Python tên `order_management`, hướng tới **Frappe v15**.
- DocType `Simple Order`: khách hàng, mặt hàng, số lượng, đơn giá, thành tiền, trạng thái.
- Desk dùng định nghĩa DocType để dựng danh sách và form nhập đơn.
- Server kiểm tra số lượng / đơn giá lớn hơn 0 và tự tính thành tiền mỗi lần lưu.
- Bước này chỉ có trạng thái **Mới**, chưa cho chuyển trạng thái.
- Có test Frappe cho phần nghiệp vụ ban đầu.

**Chưa làm:** Đã giao / Hủy, khóa đơn sau khi kết thúc, báo cáo doanh thu, ảnh/video bài nộp.
Chưa có React, giao diện riêng, danh mục khách hàng/mặt hàng hoặc ERPNext.

## Đối chiếu với .NET

| Trong .NET | Trong app Frappe này |
| --- | --- |
| `.csproj` | `pyproject.toml`: thông tin package và công cụ đóng gói |
| `namespace` / assembly | Package Python: thư mục có `__init__.py` |
| Entity + cấu hình mapping + metadata form | DocType trong `simple_order.json` |
| Entity instance | Document, ví dụ một đơn hàng cụ thể |
| Validation / nghiệp vụ trước khi `SaveChanges()` | `SimpleOrder.validate()` trong `simple_order.py` |
| EF Core migrations | Frappe đồng bộ schema từ DocType khi install / migrate; data migration viết trong patches |
| Controller API cơ bản | Frappe có API thao tác Document sẵn; bước này chưa cần tự viết endpoint |
| Trang quản trị CRUD | Desk tạo list/form từ DocType |
| `Program.cs`, cấu hình mở rộng | Frappe khởi động ứng dụng; `hooks.py` khai báo metadata và các điểm mở rộng |
| xUnit / NUnit | `FrappeTestCase` dựa trên Python `unittest` |

Các đối chiếu trên giúp làm quen, không phải tương đương hoàn toàn.
`SimpleOrder` là controller của Document, không phải ASP.NET HTTP Controller.
Không cần tự thêm Repository, Service và Controller cho thao tác lưu đơn cơ bản này.

## Cấu trúc cần đọc

```text
testegeg/                            # thư mục gốc của app, có pyproject.toml
├── JD-IT-ERP-bai-test.md             # đề gốc
├── pyproject.toml                   # package/build; Frappe do Bench quản lý
├── README.md
└── order_management/                # package Python của app
    ├── __init__.py                  # phiên bản app
    ├── hooks.py                     # thông tin app / điểm mở rộng
    ├── modules.txt                  # đăng ký module Order Management
    ├── patches.txt                  # danh sách data migration, hiện chưa có
    ├── public/                      # tài nguyên tĩnh, hiện chưa có
    └── order_management/            # module nghiệp vụ Order Management
        └── doctype/
            └── simple_order/
                ├── simple_order.json
                ├── simple_order.py
                └── test_simple_order.py
```

Hai thư mục `order_management` lồng nhau là quy ước **app → module** của Frappe.
Các file `__init__.py` rỗng đánh dấu package Python; không chứa nghiệp vụ.

Đọc theo thứ tự:

1. `simple_order.json`: `fieldname` là tên thuộc tính; `fieldtype` là loại dữ liệu;
   `reqd` bắt buộc nhập; `read_only` chỉ đọc trên form.
2. `simple_order.py`: lớp kế thừa `Document`; Frappe gọi `validate()` khi lưu.
3. `test_simple_order.py`: ví dụ tạo, lưu, sửa và tải lại Document.
4. `hooks.py`, `modules.txt`, `pyproject.toml`: cách app được đăng ký / đóng gói.

Luồng lưu: **Form Desk → server Frappe → validate() → database → trả kết quả cho form**.
`read_only` giúp giao diện; server vẫn tính lại `total` để không tin dữ liệu người dùng gửi.
`customer_name`, `item_name` là hai trường tên đơn giản; chưa liên kết danh mục riêng.

## Chạy app

App này cần chạy **bên trong Frappe Bench**. Không chạy bằng `python simple_order.py`.
Bench quản lý Frappe, app và site; một site có database/cấu hình riêng.

### 1. Chuẩn bị môi trường Linux / WSL

Trên Windows dùng Ubuntu trong WSL. Làm theo [hướng dẫn cài Frappe](https://docs.frappe.io/framework/user/en/installation),
chọn dependency phù hợp **v15**, gồm Python, Node/Yarn, MariaDB, Redis và Bench CLI.
Ví dụ chọn Python 3.12, Node 22 và MariaDB 10.6+ cho môi trường v15.
Các lệnh bên dưới chạy trong terminal Ubuntu, sau khi các dependency đã sẵn sàng.
Không dùng Python 3.14 cho môi trường v15 của dự án này.

Nên để Bench trong filesystem Linux (`~/frappe-bench`), giữ mã nguồn đang học tại thư mục hiện tại.

```bash
bench init --frappe-branch version-15 --python python3.12 ~/frappe-bench
cd ~/frappe-bench
bench new-site orders.localhost
bench get-app --soft-link /mnt/c/Users/CytekPC/OneDrive/Desktop/testegeg
bench --site orders.localhost install-app order_management
bench --site orders.localhost set-config developer_mode 1
bench use orders.localhost
bench start
```

`bench new-site` yêu cầu tài khoản database và mật khẩu Administrator cho site.
`get-app --soft-link` liên kết mã nguồn này vào Bench để sửa ở đây và chạy trong WSL.
Không chạy `bench new-app order_management` nữa vì mã app đã có.

Mở `http://orders.localhost:8000/app`, đăng nhập bằng `Administrator` và mật khẩu vừa đặt.
Nếu hostname không phân giải, thử `http://localhost:8000/app` sau khi đã `bench use orders.localhost`.
Hoàn thành trình thiết lập lần đầu, chọn tiền tệ VND và múi giờ Asia/Ho_Chi_Minh.
Tìm **Simple Order** trong thanh tìm kiếm của Desk, hoặc mở:

```text
http://orders.localhost:8000/app/simple-order
```

Nhấn **New**, nhập khách hàng, mặt hàng, số lượng `2`, đơn giá `150000`, rồi **Save**.
Kết quả mong đợi: mã `ORD-00001` (trên database mới), thành tiền `300000`, trạng thái `Mới`.
Thành tiền được cập nhật sau khi lưu, chưa có tính nháp trên trình duyệt.

### 2. Sau khi sửa mã

- Sửa controller `.py`: Bench ở chế độ dev thường tự tải lại mã server.
- Sửa DocType `.json`: chạy lệnh dưới từ thư mục Bench rồi tải lại trang.

```bash
bench --site orders.localhost migrate
```

### 3. Khi có repository để nộp

Đẩy **thư mục chứa `pyproject.toml`** lên repo. Trên một Bench v15 đã sẵn sàng:

```bash
bench get-app <URL_REPOSITORY>
bench --site <TEN_SITE> install-app order_management
```

Đổi `ERP Test` / `dev@example.com` trong `pyproject.toml` và `hooks.py` thành thông tin của bạn trước khi nộp.

## Test

Trên **site phát triển riêng**, trong terminal thứ hai tại `~/frappe-bench`
(giữ `bench start` chạy ở terminal thứ nhất):

```bash
bench --site orders.localhost set-config allow_tests true
bench --site orders.localhost run-tests --app order_management
```

Test cần Frappe + database + Redis; không chạy trực tiếp bằng `python -m unittest` trên Windows.

## Giả định cho bước khởi tạo

- Khách hàng / mặt hàng nhập tên, không có bảng danh mục riêng.
- Số lượng cho phép lẻ, tối đa 3 chữ số thập phân; đơn giá và thành tiền 2 chữ số.
- Dùng cách làm tròn của Frappe; tiền tệ lấy theo cấu hình site.
- Chỉ cấp thao tác cho System Manager / Administrator trong môi trường học;
  chưa cấp quyền xóa đơn và chưa thiết kế vai trò nghiệp vụ riêng.
- Trạng thái luôn được server đặt về `Mới`; bước tiếp theo sẽ thay bằng quy tắc chuyển trạng thái.

## Tình trạng kiểm chứng khi khởi tạo

Mã nguồn được tạo theo cấu trúc app Frappe v15.
Đã kiểm tra cú pháp Python và cấu trúc JSON/TOML của package bằng Python 3.12.
Chưa xác nhận cài và chạy trên site thực: Docker Engine chưa chạy,
và lệnh liệt kê WSL bị từ chối truy cập trong phiên khởi tạo.
Thử đóng gói wheel cũng chưa hoàn tất vì phiên này không kết nối được PyPI
để tải `flit_core` (build backend), không phải lỗi đã xác định trong mã app.
Các test Frappe cần được chạy bằng các lệnh ở trên khi có môi trường.

## Bước tiếp theo

1. Chạy thử form, hiểu sự liên kết giữa JSON, Python và database.
2. Thêm chuyển `Mới → Đã giao / Hủy`, khóa sửa tại server và test.
3. Thêm báo cáo doanh thu theo ngày tạo, chỉ lấy đơn đã giao.
4. Cài thử trên site sạch, chụp ảnh và hoàn thiện README bài nộp.

Tham khảo: [DocType](https://docs.frappe.io/framework/user/en/basics/doctypes),
[Controller](https://docs.frappe.io/framework/user/en/basics/doctypes/controllers),
[tạo app](https://docs.frappe.io/framework/user/en/tutorial/create-an-app).
