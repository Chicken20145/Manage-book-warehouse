from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from .models import Book
from .forms import BookForm

# 1. HÀM KIỂM TRA PHÂN QUYỀN
def is_admin_or_librarian(user):
    # Kiểm tra theo role của nhóm bạn tự định nghĩa
    return getattr(user, 'role', '') in ['ADMIN', 'LIBRARIAN'] or user.is_superuser

# 2. XEM DANH SÁCH & TÌM KIẾM (Ai cũng xem được)
@login_required
def book_list_view(request):
    query = request.GET.get('q', '')
    books = Book.objects.all()
    
    # Logic tìm kiếm theo Tên, Tác giả hoặc Mã sách
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(code__icontains=query)
        )
    
    # Biến 'can_edit' giúp template biết để ẩn/hiện nút Thêm/Sửa/Xóa
    can_edit = is_admin_or_librarian(request.user)
    
    return render(request, 'catalog/book_list.html', {
        'books': books, 
        'query': query,
        'can_edit': can_edit
    })

# 3. THÊM SÁCH (Chỉ ADMIN/LIBRARIAN)
@login_required
@user_passes_test(is_admin_or_librarian, login_url='/')
def book_create_view(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('book-list')
    else:
        form = BookForm()
    return render(request, 'catalog/book_form.html', {'form': form, 'action': 'Thêm Sách'})

# 4. SỬA SÁCH (Chỉ ADMIN/LIBRARIAN)
@login_required
@user_passes_test(is_admin_or_librarian, login_url='/')
def book_update_view(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book-list')
    else:
        form = BookForm(instance=book)
    return render(request, 'catalog/book_form.html', {'form': form, 'action': 'Cập nhật Sách'})

# 5. XÓA SÁCH (Chỉ ADMIN/LIBRARIAN)
@login_required
@user_passes_test(is_admin_or_librarian, login_url='/')
def book_delete_view(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        if book.borrowed_items.exists():
            messages.error(request, 'Không thể xóa sách đã phát sinh phiếu mượn. Hãy điều chỉnh số lượng hoặc ngưng sử dụng sách này.')
            return redirect('book-list')
        book.delete()
        messages.success(request, 'Đã xóa sách khỏi danh mục.')
        return redirect('book-list')
    return render(request, 'catalog/book_confirm_delete.html', {'book': book})
