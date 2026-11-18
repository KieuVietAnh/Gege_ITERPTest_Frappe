# Hướng dẫn test Sale – Kho

Chạy tại thư mục repo: `docker compose up -d --build --wait`.
Bản Docker local dùng http://localhost:8080.
Nếu cài bằng Bench theo README, thay cổng `8080` trong các URL dưới đây bằng `8000`.

## Tài khoản demo

| Tài khoản | Mật khẩu | Vai trò |
| --- | --- | --- |
| `Administrator` | `admin` | Xem mọi đơn, quản lý kho và xem báo cáo |
| `sale1@example.com` | `SaleDemo@12345!` | Nguyễn Minh Anh — Sale, đơn 001/003/004 |
| `sale2@example.com` | `SaleDemo@12345!` | Trần Quốc Huy — Sale, đơn 002/005/006 |
| `kho1@example.com` | `KhoDemo@12345!` | Lê Hoàng Nam — Kho được giao đơn 001/003/004; quản lý nhập kho |
| `kho2@example.com` | `KhoDemo@12345!` | Phạm Thu Hà — Kho được giao đơn 002/005/006; quản lý nhập kho |
| `Guest` | Không có | Chưa đăng nhập, không truy cập dữ liệu |

Seed tự tạo các tài khoản này khi install/migrate ở cả Bench và Docker. Khi chạy lại, không reset mật khẩu đã đổi,
không bổ sung lại tồn đã dùng. Đổi mật khẩu demo trước khi mở web công khai.
Mật khẩu `admin` chỉ là mặc định của Docker; với Bench dùng mật khẩu Administrator đã đặt khi tạo site.
Admin tạo thêm System User và cấp `Order Sales` hoặc `Order Warehouse` tại màn hình User.
Role `System Manager` riêng lẻ không có quyền xem toàn bộ đơn/doanh thu của app.

Dùng cửa sổ/profile trình duyệt riêng cho mỗi tài khoản để tránh đăng nhập đè phiên.
Đăng xuất: bấm avatar góc trên bên phải → **Log out**. Các tab cùng profile dùng chung phiên đăng nhập.

## Các màn hình

| Chức năng | URL |
| --- | --- |
| Trang chính app | http://localhost:8080/app/order-management |
| Đơn hàng | http://localhost:8080/app/simple-order |
| Mặt hàng và tồn kho | http://localhost:8080/app/stock-item |
| Phiếu nhập | http://localhost:8080/app/stock-receipt |
| Lịch sử nhập / phiếu xuất (Kho/Admin) | http://localhost:8080/app/stock-movement |
| Doanh thu (Admin) | http://localhost:8080/app/query-report/Daily%20Revenue |

## Dữ liệu có sẵn trên site mới

| Mã hàng | Tên | Đơn giá | Nhập đầu | Tồn sau seed |
| --- | --- | ---: | ---: | ---: |
| KB001 | Bàn phím văn phòng | 150.000 | 20 | 19 |
| MS001 | Chuột không dây | 200.000 | 20 | 17 |
| HS001 | Tai nghe USB | 350.000 | 20 | 20 |

| Mã đơn | Khách hàng | Hàng × SL | Thành tiền | Trạng thái | Sale / Kho |
| --- | --- | --- | ---: | --- | --- |
| DEMO-ORD-001 | Văn phòng An Phát | KB001 × 2 | 300.000 | Mới | Sale 1 / Kho 1 |
| DEMO-ORD-002 | Trung tâm Sao Mai | HS001 × 2 | 700.000 | Mới | Sale 2 / Kho 2 |
| DEMO-ORD-003 | Cửa hàng Minh Anh | MS001 × 3 | 600.000 | Đã giao | Sale 1 / Kho 1 |
| DEMO-ORD-004 | Công ty Hòa Bình | HS001 × 1 | 350.000 | Hủy | Sale 1 / Kho 1 |
| DEMO-ORD-005 | Văn phòng Thành Công | KB001 × 1 | 150.000 | Đã giao | Sale 2 / Kho 2 |
| DEMO-ORD-006 | Cửa hàng Gia Hưng | MS001 × 2 | 400.000 | Hủy | Sale 2 / Kho 2 |

Có 3 phiếu nhập và 2 phiếu xuất gắn với đơn 003/005; sổ kho gồm 5 bản ghi.
Báo cáo ban đầu: **2 đơn Đã giao, doanh thu 750.000**, theo ngày tạo đơn lúc chạy seed.
Mã phiếu tự sinh; tìm theo mặt hàng hoặc chứng từ nguồn, không phụ thuộc số thứ tự phiếu.

Đây là dữ liệu của **site mới, chưa thao tác**. Site đã dùng có thể khác vì seed không thay tên,
đơn, mật khẩu đã tồn tại và không cộng lại tồn hay xóa dữ liệu test cũ.
Dataset: [order_management/seed.sql](order_management/seed.sql), được tạo qua ORM Frappe.
Chi tiết quy tắc: [Luồng đơn và kho](docs/stock-flow.md).

## Test nhanh bằng đơn có sẵn

Thực hiện lần lượt trên site mới; các bước này thay đổi dữ liệu thật.

| Bước | Tài khoản / thao tác | Kết quả mong đợi |
| --- | --- | --- |
| 1 | Admin xem Daily Revenue | 2 đơn, 750.000 |
| 2 | Sale 1 xem danh sách đơn | Chỉ có 001/003/004; không mở được đơn 002 của Sale 2 |
| 3 | Kho 1 mở 001, bấm Đã giao và xác nhận | Đơn khóa, KB001 từ 19 còn 17; có đúng một phiếu OUT cho 001 |
| 4 | Kho 1 xem/in phiếu xuất của 001 | SL 2, tồn 19 → 17, người thực hiện kho1@example.com |
| 5 | Sale 2 mở 002, bấm Hủy và xác nhận | Đơn khóa, HS001 vẫn 20, không có phiếu xuất cho 002 |
| 6 | Admin xem lại doanh thu | 3 đơn Đã giao, tổng 1.050.000 nếu chưa có thao tác khác |
| 7 | Admin mở 003 (Đã giao) hoặc 004 (Hủy) | Không sửa hoặc chuyển trạng thái được |
| 8 | Sale mở URL báo cáo hoặc lịch sử kho | Bị từ chối; Kho xem sổ kho nhưng không xem báo cáo doanh thu |

Nếu đã xử lý 001/002, tạo đơn mới theo luồng dưới đây để test lại; không mở lại đơn đóng.

## Luồng demo từ đầu

1. Đăng nhập Kho 1, mở **Mặt hàng và tồn kho**, tạo mã riêng, ví dụ `DEMO-001`.
   Nhập tên, đơn vị Cái, giá bán mặc định 150000. Save: tồn ban đầu bằng 0.
2. Trên mặt hàng, bấm **Nhập kho**, nhập số lượng 10 và Save.
   Phiếu đã lưu chỉ đọc, mặt hàng có tồn 10. Lịch sử kho có bản ghi Nhập: 0 → 10, số lượng 10.
3. Đăng nhập Sale 1, tạo Simple Order: khách hàng `Khách thử`, chọn `DEMO-001`,
   số lượng 2. Giá tự điền 150000, thành tiền nháp 300000. Chọn người xử lý kho `kho1@example.com`, Save.
4. Đơn ở **Mới**. Sale 1 được sửa thông tin hoặc Hủy, không có nút Đã giao và không xem doanh thu.
5. Đăng nhập Sale 2: không thấy đơn của Sale 1. Kho 2 cũng không thấy đơn giao cho Kho 1.
   Mở URL trực tiếp của đơn bằng hai tài khoản này cũng bị từ chối.
6. Đăng nhập Kho 1, mở đơn được phân công. Giá/số lượng/khách hàng chỉ đọc.
   Bấm **Đã giao**, xác nhận Yes. Đơn khóa sửa, tồn còn 8.
   Mở Lịch sử kho, lọc mặt hàng: có phiếu `OUT-…` liên kết đơn, số lượng 2, tồn 10 → 8,
   người thực hiện Kho 1. Kho/Admin xem và in được; không tạo tay/sửa/xóa phiếu xuất.
7. Admin mở báo cáo: tăng 1 đơn và 300000 ở **ngày tạo đơn**.
   Cả Sale và Kho mở URL báo cáo hoặc gọi API báo cáo đều bị từ chối.

## Hủy và phân công lại

- Sale tạo một đơn Mới khác rồi Hủy. Tồn và doanh thu không đổi.
- Khi còn Mới, Sale có thể đổi người xử lý kho từ Kho 1 sang Kho 2.
  Kho 1 mất quyền; Kho 2 nhận quyền. Tab cũ không được ghi đè hoặc tự nhận lại đơn.
- Đơn Đã giao/Hủy khóa với mọi người, kể cả Admin. Không mở lại, không xóa đơn kết thúc.
- Không có bước duyệt hoặc trạng thái Đang giao: giữ ba trạng thái theo đề bài.

## Kiểm tra kho và dữ liệu sai

| Thử | Kết quả |
| --- | --- |
| Nhập kho số lượng 0, âm hoặc không hữu hạn | Từ chối, tồn không đổi |
| Tạo đơn với số lượng hoặc đơn giá ≤ 0 | Server từ chối lưu |
| Sửa/xóa/tự tạo phiếu xuất hoặc bản ghi lịch sử | Từ chối; chỉ tự sinh từ nhập/giao đơn |
| Sửa trực tiếp tồn qua form/API | Từ chối; phải nhập bằng phiếu hoặc xuất bằng đơn |
| Sửa/xóa phiếu nhập đã lưu | Từ chối |
| Sale tạo mặt hàng hoặc phiếu nhập | Từ chối; Sale chỉ đọc danh mục và tồn |
| Phân công cho tài khoản Sale, tài khoản bị khóa hoặc không có role Kho | Từ chối |
| Sale tự đổi trạng thái Đã giao qua API | Từ chối |
| Kho sửa giá/số lượng hoặc tự đổi người xử lý qua API | Từ chối |
| Xuất số lượng lớn hơn tồn | Từ chối; đơn vẫn Mới, tồn không đổi |
| Xác nhận lại đơn đã giao | Từ chối; không trừ tồn lần hai |
| Hai đơn cùng xuất lượng hàng cuối | Chỉ một thành công; đơn còn lại vẫn Mới, không âm kho |

Số lượng có 3 chữ số thập phân, tiền có 2 chữ số. Giá trên đơn có thể điều chỉnh bởi Sale
khi đơn còn Mới; thành tiền cuối cùng luôn tính ở server.

## Race condition và transaction

Frappe khóa dòng đơn trước khi kiểm tra bản lưu mới nhất. Quyền xử lý được kiểm tra từ dữ liệu
đã lưu, không dựa vào người tạo/người xử lý giả mạo trong request.

Nhập/xuất khóa dòng mặt hàng bằng `SELECT ... FOR UPDATE`. Kiểm tra tồn, trừ/cộng tồn và lưu
chứng từ cùng transaction; không commit giữa chừng. Nếu thiếu hàng hoặc lưu lỗi, request rollback.
Các test dùng hai kết nối DB độc lập và hai request HTTP đồng thời để kiểm tra hành vi thực tế.

Đơn Mới không giữ chỗ tồn. Phiên bản đầu chỉ có một kho chung; chưa có hoàn hàng,
điều chỉnh tồn, nhiều kho, lô hoặc hạn sử dụng.

## Test tự động

Test server, JavaScript và khởi tạo Docker:

```bash
docker compose exec -T backend bash apps/order_management/docker/test.sh
```

Browser test từ PowerShell, dùng Chrome headless riêng:

```powershell
npm install --prefix .cache/ui --no-save --no-package-lock playwright@1.65.1
node .cache/ui/node_modules/playwright/cli.js install chromium --only-shell
$env:NODE_PATH = Join-Path $PWD '.cache/ui/node_modules'
node tests/e2e.cjs
node tests/rbac-stock-e2e.cjs
```

Browser test tạo thêm dữ liệu demo thật và chụp ảnh trong `docs/screenshots/`.
Test server bao gồm phân quyền, dữ liệu sai, tính tiền, báo cáo, rollback và xử lý đồng thời.
Script dùng `CI=1` để Bench trả exit code lỗi khi có test fail.

## Đọc code

- `permissions.py`: giới hạn danh sách và từng đơn, tìm người xử lý kho.
- `doctype/simple_order/`: đơn hàng, chuyển trạng thái, kiểm tra người thao tác.
- `doctype/stock_item/`: danh mục mặt hàng, bảo vệ tồn.
- `doctype/stock_receipt/`: nhập kho; phiếu đã lưu bất biến.
- `doctype/stock_movement/`: lịch sử nhập/xuất, phiếu xuất tự động và khóa chứng từ unique.
- `stock.py`: cập nhật tồn có khóa dòng, không tự commit.
- `test_stock_concurrency.py`: hai kết nối database chạy cùng lúc.
- [Luồng và ma trận quyền](docs/rbac-flow.md).

Nếu không mở được web, xem `docker compose ps -a` và `docker compose logs initialize backend frontend`.
Sửa code rồi chạy lại lệnh Compose có `--build`, sau đó Ctrl + Shift + R.
Bản WSL cũ ở cổng 8000 có database/mật khẩu riêng. Bản đó cần backup/migrate schema trước khi dùng
chức năng kho mới; hiện hãy kiểm tra bằng Docker ở cổng 8080.
