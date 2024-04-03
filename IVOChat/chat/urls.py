from django.urls import path

from . import views


urlpatterns = [
    path('', view=views.index, name='chat-index'),
    path('<str:room_name>/', view=views.sala, name='chat-sala')
]
