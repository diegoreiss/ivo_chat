from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login as auth_login

# Create your views here.

class LoginView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'accounts/login.html')
