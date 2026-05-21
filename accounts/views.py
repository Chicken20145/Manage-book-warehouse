from django.shortcuts import render, redirect
from django.contrib.auth import login
from.forms import CustomUserCreationForm

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Đăng nhập luôn sau khi đăng ký thành công
            return redirect('login') # Tạm thời chuyển hướng về trang login
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})