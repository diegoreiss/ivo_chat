from django.urls import path

from . import views


urlpatterns = [
    path('<str:room_name>/', views.ChatHistoryRetrieveUpdate.as_view(), name='chat_history_retrieve_update')
]
