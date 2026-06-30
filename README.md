# Book Warehouse - Hệ thống quản lý thư viện

Book Warehouse là website quản lý thư viện được xây dựng bằng Django. Dự án hỗ trợ quản lý tài khoản theo vai trò, quản lý kho sách, tra cứu sách, tạo phiếu mượn/trả, theo dõi sách quá hạn và ghi nhận tiền phạt.

README này được dùng như tài liệu đọc nhanh cho giảng viên hoặc thành viên mới của nhóm. Nội dung bên dưới giới thiệu dự án làm gì, có những chức năng nào, cách chạy hệ thống, tài khoản demo và ý nghĩa của các thư mục/file chính trong mã nguồn.

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

## Mô tả thư mục và file chính

Bảng này giải thích vai trò của từng phần trong mã nguồn để người đọc có thể hiểu nhanh dự án được chia module như thế nào và mỗi file đang phục vụ chức năng gì.

| Đường dẫn | File/thư mục này dùng để làm gì |
| --- | --- |
| `README.md` | Tài liệu giới thiệu tổng quan dự án cho giảng viên và thành viên nhóm: chức năng, cách chạy, tài khoản demo và cấu trúc mã nguồn. |
| `manage.py` | File lệnh trung tâm của Django. Dùng để chạy server, tạo/cập nhật database, chạy test và gọi các lệnh quản lý dữ liệu mẫu. |
| `requirements.txt` | Danh sách thư viện Python cần cài để dự án chạy đúng trên máy khác. |
| `.env` | File cấu hình riêng của từng máy, ví dụ `SECRET_KEY` và `DEBUG`. File này không nên đưa lên Git vì có thể chứa thông tin nhạy cảm. |
| `.gitignore` | Danh sách file/thư mục không cần hoặc không nên push lên GitHub, ví dụ môi trường ảo, cache, file cấu hình local và tài liệu xuất tạm. |
| `db.sqlite3` | Database SQLite dùng cho chạy thử local. File này lưu dữ liệu demo, tài khoản, sách và phiếu mượn trên máy đang chạy dự án. |
| `core/` | Phần cấu hình gốc của toàn bộ website Django. Có thể hiểu đây là nơi nối các module chức năng lại thành một hệ thống hoàn chỉnh. |
| `core/settings.py` | Khai báo cấu hình chính của dự án: app nào được bật, dùng database nào, template ở đâu, timezone, đăng nhập và email reset mật khẩu. |
| `core/urls.py` | Bản đồ đường dẫn cấp cao của website. File này điều hướng người dùng tới các module như tài khoản, dashboard, danh mục sách và mượn trả. |
| `core/asgi.py`, `core/wsgi.py` | File khởi chạy khi triển khai website lên server thật. Trong demo local thường không cần chỉnh trực tiếp. |
| `accounts/` | Module tài khoản và phân quyền. Phần này quyết định ai được đăng nhập, ai là Admin, Thủ thư hoặc Sinh viên, và mỗi vai trò được làm gì. |
| `accounts/models.py` | Định nghĩa bảng người dùng `CustomUser`, bổ sung vai trò và mã sinh viên để phục vụ phân quyền trong hệ thống thư viện. |
| `accounts/forms.py` | Chứa các form liên quan đến tài khoản như đăng ký, chỉnh thông tin cá nhân, đổi mật khẩu và reset mật khẩu. |
| `accounts/views.py` | Xử lý logic cho các màn hình tài khoản: đăng ký, cài đặt tài khoản, danh sách người dùng, sửa vai trò và đặt lại mật khẩu cho tài khoản khác. |
| `accounts/decorators.py` | Chứa hàm kiểm tra quyền theo vai trò. Ví dụ chỉ Admin mới vào được trang quản trị tài khoản. |
| `accounts/templates/accounts/` | Các trang giao diện của phần tài khoản: đăng nhập, đăng ký, quên mật khẩu, đổi mật khẩu, cài đặt tài khoản và quản trị người dùng. |
| `catalog/` | Module quản lý kho sách. Phần này chịu trách nhiệm lưu thông tin sách, tìm kiếm sách và kiểm soát sách còn được sử dụng hay không. |
| `catalog/models.py` | Định nghĩa bảng sách `Book`, gồm mã sách, tên sách, tác giả, ISBN, tổng số bản, số bản còn lại và trạng thái hoạt động. |
| `catalog/forms.py` | Form nhập liệu cho chức năng thêm/sửa sách, đồng thời kiểm tra dữ liệu số lượng để tránh nhập sai. |
| `catalog/views.py` | Xử lý các thao tác danh mục sách: xem danh sách, tìm kiếm, thêm sách, sửa sách và ngưng sử dụng/xóa sách theo điều kiện. |
| `catalog/templates/catalog/` | Các màn hình của module sách: danh sách sách, form thêm/sửa và trang xác nhận trước khi xóa hoặc ngưng sử dụng sách. |
| `circulation/` | Module nghiệp vụ mượn trả. Đây là phần mô phỏng quy trình thư viện thực tế: lập phiếu mượn, trả sách, quá hạn và thu phạt. |
| `circulation/models.py` | Định nghĩa bảng phiếu mượn `Borrowing` và chi tiết sách mượn `BorrowedItem`, bao gồm hạn trả, ngày trả, trạng thái và tiền phạt. |
| `circulation/forms.py` | Form tạo phiếu mượn và nhập ngày trả sách, giúp thủ thư thao tác nhanh trong giao diện mượn trả. |
| `circulation/views.py` | Xử lý các nghiệp vụ chính: tạo phiếu mượn, xác nhận mượn, xác nhận trả, tự cập nhật tồn kho và ghi nhận thu phạt. |
| `circulation/templates/circulation/` | Giao diện theo dõi phiếu mượn/trả, hiển thị trạng thái phiếu, tiền phạt và các nút thao tác theo đúng quyền người dùng. |
| `circulation/management/commands/load_sample_data.py` | Lệnh tạo dữ liệu demo gồm tài khoản mẫu, sách mẫu và phiếu mượn mẫu để nhóm có thể trình bày dự án ngay sau khi cài đặt. |
| `dashboard/` | Module trang chủ, tra cứu OPAC và thống kê. Đây là nơi người dùng nhìn tổng quan tình hình thư viện. |
| `dashboard/views.py` | Tính toán số liệu cho dashboard, xử lý tra cứu sách ở OPAC và chuẩn bị dữ liệu cho trang thống kê. |
| `dashboard/templates/dashboard/` | Giao diện trang tổng quan, trang tra cứu sách OPAC và trang thống kê vận hành. |
| `templates/base.html` | Layout chung của toàn website, gồm sidebar, thanh trên, vùng nội dung, style tổng quát và các thành phần dùng lại ở nhiều trang. |
| `data/book_warehouse_sample_data.xlsx` | File Excel dữ liệu mẫu dùng để tham khảo khi làm báo cáo hoặc khi cần minh họa nguồn dữ liệu sách. |
| `*/migrations/` | Các file ghi lại lịch sử thay đổi cấu trúc database của từng module. Khi chạy `migrate`, Django dùng các file này để tạo bảng. |
| `*/tests.py` | Test tự động kiểm tra những chức năng quan trọng, giúp nhóm biết hệ thống còn chạy đúng sau khi sửa code. |
| `output/` | Thư mục xuất báo cáo/tài liệu local trong quá trình làm bài. Đây không phải mã nguồn chính nên không cần đưa lên GitHub. |
| `venv/` | Môi trường ảo Python trên máy local. Thư mục này giúp cài thư viện riêng cho dự án nhưng không đưa lên GitHub. |

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

## Trạng thái hoàn thiện

Dự án đã hoàn thiện các chức năng chính phục vụ báo cáo và demo cuối kỳ: xác thực người dùng, phân quyền theo vai trò, quản lý danh mục sách, tra cứu OPAC, mượn/trả sách, theo dõi quá hạn, ghi nhận tiền phạt, thống kê tổng quan và dữ liệu mẫu. README này là tài liệu tổng hợp để giảng viên có thể nắm nhanh phạm vi, cách chạy và cấu trúc của hệ thống.
