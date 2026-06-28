from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['code', 'title', 'author', 'isbn', 'total_copies', 'available_copies', 'is_active']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VD: BK-021...'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tiêu đề sách...'}),
            'author': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tên tác giả...'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mã ISBN (tùy chọn)'}),
            'total_copies': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'available_copies': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'code': 'Mã sách',
            'title': 'Tên sách',
            'author': 'Tác giả',
            'isbn': 'Mã ISBN',
            'total_copies': 'Tổng số sách',
            'available_copies': 'Sách khả dụng (có thể mượn)',
            'is_active': 'Đang sử dụng',
            }
