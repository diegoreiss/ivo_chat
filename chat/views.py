from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema
from django.core.cache import caches 

from . import serializers

# Create your views here.

class ChatHistoryRetrieveUpdate(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(operation_summary='Retorna o histórico do chat', responses={
        status.HTTP_200_OK: serializers.ChatMessageSerializer
    })
    def get(self, request, room_name):
        default_cache = caches['default']
        history = default_cache.get(f'chat_history:{room_name}', [])

        return Response(history, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(operation_summary='Deleta o histórico do chat')
    def delete(self, request, room_name):
        default_cache = caches['default']
        default_cache.set(f'chat_history:{room_name}', [])

        return Response({}, status=status.HTTP_200_OK)
