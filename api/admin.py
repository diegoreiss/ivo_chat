from typing import Any
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from . import models


admin.site.site_header = 'Super Administração do IVO'

@admin.register(models.CustomUser)
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
                    'is_password_changed',
                    'is_staff', 
                    'is_superuser',
                ),
            },
        ),
    )
    list_display = ('uuid', 'pk', 'username', 'turma', 'email', 'role', 'is_staff', 'is_active', 'is_password_changed')
    fieldsets = (
        (_('Dados de autenticação'), {'fields': ('username', 'password')}),
        (_('Dados de conta'), {'fields': ('role', 'is_password_changed', 'turma')}),
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
        (_('Dados Importantes'), {'fields': ('last_login', 'date_joined')})
    )

    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        dados_form = {key: value for key, value in request.POST.copy().items()}
        del dados_form['csrfmiddlewaretoken']

        return super().save_model(request, obj, form, change)


@admin.register(models.Disciplina)
class CustomDisciplinaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'uuid', 'pk')


@admin.register(models.Turma)
class CustomTurmaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'turno', 'calendario', 'uuid', 'pk')

@admin.register(models.CustomUserDisciplina)
class CustomUserDisciplinaModel(admin.ModelAdmin):
    list_display = ('custom_user', 'disciplina', 'falta', 'notas')
