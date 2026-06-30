# Book Warehouse - Hệ thống quản lý thư viện

Book Warehouse là website quản lý thư viện được xây dựng bằng Django. Dự án hỗ trợ quản lý tài khoản theo vai trò, quản lý kho sách, tra cứu sách, tạo phiếu mượn/trả, theo dõi sách quá hạn và ghi nhận tiền phạt.

## Mục tiêu dự án

- Xây dựng hệ thống thư viện chạy được trên môi trường web.
- Phân quyền rõ ràng cho Quản trị viên, Thủ thư và Sinh viên.
- Quản lý vòng đời sách từ nhập danh mục, tìm kiếm, mượn, trả đến ngưng sử dụng.
- Hỗ trợ dữ liệu mẫu để demo, kiểm thử và trình bày báo cáo.
- Có giao diện thống nhất, dễ thao tác và phù hợp với bài dự án nhóm.

## Công nghệ sử dụng

| Thành phần | Công nghệ |
| --- | --- |
| Backend | Python, Django |
| Database | SQLite |
| Frontend | Django Template, HTML, CSS, Bootstrap |
| Quản lý môi trường | Virtual environment, python-dotenv |
| Kiểm thử | Django TestCase |
| Dữ liệu mẫu | Django management command, Excel |

## Chức năng chính

### 1. Tài khoản và phân quyền

- Đăng ký, đăng nhập, đăng xuất.
- Quên mật khẩu và đặt lại mật khẩu qua console email backend.
- Cài đặt tài khoản và đổi mật khẩu.
- Quản trị viên có quyền quản lý tài khoản, chỉnh vai trò và đặt lại mật khẩu người dùng.
- Phân quyền theo 3 vai trò:
  - `ADMIN`: quản trị toàn hệ thống.
  - `LIBRARIAN`: quản lý sách và phiếu mượn/trả.
  - `STUDENT`: tra cứu sách và xem phiếu mượn của chính mình.

### 2. Danh mục sách

- Xem danh sách sách trong kho.
- Thêm, sửa, tìm kiếm sách theo mã sách, tên sách và tác giả.
- Theo dõi tổng số bản và số bản còn khả dụng.
- Ngưng sử dụng sách bằng `is_active` thay vì xóa cứng khi sách đã có lịch sử mượn.

### 3. Mượn trả sách

- Tạo phiếu mượn cho sinh viên.
- Tự động giảm số lượng sách còn khả dụng khi tạo phiếu.
- Xác nhận trả sách và tự động hoàn lại số lượng sách vào kho.
- Tự động nhận diện phiếu quá hạn.
- Tính tiền phạt theo số ngày trả muộn.
- Chỉ Admin và Thủ thư được ghi nhận thu phạt.

### 4. Dashboard và OPAC

- Trang tổng quan hiển thị số liệu nhanh của hệ thống.
- OPAC cho phép tra cứu sách đang hoạt động và còn trong kho.
- Trang thống kê hỗ trợ theo dõi tình hình vận hành.

## Cài đặt và chạy dự án

### 1. Tải mã nguồn

```powershell
git clone https://github.com/Chicken20145/Manage-book-warehouse.git
cd Manage-book-warehouse
```

### 2. Tạo và kích hoạt môi trường ảo

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Cài thư viện

```powershell
pip install -r requirements.txt
```

### 4. Tạo file môi trường

Tạo file `.env` ở thư mục gốc:

```env
SECRET_KEY=django-insecure-local-demo-key
DEBUG=True
```

### 5. Khởi tạo database

```powershell
venv\Scripts\python.exe manage.py migrate
```

### 6. Nạp dữ liệu mẫu

```powershell
venv\Scripts\python.exe manage.py load_sample_data
```

### 7. Chạy server

```powershell
venv\Scripts\python.exe manage.py runserver
```

Mở trình duyệt tại:

```text
http://127.0.0.1:8000/
```

## Tài khoản demo

Sau khi chạy `load_sample_data`, có thể dùng các tài khoản sau để demo:

| Vai trò | Tài khoản | Mật khẩu | Mục đích |
| --- | --- | --- | --- |
| Quản trị viên | `admin_demo` | `admin123` | Quản lý tài khoản, sách, phiếu mượn/trả và thu phạt |
| Thủ thư | `librarian` | `lib123` | Quản lý sách và nghiệp vụ mượn/trả |
| Sinh viên | `student01` | `stu123` | Tra cứu sách và xem phiếu mượn cá nhân |

## Cấu trúc thư mục và file

| Đường dẫn | Mô tả |
| --- | --- |
| `manage.py` | File lệnh chính của Django, dùng để chạy migrate, test, server và command dữ liệu mẫu. |
| `requirements.txt` | Danh sách thư viện Python cần cài đặt cho dự án. |
| `.env` | File cấu hình môi trường local như `SECRET_KEY`, `DEBUG`; không đưa lên Git. |
| `.gitignore` | Quy định các file/thư mục local không cần đưa lên repository. |
| `db.sqlite3` | Database SQLite dùng khi chạy local. |
| `core/` | Cấu hình lõi của Django project. |
| `core/settings.py` | Cấu hình app, database, template, timezone, đăng nhập và email backend. |
| `core/urls.py` | Khai báo URL tổng, kết nối các app `accounts`, `dashboard`, `catalog`, `circulation`. |
| `core/asgi.py`, `core/wsgi.py` | Điểm khởi chạy ứng dụng khi deploy theo ASGI/WSGI. |
| `accounts/` | App quản lý người dùng, xác thực và phân quyền. |
| `accounts/models.py` | Định nghĩa `CustomUser` với vai trò `ADMIN`, `LIBRARIAN`, `STUDENT`. |
| `accounts/forms.py` | Form đăng ký, chỉnh tài khoản, đổi mật khẩu và đặt lại mật khẩu. |
| `accounts/views.py` | Xử lý đăng ký, cài đặt tài khoản, admin panel, chỉnh người dùng. |
| `accounts/decorators.py` | Decorator kiểm tra quyền truy cập theo vai trò. |
| `accounts/templates/accounts/` | Giao diện đăng nhập, đăng ký, quên mật khẩu, cài đặt và quản trị tài khoản. |
| `catalog/` | App quản lý danh mục sách. |
| `catalog/models.py` | Model `Book`, lưu mã sách, tên sách, tác giả, ISBN, số lượng và trạng thái hoạt động. |
| `catalog/forms.py` | Form thêm/sửa sách và validate số lượng sách. |
| `catalog/views.py` | Xử lý danh sách sách, tìm kiếm, thêm, sửa và ngưng sử dụng/xóa sách. |
| `catalog/templates/catalog/` | Giao diện danh mục sách, form sách và xác nhận xóa/ngưng sử dụng. |
| `circulation/` | App xử lý nghiệp vụ mượn trả. |
| `circulation/models.py` | Model `Borrowing` và `BorrowedItem`, lưu phiếu mượn, sách mượn, hạn trả và tiền phạt. |
| `circulation/forms.py` | Form tạo phiếu mượn và xác nhận ngày trả. |
| `circulation/views.py` | Xử lý tạo phiếu, xác nhận mượn, xác nhận trả và ghi nhận thu phạt. |
| `circulation/templates/circulation/` | Giao diện quản lý phiếu mượn/trả và trạng thái tiền phạt. |
| `circulation/management/commands/load_sample_data.py` | Command tạo tài khoản demo, sách mẫu và phiếu mượn mẫu. |
| `dashboard/` | App hiển thị tổng quan, OPAC và thống kê. |
| `dashboard/views.py` | Tính số liệu tổng quan, lọc dữ liệu OPAC và thống kê hệ thống. |
| `dashboard/templates/dashboard/` | Giao diện dashboard, tra cứu sách OPAC và thống kê. |
| `templates/base.html` | Layout gốc dùng chung cho toàn bộ giao diện. |
| `data/book_warehouse_sample_data.xlsx` | File Excel dữ liệu mẫu phục vụ báo cáo hoặc nhập liệu tham khảo. |
| `*/migrations/` | Lịch sử thay đổi database schema của từng app. |
| `*/tests.py` | Test tự động cho các chức năng chính của từng app. |
| `output/` | Thư mục xuất tài liệu/báo cáo local, không cần đưa lên Git. |
| `venv/` | Môi trường ảo Python local, không đưa lên Git. |

## Kiểm thử

Chạy kiểm tra cấu hình:

```powershell
venv\Scripts\python.exe manage.py check
```

Chạy toàn bộ test:

```powershell
venv\Scripts\python.exe manage.py test
```

Các nhóm test hiện tập trung vào:

- Flow tài khoản, đăng nhập, đăng ký, đổi mật khẩu và phân quyền.
- CRUD danh mục sách và tìm kiếm sách.
- Nghiệp vụ mượn/trả, quá hạn, trả sách và thu phạt.
- Dashboard, OPAC và thống kê.

## Gợi ý demo

1. Đăng nhập bằng `admin_demo`.
2. Kiểm tra dashboard tổng quan.
3. Vào Quản trị để xem/chỉnh tài khoản và phân quyền.
4. Vào Danh mục sách để thêm, sửa, tìm kiếm hoặc ngưng sử dụng sách.
5. Vào Mượn trả để tạo phiếu mượn, xác nhận trả và ghi nhận thu phạt.
6. Đăng xuất và đăng nhập bằng `student01` để kiểm tra giao diện sinh viên chỉ xem được dữ liệu phù hợp.
7. Mở OPAC để tra cứu sách như người dùng cuối.

## Lưu ý khi làm nhóm

- Trước khi code nên chạy `git pull origin main`.
- Không commit `venv/`, `.env`, file cache, file báo cáo xuất tạm hoặc dữ liệu local không cần thiết.
- Nếu thay đổi model cần chạy `makemigrations`, sau đó cả nhóm chạy `migrate`.
- Trước khi push nên chạy `manage.py check` và `manage.py test`.
- Khi có xung đột migration hoặc database local, báo nhóm trước khi sửa để tránh làm lệch schema.
