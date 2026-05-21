from django import forms
from .models import Borrowing
from catalog.models import Book  # import từ app catalog

class BorrowingForm(forms.ModelForm):
    books = forms.ModelMultipleChoiceField(
        queryset=Book.objects.filter(available_copies__gt=0),
        widget=forms.CheckboxSelectMultiple,
        label="Chọn sách mượn"
    )

    class Meta:
        model = Borrowing
        fields = ['user']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'})
        }

    def clean_books(self):
        books = self.cleaned_data['books']
        if len(books) > 5:
            raise forms.ValidationError("Chỉ được mượn tối đa 5 cuốn sách cùng lúc.")
        return books