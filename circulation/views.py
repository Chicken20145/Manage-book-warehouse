from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.dateparse import parse_date
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.decorators import role_required
from catalog.models import Book
from .forms import BorrowingForm, ReturnForm
from .models import BorrowedItem, Borrowing


def _is_staff_librarian(user):
    return getattr(user, 'role', None) in {'ADMIN', 'LIBRARIAN'}


@login_required
def loan_list_view(request):
    if request.user.is_authenticated and not _is_staff_librarian(request.user):
        borrowings = Borrowing.objects.filter(user=request.user).select_related('user', 'confirmed_by').prefetch_related('items__book')
    else:
        borrowings = Borrowing.objects.select_related('user', 'confirmed_by').prefetch_related('items__book')

    fine_status = request.GET.get('fine_status', '').strip().lower()
    if fine_status == 'unpaid':
        borrowings = borrowings.filter(fine__gt=0, is_fine_paid=False)
    elif fine_status == 'paid':
        borrowings = borrowings.filter(is_fine_paid=True)

    today = timezone.localdate()
    Borrowing.objects.filter(status=Borrowing.Status.BORROWED, due_date__lt=today, returned_date__isnull=True).update(status=Borrowing.Status.OVERDUE)
    for borrowing in borrowings:
        if borrowing.status == Borrowing.Status.BORROWED and borrowing.due_date < today:
            borrowing.status = Borrowing.Status.OVERDUE

    context = {
        'loans': borrowings,
        'borrow_form': BorrowingForm(),
        'return_form': ReturnForm(),
        'fine_status': fine_status,
    }
    return render(request, 'circulation/loan_list.html', context)


@role_required('ADMIN', 'LIBRARIAN')
def create_borrowing_view(request):
    if request.method == 'POST':
        form = BorrowingForm(request.POST)
        if form.is_valid():
            books = list(form.cleaned_data['books'])
            borrowing = form.save(commit=False)
            borrowing.status = Borrowing.Status.BORROWED
            borrowing.confirmed_by = request.user
            borrowing.confirmed_at = timezone.now()
            if not borrowing.due_date:
                borrowing.due_date = borrowing.borrow_date + timedelta(days=14)
            try:
                with transaction.atomic():
                    borrowing.save()
                    for book in books:
                        locked_book = Book.objects.select_for_update().get(pk=book.pk)
                        if locked_book.available_copies < 1:
                            raise ValueError(f'Sách "{locked_book.title}" không đủ số lượng.')
                        locked_book.available_copies -= 1
                        locked_book.save(update_fields=['available_copies', 'updated_at'])
                        BorrowedItem.objects.create(borrowing=borrowing, book=locked_book, quantity=1)
            except ValueError as exc:
                messages.error(request, str(exc))
                return redirect('loan-list')
            messages.success(request, 'Đã tạo phiếu mượn.')
            return redirect('loan-list')
        error_messages = []
        for field, errors in form.errors.items():
            label = form.fields[field].label if field in form.fields else field
            for error in errors:
                error_messages.append(f'{label}: {error}')
        messages.error(
            request,
            'Không thể tạo phiếu mượn. ' + (' | '.join(error_messages) if error_messages else 'Vui lòng kiểm tra lại dữ liệu.'),
        )
    return redirect('loan-list')


@role_required('ADMIN', 'LIBRARIAN')
@require_POST
def confirm_return_view(request, borrowing_id):
    borrowing = get_object_or_404(Borrowing, pk=borrowing_id)
    returned_date = parse_date(request.POST.get('returned_date') or '') or timezone.localdate()
    with transaction.atomic():
        borrowing = Borrowing.objects.select_for_update().get(pk=borrowing_id)
        borrowing.returned_date = returned_date or timezone.localdate()
        borrowing.status = Borrowing.Status.RETURNED
        borrowing.confirmed_by = request.user
        borrowing.confirmed_at = timezone.now()
        borrowing.fine = borrowing.calculate_fine()
        borrowing.save()
        items = BorrowedItem.objects.select_related('book').filter(borrowing=borrowing)
        for item in items:
            if not item.is_returned:
                book = Book.objects.select_for_update().get(pk=item.book_id)
                book.available_copies += item.quantity
                book.save(update_fields=['available_copies', 'updated_at'])
                item.is_returned = True
                item.returned_date = borrowing.returned_date
                item.save(update_fields=['is_returned', 'returned_date'])
    messages.success(request, 'Đã xác nhận trả sách.')
    return redirect('loan-list')


@role_required('ADMIN', 'LIBRARIAN')
@require_POST
def confirm_borrowing_view(request, borrowing_id):
    borrowing = get_object_or_404(Borrowing, pk=borrowing_id)
    if borrowing.status != Borrowing.Status.BORROWED:
        messages.error(request, 'Chỉ có thể xác nhận mượn với phiếu đang mượn.')
        return redirect('loan-list')
    borrowing.confirmed_by = request.user
    borrowing.confirmed_at = timezone.now()
    borrowing.save(update_fields=['confirmed_by', 'confirmed_at', 'updated_at'])
    messages.success(request, 'Đã xác nhận phiếu mượn.')
    return redirect('loan-list')


@role_required('ADMIN', 'LIBRARIAN')
@require_POST
def confirm_fine_payment_view(request, borrowing_id):
    borrowing = get_object_or_404(Borrowing, pk=borrowing_id)
    borrowing.is_fine_paid = True
    borrowing.save(update_fields=['is_fine_paid', 'updated_at'])
    messages.success(request, 'Đã ghi nhận thu phạt.')
    return redirect('loan-list')
