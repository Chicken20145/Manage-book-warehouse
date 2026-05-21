from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Sach
from .forms import SachForm

# 1. Xem danh sách sách
class DanhSachSachView(ListView):
    model = Sach
    template_name = 'catalog/sach_list.html'
    context_object_name = 'danh_sach_sach'

# 2. Thêm sách mới
class SachCreateView(CreateView):
    model = Sach
    form_class = SachForm
    template_name = 'catalog/sach_form.html'
    success_url = reverse_lazy('danh-sach-sach')

# 3. Chỉnh sửa thông tin sách (Sử dụng lại luôn file sach_form.html)
class SachUpdateView(UpdateView):
    model = Sach
    form_class = SachForm
    template_name = 'catalog/sach_form.html'
    success_url = reverse_lazy('danh-sach-sach')

# 4. Xóa sách
class SachDeleteView(DeleteView):
    model = Sach
    template_name = 'catalog/sach_confirm_delete.html' # Trang xác nhận trước khi xóa
    success_url = reverse_lazy('danh-sach-sach')