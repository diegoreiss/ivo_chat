from django.urls import path

from . import views


urlpatterns = [
    path('', view=views.ChatView.as_view(), name='chat_index'),
    path('admin/', view=views.ChatAdminView.as_view(), name='chat_admin_index'),
]
