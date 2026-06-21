from django import forms

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
        fields = ['user', 'borrow_date', 'due_date', 'notes']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'borrow_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['books'].queryset = Book.objects.filter(available_copies__gt=0)

    def clean_books(self):
        books = self.cleaned_data['books']
        if len(books) > 5:
            raise forms.ValidationError('Chỉ được mượn tối đa 5 cuốn sách cùng lúc.')
        return books


class ReturnForm(forms.Form):
    returned_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
