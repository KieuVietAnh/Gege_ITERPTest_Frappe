# Luồng đơn hàng và nhập/xuất kho

## Đối chiếu đề

Đề yêu cầu mỗi đơn một mặt hàng, số lượng/đơn giá > 0, server tính thành tiền;
Mới → Đã giao hoặc Hủy; đơn đóng không sửa hoặc đổi trạng thái, kể cả Administrator.
Doanh thu chỉ tính Đã giao và nhóm theo ngày tạo đơn. App giữ nguyên các quy tắc này.
Role và quản lý kho là phần mở rộng. Không thêm trạng thái Đang giao.

## Quyền và chuyển trạng thái

| Thao tác | Sale | Kho | Administrator |
|---|---|---|---|
| Tạo đơn | Được | Không | Được |
| Xem đơn | Đơn mình tạo | Đơn được phân công | Tất cả |
| Sửa/phân công/hủy đơn Mới | Đơn mình tạo | Không | Được |
| Mới → Đã giao | Không | Đơn được phân công | Được |
| Sửa/đổi trạng thái đơn Đã giao hoặc Hủy | Không | Không | Không |
| Nhập hàng | Không | Được | Được |
| Xem sổ kho chung | Không | Được | Được |

Mới chưa giữ hay trừ tồn. Hủy không phát sinh xuất hoặc hoàn kho.
Đã giao đồng nghĩa hoàn tất giao hàng và xuất kho trong phạm vi bài test;
chưa tách thời điểm gửi hàng với thời điểm khách nhận, chưa giao từng phần hoặc hoàn hàng.

## Nhập và xuất

1. Kho tạo **Stock Receipt** tại `/app/stock-receipt`, chọn mặt hàng, số lượng, ghi chú rồi lưu.
2. Server cộng tồn và tự ghi **Stock Movement** loại Nhập, mã `IN-LOG-…`.
3. Sale tạo đơn Mới và phân công Kho. Kho xác nhận **Đã giao** trên đơn.
4. Server kiểm tra tồn, tự ghi Stock Movement loại Xuất, mã `OUT-…`, và trừ tồn.
5. Tại `/app/stock-movement`, lọc Loại = Xuất để xem phiếu xuất, hoặc Nhập để xem lịch sử nhập.
   Mở bản ghi để xem/in, bấm chứng từ nguồn để mở đơn hoặc phiếu nhập (vẫn kiểm tra quyền chứng từ).

Stock Movement là sổ kho chung; bản ghi Xuất đồng thời là phiếu xuất, không có bước xuất tay riêng.
Lưu mặt hàng, số lượng, tồn trước/sau, chứng từ, người thực hiện và thời gian tạo.
Kho xem lịch sử tồn chung nhưng chỉ được mở nội dung đơn được giao. Sale không đọc sổ kho chung.
Phiếu nhập và lịch sử không sửa/xóa qua ứng dụng, kể cả Admin; không cho API tạo lịch sử tùy ý.

## Giao dịch và yêu cầu đồng thời

Khóa dòng đơn khi lưu; khóa dòng mặt hàng `FOR UPDATE` trước khi đọc tồn.
Đổi trạng thái, ghi lịch sử/phiếu xuất và cập nhật tồn cùng transaction, lỗi thì rollback.
Khóa chứng từ nguồn có unique index: một đơn chỉ có một phiếu xuất.
Hai đơn tranh lượng tồn cuối chỉ đơn đủ tồn được giao; xác nhận một đơn hai lần chỉ trừ một lần.
Nhập và xuất đồng thời dùng chung khóa mặt hàng nên tồn trước/sau được tính tuần tự.

## Seed trên site mới

Mật khẩu Sale: `SaleDemo@12345!`; Kho: `KhoDemo@12345!`.

| Tài khoản | Tên hiển thị | Đơn |
|---|---|---|
| sale1@example.com | Nguyễn Minh Anh | 001, 003, 004 |
| sale2@example.com | Trần Quốc Huy | 002, 005, 006 |
| kho1@example.com | Lê Hoàng Nam | Xử lý đơn Sale 1 |
| kho2@example.com | Phạm Thu Hà | Xử lý đơn Sale 2 |

| Mã đơn | Khách hàng | Hàng × số lượng | Trạng thái |
|---|---|---|---|
| DEMO-ORD-001 | Văn phòng An Phát | KB001 × 2 | Mới |
| DEMO-ORD-002 | Trung tâm Sao Mai | HS001 × 2 | Mới |
| DEMO-ORD-003 | Cửa hàng Minh Anh | MS001 × 3 | Đã giao |
| DEMO-ORD-004 | Công ty Hòa Bình | HS001 × 1 | Hủy |
| DEMO-ORD-005 | Văn phòng Thành Công | KB001 × 1 | Đã giao |
| DEMO-ORD-006 | Cửa hàng Gia Hưng | MS001 × 2 | Hủy |

Nhập đầu 20 mỗi mã. Sau seed site mới: KB001 còn 19, MS001 còn 17, HS001 còn 20;
có 3 phiếu nhập, 3 lịch sử Nhập, 2 phiếu Xuất; doanh thu 750.000, 2 đơn Đã giao.
Ngày tạo đơn là ngày chạy seed. Seed chuyển trạng thái qua controller với đúng người Sale/Kho,
không chèn trực tiếp trạng thái hay tồn kho bằng SQL.

## Khi nâng cấp site cũ

Seed bỏ qua ID đã tồn tại: không đặt lại mật khẩu, tên, nội dung/trạng thái đơn hoặc cộng lại tồn.
Vì vậy site cũ có thể còn tên Sale 1/Kho 1, đơn cũ hoặc dữ liệu test; không tự xóa để ép còn sáu đơn.
Các giao dịch trước cập nhật không có lịch sử kho mới. Không dựng giả tồn trước/sau hoặc xuất lại
đơn đã giao. Tồn trước ở bản ghi mới đầu tiên là số dư thực tế lúc thao tác, không nhất thiết bằng 0.
