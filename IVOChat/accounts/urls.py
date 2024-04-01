from django.urls import path

from . import views


urlpatterns = [
    path('login/', view=views.login, name='auth-login'),
]
