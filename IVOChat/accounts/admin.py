from typing import Any
from django.shortcuts import HttpResponseRedirect
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser


admin.site.site_header = 'Administração da Biblioteca'

@admin.register(CustomUser)
class CustomAdmin(UserAdmin):
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'first_name',
                    'last_name',
                    'username', 
                    'email', 
                    'password1', 
                    'password2', 
                    'role', 
                    'is_staff', 
                    'is_superuser'
                ),
            },
        ),
    )
    list_display = ('username', 'email', 'role', 'is_staff', 'is_password_changed')
    fieldsets = (
        (_('Dados de autenticação'), {'fields': ('username', 'password')}),
        (_('Dados de conta'), {'fields': ('role',)}),
        (_('Dados Pessoais'), {'fields': ('first_name', 'last_name', 'email')}),
        (
            _('Permissões'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions'
                )
            }
        ),
        (_('Dadas Importantes'), {'fields': ('last_login', 'date_joined')})
    )

    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        dados_form = {key: value for key, value in request.POST.copy().items()}
        del dados_form['csrfmiddlewaretoken']

        return super().save_model(request, obj, form, change)
    