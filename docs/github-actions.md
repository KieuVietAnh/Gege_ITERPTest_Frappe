# GitHub Actions — kiểm thử khi push code

Workflow: [`.github/workflows/ci.yml`](../.github/workflows/ci.yml).
Đã kiểm tra cú pháp và biểu thức bằng actionlint. Lần chạy thực tế trên GitHub sẽ diễn ra sau khi bạn push repo.

## Phạm vi hiện tại

CI chạy trên máy Ubuntu tạm của GitHub khi:

- Push vào nhánh `main`.
- Mở/cập nhật pull request vào `main`.
- Chọn **Actions → Frappe CI → Run workflow**.

Các bước: checkout → Python 3.12 / Node.js 22 → Bench 5.31.1 / Frappe 15.126.1
→ MariaDB/Redis tạm → cài app vào site sạch → test server và JS → build giao diện → đóng gói artifact.

Không cần EC2, AWS credentials, SSH key hoặc GitHub Secrets để chạy CI này.
Workflow chưa deploy và không tạo tài nguyên AWS. Mật khẩu `ci-...` trong YAML chỉ dành cho
database/site tạm trên runner, không phải mật khẩu app đang chạy trên máy bạn và không dùng cho production.

## Đưa repo lên GitHub

1. Tạo repository trống trên GitHub, không thêm README sẵn để tránh xung đột với repo hiện tại.
2. Mở PowerShell tại thư mục dự án, thay URL bên dưới bằng URL repo của bạn:

```powershell
git status
git add .
git commit -m "feat: complete order management and add CI"
git remote add origin https://github.com/TEN_GITHUB/TEN_REPO.git
git push -u origin main
```

Nếu đã có remote `origin`, kiểm tra `git remote -v` và dùng remote phù hợp thay vì thêm lại.
Đăng nhập GitHub bằng cơ chế Git của bạn khi được yêu cầu; không đưa token vào URL hoặc commit.
`.cache`, `.env`, database, log và `dist` được Git bỏ qua.

## Xem kết quả

1. Mở repository → **Actions → Frappe CI**.
2. Chọn lần chạy mới nhất → job **test-and-package**.
3. Nếu đỏ, mở step bị lỗi để xem log. Lần đầu phải tải dependency và dựng Bench nên có thể mất vài phút.
4. Nếu xanh, cuộn đến **Artifacts**, tải gói `order-management-<commit SHA>`.
5. Bên trong có wheel của app và `order-management-source.zip` lấy từ commit đã kiểm thử.

Artifact được giữ 7 ngày. Muốn có bản mới thì push commit mới hoặc chạy workflow thủ công.
Đây là file để tải xuống, chưa phải một website có URL công khai.

## Chi phí và triển khai sau này

CI này dùng quota GitHub Actions của repository/tài khoản GitHub, không dùng credit AWS $120.
Khi bắt đầu deploy EC2, bổ sung workflow deploy cùng cấu hình máy chủ và secrets cần thiết sau;
hiện chưa có thao tác nào tiêu credit AWS trong workflow này.

## Kiểm tra trước khi push

- Code, test, `.github/workflows/ci.yml`, thư mục `scripts` và tài liệu cần được commit đầy đủ.
- Không commit `.cache/local-login.txt`, token, private key hoặc mật khẩu thật.
- Workflow chỉ chạy test server và JS; browser test `tests/e2e.cjs` hiện chạy cục bộ theo README.
- Thay metadata tác giả `ERP Test` / `dev@example.com` trước khi nộp nếu cần.
