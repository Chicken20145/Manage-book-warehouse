from django.db import models

class TheLoai(models.Model):
    ten_the_loai = models.CharField(max_length=100, verbose_name="Tên thể loại")
    
    class Meta:
        verbose_name = "Thể loại"
        verbose_name_plural = "Quản lý Thể loại" # Tên hiển thị ở trang tổng

    def __str__(self):
        return self.ten_the_loai

class TacGia(models.Model):
    ten_tac_gia = models.CharField(max_length=200, verbose_name="Tên tác giả")
    
    class Meta:
        verbose_name = "Tác giả"
        verbose_name_plural = "Quản lý Tác giả"

    def __str__(self):
        return self.ten_tac_gia

class Sach(models.Model):
    tieu_de = models.CharField(max_length=200, verbose_name="Tiêu đề sách")
    tac_gia = models.ForeignKey(TacGia, on_delete=models.SET_NULL, null=True, verbose_name="Tác giả")
    the_loai = models.ManyToManyField(TheLoai, verbose_name="Thể loại")
    so_luong_kho = models.IntegerField(default=1, verbose_name="Số lượng trong kho")

    class Meta:
        verbose_name = "Sách"
        verbose_name_plural = "Quản lý Kho Sách"

    def __str__(self):
        return self.tieu_de