from functools import wraps

from django.shortcuts import redirect, render
from django.contrib import messages


def role_required(function):
    @wraps(function)
    def wrapper(request, *args, **kwargs):
        role = request.user.role

        if not role:
            messages.error(request, 'Credenciais Inválidas!')
            return redirect('auth-login')
        
        return function(request, *args, **kwargs)
    
    return wrapper


def redirect_by_role(function):
    redirects = {
        1: 'chat/chat_adm.html',
        2: 'chat/chatIVO.html',
    }

    @wraps(function)
    def wrapper(request, *args, **kwargs):
        role = request.user.role
        print(role)
        print(redirects[role])

        return render(request, redirects[role])
    
    return wrapper
