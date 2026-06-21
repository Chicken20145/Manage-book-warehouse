from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'role', 'student_id')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        labels = {
            'username': 'Tên đăng nhập',
            'email': 'Email',
            'role': 'Vai trò',
            'student_id': 'Mã sinh viên',
            'password1': 'Mật khẩu',
            'password2': 'Nhập lại mật khẩu',
        }
        placeholders = {
            'username': 'vd: nguyenvana',
            'email': 'vd: ban@example.com',
            'student_id': 'Bỏ trống nếu không phải sinh viên',
        }
        for name, field in self.fields.items():
            field.label = labels.get(name, field.label)
            css_class = 'form-select' if name == 'role' else 'form-control'
            field.widget.attrs.update({'class': css_class})
            if name in placeholders:
                field.widget.attrs['placeholder'] = placeholders[name]
