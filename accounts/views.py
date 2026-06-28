import sys
from django.db.models import Q
from django import get_version as get_django_version
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from .decorators import role_required
from .forms import AdminPasswordResetForm, AdminUserUpdateForm, CustomUserCreationForm, ProfileUpdateForm, StyledPasswordChangeForm
from .models import CustomUser


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def account_settings_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật thông tin tài khoản.')
            return redirect('account-settings')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'accounts/settings.html', {'form': form})


class AccountPasswordChangeView(PasswordChangeView):
    form_class = StyledPasswordChangeForm
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('account-settings')

    def form_valid(self, form):
        messages.success(self.request, 'Đã đổi mật khẩu thành công.')
        return super().form_valid(form)


@role_required('ADMIN')
def admin_panel_view(request):
    query = request.GET.get('q', '').strip()
    users = CustomUser.objects.order_by('username')
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(student_id__icontains=query)
        )
    
    # Tính toán số liệu thống kê tài khoản
    total_users = CustomUser.objects.count()
    admin_count = CustomUser.objects.filter(role='ADMIN').count()
    librarian_count = CustomUser.objects.filter(role='LIBRARIAN').count()
    student_count = CustomUser.objects.filter(role='STUDENT').count()
    active_count = CustomUser.objects.filter(is_active=True).count()
    locked_count = total_users - active_count
    
    # Thông tin hệ thống máy chủ
    python_version = sys.version.split(' ')[0]
    django_version = get_django_version()
    
    context = {
        'users': users,
        'query': query,
        'stats': {
            'total': total_users,
            'admin': admin_count,
            'librarian': librarian_count,
            'student': student_count,
            'active': active_count,
            'locked': locked_count,
        },
        'sys_info': {
            'python': python_version,
            'django': django_version,
            'os': sys.platform,
        }
    }
    return render(request, 'accounts/admin_panel.html', context)


@role_required('ADMIN')
def user_update_view(request, pk):
    target_user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = AdminUserUpdateForm(request.POST, instance=target_user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Đã cập nhật tài khoản.')
            return redirect('admin-panel')
    else:
        form = AdminUserUpdateForm(instance=target_user)
    return render(request, 'accounts/user_form.html', {'form': form, 'target_user': target_user})


@role_required('ADMIN')
def user_password_reset_view(request, pk):
    target_user = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = AdminPasswordResetForm(target_user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Đã đặt lại mật khẩu cho {target_user.username}.')
            return redirect('admin-panel')
    else:
        form = AdminPasswordResetForm(target_user)
    return render(request, 'accounts/user_password_reset.html', {'form': form, 'target_user': target_user})
