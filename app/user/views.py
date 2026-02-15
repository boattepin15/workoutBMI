from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView
from django.contrib import messages
from .forms import UserRegisterForm

class UserLoginView(LoginView):
    template_name = 'user/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('home') 
    
    def form_invalid(self, form):
        messages.error(self.request, "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")
        return super().form_invalid(form)

class UserLogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, "ออกจากระบบเรียบร้อยแล้ว")
        return redirect('login')

class UserRegisterView(CreateView):
    template_name = 'user/register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        messages.success(self.request, "สมัครสมาชิกสำเร็จ กรุณาเข้าสู่ระบบ")
        return super().form_valid(form)
