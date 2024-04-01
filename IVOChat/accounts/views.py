from django.shortcuts import render
from django.contrib.auth import authenticate, login as auth_login

# Create your views here.

def login(request):
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)

            return render(request, 'accounts/ok.html', context={'user': user.get_username()})

    return render(request, 'accounts/login.html')
    ...


def logout(request):
    ...
