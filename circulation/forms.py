from django import forms

from accounts.models import CustomUser
from catalog.models import Book
from .models import Borrowing


class BorrowingForm(forms.ModelForm):
    books = forms.ModelMultipleChoiceField(
        queryset=Book.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        label='Chọn sách mượn',
    )

    class Meta:
        model = Borrowing
        fields = ['user', 'borrow_date', 'notes']
        labels = {
            'user': 'Sinh viên',
            'borrow_date': 'Ngày mượn',
            'notes': 'Ghi chú',
        }
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'borrow_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = CustomUser.objects.filter(role='STUDENT').order_by('username')
        self.fields['user'].empty_label = 'Chọn sinh viên'
        self.fields['books'].queryset = Book.objects.filter(is_active=True, available_copies__gt=0)
        self.fields['books'].widget.attrs.update({'class': 'form-check-input'})

    def clean_books(self):
        books = self.cleaned_data['books']
        if len(books) > 5:
            raise forms.ValidationError('Chỉ được mượn tối đa 5 cuốn sách cùng lúc.')
        return books


class ReturnForm(forms.Form):
    returned_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
