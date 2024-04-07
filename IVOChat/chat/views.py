from os import environ
from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'chat/chat.html')


def sala(request, room_name):
    return render(request, 'chat/chatIVO.html', context={
        'room_name': room_name,
        'rasa_url': environ['RASA_URL'],
    })

