# GitHub Actions — Docker

Workflow: [`.github/workflows/ci.yml`](../.github/workflows/ci.yml).
Chạy khi push/PR vào `main` hoặc chọn **Actions → Frappe Docker CI → Run workflow**.

1. Build image `order-management:local` từ Dockerfile, gồm Frappe v15.126.1, app và assets.
2. Chạy Compose với MariaDB/Redis và site mới, chờ web healthy.
3. Chạy test nghiệp vụ, báo cáo, form JavaScript và khởi tạo Docker trong container.
4. Khi chạy trên `main` ngoài pull request, đẩy image đã test lên GHCR:
   `ghcr.io/kieuvietanh/gege_iterptest_frappe:latest` và tag theo commit SHA.
5. In log và xóa containers/volumes tạm của CI.

Không cần cài Python/Node/Bench trên runner. Không còn đóng gói wheel/ZIP trong workflow.
Image chứa code và assets; database, mật khẩu site và đơn hàng nằm trong volumes khi chạy.

Workflow dùng `GITHUB_TOKEN` tự cấp với quyền `packages: write`, không cần tự thêm token
([tài liệu GHCR](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)).
Lần đầu, package GHCR có thể ở chế độ private; xem trong **GitHub profile → Packages**.
Kết quả build/test xem ở **Actions → Frappe Docker CI → build-and-test**.
Nếu push image bị từ chối, kiểm tra quyền Packages/Actions của repository hoặc tổ chức.

Workflow chỉ build/test/publish image, chưa chạy website trên máy chủ. Không cần EC2 hay AWS Secrets.
Browser test hiện chạy local theo [hướng dẫn test](../HUONG-DAN-TEST.md).
