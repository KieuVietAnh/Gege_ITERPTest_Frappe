# Hướng dẫn tài khoản và kiểm thử Order Management

Hướng dẫn cho bản demo đang chạy trên máy hiện tại, site `orders.localhost`.
Không cần tài khoản AWS để sử dụng app cục bộ.

## 1. Tài khoản nào dùng để test?

Danh sách tài khoản đã kiểm tra trực tiếp trên site:

| Tài khoản | Mật khẩu | Dùng để làm gì? |
| --- | --- | --- |
| `Administrator` | Xem dòng `Password:` trong [.cache/local-login.txt](.cache/local-login.txt) | Đăng nhập Desk, tạo/sửa đơn Mới, giao/hủy đơn, xem báo cáo |
| `Guest` | Không có | Đại diện cho người chưa đăng nhập; không dùng để đăng nhập và không được xem dữ liệu đơn hàng/báo cáo |

**Hiện chỉ có một tài khoản đăng nhập để test: `Administrator`.**
Chưa tạo tài khoản riêng cho nhân viên/kế toán; đề không yêu cầu quy trình duyệt giữa nhiều vai trò.
`System Manager` là **vai trò được cấp quyền trong app**, không phải tên tài khoản.

Phân biệt để tránh nhập nhầm:

- `Administrator`: tài khoản của ứng dụng web Frappe.
- `vietanh`: user của Ubuntu WSL, không phải tài khoản web.
- `ERP Test` / `dev@example.com`: metadata tác giả trong mã nguồn, không phải tài khoản web.
- Tài khoản database cũng không dùng để đăng nhập màn hình web.

File mật khẩu nằm trong `.cache`, đã được Git và ZIP bài nộp bỏ qua.
Hướng dẫn này không chứa mật khẩu trực tiếp. Nếu cài app trên site/máy mới,
dùng mật khẩu Administrator bạn tự đặt lúc chạy `bench new-site`; các tài khoản và mật khẩu cũ không tự đi theo mã nguồn.

## 2. Khởi động và đăng nhập

Mở PowerShell tại thư mục dự án:

```powershell
cd C:\Users\CytekPC\OneDrive\Desktop\testegeg
.\start.ps1
```

Sau khi thấy `Frappe is running`:

1. Mở [màn hình đăng nhập](http://localhost:8000/login).
2. Username/email: nhập `Administrator`.
3. Password: lấy từ dòng `Password:` trong [file mật khẩu cục bộ](.cache/local-login.txt).
4. Bấm **Login**. Nếu trình duyệt đã đăng nhập thì có thể mở danh sách đơn luôn.

Hai màn hình chính:

| Màn hình | Địa chỉ |
| --- | --- |
| Danh sách đơn hàng | http://localhost:8000/app/simple-order |
| Báo cáo doanh thu | http://localhost:8000/app/query-report/Daily%20Revenue |

Nếu giao diện còn mã cũ sau khi sửa code, nhấn **Ctrl + Shift + R**.

## 3. Luồng nghiệp vụ cần nhớ

```text
Đăng nhập → Tạo đơn → Save → Mới
                              ├── Sửa dữ liệu → Save → vẫn Mới
                              ├── Đã giao → xác nhận Yes → khóa đơn → tính vào báo cáo
                              └── Hủy     → xác nhận Yes → khóa đơn → không tính vào báo cáo
```

| Trạng thái | Sửa dữ liệu | Đổi trạng thái | Tính doanh thu |
| --- | --- | --- | --- |
| Mới | Có | Sang Đã giao hoặc Hủy | Không |
| Đã giao | Không | Không | Có, theo ngày tạo đơn |
| Hủy | Không | Không | Không |

**Trạng thái là trường chỉ đọc.** Để đổi trạng thái, dùng nút **Đã giao** hoặc **Hủy** trên đầu form.
Hai nút này chỉ xuất hiện sau khi đơn mới đã được lưu lần đầu.

## 4. Ghi nhận báo cáo ban đầu

Trước khi tạo thêm đơn, mở báo cáo và ghi lại số đơn / doanh thu của hôm nay.
Các bước test bên dưới so sánh phần **tăng thêm**, tránh nhầm dữ liệu demo cũ.

Tại thời điểm viết hướng dẫn, ngày **17/11/2026**, site đang có:

| Đơn demo | Trạng thái | Thành tiền | Có trong doanh thu? |
| --- | --- | --- | --- |
| [ORD-00002](http://localhost:8000/app/simple-order/ORD-00002) | Mới | 300.000 | Không |
| [ORD-00004](http://localhost:8000/app/simple-order/ORD-00004) | Đã giao | 300.000 | Có |
| [ORD-00005](http://localhost:8000/app/simple-order/ORD-00005) | Hủy | 300.000 | Không |
| [ORD-00006](http://localhost:8000/app/simple-order/ORD-00006) | Đã giao | 300.000 | Có |
| [ORD-00007](http://localhost:8000/app/simple-order/ORD-00007) | Hủy | 300.000 | Không |

Báo cáo lúc kiểm tra: **2 đơn đã giao, tổng 600.000**, thuộc ngày tạo **17/11/2026**.
Đây là dữ liệu tại lúc viết, không phải con số cố định mà mọi lần test đều phải giống.
Site còn có các đơn Mới khác; chúng không làm tăng doanh thu.
Khi cài trên site mới, các bản ghi demo này không được tạo tự động.

## 5. Test tạo đơn và sửa khi còn Mới

1. Mở danh sách đơn, bấm **Add Simple Order** (hoặc **New** tùy vị trí hiển thị).
2. Nhập:

   | Trường | Giá trị |
   | --- | --- |
   | Khách hàng | TEST - Giao hàng |
   | Mặt hàng | Bàn phím |
   | Số lượng | 2 |
   | Đơn giá | 150000 |

3. Nhấn **Tab** hoặc click ra khỏi ô đơn giá để chốt thay đổi.
4. Thành tiền nháp phải là **300.000**, trạng thái **Mới**.
5. Bấm **Save**, ghi lại mã `ORD-xxxxx` mà hệ thống tạo.
6. Đổi số lượng thành `3`, nhấn Tab: thành tiền nháp phải thành **450.000**.
7. Bấm Save, tải lại trang: số lượng vẫn `3`, thành tiền vẫn **450.000**, trạng thái vẫn Mới.
8. Kiểm tra báo cáo: đơn này **chưa** được tính vào doanh thu.

Kết quả cần đạt:

- Không nhập tay được thành tiền; server vẫn tự tính lại khi lưu.
- Khi còn Mới, khách hàng, mặt hàng, số lượng và đơn giá vẫn sửa được.
- Đơn mới được gán trạng thái Mới tại server.

## 6. Test dữ liệu sai

Dùng **một đơn Mới riêng** để thử, không thử sửa đơn đã kết thúc.
Mỗi lần thử một trường hợp, bấm Save rồi sửa về giá trị hợp lệ trước khi thử tiếp.

| Trường hợp | Kết quả mong đợi |
| --- | --- |
| Bỏ trống khách hàng | Không lưu được; thông báo trường bắt buộc |
| Bỏ trống mặt hàng | Không lưu được; thông báo trường bắt buộc |
| Số lượng = 0 | Không lưu được |
| Số lượng = -1 | Không lưu được |
| Đơn giá = 0 | Không lưu được |
| Đơn giá = -1 | Không lưu được |
| Số lượng = 1,5; đơn giá = 10,25 | Lưu hợp lệ; thành tiền 15,38 theo cách làm tròn hiện tại |

Nhập dấu thập phân theo cách hiển thị trên form. Với cấu hình hiện tại,
form có thể hiển thị `150.000,00` thay vì `150000.00`.
Thông báo ở trình duyệt không phải bằng chứng duy nhất: các test server/API ở cuối file cũng kiểm tra việc từ chối dữ liệu sai.

## 7. Test giao hàng và khóa đơn

Dùng đơn **TEST - Giao hàng** ở mục 5, hiện có số lượng 3, thành tiền 450.000.

1. Mở đơn đã lưu, kiểm tra trạng thái còn **Mới**.
2. Bấm nút **Đã giao** trên đầu form.
3. Hộp xác nhận cho biết sau khi lưu sẽ không sửa được nữa; bấm **Yes**.
4. Chờ lưu xong và hộp xác nhận đóng.
5. Kiểm tra:
   - Trạng thái **Đã giao**, có thông báo `Đơn đã kết thúc, chỉ được xem.`
   - Các trường nhập chuyển sang chỉ đọc.
   - Không còn nút Save, Đã giao hoặc Hủy.
6. Tải lại trang: đơn vẫn Đã giao và chỉ đọc.
7. Bấm **Doanh thu theo ngày** để xem báo cáo.

Kết quả báo cáo: so với trước khi giao đơn này, **tăng 1 đơn và tăng 450.000**
tại ngày tạo của đơn. Nếu không có ai tạo/giao đơn khác và số đầu kỳ đúng là 2 đơn / 600.000,
kết quả mới sẽ là **3 đơn / 1.050.000**.

**Không dùng một đơn đã giao để thử lại luồng hủy.** Đó là chuyển trạng thái bị cấm;
muốn thử hủy hãy tạo đơn mới ở bước tiếp theo.

## 8. Test hủy đơn

1. Tạo đơn khác: khách hàng `TEST - Hủy đơn`, mặt hàng `Chuột`, số lượng `1`, đơn giá `200000`.
2. Bấm Save; đơn phải ở trạng thái **Mới**, thành tiền **200.000**.
3. Bấm **Hủy**, xác nhận **Yes**.
4. Chờ lưu xong: trạng thái Hủy, các trường chỉ đọc và không còn nút Save/chuyển trạng thái.
5. Tải lại đơn: trạng thái vẫn Hủy.
6. Mở báo cáo: số đơn và doanh thu **không tăng** do đơn hủy này.

Đơn đã hủy cũng không được đổi lại thành Mới hoặc Đã giao.
App không cung cấp chức năng xóa để làm lại bài test; hãy tạo một đơn khác.

## 9. Test hai tab cùng sửa một đơn

1. Tạo một đơn Mới riêng, lưu lại và mở đúng URL đơn đó ở hai tab A/B.
2. Tab A: bấm Đã giao và xác nhận thành công.
3. Tab B: vẫn giữ dữ liệu cũ, sửa số lượng rồi bấm Save.
4. Mong đợi: bị từ chối vì dữ liệu đã được cập nhật; thông báo có thể là
   `Document has been modified after you have opened it`.
5. Tải lại tab B: trạng thái Đã giao, dữ liệu đúng theo bản đã lưu và form bị khóa.

Không được xảy ra tình huống tab B đưa đơn về Mới hoặc ghi đè dữ liệu đã giao.
Đơn được giao thêm trong mục này cũng sẽ làm tăng báo cáo; nhớ tính phần tăng thêm đó khi đối chiếu.

## 10. Hiểu báo cáo theo ngày tạo đơn

- Chỉ cộng **Đã giao**; không cộng Mới hoặc Hủy.
- `Số đơn đã giao` là số đơn, không phải tổng số lượng mặt hàng.
- Mỗi ngày một dòng; ngày không có đơn đã giao sẽ không hiện dòng.
- Lấy ngày của `creation` theo múi giờ site `Asia/Ho_Chi_Minh`, không lấy ngày sửa hay ngày giao.
- Ví dụ đơn tạo **16/11**, giao **17/11** thì được tính vào dòng **16/11**.

Không có ô nhập ngày tạo trên form. Trường hợp tạo/giao khác ngày và ranh giới 23:59:59/00:00:00
đã được kiểm tra trong test server bằng dữ liệu fixture riêng.

## 11. Test quyền của người chưa đăng nhập

1. Mở cửa sổ ẩn danh hoặc trình duyệt chưa đăng nhập app.
2. Truy cập URL danh sách đơn hoặc báo cáo.
3. Mong đợi: yêu cầu đăng nhập / từ chối truy cập, không hiển thị dữ liệu đơn hàng hoặc doanh thu.
4. Không nhập `Guest` như một tài khoản để đăng nhập.

Hiện không có luồng nhân viên gửi duyệt rồi quản lý phê duyệt; đây là một app đơn hàng nhỏ theo đề.

## 12. Chạy test tự động nếu muốn kiểm tra server/API

Các lệnh sau chạy trong PowerShell tại thư mục dự án, sau khi `.\start.ps1` đã chạy:

```powershell
wsl -d Ubuntu --cd /home/vietanh/frappe-bench -- /home/vietanh/.local/share/orders-tools/bin/bench --site orders.localhost run-tests --app order_management
wsl -d Ubuntu --cd /home/vietanh/frappe-bench -- node apps/order_management/tests/simple-order-form.test.cjs
```

Đã có **14 test server** cho dữ liệu, tính tiền, chuyển trạng thái, khóa sửa/xóa,
tab cũ, báo cáo theo ngày tạo và quyền xem báo cáo.
Test Node kiểm tra tính nháp, khóa form và xử lý khi lưu thất bại.

Test trình duyệt đầy đủ, bao gồm gọi API cố sửa đơn đã giao:

```powershell
npm install --prefix .cache/ui --no-save --no-package-lock playwright@1.65.1
node .cache/ui/node_modules/playwright/cli.js install chromium --only-shell
$env:NODE_PATH = Join-Path $PWD '.cache/ui/node_modules'
node tests/e2e.cjs
```

Đây là test dành cho môi trường phát triển; mỗi lần chạy browser test sẽ tạo thêm **2 đơn demo**,
một Đã giao và một Hủy, nên doanh thu sẽ tăng tương ứng. Test cũng chụp lại ảnh trong `docs/screenshots/`.

## 13. Checklist demo nhanh khi phỏng vấn

- [ ] Đăng nhập Administrator.
- [ ] Tạo đơn Mới; đổi số lượng và chỉ ra thành tiền nháp.
- [ ] Save; giải thích server kiểm tra và tính tiền lại.
- [ ] Thử dữ liệu 0 hoặc âm; chỉ ra lỗi và sửa lại hợp lệ.
- [ ] Giao một đơn; tải lại để chứng minh khóa sửa.
- [ ] Hủy một đơn khác; chứng minh không cộng doanh thu.
- [ ] Mở báo cáo; đối chiếu số đơn và số tiền tăng thêm.
- [ ] Giải thích báo cáo dùng ngày tạo đơn.
- [ ] Mở `simple_order.py`, `simple_order.js` và `daily_revenue.py` để chỉ ra nơi xử lý.

Ảnh đã chuẩn bị: [Tạo đơn](docs/screenshots/01-create-order.png),
[Đã giao](docs/screenshots/02-delivered-order.png), [Hủy](docs/screenshots/03-cancelled-order.png),
[Báo cáo](docs/screenshots/04-daily-revenue.png).

## 14. Nếu gặp vấn đề

| Hiện tượng | Kiểm tra |
| --- | --- |
| Không mở được localhost:8000 | Chạy `.\start.ps1`; xem `.cache/bench.log` và `.cache/bench.error.log` nếu có lỗi |
| Sai mật khẩu | Đọc file `.cache/local-login.txt` trên máy này; không dùng mật khẩu Windows/WSL |
| Không thấy nút Đã giao/Hủy | Đơn đã Save lần đầu chưa? Đơn đã kết thúc thì hai nút được ẩn đúng chủ đích |
| Không sửa được đơn Đã giao/Hủy | Đúng quy tắc nghiệp vụ; tạo đơn mới để test tiếp |
| Doanh thu không tăng | Kiểm tra đã giao chưa và xem đúng dòng ngày tạo; Mới/Hủy không được cộng |
| Doanh thu lớn hơn ví dụ | Đã có thêm đơn được giao từ thao tác tay hoặc browser test; đối chiếu phần tăng thêm |
| Form chưa hiện thay đổi code mới | Nhấn Ctrl + Shift + R |

Tham khảo thêm: [README](README.md) và [hướng dẫn code FE](docs/frappe-frontend.md).
