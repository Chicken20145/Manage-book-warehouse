from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone
from .models import Borrowing, BorrowedItem
from .forms import BorrowingForm
from catalog.models import Book

class BorrowingListView(LoginRequiredMixin, ListView):
    model = Borrowing
    template_name = 'circulation/borrowing_list.html'
    context_object_name = 'borrowings'

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Borrowing.objects.all().order_by('-borrow_date')
        return Borrowing.objects.filter(user=user).order_by('-borrow_date')

class BorrowingDetailView(LoginRequiredMixin, DetailView):
    model = Borrowing
    template_name = 'circulation/borrowing_detail.html'
    context_object_name = 'borrowing'

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Borrowing.objects.all()
        return Borrowing.objects.filter(user=user)

@method_decorator(staff_member_required, name='dispatch')
class BorrowingCreateView(CreateView):
    model = Borrowing
    form_class = BorrowingForm
    template_name = 'circulation/borrowing_form.html'
    success_url = reverse_lazy('circulation:list')

    def form_valid(self, form):
        borrowing = form.save(commit=False)
        borrowing.save()
        books = form.cleaned_data['books']
        for book in books:
            BorrowedItem.objects.create(borrowing=borrowing, book=book)
            book.borrow_copy()  # gọi method từ catalog.Book
        return super().form_valid(form)

@staff_member_required
def return_book_item(request, item_id):
    item = get_object_or_404(BorrowedItem, id=item_id, is_returned=False)
    item.is_returned = True
    item.returned_date = timezone.now().date()
    item.save()
    # Cập nhật số lượng sách
    item.book.return_copy()

    borrowing = item.borrowing
    if all(i.is_returned for i in borrowing.items.all()):
        borrowing.returned_date = timezone.now().date()
        borrowing.fine = borrowing.calculate_fine()
        borrowing.status = 'RETURNED'
        borrowing.save()
    return redirect('circulation:detail', pk=borrowing.pk)

@login_required
def renew_borrowing(request, pk):
    borrowing = get_object_or_404(Borrowing, pk=pk, user=request.user)
    if not borrowing.extended and borrowing.due_date >= timezone.now().date():
        borrowing.due_date += timezone.timedelta(days=7)
        borrowing.extended = True
        borrowing.save()
    return redirect('circulation:detail', pk=pk)