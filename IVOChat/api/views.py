from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema

from . import serializers
from accounts import models as accounts_models
from . import models
from utils import email_utils


# Create your views here.


class CustomUserListCreate(generics.ListCreateAPIView):
    queryset = accounts_models.CustomUser.objects.all()
    serializer_class = serializers.CustomUserSerializer
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )
 
    @swagger_auto_schema(operation_summary='Retorna todos os usuários')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CustomUserRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = accounts_models.CustomUser.objects.all()
    serializer_class = serializers.CustomUserCreateSerializer
    lookup_field = 'pk'

    @swagger_auto_schema(operation_summary='Altera senha provisória e envia o email')
    def patch(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            self.object.set_password(serializer.data.get('password'))
            self.object.is_active = True
            self.object.save()

            email_utils.send_email('Nova Senha', self.object.email,
                                   f'Sua nova senha: {serializer.data.get("password")}')

            return Response({
                'message': 'works'
            }, status=status.HTTP_200_OK)


class CustomUserCurrentRetrieve(generics.RetrieveAPIView):
    serializer_class = serializers.CustomUserRetrieveSerializer
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(operation_summary='Retona o usuário atual autorizado')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self):
        return self.request.user


class CustomUserByRoleAlunoAPIView(generics.ListAPIView):
    serializer_class = serializers.CustomUserSerializer
    queryset = accounts_models.CustomUser.objects.filter(role=2)

    @swagger_auto_schema(operation_summary='Retona todos os usuários com a role [Aluno]')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)