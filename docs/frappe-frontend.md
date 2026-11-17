# Cách code giao diện Frappe từ dự án hiện tại

Nếu chưa rõ Desk, Workspace Users và app đơn hàng khác nhau ở đâu, đọc [GIAI-THICH-FRAPPE.md](../GIAI-THICH-FRAPPE.md) trước.

## 1. Thư mục framework nằm ở đâu?

Với bản Docker, mã framework và app nằm trong container. Xem bằng
`docker compose exec backend bash`, rồi `cd /home/frappe/frappe-bench`:

```text
/home/frappe/frappe-bench/               # nằm trong container
├── env/                                # Python virtualenv
├── apps/
│   ├── frappe/                         # mã nguồn framework tải từ GitHub Frappe
│   └── order_management/                # bản code COPY vào image lúc build
├── sites/
│   ├── orders.localhost/               # cấu hình và file riêng của site
│   └── assets/                         # tài nguyên frontend đã build / liên kết
└── logs/
```

Đường dẫn `/home/vietanh/frappe-bench/apps/frappe` bạn hỏi trước đây là của bản
Ubuntu WSL cũ. Bản Docker dùng `/home/frappe/...` và web cổng 8080.
Một Bench có thể chứa nhiều app.

Bạn sửa nghiệp vụ / giao diện của mình tại:

```text
C:\Users\CytekPC\OneDrive\Desktop\testegeg
```

Không sửa trực tiếp `apps/frappe` cho bài này. Đó là mã framework dùng chung;
chỉnh ở đó khó đóng gói bài nộp và dễ xung đột khi cập nhật Frappe.

## 2. Dùng giao diện có sẵn nghĩa là gì?

Bạn khai báo dữ liệu, Frappe dựng các control và nối chúng với thao tác lưu.
Trong .NET, có thể hình dung gần với scaffold Entity + form CRUD, nhưng metadata
của Frappe còn quyết định nhiều hành vi trên form.

Ba file làm việc cùng nhau:

```text
order_management/order_management/doctype/simple_order/
├── simple_order.json     # dữ liệu, control, quyền, trường hiển thị danh sách
├── simple_order.js       # hành vi của form trong trình duyệt
└── simple_order.py       # nghiệp vụ / kiểm tra trên server
```

- JSON: form có những trường nào, kiểu dữ liệu, thứ tự, nhãn, bắt buộc nhập, chỉ đọc.
- JavaScript: người dùng đổi một trường thì giao diện phản ứng ra sao.
- Python: server cho phép lưu hay từ chối; kết quả cuối cùng được lưu là gì.

Frappe có sẵn danh sách, form, tìm kiếm, bộ lọc, phân trang, nút New và Save.
Bạn không cần tự viết HTML cho từng textbox trong cách làm này.

## 3. Ví dụ đổi form bằng JSON

Trong `simple_order.json`, trường đơn giá hiện có:

```json
{
  "fieldname": "unit_price",
  "fieldtype": "Currency",
  "label": "Đơn giá",
  "precision": "2",
  "reqd": 1
}
```

| Thuộc tính | Tác dụng |
| --- | --- |
| `fieldname` | Tên thuộc tính để JS/Python đọc, tương tự property |
| `fieldtype` | Loại control / dữ liệu, ví dụ Data, Float, Currency, Select |
| `label` | Nhãn hiển thị cho người dùng |
| `reqd: 1` | Bắt buộc nhập |
| `read_only: 1` | Control chỉ đọc trên form |
| `in_list_view: 1` | Cho phép trường xuất hiện trong danh sách |
| `field_order` | Thứ tự các trường trên form |

Để thử, bạn có thể đổi `label` thành `Đơn giá bán`, chạy migrate và tải lại trang.
Không cần đổi `fieldname` chỉ để đổi chữ hiển thị. Đổi tên field đã có dữ liệu
là thay đổi schema, cần cân nhắc migration riêng.

Trong PowerShell, lệnh migrate cho môi trường đang cài là:

```powershell
docker compose up -d --build --wait
```

Lệnh này build lại image từ code Windows rồi tự migrate site. Nếu thêm field mới trong JSON, thêm cả vào `fields` và `field_order`.
Các thay đổi JSON được lưu trong repo nên người chấm có thể cài lại.

## 4. Ví dụ JavaScript đã thêm vào app

Phần tính nháp trong `simple_order.js` có dạng sau (file hiện tại còn có handler `refresh` và các nút nghiệp vụ):

```javascript
frappe.ui.form.on("Simple Order", {
    quantity(frm) {
        return update_total_preview(frm);
    },

    unit_price(frm) {
        return update_total_preview(frm);
    },
});

function update_total_preview(frm) {
    const quantity = flt(frm.doc.quantity, 3);
    const unit_price = flt(frm.doc.unit_price, 2);
    return frm.set_value("total", flt(quantity * unit_price, 2));
}
```

Giải thích:

1. `frappe.ui.form.on("Simple Order", ...)` đăng ký sự kiện cho form của DocType đó.
2. `quantity` là tên field, đồng thời là sự kiện khi giá trị field thay đổi.
3. `unit_price` hoạt động tương tự.
4. `frm` là đối tượng form hiện tại, không phải HTTP request.
5. `frm.doc` là dữ liệu đơn hàng đang có trên trình duyệt.
6. `flt` là helper số của Frappe; tham số thứ hai là số chữ số thập phân.
7. `frm.set_value` cập nhật dữ liệu và control trên form; nó trả về Promise.
8. Hàm chung tránh viết phép tính lặp lại cho hai sự kiện.

Đây là tổng nháp để hỗ trợ nhập liệu. `frm.set_value` chưa lưu database.
Khi bạn bấm Save, Frappe gửi Document lên server; Python `validate()` tính lại `total`.
Người gọi API trực tiếp vẫn phải qua kiểm tra server, kể cả khi không chạy JS.

Frappe nạp file `.js` cùng tên DocType theo quy ước; không cần thêm thẻ `<script>`
hay cấu hình `hooks.py` cho Form Script này.

## 5. Cách thử ngay

1. Mở PowerShell tại dự án và chạy `docker compose up -d --build --wait`.
2. Sau khi sửa JS, chạy lại lệnh trên rồi tải lại trang bằng **Ctrl + Shift + R**.
3. Mở `http://localhost:8080/app/simple-order`, chọn **New**.
4. Nhập khách hàng, chọn mã mặt hàng `KB001`, số lượng `2`, đơn giá `150000`.
5. Nhấn Tab hoặc click ra khỏi ô để chốt thay đổi; thành tiền nháp là `300000`.
6. Đổi số lượng thành `3`, nhấn Tab: thành tiền nháp là `450000`, chưa cần Save.
7. Bấm Save, tải lại đơn và kiểm tra kết quả đã lưu.
8. Thử số lượng `0`: tổng nháp có thể là 0 nhưng server phải từ chối Save.

Nếu vẫn thấy mã cũ, chạy clear-cache rồi Ctrl + Shift + R:

```powershell
docker compose exec backend bench --site orders.localhost clear-cache
```

Với Bench chạy trực tiếp, Form Script thường chỉ cần clear-cache và tải lại trang;
JSON cần migrate, bundle JS/CSS cần build. Với Docker hiện tại, code được COPY vào image,
nên luôn chạy lại lệnh Compose có `--build` để cập nhật code trong container.

## 6. Thêm nút hoặc hướng dẫn trên form

App hiện đã có handler `refresh` để khóa form và thêm nút Đã giao/Hủy/báo cáo.
Đoạn dưới là **ví dụ để tự thử**, chưa thêm vào app: chèn các dòng này **bên trong handler `refresh` đang có**.
Không khai báo thêm key `refresh` trùng tên vì sẽ ghi đè handler hiện tại.

```javascript
frm.add_custom_button("Hướng dẫn", () => {
    frappe.msgprint("Thành tiền được server tính lại khi lưu đơn.");
});
```

`refresh` chạy khi form được hiển thị / làm mới. `set_intro` thêm lời hướng dẫn;
`add_custom_button` thêm nút; callback chạy khi bấm nút.
Không dùng `refresh` để tự lưu form, vì việc làm mới có thể xảy ra nhiều lần.

Nếu nút thực hiện nghiệp vụ như giao đơn, cần có kiểm tra tương ứng tại server;
việc ẩn nút hoặc khóa control bằng JavaScript không thay thế kiểm tra quyền / trạng thái.

## 7. Debug và test

Mở F12 trên trình duyệt:

- **Console:** đọc lỗi JS; có thể tạm thêm `console.log(frm.doc)` trong handler.
- **Sources:** tìm `simple_order.js` hoặc đặt `debugger;` trong handler để dừng khi đổi field.
- **Network:** xem request khi bấm Save và kết quả trả về từ server.

Không log mật khẩu hoặc token; bỏ các dòng debug tạm trước khi nộp bài.

Test phần tính nháp bằng Node trong container, chạy từ thư mục repo:

```bash
docker compose exec -T backend node apps/order_management/tests/simple-order-form.test.cjs
```

Test dùng hàm số của Frappe đã cài và form giả lập; không thay cho kiểm tra hiển thị trong browser.

## 8. Nếu muốn giao diện riêng hoàn toàn

Bạn có thể làm page riêng trong Frappe hoặc frontend riêng gọi API Frappe.
Ví dụ React/Vue/Blazor hiển thị theo thiết kế của bạn, còn Frappe giữ database,
đăng nhập, phân quyền và nghiệp vụ. Khi đó bạn phải tự làm thêm các phần UI, gọi API,
đăng nhập và xử lý lỗi mà Desk đang cung cấp.

Với bài test này, bắt đầu bằng **DocType JSON + Form Script JS + controller Python**
là phạm vi phù hợp để hiểu và giải thích được mã.

Tài liệu: [Form Scripts / Form API](https://docs.frappe.io/framework/user/en/api/form),
[tutorial Form Scripts](https://docs.frappe.io/framework/user/en/tutorial/form-scripts),
[Frappe Apps](https://docs.frappe.io/framework/user/en/basics/apps).
