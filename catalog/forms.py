from django import forms
from .models import Sach

class SachForm(forms.ModelForm):
    class Meta:
        model = Sach
        fields = ['tieu_de', 'tac_gia', 'the_loai', 'so_luong_kho']
        widgets = {
            'tieu_de': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tiêu đề sách...'}),
            'tac_gia': forms.Select(attrs={'class': 'form-select'}),
            'the_loai': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'so_luong_kho': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }

    # Bổ sung tính năng Validation dữ liệu
    def clean_tieu_de(self):
        tieu_de = self.cleaned_data.get('tieu_de')
        if len(tieu_de) < 3:
            raise forms.ValidationError("❌ Tên sách quá ngắn, vui lòng nhập tên đầy đủ và rõ nghĩa hơn!")
        return tieu_de