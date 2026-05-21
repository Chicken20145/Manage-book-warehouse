from django.contrib import admin
from .models import TheLoai, TacGia, Sach

@admin.register(TheLoai)
class TheLoaiAdmin(admin.ModelAdmin):
    list_display = ('id', 'ten_the_loai') # Hiển thị cột ID và Tên thể loại

@admin.register(TacGia)
class TacGiaAdmin(admin.ModelAdmin):
    list_display = ('id', 'ten_tac_gia') # Hiển thị cột ID và Tên tác giả

@admin.register(Sach)
class SachAdmin(admin.ModelAdmin):
    # Cấu hình các cột sẽ hiển thị ra danh sách
    list_display = ('id', 'tieu_de', 'tac_gia', 'so_luong_kho')
    
    # Tạo bộ lọc nhanh ở cột bên phải (Lọc theo tác giả và thể loại)
    list_filter = ('the_loai', 'tac_gia')
    
    # Tạo thanh tìm kiếm thông minh (Tìm theo tiêu đề sách hoặc tên tác giả)
    search_fields = ('tieu_de', 'tac_gia__ten_tac_gia')
