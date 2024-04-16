from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.views import View

from . import decorators

# Create your views here.

class ChatView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'chat/chatIVO.html')


class ChatAdminView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'chat/relatorio_adm.html')


# def sala(request, room_name):
#     return render(request, 'chat/chatIVO.html', context={
#         'room_name': room_name,
#         'rasa_url': environ['RASA_URL'],
#     })

